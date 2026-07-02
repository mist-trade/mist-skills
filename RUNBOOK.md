# AstrBot Mist Skills Runbook

This runbook verifies the deployed AstrBot container can execute `mist-skills`
against the live Mist backend.

## Runtime Contract

- AstrBot data mount: `/Users/moyui/sean/napcat-astrbot/data` -> `/AstrBot/data`
- Active skills: `data-query`, `technical-indicators`, `chan-theory`
- Python import path: `PYTHONPATH=/AstrBot/data`
- Backend URL: `MIST_API_BASE_URL=http://192.168.31.182:8001`
- Default source: `MIST_DEFAULT_SOURCE=tdx`

## Container Smoke

Run from the Docker host:

```bash
docker exec astrbot sh -lc 'PYTHONPATH=/AstrBot/data python /AstrBot/data/skills/data-query/scripts/list_indices.py'
```

Expected: JSON array of securities, including `600519`.

```bash
docker exec astrbot sh -lc 'PYTHONPATH=/AstrBot/data python /AstrBot/data/skills/data-query/scripts/get_daily_kline.py --code 600519.SH --name "贵州茅台" --start-date 2026-06-21 --end-date 2026-06-28 --source tdx'
```

Expected: non-empty JSON array of daily K-lines.

```bash
docker exec astrbot sh -lc 'PYTHONPATH=/AstrBot/data python /AstrBot/data/skills/technical-indicators/scripts/macd.py --code 600519.SH --period daily --start-date 2026-01-01 --end-date 2026-06-28 --source tdx'
```

Expected: non-empty JSON array with non-null `macd` values after the warm-up
period.

```bash
docker exec astrbot sh -lc 'PYTHONPATH=/AstrBot/data python /AstrBot/data/skills/chan-theory/scripts/merge_k.py --code 600519.SH --period daily --start-date 2026-01-01 --end-date 2026-06-28 --source tdx'
```

Expected: non-empty JSON array of merged K-line groups. `analyze_chan.py` may
return an empty array when the selected window does not produce a channel.

## Debug Order

1. Check `docker ps` confirms `astrbot` is running.
2. Check `docker exec astrbot env | grep -E 'MIST_|PYTHONPATH'`.
3. Check `GET $MIST_API_BASE_URL/app/hello`.
4. Run `list_indices.py`.
5. Run a K-line script before indicator or Chan Theory scripts for new symbols.
6. For `Index information not found`, confirm the security exists and scripts
   are sending backend codes without exchange suffixes.
