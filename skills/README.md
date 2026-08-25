# skills — Mist AI 技能列表与调用速查

`skills` 目录包含了供大语言模型（Agent）与 AstrBot 调用的各项独立功能技能定义与执行脚本。

---

## 🎯 技能列表与职责

| 技能目录 | 职责与适用场景 |
| :--- | :--- |
| **`chan-theory`** | 缠论形态诊断：K 线合并、顶底分型、笔结构、特征序列线段与中枢识别。 |
| **`technical-indicators`** | 技术指标分析：MACD 金叉死叉、KDJ 超买超卖、RSI 强弱形态计算。 |
| **`data-query`** | 行情数据查询：查询股票/指数列表、拉取历史 K 线并自动补齐缺失数据。 |
| **`strategy-alerts`** | 策略告警消费：消费后端未决的 `StrategyAlertEvent` 并自动回写投递状态。 |

---

## 📂 核心公共库速查 (`../shared/`)

- `shared/mist_client.py`：Mist 后端统一 HTTP API 客户端封装。
- `shared/periods.py`：自然语言周期（如 `5min`, `daily`）与后端周期枚举转换器。
- `shared/kline_runner.py`：K 线数据拉取与前置补齐通用流程。

---

## 🛠️ 测试与验证

```bash
# 验证全部技能调用
uv run pytest
```

---

## 🔗 上下游边界

- **上游**：Agent 工具调度或 AstrBot 消息命令触发。
- **下游**：调用 Mist Backend `/v1/*` 端点。
