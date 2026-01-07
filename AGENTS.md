# AGENTS.md - RSI+ Breadth Multi-Factor Indicator

> Guidelines for AI coding agents working in this Pine Script repository.

## Project Overview

| Item | Value |
|------|-------|
| **Language** | Pine Script v6 (TradingView) |
| **Main File** | `RSI+` (~1200 lines) |
| **Version** | v7.2 |
| **Purpose** | US market timing for SPY, QQQ, IWM |

Multi-factor scoring: RSI + Market Breadth (TW/FI) + Volume Ratio + Divergence.

---

## Build / Lint / Test

Pine Script has **no local build/test system**. Validation is manual in TradingView.

```bash
# Workflow:
# 1. Copy RSI+ to TradingView Pine Editor
# 2. Click "Add to Chart" - errors appear in console
# 3. Visual verification on SPY/QQQ/IWM daily charts

# Git (bilingual commits preferred)
git add RSI+
git commit -m "feat: description / 中文描述"
```

### Validation Checklist
- [ ] Compiles without errors in TradingView
- [ ] Signals render on SPY, QQQ, IWM charts
- [ ] Dashboard displays (Full/Mobile modes)
- [ ] Alerts fire correctly
- [ ] README updated if user-facing changes

---

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
| Functions | `f_` prefix + camelCase | `f_rsiScore()`, `f_signalQuality()` |
| Variables | camelCase | `spyScore`, `displayUptrend` |
| Input groups | `grp` prefix | `grpMode`, `grpOptimize` |
| Function params | `_` prefix | `_rsi`, `_lookback` |

### Input Parameters
```pine
grpOptimize = "v7.0 Optimizations 胜率优化"

useSignalQuality = input.bool(true, "Signal Quality Filter 信号质量过滤", 
    group=grpOptimize,
    tooltip="仅触发A/B级信号\nOnly trigger A/B grade signals")
```

### Functions
```pine
// Single return - always end with result variable
f_rsiScore(_rsi, _os1, _os2, _ob1, _ob2) =>
    score = 0.0
    if not na(_rsi)
        if _rsi < _os1
            score := 2
    score

// Multi-return tuple
f_signalQuality(_rsiS, _fiS, _twS, _volS, _addS, _intraday) =>
    // calculations...
    [buyQuality, sellQuality, positiveFactors, negativeFactors]
```

---

## Pine Script Patterns

### Security Requests (CRITICAL)
```pine
// Always use barmerge.gaps_off + barmerge.lookahead_off
f_sec(_sym, _expr) =>
    request.security(_sym, tfData, _expr, barmerge.gaps_off, barmerge.lookahead_off)
```

### State Management
```pine
var int spyLastBot = na              // Persistent across bars
varip int buy_alert_level_sent = 0   // Intrabar persistence (for alerts)

if barstate.isnew
    buy_alert_level_sent := 0        // Reset on new bar
```

### Error Handling (MANDATORY)
```pine
if not na(_rsi)                      // Always check na
    // safe to use

safe_lookback = math.max(10, math.min(_lookback, bar_index - 1))  // Clamp lookback
ratio = _dvol > 0 ? _uvol / _dvol : 0                             // Division guard
```

---

## Signal Reference

| Score | Emoji | Signal | Condition |
|:-----:|:-----:|--------|-----------|
| ≥ 6 | 🚀 | PANIC LOW | Extreme oversold + panic |
| ≥ 4 | 📈 | BUY ZONE | Multi-factor buy |
| DIV | 💎 | DIVERGENCE | Z-Score threshold |
| ≤ -4↑ | ⭐ | ELEVATED | Overbought + uptrend |
| ≤ -4↓ | ⚡ | CAUTION | Overbought + downtrend |
| ≤ -6↓ | ⚠️ | REDUCE | Extreme overbought |
| 2+ mkts | 🔥 | RESONANCE BUY | Multi-market bullish |
| 2+ mkts | ❄️ | RESONANCE RISK | Multi-market bearish |

---

## v7.x Key Features

| Feature | Function | Purpose |
|---------|----------|---------|
| Signal Quality | `f_signalQuality()` | A/B/C grade (factor alignment) |
| Drawdown Bonus | `f_drawdownBonus()` | +1/+2/+3 at 5/10/20% DD |
| Divergence Assist | `f_divergenceAssisted()` | Boost edge signals |
| Tiered Resonance | `f_resonanceStrength()` | Sync > Window > Single |
| Progress Bar | `f_progressBar()`, `f_centeredBar()` | v7.2 visual dashboard |

---

## Documentation Standards

**Bilingual required** - ALL user-facing text must have English/Chinese:
```pine
"Signal Mode 信号模式"                           // Input labels
tooltip="仅触发A/B级信号\nOnly trigger A/B grade"  // Tooltips with \n
```

---

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| `na` errors | Always check `not na(value)` before use |
| Lookahead bias | Use `barmerge.lookahead_off` |
| History overflow | Clamp with `math.min(_lookback, bar_index - 1)` |
| Division by zero | Guard with `_denom > 0 ? ... : 0` |
| Alert spam | Use `varip` + reset on `barstate.isnew` |

---

## Quick Reference
```pine
//@version=6
indicator("RSI+Breadth Multi-Factor v7.2", overlay=true, max_labels_count=500, max_bars_back=1100)

// Function: f_name(_param) => result
// Multi-return: [a, b] = f_name(args)
// Security: request.security(sym, tf, expr, barmerge.gaps_off, barmerge.lookahead_off)
// Alert: alert(msg, alert.freq_once_per_bar)
// Table: table.new(position, cols, rows, bgcolor, frame_color, ...)
```
