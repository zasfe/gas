import math

from scripts.station_data import haversine_km, sort_stations, validate_station_records


def test_haversine_distance_is_in_kilometres():
    distance = haversine_km(37.5665, 126.9780, 37.5650, 126.9780)
    assert 0.16 < distance < 0.18


def test_sort_stations_uses_price_distance_then_name():
    stations = [
        {"name": "나", "price": 1700, "distance_km": 1.0},
        {"name": "다", "price": 1600, "distance_km": 2.0},
        {"name": "가", "price": 1600, "distance_km": 1.0},
    ]
    assert [s["name"] for s in sort_stations(stations)] == ["가", "다", "나"]


def test_validate_station_records_rejects_missing_price():
    errors = validate_station_records([{"id": "A", "name": "주유소"}])
    assert any("price" in error for error in errors)
