# mist-skills

Anthropic Agent Skills for the mist stock analysis backend. Provides 3 Skills covering Chan Theory, technical indicators, and market data queries for A-shares.

## Skills

| Skill | Description | Scripts |
|-------|-------------|---------|
| `chan-theory` | Chan Theory analysis | merge_k, create_bi, get_fenxing, analyze_chan |
| `technical-indicators` | MACD, KDJ, RSI | macd, kdj, rsi |
| `data-query` | Market data retrieval | list_indices, get_index_info, get_kline_data, get_daily_kline |

## Setup

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MIST_API_BASE_URL` | `http://127.0.0.1:8001` | mist backend URL |
| `MIST_API_TIMEOUT` | `30` | Request timeout (seconds) |
| `MIST_DEFAULT_SOURCE` | `tdx` | Default source for scripts that can collect missing data |

For the current Windows Mist appliance used by AstrBot, set:

```bash
export MIST_API_BASE_URL=http://192.168.31.182:8001
```

If AstrBot runs in Docker Desktop and the Mist backend runs on the Docker host
instead, use `http://host.docker.internal:8001`.

## Mist API Compatibility

The current Mist backend expects numeric period enum values (`1`, `5`, `15`,
`30`, `60`, `1440`). These Skills keep user-facing aliases such as `5min` and
`daily`, then convert them before sending requests to Mist.

## Testing

```bash
pytest
```

For container-local AstrBot checks, see [RUNBOOK.md](RUNBOOK.md).

## Usage with AstrBot

Install the three directories under `skills/` into AstrBot's
`/AstrBot/data/skills/` directory. Also copy the repository `shared/` directory
to `/AstrBot/data/shared/`; the scripts import the shared Mist client and period
conversion helper from there.

For the previously deployed Docker Desktop AstrBot stack, make sure the AstrBot
container environment includes:

```bash
MIST_API_BASE_URL=http://192.168.31.182:8001
MIST_API_TIMEOUT=30
MIST_DEFAULT_SOURCE=tdx
```

Quick smoke check from the same Python environment:

```bash
python skills/data-query/scripts/list_indices.py
python skills/data-query/scripts/get_daily_kline.py --code 600519.SH --name "贵州茅台" --start-date "2026-06-21" --end-date "2026-06-28"
```

`get_daily_kline` can initialize a missing security, attach the default data
source, collect the requested window, and retry the query. The indicator and Chan
scripts still require K-line data to exist first, so run the data-query Skill
before indicator analysis for a brand-new symbol.

## First Bot Experience

Supported first-version intents:

- List available securities.
- Query daily or intraday K-line data for a known A-share code.
- Calculate MACD, KDJ, or RSI for a code and period.
- Run Chan Theory merge, bi, fenxing, or channel analysis for a code and period.

Defaults:

- `source`: `tdx`
- `period`: use the period requested by the user; if omitted, prefer `daily`
- date range: use the user's date range; for recent daily questions, a 30- to
  180-trading-day range gives indicators enough warm-up data

Guardrails:

- Ask for or infer a security code before calling scripts.
- Use `--name` when a script may need to initialize a new security.
- Reject overly broad requests that would require many symbols or unbounded
  history.
- Treat empty arrays as "no data/result for this window", not as script failure.
