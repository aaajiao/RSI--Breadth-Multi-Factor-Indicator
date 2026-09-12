# RSI+ Breadth Multi-Factor Indicator v7.6

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
- **Smart alerts V2**: level-based alerts keyed to the latest bar's first visible K-line signal, with bar-level dedup and cross-bar upgrade logic.

### v7.6 Reliability and Adaptive Updates

- Only realtime publications consume alert state. Loading historical bars cannot mute the first subsequent live reminder.
- Intrabar events retained on the chart also update cooldowns and resonance history, including strict strong-signal upgrades and divergence cooldowns.
- The panel, signal background, and alert side use the highest visible event level on the current bar; equal levels favor buy. Both accepted chart markers remain visible if opposite sides fired intrabar. The first notification is retained: a later same-bar upgrade does not send a second notification.
- Lookback lengths (`Auto`, `Fixed 252`, `Custom`) count current-chart bars; `Fixed 252` means 252 chart bars, not one calendar year on intraday charts.
- Each market computes its own adaptive bands, lookback, and cooldown. Manual display selection does not switch another market's volatility into its calculations.
- `Vol History` now means **126 / 252 / 504 confirmed daily RSI samples** for `6 Months / 1 Year / 2 Years`. This daily baseline is combined with each market's current-chart RSI volatility. It is no longer capped to the same 1000 intraday bars for all settings. This changes intraday adaptive results compared with v7.5.
- A temporary data gap preserves accepted panel/zone state and does not re-arm daily/confirmed-mode alerts. The UI shows WAIT DATA and hides the background until inputs recover; only a valid HOLD condition may clear the retained state.
- During statistical warmup, Auto lookback uses available shorter-term volatility; unavailable adaptive bands fall back to the configured fixed bands. Missing required price or factor data blocks new signals and shows `WAIT DATA / 等待数据`.
- Confirmed/developing values share a daily tuple request per breadth source. Daily market context also batches the confirmed 252-day closing high, long-term volatility, and sample count. No speedup percentage has been measured in Pine Profiler.
- Supported chart intervals are time-based intraday bars and **1D**. Multi-day, weekly, monthly, and tick charts are rejected explicitly. Fixed RSI bands must be strictly ordered; RSI Length is limited to 2–250 to fit the history buffer.

### Markets and Data Sources

- **Tracked markets**: `SPY`, `QQQ`, `IWM`
- **Breadth inputs**:
  - SPY: `S5TW`, `S5FI`
  - QQQ: `NCTW`, `NCFI`
  - IWM: `R2TW`, `R2FI`
- **Volume breadth**:
  - NYSE: `UVOL`, `DVOL`
  - NASDAQ: `UVOLQ`, `DVOLQ`
- **Intraday breadth proxy**: `ADD`; during the regular session, missing ADD values fall back to the previous valid value (na-guard) so the score does not transiently drop, and the last regular-session value is frozen after the close
- **Confirmed daily data**: the confirmed leg of `f_secDailyLive()` and the `f_secDaily()` helper use the previous fully confirmed daily value
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
- Sensitivity direction: a lower `Buy/Sell Sensitivity` % means a lower threshold and more sensitive signals; a higher % is stricter (the input tooltips were corrected to this direction in v7.5; the formulas themselves are unchanged)

Mode adjustments:

- `Aggressive`: lowers buy thresholds and relaxes sell thresholds by 1 point
- `Conservative`: raises buy thresholds and tightens sell thresholds by 1 point
- `Intraday`: applies an extra 2-point sensitivity adjustment
- Final weak thresholds are bounded to buy `>= +1` and risk `<= -1`; strong thresholds stay at least 1 point beyond the corresponding weak threshold. Standard daily defaults remain `4 / 6 / -4 / -6`. Opposite sides can still coincide because buy scores may include a drawdown bonus or divergence assist; the event-level arbitration above handles that case.

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
| Buy resonance | `minAgree` markets align in buy window (default 2) | `🔥` | `RESONANCE` | Multi-market long confirmation |
| Risk resonance | `minAgree` markets align in risk window (default 2) | `❄️` | `RESONANCE` | Multi-market risk confirmation |

Important behavior:

- `ELEVATED` is not just a weaker sell signal. It is the actual display state when sell thresholds are hit but the trend filter keeps the script from issuing `CAUTION` or `REDUCE`.
- `ELEVATED` respects the Signal Quality Filter the same way `CAUTION` and `REDUCE` do: C-grade conditions do not display or alert as `ELEVATED`.
- Divergence is a separate overlay signal and can also assist borderline buy signals when `Divergence Assist` is enabled.
- Resonance is based on multi-market agreement, not a single-market score.

### Filters and Enhancements

#### Signal Quality Filter

`f_signalQuality()` grades signals as:

- `A`: 3+ aligned factors
- `B`: 2 aligned factors
- `C`: fewer than 2 aligned factors

When `Signal Quality Filter` is enabled, only `A` and `B` signals can trigger buys or sells. The gate also applies to `ELEVATED`, so C-grade conditions cannot display or alert as `ELEVATED` either.

#### Drawdown Bonus

`f_drawdownBonus()` adds buy-side score only:

- `>= 5%` drawdown: `+1`
- `>= 10%` drawdown: `+2`
- `>= 20%` drawdown: `+3`

This bonus affects buy evaluation and the buy/neutral dashboard score. Risk panel states and risk alerts use the raw sell score. The DD row labels any enabled bonus as buy-side only; disabling the bonus removes that annotation.

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
| 3 | Daily: `FI + TW`; intraday: `ADD` plus actual confirmed daily RSI history coverage, e.g. `Hist/历史:126/252D` |
| 4 | Trend + divergence + current factor quality for the panel side (`B/买` or `S/卖`); `/3` intraday, `/4` daily. AGG grades its floored mean aligned-factor count and does not display hidden divergence events |
| 5 | Drawdown + enabled buy-only bonus + filter/data status, e.g. `DD8% B/买+1` |
| 6 | Raw factor status for `SPY/QQQ/IWM` plus resonance icon; gray = data unavailable, red = raw sell threshold met, otherwise green = buy threshold met, yellow = neutral. These dots do not apply signal-quality or trend filters |

#### Mobile Mode

Actual layout in code: **2 rows x 1 column**

| Row | Content |
|---:|---|
| 0 | Signal + score + trend |
| 1 | Filter status only |

#### Filter Status Labels

| Display | Condition in script | Meaning |
|---|---|---|
| `WAIT DATA / 等待数据` | Required price/factor data missing | New signals disabled |
| `WARMUP / 预热` | Adaptive statistics still warming up | Shorter-term volatility or fixed RSI bands in use |
| `👀` | No active filter block | Watching |
| `✋ WAIT` | Score reaches buy zone but signal is filtered | Buy score is there, confirmation is not |
| `☕ HOLD` | Raw sell score (no drawdown bonus) reaches sell threshold, but uptrend blocks sell signal | Trend says hold risk cautiously |
| `🚫` | Buy-zone score in downtrend with trend filter active and no buy signal plotted | Bear-market style risk filter |

Two consistency details:

- `☕ HOLD` plus the hold-zone / zone-exit detection (signal-zone background) all compare the raw sell score (no drawdown bonus) against the sell threshold, so a large drawdown bonus pushing up the displayed score cannot misalign the filter status with the actual sell-threshold logic.
- `🚫` only shows when no buy signal is plotted or active, so it never contradicts an on-chart `BUY ZONE` marker.

#### How To Read `filterStatus` And `signalText`

`filterStatus` and the main signal line do different jobs:

- `filterStatus` tells you whether the setup is being blocked by a filter.
- In `SPY / QQQ / IWM` display modes, `signalText` follows the latest plotted chart signal state, with same-bar conflicts resolved by visible event level.
- On realtime bars, accepted markers survive a raw-condition fade. If both sides are visible, the dashboard uses the higher event level (buy on a tie); `ELEVATED` also enters the risk background zone. AGG displays `RESONANCE` and only publishes Lv3.
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
- `Lv2 (DIVERGENCE)` and `Lv3 (RESONANCE)` are upgrade tags on a visible base buy/risk trigger; divergence-only or resonance-only states do not publish hidden standalone alerts
- Resonance upgrades apply on every display path: on `SPY / QQQ / IWM`, a visible base buy/risk trigger that coincides with the resonance edge on the same bar publishes `Lv3` (base + resonance) or `Lv5` (strong + resonance, e.g. `PANIC LOW + RESONANCE`)
- Smart alerts publish when the latest realtime bar first shows a visible trigger level on that tick; later historical backfill does not cancel or replay that reminder
- On realtime bars, plotted signals are bar-latched: once a buy/risk marker fires intrabar, that bar keeps the marker and aligned panel state after the close
- Same-level or downgraded alerts do not re-fire inside the same bar even if the live condition flickers off and back on
- `PANIC LOW` / `REDUCE` upgrades from an already-active `BUY ZONE` / `CAUTION` still count as fresh strict upgrades for chart markers; alert upgrades now publish only on later bars
- Smart alerts are limited to one publish per bar; if both buy and risk qualify on the same tick, only the higher-level side publishes
- `varip` state remembers the latest bar's observed visible level, so same-bar flicker or later historical backfill does not erase the first reminder
- Published alert levels also use rollback-safe `varip` state, so realtime bars do not re-fire the same level on each tick
- In manual `SPY / QQQ / IWM` display modes, AGG resonance does not publish a separate hidden-symbol alert path; resonance-only alerts remain on the `AGG(共振)` path
- The `AGG(共振)` path publishes `Lv3` only, since it has no strong-signal or divergence states of its own
- On `intraday + Live Alert Data`, same-side alerts are latched for the regular session, so Lv1 does not re-fire repeatedly during the day
- Live intraday re-arms those side latches on the first regular-session bar of each new trading day (date-key detection), which also works on RTH-only charts that have no extended-hours session transition; same-level repeats and downgrades stay muted during the current session
- After-hours bars never publish alerts and never re-arm the latches; extended-hours behavior is unchanged
- Live intraday still allows strict level upgrades only across later bars (`Lv1 -> Lv3/4/5`)
- Cross-bar alert state suppresses repeated alerts while the same side stays active at the same or lower level
- Buy and risk alerts are tracked separately
- `ELEVATED` alerts fire on entry or later level upgrades, not on every new bar
- Intraday charts can use live daily data if `Live Alert Data` is enabled
- On intraday charts, smart alerts are limited to regular market hours; after the close the script still freezes breadth snapshots, but it does not publish after-hours alerts

### Known Limitations

These limitations are inherent to the current design and worth knowing before trusting historical markers:

- **Historical intraday markers are not a backtest.** On intraday charts, historical bars use end-of-day daily breadth values (`f_secDailyLive()` requests with lookahead), so historical intraday markers can look better than what realtime would have shown. Realtime alerts use developing values instead.
- **Daily charts lag breadth by one day.** On daily charts, breadth and volume factors come from the previous confirmed day through the confirmed daily request leg. The `Live Alert Data` option only affects intraday charts.
- **Futures support is best-effort.** Futures tickers (`ES` / `NQ` / `RTY` etc.) are detected best-effort by ticker matching. Session gating and breadth freezing are designed for US equity regular hours and are not validated for futures sessions.

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

Local behavioral regression checks use the Python standard library:

```sh
python3 -m unittest discover -s tests -v
```

These checks exercise selected source helpers, state transitions, and source wiring. They are **not a Pine compiler**, a TradingView execution engine, a performance benchmark, or a strategy backtest. TradingView compilation and chart validation remain required:

1. Copy `RSI+` into TradingView Pine Editor
2. Click `Add to Chart`
3. Verify behavior on `SPY`, `QQQ`, `IWM`
4. Check both `Full` and `Mobile` dashboard modes
5. Check buy, risk, divergence, and resonance labels against the script logic above
6. On extended-hours intraday charts, confirm there are no after-hours smart alerts after the regular close
7. On RTH-only intraday charts with `Live Alert Data`, confirm same-side alert latches re-arm on the first regular-session bar of a new trading day
8. Create a fresh alert mid-session after historical signals; verify that history has not consumed live notification state
9. Verify intrabar trigger/fade, cooldown, resonance window, weak-to-strong upgrade, and opposite-side events; historical replay alone cannot reconstruct realtime ticks
10. Compare manual QQQ display on SPY/QQQ charts with the same timeframe/session, check all Vol History settings, warmup, and rejected input combinations
11. After compiling an updated script, recreate running TradingView alerts: existing alerts retain the script/input snapshot from their creation

---

## Disclaimer | 免责声明

This indicator is for educational purposes only. Past performance does not guarantee future results.

**Version**: 7.6 | **Pine Script**: v6 | **Updated**: 2026-09-12
