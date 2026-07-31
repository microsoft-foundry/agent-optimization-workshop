from __future__ import annotations
"""CSVs in data/ must validate against their schema."""
import csv
import json
from pathlib import Path

from conftest import REPO_ROOT, SPECS_DIR

try:
    from jsonschema import validate
except ImportError:  # pragma: no cover
    validate = None


CSVS = [
    ("flights.csv",     "flights.schema.json"),
    ("hotels.csv",      "hotels.schema.json"),
    ("car_rentals.csv", "car_rentals.schema.json"),
]


def test_data_csvs_match_schema():
    assert validate is not None, "jsonschema required — pip install -r requirements-dev.txt"
    for csv_name, schema_name in CSVS:
        with open(SPECS_DIR / "schemas" / schema_name) as f:
            schema = json.load(f)
        with open(REPO_ROOT / "data" / csv_name) as f:
            for i, row in enumerate(csv.DictReader(f), start=1):
                try:
                    validate(row, schema)
                except Exception as e:  # pragma: no cover — surface row number
                    raise AssertionError(f"{csv_name} row {i} failed schema: {e}")
