# AGENTS.md - RSI+ Breadth Multi-Factor Indicator

> Guidelines for AI coding agents working in this Pine Script repository.

## Project Overview

**Language**: Pine Script v6 (TradingView)  
**Type**: Quantitative trading indicator for US market timing  
**Main File**: `RSI+` (1135 lines)  
**Current Version**: v7.0  
**Documentation**: `README.md` (bilingual: English/Chinese)

Multi-factor scoring system combining RSI, Market Breadth, Volume Ratio, and Divergence for SPY, QQQ, and IWM signals.

---

## Build / Lint / Test Commands

Pine Script has **no local build system**. All validation happens in TradingView.

```bash
# Validation workflow:
# 1. Copy RSI+ contents to TradingView Pine Editor
# 2. Click "Add to Chart" - errors appear in console
# 3. Visual verification on SPY/QQQ/IWM charts

# Git operations (bilingual commit messages preferred)
git status
git add RSI+
git commit -m "feat: add feature / 新增功能"
```

### Testing Checklist

- [ ] Code compiles without errors in TradingView
- [ ] Signals render correctly on SPY, QQQ, IWM charts
- [ ] Dashboard displays properly (Full/Mobile modes)
- [ ] Alerts fire with correct message format
- [ ] Signal Zone backgrounds appear correctly (v7.0)
- [ ] README updated if user-facing features changed

---

## Code Style Guidelines

### File Structure

```pine
//@version=6
indicator("Name", overlay=true, max_labels_count=500, max_bars_back=1100)

//==============================================================================
// SECTION HEADER (ALL CAPS, BORDERED WITH =)
//==============================================================================

//========================
// Subsection Header
//========================

// Implementation...
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Functions | `f_` prefix, camelCase | `f_rsiScore()`, `f_signalQuality()` |
| Variables | camelCase | `spyScore`, `driverRSI` |
| Input groups | `grp` prefix | `grpMode`, `grpOptimize` |
| Parameters | Descriptive camelCase | `rsiLen`, `useDrawdownBonus` |

### Input Parameter Style

```pine
grpOptimize = "v7.0 Optimizations 胜率优化"

useSignalQuality = input.bool(true, "Signal Quality Filter 信号质量过滤", 
    group=grpOptimize,
    tooltip="仅触发A/B级信号\nOnly trigger A/B grade signals")
```

### Function Patterns

```pine
// Single return
f_rsiScore(_rsi, _os1, _os2, _ob1, _ob2) =>
    score = 0.0
    if not na(_rsi)
        if _rsi < _os1
            score := 2
    score

// Multi-return (tuple)
f_signalQuality(_rsiS, _fiS, _twS, _volS, _addS, _intraday) =>
    // ... calculations
    [buyQuality, sellQuality, positiveFactors, negativeFactors]
```

---

## Pine Script Patterns

### Security Requests

```pine
f_sec(_sym, _expr) =>
    request.security(_sym, tfData, _expr, barmerge.gaps_off, barmerge.lookahead_off)

f_secDaily(_sym, _expr) =>
    request.security(_sym, "D", _expr, barmerge.gaps_off, barmerge.lookahead_off)
```

### State Management

```pine
// Persistent across bars
var int spyLastBot = na

// Intrabar persistence (for alerts)
varip int buy_alert_level_sent = 0

// Reset on new bar
if barstate.isnew
    buy_alert_level_sent := 0
```

### Error Handling

```pine
// Always check na values
if not na(_rsi)
    // safe to use

// Clamp lookback to available history
safe_lookback = math.max(10, math.min(_lookback, bar_index - 1))

// Division by zero protection
ratio = _dvol > 0 ? _uvol / _dvol : 0
```

---

## v7.0 Key Features

| Feature | Function | Purpose |
|---------|----------|---------|
| Signal Quality Filter | `f_signalQuality()` | A/B grade only (2+ factors aligned) |
| Drawdown Bonus | `f_drawdownBonus()` | +1/+2/+3 at 5/10/20% drawdown |
| Divergence Assist | `f_divergenceAssisted()` | Edge signals boosted by divergence |
| Tiered Resonance | `f_resonanceStrength()` | Sync > Window > Single market |
| Signal Zone | `showSignalZone` input | Background highlighting |

---

## Signal Emoji Reference

| Signal | Emoji | Condition |
|--------|-------|-----------|
| Panic Low | 🚀 | score ≥ 6 |
| Buy Zone | 📈 | score ≥ 4 |
| Divergence | 💎 | Z-Score threshold |
| Elevated | ⭐ | score ≤ -4 + uptrend |
| Caution | ⚡ | score ≤ -4 + downtrend |
| Reduce | ⚠️ | score ≤ -6 + downtrend |
| Resonance Buy | 🔥 | 2+ markets in buy zone |
| Resonance Risk | ❄️ | 2+ markets in risk zone |

---

## Documentation Standards

**Bilingual requirement** - ALL docs must have English/Chinese:

```markdown
## Feature / 功能

English description.

中文描述。
```

---

## Quick Reference

```pine
// Indicator declaration
//@version=6
indicator("RSI+Breadth Multi-Factor v7.0", overlay=true, max_labels_count=500, max_bars_back=1100)

// Function pattern
f_functionName(_param1, _param2) =>
    result = 0.0
    // logic
    result

// Multi-return
[val1, val2] = f_multiReturn(args)

// Security call
data = request.security(symbol, timeframe, expr, barmerge.gaps_off, barmerge.lookahead_off)

// Alert (V2 Smart Alert)
alert(msg, alert.freq_once_per_bar)
```
