# RSI+ Breadth Multi-Factor Indicator v7.4

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/scripts/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-reference/v6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English | [中文文档](docs/README_CN.md)

RSI+ is a Pine Script v6 market-timing indicator for US index markets. The current script targets **SPY**, **QQQ**, and **IWM**, and combines **RSI**, **breadth**, **volume breadth**, **divergence**, **trend filter**, and **multi-market resonance** into a single decision framework.

---

### Overview

The current `RSI+` script implements these modules:

- **Core score engine**: RSI + breadth + volume breadth.
- **Daily breadth mode**: uses TW/FI series for SPY, QQQ, IWM.
- **Intraday breadth mode**: replaces the daily `TW/FI` scoring block with `ADD` intraday breadth.
- **Adaptive threshold system**: auto lookback, volatility-driven threshold selection, adaptive RSI bands.
- **Signal quality filter**: only A/B-grade signals pass when enabled.
- **Drawdown bonus**: adds buy-side score in 5% / 10% / 20% drawdown states.
- **Divergence system**: bullish and bearish RSI-price divergence with cooldown.
- **Trend filter**: converts sell-side signals into `ELEVATED` during uptrends.
- **Resonance engine**: detects multi-market agreement across SPY / QQQ / IWM.
- **Dashboard**: compact `Full` and `Mobile` modes.
- **Smart alerts V2**: level-based alerts with same-bar upgrade logic.

### Markets and Data Sources

- **Tracked markets**: `SPY`, `QQQ`, `IWM`
- **Breadth inputs**:
  - SPY: `S5TW`, `S5FI`
  - QQQ: `NCTW`, `NCFI`
  - IWM: `R2TW`, `R2FI`
- **Volume breadth**:
  - NYSE: `UVOL`, `DVOL`
  - NASDAQ: `UVOLQ`, `DVOLQ`
- **Intraday breadth proxy**: `ADD`
- **Confirmed daily helper**: `f_secDaily()` now returns the previous fully confirmed daily value
- **Intraday live alert mode**: `f_secDailyLive()` can use developing daily values during regular market hours, then freezes breadth/volume snapshots after the close
- **Intraday session handling**: SPY / QQQ / IWM / ADD intraday requests inherit the chart session modifier so extended-hours charts only react to real post-market bars

### Score Model

Default theoretical score ranges in the script:

| Component | Buy-side max | Sell-side min | Notes |
|---|---:|---:|---|
| RSI | `+2` | `-2` | Adaptive or fixed bands |
| FI breadth | `+3` | `-2` | Daily mode only |
| TW breadth | `+1` | `-3` | Daily mode only |
| Volume ratio | `+2` | `-2` | `UVOL / DVOL` or `UVOLQ / DVOLQ` |
| ADD breadth | `+3` | `-3` | Intraday mode only; daily `TW/FI` score inputs are zeroed in this path |
| Drawdown bonus | `+1 / +2 / +3` | `0` | Buy-side only |

Default threshold math:

- `maxBuyScore = 8`
- `maxSellScore = 9`
- `Buy Sensitivity = 50%` -> `BUY ZONE >= 4`
- `Buy strong offset = +25%` -> `PANIC LOW >= 6`
- `Sell Sensitivity = 45%` -> `CAUTION <= -4`
- `Sell strong offset = +25%` -> `REDUCE <= -6`

Mode adjustments:

- `Aggressive`: lowers buy thresholds and relaxes sell thresholds by 1 point
- `Conservative`: raises buy thresholds and tightens sell thresholds by 1 point
- `Intraday`: applies an extra 2-point sensitivity adjustment

### Signal Reference

The script currently uses the following signal names and emojis:

| Type | Trigger in script | Emoji | Label | Meaning |
|---|---|---|---|---|
| Strong buy | `buyScore >= adjStrongBotThreshold` | `🚀` | `PANIC LOW` | Extreme oversold, strongest long setup |
| Buy | `buyScore >= adjBotThreshold` | `📈` | `BUY ZONE` | Standard accumulation zone |
| Neutral | Between buy/sell thresholds | `⚪` | `HOLD` | No active edge |
| Uptrend risk | Sell threshold reached while `price > trend MA` and trend filter is on | `⭐` | `ELEVATED` | Overbought, but trend still strong |
| Risk | `sellScore <= adjTopThreshold` in non-uptrend | `⚡` | `CAUTION` | Take-profit / risk-control zone |
| Strong risk | `sellScore <= adjStrongTopThreshold` in non-uptrend | `⚠️` | `REDUCE` | Highest sell/risk state |
| Bullish divergence | `divStrength < -threshold` and RSI below `OS2` | `💎` | `DIVERGENCE` | Reversal assist / confirmation |
| Bearish divergence | `divStrength > threshold` and RSI above `OB2` | `💎` | `DIVERGENCE` | Risk reversal warning |
| Buy resonance | 2+ markets align in buy window | `🔥` | `RESONANCE` | Multi-market long confirmation |
| Risk resonance | 2+ markets align in risk window | `❄️` | `RESONANCE` | Multi-market risk confirmation |

Important behavior:

- `ELEVATED` is not just a weaker sell signal. It is the actual display state when sell thresholds are hit but the trend filter keeps the script from issuing `CAUTION` or `REDUCE`.
- Divergence is a separate overlay signal and can also assist borderline buy signals when `Divergence Assist` is enabled.
- Resonance is based on multi-market agreement, not a single-market score.

### Filters and Enhancements

#### Signal Quality Filter

`f_signalQuality()` grades signals as:

- `A`: 3+ aligned factors
- `B`: 2 aligned factors
- `C`: fewer than 2 aligned factors

When `Signal Quality Filter` is enabled, only `A` and `B` signals can trigger buys or sells.

#### Drawdown Bonus

`f_drawdownBonus()` adds buy-side score only:

- `>= 5%` drawdown: `+1`
- `>= 10%` drawdown: `+2`
- `>= 20%` drawdown: `+3`

This bonus affects buy evaluation and dashboard score, but not sell-side thresholds.

#### Divergence Assist

When enabled, bullish divergence can push a buy signal through even if the score is still **1-2 points below** the buy threshold.

#### Dynamic Cooldown

Cooldown becomes:

- shorter in high volatility
- unchanged in normal volatility
- longer in low volatility

The script preserves a minimum cooldown of 3 bars unless the base cooldown is set to 0.

### Dashboard

The current script renders two dashboard modes.

#### Full Mode

Actual layout in code: **7 rows x 1 column**

| Row | Content |
|---:|---|
| 0 | Signal + score + trend, e.g. `🚀 PANIC LOW +6.5↑` |
| 1 | Centered score bar |
| 2 | RSI score + volume score |
| 3 | `FI + TW` in daily mode, or `ADD + TW` in intraday mode; current code keeps the compact `TW` slot even though intraday breadth scoring is driven by `ADD` |
| 4 | Trend + divergence + quality, e.g. `↑UP 💎B A3/4` |
| 5 | Drawdown + filter status, e.g. `DD8%+2 ✋ WAIT` |
| 6 | `SPY/QQQ/IWM` status plus resonance icon |

#### Mobile Mode

Actual layout in code: **2 rows x 1 column**

| Row | Content |
|---:|---|
| 0 | Signal + score + trend |
| 1 | Filter status only |

#### Filter Status Labels

| Display | Condition in script | Meaning |
|---|---|---|
| `👀` | No active filter block | Watching |
| `✋ WAIT` | Score reaches buy zone but signal is filtered | Buy score is there, confirmation is not |
| `☕ HOLD` | Sell threshold reached, but uptrend blocks sell signal | Trend says hold risk cautiously |
| `🚫` | Buy-zone score in downtrend with trend filter active | Bear-market style risk filter |

#### How To Read `filterStatus` And `signalText`

`filterStatus` and the main signal line do different jobs:

- `filterStatus` tells you whether the setup is being blocked by a filter.
- In `SPY / QQQ / IWM` display modes, `signalText` follows the latest plotted chart signal state, so the dashboard stays aligned with the K-line marker sequence.
- On realtime bars, once a plotted buy/risk marker fires intrabar, the dashboard keeps that bar's latest plotted state instead of reverting if the raw condition fades before close.
- `signalText` tells you the current displayed market state: `PANIC LOW`, `BUY ZONE`, `HOLD`, `ELEVATED`, `CAUTION`, or `REDUCE`.

Read them together:

- `👀 + ⚪ HOLD`: no active filter block, but there is still no buy signal. This is a clean neutral state, not an entry by itself.
- `👀 + 📈 BUY ZONE`: the chart is in the buy zone and no filter is blocking it. This is the standard valid buy window.
- `👀 + 🚀 PANIC LOW`: the chart is in the stronger buy state and no filter is blocking it.

### Smart Alerts V2

The script now uses a level system:

| Level | Trigger |
|---:|---|
| `Lv1` | `BUY ZONE`, `CAUTION`, or `ELEVATED` |
| `Lv2` | `DIVERGENCE` |
| `Lv3` | `RESONANCE` |
| `Lv4` | `PANIC LOW` or `REDUCE` |
| `Lv5` | `PANIC LOW + RESONANCE` or `REDUCE + RESONANCE` |

Alert behavior:

- Smart alerts reuse the same `Trig / Edge` signals that drive plotted chart markers, instead of firing directly from raw live state
- Smart alerts follow the currently displayed plotted K-line signal path, so manual `Display Mode` changes stay visually aligned with alerts
- On realtime bars, plotted signals are bar-latched: once a buy/risk marker fires intrabar, that bar keeps the marker and aligned panel state after the close
- Same-level or downgraded alerts do not re-fire inside the same bar even if the live condition flickers off and back on
- `PANIC LOW` / `REDUCE` upgrades from an already-active `BUY ZONE` / `CAUTION` still count as fresh strict upgrades for both chart markers and alerts
- Same-bar upgrade alerts are allowed
- `varip` state prevents duplicate lower-level alerts in the same bar
- Published alert levels also use rollback-safe `varip` state, so realtime bars do not re-fire the same level on each tick
- In manual `SPY / QQQ / IWM` display modes, AGG resonance does not publish a separate hidden-symbol alert path; resonance-only alerts remain on the `AGG(共振)` path
- On `intraday + Live Alert Data`, same-side alerts are latched for the regular session, so Lv1 does not re-fire repeatedly during the day
- Live intraday resets those side latches only at the next regular-session open; same-level repeats and downgrades stay muted during the current session
- Live intraday still allows strict level upgrades only (`Lv1 -> Lv3/4/5`)
- Cross-bar alert state suppresses repeated alerts while the same side stays active at the same or lower level
- Buy and risk alerts are tracked separately
- `ELEVATED` alerts fire on entry or later level upgrades, not on every new bar
- Intraday charts can use live daily data if `Live Alert Data` is enabled
- On intraday charts, smart alerts are limited to regular market hours; after the close the script still freezes breadth snapshots, but it does not publish after-hours alerts

### Recommended Defaults

Current defaults in the script:

| Setting | Default |
|---|---|
| Signal Mode | `Standard` |
| Lookback Mode | `Auto` |
| Precision | `High` |
| Vol History | `1 Year` |
| Threshold Mode | `Auto` |
| RSI Vol Threshold | `8.0` |
| RSI Length | `14` |
| Dynamic Cooldown | `true` |
| Resonance Window | `3` |
| Min Markets | `2` |
| Signal Quality Filter | `true` |
| Drawdown Bonus | `true` |
| Divergence Assist | `true` |
| Divergence | `true` |
| Divergence Threshold | `1.7` |
| Trend Filter | `true` |
| Dashboard Mode | `Full` |
| Smart Alert | `true` |
| Min Alert Level | `Lv1 Buy Zone` |

### Validation

Pine Script has no local build system in this repo. Validation is manual:

1. Copy `RSI+` into TradingView Pine Editor
2. Click `Add to Chart`
3. Verify behavior on `SPY`, `QQQ`, `IWM`
4. Check both `Full` and `Mobile` dashboard modes
5. Check buy, risk, divergence, and resonance labels against the script logic above
6. On extended-hours intraday charts, confirm there are no after-hours smart alerts after the regular close

---

## Disclaimer | 免责声明

This indicator is for educational purposes only. Past performance does not guarantee future results.

**Version**: 7.4 | **Pine Script**: v6 | **Updated**: 2026-03-11
