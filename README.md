# RSI+ Breadth Multi-Factor Indicator

**Multi-factor scoring system for US market timing | 美股多因子择时评分系统**

[![TradingView](https://img.shields.io/badge/TradingView-Indicator-blue?logo=tradingview)](https://www.tradingview.com/)
[![Pine Script](https://img.shields.io/badge/Pine%20Script-v5-brightgreen)](https://www.tradingview.com/pine-script-docs/en/v5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview | 概述

A quantitative indicator that combines **RSI**, **market breadth** (% above 20/50-day MA), and **up/down volume ratio** to generate actionable buy/sell signals for SPY, QQQ, and IWM.

这是一个结合 **RSI**、**市场广度**（站上20/50日均线比例）和 **涨跌成交量比** 的量化指标，为 SPY、QQQ 和 IWM 生成可操作的买卖信号。

---

## Features | 功能特点

| Feature | 功能 |
|---------|------|
| 🎯 Multi-factor scoring (-10 to +10) | 多因子评分系统 (-10 到 +10) |
| 📊 RSI + Breadth + Volume integration | RSI + 广度 + 成交量三重验证 |
| 🔀 Three markets: SPY, QQQ, IWM | 三大市场：SPY、QQQ、IWM |
| 🔥 Cross-market resonance detection | 跨市场共振信号检测 |
| 📈 Trend filter (MA-based) | 趋势过滤（均线判断） |
| ⏰ Auto-adapts to intraday timeframes | 自动适配日内时间周期 |
| 🎚️ Three modes: Aggressive/Standard/Conservative | 三种模式：激进/标准/保守 |

---

## Signal Reference | 信号说明

| Score | Emoji | Signal | 中文 | Action |
|:-----:|:-----:|--------|:----:|--------|
| ≥ 6 | 🚀 | **PANIC LOW** | 恐慌低点 | Strong buy 强烈买入 |
| ≥ 4 | 📈 | **BUY ZONE** | 低吸区 | Accumulate 分批建仓 |
| -3~3 | - | **HOLD** | 持有 | Hold position 持仓观望 |
| ≤ -4↑ | ⭐ | **ELEVATED** | 高估 | Hold cautious 持有但谨慎 |
| ≤ -4↓ | ⚡ | **CAUTION** | 观望 | Take profit 止盈 |
| ≤ -6↓ | ⚠️ | **REDUCE** | 减仓 | Reduce position 减少仓位 |

> **↑ = Uptrend** (price > MA) | **↓ = Downtrend** (price < MA)

### Resonance Signals | 共振信号

| Emoji | Signal | Description |
|:-----:|--------|-------------|
| 🔥 | Resonance Buy | Multiple markets in buy zone 多市场同时低吸 |
| ❄️ | Resonance Risk | Multiple markets in risk zone 多市场同时高估 |

---

## Scoring Logic | 评分逻辑

### Factors | 因子

| Factor | Weight | Buy Score | Sell Score |
|--------|--------|-----------|------------|
| **RSI** | 1x | RSI < 30 → +2, < 40 → +1 | RSI > 75 → -2, > 65 → -1 |
| **FI (50D MA%)** | Bottom focus | < 25% → +3, < 35% → +2 | > 85% → -2, > 78% → -1 |
| **TW (20D MA%)** | Top focus | < 30% → +1 | > 82% → -3, > 72% → -2 |
| **Volume Ratio** | 1x | UVOL/DVOL < 0.5 → +2 | > 2.5 → -2 |

### Breadth Symbols | 广度数据

| Market | TW Symbol | FI Symbol | Volume |
|--------|-----------|-----------|--------|
| SPY (S&P 500) | INDEX:S5TW | INDEX:S5FI | USI:UVOL/DVOL |
| QQQ (NASDAQ) | INDEX:NCTW | INDEX:NCFI | USI:UVOLQ/DVOLQ |
| IWM (Russell 2000) | INDEX:R2TW | INDEX:R2FI | USI:UVOL/DVOL |

---

## Settings | 设置说明

### Mode | 模式
- **Aggressive**: Lower thresholds, shorter cooldown (5 bars)
- **Standard**: Balanced defaults (10 bar cooldown)  
- **Conservative**: Higher thresholds, longer cooldown (15 bars)

### Key Parameters | 关键参数
| Parameter | Default | Description |
|-----------|---------|-------------|
| RSI Length | 14 | RSI calculation period |
| Trend MA Length | 10 | MA for trend filter |
| Cooldown Bars | 10 | Min bars between same signals |
| Resonance Window | 3 | Bars to check for multi-market agreement |
| Min Markets | 2 | # of markets needed for resonance |

---

## Usage | 使用方法

### Installation | 安装
1. Copy the indicator code
2. In TradingView: **Pine Editor** → **New** → Paste code → **Add to Chart**

### Recommended Setup | 推荐设置
- **Timeframe**: Daily (D) for best accuracy | 推荐日线图
- **Markets**: Apply on SPY, QQQ, or IWM | 应用于SPY/QQQ/IWM
- **Mode**: Start with "Standard" | 建议从"标准"模式开始

### Intraday Mode | 日内模式
The indicator automatically detects intraday timeframes and adjusts:
- Uses only RSI + Volume factors (TW/FI are daily-only data)
- Lowers signal thresholds accordingly

指标会自动检测日内周期并调整：
- 仅使用 RSI + 成交量因子（TW/FI 仅有日线数据）
- 相应降低信号触发阈值

---

## Dashboard | 仪表盘

Displays real-time factor breakdown:

```
┌────────┬───────┬────────┐
│ Factor │ Score │ Weight │
├────────┼───────┼────────┤
│ RSI    │  1.0  │   1x   │
│ FI(50D)│  2.0  │ Bottom │
│ TW(20D)│ -1.0  │  Top   │
│ Vol    │  1.0  │   1x   │
│ Trend  │  ↑    │  10MA  │
├────────┼───────┼────────┤
│ Total  │  3.0  │  HOLD  │
└────────┴───────┴────────┘
```

---

## Alerts | 警报

Available alerts for each market (SPY/QQQ/IWM):
- Panic Low / Buy Zone (entry signals)
- Reduce / Caution (exit signals)
- Resonance Buy / Risk (cross-market confirmation)

每个市场（SPY/QQQ/IWM）可设置以下警报：
- 恐慌低点 / 低吸区（入场信号）
- 减仓 / 观望（出场信号）
- 共振买入 / 风险（跨市场确认）

---

## Trend Filter | 趋势过滤

**Key feature**: Risk signals (CAUTION/REDUCE) only trigger when **price is below the trend MA**.

When price is above MA (uptrend), the indicator shows **ELEVATED** ⭐ instead, preventing premature exits during strong rallies.

**核心功能**：风险信号（观望/减仓）仅在 **价格跌破趋势均线** 时触发。

当价格在均线之上（上升趋势）时，指标显示 **高估** ⭐，避免在强势上涨中过早离场。

---

## Disclaimer | 免责声明

This indicator is for **educational and informational purposes only**. It is not financial advice. Past performance does not guarantee future results. Always do your own research and consider your risk tolerance before trading.

本指标仅供 **教育和参考用途**，不构成投资建议。历史表现不代表未来收益。交易前请自行研究并考虑风险承受能力。

---

## License | 许可

MIT License - Free to use and modify with attribution.

MIT 许可证 - 可自由使用和修改，请注明出处。

---

## Author | 作者

Built with ❤️ for the trading community.

为交易社区精心打造 ❤️
