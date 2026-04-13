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
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MIST_API_BASE_URL` | `http://127.0.0.1:8001` | mist backend URL |
| `MIST_API_TIMEOUT` | `30` | Request timeout (seconds) |

## Testing

```bash
pytest
```

## Usage with AstrBot

Add this repository as a Skills source in your AstrBot configuration. AstrBot will discover and load the three Skills automatically.
