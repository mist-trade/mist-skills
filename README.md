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

Agent skills for Mist: market-data queries, Chan Theory analysis, technical indicators, and strategy alert consumption for LLM agents (e.g. Codex, Claude) and chat bots (AstrBot / QQ / WeChat).

> See [README.zh-CN.md](./README.zh-CN.md) for Chinese.

---

## 🌟 Core Features

- **Four canonical AI Skills**:
  - `chan-theory`: merged K, fractal, wide Bi, Duan & Zhongshu interpretation.
  - `technical-indicators`: MACD / KDJ / RSI status & multi-period analysis.
  - `data-query`: symbol quotes, index listing, and historical/intraday K-line aligned fill.
  - `strategy-alerts`: consume undelivered alerts and write back status.
- **Pure standard client access**: all scripts call Mist Backend REST APIs (`/v1/*`) only, never the TDX/QMT hardware datasources — clean layer separation.
- **Period alias auto-mapping**: human-friendly aliases (`5min`, `daily`, `1d`, `30m`, …) are automatically mapped to backend numeric enums.
- **AstrBot-native**: mount directly into the AstrBot plugin directory to power an in-group quant research assistant.

---

## 🏛️ Data Chain & Interaction

```text
┌─────────────────────────────────────────────────────────────┐
│               LLM Agent / Chatbot (AstrBot)                 │
│       "Analyze 600519 Moutai daily Chan Zhongshu & MACD"    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────▼──────────────┐
                │      Mist Skills Tool Layer │
                │ (Python 3.12 / Shared Lib)  │
                └──────────────┬──────────────┘
                               │ REST HTTP requests
                ┌──────────────▼──────────────┐
                │    Mist Backend (:8001)     │
                │  (or Nginx Gateway          │
                │   /api/mist)                │
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
# Point to Mist backend API (local or production gateway)
export MIST_API_BASE_URL=http://127.0.0.1:8001
export MIST_API_TIMEOUT=30
export MIST_DEFAULT_SOURCE=tdx
```

### 3. Run a skill script

```bash
# List market indices
uv run python skills/data-query/scripts/list_indices.py

# Query historical daily K-lines for a symbol
uv run python skills/data-query/scripts/get_daily_kline.py \
  --code 600519.SH --name "Kweichow Moutai" \
  --start-date 2026-08-01 --end-date 2026-08-25

# Run Chan Theory structure analysis
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
MIST_API_BASE_URL=http://<gateway>/api/mist
MIST_API_TIMEOUT=30
MIST_DEFAULT_SOURCE=tdx
```

See [RUNBOOK.md](./RUNBOOK.md) for mount & on-device testing details.

---

## 📂 Skill Module Index

- [Skills catalog (skills)](./skills/README.md)
- [Shared client lib (shared)](./shared/)

---

## 📄 License

Licensed under [BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause).
