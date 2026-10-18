"""Pure data validation and normalization helpers for the Opinet snapshot."""
from __future__ import annotations

import math
from typing import Any


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def sort_stations(stations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(stations, key=lambda station: (
        station["price"], station["distance_km"], station["name"]
    ))


def validate_station_records(stations: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, station in enumerate(stations):
        for field in ("id", "name", "address", "latitude", "longitude", "price", "distance_km"):
            if field not in station or station[field] in (None, ""):
                errors.append(f"station[{index}] missing {field}")
        if "price" in station and (not isinstance(station["price"], (int, float)) or station["price"] <= 0):
            errors.append(f"station[{index}] invalid price")
    return errors


def convert_katec_to_wgs84(x: float, y: float) -> tuple[float, float]:
    """Convert Opinet KATEC X/Y through pyproj's documented KATEC definition."""
    try:
        from pyproj import Transformer
    except ImportError as exc:  # pragma: no cover - exercised in CI dependency setup
        raise RuntimeError("pyproj is required for KATEC coordinate conversion") from exc
    transformer = Transformer.from_crs(
        "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 "
        "+ellps=bessel +towgs84=-145.907,505.034,685.756,-1.162,2.347,1.592,6.342 "
        "+units=m +no_defs",
        "EPSG:4326",
        always_xy=True,
    )
    longitude, latitude = transformer.transform(float(x), float(y))
    return latitude, longitude
