---
name: chan-theory
description: Chan Theory analysis for A-shares. Merge K-lines by containment, identify strokes (bi), fractals (fenxing), and channels. Supports step-by-step or combined full analysis pipeline.
---

# Chan Theory (缠论) Analysis

Analyze market data using Chan Theory (缠论) via the mist backend.

## Analysis Pipeline

Chan Theory analysis follows a sequential pipeline:

```
merge_k → create_bi → get_fenxing → channel
```

1. **merge_k**: Merge raw K-lines by containment relationship
2. **create_bi**: Identify strokes (笔) from merged K-lines
3. **get_fenxing**: Find fractals (分型) — top/bottom turning points
4. **channel**: Build channels and identify consolidation zones (中枢)

## Available Scripts

### merge_k
Merge K-lines based on containment relationships.
```bash
python scripts/merge_k.py --code 000001.SH --period daily --start-date "2026-01-01" --end-date "2026-04-13"
```
Returns: Array of merged K-line groups with `{startTime, endTime, highest, lowest, trend, mergedCount}`.

### create_bi
Identify strokes (笔) from K-line data.
```bash
python scripts/create_bi.py --code 000001.SH --period daily --start-date "2026-01-01" --end-date "2026-04-13"
```
Returns: Bi (stroke) data derived from merged K-lines.

### get_fenxing
Identify fractals (分型) — top and bottom turning points.
```bash
python scripts/get_fenxing.py --code 000001.SH --period daily --start-date "2026-01-01" --end-date "2026-04-13"
```
Returns: Fenxing data marking potential reversal points.

### analyze_chan
Full Chan Theory analysis in one call. Runs the complete pipeline: merge → bi → fenxing → channel.
```bash
python scripts/analyze_chan.py --code 000001.SH --period daily --start-date "2026-01-01" --end-date "2026-04-13"
```
Returns: Channel data with consolidation zones.

## Common Parameters

All chan-theory scripts accept:
- `--code` (required): Security code, e.g. `000001.SH`
- `--period` (required): Time period — `1min`, `5min`, `15min`, `30min`, `60min`, `daily` (converted to Mist numeric period values before request)
- `--start-date` (required): Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `--end-date` (required): End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
- `--source` (optional): Data source — `ef`, `tdx`, `mqmt`

## Step-by-Step vs Combined

Use `analyze_chan` for a quick overview. Use individual scripts when you need to inspect intermediate results (e.g., examine merged K-lines before running bi analysis).

## AstrBot Intent Examples

- "贵州茅台做一下缠论分析" → run `analyze_chan --code 600519.SH --period daily`
- "贵州茅台合并 K 线" → run `merge_k --code 600519.SH --period daily`
- "600519 找一下分型" → run `get_fenxing --code 600519.SH --period daily`

Defaults and guardrails:
- Use `daily` when the user does not specify a period.
- Use `tdx` unless the user asks for another source.
- Prefer a broad enough date range for Chan Theory structure detection.
- Empty `analyze_chan` results mean no channel was identified for that window; this is not an API error.

## Mist API Notes

The current Mist backend expects numeric period enum values. Use the aliases
above in Skill calls; scripts convert them automatically.
