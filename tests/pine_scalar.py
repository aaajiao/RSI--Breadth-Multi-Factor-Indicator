"""Evaluate a deliberately small, scalar subset of the *actual* RSI+ source.

This is not a Pine compiler or runtime. It supports assignments, if/else,
scalar expressions and helper calls only. It cannot validate request.security,
time-series functions, Pine rollback, types, historical backfill, or rendering.
Unsupported syntax fails instead of silently substituting a reference model.
"""

import ast
import math
from pathlib import Path
import re
from types import SimpleNamespace


SOURCE = Path(__file__).resolve().parents[1] / "RSI+"
NA = float("nan")


def is_na(value):
    return isinstance(value, float) and math.isnan(value)


def uncomment(line):
    # A string may contain //; only remove comments outside quoted strings.
    return re.split(r'("(?:\\.|[^"\\])*"|//.*$)', line)[0] if '"' not in line else re.sub(
        r'("(?:\\.|[^"\\])*")|//.*$', lambda m: m[1] or "", line
    )


def outside(text):
    """Yield positions outside strings and brackets, including bracket starts."""
    depth = 0
    quote = False
    escaped = False
    for index, char in enumerate(text):
        if quote:
            if char == '"' and not escaped:
                quote = False
            escaped = char == "\\" and not escaped
            continue
        if char == '"':
            quote = True
            continue
        if depth == 0:
            yield index, char
        if char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1


def expression(text):
    """Translate nested Pine ternaries, retaining normal expression precedence."""
    text = text.strip()
    positions = list(outside(text))
    commas = [i for i, char in positions if char == ","]
    if commas:
        points = [-1] + commas + [len(text)]
        return ", ".join(expression(text[a + 1:b]) for a, b in zip(points, points[1:]))
    question = next((i for i, char in positions if char == "?"), None)
    if question is not None:
        nesting = 0
        for index, char in positions:
            if index <= question:
                continue
            if char == "?":
                nesting += 1
            elif char == ":":
                if nesting == 0:
                    return f"({expression(text[question + 1:index])} if {expression(text[:question])} else {expression(text[index + 1:])})"
                nesting -= 1
        raise ValueError(f"Unmatched ternary: {text}")

    # Translate the interior of each outer bracket without altering strings.
    starts = [i for i, char in positions if char in "(["]
    for start in reversed(starts):
        depth, quote, escaped = 0, False, False
        for end in range(start, len(text)):
            char = text[end]
            if quote:
                if char == '"' and not escaped:
                    quote = False
                escaped = char == "\\" and not escaped
                continue
            if char == '"':
                quote = True
            elif char in "([":
                depth += 1
            elif char in ")]":
                depth -= 1
                if depth == 0:
                    text = text[:start + 1] + expression(text[start + 1:end]) + text[end:]
                    break
    return re.sub(r'("(?:\\.|[^"\\])*")|\b(true|false|na)\b(?!\s*\()',
                  lambda m: m[1] or {"true": "True", "false": "False", "na": "NA"}[m[2]], text)


def statements(source):
    lines = []
    pending, indent, depth = "", 0, 0
    for raw in source.splitlines():
        clean = uncomment(raw).rstrip()
        if not clean.strip():
            continue
        if not pending:
            indent = len(clean) - len(clean.lstrip())
        pending += (" " if pending else "") + clean.strip()
        strings_removed = re.sub(r'"(?:\\.|[^"\\])*"', '""', clean)
        depth += sum(strings_removed.count(c) for c in "([") - sum(strings_removed.count(c) for c in ")]")
        if depth == 0:
            lines.append((indent, pending))
            pending = ""
    if pending:
        raise ValueError("Unclosed statement")
    return lines


class ScalarSource:
    def __init__(self, source=None):
        self.source = SOURCE.read_text() if source is None else source
        self.functions = {}
        lines = self.source.splitlines()
        for index, line in enumerate(lines):
            match = re.fullmatch(r"(f_\w+)\((.*?)\) =>", line)
            if match:
                end = index + 1
                while end < len(lines) and (not lines[end].strip() or lines[end].startswith(" ")):
                    end += 1
                self.functions[match[1]] = (
                    [arg.strip() for arg in match[2].split(",")],
                    statements("\n".join(lines[index + 1:end])),
                )

    def evaluate(self, text, env):
        tree = ast.parse(expression(text), mode="eval")
        # Inputs are repository source, but keep the evaluator narrow and explicit.
        allowed = (ast.Expression, ast.Constant, ast.Name, ast.Load, ast.Call,
                   ast.Attribute, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
                   ast.IfExp, ast.List, ast.Tuple, ast.Subscript, ast.operator,
                   ast.unaryop, ast.boolop, ast.cmpop)
        if any(not isinstance(node, allowed) for node in ast.walk(tree)):
            raise ValueError(f"Unsupported scalar expression: {text}")
        context = {
            "NA": NA, "na": is_na, "nz": lambda value, replacement=0: replacement if is_na(value) else value,
            "math": SimpleNamespace(max=max, min=min, abs=abs, pow=pow, sqrt=math.sqrt, round=lambda v: math.floor(v + .5)),
            "int": int, "float": float,
        }
        context.update({name: lambda *args, name=name: self.call(name, *args, env=env) for name in self.functions})
        context.update(env)
        return eval(compile(tree, "<Pine scalar subset>", "eval"), {"__builtins__": {}}, context)

    def call(self, name, *args, env=None):
        params, body = self.functions[name]
        if len(params) != len(args):
            raise ValueError(f"{name}: expected {len(params)} arguments, got {len(args)}")
        local = dict(env or {})
        local.update(zip(params, args))
        return self.run(body, local)

    def run(self, lines, env):
        """Run scalar statements; var/varip declarations initialize only once."""
        result, index = None, 0
        while index < len(lines):
            indent, line = lines[index]
            if line.startswith("if "):
                branches = []
                while True:
                    condition = line[3:] if line.startswith("if ") else line[8:] if line.startswith("else if ") else None
                    end = index + 1
                    while end < len(lines) and lines[end][0] > indent:
                        end += 1
                    branches.append((condition, lines[index + 1:end]))
                    index = end
                    if index >= len(lines) or lines[index][0] != indent or not lines[index][1].startswith("else"):
                        break
                    _, line = lines[index]
                for condition, body in branches:
                    if condition is None or self.evaluate(condition, env):
                        result = self.run(body, env)
                        break
                continue
            assignment = re.fullmatch(r"(?:(varip|var) )?(?:(?:int|float|bool|string) )?(\w+)\s*(?::=|=(?!=))\s*(.+)", line)
            if assignment:
                persistent, name, value = assignment.groups()
                if not persistent or name not in env:
                    env[name] = self.evaluate(value, env)
                result = env[name]
            else:
                result = self.evaluate(line, env)
            index += 1
        return result

    def assignment(self, name, env):
        match = re.search(rf"^[ \t]*(?:int |float |bool |string )?{re.escape(name)}\s*=\s*(.+)$", self.source, re.MULTILINE)
        if not match:
            raise AssertionError(f"Missing one-line assignment: {name}")
        return self.evaluate(uncomment(match[1]), env)
