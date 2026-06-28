---
name: technical-indicators
description: Technical indicator calculations for A-shares including MACD trend analysis, KDJ stochastic oscillator, and RSI relative strength index. Returns time-series data with indicator values for each period.
---

# Technical Indicators

Calculate technical indicators using the mist stock analysis backend.

## Available Scripts

### macd
MACD (Moving Average Convergence Divergence) — trend-following momentum indicator.
Default parameters: fast=12, slow=26, signal=9.
```bash
python scripts/macd.py --code 000001.SH --period daily --start-date "2026-01-01" --end-date "2026-04-13"
```
Returns: Array of `{macd, signal, histogram, symbol, time, close}`.

### kdj
KDJ Stochastic Oscillator — identifies overbought/oversold conditions.
Default parameters: period=14, kSmoothing=3, dSmoothing=3.
```bash
python scripts/kdj.py --code 000001.SH --period daily --start-date "2026-01-01" --end-date "2026-04-13"
```
Returns: Array of `{k, d, j, symbol, time, close}`.

### rsi
RSI (Relative Strength Index) — measures momentum and divergence.
Default period: 14.
```bash
python scripts/rsi.py --code 000001.SH --period daily --start-date "2026-01-01" --end-date "2026-04-13"
```
Returns: Array of `{rsi, symbol, time, close}`.

## Common Parameters

All indicator scripts accept:
- `--code` (required): Security code, e.g. `000001.SH`
- `--period` (required): Time period — `1min`, `5min`, `15min`, `30min`, `60min`, `daily` (converted to Mist numeric period values before request)
- `--start-date` (required): Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `--end-date` (required): End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `--source` (optional): Data source — `ef`, `tdx`, `mqmt`

## Choosing an Indicator

- **MACD**: Trend direction, momentum shifts, crossovers
- **KDJ**: Overbought (>80) / oversold (<20) conditions, short-term reversals
- **RSI**: Momentum strength (0-100), divergence detection, overbought (>70) / oversold (<30)

## Mist API Notes

The current Mist backend expects numeric period enum values. Use the aliases
above in Skill calls; scripts convert them automatically.
