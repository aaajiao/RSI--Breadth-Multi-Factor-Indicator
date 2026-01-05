# RSI+ Breadth Multi-Factor Indicator v7.2

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/scripts/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-reference/v6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## English Documentation

### Overview

RSI+ is a comprehensive quantitative indicator designed for US market timing (SPY, QQQ, IWM). It combines **RSI**, **Market Breadth**, **Volume Ratio**, and **Divergence** into a single composite score to identify high-probability reversal points. Version 7.2 features a **Progress Bar Dashboard** for intuitive visual analysis.

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
| ≥ 6 | 🚀 | **PANIC LOW** | **Strong Buy** | Extreme oversold + panic selling |
| ≥ 4 | 📈 | **BUY ZONE** | **Accumulate** | Multi-factor confirmed buy signal |
| DIV | 💎 | **DIVERGENCE**| **Reversal** | Price vs. RSI divergence detected |
| -3~3| - | **HOLD** | **Hold** | Neutral zone |
| ≤ -4↑| ⭐ | **ELEVATED** | **Caution** | Overbought but uptrend |
| ≤ -4↓| ⚡ | **CAUTION** | **Take Profit**| Overbought + downtrend |
| ≤ -6↓| ⚠️ | **REDUCE** | **Reduce** | Extreme overbought + breakdown |

**Resonance**: 🔥 Buy (2+ markets bullish) | ❄️ Risk (2+ markets bearish)

### Dashboard Guide (v7.2)

**Visual Elements**:
- `█` Filled bar | `░` Empty bar
- 🟢 Buy Zone | 🟡 Neutral | 🔴 Risk Zone
- Frame color: Green (buy) / Red (sell) / Gray (neutral)

**Full Mode (8 rows)**:

| Row | Content | Description |
|:---:|---------|-------------|
| 0 | `🚀 PANIC LOW +6.5↑` | Signal emoji + name + score with trend |
| 1 | `░░░░░░│██████████` | Score bar: left = negative, right = positive |
| 2 | `RSI █████ +2  Vol ███ +1` | RSI and Volume factor bars |
| 3 | `FI █████ +3   TW ████ +1` | Market Breadth factor bars (FI/ADD + TW) |
| 4 | `Trend ↑UP   💎 BULL` | Trend direction + Divergence status |
| 5 | `Quality █████ A  3/4` | Signal quality grade + aligned factors |
| 6 | `DD ██████░░ 8.2% +2` | Drawdown % bar + bonus score |
| 7 | `SPY🟢 QQQ🟢 IWM🟡 🔥` | Three-market status + resonance |

**Mobile Mode (4 rows)**: Compact version with score bar + three-market resonance.

### Recommended Settings

| Scenario | Mode | Lookback | Precision | Vol Threshold |
|:---------|:-----|:---------|:----------|:--------------|
| **Index** (SPY/QQQ) | `Standard` | `Auto` | `High` | `8.0` |
| **Stock** (NVDA) | `Aggressive` | `Auto` | `Normal`| `10.0` |
| **Intraday** | `Standard` | `Auto` | `Normal`| `8.0` |

### Changelog

**v7.2** - Progress bar dashboard redesign (13→8 rows), three-market resonance display, dynamic frame colors.

**v7.1** - Bug fixes for alerts, cooldown logic, market driver RSI, drawdown buy-only.

**v7.0** - Signal quality filter (A/B/C), drawdown bonus, divergence assist.

---

## 中文说明文档

### 概述

RSI+ 是专为美股指数（SPY, QQQ, IWM）设计的量化择时系统。结合 **RSI**、**市场广度**、**成交量比** 和 **背离** 计算综合评分，识别高胜率反转点。v7.2 版本引入 **进度条可视化面板**，让分析更直观。

### 快速入门

1. **添加到图表**：建议在 **SPY**, **QQQ**, 或 **IWM** 日线图使用。
2. **配置**：指数用 `Standard`，个股用 `Aggressive`。
3. **解读**：正分(4+)关注买入，负分(-4以下)注意风险，🔥共振信号胜率更高。

### 信号参考

| 分数 | 图标 | 信号 | 操作 | 条件 |
|:----:|:----:|------|------|------|
| ≥ 6 | 🚀 | **恐慌低点** | **强买** | 极端超卖 + 恐慌抛售 |
| ≥ 4 | 📈 | **低吸区** | **建仓** | 多因子确认 |
| DIV | 💎 | **背离** | **反转** | 价格与RSI背离 |
| -3~3 | - | **持有** | **观望** | 中性区域 |
| ≤ -4↑| ⭐ | **高估** | **谨慎** | 超买但上升趋势 |
| ≤ -4↓| ⚡ | **观望** | **止盈** | 超买 + 下降趋势 |
| ≤ -6↓| ⚠️ | **减仓** | **减仓** | 极端超买 + 破位 |

**共振**：🔥 共振买入 (2+市场看多) | ❄️ 共振风险 (2+市场看空)

### 面板指南 (v7.2)

**视觉元素**：
- `█` 填充格 | `░` 空格
- 🟢 买入区 | 🟡 中性 | 🔴 风险区
- 边框颜色：绿色(买入) / 红色(卖出) / 灰色(中性)

**完整模式 (8行)**：

| 行 | 内容 | 说明 |
|:--:|------|------|
| 0 | `🚀 PANIC LOW +6.5↑` | 信号图标 + 名称 + 分数趋势 |
| 1 | `░░░░░░│██████████` | 分数条：左负右正，中线为0 |
| 2 | `RSI █████ +2  Vol ███ +1` | RSI 和成交量因子条 |
| 3 | `FI █████ +3   TW ████ +1` | 市场广度因子条 (FI/ADD + TW) |
| 4 | `Trend ↑UP   💎 BULL` | 趋势方向 + 背离状态 |
| 5 | `Quality █████ A  3/4` | 信号质量等级 + 同向因子数 |
| 6 | `DD ██████░░ 8.2% +2` | 回撤百分比条 + 加分 |
| 7 | `SPY🟢 QQQ🟢 IWM🟡 🔥` | 三市场状态 + 共振指示 |

**精简模式 (4行)**：压缩版，含分数条 + 三市场共振。

### 推荐设置

| 场景 | 模式 | 回溯 | 精度 | 波动阈值 |
|:-----|:-----|:-----|:-----|:---------|
| **指数** (SPY/QQQ) | `Standard` | `Auto` | `High` | `8.0` |
| **个股** (NVDA) | `Aggressive` | `Auto` | `Normal`| `10.0` |
| **日内** | `Standard` | `Auto` | `Normal`| `8.0` |

### 更新日志

**v7.2** - 进度条面板重构 (13→8行)，三市场共振显示，动态边框颜色。

**v7.1** - 修复警报、冷却逻辑、市场驱动RSI、回撤仅买入方向。

**v7.0** - 信号质量过滤 (A/B/C)，回撤加分，背离助推。

---

## Disclaimer | 免责声明

This indicator is for educational purposes only. Past performance does not guarantee future results.

本指标仅供教育用途。历史表现不代表未来收益。

**Version**: 7.2 | **Pine Script**: v6 | **Updated**: 2025-01-05
