SUPPORTED_EXCHANGES = {"SH", "SZ"}


def split_exchange_suffix(code: str) -> tuple[str, str | None]:
    normalized = code.strip().upper()
    if "." not in normalized:
        return normalized, None

    base, exchange = normalized.rsplit(".", 1)
    if exchange in SUPPORTED_EXCHANGES and base:
        return base, exchange
    return normalized, None


def source_format_code(code: str) -> str:
    normalized = code.strip().upper()
    base, exchange = split_exchange_suffix(normalized)
    if exchange:
        return normalized
    if base.startswith("6"):
        return f"{base}.SH"
    if base.startswith(("0", "3")):
        return f"{base}.SZ"
    return normalized
