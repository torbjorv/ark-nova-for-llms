#!/usr/bin/env python3
"""Extract Ark Nova card metadata from ssimeonoff/ssimeonoff.github.io ark-nova.html.

Source: https://raw.githubusercontent.com/ssimeonoff/ssimeonoff.github.io/master/ark-nova.html

That page encodes every card's metadata as tokens in the `class` attribute of an
`<li>` element, with the card number and name in inner `<div>`s. It does NOT
contain card text, numeric values (appeal / conservation points / money cost /
strength / reputation cost), or cost structure — only structural flags. This
script extracts what IS there; text and numerics can be backfilled from another
source later.

Usage:
    python3 scripts/extract_ssimeonoff.py path/to/ark-nova.html > cards.jsonl

There is also a `--discover` flag that dumps all unique class tokens (grouped by
card type) so a human can categorise them before they land in cards.jsonl.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


LAYOUT_TOKEN_RE = re.compile(r"^(cards\d+|filterDiv|r\d+|c\d+)$")

CARD_RE = re.compile(
    r'<li\s+onclick="getClickedCard\(\);"\s+class="([^"]+)"[^>]*>\s*'
    r'<div class="number">#(\d+)</div>\s*'
    r'<div class="name">([^<]+)</div>',
    re.DOTALL,
)

# Section markers (HTML comments) and marine-worlds sub-section marker
SECTION_RE = re.compile(
    r"<!--\s*(ANIMALS|SPONSORS|STANDARD PROJECTS|CARDS3|Endgame CARDS)\s*-->",
    re.IGNORECASE,
)
MARINE_RE = re.compile(r"<!--\s*Marine Worlds\s*-->", re.IGNORECASE)

TYPE_TOKENS = {
    "animal": "animal",
    "sponsor": "sponsor",
    "project": "conservation-project",
    "endgame": "final-scoring",
}

CONTINENT_TOKENS = {
    "africa": "africa",
    "america": "americas",
    "asia": "asia",
    "europe": "europe",
    "australia": "australia",
}

# Habitat / terrain group tokens. Treated as biomes in the output schema because
# they describe where the animal lives / what enclosure it needs.
BIOME_TOKENS = {
    "rock": "rock",
    "water": "water",
    "marine": "marine",
}

SIZE_TOKENS = {f"size{i}": i for i in range(1, 6)}

# "base" appears on standard-project cards and means base-set. Handled via the
# set logic, not as an ability.
NON_ABILITY_TOKENS = {"base"} | TYPE_TOKENS.keys() | CONTINENT_TOKENS.keys() \
                    | BIOME_TOKENS.keys() | SIZE_TOKENS.keys()


def walk_markers(html: str):
    """Yield (pos, kind, payload) in document order for section / marine / card markers."""
    events = []
    for m in SECTION_RE.finditer(html):
        events.append((m.start(), "section", m.group(1).upper()))
    for m in MARINE_RE.finditer(html):
        events.append((m.start(), "marine", True))
    for m in CARD_RE.finditer(html):
        events.append((m.start(), "card", m))
    events.sort(key=lambda x: x[0])
    return events


def parse_card(match: re.Match, is_marine: bool) -> dict:
    class_str, number_str, name = match.groups()
    tokens = [t for t in class_str.split() if not LAYOUT_TOKEN_RE.match(t)]

    card_type = "other"
    continents: list[str] = []
    biomes: list[str] = []
    size = None
    abilities: list[str] = []

    for t in tokens:
        if t in TYPE_TOKENS:
            card_type = TYPE_TOKENS[t]
        elif t in CONTINENT_TOKENS:
            continents.append(CONTINENT_TOKENS[t])
        elif t in BIOME_TOKENS:
            biomes.append(BIOME_TOKENS[t])
        elif t in SIZE_TOKENS:
            size = SIZE_TOKENS[t]
        elif t == "base":
            pass  # set marker, handled separately
        else:
            abilities.append(t)

    card_set = "marine-worlds" if is_marine else "base"
    prefix = "MW" if card_set == "marine-worlds" else "AN"
    card_id = f"{prefix}-{number_str.zfill(3)}"

    return {
        "id": card_id,
        "name": name.strip(),
        "set": card_set,
        "type": card_type,
        "biomes": sorted(set(biomes)),
        "continents": sorted(set(continents)),
        "size": size,
        "abilities": sorted(set(abilities)),
        "requires": [],
        "provides": [],
        "triggers": [],
        "appeal": None,
        "conservation_points": None,
        "strength": None,
        "reputation_requirement": None,
        "reputation_reward": None,
        "money_cost": None,
        "text": "",
        "notes": f"Imported from ssimeonoff ark-nova.html (source #{number_str}). "
                 "Numeric values and card text pending.",
    }


def extract(html: str) -> list[dict]:
    cards: list[dict] = []
    current_section = None
    is_marine = False
    for _pos, kind, payload in walk_markers(html):
        if kind == "section":
            current_section = payload
            is_marine = False
        elif kind == "marine":
            is_marine = True
        elif kind == "card":
            cards.append(parse_card(payload, is_marine))
    return cards


def discover(html: str) -> str:
    by_type: dict[str, Counter] = defaultdict(Counter)
    total = 0
    for m in CARD_RE.finditer(html):
        class_str = m.group(1)
        tokens = [t for t in class_str.split() if not LAYOUT_TOKEN_RE.match(t)]
        card_type = next((t for t in tokens if t in TYPE_TOKENS), "unknown")
        for t in tokens:
            if t == card_type:
                continue
            by_type[card_type][t] += 1
        total += 1
    lines = [f"== {total} cards parsed =="]
    for t, counter in sorted(by_type.items()):
        lines.append(
            f"\n-- type={t} ({sum(counter.values())} tokens, {len(counter)} unique) --"
        )
        for tok, c in sorted(counter.items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"  {c:4d}  {tok}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    ap.add_argument("--discover", action="store_true",
                    help="Dump unique class tokens by card type instead of JSONL.")
    args = ap.parse_args()

    html = args.html.read_text()
    if args.discover:
        print(discover(html))
        return 0

    cards = extract(html)
    for c in cards:
        print(json.dumps(c, ensure_ascii=False))
    print(f"# extracted {len(cards)} cards", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
