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
Query intraday K-line data. If stored data is missing, this script can
initialize the security, attach a data source, trigger Mist collection, and
retry the query.
```bash
python scripts/get_kline_data.py --code 600519.SH --name "贵州茅台" --period 60min --start-date "2026-06-26 09:30:00" --end-date "2026-06-26 15:00:00"
```
Parameters:
- `--code` (required): Security code
- `--period` (required): One of `1min`, `5min`, `15min`, `30min`, `60min` (converted to Mist numeric period values before request)
- `--start-date` (required): Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `--end-date` (required): End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `--source` (optional): Data source — `ef` (East Money), `tdx` (TongDaXin), `mqmt` (MaQiMaTe). Defaults to `MIST_DEFAULT_SOURCE` or `tdx`
- `--name` (optional): Security display name used when the security must be initialized
- `--no-auto-collect` (optional): Only query stored data; do not initialize or collect

### get_daily_kline
Query daily K-line data. If stored data is missing, this script can initialize
the security, attach a data source, trigger Mist collection, and retry the query.
```bash
python scripts/get_daily_kline.py --code 600519.SH --name "贵州茅台" --start-date "2026-06-21" --end-date "2026-06-28"
```
Parameters:
- `--code` (required): Security code
- `--start-date` (required): Start date
- `--end-date` (required): End date
- `--source` (optional): Data source, defaults to `MIST_DEFAULT_SOURCE` or `tdx`
- `--name` (optional): Security display name used when the security must be initialized
- `--no-auto-collect` (optional): Only query stored data; do not initialize or collect

## Usage Pattern

1. Run `list_indices` first to discover available securities
2. Use `get_index_info` to verify a specific symbol
3. Query K-line data with `get_kline_data` (intraday/minute/hour) or `get_daily_kline` (daily)
4. For a daily query like "贵州茅台最近一周日线", call `get_daily_kline` directly with `--code 600519.SH --name "贵州茅台"`; do not try `POST /security/v1`, because Mist uses `POST /security/v1/initialize`, `POST /security/v1/sources`, and `POST /v1/collector/collect` internally.

## Response Fields

K-line data returns: `id`, `symbol`, `time`, `amount`, `open`, `close`, `highest`, `lowest`.

## Mist API Notes

The current Mist backend expects numeric period enum values. Use the aliases
above in Skill calls; scripts convert them automatically.
