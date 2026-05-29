# schema_inference.py
import csv
import json
import io
from datetime import datetime
from typing import Any

SAMPLE_ROWS = 5

def infer_type(values: list[str | Any]) -> str:
    """Infer the most specific type that fits all non-empty values."""
    candidates = {"boolean", "integer", "float", "date", "string"}

    for raw in values:
        v = str(raw).strip() if raw is not None else ""
        if v == "":
            continue  # nulls don't constrain the type

        if "boolean" in candidates and v.lower() not in ("true", "false", "1", "0", "yes", "no"):
            candidates.discard("boolean")

        if "integer" in candidates:
            try:
                int(v)
            except ValueError:
                candidates.discard("integer")

        if "float" in candidates:
            try:
                float(v)
            except ValueError:
                candidates.discard("float")

        if "date" in candidates and not _is_date(v):
            candidates.discard("date")

    # return the most specific surviving type
    for t in ("boolean", "integer", "float", "date"):
        if t in candidates:
            return t
    return "string"


_DATE_FORMATS = (
    "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y",
    "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
)

def _is_date(value: str) -> bool:
    return any(
        _try_parse(value, fmt) for fmt in _DATE_FORMATS
    )

def _try_parse(value: str, fmt: str) -> bool:
    try:
        datetime.strptime(value, fmt)
        return True
    except ValueError:
        return False

def infer_csv_schema(raw: bytes) -> list[dict]:
    """Return [{column, type, nullable}] from up to SAMPLE_ROWS of a CSV."""
    text = raw.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))

    columns = reader.fieldnames or []
    buckets: dict[str, list[str]] = {col: [] for col in columns}
    nullable: dict[str, bool] = {col: False for col in columns}

    for i, row in enumerate(reader):
        if i >= SAMPLE_ROWS:
            break
        for col in columns:
            val = row.get(col, "")
            if val is None or str(val).strip() == "":
                nullable[col] = True
            else:
                buckets[col].append(val)

    return [
        {"column": col, "type": infer_type(buckets[col]), "nullable": nullable[col]}
        for col in columns
    ]

def infer_json_schema(raw: bytes) -> list[dict]:
    """Return [{column, type, nullable}] from an array-of-objects JSON file."""
    text = raw.decode("utf-8", errors="replace")
    data = json.loads(text)

    if not isinstance(data, list):
        raise ValueError("JSON schema inference requires an array-of-objects at the root")
    if not data:
        return []

    sample = data[:SAMPLE_ROWS]
    all_keys: list[str] = list(dict.fromkeys(k for obj in sample for k in obj))

    buckets: dict[str, list] = {k: [] for k in all_keys}
    nullable: dict[str, bool] = {k: False for k in all_keys}

    for obj in sample:
        for key in all_keys:
            val = obj.get(key)
            if val is None:
                nullable[key] = True
            else:
                buckets[key].append(val)

    return [
        {"column": key, "type": infer_type(buckets[key]), "nullable": nullable[key]}
        for key in all_keys
    ]
