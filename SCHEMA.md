# Schema

Every row in `cards.jsonl` is a single JSON object with **every** field below present. Use `null` or `[]` / `{}` where a field doesn't apply — never omit a field.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Stable unique ID. Format: `AN-###` for base, `MW-###` for Marine Worlds, `ZM-###` for zoo-map pack, `PR-###` for promos. Base and Marine-Worlds cards that share a printed number (e.g. the MW replacement for base `101`) coexist as `AN-101` and `MW-101`. |
| `name` | string | yes | Card name as printed. |
| `set` | enum | yes | One of `set` enum below. |
| `type` | enum | yes | One of `type` enum below. |
| `biomes` | array of enum | yes | Zero or more from `biomes` enum. **Duplicates encode multiplicity** — `["water","water"]` = two water-habitat icons (`2W`). `[]` if the card has no biome. |
| `continents` | array of enum | yes | Zero or more from `continents` enum. **Duplicates encode multiplicity** — `["africa","africa"]` = Africa ×2. `[]` if none. |
| `size` | integer or null | yes | Scoring / category size (1–5). For land animals this equals `standard_size`. For sea animals this is the *category size* — the number in parentheses on the card, used by size-tier scoring — which is distinct from `aquarium_size`. `null` for non-animal cards. |
| `abilities` | array of tag | yes | Tags from `ABILITIES.md`. **Duplicates encode multiplicity** — `["predator","predator"]` = Predator ×2. `[]` if none. |
| `requires` | array of tag | yes | Prerequisite tags from `ABILITIES.md` (enclosure, adjacency, other prereqs). Duplicates allowed. `[]` if none. |
| `provides` | array of tag | yes | Effect tags from `ABILITIES.md` (icons / effects a sponsor or card grants when played). Duplicates allowed. `[]` if none. |
| `triggers` | array of tag | yes | When effects fire. Tags from `ABILITIES.md`. `[]` if none. |
| `appeal` | integer or null | yes | Appeal value. `null` if the card has no appeal. |
| `conservation_points` | integer or null | yes | Conservation points. `null` if none. |
| `strength` | integer or null | yes | Sponsor strength (level). `null` if the card has no strength. |
| `reputation_requirement` | integer or null | yes | Minimum reputation-track position required to play the card. `null` if no threshold. Reputation is never spent in Ark Nova — it's strictly a threshold check, so there is no separate "cost" field. If the card has a rep requirement but the specific threshold is unknown from the source, set this to `null` and add the `reputation` tag to `requires`. |
| `reputation_reward` | integer or null | yes | Reputation gained on play (sponsors) or on release (animals). `null` if none. |
| `money_cost` | integer or null | yes | Money cost to play. `null` if free / non-playable. |
| `text` | string | yes | Full verbatim card text. Empty string `""` if the card has no effect text. |
| `notes` | string or null | yes | Optional rulings / clarifications / FAQ references. `null` if none. |
| `standard_size` | integer or null | yes | Space requirement in a standard enclosure. `null` if the animal cannot be placed in a standard enclosure. |
| `reptile_house_size` | integer or null | yes | Space requirement in a small reptile house (`RH N` on reptile cards). `null` if not applicable. |
| `large_bird_aviary_size` | integer or null | yes | Space requirement in a large bird aviary (`LBA N` on bird cards). `null` if not applicable. |
| `petting_zoo_size` | integer or null | yes | Space requirement in the petting zoo (`PZ N`). `null` if not applicable. |
| `aquarium_size` | integer or null | yes | Space requirement in an aquarium (`Aq N`). `null` if not applicable. |
| `large_reptile_house_size` | integer or null | yes | Space requirement in a large reptile house (`LRH N`). `null` if not applicable. Used by sea turtles, which accept aquarium *or* large-reptile-house. |
| `reef_ability` | string or null | yes | Verbatim reef-ability payoff shorthand (e.g. `"DRAW CARD"`, `"KIOSK/PAV"`, `"SA 1"`). `null` for cards without a reef ability. |
| `wave_icon` | boolean | yes | `true` if the card carries the wave icon (Marine Worlds trigger). `false` otherwise. |
| `ability_levels` | object | yes | Map of `tag → integer` recording the printed level for level-bearing abilities (e.g. `{"hunter": 4}` for Hunter 4). Keys must also appear in `abilities`. `{}` if none. |
| `ability_targets` | object | yes | Map of `tag → string` recording the sub-type for parameterised abilities (e.g. `{"multiplier": "sponsors"}` for Multiplier: Sponsors, `{"iconic": "europe"}` for Iconic Animal: Europe). Keys must also appear in `abilities`. `{}` if none. |
| `tier_thresholds` | array of int | yes | Tiered score-requirement values for conservation projects and final-scoring cards (e.g. `[5,4,2]` for `5/4/2`). `[]` if the card has no tiered scoring. |
| `tier_rewards` | array of int | yes | Tiered reward values paired 1:1 with `tier_thresholds` (e.g. `[5,3,2]` for `5/3/2` CP). `[]` if none. |

## Enums

### `set`
```
base | marine-worlds | zoo-map | promos
```

### `type`
```
animal | sponsor | conservation-project | zoo-map | final-scoring | other
```

### `biomes`
Ark Nova has three habitat icons that appear on cards. Use `[]` for cards with no habitat icon.
```
rock | water | marine
```
- `rock` — card has the rock-habitat icon (typically requires rock in its enclosure).
- `water` — card has the water-habitat icon (typically requires water in its enclosure).
- `marine` — card has the marine / aquarium icon (Marine Worlds group).

### `continents`
Ark Nova has five continent icons. Use `[]` for cards with no continent attribution. Use multiple entries for animals native to multiple continents or with an `×2` icon.
```
africa | americas | asia | europe | australia
```

## Tag fields

`abilities`, `requires`, `provides`, `triggers` each draw from the closed vocabulary in `ABILITIES.md`. Each tag must be defined there before it can appear in a row. The validator enforces this.

## Example rows

**Land animal — Grizzly Bear (AN-411)** — standard enclosure, multi-line Reqs, levelled ability:

```json
{
  "id": "AN-411",
  "name": "Grizzly Bear",
  "set": "base",
  "type": "animal",
  "biomes": [],
  "continents": ["americas"],
  "size": 5,
  "abilities": ["predator", "inventive", "full-throated"],
  "requires": ["predator", "predator", "animals-ii"],
  "provides": [],
  "triggers": [],
  "appeal": 9,
  "conservation_points": null,
  "strength": null,
  "reputation_requirement": null,
  "reputation_reward": null,
  "money_cost": 22,
  "text": "(verbatim card text)",
  "notes": null,
  "standard_size": 5,
  "reptile_house_size": null,
  "large_bird_aviary_size": null,
  "petting_zoo_size": null,
  "aquarium_size": null,
  "large_reptile_house_size": null,
  "reef_ability": null,
  "wave_icon": false,
  "ability_levels": {},
  "ability_targets": {},
  "tier_thresholds": [],
  "tier_rewards": []
}
```

**Reptile with alt enclosure — Nile Crocodile (`5W (RH 3)`)**:

```json
{
  "id": "AN-469",
  "name": "Nile Crocodile",
  "type": "animal",
  "biomes": ["water"],
  "continents": ["africa"],
  "size": 5,
  "abilities": ["lizard", "snapping"],
  "requires": ["lizard", "lizard", "lizard"],
  "ability_levels": {"snapping": 2},
  "ability_targets": {},
  "standard_size": 5,
  "reptile_house_size": 3,
  "large_bird_aviary_size": null,
  "petting_zoo_size": null,
  "aquarium_size": null,
  "large_reptile_house_size": null,
  "reef_ability": null,
  "wave_icon": false
}
```

**Sea animal — Blackside Hawkfish (`(2) Aq 1`, reef `KIOSK/PAV`)**:

```json
{
  "id": "MW-533",
  "name": "Blackside Hawkfish",
  "type": "animal",
  "biomes": ["marine"],
  "continents": ["australia"],
  "size": 2,
  "abilities": ["marine", "posturing"],
  "ability_levels": {"posturing": 1},
  "standard_size": null,
  "reptile_house_size": null,
  "large_bird_aviary_size": null,
  "petting_zoo_size": null,
  "aquarium_size": 1,
  "large_reptile_house_size": null,
  "reef_ability": "KIOSK/PAV",
  "wave_icon": true
}
```

**Conservation project with tiered scoring — Africa (`5/4/2` → `5/3/2`)**:

```json
{
  "id": "AN-103",
  "name": "Africa",
  "type": "conservation-project",
  "continents": ["africa"],
  "requires": ["africa"],
  "tier_thresholds": [5, 4, 2],
  "tier_rewards": [5, 3, 2]
}
```

*(Examples above are abbreviated — real rows include every field.)*

## Design rules

1. **If a user might filter on it, it's a structured field or tag — not prose.** When a card has a mechanic that isn't yet captured structurally, extend the schema or add a tag, then re-tag affected rows.
2. **Tag vocabularies are closed.** Adding a tag means editing `ABILITIES.md` first.
3. **Enums are closed too.** Don't sneak a new `type` or `biome` into a row without adding it here.
4. **Nulls over omissions.** Every field is always present.
5. **Duplicates encode multiplicity** in `biomes`, `continents`, `abilities`, `requires`, and `provides`. Don't collapse them.
