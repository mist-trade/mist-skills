# Mist Skills

Mist Skills 为 Codex/Agent/AstrBot 提供缠论、技术指标、行情查询和策略告警消费能力。
所有脚本只调用 Mist backend `/v1/*`，不直连 TDX/QMT datasource，也不执行 native
provider raw API。

## Skills

| Skill | 用途 |
|---|---|
| `chan-theory` | merge K、笔、分型、中枢分析 |
| `technical-indicators` | MACD、KDJ、RSI |
| `data-query` | 证券、指数与 K 线查询/补齐 |
| `strategy-alerts` | 消费 backend strategy alert event 并回写投递结果（仅 `SKILL.md`，实现位于 `shared/strategy_alerts.py`，无独立脚本） |

## 安装

仓库由 `uv` 管理（见 `uv.lock`，CI 使用 `uv sync --frozen --extra dev`）：

```bash
uv sync --frozen --extra dev
```

运行脚本与工具时使用 `uv run ...`（与 `.github/workflows/ci.yml` 一致）。

## 配置

| 变量 | 默认值 | 说明 |
|---|---|---|
| `MIST_API_BASE_URL` | `http://127.0.0.1:8001` | Mist backend base URL |
| `MIST_API_TIMEOUT` | `30` | 请求超时秒数 |
| `MIST_DEFAULT_SOURCE` | `tdx` | 需要补数据时的默认 source |

生产环境优先通过同源 gateway：

```bash
export MIST_API_BASE_URL=http://www.moyui.mist/api/mist
```

如果调用环境不能解析该主机名，可临时使用
`http://<windows-lan-ip>/api/mist`。只有同机诊断才直接使用 `:8001`。

Backend period 使用数字 enum（`1`、`5`、`15`、`30`、`60`、`1440`）；Skills
保留 `5min`、`daily` 等用户别名，并在请求前转换。

## 测试

```bash
uv run pytest
uv run python skills/data-query/scripts/list_indices.py
uv run python skills/data-query/scripts/get_daily_kline.py \
  --code 600519.SH --name 贵州茅台 \
  --start-date 2026-06-21 --end-date 2026-06-28
```

新证券先运行 data-query 补齐 K 线，再执行指标或缠论。空数组表示当前窗口无结果，
不等同于脚本异常。

## AstrBot

把 `skills/` 安装到 `/AstrBot/data/skills/`，把 `shared/` 放到
`/AstrBot/data/shared/`，并设置：

```bash
PYTHONPATH=/AstrBot/data
MIST_API_BASE_URL=http://www.moyui.mist/api/mist
MIST_API_TIMEOUT=30
MIST_DEFAULT_SOURCE=tdx
```

策略告警只使用 `/v1/strategy-alert-events`。Skills 不计算策略规则、不轮询
datasource、不直接保存行情。容器实测步骤见 [RUNBOOK.md](RUNBOOK.md)。
