# RSI+ Breadth Multi-Factor Indicator v7.1

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/scripts/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-reference/v6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## English Documentation

### Overview

RSI+ is a comprehensive quantitative indicator designed for US market timing (SPY, QQQ, IWM). It combines **RSI**, **Market Breadth**, **Volume Ratio**, and **Divergence** into a single composite score to identify high-probability reversal points. Version 7.1 features **Adaptive Technology** that automatically adjusts lookback periods and thresholds based on market volatility.

### Quick Start Guide

1. **Add to Chart**: Best used on **SPY**, **QQQ**, or **IWM** daily charts.
2. **Configuration**:
   - For **Index ETFs**: Use default settings (`Standard` mode, `Auto` lookback).
   - For **Individual Stocks**: Switch Mode to `Aggressive`.
3. **Interpretation**:
   - Look for **Positive Scores (4+)** for buying opportunities.
   - Look for **Negative Scores (-4 and below)** for risks.
   - Watch for **Resonance (🔥)** signals where multiple markets align.

### Signal Reference

| Score | Emoji | Signal | Action | Condition |
|:-----:|:-----:|--------|--------|-----------|
| ≥ 6 | 🚀 | **PANIC LOW** | **Strong Buy** | Extreme oversold conditions + panic selling |
| ≥ 4 | 📈 | **BUY ZONE** | **Accumulate** | Solid buy signal confirmed by multiple factors |
| DIV | 💎 | **DIVERGENCE**| **Reversal** | Price vs. RSI divergence detected |
| -3~3| - | **HOLD** | **Hold** | Neutral zone, stay the course |
| ≤ -4↑| ⭐ | **ELEVATED** | **Caution** | Overbought but trend is still up |
| ≤ -4↓| ⚡ | **CAUTION** | **Take Profit**| Overbought with downtrend starting |
| ≤ -6↓| ⚠️ | **REDUCE** | **Reduce** | Extreme overbought + breakdown risk |

**Resonance Signals**:
- 🔥 **Resonance Buy**: 2+ markets (e.g., SPY & QQQ) are in the Buy Zone simultaneously.
- ❄️ **Resonance Risk**: 2+ markets are in the Risk Zone simultaneously.

### Dashboard Guide

The dashboard provides a real-time health check of the market internals.

| Row | Indicator | Description |
|:---:|-----------|-------------|
| **RSI** | Relative Strength | Primary driver. Uses adaptive thresholds based on volatility. |
| **FI/TW** | Market Breadth | Percentage of stocks above 20D/50D moving averages. |
| **Vol** | Volume Ratio | Ratio of Up-Volume to Down-Volume (UVOL/DVOL). |
| **Trend** | Market Trend | Current trend direction (Up/Down) based on MA. |
| **Div** | Divergence | Real-time detection of Bullish/Bearish divergences. |
| **Quality** | Signal Quality | **A/B/C Grade**. v7.0+ filters out low-quality "C" signals. |
| **Drawdown**| DD Bonus | Bonus score (+1/+2/+3) applied during significant market drawdowns. |
| **Total** | Composite Score | Final weighted score. Triggers signals when thresholds are met. |

### Recommended Settings

| Scenario | Mode | Lookback | Precision | Vol Threshold |
|:---------|:-----|:---------|:----------|:--------------|
| **Index Trading** (SPY/QQQ) | `Standard` | `Auto` | `High` | `8.0` |
| **Stock Trading** (NVDA/AAPL)| `Aggressive` | `Auto` | `Normal`| `10.0` |
| **Intraday** (Hourly) | `Standard` | `Auto` | `Normal`| `8.0` |

### Recent Changes

**v7.1 (Latest)**
- 🔧 **Fixes**: Resolved alert upgrade triggers and cooldown logic issues.
- 🎯 **Market Driver**: Each market now strictly uses its own RSI for adaptive calculations.
- 📉 **Logic**: Drawdown bonus now correctly applies only to buy signals.

**v7.0**
- 🎯 **Quality Filter**: New A/B/C grading system to filter weak signals.
- 📉 **Drawdown Bonus**: Adds score bonuses during 5%/10%/20% drawdowns.
- 💎 **Divergence Assist**: Allows divergence to trigger signals that are slightly below threshold.

---

## 中文说明文档 (Chinese Documentation)

### 概述 | Overview

RSI+ 是一个专为美股指数（SPY, QQQ, IWM）设计的量化择时系统。它结合了 **RSI**、**市场广度**、**成交量比** 和 **背离** 等多个因子，计算出一个综合评分来识别高胜率的反转点。v7.1 版本引入了 **自适应技术**，能够根据市场波动率自动调整回溯期和信号阈值。

### 快速入门 | Quick Start

1. **添加到图表**：建议在 **SPY**, **QQQ**, 或 **IWM** 的日线图上使用。
2. **配置建议**：
   - **指数 ETF**：使用默认设置（`Standard` 模式，`Auto` 回溯）。
   - **个股交易**：将模式切换为 `Aggressive`（更灵敏）。
3. **如何解读**：
   - **正分 (4+)**：关注买入机会。
   - **负分 (-4 及以下)**：注意风险，考虑止盈。
   - **共振 (🔥)**：当多个市场同时出现信号时，胜率更高。

### 信号参考 | Signal Reference

| 分数 | 图标 | 信号名称 | 操作建议 | 触发条件 |
|:----:|:----:|----------|----------|----------|
| ≥ 6 | 🚀 | **恐慌低点** | **强烈买入** | 极端超卖 + 恐慌性抛售 |
| ≥ 4 | 📈 | **低吸区** | **分批建仓** | 多因子确认的稳健买入信号 |
| DIV | 💎 | **背离** | **反转确认** | 价格与 RSI 出现顶/底背离 |
| -3~3 | - | **持有** | **持仓观望** | 中性区域，趋势延续 |
| ≤ -4↑| ⭐ | **高估** | **谨慎持有** | 超买但趋势向上，警惕回调 |
| ≤ -4↓| ⚡ | **观望** | **获利了结** | 超买且趋势开始向下 |
| ≤ -6↓| ⚠️ | **减仓** | **降低仓位** | 极端超买 + 破位风险 |

**共振信号**：
- 🔥 **共振买入**：2个或以上市场（如 SPY 和 QQQ）同时进入低吸区。
- ❄️ **共振风险**：2个或以上市场同时进入高风险区。

### 面板指南 | Dashboard Guide

仪表板提供实时的市场内部健康检查。

| 行名称 | 指标含义 | 说明 |
|:------:|----------|------|
| **RSI** | 相对强弱 | 核心因子。基于波动率使用自适应阈值。 |
| **FI/TW** | 市场广度 | 股价高于20日/50日均线的股票比例。 |
| **Vol** | 成交量比 | 上涨量与下跌量的比率 (UVOL/DVOL)。 |
| **Trend** | 市场趋势 | 当前均线趋势方向 (↑上涨 / ↓下跌)。 |
| **Div** | 背离检测 | 实时检测看涨/看跌背离。 |
| **Quality** | 信号质量 | **A/B/C 分级**。v7.0+ 自动过滤低质量 "C" 级信号。 |
| **Drawdown**| 回撤加分 | 在市场显著回撤时给予额外加分 (+1/+2/+3)。 |
| **Total** | 综合得分 | 最终加权得分。达到阈值时触发信号。 |

### 推荐设置 | Recommended Settings

| 交易场景 | 模式 (Mode) | 回溯模式 (Lookback) | 精度 (Precision) | 波动阈值 (Vol Threshold) |
|:---------|:------------|:--------------------|:-----------------|:-------------------------|
| **指数交易** (SPY/QQQ) | `Standard` | `Auto` | `High` | `8.0` |
| **个股交易** (NVDA等) | `Aggressive` | `Auto` | `Normal`| `10.0` |
| **日内交易** (小时图) | `Standard` | `Auto` | `Normal`| `8.0` |

### 最近更新 | Recent Changes

**v7.1 (最新版)**
- 🔧 **修复**：修正了警报升级触发和冷却逻辑的问题。
- 🎯 **市场驱动**：每个市场现在严格使用其自身的 RSI 进行自适应计算。
- 📉 **逻辑优化**：回撤加分现在正确地仅应用于买入信号。

**v7.0**
- 🎯 **质量过滤**：引入 A/B/C 分级系统，自动过滤微弱信号。
- 📉 **回撤加分**：在指数回撤 5%/10%/20% 时增加买入评分。
- 💎 **背离助推**：允许背离信号助推那些略低于阈值的边缘机会。

---

## Disclaimer | 免责声明

This indicator is for educational and research purposes only. Past performance does not guarantee future results. Always conduct your own analysis and risk management.

本指标仅供教育和研究用途。历史表现不代表未来收益。请务必进行自己的分析和风险管理。

**Version**: 7.1
**Pine Script**: v6
**Last Updated**: 2025-01-05
