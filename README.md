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
| 🧠 | **Adaptive Lookback** | **自适应回溯**：使用统计公式 n=(Z×σ/E)² 自动计算最优回溯期 |
| 💎 | **Smart Divergence** | **智能背离**：背离回溯期自动关联 RSI 长度 (4×)，避免周期错配 |
| ⚡ | **Dual Detection** | **双重检测**：快速触发(1.5×)+慢速确认(3×)，更快响应市场变化 |
| 📊 | **Health Monitor** | **健康监控**：实时验证 Lookback 统计有效性与分布宽度 |
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

### Advanced / 高级设置

- **Lookback Mode / 回溯模式**:
    - `Auto`: 使用统计公式自适应计算 (推荐大盘指数)
    - `Fixed 252`: 传统固定 1 年
    - `Custom`: 自定义数值 (100-1000)
    
- **Lookback Precision / 回溯精度**: 
    - `High`: E=2.0 更精确，Lookback 更长 (大盘指数推荐)
    - `Normal`: E=2.5 平衡
    - `Low`: E=3.5 更宽松，Lookback 更短
    
- **Vol History / 波动历史**: 长期波动率的历史深度
    - `6 Months`: 适合快速变化的市场
    - `1 Year`: 默认，平衡性好
    - `2 Years`: 适合稳定市场

- **Threshold Mode / 阈值模式**:
    - `Auto`: 根据 RSI 波动率自动选择 (推荐)
    - `Fixed`: 使用固定阈值 (30/70)
    - `Adaptive`: 始终使用历史百分位阈值

- **RSI Vol Threshold / RSI波动阈值**: Auto 模式切换阈值
    - 大盘指数建议: 8.0
    - 个股建议: 10.0

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
