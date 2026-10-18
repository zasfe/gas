from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_TOP = {"schema_version", "generated_at", "source", "region", "fuel", "anchor", "stations", "metadata"}
REQUIRED_STATION = {"id", "name", "address", "latitude", "longitude", "price", "distance_km", "rank"}


def validate(path: str) -> list[str]:
    errors: list[str] = []
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors.extend(f"missing top-level field: {field}" for field in sorted(REQUIRED_TOP - data.keys()))
    stations = data.get("stations", [])
    if not isinstance(stations, list):
        return errors + ["stations must be a list"]
    for index, station in enumerate(stations):
        errors.extend(f"station[{index}] missing field: {field}" for field in sorted(REQUIRED_STATION - station.keys()))
        if station.get("price", 1) <= 0:
            errors.append(f"station[{index}] price must be positive")
    return errors


if __name__ == "__main__":
    problems = validate(sys.argv[1] if len(sys.argv) > 1 else "public/data.json")
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("data.json valid")
