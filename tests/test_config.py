import os
from unittest.mock import patch


def test_default_config():
    """Config uses sensible defaults when no env vars set."""
    with patch.dict(os.environ, {}, clear=True):
        import importlib

        import shared.config as cfg

        importlib.reload(cfg)

        assert cfg.get_base_url() == "http://127.0.0.1:8001"
        assert cfg.get_timeout() == 30
        assert cfg.get_default_source() == "tdx"


def test_config_from_env():
    """Config reads from environment variables."""
    with patch.dict(
        os.environ,
        {
            "MIST_API_BASE_URL": "http://mist:9000",
            "MIST_API_TIMEOUT": "60",
            "MIST_DEFAULT_SOURCE": "ef",
        },
    ):
        import importlib

        import shared.config as cfg

        importlib.reload(cfg)

        assert cfg.get_base_url() == "http://mist:9000"
        assert cfg.get_timeout() == 60
        assert cfg.get_default_source() == "ef"
