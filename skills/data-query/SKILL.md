---
name: data-query
description: Market data discovery and retrieval for A-shares. List available securities, get security details, and query K-line data across intraday and daily periods from the mist backend.
---

# Data Query

Retrieve market data from the mist stock analysis backend.

## Available Scripts

### list_indices
List all available securities (stocks, indices, funds).
```bash
python scripts/list_indices.py
```
Returns: Array of `{id, symbol, name, type}` objects.

### get_index_info
Get details for a specific security by code.
```bash
python scripts/get_index_info.py --code 000001.SH
```
Parameters:
- `--code` (required): Security code, e.g. `000001.SH`, `399006.SZ`

### get_kline_data
Query intraday K-line data.
```bash
python scripts/get_kline_data.py --code 000001.SH --period 5min --start-date "2026-01-01" --end-date "2026-04-13"
```
Parameters:
- `--code` (required): Security code
- `--period` (required): One of `1min`, `5min`, `15min`, `30min`, `60min`
- `--start-date` (required): Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `--end-date` (required): End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `--source` (optional): Data source — `ef` (East Money), `tdx` (TongDaXin), `mqmt` (MaQiMaTe)

### get_daily_kline
Query daily K-line data.
```bash
python scripts/get_daily_kline.py --code 000001.SH --start-date "2026-01-01" --end-date "2026-04-13"
```
Parameters:
- `--code` (required): Security code
- `--start-date` (required): Start date
- `--end-date` (required): End date
- `--source` (optional): Data source

## Usage Pattern

1. Run `list_indices` first to discover available securities
2. Use `get_index_info` to verify a specific symbol
3. Query K-line data with `get_kline_data` (intraday) or `get_daily_kline` (daily)

## Response Fields

K-line data returns: `id`, `symbol`, `time`, `amount`, `open`, `close`, `highest`, `lowest`.
