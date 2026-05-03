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
    "games": list,
    "type": str,
    "rock_icons": int,
    "water_icons": int,
    "icons": list,
    "size": (int, type(None)),
    "abilities": list,
    "requires": list,
    "triggers": list,
    "appeal": (int, type(None)),
    "conservation_points": (int, type(None)),
    "strength": (int, type(None)),
    "reputation_requirement": (int, type(None)),
    "bonus_reward": (str, type(None)),
    "money_cost": (int, type(None)),
    "text": str,
    "notes": (str, type(None)),
    "standard_size": (int, type(None)),
    "reptile_house_size": (int, type(None)),
    "large_bird_aviary_size": (int, type(None)),
    "petting_zoo_size": (int, type(None)),
    "aquarium_size": (int, type(None)),
    "reef_ability": (str, type(None)),
    "wave_icon": bool,
    "alternative_ability": (str, type(None)),
    "tier_thresholds": list,
    "tier_rewards": list,
}

# Abilities that take an integer level as `name:N` (1..5 in the printed deck).
LEVELED_ABILITIES = {
    "adapt", "digging", "flock", "glide", "hunter", "hypnosis", "jumping",
    "perception", "pilfering", "posturing", "pouch", "scavenging", "shark-attack",
    "snapping", "sprint", "sunbathing", "venom",
}

# Abilities that take a string target as `name:<target>`, with the allowed
# targets enumerated per ability.
TARGETED_ABILITIES = {
    "iconic": {"africa", "americas", "asia", "europe", "australia"},
    "boost": {"association", "sponsors", "cards", "build", "animals"},
    "action": {"association", "sponsors", "cards", "build"},
    "multiplier": {"association", "sponsors", "cards", "build"},
    "magnet": {"sponsors", "sea-animal"},
}

# `alternative_ability` is the smaller "alt-ability" box printed below the
# primary ability on certain animal cards. Closed vocabulary: the four known
# primary→alt mappings. Pilfering→Sprint and Venom→Inventive carry a level
# matching the primary (encoded `sprint:N` / `inventive:N`); Constriction→Clever
# and Hypnosis→Determination are unlevelled (bare name).
ALT_ABILITY_PATTERN = re.compile(r"^(?:(?:sprint|inventive):[1-9]|clever|determination)$")

GAMES_ENUM = {"base", "marine-worlds"}
TYPE_ENUM = {"animal", "sponsor", "conservation-project", "final-scoring"}
ICON_ENUM = {
    # 5 continents
    "africa", "americas", "asia", "europe", "australia",
    # 8 animal categories
    "bear", "bird", "herbivore", "petting-zoo", "predator", "primate", "reptile", "sea-animal",
    # 3 named icons (sponsor-granted)
    "rock", "water", "science",
}
TAG_LINE = re.compile(r"^\s*-\s+`([a-z0-9\-\+]+)`")


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

    if "games" in row and isinstance(row["games"], list):
        if not row["games"]:
            errors.append(f"{prefix}: `games` must be non-empty")
        if len(row["games"]) != len(set(row["games"])):
            errors.append(f"{prefix}: `games` has duplicates: {row['games']}")
        for s in row["games"]:
            if s not in GAMES_ENUM:
                errors.append(f"{prefix}: invalid `games` element `{s}`")
    if "type" in row and row["type"] not in TYPE_ENUM:
        errors.append(f"{prefix}: invalid `type` value `{row['type']}`")

    for f in ("rock_icons", "water_icons"):
        v = row.get(f)
        if isinstance(v, int) and v < 0:
            errors.append(f"{prefix}: `{f}` must be ≥ 0 (got {v})")
    for icon in row.get("icons", []) or []:
        if icon not in ICON_ENUM:
            errors.append(f"{prefix}: invalid icon `{icon}`")

    for tag_field in ("requires", "triggers"):
        for tag in row.get(tag_field, []) or []:
            if tag not in valid_tags:
                errors.append(f"{prefix}: `{tag_field}` tag `{tag}` not defined in ABILITIES.md")

    # `abilities` entries are `name` or `name:param`. The bare name must be in
    # ABILITIES.md. A `:param` is allowed only when the ability is leveled or
    # targeted; the param must match the contract for that ability.
    for entry in row.get("abilities", []) or []:
        if not isinstance(entry, str) or not entry:
            errors.append(f"{prefix}: `abilities` entry is not a non-empty string")
            continue
        name, sep, param = entry.partition(":")
        if name not in valid_tags:
            errors.append(f"{prefix}: `abilities` tag `{name}` not defined in ABILITIES.md")
            continue
        if not sep:
            if name in LEVELED_ABILITIES:
                errors.append(
                    f"{prefix}: `abilities` entry `{name}` is leveled and must be encoded as `{name}:N`"
                )
            elif name in TARGETED_ABILITIES:
                errors.append(
                    f"{prefix}: `abilities` entry `{name}` is targeted and must be encoded as `{name}:<target>`"
                )
            continue
        if name in LEVELED_ABILITIES:
            if not (param.isdigit() and 1 <= int(param) <= 9):
                errors.append(
                    f"{prefix}: `abilities` entry `{entry}` — leveled ability requires integer level"
                )
        elif name in TARGETED_ABILITIES:
            if param not in TARGETED_ABILITIES[name]:
                errors.append(
                    f"{prefix}: `abilities` entry `{entry}` — target `{param}` not in allowed set for `{name}`"
                )
        else:
            errors.append(
                f"{prefix}: `abilities` entry `{entry}` — `{name}` is not a leveled or targeted ability and must not carry `:param`"
            )

    alt = row.get("alternative_ability")
    if isinstance(alt, str):
        if not ALT_ABILITY_PATTERN.match(alt):
            errors.append(
                f"{prefix}: `alternative_ability` value `{alt}` is not in the closed vocabulary"
            )
        if row.get("type") != "animal":
            errors.append(
                f"{prefix}: `alternative_ability` is set on a non-animal card"
            )

    thr = row.get("tier_thresholds") or []
    rew = row.get("tier_rewards") or []
    if thr and rew and len(thr) != len(rew):
        errors.append(
            f"{prefix}: tier_thresholds ({len(thr)}) and tier_rewards ({len(rew)}) length mismatch"
        )
    for v in thr:
        if not isinstance(v, int):
            errors.append(f"{prefix}: tier_thresholds entry has wrong type ({type(v).__name__})")
    for v in rew:
        if not isinstance(v, str):
            errors.append(f"{prefix}: tier_rewards entry has wrong type ({type(v).__name__})")

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
