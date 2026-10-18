import json
from pathlib import Path

from scripts.validate_data import validate


def test_example_data_matches_contract(tmp_path):
    payload = {
        "schema_version": 1, "generated_at": "now", "source": "Opinet",
        "region": {}, "fuel": {}, "anchor": {}, "stations": [], "metadata": {}
    }
    path = tmp_path / "data.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert validate(str(path)) == []
