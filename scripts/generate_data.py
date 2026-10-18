"""Generate a validated public/data.json snapshot from Opinet."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from scripts.fetch_opinet import normalize_station, search_nearby, station_detail
from scripts.station_data import haversine_km, sort_stations, validate_station_records


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def build_snapshot(args: argparse.Namespace) -> dict:
    raw_stations = search_nearby(args.anchor_latitude, args.anchor_longitude, args.radius_m, args.fuel_product)
    if not raw_stations:
        raise RuntimeError("Opinet returned no nearby stations; refusing to publish an empty snapshot")
    stations: list[dict] = []
    failures: list[dict] = []
    for raw in raw_stations:
        station_id = str(raw.get("UNI_ID") or "")
        try:
            item = normalize_station(raw, station_detail(station_id), args.fuel_product)
            item["distance_km"] = round(haversine_km(
                args.anchor_latitude, args.anchor_longitude,
                item["latitude"], item["longitude"],
            ), 2)
            stations.append(item)
        except Exception as exc:
            failures.append({"id": station_id, "reason": str(exc)})
    if failures and not args.allow_partial:
        raise RuntimeError(f"station detail failures: {len(failures)}; rerun with --allow-partial only when intentional")
    validation_errors = validate_station_records(stations)
    if validation_errors:
        raise RuntimeError("invalid normalized station data: " + "; ".join(validation_errors))
    stations = sort_stations(stations)
    for rank, station in enumerate(stations, 1):
        station["rank"] = rank
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "source": "Opinet",
        "region": {"code": args.region, "name": "의정부시"},
        "fuel": {"product_code": args.fuel_product, "name": "보통휘발유", "unit": "KRW/L"},
        "anchor": {
            "name": args.anchor_name,
            "address": args.anchor_address,
            "latitude": args.anchor_latitude,
            "longitude": args.anchor_longitude,
            "coordinate_source": "Nominatim address search; road-address result",
        },
        "stations": stations,
        "metadata": {
            "radius_m": args.radius_m,
            "candidate_count": len(raw_stations),
            "success_count": len(stations),
            "failure_count": len(failures),
            "failures": failures,
            "partial": bool(failures),
            "fetched_at": now_iso(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="public/data.json")
    parser.add_argument("--region", default="0203")
    parser.add_argument("--fuel-product", default="B027")
    parser.add_argument("--anchor-name", default="롯데슈퍼프레시 신곡점")
    parser.add_argument("--anchor-address", default="경기 의정부시 동일로 583")
    parser.add_argument("--anchor-latitude", type=float, default=37.7343555)
    parser.add_argument("--anchor-longitude", type=float, default=127.0582703)
    parser.add_argument("--radius-m", type=int, default=5000)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    snapshot = build_snapshot(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"candidates={snapshot['metadata']['candidate_count']} success={snapshot['metadata']['success_count']} failures={snapshot['metadata']['failure_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
