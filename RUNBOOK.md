# AstrBot Mist Skills 验证手册

本文验证已部署 AstrBot 能否通过生产 gateway 调用 `mist-skills`。

## 运行契约

- Skills：`data-query`、`technical-indicators`、`chan-theory`、
  `strategy-alerts`。
- Python path：`PYTHONPATH=/AstrBot/data`。
- Backend：`MIST_API_BASE_URL=http://www.moyui.mist/api/mist`。
- 默认 source：`MIST_DEFAULT_SOURCE=tdx`。

容器如果不能解析 `www.moyui.mist`，先修复 Docker DNS/hosts；临时诊断可使用
`http://host.docker.internal/api/mist`，不要改成 datasource `:9001/:9002`。

## 容器 smoke

```bash
docker exec astrbot sh -lc \
  'PYTHONPATH=/AstrBot/data python /AstrBot/data/skills/data-query/scripts/list_indices.py'
```

预期：返回证券 JSON 数组。

```bash
docker exec astrbot sh -lc \
  'PYTHONPATH=/AstrBot/data python /AstrBot/data/skills/data-query/scripts/get_daily_kline.py --code 600519.SH --name "贵州茅台" --start-date 2026-06-21 --end-date 2026-06-28 --source tdx'
```

预期：返回非空日线数组。

```bash
docker exec astrbot sh -lc \
  'PYTHONPATH=/AstrBot/data python /AstrBot/data/skills/technical-indicators/scripts/macd.py --code 600519.SH --period daily --start-date 2026-01-01 --end-date 2026-06-28 --source tdx'
```

预期：warm-up 后存在非空 `macd`。

```bash
docker exec astrbot sh -lc \
  'PYTHONPATH=/AstrBot/data python /AstrBot/data/skills/chan-theory/scripts/merge_k.py --code 600519.SH --period daily --start-date 2026-01-01 --end-date 2026-06-28 --source tdx'
```

预期：返回合并 K；窗口不形成中枢时 `analyze_chan.py` 可以返回空数组。

## 排查顺序

1. `docker ps` 确认 `astrbot` 运行。
2. 检查 `MIST_*` 和 `PYTHONPATH`。
3. 请求 `$MIST_API_BASE_URL/app/hello`。
4. 运行 `list_indices.py`。
5. 新证券先运行 K 线脚本，再运行指标/缠论。
6. `Index information not found` 时检查证券是否存在及 code canonicalization。
7. 告警只使用 `/v1/strategy-alert-events`，不得调用 datasource 或 raw provider。
