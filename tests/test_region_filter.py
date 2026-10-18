from scripts.fetch_opinet import is_station_in_region


def test_station_region_filter_uses_siguncd():
    assert is_station_in_region({"SIGUNCD": "0203"}, "0203")
    assert not is_station_in_region({"SIGUNCD": "0204"}, "0203")
