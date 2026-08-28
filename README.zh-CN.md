<p align="right">
  <strong>中文</strong> | <a href="./README.md">English</a>
</p>

# Mist Skills AI 与智能机器人技能套件

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/AstrBot-Integration-ff69b4.svg" alt="AstrBot" />
  <img src="https://img.shields.io/badge/uv-Package_Manager-purple.svg" alt="uv" />
  <img src="https://img.shields.io/badge/License-BSD--3--Clause-green.svg" alt="License" />
</p>

Mist Skills 为大语言模型 Agent（如 OpenAI Codex、Claude 等）与智能聊天机器人（AstrBot、QQ/微信机器人）提供 A 股市场行情查询、缠论分析、技术指标计算与策略告警消费的标准化技能插件集。




---

## 🌟 核心特性

- **四大约定 AI Skills**：
  - `chan-theory`：K 线合并、顶底分型、宽笔、线段与中枢解盘。
  - `technical-indicators`：MACD、KDJ、RSI 等指标状态诊断与多周期分析。
  - `data-query`：标的行情查询、指数列表与历史/当日 K 线自动对齐补齐。
  - `strategy-alerts`：自动化消费未投递告警并回写状态。
- **纯标准客户端访问**：所有脚本严格调用 Mist Backend REST API（`/v1/*`），不直连 TDX/QMT 硬件数据源，保持清晰的架构分层。
- **周期别名自动转换**：智能支持人类自然语言别名（`5min`、`daily`、`1d`、`30m` 等）向后端标准数字枚举的自动映射。
- **AstrBot 插件原生兼容**：支持直接挂载至 AstrBot 插件目录，赋能聊天群内智能量化投研助手。

---

## 🏛️ 数据链路与交互

```text
┌─────────────────────────────────────────────────────────────┐
│               LLM Agent / 聊天机器人 (AstrBot)              │
│       "分析一下 600519 茅台的日线缠论中枢和 MACD 状态"       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────▼──────────────┐
                │      Mist Skills 工具层     │
                │ (Python 3.12 / Shared Lib)  │
                └──────────────┬──────────────┘
                               │ REST HTTP 请求
                ┌──────────────▼──────────────┐
                │    Mist Backend (:8001)     │
                │  (或 Nginx 网关 /api/mist)  │
                └─────────────────────────────┘
```

---

## 📋 环境与依赖要求

- **Python**：`>= 3.12`
- **包管理器**：`uv` (`uv sync --frozen --extra dev`)

---

## 🚀 快速上手 (本地运行)

### 1. 同步环境

```bash
uv sync --frozen --extra dev
```

### 2. 环境变量配置

```bash
# 指向 Mist 后端 API 地址 (本地或生产网关)
export MIST_API_BASE_URL=http://127.0.0.1:8001
export MIST_API_TIMEOUT=30
export MIST_DEFAULT_SOURCE=tdx
```

### 3. 执行单项技能脚本

```bash
# 查询大盘指数列表
uv run python skills/data-query/scripts/list_indices.py

# 查询指定个股历史日线
uv run python skills/data-query/scripts/get_daily_kline.py \
  --code 600519.SH --name 贵州茅台 \
  --start-date 2026-08-01 --end-date 2026-08-25

# 运行个股缠论形态分析
uv run python skills/chan-theory/scripts/analyze_chan.py \
  --code 600519.SH --period daily \
  --start-date 2026-08-01 --end-date 2026-08-25
```

---

## 🧪 测试与质量门禁

```bash
# 运行全部技能单元测试
uv run pytest

# 静态代码检查
uv run ruff check .
```

---

## 🤖 AstrBot 机器人部署

将 `skills/` 与 `shared/` 挂载到 AstrBot 容器数据路径中：

```bash
# 容器内环境变量配置
PYTHONPATH=/AstrBot/data
MIST_API_BASE_URL=http://www.mist.local/api/mist
MIST_API_TIMEOUT=30
MIST_DEFAULT_SOURCE=tdx
```

详细挂载与实机测试指南请参阅 [RUNBOOK.md](./RUNBOOK.md)。

---

## 📂 技能模块索引

- [技能目录与说明 (skills)](./skills/README.md)
- [公共客户端库 (shared)](./shared/)

---

## 📄 许可证

本项目遵循 [BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause) 开源许可证。
