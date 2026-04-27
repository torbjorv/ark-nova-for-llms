#!/usr/bin/env python3
"""Validate cards.jsonl against SCHEMA.md and ABILITIES.md.

Exits non-zero with human-readable errors on the first batch of failures found.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

REQUIRED_FIELDS = {
    "id": str,
    "name": str,
    "set": str,
    "type": str,
    "rock_icons": int,
    "water_icons": int,
    "continents": list,
    "categories": list,
    "size": (int, type(None)),
    "abilities": list,
    "requires": list,
    "provides": list,
    "triggers": list,
    "appeal": (int, type(None)),
    "conservation_points": (int, type(None)),
    "strength": (int, type(None)),
    "reputation_requirement": (int, type(None)),
    "reputation_reward": (int, type(None)),
    "money_cost": (int, type(None)),
    "text": str,
    "notes": (str, type(None)),
    "standard_size": (int, type(None)),
    "reptile_house_size": (int, type(None)),
    "large_bird_aviary_size": (int, type(None)),
    "petting_zoo_size": (int, type(None)),
    "aquarium_size": (int, type(None)),
    "large_reptile_house_size": (int, type(None)),
    "reef_ability": (str, type(None)),
    "wave_icon": bool,
    "ability_levels": dict,
    "ability_targets": dict,
    "tier_thresholds": list,
    "tier_rewards": list,
}

SET_ENUM = {"base", "marine-worlds"}
TYPE_ENUM = {"animal", "sponsor", "conservation-project", "final-scoring"}
CONTINENT_ENUM = {"africa", "americas", "asia", "europe", "australia"}
CATEGORY_ENUM = {"bear", "bird", "herbivore", "petting-zoo", "predator", "primate", "reptile", "sea-animal"}
TAG_LINE = re.compile(r"^\s*-\s+`([a-z0-9\-]+)`")


def load_tags(abilities_md: Path) -> set[str]:
    tags: set[str] = set()
    for line in abilities_md.read_text().splitlines():
        m = TAG_LINE.match(line)
        if m:
            tags.add(m.group(1))
    return tags


def check_row(row: dict, lineno: int, valid_tags: set[str]) -> list[str]:
    errors: list[str] = []
    prefix = f"line {lineno}"

    for field, expected in REQUIRED_FIELDS.items():
        if field not in row:
            errors.append(f"{prefix}: missing field `{field}`")
            continue
        value = row[field]
        if not isinstance(value, expected):
            errors.append(f"{prefix}: field `{field}` has wrong type ({type(value).__name__})")

    if "set" in row and row["set"] not in SET_ENUM:
        errors.append(f"{prefix}: invalid `set` value `{row['set']}`")
    if "type" in row and row["type"] not in TYPE_ENUM:
        errors.append(f"{prefix}: invalid `type` value `{row['type']}`")

    for f in ("rock_icons", "water_icons"):
        v = row.get(f)
        if isinstance(v, int) and v < 0:
            errors.append(f"{prefix}: `{f}` must be ≥ 0 (got {v})")
    for c in row.get("continents", []) or []:
        if c not in CONTINENT_ENUM:
            errors.append(f"{prefix}: invalid continent `{c}`")
    for c in row.get("categories", []) or []:
        if c not in CATEGORY_ENUM:
            errors.append(f"{prefix}: invalid category `{c}`")

    for tag_field in ("abilities", "requires", "provides", "triggers"):
        for tag in row.get(tag_field, []) or []:
            if tag not in valid_tags:
                errors.append(f"{prefix}: `{tag_field}` tag `{tag}` not defined in ABILITIES.md")

    abilities = row.get("abilities") or []
    for ab_field in ("ability_levels", "ability_targets"):
        m = row.get(ab_field) or {}
        if not isinstance(m, dict):
            continue
        for k, v in m.items():
            if k not in abilities:
                errors.append(
                    f"{prefix}: `{ab_field}` key `{k}` is not in `abilities`"
                )
            expected_type = int if ab_field == "ability_levels" else str
            if not isinstance(v, expected_type):
                errors.append(
                    f"{prefix}: `{ab_field}[{k}]` has wrong type ({type(v).__name__})"
                )

    thr = row.get("tier_thresholds") or []
    rew = row.get("tier_rewards") or []
    if thr and rew and len(thr) != len(rew):
        errors.append(
            f"{prefix}: tier_thresholds ({len(thr)}) and tier_rewards ({len(rew)}) length mismatch"
        )

    return errors


def main() -> int:
    cards_path = REPO / "cards.jsonl"
    abilities_path = REPO / "ABILITIES.md"

    if not abilities_path.exists():
        print("ERROR: ABILITIES.md not found", file=sys.stderr)
        return 2

    valid_tags = load_tags(abilities_path)
    if not valid_tags:
        print("WARNING: no tags found in ABILITIES.md", file=sys.stderr)

    if not cards_path.exists():
        print(f"ERROR: {cards_path} not found", file=sys.stderr)
        return 2

    errors: list[str] = []
    ids_seen: set[str] = set()
    rows = 0

    with cards_path.open() as f:
        for lineno, line in enumerate(f, start=1):
            if not line.strip():
                continue
            rows += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"line {lineno}: invalid JSON ({e.msg})")
                continue
            if not isinstance(row, dict):
                errors.append(f"line {lineno}: row is not a JSON object")
                continue

            row_id = row.get("id")
            if isinstance(row_id, str):
                if row_id in ids_seen:
                    errors.append(f"line {lineno}: duplicate id `{row_id}`")
                ids_seen.add(row_id)

            errors.extend(check_row(row, lineno, valid_tags))

    if errors:
        print(f"Validation failed ({len(errors)} errors across {rows} rows):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    print(f"OK: {rows} rows, {len(valid_tags)} known tags.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
