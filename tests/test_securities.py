from shared.securities import source_format_code, split_exchange_suffix


def test_split_exchange_suffix_for_tdx_symbol():
    assert split_exchange_suffix("600519.SH") == ("600519", "SH")


def test_source_format_code_infers_exchange_for_common_a_share_codes():
    assert source_format_code("600519") == "600519.SH"
    assert source_format_code("000001") == "000001.SZ"
    assert source_format_code("300750") == "300750.SZ"
