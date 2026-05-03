# Animal schema

Schema for cards with `"type": "animal"`. **160 cards** in the dataset (base + Marine Worlds).

Animals are creature cards placed into enclosures. They contribute appeal and ability icons; some award conservation points or release-bonus reputation; Marine Worlds animals carry a wave icon and/or a reef payoff.

Read [SCHEMA.md](./SCHEMA.md) first for the global enums (`games`, `type`, `icons`), the rock/water icon convention, the closed-vocabulary rule for tag fields, and the "every row contains every field" invariant.

## Fields

### Identity & common

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable unique ID (`AN-###`, `MW-###`, `ZM-###`, `PR-###`). |
| `name` | string | Card name as printed. |
| `games` | array of enum | Non-empty subset of the global `games` enum. See SCHEMA.md for `games` semantics. |
| `type` | const | Always `"animal"` for cards in this schema. |
| `text` | string | Full verbatim card text. `""` if the animal has no effect text (vanilla appeal-only animals). |
| `notes` | string or null | Optional rulings / Latin name / FAQ refs. `null` if none. |

### Iconography

| Field | Type | Description |
|---|---|---|
| `rock_icons` | integer | Number of rock-requirement icons printed on the card (`0`–`2` in practice). The animal's enclosure must include this many rock spaces. |
| `water_icons` | integer | Number of water-requirement icons printed on the card (`0`–`2` in practice). The animal's enclosure must include this many water spaces. |
| `icons` | array of enum | All zoo-icons printed on the card — continent icons (`africa`, `americas`, `asia`, `europe`, `australia`) plus animal-category icons (`bear`, `bird`, `herbivore`, `petting-zoo`, `predator`, `primate`, `reptile`, `sea-animal`). **Duplicates encode multiplicity** — `["primate","primate","africa"]` = double-primate Africa animal. `[]` only for animals with no printed icons. See `SCHEMA.md` for the full closed vocabulary. |
| `wave_icon` | boolean | `true` if the card carries the Marine Worlds wave icon. `false` otherwise. |

Sea-animal identity is captured by `"sea-animal"` in `icons` plus the `aquarium_size` field — there is no sea-animal enclosure-requirement icon in the rock/water sense.

### Size & enclosure placement

| Field | Type | Description |
|---|---|---|
| `size` | integer | Scoring / category size, 1–5. For land animals this matches `standard_size`. For sea animals this is the *category size* — the parenthesised number on the card used by size-tier scoring — and is distinct from `aquarium_size`. Always populated for animals. |
| `standard_size` | integer or null | Space requirement in a standard enclosure. `null` if the animal cannot be placed in a standard enclosure (most marine animals; reptile-house-only / petting-zoo-only / large-bird-aviary-only animals). |
| `reptile_house_size` | integer or null | Space requirement in the reptile house (`RH N`). `null` if not applicable. Sea turtles populate this *and* `aquarium_size` because they accept either enclosure. |
| `large_bird_aviary_size` | integer or null | Space requirement in a large bird aviary (`LBA N`). `null` if not applicable. |
| `petting_zoo_size` | integer or null | Space requirement in the petting zoo (`PZ N`). `null` if not applicable. |
| `aquarium_size` | integer or null | Space requirement in an aquarium (`Aq N`) — Marine Worlds adds Small Aquarium and Large Aquarium, but tokens are interchangeable across the two so a single field captures the requirement. `null` if not applicable. |

To find animals placeable in a given enclosure kind, filter on the matching `*_size` field being non-null.

### Costs, rewards, prerequisites

| Field | Type | Description |
|---|---|---|
| `money_cost` | integer | Money cost to play. Always populated for animals. |
| `appeal` | integer or null | Appeal value. `null` for the small number of animals that grant no direct appeal. |
| `conservation_points` | integer or null | Conservation points the card itself awards (e.g. on release). `null` if none. |
| `reputation_requirement` | integer or null | Minimum reputation-track position required to play. `null` if no threshold. Reputation is never spent — strictly a threshold check. |
| `bonus_reward` | string or null | Verbatim text for any always-fires reward triggered by playing or releasing the animal — typically `"<N> reputation"` for animals that grant rep on release. `null` if none. (This field is shared with conservation projects, where it carries non-rep card-wide rewards like `"build 1 kiosk or pavilion"`.) |

### Tags

| Field | Type | Description |
|---|---|---|
| `abilities` | array of tag | **Ability keywords only** — from `ABILITIES.md`. Animal-category icons (`bear`, `bird`, `predator`, `sea-animal`, …) live in the structured `icons` field above, **not** here. Each entry is either a bare name (`"inventive"`, `"petting"`) or `name:param` for leveled / targeted abilities: leveled (printed 1–5 level) as `"sprint:3"`, `"snapping:2"`, `"scavenging:5"`; targeted as `"iconic:europe"`, `"boost:sponsors"`, `"magnet:sea-animal"`. See `SCHEMA.md`'s `abilities` section for the closed leveled / targeted sets. **Duplicates encode multiplicity.** `[]` if the card has no ability keyword. |
| `requires` | array of tag | Prereq tags from `ABILITIES.md` — enclosure prereqs, adjacency prereqs, category prereqs (e.g. `["predator","predator"]` for *2 predator icons in the zoo*). Duplicates allowed. `[]` if no prerequisites. |
| `alternative_ability` | string or null | The smaller "alternative ability" box printed below the primary ability on some animals — a game-mode option where players agree to use the alt instead of the primary. Free-text in general, but animal cards follow a closed convention: a single short tag using the same `name[:param]` form as `abilities[]` (`"sprint:1"`, `"sprint:2"`, `"inventive:1"`, `"inventive:2"`, `"clever"`, `"determination"`). `null` for animals with no alternative-ability box. The four printed primary→alt patterns are listed in `ABILITIES.md`. Animals with two real ability boxes (Grizzly Bear's Inventive + Full-throated, Loggerhead Sea Turtle's Scuba-Dive + Marketing, etc.) carry both tags in `abilities` and leave this field `null` — the alt-ability box is visually distinct from a regular second ability. One final-scoring card also uses this column for a different alt-ability mechanic (printed prose, not a tag) — see `SCHEMA-final-scoring.md`. |

### Marine Worlds reef payload

| Field | Type | Description |
|---|---|---|
| `reef_ability` | string or null | Verbatim reef-ability payoff shorthand (e.g. `"DRAW CARD"`, `"KIOSK/PAV"`, `"SA 1"`). `null` for cards without a reef ability (all base-set animals; Marine Worlds animals without a printed reef payload). |

## Always null/empty for animals

These fields are part of every row (per the universal "every field always present" rule) but are **constant** on animal cards:

| Field | Constant | Used by |
|---|---|---|
| `triggers` | `[]` | sponsor, conservation-project (when effects fire) |
| `strength` | `null` | sponsor |
| `tier_thresholds` | `[]` | conservation-project, final-scoring |
| `tier_rewards` | `[]` | conservation-project, final-scoring |

## Examples

### Land animal — Grizzly Bear (`AN-411`)

Standard enclosure, no rock/water requirement, multi-icon prereq (Predator ×2):

```json
{
  "id": "AN-411",
  "name": "Grizzly Bear",
  "games": ["base", "marine-worlds"],
  "type": "animal",
  "rock_icons": 0,
  "water_icons": 0,
  "icons": ["predator", "americas"],
  "size": 5,
  "abilities": ["inventive", "full-throated"],
  "requires": ["predator", "predator", "animals-ii"],
  "triggers": [],
  "appeal": 9,
  "conservation_points": null,
  "strength": null,
  "reputation_requirement": null,
  "bonus_reward": null,
  "money_cost": 22,
  "text": "",
  "notes": "Latin: Ursus arctos horribilis",
  "standard_size": 5,
  "reptile_house_size": null,
  "large_bird_aviary_size": null,
  "petting_zoo_size": null,
  "aquarium_size": null,
  "reef_ability": null,
  "wave_icon": false,
  "alternative_ability": null,
  "tier_thresholds": [],
  "tier_rewards": []
}
```

(Currently `text` is `""` for every animal row — see issue #8 for the planned audit that will populate verbatim card text where the printed ability has effect text the tag alone can't capture.)

### Reptile with alt enclosure — Nile Crocodile (`AN-469`, `5W (RH 3)`)

Standard *and* small-reptile-house, one water icon, levelled ability:

```json
{
  "id": "AN-469",
  "name": "Nile Crocodile",
  "games": ["base", "marine-worlds"],
  "type": "animal",
  "rock_icons": 0,
  "water_icons": 1,
  "icons": ["reptile", "africa"],
  "size": 5,
  "abilities": ["snapping:2"],
  "requires": ["reptile", "reptile", "reptile"],
  "standard_size": 5,
  "reptile_house_size": 3,
  "large_bird_aviary_size": null,
  "petting_zoo_size": null,
  "aquarium_size": null,
  "reef_ability": null,
  "wave_icon": false,
  "...": "(remaining fields null/empty as per the schema)"
}
```

### Sea animal — Blackside Hawkfish (`MW-533`, `(2) Aq 1`, reef `KIOSK/PAV`)

Aquarium-only sea animal, wave-trigger, reef payload. Sea-animal identity comes from `"sea-animal"` in `icons` plus `aquarium_size`, not from any rock/water icon.

```json
{
  "id": "MW-533",
  "name": "Blackside Hawkfish",
  "games": ["marine-worlds"],
  "type": "animal",
  "rock_icons": 0,
  "water_icons": 0,
  "icons": ["sea-animal", "australia"],
  "size": 2,
  "abilities": ["posturing:1"],
  "standard_size": null,
  "aquarium_size": 1,
  "reef_ability": "KIOSK/PAV",
  "wave_icon": true,
  "...": "(remaining fields null/empty as per the schema)"
}
```

*(Examples 2 and 3 are abbreviated. Real rows include every field — see Grizzly Bear above for the full layout.)*
