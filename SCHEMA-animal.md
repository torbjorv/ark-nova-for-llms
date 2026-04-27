# Animal schema

Schema for cards with `"type": "animal"`. **160 cards** in the dataset (base + Marine Worlds).

Animals are creature cards placed into enclosures. They contribute appeal and ability icons; some award conservation points or release-bonus reputation; Marine Worlds animals carry a wave icon and/or a reef payoff.

Read [SCHEMA.md](./SCHEMA.md) first for the global enums (`set`, `type`, `continents`), the rock/water icon convention, the closed-vocabulary rule for tag fields, and the "every row contains every field" invariant.

## Fields

### Identity & common

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable unique ID (`AN-###`, `MW-###`, `ZM-###`, `PR-###`). |
| `name` | string | Card name as printed. |
| `set` | array of enum | Non-empty subset of the global `set` enum. See SCHEMA.md for set semantics. |
| `type` | const | Always `"animal"` for cards in this schema. |
| `text` | string | Full verbatim card text. `""` if the animal has no effect text (vanilla appeal-only animals). |
| `notes` | string or null | Optional rulings / Latin name / FAQ refs. `null` if none. |

### Iconography

| Field | Type | Description |
|---|---|---|
| `rock_icons` | integer | Number of rock-requirement icons printed on the card (`0`–`2` in practice). The animal's enclosure must include this many rock spaces. |
| `water_icons` | integer | Number of water-requirement icons printed on the card (`0`–`2` in practice). The animal's enclosure must include this many water spaces. |
| `continents` | array of enum | Continent icons, from the global `continents` enum. **Duplicates encode multiplicity** — `["africa","africa"]` = Africa ×2. `[]` for animals with no continent attribution. |
| `categories` | array of enum | Animal categories printed on the card, from the global `categories` enum (`bear`, `bird`, `herbivore`, `petting-zoo`, `predator`, `primate`, `reptile`, `sea-animal`). Most animals have one category; some belong to two (e.g. Sand Tiger Shark = sea-animal + predator). `[]` only for cards with no printed category icon. **Duplicates encode multiplicity** in principle, though no real card prints the same category twice. |
| `wave_icon` | boolean | `true` if the card carries the Marine Worlds wave icon. `false` otherwise. |

Sea-animal identity is captured by `"sea-animal"` in `categories` plus the `aquarium_size` field — there is no sea-animal enclosure-requirement icon in the rock/water sense.

### Size & enclosure placement

| Field | Type | Description |
|---|---|---|
| `size` | integer | Scoring / category size, 1–5. For land animals this matches `standard_size`. For sea animals this is the *category size* — the parenthesised number on the card used by size-tier scoring — and is distinct from `aquarium_size`. Always populated for animals. |
| `standard_size` | integer or null | Space requirement in a standard enclosure. `null` if the animal cannot be placed in a standard enclosure (most marine animals; reptile-house-only / petting-zoo-only / large-bird-aviary-only animals). |
| `reptile_house_size` | integer or null | Space requirement in a small reptile house (`RH N`). `null` if not applicable. |
| `large_bird_aviary_size` | integer or null | Space requirement in a large bird aviary (`LBA N`). `null` if not applicable. |
| `petting_zoo_size` | integer or null | Space requirement in the petting zoo (`PZ N`). `null` if not applicable. |
| `aquarium_size` | integer or null | Space requirement in an aquarium (`Aq N`). `null` if not applicable. |
| `large_reptile_house_size` | integer or null | Space requirement in a large reptile house (`LRH N`). `null` if not applicable. Used by sea turtles, which accept aquarium *or* large-reptile-house. |

To find animals placeable in a given enclosure kind, filter on the matching `*_size` field being non-null.

### Costs, rewards, prerequisites

| Field | Type | Description |
|---|---|---|
| `money_cost` | integer | Money cost to play. Always populated for animals. |
| `appeal` | integer or null | Appeal value. `null` for the small number of animals that grant no direct appeal. |
| `conservation_points` | integer or null | Conservation points the card itself awards (e.g. on release). `null` if none. |
| `reputation_requirement` | integer or null | Minimum reputation-track position required to play. `null` if no threshold. Reputation is never spent — strictly a threshold check. If a rep requirement is known to exist but the threshold isn't, set this to `null` and add the `reputation` tag to `requires`. |
| `reputation_reward` | integer or null | Reputation gained when the animal is released. `null` if none. |

### Tags

| Field | Type | Description |
|---|---|---|
| `abilities` | array of tag | **Ability keywords only** — `sprint`, `venom`, `inventive`, etc., from `ABILITIES.md`. Animal-category icons (`bear`, `bird`, `predator`, `sea-animal`, …) live in the structured `categories` field above, **not** here. **Duplicates encode multiplicity.** `[]` if the card has no ability keyword. |
| `requires` | array of tag | Prereq tags from `ABILITIES.md` — enclosure prereqs, adjacency prereqs, category prereqs (e.g. `["predator","predator"]` for *2 predator icons in the zoo*). Duplicates allowed. `[]` if no prerequisites. |
| `ability_levels` | object | `{tag: int}` for level-bearing abilities (e.g. `{"snapping": 2}` for Snapping 2). Keys must also appear in `abilities`. `{}` if none. |
| `ability_targets` | object | `{tag: string}` for parameterised abilities (e.g. `{"iconic": "europe"}`). Keys must also appear in `abilities`. `{}` if none. |

### Marine Worlds reef payload

| Field | Type | Description |
|---|---|---|
| `reef_ability` | string or null | Verbatim reef-ability payoff shorthand (e.g. `"DRAW CARD"`, `"KIOSK/PAV"`, `"SA 1"`). `null` for cards without a reef ability (all base-set animals; Marine Worlds animals without a printed reef payload). |

## Always null/empty for animals

These fields are part of every row (per the universal "every field always present" rule) but are **constant** on animal cards:

| Field | Constant | Used by |
|---|---|---|
| `provides` | `[]` | sponsor (icons / effects granted on play) |
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
  "set": ["base", "marine-worlds"],
  "type": "animal",
  "rock_icons": 0,
  "water_icons": 0,
  "continents": ["americas"],
  "categories": ["predator", "bear"],
  "size": 5,
  "abilities": ["inventive", "full-throated"],
  "requires": ["predator", "predator", "animals-ii"],
  "provides": [],
  "triggers": [],
  "appeal": 9,
  "conservation_points": null,
  "strength": null,
  "reputation_requirement": null,
  "reputation_reward": null,
  "money_cost": 22,
  "text": "Gain {} X-token -token for each bear icon in all zoos (max.3). / Hire an association worker.",
  "notes": "Latin: Ursus arctos horribilis",
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

### Reptile with alt enclosure — Nile Crocodile (`AN-469`, `5W (RH 3)`)

Standard *and* small-reptile-house, one water icon, levelled ability:

```json
{
  "id": "AN-469",
  "name": "Nile Crocodile",
  "set": ["base", "marine-worlds"],
  "type": "animal",
  "rock_icons": 0,
  "water_icons": 1,
  "continents": ["africa"],
  "categories": ["reptile"],
  "size": 5,
  "abilities": ["snapping"],
  "requires": ["reptile", "reptile", "reptile"],
  "ability_levels": {"snapping": 2},
  "ability_targets": {},
  "standard_size": 5,
  "reptile_house_size": 3,
  "large_bird_aviary_size": null,
  "petting_zoo_size": null,
  "aquarium_size": null,
  "large_reptile_house_size": null,
  "reef_ability": null,
  "wave_icon": false,
  "...": "(remaining fields null/empty as per the schema)"
}
```

### Sea animal — Blackside Hawkfish (`MW-533`, `(2) Aq 1`, reef `KIOSK/PAV`)

Aquarium-only sea animal, wave-trigger, reef payload. Sea-animal identity comes from `"sea-animal"` in `categories` plus `aquarium_size`, not from any rock/water icon.

```json
{
  "id": "MW-533",
  "name": "Blackside Hawkfish",
  "set": ["marine-worlds"],
  "type": "animal",
  "rock_icons": 0,
  "water_icons": 0,
  "continents": ["australia"],
  "categories": ["sea-animal"],
  "size": 2,
  "abilities": ["posturing"],
  "ability_levels": {"posturing": 1},
  "standard_size": null,
  "aquarium_size": 1,
  "reef_ability": "KIOSK/PAV",
  "wave_icon": true,
  "...": "(remaining fields null/empty as per the schema)"
}
```

*(Examples 2 and 3 are abbreviated. Real rows include every field — see Grizzly Bear above for the full layout.)*
