"""Opinet API client used only by GitHub Actions."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any

from scripts.station_data import convert_katec_to_wgs84

BASE_URL = "https://www.opinet.co.kr/api"


def _request(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    query = {**params, "code": os.environ["OPINET_API_KEY"], "out": "json"}
    url = f"{BASE_URL}/{endpoint}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(url, headers={"User-Agent": "zasfe-gas/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError("Opinet response is not an object")
    return payload


def _records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    result = payload.get("RESULT", payload)
    if isinstance(result, dict):
        for value in result.values():
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                return value
            if isinstance(value, dict):
                nested = _records(value)
                if nested:
                    return nested
    return []


def wgs84_to_katec(latitude: float, longitude: float) -> tuple[float, float]:
    from pyproj import Transformer
    transformer = Transformer.from_crs(
        "EPSG:4326",
        "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 "
        "+ellps=bessel +towgs84=-145.907,505.034,685.756,-1.162,2.347,1.592,6.342 "
        "+units=m +no_defs",
        always_xy=True,
    )
    return transformer.transform(longitude, latitude)


def region_grid_points(
    south: float, north: float, west: float, east: float,
    latitude_step: float = 0.05, longitude_step: float = 0.07,
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    lat = south
    while lat <= north + 1e-9:
        lon = west
        while lon <= east + 1e-9:
            points.append((round(lat, 5), round(lon, 5)))
            lon += longitude_step
        lat += latitude_step
    return points


def deduplicate_stations(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for record in records:
        station_id = str(record.get("UNI_ID") or "")
        if station_id and station_id not in unique:
            unique[station_id] = record
    return list(unique.values())


def search_nearby(latitude: float, longitude: float, radius_m: int, product_code: str) -> list[dict[str, Any]]:
    x, y = wgs84_to_katec(latitude, longitude)
    payload = _request("aroundAll.do", {
        "x": round(x, 3), "y": round(y, 3), "radius": radius_m,
        "prodcd": product_code, "sort": 2,
    })
    return _records(payload)


def search_region(
    south: float, north: float, west: float, east: float,
    radius_m: int, product_code: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for latitude, longitude in region_grid_points(south, north, west, east):
        records.extend(search_nearby(latitude, longitude, radius_m, product_code))
    return deduplicate_stations(records)


def station_detail(station_id: str) -> dict[str, Any]:
    records = _records(_request("detailById.do", {"id": station_id}))
    if not records:
        raise ValueError(f"no detail returned for station {station_id}")
    return records[0]


def normalize_station(raw: dict[str, Any], detail: dict[str, Any], product_code: str) -> dict[str, Any]:
    products = detail.get("OIL_PRICE", [])
    if isinstance(products, dict):
        products = [products]
    price_row = next((row for row in products if row.get("PRODCD") == product_code), None)
    if price_row is None:
        raise ValueError(f"product {product_code} missing for {raw.get('UNI_ID')}")
    lat, lon = convert_katec_to_wgs84(detail["GIS_X_COOR"], detail["GIS_Y_COOR"])
    return {
        "id": str(raw.get("UNI_ID") or detail.get("UNI_ID")),
        "name": str(detail.get("OS_NM") or raw.get("OS_NM") or ""),
        "address": str(detail.get("NEW_ADR") or detail.get("VAN_ADR") or ""),
        "latitude": round(lat, 7),
        "longitude": round(lon, 7),
        "brand_code": detail.get("POLL_DIV_CD"),
        "price": int(float(price_row["PRICE"])),
        "trade_date": str(price_row.get("TRADE_DT") or ""),
        "trade_time": str(price_row.get("TRADE_TM") or ""),
        "distance_km": round(float(raw.get("DISTANCE", 0)) / 1000, 2),
    }
