#!/usr/bin/env python3
"""Regenerate sets/*.txt from cards.jsonl.

Each set file lists the IDs of cards belonging to that set, one per line,
sorted by ID. Runs from repo root.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SETS_DIR = REPO / "sets"

# All sets the schema knows about — make sure every file exists even if empty.
KNOWN_SETS = {"base", "marine-worlds"}


def main() -> int:
    by_set: dict[str, list[str]] = defaultdict(list)
    with (REPO / "cards.jsonl").open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            by_set[row["set"]].append(row["id"])

    for s in KNOWN_SETS | set(by_set.keys()):
        ids = sorted(by_set.get(s, []))
        out = SETS_DIR / f"{s}.txt"
        out.write_text("\n".join(ids) + ("\n" if ids else ""))
        print(f"  {s}: {len(ids)} ids -> {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
