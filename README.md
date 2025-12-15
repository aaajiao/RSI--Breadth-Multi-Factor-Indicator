# RSI+ Breadth Multi-Factor Indicator v6

**Adaptive Scoring System for US Market Timing | 美股多因子自适应择时系统**

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-brightgreen)](https://www.tradingview.com/pine-script-docs/en/v6/)

---

## Overview | 概述

A quantitative indicator that combines **RSI**, **Market Breadth**, **Volume Ratio**, and **Divergence** to generate actionable buy/sell signals. Version 6 introduces **Adaptive Technology**, automatically adjusting signal thresholds based on market volatility.

这是一个结合 **RSI**、**市场广度**、**成交量比** 和 **背离** 的量化指标。v6 版本引入了 **自适应技术**，能根据市场波动率自动调整信号阈值。

---

## What's New in v6 | v6 新功能

| Feature | Description | 中文说明 |
|:---:|---|---|
| 🧠 | **Adaptive Thresholds** | **自适应阈值**：基于历史波动率自动调整 RSI 超买超卖线 |
| 💎 | **Divergence Detection** | **背离检测**：基于 Z-Score 强度的价格与 RSI 背离 |
| ⚡ | **Auto Mode** | **自动模式**：高波动时自动切换为自适应，低波动保持固定 |
| 📉 | **Intraday Breadth** | **日内广度**：使用 `USI:ADD` (涨跌家数差) 支持小时图广度分析 |

---

## Signal Reference | 信号说明

| Score | Emoji | Signal | 中文 | Action |
|:-----:|:-----:|--------|:----:|--------|
| ≥ 6 | 🚀 | **PANIC LOW** | 恐慌低点 | Strong buy 强烈买入 |
| ≥ 4 | 📈 | **BUY ZONE** | 低吸区 | Accumulate 分批建仓 |
| Div | 💎 | **DIVERGENCE** | 背离 | Reversal Confirmation 反转确认 |
| -3~3 | - | **HOLD** | 持有 | Hold position 持仓观望 |
| ≤ -4↑ | ⭐ | **ELEVATED** | 高估 | Hold cautious 持有但谨慎 |
| ≤ -4↓ | ⚡ | **CAUTION** | 观望 | Take profit 止盈 |
| ≤ -6↓ | ⚠️ | **REDUCE** | 减仓 | Reduce position 减少仓位 |

> **↑ = Uptrend** (Price > MA) | **↓ = Downtrend** (Price < MA)

---

## Adaptive Logic | 自适应逻辑

### How it works | 工作原理
The indicator monitors the volatility of RSI (Standard Deviation).
-   **Low Volatility**: Uses classic fixed thresholds (30/70) to avoid noise.
-   **High Volatility**: Switches to percentiles (e.g., historical 10% / 90%) to catch extremes that fixed levels might miss.

指标监控 RSI 的波动率（标准差）：
-   **低波动**: 使用经典固定阈值 (30/70) 以避免噪音。
-   **高波动**: 切换到历史百分位 (如历史 10%/90%)，以捕捉固定阈值可能错过的极端行情。

### Auto Mode | 自动模式
-   **Setting**: `Threshold Mode = Auto`
-   Automatically toggles between **Fixed** and **Adaptive** based on real-time market conditions.

---

## Settings | 设置说明

### Adaptive / 自适应
-   **Threshold Mode**:
    -   `Auto`: Recommended. Smart switching. (推荐)
    -   `Fixed`: Classic behavior (30/70).
    -   `Adaptive`: Always use percentile-based thresholds.
-   **History Lookback**: Period for calculating percentiles (Default: 252 days).

### Divergence / 背离
-   **Enable Divergence**: Turn on/off 💎 signals.
-   **Z-Score Threshold**: Strength required to trigger divergence (Default: 1.5).

### Intraday vs Daily
-   **Daily**: Uses Breadth (stocks > 20/50MA) for scoring.
-   **Intraday**: Automatically switches to use **Advance-Decline (ADD)** data for breadth scoring.

---

## Disclaimer | 免责声明

This indicator is for educational purposes only. Past performance does not guarantee future results.

本指标仅供教育用途。历史表现不代表未来收益。
