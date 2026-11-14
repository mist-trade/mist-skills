<p align="right">
  <a href="./README.zh-CN.md">中文</a> | <strong>English</strong>
</p>

# Mist Skills — AI & Agent Skills Suite

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/AstrBot-Integration-ff69b4.svg" alt="AstrBot" />
  <img src="https://img.shields.io/badge/uv-Package_Manager-purple.svg" alt="uv" />
  <img src="https://img.shields.io/badge/License-BSD--3--Clause-green.svg" alt="License" />
</p>

Agent skills suite for Mist: market-data queries, Chan Theory structural analysis, Rust SIMD technical indicators, and strategy alert consumption for LLM agents (Codex, Claude) and chat assistants (AstrBot / QQ / WeChat).

---

## 🌟 Core Features

- **Four Canonical AI Skills**:
  - `chan-theory`: Merged K containment, fractals (fenxing), wide Bi, feature sequence Duan, and Zhongshu structure analysis.
  - `technical-indicators`: Status diagnosis and multi-period analysis based on Rust Polars SIMD indicator calculations (MACD, KDJ, RSI).
  - `data-query`: Symbol quotes, index listing, and historical/intraday K-line auto-alignment & fill.
  - `strategy-alerts`: Automated consumption of pending `StrategyAlertEvent` records and delivery status reporting.
- **Pure Standard Client Access**: All scripts call Mist Backend REST APIs (`/v1/*`, port 8001) exclusively; never direct to TDX/QMT hardware datasources — maintaining clear architectural boundaries.
- **Period Alias Auto-Mapping**: Human-friendly aliases (`5min`, `daily`, `1d`, `30m`, …) are automatically mapped to backend numeric enums.
- **Synergy with Mist Notification Pipeline**:
  - Enterprise Webhooks (WeCom, Feishu, etc.) with strict rate limiting are handled by `apps/notification` within the core backend;
  - AstrBot functions as an external interactive chat assistant, querying pending alerts via `GET /v1/strategy-alert-events?status=pending` and writing back outcomes via `POST /v1/strategy-alert-events/:id/delivered` or `failed`.
- **AstrBot-Native**: Mount directly into the AstrBot plugin directory to power an in-group quantitative research assistant.

---

## 🏛️ Data Flow & Interaction

```text
┌─────────────────────────────────────────────────────────────┐
│               LLM Agent / Chatbot (AstrBot)                 │
│      "Analyze 600519 Moutai daily Chan Zhongshu & MACD"     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────▼──────────────┐
                │      Mist Skills Tool Layer │
                │ (Python 3.12 / Shared Lib)  │
                └──────────────┬──────────────┘
                               │ REST HTTP Requests
                ┌──────────────▼──────────────┐
                │     Mist Backend (:8001)    │
                │ /v1/indicators/*  /v1/chan/*│
                │ /v1/securities    /v1/alert │
                └─────────────────────────────┘
```

---

## 📋 Requirements

- **Python**: `>= 3.12`
- **Package manager**: `uv` (`uv sync --frozen --extra dev`)

---

## 🚀 Quick Start (Local Run)

### 1. Sync environment

```bash
uv sync --frozen --extra dev
```

### 2. Configure environment variables

```bash
# Point to Mist backend API (local or production)
export MIST_API_BASE_URL=http://127.0.0.1:8001
export MIST_API_TIMEOUT=30
export MIST_DEFAULT_SOURCE=tdx
```

### 3. Run a skill script

```bash
# List market indices
uv run python skills/data-query/scripts/list_indices.py

# Query historical daily K-lines for a symbol (source tdx or qmt)
uv run python skills/data-query/scripts/get_daily_kline.py \
  --code 600519.SH --name "Kweichow Moutai" \
  --start-date 2026-08-01 --end-date 2026-08-25 --source tdx

# Run Chan Theory structural analysis
uv run python skills/chan-theory/scripts/analyze_chan.py \
  --code 600519.SH --period daily \
  --start-date 2026-08-01 --end-date 2026-08-25
```

---

## 🧪 Testing & Quality Gates

```bash
# Run all skill unit tests
uv run pytest

# Static checks
uv run ruff check .
```

---

## 🤖 AstrBot Deployment

Mount `skills/` & `shared/` into the AstrBot container data path:

```bash
# In-container env
PYTHONPATH=/AstrBot/data
MIST_API_BASE_URL=http://<backend-host>:8001
MIST_API_TIMEOUT=30
MIST_DEFAULT_SOURCE=tdx
```

See [RUNBOOK.md](./RUNBOOK.md) for mounting and on-device verification details.

---

## 📂 Skill Module Index

- [Skills catalog (skills)](./skills/README.md)
- [Shared client lib (shared)](./shared/)

---

## 📄 License

Licensed under [BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause).
