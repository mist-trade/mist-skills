# Mist Skills — 架构与开发认知 (AGENTS.md)

> 本文件是 `mist-skills` 仓库（Python 3.12 + AstrBot 技能集）的项目级开发守则与接口规约。
> 工作区总览见根目录 `../AGENTS.md`。

---

## 一、定位与架构分层边界（刚性红线）

- **纯标准客户端定位**：`mist-skills` 是大语言模型（LLM Agent、Codex、Claude）与智能聊天机器人（AstrBot、微信/QQ 机器人）的技能插件集。
- **严禁直连底层数据源与存储**：
  - 必须**100% 通过 HTTP REST 请求访问 Mist Backend（默认端口 8001）**；
  - **严禁**直接连接底层硬件数据源端口（9001/9002）；
  - **严禁**直接连接底层 MySQL 或 Redis 数据库；
  - **严禁**在技能代码中引入 `pytdx`、`xtquant` 等硬件驱动库。
- **严禁在技能内执行策略推演或买卖点运算**：
  - 核心缠论几何与买卖点必须由后端的纯数学算法库 `@app/chancore` 与 `StrategyEvaluationKernel` 计算；
  - 严禁在 Python 侧手写伪策略循环或私自发明买卖点规则。

---

## 二、数据源标识与合法枚举

- **数据源命名契约**：系统已全面收敛数据源标识，合法源严格为：
  - `tdx`：通达信高速快照与日线源；
  - `qmt`：迅投 QMT 原生极速行情源；
  - `ef`：历史日线备用数据源。
- **废弃别名清理**：历史遗留别名 `mqmt` 已彻底退役废弃，**严禁再次引入 `mqmt` 或在 Python 侧进行静默重映射**，传给后端必须统一为 `qmt`。

---

## 三、后端通信与统一 Envelope 契约

客户端通信核心统一沉淀在 `shared/mist_client.py`：

1. **响应异常双轨分类**：
   - **`MistApiError`**：后端返回合法 Envelope 但业务报错（包含明确的错误代码 `code`、错误信息 `message` 及诊断用 `http_status`）；
   - **`MistApiContractError`**：后端响应无法被解析为标准统一 Envelope 时的契约破坏异常（缺少必要字段、数据格式错位或非 JSON 体）。
2. **后端端点映射标准**：
   - 指标族端点：`/v1/indicators/{name}`（例如 `/v1/indicators/k`, `/v1/indicators/macd`, `/v1/indicators/kdj`, `/v1/indicators/rsi`）；
   - 缠论几何端点：`/v1/chan/{name}`（`/v1/chan/merge-k`, `/v1/chan/bi`, `/v1/chan/fenxing`, `/v1/chan/channel`）；
   - 证券元数据与自愈补采：`/v1/securities`, `/v1/security-sources`, `/v1/collector/collect`；
   - 告警消费与回写：`/v1/strategy-alert-events`。

---

## 四、四大核心技能职责与边界

| 技能名称 | 职责边界 | 交互规范 |
| :--- | :--- | :--- |
| **`data-query`** | 标的行情查询、指数列表与历史/当日 K 线自动对齐补齐。 | 缺失数据时通过后端标准端点触发自动采集与入库，避免向上层暴露脏数据。 |
| **`technical-indicators`** | 基于后端 Rust Polars SIMD 引擎的工业级技术指标状态诊断。 | 接收后端双轨输出的指标切片，支持金叉死叉与超买超卖自然语言解盘。 |
| **`chan-theory`** | 缠论形态诊断：K 线包含合并、顶底分型、笔结构、特征序列线段与中枢识别。 | 仅展示与解释后端返回的几何图元，不私设主观形态。 |
| **`strategy-alerts`** | 策略告警消费：消费后端未决的 `StrategyAlertEvent` 并自动回写投递状态。 | 仅负责事件消费与投递成功/失败回写，严禁在此触发策略计算。 |

---

## 五、与后端 Notification 体系的协同准则

1. **职责分离**：
   - 后端 `apps/notification` 专职负责实盘环境下企业微信、飞书等自动化 Webhook 的矩阵投递与严格频控（过滤与去抖）；
   - `mist-skills` 中的 AstrBot 属于**交互式外围机器人终端**。
2. **告警消费闭环**：
   - 流程：调用 `list_pending_strategy_alerts()`（`GET /v1/strategy-alert-events?status=pending`）拉取事件 $\to$ 机器人发送消息 $\to$ 成功调用 `mark_strategy_alert_delivered(id)` 或失败调用 `mark_strategy_alert_failed(id)`；
   - 操作员在 Web UI 上的确认（`acknowledged`）属独立操作，不得由机器人代劳。

---

## 六、开源合规与私密策略隔离

1. **严禁泄漏私有策略资产**：`mist-skills` 为完全公开的开源仓库，严禁在任何 Skill 脚本或提示词中固化、引用或泄漏私有插件仓库 `mist-alpha-private` 的任何因子逻辑、参数配置或专有策略名称。
2. **防过拟合无偏准则**：指标与缠论分析脚本一律输出客观数学事实，严禁加入经验松弛因子。
