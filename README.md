# RSI+ Breadth Multi-Factor Indicator v7.4

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/scripts/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-reference/v6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

RSI+ is a Pine Script v6 market-timing indicator for US index markets. The current script targets **SPY**, **QQQ**, and **IWM**, and combines **RSI**, **breadth**, **volume breadth**, **divergence**, **trend filter**, and **multi-market resonance** into a single decision framework.

RSI+ 是一个面向美股指数市场的 Pine Script v6 择时指标。当前脚本主要围绕 **SPY**、**QQQ**、**IWM**，把 **RSI**、**市场广度**、**成交量广度**、**背离**、**趋势过滤** 和 **多市场共振** 组合成一套统一决策框架。

---

## English Documentation

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
- **Intraday live alert mode**: can use developing daily values via `f_secDailyLive()`

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

- Same-bar upgrade alerts are allowed
- `varip` state prevents duplicate lower-level alerts in the same bar
- Buy and risk alerts are tracked separately
- Intraday charts can use live daily data if `Live Alert Data` is enabled

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

---

## 中文说明文档

### 概述

当前 `RSI+` 脚本包含这些模块：

- **核心评分引擎**：RSI + 市场广度 + 成交量广度
- **日线广度模式**：使用 `TW / FI`
- **日内广度模式**：使用 `ADD` 取代日线 `TW / FI` 评分块
- **自适应阈值系统**：自动回溯、波动率驱动、自适应 RSI 区间
- **信号质量过滤**：启用后仅允许 `A/B` 级信号通过
- **回撤加分**：5% / 10% / 20% 回撤分别加 `+1 / +2 / +3`
- **背离系统**：价格与 RSI 的多空背离，带冷却期
- **趋势过滤**：上升趋势中把卖出侧信号转为 `ELEVATED`
- **多市场共振**：检测 SPY / QQQ / IWM 是否同步
- **面板系统**：`Full` 与 `Mobile` 两种模式
- **Smart Alerts V2**：按等级触发、支持同一根 K 线升级警报

### 市场与数据源

- **跟踪市场**：`SPY`、`QQQ`、`IWM`
- **日线广度**：
  - SPY: `S5TW`, `S5FI`
  - QQQ: `NCTW`, `NCFI`
  - IWM: `R2TW`, `R2FI`
- **成交量广度**：
  - NYSE: `UVOL`, `DVOL`
  - NASDAQ: `UVOLQ`, `DVOLQ`
- **日内广度代理**：`ADD`
- **日内实时警报模式**：可通过 `f_secDailyLive()` 使用 developing daily 数据

### 评分模型

脚本中的默认理论分数范围如下：

| 组件 | 买入最大分 | 卖出最小分 | 说明 |
|---|---:|---:|---|
| RSI | `+2` | `-2` | 固定或自适应阈值 |
| FI 广度 | `+3` | `-2` | 仅日线模式 |
| TW 广度 | `+1` | `-3` | 仅日线模式 |
| 成交量比 | `+2` | `-2` | `UVOL / DVOL` 或 `UVOLQ / DVOLQ` |
| ADD 广度 | `+3` | `-3` | 仅日内模式；此路径下日线 `TW / FI` 评分输入归零 |
| 回撤加分 | `+1 / +2 / +3` | `0` | 只影响买入侧 |

默认阈值计算结果：

- `maxBuyScore = 8`
- `maxSellScore = 9`
- `Buy Sensitivity = 50%` -> `BUY ZONE >= 4`
- 强买偏移 `+25%` -> `PANIC LOW >= 6`
- `Sell Sensitivity = 45%` -> `CAUTION <= -4`
- 强卖偏移 `+25%` -> `REDUCE <= -6`

模式调整：

- `Aggressive`：买入阈值更低，卖出阈值更宽松
- `Conservative`：买入阈值更高，卖出阈值更严格
- `Intraday`：额外再做 2 分灵敏度调整

### 信号说明

脚本当前使用的信号名称与图标如下：

| 类型 | 脚本触发条件 | 图标 | 标签 | 含义 |
|---|---|---|---|---|
| 强买 | `buyScore >= adjStrongBotThreshold` | `🚀` | `PANIC LOW` | 极端超卖，最强买入状态 |
| 买入 | `buyScore >= adjBotThreshold` | `📈` | `BUY ZONE` | 常规低吸区 |
| 中性 | 买卖阈值之间 | `⚪` | `HOLD` | 无明显优势 |
| 上涨中的风险 | 达到卖出阈值，但 `price > trend MA` 且趋势过滤开启 | `⭐` | `ELEVATED` | 高估但趋势未坏 |
| 风险 | 非上涨趋势下 `sellScore <= adjTopThreshold` | `⚡` | `CAUTION` | 止盈 / 风险控制区 |
| 强风险 | 非上涨趋势下 `sellScore <= adjStrongTopThreshold` | `⚠️` | `REDUCE` | 最强减仓状态 |
| 看多背离 | `divStrength < -threshold` 且 RSI 低于 `OS2` | `💎` | `DIVERGENCE` | 反转辅助 / 确认 |
| 看空背离 | `divStrength > threshold` 且 RSI 高于 `OB2` | `💎` | `DIVERGENCE` | 风险反转警告 |
| 买入共振 | 2 个以上市场在窗口期内同步进入买入侧 | `🔥` | `RESONANCE` | 多市场看多确认 |
| 风险共振 | 2 个以上市场在窗口期内同步进入风险侧 | `❄️` | `RESONANCE` | 多市场风险确认 |

几个关键点：

- `ELEVATED` 不是弱化版 `CAUTION`，而是卖出阈值已到、但趋势过滤阻止真正卖出信号时的正式显示状态。
- 背离是独立叠加信号；启用 `Divergence Assist` 后，也可以推动边缘买入信号通过。
- 共振不是单一市场高分，而是跨市场同步。

### 过滤与增强机制

#### 信号质量过滤

`f_signalQuality()` 的等级定义：

- `A`：3 个及以上因子同向
- `B`：2 个因子同向
- `C`：少于 2 个因子同向

开启后，只允许 `A/B` 级买卖信号触发。

#### 回撤加分

`f_drawdownBonus()` 只增加买入侧分数：

- 回撤 `>= 5%`：`+1`
- 回撤 `>= 10%`：`+2`
- 回撤 `>= 20%`：`+3`

它会影响买入判定和面板分数，但不会影响卖出侧分数。

#### 背离助推

启用后，看多背离可以在分数还差 **1-2 分** 时提前推过买入阈值。

#### 动态冷却

冷却期会根据波动率变化：

- 高波动 -> 缩短
- 正常波动 -> 保持
- 低波动 -> 拉长

只要基础冷却不是 0，脚本会保证最小冷却为 3 根 K 线。

### 面板说明

当前脚本有两种面板模式。

#### Full 模式

代码中的真实布局：**7 行 x 1 列**

| 行 | 内容 |
|---:|---|
| 0 | 信号 + 分数 + 趋势，例如 `🚀 PANIC LOW +6.5↑` |
| 1 | 居中分数条 |
| 2 | RSI 分项 + 成交量分项 |
| 3 | 日线显示 `FI + TW`，日内显示 `ADD + TW`；当前代码仍保留紧凑的 `TW` 显示位，但日内评分实际由 `ADD` 驱动 |
| 4 | 趋势 + 背离 + 质量，例如 `↑UP 💎B A3/4` |
| 5 | 回撤 + 过滤状态，例如 `DD8%+2 ✋ WAIT` |
| 6 | `SPY / QQQ / IWM` 状态 + 共振图标 |

#### Mobile 模式

代码中的真实布局：**2 行 x 1 列**

| 行 | 内容 |
|---:|---|
| 0 | 信号 + 分数 + 趋势 |
| 1 | 过滤状态 |

#### 过滤状态含义

| 显示 | 脚本条件 | 含义 |
|---|---|---|
| `👀` | 当前没有过滤阻塞 | 观望 |
| `✋ WAIT` | 分数达到买入区，但信号被过滤 | 分数够了，确认还不够 |
| `☕ HOLD` | 达到卖出阈值，但上升趋势阻止卖出 | 风险升高，但趋势未坏 |
| `🚫` | 下跌趋势中进入买入区，且趋势过滤开启 | 熊市风格风险过滤 |

### Smart Alerts V2

脚本当前的警报等级如下：

| 等级 | 触发内容 |
|---:|---|
| `Lv1` | `BUY ZONE`、`CAUTION`、`ELEVATED` |
| `Lv2` | `DIVERGENCE` |
| `Lv3` | `RESONANCE` |
| `Lv4` | `PANIC LOW` 或 `REDUCE` |
| `Lv5` | `PANIC LOW + RESONANCE` 或 `REDUCE + RESONANCE` |

警报行为：

- 允许同一根 K 线内升级触发
- 用 `varip` 防止同一根 K 线重复发低等级警报
- 买入侧与风险侧分别去重
- 日内图在 `Live Alert Data` 开启时可用实时日线 developing 数据

### 默认设置

脚本当前默认值：

| 项目 | 默认值 |
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

### 验证方式

这个仓库没有本地 Pine 构建系统，验证方式仍然是手动：

1. 将 `RSI+` 复制到 TradingView Pine Editor
2. 点击 `Add to Chart`
3. 在 `SPY`、`QQQ`、`IWM` 上检查表现
4. 检查 `Full` 和 `Mobile` 面板模式
5. 对照上面的信号、风险、背离、共振逻辑检查显示和警报

---

## Disclaimer | 免责声明

This indicator is for educational purposes only. Past performance does not guarantee future results.

本指标仅供教育用途。历史表现不代表未来收益。

**Version**: 7.4 | **Pine Script**: v6 | **Updated**: 2026-03-11
