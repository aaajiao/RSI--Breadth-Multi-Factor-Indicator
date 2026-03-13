# AGENTS.md - RSI+ Breadth Multi-Factor Indicator

> Working rules for AI coding agents in this Pine Script repository.

## Project Overview

| Item | Value |
|------|-------|
| **Language** | Pine Script v6 |
| **Main file** | `RSI+` |
| **Current version** | `v7.4` |
| **Primary markets** | `SPY`, `QQQ`, `IWM` |
| **Use case** | US index market timing |

The script is a multi-factor indicator that combines:

- RSI
- Daily breadth (`TW`, `FI`)
- Intraday breadth (`ADD`, replacing daily breadth scoring in intraday mode)
- Up/Down volume ratio
- Divergence
- Trend filter
- Drawdown bonus
- Multi-market resonance
- Smart alerts

## Repository Files

| File | Role |
|------|------|
| `RSI+` | Source of truth for behavior |
| `README.md` | User-facing documentation; must match the script |
| `CLAUDE.md` | Claude Code entrypoint that imports this file |
| `AGENTS.md` | Agent-facing implementation guidance |

If script behavior changes, update `README.md` and `AGENTS.md` in the same change.

## Build / Test

There is no local Pine build or test runner in this repo.

Manual validation workflow:

1. Copy `RSI+` into TradingView Pine Editor
2. Click `Add to Chart`
3. Confirm it compiles without errors
4. Validate behavior on `SPY`, `QQQ`, `IWM`
5. Check both dashboard modes
6. Check buy, risk, divergence, resonance, and alert behavior

## Current Script Defaults

These values should stay synchronized with `RSI+`.

### Core Defaults

| Setting | Default |
|------|------|
| `mode` | `Standard` |
| `lookbackMode` | `Auto` |
| `lookbackCustom` | `252` |
| `lookbackPrecision` | `High` |
| `volHistoryMode` | `1 Year` |
| `thresholdMode` | `Auto` |
| `rsiVolThreshold` | `8.0` |
| `rsiLen` | `14` |
| `useLiveData` | `true` |

### Fixed RSI Threshold Defaults

| Input | Default |
|------|------|
| `fixedRsiOversold1` | `30` |
| `fixedRsiOversold2` | `40` |
| `fixedRsiOverbought1` | `75` |
| `fixedRsiOverbought2` | `65` |

### Signal Logic Defaults

| Setting | Default |
|------|------|
| `buyThresholdPct` | `50` |
| `sellThresholdPct` | `45` |
| `strongOffset` | `25` |
| `cooldownIn` | `10` |
| `useDynamicCooldown` | `true` |
| `confirmBars` | `3` |
| `minAgree` | `2` |

### Optimization Defaults

| Setting | Default |
|------|------|
| `useSignalQuality` | `true` |
| `useDrawdownBonus` | `true` |
| `useDivergenceAssist` | `true` |
| `useDivergence` | `true` |
| `divZScoreThreshold` | `1.7` |
| `divCooldownBars` | `5` |
| `trendMALen` | `10` |
| `useTrendFilter` | `true` |

### Display / Alert Defaults

| Setting | Default |
|------|------|
| `plotMode` | `AUTO` |
| `showDashboard` | `true` |
| `dashboardMode` | `Full` |
| `dashboardPosition` | `Top Right` |
| `dashboardFontSize` | `Small` |
| `showSignalZone` | `true` |
| `enable_smart_alert` | `true` |
| `min_alert_level_str` | `📈 Lv1 Buy Zone` |

## Scoring Model

### Factor Weights

Daily mode uses:

- `RSI`: `+2 / +1 / 0 / -1 / -2`
- `FI`: `+3 / +2 / +1 / 0 / -1 / -2`
- `TW`: `+1 / 0 / -1 / -2 / -3`
- `Vol ratio`: `+2 / +1 / 0 / -1 / -2`

Intraday mode changes breadth behavior:

- `ADD` replaces the daily `TW/FI` scoring block
- `TW` and `FI` factor scores are zeroed in this path
- `ADD`: `+3 / +2 / +1 / 0 / -1 / -2 / -3`

The script defines:

- `maxBuyScore = 8`
- `maxSellScore = 9`

### Threshold Formulas

```pine
botThreshold = int(maxBuyScore * buyThresholdPct / 100)
strongBotThreshold = int(maxBuyScore * (buyThresholdPct + strongOffset) / 100)
topThreshold = -int(maxSellScore * sellThresholdPct / 100)
strongTopThreshold = -int(maxSellScore * (sellThresholdPct + strongOffset) / 100)
```

With current defaults on standard daily charts:

- `BUY ZONE >= 4`
- `PANIC LOW >= 6`
- `CAUTION <= -4`
- `REDUCE <= -6`

Mode adjustments:

- `Aggressive` -> subtracts 1 from buy thresholds and adds 1 to sell thresholds
- `Conservative` -> inverse of aggressive
- `Intraday` -> applies an extra 2-point sensitivity adjustment

## Signal Semantics

These names must stay consistent across script comments, README, alerts, and docs.

| Display | Emoji | Trigger |
|------|------|------|
| `PANIC LOW` | `🚀` | `buyScore >= adjStrongBotThreshold` |
| `BUY ZONE` | `📈` | `buyScore >= adjBotThreshold` and below strong buy |
| `HOLD` | `⚪` | score is between buy and sell thresholds |
| `ELEVATED` | `⭐` | sell threshold reached while uptrend blocks the sell signal |
| `CAUTION` | `⚡` | sell threshold reached in non-uptrend state |
| `REDUCE` | `⚠️` | strong sell threshold reached in non-uptrend state |
| `DIVERGENCE` | `💎` | bullish or bearish divergence event |
| `RESONANCE` | `🔥 / ❄️` | multi-market agreement on buy or risk side |

Important nuance:

- In uptrends with `useTrendFilter = true`, sell-side states display as `ELEVATED` instead of `CAUTION` or `REDUCE`.
- Divergence is both a displayed overlay and a possible buy-side assist.
- Resonance is cross-market logic, not a single score threshold.

## Current Function Map

These functions define the main behavior and should be preserved when refactoring.

| Function | Purpose |
|------|------|
| `f_sec()` | Session-aware intraday security request |
| `f_ohlc()` | Session-aware OHLC request helper |
| `f_secDaily()` | Previous confirmed daily data request |
| `f_secDailyLive()` | Developing daily data for intraday alerts |
| `f_dynamicCooldown()` | Volatility-based cooldown adjustment |
| `f_signalQuality()` | A/B/C signal quality grading |
| `f_drawdownBonus()` | Buy-side drawdown bonus |
| `f_divergenceAssisted()` | Lets divergence push borderline buys through |
| `f_resonanceStrength()` | Tiered multi-market resonance |
| `f_adaptiveThresholds()` | Adaptive RSI bands from percentile math |
| `f_rsiScore()` | RSI factor score |
| `f_fiScore()` | FI breadth score |
| `f_twScore()` | TW breadth score |
| `f_volScore()` | UVOL/DVOL breadth score |
| `f_addScore()` | Intraday ADD breadth score |
| `f_divergence()` | Price/RSI divergence z-score |
| `f_totalScore()` | Total factor score |
| `f_generateSignals()` | Buy/sell/elevated state generation |
| `f_progressBar()` | Horizontal factor bar |
| `f_centeredBar()` | Centered score bar |
| `f_marketStatus()` | Three-market status icon |

## Dashboard Reference

The actual rendered layouts in `RSI+` are:

### Full Mode

- `7 rows x 1 column`
- Row 0: signal + score + trend
- Row 1: centered score bar
- Row 2: RSI + volume
- Row 3: `FI + TW` in daily mode, `ADD + TW` in intraday mode; the compact `TW` slot still renders in intraday mode even though `ADD` drives the breadth score there
- Row 4: trend + divergence + quality
- Row 5: drawdown + filter status
- Row 6: `SPY / QQQ / IWM` status + resonance icon

### Mobile Mode

- `2 rows x 1 column`
- Row 0: signal + score + trend
- Row 1: filter status

Do not document old `11-row` or `3-row` layouts. The current output code is `7` and `2`.

## Filter Status Rules

`filterStatus` currently maps to:

| Label | Meaning |
|------|------|
| `👀` | no active filter block |
| `✋ WAIT` | buy-zone score exists but signal is filtered out |
| `☕ HOLD` | sell threshold hit but uptrend blocks the sell |
| `🚫` | downtrend buy-zone score while trend filter is active |

## Alert System

Smart Alert V2 levels:

| Level | Meaning |
|------|------|
| `Lv1` | `BUY ZONE`, `CAUTION`, `ELEVATED` |
| `Lv2` | `DIVERGENCE` |
| `Lv3` | `RESONANCE` |
| `Lv4` | `PANIC LOW`, `REDUCE` |
| `Lv5` | strong signal + resonance combo |

Implementation details that matter:

- Smart alerts must reuse the plotted `Trig / Edge` signals (`spyBotTrig`, `spyTopTrig`, `aggBottomEdge`, divergence/elevated edges, etc.); do not drive published alerts directly from raw active state.
- The script uses `varip` state to deduplicate alerts within the same bar.
- Same-bar alert upgrades are allowed if a higher level appears later in the bar.
- Buy and sell alert states are tracked separately.
- Cross-bar alert state suppresses repeated alerts while the same side remains active at the same or lower level.
- On `intradayMode + useLiveData`, same-side alerts are latched for the full regular session and only re-arm at the next regular-session open.
- Live intraday same-level repeats and downgrades stay muted during the current regular session; only strict upgrades may publish after the first alert.
- `ELEVATED` is an entry/upgrade alert state, not a per-bar repeating alert.
- Intraday smart alerts must be limited to `session.ismarket`; after-hours bars may update price, but they must not publish new alerts.
- Alert messages include ticker, side, level, signal tags, score, trend, and drawdown context where applicable.

## Pine Script Rules Specific To This Repo

### Security Requests

Use the existing helpers:

```pine
f_intradayTicker(_sym) =>
    intradayMode ? ticker.modify(_sym, syminfo.session) : _sym

f_sec(_sym, _expr) =>
    request.security(f_intradayTicker(_sym), tfData, _expr, intradayMode ? barmerge.gaps_on : barmerge.gaps_off, barmerge.lookahead_off)

f_secDaily(_sym, _expr) =>
    request.security(_sym, "D", _expr[1], barmerge.gaps_off, barmerge.lookahead_on)

f_secDailyLive(_sym, _expr) =>
    request.security(_sym, "D", _expr, barmerge.gaps_off, barmerge.lookahead_on)
```

Rules:

- Do not introduce lookahead bias outside `f_secDailyLive()`.
- Intraday SPY / QQQ / IWM / ADD requests should inherit the chart session modifier.
- `ADD`, `TW/FI`, and `UVOL/DVOL` live values should freeze outside `session.ismarket`; do not let regular-session values drift through post-market bars.

### State and Cooldown

Use persistent state for bar-to-bar tracking:

```pine
var int spyLastBot = na
varip int buy_alert_level_sent = 0
varip int buy_alert_level_published = 0
varip bool buy_alert_armed = true
varip int buy_alert_latched_level = 0

if barstate.isnew
    buy_alert_level_sent := 0
```

### Defensive Coding

Always guard:

- `na` values before comparisons
- divisions with zero checks
- lookback length with `math.min(..., bar_index)`
- multi-line ternaries by keeping them on one line
- cross-scope assignment by declaring variables first and using `:=`

## Documentation Rules

- `README.md` must describe the current script behavior, not legacy versions.
- Any user-facing signal list must include `PANIC LOW`, `BUY ZONE`, `HOLD`, `ELEVATED`, `CAUTION`, `REDUCE`, `DIVERGENCE`, and `RESONANCE`.
- Dashboard docs must reflect `Full = 7 rows` and `Mobile = 2 rows`.
- Alert docs must reflect the current `Lv1` to `Lv5` level system.
- All user-facing text added to the script should remain bilingual (`English / 中文`).

## Validation Checklist

- [ ] Script compiles in TradingView
- [ ] SPY / QQQ / IWM logic still works
- [ ] Daily and intraday paths both behave correctly
- [ ] Extended-session intraday charts do not publish any smart alerts after the regular close
- [ ] Dashboard Full/Mobile output matches docs
- [ ] Alert labels and thresholds match docs
- [ ] README updated when behavior changes
