import os


def get_base_url() -> str:
    return os.environ.get("MIST_API_BASE_URL", "http://127.0.0.1:8001")


def get_timeout() -> int:
    return int(os.environ.get("MIST_API_TIMEOUT", "30"))
