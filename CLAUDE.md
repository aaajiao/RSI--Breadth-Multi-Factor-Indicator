# AGENTS.md - RSI+ Breadth Multi-Factor Indicator

> Guidelines for AI coding agents working in this Pine Script repository.

## Project Overview

| Item | Value |
|------|-------|
| **Language** | Pine Script v6 (TradingView) |
| **Main File** | `RSI+` (~1224 lines) |
| **Version** | v7.4 |
| **Purpose** | US market timing for SPY, QQQ, IWM |

Multi-factor scoring: RSI + Market Breadth (TW/FI) + Volume Ratio + Divergence.

## Build / Lint / Test

**Pine Script has NO local build/test system.** Validation is manual in TradingView.

```bash
# Workflow:
# 1. Copy RSI+ to TradingView Pine Editor
# 2. Click "Add to Chart" - errors appear in console
# 3. Visual verification on SPY/QQQ/IWM daily

# Git (bilingual commits preferred)
git commit -m "feat: description / 中文描述"
```

### Validation Checklist
- [ ] Compiles in TradingView without errors
- [ ] Signals render on SPY, QQQ, IWM charts
- [ ] Dashboard displays (Full/Mobile modes)
- [ ] README updated if user-facing changes

## Code Style

### File Structure
```pine
//@version=6
indicator("Name", overlay=true, max_labels_count=500, max_bars_back=1100)

//==============================================================================
// SECTION HEADER (ALL CAPS, = BORDER)
//==============================================================================

//========================
// Subsection Header
//========================
```

### Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Functions | `f_` prefix + camelCase | `f_rsiScore()` |
| Variables | camelCase | `spyScore`, `displayUptrend` |
| Input groups | `grp` prefix | `grpMode`, `grpOptimize` |
| Function params | `_` prefix | `_rsi`, `_lookback` |

### Input Parameters (Bilingual Required)
```pine
grpOptimize = "v7.0 Optimizations 胜率优化"

useSignalQuality = input.bool(true, "Signal Quality Filter 信号质量过滤", 
    group=grpOptimize,
    tooltip="仅触发A/B级信号\nOnly trigger A/B grade signals")
```

### Functions
```pine
// Single return - end with result variable
f_rsiScore(_rsi, _os1, _os2, _ob1, _ob2) =>
    score = 0.0
    if not na(_rsi)
        if _rsi < _os1
            score := 2
    score

// Multi-return tuple
f_signalQuality(_rsiS, _fiS, _twS, _volS) =>
    positiveFactors = (_rsiS > 0 ? 1 : 0) + (_fiS > 0 ? 1 : 0)
    buyQuality = positiveFactors >= 3 ? "A" : positiveFactors >= 2 ? "B" : "C"
    [buyQuality, positiveFactors]
```

## Critical Pine Script Patterns

### Security Requests (ALWAYS use both flags)
```pine
f_sec(_sym, _expr) =>
    request.security(_sym, tfData, _expr, barmerge.gaps_off, barmerge.lookahead_off)

f_secDaily(_sym, _expr) =>
    request.security(_sym, "D", _expr, barmerge.gaps_off, barmerge.lookahead_off)

// v7.4: Intraday live daily data (lookahead_on for developing bar)
f_secDailyLive(_sym, _expr) =>
    request.security(_sym, "D", _expr, barmerge.gaps_off, barmerge.lookahead_on)
```

### State Management
```pine
var int spyLastBot = na              // Persistent across bars
varip int buy_alert_level_sent = 0   // Intrabar persistence (alerts)

if barstate.isnew
    buy_alert_level_sent := 0        // Reset on new bar
```

### Error Handling (MANDATORY)
```pine
if not na(_rsi)                      // Always check na
    // safe to use

safe_lookback = math.max(10, math.min(_lookback, bar_index - 1))  // Clamp
ratio = _dvol > 0 ? _uvol / _dvol : 0                             // Division guard
```

## Signal Reference

| Score | Emoji | Signal | Condition |
|:-----:|:-----:|--------|-----------|
| ≥ 6 | 🚀 | PANIC LOW | Extreme oversold + panic |
| ≥ 4 | 📈 | BUY ZONE | Multi-factor buy |
| DIV | 💎 | DIVERGENCE | Z-Score threshold |
| ≤ -4↑ | ⭐ | ELEVATED | Overbought + uptrend |
| ≤ -4↓ | ⚡ | CAUTION | Overbought + downtrend |
| ≤ -6↓ | ⚠️ | REDUCE | Extreme overbought |
| 2+ mkts | 🔥 | RESONANCE | Multi-market aligned |

## v7.x Key Functions

| Function | Purpose |
|----------|---------|
| `f_signalQuality()` | A/B/C grade (factor alignment) |
| `f_drawdownBonus()` | +1/+2/+3 at 5/10/20% DD |
| `f_divergenceAssisted()` | Boost edge signals |
| `f_resonanceStrength()` | Tiered multi-market sync |
| `f_progressBar()` | v7.4 visual dashboard bars |
| `f_centeredBar()` | v7.4 centered score bar (-8 to +8) |
| `f_adaptiveThresholds()` | Dynamic RSI levels |
| `f_dynamicCooldown()` | Vol-adjusted signal spacing |
| `f_secDailyLive()` | v7.4 intraday developing daily data |

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| `na` runtime errors | Check `not na(value)` before use |
| Lookahead bias | Use `lookahead_off` (except `f_secDailyLive` for intraday) |
| History overflow | Clamp with `math.min(_lookback, bar_index - 1)` |
| Division by zero | Guard with `_denom > 0 ? ... : 0` |
| Alert spam | Use `varip` + reset on `barstate.isnew` |
| Wrong timeframe | Use `f_secDaily()` for 252-day calcs |
| **Multi-line ternary** | **Keep on single line (no line breaks)** |
| **if/else variable scope** | **Declare variable before if, use `:=` inside** |

### Syntax Gotchas (CRITICAL)

**1. Multi-line expressions cause "end of line" errors:**
```pine
// ❌ WRONG - breaks on multiple lines
status = condA ? "A" : 
         condB ? "B" : "C"

// ✅ CORRECT - single line
status = condA ? "A" : condB ? "B" : "C"
```

**2. Variables in if/else blocks have local scope:**
```pine
// ❌ WRONG - "Undeclared identifier" error
if condition
    myVar = "value1"
else
    myVar = "value2"
doSomething(myVar)  // ERROR!

// ✅ CORRECT - declare first, assign with :=
string myVar = ""
if condition
    myVar := "value1"
else
    myVar := "value2"
doSomething(myVar)  // OK
```

## Documentation Standards

**ALL user-facing text must be bilingual (English/Chinese):**
```pine
"Signal Mode 信号模式"                           // Input labels
tooltip="仅触发A/B级信号\nOnly trigger A/B grade"  // Tooltips (use \n)
```

## Quick Reference

```pine
//@version=6
indicator("RSI+Breadth Multi-Factor v7.4", overlay=true, max_labels_count=500, max_bars_back=1100)

// Function: f_name(_param) => result
// Multi-return: [a, b] = f_name(args)
// Security: request.security(sym, tf, expr, barmerge.gaps_off, barmerge.lookahead_off)
// Live data: request.security(sym, "D", expr, barmerge.gaps_off, barmerge.lookahead_on)
// Alert: alert(msg, alert.freq_all)
// Table: table.new(position, cols, rows, bgcolor, frame_color, ...)
```
