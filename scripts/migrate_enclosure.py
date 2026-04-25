#!/usr/bin/env python3
"""Migrate cards.jsonl from the old enclosure_type/alt_* schema to per-enclosure-type size columns.

Drops:  enclosure_type, alt_enclosure_type, alt_enclosure_size
Adds:   standard_size, reptile_house_size, large_bird_aviary_size,
        petting_zoo_size, aquarium_size, large_reptile_house_size

`size` is preserved with refined semantics: scoring/category size only.
For land animals it equals `standard_size`; for sea animals it is the
parenthesised number on the card (distinct from `aquarium_size`).

Source of truth for parsing: source_data/arknovaanimals_VM_v2.xlsx
column "Enclosure size (Rock/Water)" — the original printed strings,
which include the Aq number that the current cards.jsonl lost for sea
turtles.

Writes cards.jsonl.new alongside cards.jsonl. Does NOT modify cards.jsonl.
Prints a per-animal verification report to stdout.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import openpyxl

REPO = Path(__file__).resolve().parent.parent

OLD_FIELDS = ("enclosure_type", "alt_enclosure_type", "alt_enclosure_size")

NEW_SIZE_FIELDS = (
    "standard_size",
    "reptile_house_size",
    "large_bird_aviary_size",
    "petting_zoo_size",
    "aquarium_size",
    "large_reptile_house_size",
)

# Canonical field order in the output JSONL — same as existing cards.jsonl,
# with the 3 old enclosure fields replaced in place by the 6 new size fields.
FIELD_ORDER = (
    "biomes", "continents", "size",
    "abilities", "requires", "provides", "triggers",
    "appeal", "conservation_points", "strength",
    "reputation_requirement", "reputation_reward", "money_cost",
    "text", "notes",
    *NEW_SIZE_FIELDS,
    "reef_ability", "wave_icon",
    "ability_levels", "ability_targets",
    "tier_thresholds", "tier_rewards",
    "id", "name", "set", "type",
)

PAREN_RE = re.compile(r"^\s*\((\d+)\)")
AQ_RE    = re.compile(r"\bAq\s+(\d+)")
LRH_RE   = re.compile(r"\bLRH\s+(\d+)")
RH_RE    = re.compile(r"(?<!L)\bRH\s+(\d+)")
LBA_RE   = re.compile(r"\bLBA\s+(\d+)")
PZ_RE    = re.compile(r"^\s*PZ\s+(\d+)")
STD_RE   = re.compile(r"^\s*(\d+)\s*[RW]*")


def card_num(card_id: str) -> int | None:
    try:
        return int(card_id.split("-", 1)[1])
    except (ValueError, IndexError, AttributeError):
        return None


def parse_enclosure(raw: str | None) -> dict:
    """Parse a printed enclosure string into the new size fields.

    Recognises:
      "PZ N"                         -> petting_zoo_size = N
      "(N)  Aq M [R]"                -> size = N, aquarium_size = M
      "(N)  Aq M / LRH P"            -> size = N, aquarium_size = M, large_reptile_house_size = P
      "N[RW]* / Aq M"                -> standard_size = N, aquarium_size = M  (penguin)
      "N[RW]* (RH M)"                -> standard_size = N, reptile_house_size = M
      "N (LBA M)"                    -> standard_size = N, large_bird_aviary_size = M
      "N[RW]*"                       -> standard_size = N

    Returns dict with `size` + the 6 new size fields, plus internal `_parsed: bool`.
    """
    out: dict = {f: None for f in NEW_SIZE_FIELDS}
    out["size"] = None
    out["_parsed"] = False

    if raw is None:
        return out
    s = str(raw).strip()
    if not s:
        return out

    if PZ_RE.match(s):
        n = int(PZ_RE.match(s).group(1))
        out["petting_zoo_size"] = n
        out["size"] = n
        out["_parsed"] = True
        return out

    if s.startswith("("):
        pm = PAREN_RE.match(s)
        if pm:
            out["size"] = int(pm.group(1))
        aq = AQ_RE.search(s)
        if aq:
            out["aquarium_size"] = int(aq.group(1))
        lrh = LRH_RE.search(s)
        if lrh:
            out["large_reptile_house_size"] = int(lrh.group(1))
        out["_parsed"] = pm is not None and aq is not None
        return out

    if "/" in s and AQ_RE.search(s):
        left, right = s.split("/", 1)
        sub = parse_enclosure(left.strip())
        for f in NEW_SIZE_FIELDS:
            if sub[f] is not None:
                out[f] = sub[f]
        out["size"] = sub["size"]
        aq = AQ_RE.search(right)
        if aq:
            out["aquarium_size"] = int(aq.group(1))
        out["_parsed"] = sub["_parsed"] and aq is not None
        return out

    rh = RH_RE.search(s)
    lba = LBA_RE.search(s)
    if rh:
        out["reptile_house_size"] = int(rh.group(1))
        head = s[: rh.start()]
    elif lba:
        out["large_bird_aviary_size"] = int(lba.group(1))
        head = s[: lba.start()]
    else:
        head = s
    head = head.rstrip(" (").strip()

    m = STD_RE.match(head)
    if m:
        n = int(m.group(1))
        out["standard_size"] = n
        out["size"] = n
        out["_parsed"] = True

    return out


def load_xlsx_enclosures(xlsx_path: Path) -> dict[int, str]:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb["Animals"]
    by_num: dict[int, str] = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        try:
            num = int(row[0])
        except (TypeError, ValueError):
            continue
        by_num[num] = "" if row[3] is None else str(row[3])
    return by_num


def transform(card: dict, xlsx_enclosures: dict[int, str]) -> tuple[dict, list[str], str]:
    """Return (new_card, warnings, xlsx_string_used)."""
    warnings: list[str] = []

    # Default new size fields to None (and drop old fields).
    new = {k: v for k, v in card.items() if k not in OLD_FIELDS}
    for f in NEW_SIZE_FIELDS:
        new[f] = None

    if card.get("type") != "animal":
        return new, warnings, ""

    num = card_num(card.get("id", ""))
    raw = xlsx_enclosures.get(num) if num is not None else None
    if raw is None:
        warnings.append(f"{card.get('id')}: not found in xlsx Animals sheet")
        return new, warnings, ""

    parsed = parse_enclosure(raw)
    if not parsed["_parsed"]:
        warnings.append(f"{card.get('id')}: enclosure string {raw!r} not parsed")
        return new, warnings, raw

    for f in NEW_SIZE_FIELDS:
        new[f] = parsed[f]

    if parsed["size"] is not None:
        new["size"] = parsed["size"]
    elif card.get("size") is not None:
        warnings.append(
            f"{card.get('id')}: parsed size is None but cards.jsonl had size={card.get('size')!r}"
        )

    if all(parsed[f] is None for f in NEW_SIZE_FIELDS):
        warnings.append(f"{card.get('id')}: animal has no enclosure size after parse ({raw!r})")

    return new, warnings, raw


def reorder(row: dict) -> dict:
    """Emit row in canonical FIELD_ORDER. Any unknown keys appended at the end."""
    out: dict = {}
    for k in FIELD_ORDER:
        if k in row:
            out[k] = row[k]
    for k in row:
        if k not in out:
            out[k] = row[k]
    return out


def fmt_old(card: dict) -> str:
    return (
        f"size={card.get('size')!r}, "
        f"enc={card.get('enclosure_type')!r}, "
        f"alt={card.get('alt_enclosure_type')!r}, "
        f"alt_size={card.get('alt_enclosure_size')!r}"
    )


def fmt_new(card: dict) -> str:
    parts = [f"size={card.get('size')}"]
    for f in NEW_SIZE_FIELDS:
        if card.get(f) is not None:
            parts.append(f"{f}={card[f]}")
    return ", ".join(parts)


def main() -> int:
    cards_path = REPO / "cards.jsonl"
    xlsx_path = REPO / "source_data" / "arknovaanimals_VM_v2.xlsx"
    out_path = REPO / "cards.jsonl.new"

    if not cards_path.exists():
        print(f"ERROR: {cards_path} not found", file=sys.stderr)
        return 2
    if not xlsx_path.exists():
        print(f"ERROR: {xlsx_path} not found", file=sys.stderr)
        return 2

    xlsx_enclosures = load_xlsx_enclosures(xlsx_path)

    rows: list[dict] = []
    with cards_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    new_rows: list[dict] = []
    all_warnings: list[str] = []
    animal_lines: list[str] = []

    for r in rows:
        new, warnings, raw = transform(r, xlsx_enclosures)
        all_warnings.extend(warnings)
        new_rows.append(reorder(new))

        if r.get("type") == "animal":
            animal_lines.append(
                f"  {r['id']:7} {r.get('name',''):35} "
                f"| xlsx={raw!r:32} "
                f"| OLD: {fmt_old(r)} "
                f"| NEW: {fmt_new(new)}"
            )

    with out_path.open("w") as f:
        for r in new_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote {len(new_rows)} rows to {out_path}\n")
    print("=== Per-animal transformation ===")
    for line in animal_lines:
        print(line)
    print()
    if all_warnings:
        print(f"=== Warnings ({len(all_warnings)}) ===")
        for w in all_warnings:
            print(f"  {w}")
        return 1
    print("No warnings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
