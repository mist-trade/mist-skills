# Review P3 Batch 3 Evidence: mist-skills

## Selected Review IDs

| Review ID | Classification | Files / Evidence | Verification |
|---|---|---|---|
| CODE_REVIEW L10 | already closed | `skills/data-query/scripts/get_index_info.py`, `tests/test_data_query.py` | Script uses `split_exchange_suffix`; test expects `/security/v1/000001` for `000001.SH`. |
| CODE_SMELL_REVIEW P4.4 | deferred | astrbot skill scripts | Template extraction deferred to the dedicated skills template pass. |
| CODE_SMELL_REVIEW M4.2 | already closed | `shared/api_contracts.py`, skill scripts | `SOURCE_HELP_TEXT` is shared by scripts that expose `--source`. |
| CODE_SMELL_REVIEW M4.3 | deferred | skill script help text | Full wording normalization deferred to template pass. |
| CODE_SMELL_REVIEW D4.1 | already closed | `tests/test_data_query.py`, `tests/test_mist_client.py` | The stale `import json` entries are absent. |

## Verification

- `UV_CACHE_DIR=.uv-cache uv run pytest tests/test_data_query.py tests/test_securities.py tests/test_repository_hygiene.py -q`
  passed: 14 tests.
- `UV_CACHE_DIR=.uv-cache uv run ruff check shared tests skills` passed.
- `UV_CACHE_DIR=.uv-cache uv run black --check shared tests skills` passed.
- `UV_CACHE_DIR=.uv-cache uv run pyright` passed with 0 errors.
