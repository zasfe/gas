from scripts.fetch_opinet import deduplicate_stations, region_grid_points


def test_region_grid_covers_bbox_with_overlap():
    points = region_grid_points(37.68, 37.78, 127.00, 127.15, 0.05, 0.07)
    assert len(points) == 9
    assert (37.68, 127.00) in points
    assert (37.73, 127.14) in points


def test_deduplicate_stations_by_opinet_id():
    records = [{"UNI_ID": "A", "DISTANCE": 10}, {"UNI_ID": "A", "DISTANCE": 20}, {"UNI_ID": "B"}]
    assert [r["UNI_ID"] for r in deduplicate_stations(records)] == ["A", "B"]
