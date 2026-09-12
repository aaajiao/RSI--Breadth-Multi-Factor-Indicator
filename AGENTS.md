# AGENTS.md - RSI+ Breadth Multi-Factor Indicator

> Working rules for AI coding agents in this Pine Script repository.

## Project Overview

| Item | Value |
|------|-------|
| **Language** | Pine Script v6 |
| **Main file** | `RSI+` |
| **Current version** | `v7.6` |
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
| `README.md` | English user documentation; must match the script |
| `docs/README_CN.md` | Chinese user documentation; update with README |
| `tests/` | Standard-library Python regression checks; not a Pine compiler |
| `CLAUDE.md` | Claude Code entrypoint that imports this file |
| `AGENTS.md` | Agent-facing implementation guidance |

If script behavior changes, update `README.md`, `docs/README_CN.md`, and `AGENTS.md` in the same change.

## Build / Test

There is no local Pine compiler in this repo. Run the local behavioral checks with:

```sh
python3 -m unittest discover -s tests -v
```

The suite evaluates a deliberately limited subset of real source helpers and state blocks, plus source wiring contracts. It does not emulate TradingView feeds, Pine's full type system, rollback engine, request scheduling, or chart rendering. Never describe it as a Pine compile, a backtest, or realtime validation.

Manual validation workflow:

1. Copy `RSI+` into TradingView Pine Editor
2. Click `Add to Chart`
3. Confirm it compiles without errors
4. Validate behavior on `SPY`, `QQQ`, `IWM`
5. Check both dashboard modes
6. Check buy, risk, divergence, resonance, and alert behavior

## v7.6 Implementation Contract

- Each market owns its adaptive RSI bands, chart-bar lookback and ordinary/divergence cooldowns. Do not reintroduce host-chart `driverRSI` coupling.
- Long volatility uses 126/252/504 **confirmed daily RSI samples**, not a capped intraday-bar approximation. `f_dailyMarketStats()` returns the previous confirmed 252-day closing high, daily RSI standard deviation and available sample count in one request.
- `f_secDailyLive()` now returns `[confirmed, developing]` in one tuple request. Only its developing leg may use unoffset daily lookahead; all market-stat tuple legs use `[1]`.
- `f_marketAdaptive()` returns per-market bands, `AdaptiveLookback`, `AdaptiveReady`, `LongVolReady`, effective `UseAdaptive`, `CooldownBars`, `DivCooldownBars`, and `AdaptiveRequested`. Distinguish requested adaptive mode from effective adaptive mode when displaying a fixed-band fallback.
- Statistical warmup uses shorter-term volatility and valid positive lookback lengths. Unavailable or collapsed percentile bands fall back to strictly ordered fixed RSI bands. `Fixed` threshold mode does not show a statistics warmup warning.
- `DataReady` requires price, RSI, trend, confirmed high and actual scored breadth/volume sources. Missing/invalid source symbols become `na` and block new events; missing values must not silently become neutral signals. ADD still preserves its accepted previous-value na guard.
- Missing inputs must not clear accepted panel/zone state or re-arm non-live alert deduplication. HOLD exits and prior-side re-arm checks require valid data; hide the background while unavailable.
- AGG requires all three markets ready because its displayed context averages all three. Individual-market paths require only that market's sources.
- Only seconds/minutes and exactly 1D charts are supported. Explicitly reject tick and higher-than-1D charts before requests; `timeframe.isintraday` alone also includes tick charts.
- RSI Length is 2–250, keeping its largest derived window at 1000 bars inside `max_bars_back=1100`. Fixed bands must satisfy OS1 < OS2 < OB2 < OB1 even in Auto/Adaptive mode because they serve as fallback.
- Keep theoretical scoring/percent inputs compatible; bound final buy/risk weak thresholds to >=1 / <=-1 and keep strong thresholds at least 1 point more extreme. Drawdown/assist can still cause both sides to qualify, so event arbitration remains necessary.
- `minAgree` controls resonance and its display bonus. A single market with `minAgree=1` may trigger AGG, but has strength 1 and no resonance score bonus.

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
- After adjustments: weak buy >= +1, weak risk <= -1; strong buy >= weak buy +1, strong risk <= weak risk -1. Defaults on standard daily charts remain unchanged.

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
- `ELEVATED` is gated by the sell-side signal quality filter the same way as `CAUTION` and `REDUCE`; with `useSignalQuality = true`, C-grade conditions do not display or alert as `ELEVATED`.
- Divergence is both a displayed overlay and a possible buy-side assist.
- Resonance is cross-market logic, not a single score threshold.

## Current Function Map

These functions define the main behavior and should be preserved when refactoring.

| Function | Purpose |
|------|------|
| `f_sec()` | Session-aware intraday security request |
| `f_ohlc()` | Session-aware OHLC request helper |
| `f_secDaily()` | Previous confirmed daily data request |
| `f_secDailyLive()` | Tuple of previous confirmed and developing daily data |
| `f_dailyMarketStats()` | Confirmed daily high, long volatility and sample count |
| `f_marketAdaptive()` | Independent per-market adaptive settings and cooldowns |
| `f_adaptiveLookback()` | Positive, available-history-bounded chart-bar lookback |
| `f_marketDataReady()` | Required price and scoring-input readiness |
| `f_qualityGrade()` | Grade from the displayed aligned-factor count |
| `f_eventSide()` | Shared highest-visible-level side selection; buy wins ties |
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
| `f_marketStatus()` | Ready-aware raw buy/sell score status icon; risk takes precedence |

## Dashboard Reference

The actual rendered layouts in `RSI+` are:

### Full Mode

- `7 rows x 1 column`
- Row 0: accepted signal + side-appropriate current score + trend; WAIT DATA replaces unavailable context
- Row 1: centered score bar
- Row 2: RSI + volume
- Row 3: `FI + TW` in daily mode; `ADD + Hist/历史:available/targetD` in intraday mode. AGG history coverage is the smallest available count among the three markets
- Row 4: trend + divergence + current factor quality for the panel side (`B/买` or `S/卖`), `x/4` daily or `x/3` intraday. AGG grades its floored mean aligned count and does not show hidden divergence events; missing data shows no trend/quality
- Row 5: drawdown + enabled buy-only bonus + filter/data status; disabling Drawdown Bonus hides its annotation
- Row 6: `SPY / QQQ / IWM` raw factor status + resonance icon. Gray = data unavailable; red = raw sell threshold; otherwise green = buy threshold, yellow = neutral. These dots do not apply trend/quality gates

### Mobile Mode

- `2 rows x 1 column`
- Row 0: accepted signal + side-appropriate current score + trend; WAIT DATA replaces unavailable context
- Row 1: filter status

Do not document old `11-row` or `3-row` layouts. The current output code is `7` and `2`.

## Filter Status Rules

`filterStatus` currently maps to:

| Label | Meaning |
|------|------|
| `WAIT DATA / 等待数据` | required inputs missing; new signals blocked |
| `WARMUP / 预热` | adaptive statistical fallback in use; signals may still pass |
| `👀` | no active filter block |
| `✋ WAIT` | buy-zone score exists but signal is filtered out |
| `☕ HOLD` | sell threshold hit but uptrend blocks the sell |
| `🚫` | downtrend buy-zone score while trend filter is active and no buy signal is plotted/active |

Sell-side comparisons for `☕ HOLD` and for hold-zone / zone-exit detection use `displaySellScore` (raw sell score, no drawdown bonus), not the displayed buy score; a large drawdown bonus must not inflate sell-side checks.

## Alert System

Dashboard main signal rules that matter:

- The panel, background and alert side use the same highest visible event level on the current bar via `f_eventSide()`; buy wins ties. Both accepted opposite-side markers remain plotted. A later same-bar upgrade may change the panel but must not publish a second alert.
- Risk panel states and risk alert messages use raw `displaySellScore` and sell quality; buy/neutral panel states retain the buy score.
- AGG shows RESONANCE rather than hidden strong/divergence states. ELEVATED enters the risk background zone.

Smart Alert V2 levels:

| Level | Meaning |
|------|------|
| `Lv1` | `BUY ZONE`, `CAUTION`, `ELEVATED` |
| `Lv2` | `DIVERGENCE` |
| `Lv3` | `RESONANCE` |
| `Lv4` | `PANIC LOW`, `REDUCE` |
| `Lv5` | strong signal + resonance combo |

Implementation details that matter:

- Smart alerts reuse accepted, bar-latched plotted events and resonance edges. Ordinary cooldowns, divergence cooldowns, and `f_recent()` windows also consume those same accepted events, never transient raw triggers.
- After latching, replay the accepted event into ordinary `var` last-bar/last-level records on every tick so Pine commits it even if raw conditions fade on the closing tick. Strong upgrades reset the relevant cooldown and enter resonance history. Track last accepted marker level to prevent reclassifying a retained strong event as another upgrade.
- Only realtime, ready, session-eligible publication may advance alert sent/published/latched levels. Historical evaluation must not consume notification state.
- Smart alerts must follow the currently displayed K-line signal path under `Display Mode`; manual `SPY / QQQ / IWM / AGG` selection must not leave alerts on a different symbol/state than the visible markers.
- `Lv2 (DIVERGENCE)` / `Lv3 (RESONANCE)` are upgrade tags that require an existing visible base buy/risk trigger on the current display path; do not publish hidden standalone divergence-only or resonance-only alerts.
- Smart alerts should publish when the latest realtime bar first shows a visible trigger level on that tick; later historical backfill may reshape prior bars, but it must not cancel or replay that reminder.
- Realtime plotted events are bar-latched: if a plotted buy/risk marker fires intrabar, that bar keeps the marker and aligned panel state even if the raw condition fades before close.
- `PANIC LOW` / `REDUCE` plot markers must also fire on strict same-side upgrades from `BUY ZONE` / `CAUTION`, even if the base cooldown would suppress a duplicate weak signal.
- The script uses `varip` state to deduplicate alerts within the same bar.
- Smart alerts are limited to one publish per bar; if buy and sell sides both qualify on the same tick, only the higher-level side is published.
- Same-level or downgraded intrabar flicker must not re-arm duplicate alerts inside the same bar.
- `varip` observation state should remember the latest bar's highest visible level for the current display path, so the first visible reminder survives later same-bar recalculations.
- Buy and sell alert states are tracked separately.
- Cross-bar alert state suppresses repeated alerts while the same side remains active at the same or lower level.
- Resonance is an upgrade tag on every display path: in manual `SPY / QQQ / IWM` modes, a visible base buy/risk trigger that coincides with the resonance edge (`aggBottomEdge` / `aggTopEdge`) on the same bar publishes `Lv3` (base + resonance) or `Lv5` (strong + resonance, e.g. `PANIC LOW` + `RESONANCE`).
- Resonance-only alerts (no visible base trigger on the current display path) still publish only on `AGG(共振)`; AGG must not publish a separate hidden-symbol alert path in manual `SPY / QQQ / IWM` modes.
- The `AGG(共振)` path publishes `Lv3` only; it has no strong or divergence states.
- On `intradayMode + useLiveData`, same-side alerts are latched for the full regular session and re-arm on the first regular-session bar of each new trading day, detected via a date key (`live_alert_session_day`); this must also work on RTH-only charts, where `session.ismarket` never flips false between days.
- Live intraday same-level repeats and downgrades stay muted during the current regular session; strict upgrades may publish only on later bars after the first alert.
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
    request.security(f_intradayTicker(_sym), tfData, _expr, intradayMode ? barmerge.gaps_on : barmerge.gaps_off, barmerge.lookahead_off, ignore_invalid_symbol=true)

f_secDaily(_sym, _expr) =>
    request.security(_sym, "D", _expr[1], barmerge.gaps_off, barmerge.lookahead_on, ignore_invalid_symbol=true)

f_secDailyLive(_sym, _expr) =>
    request.security(_sym, "D", [_expr[1], _expr], barmerge.gaps_off, barmerge.lookahead_on, ignore_invalid_symbol=true)
```

Rules:

- Do not introduce lookahead bias outside `f_secDailyLive()`.
- Intraday SPY / QQQ / IWM / ADD requests should inherit the chart session modifier.
- `ADD`, `TW/FI`, and `UVOL/DVOL` live values should freeze outside `session.ismarket`; do not let regular-session values drift through post-market bars.
- Intraday `ADD` is also `na`-guarded during the regular session (`nz(addValueRaw, addValue[1])`) so a missing ADD bar does not cause transient score drops.

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
- lookback length with a defined positive fallback and an available-history bound; never pass `na` or 0
- multi-line ternaries by keeping them on one line
- cross-scope assignment by declaring variables first and using `:=`

## Documentation Rules

- `README.md` must describe the current script behavior, not legacy versions.
- Any user-facing signal list must include `PANIC LOW`, `BUY ZONE`, `HOLD`, `ELEVATED`, `CAUTION`, `REDUCE`, `DIVERGENCE`, and `RESONANCE`.
- Dashboard docs must reflect `Full = 7 rows` and `Mobile = 2 rows`.
- Alert docs must reflect the current `Lv1` to `Lv5` level system.
- All user-facing text added to the script should remain bilingual (`English / 中文`).

## Known Limitations

Accepted design constraints; do not describe them as bugs or silently "fix" them:

- Historical intraday bars read end-of-day daily breadth values through `f_secDailyLive()` lookahead, so historical intraday markers can look better than what realtime would have shown; realtime alerts use developing values. Historical markers are not a backtest of live behavior.
- On daily charts, breadth/volume factors come from the previous confirmed daily leg (1-day lag); the `useLiveData` option only affects intraday charts.
- Futures tickers (`ES` / `NQ` / `RTY` etc.) are detected best-effort; session gating and breadth freezing are designed for US equity regular hours and are not validated for futures sessions.

## Validation Checklist

- [ ] Python regression suite passes
- [ ] Script compiles in TradingView
- [ ] SPY / QQQ / IWM logic still works
- [ ] Daily and intraday paths both behave correctly
- [ ] Extended-session intraday charts do not publish any smart alerts after the regular close
- [ ] RTH-only intraday charts re-arm latched live alerts on the first regular-session bar of each new trading day
- [ ] Dashboard Full/Mobile output matches docs
- [ ] Alert labels and thresholds match docs
- [ ] Intrabar trigger/fade preserves cooldown and resonance history
- [ ] Historical loading does not consume live reminder state
- [ ] Same-bar opposite sides use the shared event-level selection
- [ ] Per-market adaptive settings, actual daily history count and warmup display are correct
- [ ] Full/Mobile risk score and factor grade use sell context
- [ ] Input bounds and supported-timeframe errors are clear
- [ ] Both README languages updated when behavior changes
- [ ] Existing TradingView alerts recreated after the new script compiles (alerts retain their original script/input snapshot)
