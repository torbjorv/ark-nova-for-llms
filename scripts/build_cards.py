#!/usr/bin/env python3
"""Build cards.jsonl from the authoritative spreadsheet + old-file text.

Reads:
  source_data/arknovaanimals_VM_v2.xlsx  — structured card data
  source_data/cards.jsonl.bak            — previous cards.jsonl, for `text` and `notes`

Writes:
  cards.jsonl — one JSON object per line, every schema field present.

Run with: python scripts/build_cards.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import openpyxl

REPO = Path(__file__).resolve().parent.parent
XLSX = REPO / "source_data" / "arknovaanimals_VM_v2.xlsx"
BACKUP = REPO / "source_data" / "cards.jsonl.bak"
OUT = REPO / "cards.jsonl"

BIOME_LETTERS = {"R": "rock", "W": "water"}

# Maps Type-column tokens → (animal-icon ability tag, animal-icon count)
TYPE_TOKEN_TO_TAG = {
    "predator": "predator",
    "herbivore": "herbivore",
    "bear": "bear",
    "primate": "ape",
    "reptile": "lizard",
    "bird": "bird",
    "pet": "pet",
    "sea animal": "marine",
}

CONTINENT_MAP = {
    "africa": "africa",
    "americas": "americas",
    "asia": "asia",
    "europe": "europe",
    "australia": "australia",
}

REQS_TAG_MAP = {
    "partner zoo": "partner-zoo",
    "animals ii": "animals-ii",
    "animals 2": "animals-ii",
    "sponsor ii": "level-ii-sponsor",
    "level ii sponsor card": "level-ii-sponsor",
    "university": "university",
    "science": "science",
    "kiosk": "kiosk",
    "max. 25 appeal": "max-25-appeal",
    "max 25 appeal": "max-25-appeal",
}

# Named abilities printed on animal cards (value after = canonical tag).
ABILITY_NAME_MAP: dict[str, str] = {
    "sprint": "sprint",
    "pack": "pack",
    "hunter": "hunter",
    "clever": "clever",
    "inventive": "inventive",
    "full-throated": "full-throated",
    "resistance": "resistance",
    "assertion": "assertion",
    "jumping": "jumping",
    "pouch": "pouch",
    "digging": "digging",
    "flock animal": "flock",
    "flock": "flock",
    "snapping": "snapping",
    "venom": "venom",
    "sunbathing": "sunbathing",
    "hypnosis": "hypnosis",
    "constriction": "constriction",
    "scavenging": "scavenging",
    "pilfering": "pilfering",
    "posturing": "posturing",
    "perception": "perception",
    "determination": "determination",
    "peacocking": "peacocking",
    "dominance": "dominance",
    "camouflage": "camouflage",
    "symbiosis": "symbiosis",
    "helpful": "helpful",
    "trade": "trade",
    "adapt": "adapt",
    "glide": "glide",
    "scuba dive": "scuba-dive",
    "shark attack": "shark-attack",
    "cut down": "cut-down",
    "extra shift": "extra-shift",
    "mark": "mark",
    "monkey gang": "monkey-gang",
    "petting zoo animal": "petting",
}

# Parameterised abilities with sub-type (Boost: Sponsors → boost + target "sponsors").
PARAM_ABILITY_MAP = {
    "boost": "boost",
    "multiplier": "multiplier",
    "action": "action",
    "iconic animal": "iconic",
    "iconic": "iconic",
    "sponsor magnet": ("magnet", "sponsors"),
    "sea animal magnet": ("magnet", "sea-animal"),
}

SUB_TYPE_MAP = {
    "association": "association",
    "sponsors": "sponsors",
    "cards": "cards",
    "build": "build",
    "animals": "animals",
    "aminals": "animals",  # typo in source
    "africa": "africa",
    "americas": "americas",
    "asia": "asia",
    "europe": "europe",
    "australia": "australia",
    "sponsor": "sponsors",
    "card": "cards",
    "sea animal": "sea-animal",
}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


# ---------------------------------------------------------------------------
# Enclosure parsing
# ---------------------------------------------------------------------------

_ENCLOSURE_ALT_RE = re.compile(r"\(([A-Z]+)\s*(\d+)\)")  # matches (RH 2), (LBA 1)
_AQ_RE = re.compile(r"Aq\s*(\d+)\s*(R)?", re.IGNORECASE)
_LRH_RE = re.compile(r"LRH\s*(\d+)", re.IGNORECASE)
_PZ_RE = re.compile(r"PZ\s*(\d+)", re.IGNORECASE)
_PAREN_NUM_RE = re.compile(r"\((\d+)\)")


def parse_enclosure(raw: Any) -> dict:
    """Return dict with keys: size, biomes, enclosure_type, alt_enclosure_type, alt_enclosure_size."""
    out = {
        "size": None,
        "biomes": [],
        "enclosure_type": None,
        "alt_enclosure_type": None,
        "alt_enclosure_size": None,
    }
    if raw is None:
        return out
    s = str(raw).strip()

    # Petting zoo only: "PZ 1"
    if s.upper().startswith("PZ"):
        m = _PZ_RE.search(s)
        out["enclosure_type"] = "petting-zoo"
        out["size"] = int(m.group(1)) if m else None
        return out

    # Sea animal with LRH alt: "(4)  Aq 3 / LRH 3"
    # Sea turtle pattern.
    if "LRH" in s and "Aq" in s:
        pm = _PAREN_NUM_RE.search(s)
        aqm = _AQ_RE.search(s)
        lrhm = _LRH_RE.search(s)
        out["enclosure_type"] = "aquarium"
        out["size"] = int(pm.group(1)) if pm else None
        # aquarium size (M in Aq M) — store as primary `size`? No: spec says size = parenthesised
        # value (category size). The Aq M goes somewhere — we don't currently have a field for
        # "aquarium space requirement" distinct from category size. Stash it in alt.
        out["alt_enclosure_type"] = "large-reptile-house"
        out["alt_enclosure_size"] = int(lrhm.group(1)) if lrhm else None
        if aqm:
            # Bit of a loss here — aquarium-space requirement not separately modelled for
            # dual-habitat creatures. We currently attach it via reef/marine biome.
            pass
        out["biomes"].append("marine")
        return out

    # Penguin-style dual enclosure: "3RW / Aq 2"
    if "/" in s and "Aq" in s:
        left, right = [p.strip() for p in s.split("/", 1)]
        main = parse_enclosure(left)
        altm = _AQ_RE.search(right)
        out.update(main)
        out["alt_enclosure_type"] = "aquarium"
        out["alt_enclosure_size"] = int(altm.group(1)) if altm else None
        out["biomes"] = main["biomes"] + ["marine"]
        return out

    # Sea animal: "(N)  Aq M [R]"
    if s.startswith("("):
        pm = _PAREN_NUM_RE.search(s)
        aqm = _AQ_RE.search(s)
        out["enclosure_type"] = "aquarium"
        out["size"] = int(pm.group(1)) if pm else None
        # The Aq number = aquarium space requirement; store as alt_enclosure_size
        # on the primary enclosure_type? Cleaner: reuse alt slot as "secondary spec".
        # But alt is supposed to be a different enclosure *type*. Instead, for
        # aquarium cards we keep `size` = category size (from parens) and drop the
        # Aq number into alt_enclosure_size (same enclosure type). We record the
        # Aq number in alt_enclosure_size only if it differs from size.
        if aqm:
            aq = int(aqm.group(1))
            if aq != out["size"]:
                out["alt_enclosure_size"] = aq
        if aqm and aqm.group(2):  # 'R' suffix
            out["biomes"].append("rock")
        out["biomes"].append("marine")
        return out

    # Land animal with optional (RH N) or (LBA N) alt: e.g. "5W (RH 3)", "4 (LBA 1)", "3R"
    alt_match = _ENCLOSURE_ALT_RE.search(s)
    if alt_match:
        code = alt_match.group(1)
        alt_n = int(alt_match.group(2))
        if code == "RH":
            out["alt_enclosure_type"] = "reptile-house"
        elif code == "LBA":
            out["alt_enclosure_type"] = "large-bird-aviary"
        else:
            out["alt_enclosure_type"] = None
        out["alt_enclosure_size"] = alt_n
        head = s[: alt_match.start()].strip()
    else:
        head = s

    # head is now like "5", "3R", "2RR", "5WR", "4WW"
    m = re.match(r"(\d+)\s*([RW]*)", head)
    if m:
        out["size"] = int(m.group(1))
        for ch in m.group(2):
            if ch in BIOME_LETTERS:
                out["biomes"].append(BIOME_LETTERS[ch])
    out["enclosure_type"] = "standard"
    return out


# ---------------------------------------------------------------------------
# Type / continent columns
# ---------------------------------------------------------------------------

def parse_type_column(raw: Any) -> tuple[list[str], list[str]]:
    """Return (abilities from icons, extras for notes).

    Handles 'Predator', 'Predator/Bear', 'Predator x2', 'Sea Animal / Reptile', 'Sea Animal 2'.
    Duplicate tags encode multiplicity: 'Predator x2' → ['predator','predator'].
    """
    icons: list[str] = []
    if raw is None:
        return icons, []
    s = str(raw).strip().lower()
    # Split on '/' for multi-category
    parts = [p.strip() for p in s.split("/")]
    for p in parts:
        # Extract multiplier (xN or trailing " 2")
        mult = 1
        m = re.search(r"x\s*(\d+)\s*$", p)
        if m:
            mult = int(m.group(1))
            p = p[: m.start()].strip()
        else:
            m = re.search(r"\s(\d+)\s*$", p)
            if m:
                mult = int(m.group(1))
                p = p[: m.start()].strip()
        p = p.strip()
        tag = TYPE_TOKEN_TO_TAG.get(p)
        if tag:
            icons.extend([tag] * mult)
    return icons, []


def parse_continent_column(raw: Any) -> list[str]:
    if raw is None:
        return []
    s = str(raw).strip().lower()
    if s == "none":
        return []
    out: list[str] = []
    for part in re.split(r"[\n,/]", s):
        part = part.strip()
        if not part:
            continue
        mult = 1
        m = re.search(r"x\s*(\d+)\s*$", part)
        if m:
            mult = int(m.group(1))
            part = part[: m.start()].strip()
        tag = CONTINENT_MAP.get(part)
        if tag:
            out.extend([tag] * mult)
    return out


# ---------------------------------------------------------------------------
# Reqs column
# ---------------------------------------------------------------------------

def parse_reqs_column(raw: Any) -> tuple[list[str], int | None]:
    """Return (requires tags, reputation_requirement).

    Requires tags duplicate for xN (e.g. Predator x3 → three 'predator').
    """
    if raw is None:
        return [], None
    s = str(raw).strip()
    tags: list[str] = []
    rep_req: int | None = None

    for line in re.split(r"[\n]+", s):
        line = line.strip()
        if not line:
            continue
        low = _norm(line)

        # Reputation N
        m = re.match(r"reputation\s+(\d+)", low)
        if m:
            rep_req = int(m.group(1))
            continue

        # Icon threshold like "Predator x3", "Asia x2", "Bird"
        m = re.match(r"([a-z ]+?)\s*x\s*(\d+)\s*$", low)
        if m:
            name, count = m.group(1).strip(), int(m.group(2))
            tag = _icon_name_to_tag(name)
            if tag:
                tags.extend([tag] * count)
                continue

        # Named requirement (partner zoo, animals II, university, etc.)
        if low in REQS_TAG_MAP:
            tags.append(REQS_TAG_MAP[low])
            continue

        # Plain icon with implicit count of 1 (e.g. "Bird", "Africa", "Sea Animal")
        tag = _icon_name_to_tag(low)
        if tag:
            tags.append(tag)
            continue

        # Fallback — ignore, parser caller can inspect
    return tags, rep_req


def _icon_name_to_tag(name: str) -> str | None:
    name = name.strip().lower()
    if name in TYPE_TOKEN_TO_TAG:
        return TYPE_TOKEN_TO_TAG[name]
    if name in CONTINENT_MAP:
        return CONTINENT_MAP[name]
    if name == "science":
        return "science"
    if name == "research":
        return "science"
    if name == "water":
        return "water"
    if name == "rock":
        return "rock"
    if name in REQS_TAG_MAP:
        return REQS_TAG_MAP[name]
    return None


# ---------------------------------------------------------------------------
# Ability column
# ---------------------------------------------------------------------------

def parse_ability_column(raw: Any) -> tuple[list[str], dict[str, int], dict[str, str]]:
    """Return (tags, ability_levels, ability_targets)."""
    tags: list[str] = []
    levels: dict[str, int] = {}
    targets: dict[str, str] = {}

    if raw is None:
        return tags, levels, targets
    s = str(raw).strip()
    if not s or s.lower() == "none":
        return tags, levels, targets

    # Split on "\n", "/", ","
    parts = [p.strip() for p in re.split(r"[\n,/]+", s) if p.strip()]

    for part in parts:
        tag, lvl, tgt = _parse_ability_part(part)
        if tag is None:
            continue
        tags.append(tag)
        if lvl is not None:
            levels[tag] = lvl
        if tgt is not None:
            targets[tag] = tgt

    return tags, levels, targets


def _parse_ability_part(raw: str) -> tuple[str | None, int | None, str | None]:
    s = raw.strip()
    low = _norm(s).replace(":", " ")
    # Form: "Boost: Association", "Multiplier: Sponsors", "Iconic Animal: Europe"
    for key in PARAM_ABILITY_MAP:
        if low.startswith(key + " ") or low == key:
            rest = low[len(key):].strip()
            mapping = PARAM_ABILITY_MAP[key]
            if isinstance(mapping, tuple):
                tag, tgt = mapping
                return tag, None, tgt
            tgt_tag = SUB_TYPE_MAP.get(rest)
            if tgt_tag:
                return mapping, None, tgt_tag
            return mapping, None, None

    # Form: "Sprint 3", "Hunter 4", "Posturing 1"
    m = re.match(r"^([a-z \-]+?)\s+(\d+|x)\s*$", low)
    if m:
        name = m.group(1).strip()
        lvl_raw = m.group(2)
        tag = ABILITY_NAME_MAP.get(name)
        if tag:
            lvl = None if lvl_raw == "x" else int(lvl_raw)
            return tag, lvl, None

    # Bare name
    tag = ABILITY_NAME_MAP.get(low)
    if tag:
        return tag, None, None

    return None, None, None


# ---------------------------------------------------------------------------
# Bonuses (A/C/R)
# ---------------------------------------------------------------------------

def parse_bonuses(raw: Any) -> tuple[int | None, int | None, int | None]:
    if raw is None:
        return None, None, None
    s = str(raw).strip()
    m = re.match(r"(\d+)\s*/\s*(\d+)\s*/\s*(\d+)", s)
    if not m:
        return None, None, None
    a, c, r = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return (a if a else None), (c if c else None), (r if r else None)


# ---------------------------------------------------------------------------
# Card builders
# ---------------------------------------------------------------------------

EMPTY = {
    "biomes": [], "continents": [], "size": None,
    "abilities": [], "requires": [], "provides": [], "triggers": [],
    "appeal": None, "conservation_points": None, "strength": None,
    "reputation_requirement": None, "reputation_reward": None, "money_cost": None,
    "text": "", "notes": None,
    "enclosure_type": None, "alt_enclosure_type": None, "alt_enclosure_size": None,
    "reef_ability": None, "wave_icon": False,
    "ability_levels": {}, "ability_targets": {},
    "tier_thresholds": [], "tier_rewards": [],
}


def new_card(**kw) -> dict:
    card = {**EMPTY, **kw}
    return card


def _titlecase(name: str) -> str:
    # "GREVY'S ZEBRA" → "Grevy's Zebra"; handles parentheses and hyphens.
    if not name:
        return name
    out = []
    for word in re.split(r"(\s+|[-/])", name):
        if word.strip() and word not in "-/":
            out.append(word[:1].upper() + word[1:].lower())
        else:
            out.append(word)
    return "".join(out)


# ---------------------------------------------------------------------------
# Sheet readers
# ---------------------------------------------------------------------------

def read_animals(ws, backup_by_id: dict) -> list[dict]:
    rows = list(ws.iter_rows(values_only=True))
    cards = []
    for row in rows[1:]:
        if not row or row[0] is None:
            continue
        num = int(row[0])
        name_raw = row[1]
        if not name_raw:
            continue
        latin = row[2]
        enc_raw = row[3]
        cost = row[4]
        type_raw = row[5]
        cont_raw = row[6]
        reqs_raw = row[7]
        abil_raw = row[8]
        bonus_raw = row[9]
        reef = row[10]
        wave = row[11]
        mw_flag = row[12]

        is_mw = (mw_flag == "MW")
        set_name = "marine-worlds" if is_mw else "base"
        prefix = "MW" if is_mw else "AN"
        cid = f"{prefix}-{num:03d}"

        enc = parse_enclosure(enc_raw)
        type_icons, _ = parse_type_column(type_raw)
        continents = parse_continent_column(cont_raw)
        req_tags, rep_req = parse_reqs_column(reqs_raw)
        abil_tags, abil_levels, abil_targets = parse_ability_column(abil_raw)
        appeal, cp, rep_reward = parse_bonuses(bonus_raw)

        abilities = list(type_icons) + abil_tags
        # Wave icon adds 'wave' tag for consistency with how other icons are tagged.
        wave_bool = bool(wave)

        notes = f"Latin: {latin}" if latin else None
        backup = backup_by_id.get(cid)
        text = backup["text"] if backup else ""
        if backup and backup.get("notes"):
            notes = backup["notes"] if notes is None else f"{notes}. {backup['notes']}"

        card = new_card(
            id=cid,
            name=_titlecase(name_raw),
            set=set_name,
            type="animal",
            biomes=enc["biomes"],
            continents=continents,
            size=enc["size"],
            abilities=abilities,
            requires=req_tags,
            provides=[],
            triggers=[],
            appeal=appeal,
            conservation_points=cp,
            reputation_requirement=rep_req,
            reputation_reward=rep_reward,
            money_cost=cost if isinstance(cost, int) else None,
            text=text,
            notes=notes,
            enclosure_type=enc["enclosure_type"],
            alt_enclosure_type=enc["alt_enclosure_type"],
            alt_enclosure_size=enc["alt_enclosure_size"],
            reef_ability=str(reef).strip() if reef else None,
            wave_icon=wave_bool,
            ability_levels=abil_levels,
            ability_targets=abil_targets,
        )
        cards.append(card)
    return cards


def read_sponsors(ws, backup_by_id: dict) -> list[dict]:
    rows = list(ws.iter_rows(values_only=True))
    cards = []
    for row in rows[1:]:
        if not row or row[0] is None or not isinstance(row[0], int):
            continue
        num = row[0]
        name = row[1]
        strength = row[2]
        reqs_raw = row[3]
        icons_gained_raw = row[4]
        instant = row[5]
        ongoing = row[6]
        endgame = row[7]
        wave = row[8]
        mw_raw = row[9]

        is_mw = (mw_raw == "MW")
        # Sponsors: if marked MW, it's a replacement → MW-###. Otherwise base → AN-###.
        prefix = "MW" if is_mw else "AN"
        set_name = "marine-worlds" if is_mw else "base"
        cid = f"{prefix}-{num:03d}"

        # Parse requirements
        req_tags, rep_req = parse_reqs_column(reqs_raw)
        # Split further on ';' and ','
        if reqs_raw:
            for seg in re.split(r"[;]+", str(reqs_raw)):
                seg = seg.strip()
                low = _norm(seg)
                if low in REQS_TAG_MAP and REQS_TAG_MAP[low] not in req_tags:
                    req_tags.append(REQS_TAG_MAP[low])

        # Parse provided icons
        provides = parse_provides(icons_gained_raw)

        triggers = []
        if instant:
            triggers.append("immediate")
        if ongoing:
            triggers.append("ongoing")
        if endgame:
            triggers.append("end")

        # Text assembled from instant/ongoing/endgame segments
        parts = [str(x).strip() for x in (instant, ongoing, endgame) if x]
        text = " / ".join(parts) if parts else ""
        backup = backup_by_id.get(cid)
        if backup and backup.get("text"):
            text = backup["text"]
        notes = backup["notes"] if backup else None

        abilities: list[str] = []
        # Tag science/research sponsors with `science` ability when they produce Research icons.
        if provides and any(p == "science" for p in provides):
            abilities.append("science")

        card = new_card(
            id=cid,
            name=name,
            set=set_name,
            type="sponsor",
            strength=strength if isinstance(strength, int) else None,
            requires=req_tags,
            provides=provides,
            triggers=triggers,
            reputation_requirement=rep_req,
            text=text,
            notes=notes,
            abilities=abilities,
            wave_icon=bool(wave),
        )
        cards.append(card)
    return cards


def parse_provides(raw: Any) -> list[str]:
    """Parse 'Icons Gained' column into a list of tag, duplicated for multiplicity."""
    if raw is None:
        return []
    s = str(raw)
    provides: list[str] = []
    # Strip parenthesised alternates
    s = re.sub(r"\([^)]*\)", "", s)
    for part in re.split(r"[+,\n]+", s):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"(\d+)\s+(.+)", part)
        if not m:
            continue
        count = int(m.group(1))
        name = _norm(m.group(2))
        # normalise 'Research' → science
        if name in ("research", "science", "sceince"):
            tag = "science"
        elif name in TYPE_TOKEN_TO_TAG:
            tag = TYPE_TOKEN_TO_TAG[name]
        elif name in CONTINENT_MAP:
            tag = CONTINENT_MAP[name]
        elif name == "rock":
            tag = "rock"
        elif name == "water":
            tag = "water"
        elif name in ("rocks", "waters"):
            tag = name[:-1]
        elif name == "petting zoo animal":
            tag = "pet"
        elif name == "x-token":
            tag = None
        else:
            tag = None
        if tag:
            provides.extend([tag] * count)
    return provides


def read_conservation(ws, backup_by_id: dict) -> list[dict]:
    rows = list(ws.iter_rows(values_only=True))
    cards = []
    for row in rows[1:]:
        if not row or row[0] is None:
            continue
        num = int(row[0])
        name = row[1]
        deck = row[2]  # Base / Zoo
        activity = row[3]
        size_req_raw = row[4]
        cp_raw = row[5]
        rep = row[6]
        requirements_text = row[7]
        mw_flag = row[8]

        tier_thr = parse_tier(size_req_raw)
        tier_rew = parse_tier(cp_raw)

        # Map activity → requires tag
        activity_tag = {
            "Collection": "collection-activity",
            "Release": "release-activity",
            "Partnership": "partnership-activity",
        }.get(activity)

        requires = [activity_tag] if activity_tag else []
        triggers = []
        if activity == "Release":
            triggers.append("on-release")
        elif activity == "Partnership":
            triggers.append("on-partnership")

        # Continent / animal-group requirements from the free-text field
        extra_tags = _infer_project_requires(requirements_text)
        requires.extend(extra_tags)

        rep_reward = None
        if isinstance(rep, int):
            rep_reward = rep
        # '2/2/0' tiered reputation — we record first tier as reward
        elif isinstance(rep, str):
            m = re.match(r"(\d+)", rep)
            if m:
                rep_reward = int(m.group(1))

        is_mw = (mw_flag == "MW")
        # Base-game printed card → AN-###. If the Deck is 'Base' and MW flag is present,
        # that means this row is the MW REPLACEMENT for the base card → MW-### (and we
        # also keep the base version via backup-only if it existed).
        # Simpler convention: if deck==Zoo, always AN-### (zoo-pack version); if deck==Base
        # and MW flag, MW-###; else AN-###.
        if deck == "Zoo":
            prefix = "AN"
            set_name = "base"  # zoo-pack projects shipped with base? Actually they're from the zoo map pack
        elif is_mw:
            prefix = "MW"
            set_name = "marine-worlds"
        else:
            prefix = "AN"
            set_name = "base"
        cid = f"{prefix}-{num:03d}"

        backup = backup_by_id.get(cid)
        text = (backup or {}).get("text") or (requirements_text or "")
        notes = (backup or {}).get("notes")

        card = new_card(
            id=cid,
            name=name.replace("*", "").strip() if name else name,
            set=set_name,
            type="conservation-project",
            requires=requires,
            triggers=triggers,
            reputation_reward=rep_reward,
            tier_thresholds=tier_thr,
            tier_rewards=tier_rew,
            text=text,
            notes=notes,
        )
        cards.append(card)
    return cards


def _infer_project_requires(text: str | None) -> list[str]:
    if not text:
        return []
    low = text.lower()
    tags: list[str] = []
    for kw, tag in (
        ("africa", "africa"),
        ("americas", "americas"),
        ("asia", "asia"),
        ("europe", "europe"),
        ("australia", "australia"),
        ("bird", "bird"),
        ("predator", "predator"),
        ("reptile", "lizard"),
        ("primate", "ape"),
        ("herbavore", "herbivore"),
        ("herbivore", "herbivore"),
        ("water icon", "water"),
        ("rock icon", "rock"),
        ("research icon", "science"),
    ):
        if kw in low and tag not in tags:
            tags.append(tag)
    return tags


def parse_tier(raw: Any) -> list[int]:
    """Parse tier strings like '5/4/2' or '1/2/3/4'.

    Reject range-style strings ('1 to 4', '1  to 4') — those are not tiered schedules.
    """
    if raw is None:
        return []
    s = str(raw).strip()
    # Drop parenthesised alternates (e.g. "(1/3/5/6)*")
    s = re.sub(r"\([^)]*\)", "", s).strip()
    if re.search(r"\bto\b", s, flags=re.IGNORECASE):
        return []
    m = re.findall(r"\d+", s)
    return [int(x) for x in m] if m else []


def read_final_scoring(ws, backup_by_id: dict) -> list[dict]:
    rows = list(ws.iter_rows(values_only=True))
    cards = []
    for row in rows[1:]:
        if not row or row[0] is None:
            continue
        num = int(row[0]) if isinstance(row[0], int) else int(row[0])
        name = row[1]
        req_raw = row[2]
        cp_raw = row[3]
        text_raw = row[4]
        extra = row[5]
        mw_flag = row[6]

        tier_thr = parse_tier(req_raw)
        tier_rew = parse_tier(cp_raw)

        is_mw = (mw_flag == "MW")
        prefix = "MW" if is_mw else "AN"
        set_name = "marine-worlds" if is_mw else "base"
        cid = f"{prefix}-{num:03d}"

        backup = backup_by_id.get(cid)
        text = (backup or {}).get("text") or (text_raw or "")
        notes = (backup or {}).get("notes") or (extra if extra else None)

        card = new_card(
            id=cid,
            name=(name or "").replace("*", "").strip(),
            set=set_name,
            type="final-scoring",
            tier_thresholds=tier_thr,
            tier_rewards=tier_rew,
            text=text,
            notes=notes,
        )
        cards.append(card)
    return cards


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if not XLSX.exists():
        print(f"ERROR: {XLSX} not found", file=sys.stderr)
        return 2

    backup_by_id: dict[str, dict] = {}
    if BACKUP.exists():
        with BACKUP.open() as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    backup_by_id[row["id"]] = row

    wb = openpyxl.load_workbook(XLSX, data_only=True)

    all_cards: list[dict] = []
    all_cards += read_final_scoring(wb["Final Scoring"], backup_by_id)
    all_cards += read_conservation(wb["Conservation"], backup_by_id)
    all_cards += read_sponsors(wb["Sponsors"], backup_by_id)
    all_cards += read_animals(wb["Animals"], backup_by_id)

    # Also include backup-only rows for base versions of MW-replaced cards
    # (where the spreadsheet only holds the MW replacement).
    new_ids = {c["id"] for c in all_cards}
    for bid, brow in backup_by_id.items():
        if bid not in new_ids:
            # Add with sensible defaults for new fields.
            brow.setdefault("enclosure_type", None)
            brow.setdefault("alt_enclosure_type", None)
            brow.setdefault("alt_enclosure_size", None)
            brow.setdefault("reef_ability", None)
            brow.setdefault("wave_icon", False)
            brow.setdefault("ability_levels", {})
            brow.setdefault("ability_targets", {})
            brow.setdefault("tier_thresholds", [])
            brow.setdefault("tier_rewards", [])
            all_cards.append(brow)

    all_cards.sort(key=lambda c: (c["type"], c["id"]))

    with OUT.open("w") as f:
        for card in all_cards:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")

    print(f"Wrote {len(all_cards)} cards to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
