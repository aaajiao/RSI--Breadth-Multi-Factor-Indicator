# RSI+ Breadth Multi-Factor Indicator v6.2

**Adaptive Scoring System for US Market Timing | 美股多因子自适应择时系统**

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-docs/en/v6/)

---

## Overview | 概述

A quantitative indicator that combines **RSI**, **Market Breadth**, **Volume Ratio**, and **Divergence** to generate actionable buy/sell signals across **SPY**, **QQQ**, and **IWM**. Version 6 introduces **Adaptive Technology**, automatically adjusting signal thresholds and lookback periods based on market volatility.

这是一个结合 **RSI**、**市场广度**、**成交量比** 和 **背离** 的量化指标，针对 **SPY**、**QQQ** 和 **IWM** 三大市场生成可执行信号。v6 版本引入了 **自适应技术**，能根据市场波动率自动调整信号阈值和回溯期。

---

## What's New in v6 | v6 新功能

| Feature | Description | 中文说明 |
|:---:|---|---|
| 🧠 | **Auto-Adaptive Lookback** | **自动回溯期**：使用统计公式 n=(Z×σ/E)² 自动计算最优回溯期 (100-1000 bars) |
| 📊 | **Dual Volatility System** | **双重波动率**：结合短期 (4×RSI) 与长期 (252D) 波动率，动态加权 |
| ⚡ | **Dual Detection Thresholds** | **双重检测**：快速触发 (1.5×RSI) + 慢速确认 (3×RSI)，捕捉波动变化 |
| 💎 | **Smart Divergence** | **智能背离**：背离回溯期自动关联 RSI 长度 (4×)，避免周期错配 |
| 🔥 | **Market Resonance** | **市场共振**：检测多市场同时触发买入/卖出信号 |
| 📈 | **Intraday Breadth** | **日内广度**：小时图自动使用 `USI:ADD` (涨跌家数差) 代替每日广度 |
| 🎯 | **Health Monitor** | **健康监控**：实时验证 Lookback 统计有效性与分布宽度 (≥12) |
| 🔔 | **Smart Alert** | **智能警报**：统一警报系统，上升沿检测防重复，单消息汇总所有信号 |
| ⏱️ | **Dynamic Cooldown** | **动态冷却**：根据波动率自动调整信号间隔，高波动60%冷却/低波动150%冷却 |

---

## Core Components | 核心组件

### Multi-Factor Scoring | 多因子评分

The indicator calculates a composite score from multiple factors:

指标从多个因子计算综合得分：

| Factor | 因子 | Weight | Description |
|:------:|:----:|:------:|-------------|
| **RSI** | RSI指标 | 1x | 14-period RSI with adaptive thresholds<br/>14周期RSI，自适应阈值 |
| **FI/TW** | 市场广度 | 2-3x | % stocks above 20D/50D MA (S5FI, S5TW, etc.)<br/>高于20日/50日均线的股票比例 |
| **Volume** | 成交量 | 1x | Up/Down volume ratio (UVOL/DVOL)<br/>上涨/下跌成交量比 |
| **ADD** | 涨跌差 | 3x | Advance-Decline spread (intraday mode only)<br/>涨跌家数差（仅日内模式） |
| **Divergence** | 背离 | Bonus | Z-Score based divergence detection<br/>基于Z值的背离检测 |

### Signal Levels | 信号级别

| Score | Emoji | Signal | 中文 | Action | Condition |
|:-----:|:-----:|--------|:----:|--------|-----------|
| ≥ 6 | 🚀 | **PANIC LOW** | 恐慌低点 | Strong buy | Score + multiple factors extreme |
| ≥ 4 | 📈 | **BUY ZONE** | 低吸区 | Accumulate | Above buy threshold |
| DIV | 💎 | **DIVERGENCE** | 背离 | Reversal signal | Z-Score divergence in extreme zone |
| -3~3 | - | **HOLD** | 持有 | Hold position | Neutral range |
| ≤ -4↑ | ⭐ | **ELEVATED** | 高估 | Hold cautious | Negative score + uptrend |
| ≤ -4↓ | ⚡ | **CAUTION** | 观望 | Take profit | Negative score + downtrend |
| ≤ -6↓ | ⚠️ | **REDUCE** | 减仓 | Reduce position | Strong negative score + downtrend |

**Resonance Signals | 共振信号**:
- 🔥 **Resonance Buy** - 2+ markets in buy zone simultaneously
- ❄️ **Resonance Risk** - 2+ markets in risk zone simultaneously

> **↑ = Uptrend** (Price > MA) | **↓ = Downtrend** (Price < MA)

---

## Adaptive Logic | 自适应逻辑

### 1️⃣ Auto-Adaptive Lookback | 自动回溯期

**Formula | 公式**: `n = (Z × σ / E)²`

Where | 其中:
- **Z** = 1.96 (95% confidence | 95%置信度)
- **σ** = Dynamic volatility (dual system) | 动态波动率（双重系统）
- **E** = Precision parameter (2.0-3.5) | 精度参数

**Dual Volatility System | 双重波动率系统**:
```
Short-term: 4 × RSI Length (快速响应)
Long-term: 252D or custom period (稳定基准)
Dynamic weighting: 70% long + 30% short (动态加权)
↳ Switches to 60% short if recent > 1.2× long
```

**Benefits | 优势**:
- ✅ Adapts to different assets automatically | 自动适应不同资产
- ✅ Balanced between stability and responsiveness | 稳定性与响应性平衡
- ✅ Statistical validity guaranteed | 保证统计有效性
- ✅ Prevents lookback truncation | 防止回溯期截断

### 2️⃣ Adaptive Threshold Selection | 自适应阈值选择

**How it works | 工作原理**:

The indicator monitors RSI volatility in real-time using **dual detection**:

指标实时监控RSI波动率，使用**双重检测**：

| Detection | Period | Trigger | Purpose |
|:---------:|:------:|:-------:|---------|
| **Fast** | 1.5 × RSI | vol > 8.0 | Quick response to volatility spikes<br/>快速响应波动突变 |
| **Slow** | 3 × RSI | vol > 9.6 | Confirm sustained volatility<br/>确认持续波动 |

**Auto Mode Logic | 自动模式逻辑**:
```
IF vol_fast > threshold OR vol_slow > threshold × 1.2
  → Use Adaptive Percentile Thresholds
ELSE
  → Use Fixed Thresholds (30/70)
```

**Threshold Comparison | 阈值对比**:

| Mode | Oversold 1 | Oversold 2 | Overbought 2 | Overbought 1 |
|:----:|:----------:|:----------:|:------------:|:------------:|
| **Fixed** | 30 | 40 | 65 | 75 |
| **Adaptive** | P10 | P20 | P80 | P90 |

### 3️⃣ Smart Divergence Detection | 智能背离检测

**Dynamic Lookback | 动态回溯**: `4 × RSI Length` (默认 56 bars)

**Z-Score Based Detection | 基于Z值检测**:
```
Price Z-Score = (Price - MA) / StdDev
RSI Z-Score = (RSI - MA) / StdDev
Divergence Strength = |Price Z - RSI Z|
```

**Trigger Conditions | 触发条件**:
- Bullish: `Divergence < -threshold` AND `RSI < Oversold2`
- Bearish: `Divergence > +threshold` AND `RSI > Overbought2`

**Cooldown Period | 冷却期**: Prevents duplicate signals (default 5 bars)

---

## Settings Reference | 设置参考

### 📊 Mode / 模式

| Setting | Description | 中文说明 |
|:-------:|-------------|----------|
| **Aggressive** | -1 threshold adjustment, faster signals | 阈值-1，信号更灵敏，冷却期5根K线 |
| **Standard** | Balanced (default) | 平衡模式（默认），冷却期10根K线 |
| **Conservative** | +1 threshold adjustment, fewer signals | 阈值+1，信号更保守，冷却期15根K线 |

### 🧠 Adaptive / 自适应

| Parameter | Options | Recommendation | Description |
|:---------:|---------|:--------------:|-------------|
| **Lookback Mode** | Auto / Fixed 252 / Custom | `Auto` for indices | 回溯模式：Auto自动计算 |
| **Precision** | High / Normal / Low | `High` for indices | 精度：High=更精确但更长 |
| **Vol History** | 6M / 1Y / 2Y | `1Y` default | 波动率历史深度 |
| **Threshold Mode** | Auto / Fixed / Adaptive | `Auto` recommended | 阈值模式：Auto自动切换 |
| **RSI Vol Threshold** | 5.0 - 20.0 | `8.0` indices, `10.0` stocks | Auto模式切换阈值 |

**Precision Parameter Mapping | 精度参数对照**:
- **High**: E = 2.0 (longer lookback, higher precision) | 更长回溯期，更高精度
- **Normal**: E = 2.5 (balanced) | 平衡
- **Low**: E = 3.5 (shorter lookback, faster response) | 更短回溯期，更快响应

### 📈 Core Settings / 核心设置

| Parameter | Default | Range | Description |
|:---------:|:-------:|:-----:|-------------|
| **RSI Length** | 14 | 2-50 | Standard RSI period<br/>标准RSI周期 |

### 🎯 Signal Thresholds / 信号阈值

| Threshold | Default | Range | Description |
|:---------:|:-------:|:-----:|-------------|
| **Panic Low** | 6 | 3-10 | Strong buy signal<br/>强烈买入阈值 |
| **Buy Zone** | 4 | 2-8 | Accumulate signal<br/>分批建仓阈值 |
| **Caution** | -4 | -8~-2 | Take profit signal<br/>止盈信号阈值 |
| **Reduce** | -6 | -10~-3 | Reduce position signal<br/>减仓信号阈值 |

### 🔄 Signal Logic / 信号逻辑

| Parameter | Default | Description |
|:---------:|:-------:|-------------|
| **Cooldown Bars** | 10 | Bars between signals (0 = no limit)<br/>信号间隔K线数（0=无限制） |
| **Dynamic Cooldown** | ON | Auto-adjust cooldown based on volatility<br/>根据波动率自动调整冷却期<br/>High vol=60% / Low vol=150% |
| **Resonance Window** | 3 | Bars to detect market resonance<br/>共振检测窗口 |
| **Min Markets** | 2 | Markets needed for resonance (1-3)<br/>触发共振所需市场数 |
| **Trend MA Length** | 10 | Trend filter MA period<br/>趋势过滤均线周期 |
| **Enable Trend Filter** | ON | Filter sell signals in uptrend<br/>上升趋势过滤卖出信号 |

### 💎 Divergence / 背离

| Parameter | Default | Range | Recommendation |
|:---------:|:-------:|:-----:|----------------|
| **Enable Divergence** | ON | - | Turn on/off divergence detection<br/>开启/关闭背离检测 |
| **Z-Score Threshold** | 1.7 | 0.5-3.0 | Indices: 2.0, Stocks: 1.5-1.8<br/>指数2.0，个股1.5-1.8 |
| **Cooldown Bars** | 5 | 0-30 | Prevent duplicate divergences<br/>防止重复背离信号 |

### 📊 Fixed Thresholds / 固定阈值

(Used when Threshold Mode = Fixed | 固定模式下使用)

| Parameter | Default | Range |
|:---------:|:-------:|:-----:|
| **Oversold 1** | 30 | 10-40 |
| **Oversold 2** | 40 | 20-50 |
| **Overbought 2** | 65 | 50-80 |
| **Overbought 1** | 75 | 60-90 |

### 📍 Symbols / 标的

**Market Indices | 市场指数**:
- SPY, QQQ, IWM (or equivalents)

**Breadth Indicators | 广度指标**:
- S5TW/S5FI (S&P 500), NCTW/NCFI (Nasdaq), R2TW/R2FI (Russell 2000)
- UVOL/DVOL (NYSE), UVOLQ/DVOLQ (Nasdaq)
- ADD (Advance-Decline, for intraday)

### 🖥️ Display / 显示

| Setting | Options | Description |
|:-------:|---------|-------------|
| **Display Mode** | AUTO / SPY / QQQ / IWM / AGG(共振) | AUTO detects chart symbol<br/>AUTO自动检测图表标的; AGG shows multi-market resonance<br/>AGG显示多市场共振 |
| **Show Dashboard** | ON/OFF | Show/hide info panel<br/>显示/隐藏信息面板 |

---

## Dashboard Reference | 面板说明

The dashboard displays real-time scoring and system status:

面板实时显示评分和系统状态：

| Row | Content | Description |
|:---:|---------|-------------|
| **RSI** | Score, Weight | RSI factor contribution<br/>RSI因子贡献 |
| **FI(50D)** | Score, "Bottom" | 50D breadth (daily) or ADD (intraday)<br/>50日广度（日线）或涨跌差（日内） |
| **TW(20D)** | Score, "Top" | 20D breadth factor<br/>20日广度因子 |
| **Vol** | Score, Weight | Volume ratio factor<br/>成交量比因子 |
| **Trend** | ↑UP/↓DOWN | Current trend direction<br/>当前趋势方向 |
| **Mode** | Fixed/Adaptive | Current threshold mode | Vol value<br/>当前阈值模式 | 波动率 |
| **Div** | BULL💎/BEAR💎/- | Divergence status | ON/OFF<br/>背离状态 | 开关 |
| **Total** | Score, Signal | Composite score and signal type<br/>综合得分和信号类型 |
| **Lookback** | Period, Health | Adaptive lookback | Health check (✓OK/⚠Check)<br/>自适应回溯期 | 健康检查 |
| **Cooldown** | Bars, Dyn/Fix | Dynamic or fixed cooldown mode<br/>动态或固定冷却模式 |

**Health Indicators | 健康指标**:
- ✓ OK: Lookback statistically valid, distribution width ≥12
- ⚠ Check: May need more historical data or adjustment

---

## Usage Tips | 使用建议

### For Index Trading | 指数交易

**Recommended Settings | 推荐设置**:
```
Mode: Standard
Lookback Mode: Auto
Precision: High
Threshold Mode: Auto
RSI Vol Threshold: 8.0
Divergence Threshold: 2.0
```

### For Stock Trading | 个股交易

**Recommended Settings | 推荐设置**:
```
Mode: Aggressive
Lookback Mode: Auto
Precision: Normal
Threshold Mode: Auto
RSI Vol Threshold: 10.0
Divergence Threshold: 1.5-1.8
```

### For Intraday Trading | 日内交易

**Key Features | 关键特性**:
- Automatically uses ADD (Advance-Decline) instead of daily breadth
- Signal thresholds adjusted +2 automatically
- Faster cooldown recommended (5-8 bars)

**关键特性**:
- 自动使用涨跌差(ADD)代替每日广度
- 信号阈值自动+2调整
- 推荐更快冷却期(5-8根K线)

---

## Smart Alert System | 智能警报系统

The indicator uses a **Unified Smart Alert** system with **Rising Edge Detection** to prevent duplicate notifications.

指标使用**统一智能警报**系统，配合**上升沿检测**防止重复通知。

### How It Works | 工作原理

```
1. Aggregate all triggered signals into ONE message
   将所有触发的信号汇总到一条消息
   
2. Rising Edge Detection: Only fires when signal changes from OFF → ON
   上升沿检测：仅在信号从无到有时触发
   
3. Include context info (Score, Trend) for quick decision making
   包含上下文信息（得分、趋势）以便快速决策
```

### Alert Message Format | 警报消息格式

**Buy Signals | 买入信号**:
```
SPY: 🟢 BUY → 🚀恐慌低点 🔥共振 💎背离 | Score:6.5 ↑UP
```

**Sell/Risk Signals | 卖出/风险信号**:
```
QQQ: 🔴 RISK → ⚠️减仓 ❄️共振 | Score:-6.2 ↓DOWN
```

### Signal Tags | 信号标签

| Tag | Signal | Description |
|:---:|:------:|-------------|
| 🚀 | **恐慌低点** | Panic Low - Strong buy opportunity |
| 📈 | **低吸区** | Buy Zone - Accumulation zone |
| 🔥 | **共振** | Resonance - Multi-market agreement |
| 💎 | **背离** | Divergence - Price/RSI divergence |
| ⚠️ | **减仓** | Reduce - High risk, reduce position |
| ⚡ | **观望** | Caution - Take profit signal |
| ⭐ | **高估** | Elevated - Overbought but uptrend |
| ❄️ | **共振** | Resonance Risk - Multi-market risk |

### Settings | 设置

| Parameter | Default | Description |
|:---------:|:-------:|-------------|
| **Enable Smart Alert** | ON | Turn on/off unified alerts<br/>开启/关闭统一警报 |

### Benefits | 优势

- ✅ **Single Message**: All signals in one notification, no spam
- ✅ **Deduplication**: Rising edge detection prevents repeats
- ✅ **Rich Context**: Includes score and trend for quick action
- ✅ **Auto-Detection**: Matches your chart symbol (SPY/QQQ/IWM)

- ✅ **单条消息**：所有信号汇总到一条通知，无骚扰
- ✅ **去重**：上升沿检测防止重复
- ✅ **丰富上下文**：包含得分和趋势，方便快速决策
- ✅ **自动检测**：自动匹配图表标的（SPY/QQQ/IWM）

---

## Technical Details | 技术细节

### Adaptive Lookback Calculation | 自适应回溯期计算

```pine
// Step 1: Short-term volatility (自适应到RSI长度)
vol_short_period = rsiLen × 4
vol_short = ta.stdev(spyRSI, vol_short_period)

// Step 2: Long-term volatility (根据历史深度)
vol_long_period = min(1000, vol_history_days × bars_per_day)
vol_long = ta.stdev(spyRSI, vol_long_period)

// Step 3: Dynamic weighting (动态加权)
vol_base = vol_long × 0.7 + vol_short × 0.3
recent_high = vol_short > vol_long × 1.2
vol_dynamic = recent_high ? (vol_short × 0.6 + vol_long × 0.4) : vol_base

// Step 4: Statistical calculation (统计公式)
stat_required = pow(1.96 × vol_final / E, 2)
auto_lookback = clamp(stat_required, 100, 1000)
```

### Health Check Criteria | 健康检查标准

- ✅ Sample Coverage: `bar_index ≥ lookback × 0.8`
- ✅ Statistical Validity: `actual_lookback ≥ required × 0.9`
- ✅ Distribution Spread: `(OB1 - OS1) ≥ 12` (for indices)

---

## Limitations | 局限性

- Requires sufficient historical data (minimum ~100 bars) | 需要足够历史数据（最少约100根K线）
- Market breadth data (TW/FI) only available for US markets | 市场广度数据仅适用于美股
- Intraday mode works best on hourly charts | 日内模式在小时图效果最佳
- Divergence detection may lag in fast-moving markets | 快速市场中背离检测可能滞后

---

## Changelog | 更新日志

### v6.2 (2025-12-17)

**⏱️ Dynamic Cooldown System | 动态冷却系统**
- **Volatility-Adaptive Cooldown**: Automatically adjusts signal cooldown period based on market volatility
  波动率自适应冷却：根据市场波动率自动调整信号冷却期
- **High Volatility Mode**: 60% cooldown for fast-moving markets (quick response)
  高波动模式：快速市场使用60%冷却期（快速响应）
- **Low Volatility Mode**: 150% cooldown for calm markets (reduce noise)
  低波动模式：平静市场使用150%冷却期（降低噪音）
- **Minimum Protection**: Always maintains minimum 3-bar cooldown
  最小保护：始终保持至少3根K线的冷却期
- **Dashboard Display**: Shows current cooldown bars and mode (Dyn/Fix) in panel
  面板显示：在面板中显示当前冷却K线数和模式（动态/固定）

---

### v6.1 (2025-12-16)

**🔔 Smart Alert System | 智能警报系统**
- **Unified Smart Alert**: Replaced multiple `alertcondition` calls with a single unified alert system
  统一智能警报：用单一警报系统替代多个 alertcondition 调用
- **Rising Edge Detection**: Prevents duplicate notifications by only triggering when signals change from OFF → ON
  上升沿检测：仅在信号从无到有时触发，防止重复通知
- **Aggregated Messages**: All triggered signals (MTF, Divergence, Resonance) combined into one message
  信号汇总：所有触发的信号（多因子、背离、共振）合并为一条消息
- **Context Info**: Includes Score and Trend direction for quick decision making
  上下文信息：包含得分和趋势方向，便于快速决策

---

### v6.0 (2025-12-15)

**🧠 Adaptive Technology | 自适应技术**
- **Auto-Adaptive Lookback**: Statistical formula `n=(Z×σ/E)²` for optimal lookback period (100-1000 bars)
  自动回溯期：使用统计公式自动计算最优回溯期
- **Dual Volatility System**: 70% long-term + 30% short-term volatility weighting
  双重波动率：长期70%+短期30%动态加权
- **Dual Detection Thresholds**: Fast (1.5×RSI) + Slow (3×RSI) confirmation
  双重检测：快速触发+慢速确认

**💎 Smart Divergence | 智能背离**
- **Dynamic Lookback**: Divergence period linked to RSI length (4×)
  动态回溯：背离周期关联RSI长度
- **Z-Score Detection**: Statistical divergence strength measurement
  Z值检测：统计背离强度测量
- **Cooldown Period**: Prevents duplicate divergence signals
  冷却期：防止重复背离信号

**📊 Dashboard Enhancements | 面板增强**
- **Health Monitor**: Real-time validation of lookback statistics
  健康监控：实时验证回溯统计有效性
- **Mode Display**: Shows current threshold mode (Fixed/Adaptive)
  模式显示：显示当前阈值模式

**🔥 Market Resonance | 市场共振**
- Multi-market simultaneous signal detection (SPY/QQQ/IWM)
  多市场同时信号检测

**📈 Intraday Support | 日内支持**
- Uses ADD (Advance-Decline) instead of daily breadth for hourly charts
  小时图自动使用涨跌差代替每日广度

---

## Disclaimer | 免责声明

This indicator is for educational and research purposes only. Past performance does not guarantee future results. Always conduct your own analysis and risk management.

本指标仅供教育和研究用途。历史表现不代表未来收益。请务必进行自己的分析和风险管理。

---

**Version**: 6.2  
**Pine Script**: v6  
**Last Updated**: 2025-12-17

