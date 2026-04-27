#!/usr/bin/env python3
"""Run a SQL query against cards.jsonl via in-memory SQLite.

Loads cards.jsonl into a single table named `cards`. Scalar fields become
typed columns; list/dict fields are stored as JSON text and can be queried
with SQLite's JSON1 functions (`json_each`, `json_extract`, ...).

Usage:
    python scripts/query.py "SELECT id, name FROM cards WHERE type = 'animal' LIMIT 3"
    python scripts/query.py - < query.sql
    echo "SELECT COUNT(*) AS n FROM cards" | python scripts/query.py -

Output is JSONL on stdout, one result row per line. Columns whose values
are JSON arrays/objects (e.g. `continents`, `ability_levels`) are emitted
as parsed JSON, not as escaped strings.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
JSONL_PATH = REPO / "cards.jsonl"

# Fields stored as JSON text in SQLite (lists / dicts in the source data).
JSON_FIELDS = {
    "continents",
    "categories",
    "abilities",
    "requires",
    "provides",
    "triggers",
    "ability_levels",
    "ability_targets",
    "tier_thresholds",
    "tier_rewards",
}


def load_db(jsonl_path: Path) -> sqlite3.Connection:
    rows: list[dict] = []
    with jsonl_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        raise SystemExit(f"No rows in {jsonl_path}")

    columns = list(rows[0].keys())
    conn = sqlite3.connect(":memory:")
    quoted = ", ".join(f'"{c}"' for c in columns)
    conn.execute(f"CREATE TABLE cards ({quoted})")

    placeholders = ",".join("?" for _ in columns)
    insert = f"INSERT INTO cards VALUES ({placeholders})"
    for row in rows:
        values = []
        for c in columns:
            v = row.get(c)
            if c in JSON_FIELDS or isinstance(v, (list, dict)):
                values.append(None if v is None else json.dumps(v, ensure_ascii=False))
            else:
                values.append(v)
        conn.execute(insert, values)
    conn.commit()
    return conn


def _maybe_parse_json(value):
    if isinstance(value, str) and value and value[0] in "[{":
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def run(sql: str, conn: sqlite3.Connection) -> int:
    cursor = conn.execute(sql)
    if cursor.description is None:
        return 0
    columns = [d[0] for d in cursor.description]
    count = 0
    for row in cursor:
        record = {c: _maybe_parse_json(v) for c, v in zip(columns, row)}
        sys.stdout.write(json.dumps(record, ensure_ascii=False))
        sys.stdout.write("\n")
        count += 1
    return count


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    sql = sys.stdin.read() if argv[1] == "-" else argv[1]
    if not sql.strip():
        print("Empty SQL.", file=sys.stderr)
        return 2
    conn = load_db(JSONL_PATH)
    try:
        run(sql, conn)
    except sqlite3.Error as e:
        print(f"SQL error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
