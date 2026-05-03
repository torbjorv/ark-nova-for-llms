# Sponsor schema

Schema for cards with `"type": "sponsor"`. **80 cards** in the dataset (base + Marine Worlds).

Sponsors are non-animal cards played for their effects. Each sponsor has a printed strength / level (the gating rule for which sponsors a player may play, controlled by their sponsor card on the action board) and an effect described in `text`. Effects decompose into `icons` granted on play and `triggers`.

Read [SCHEMA.md](./SCHEMA.md) first for the global enums, the closed-vocabulary rule for tag fields, and the "every row contains every field" invariant.

## Fields

### Identity & common

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable unique ID. |
| `name` | string | Card name as printed. |
| `games` | array of enum | Non-empty subset of the global `games` enum. See SCHEMA.md for `games` semantics. |
| `type` | const | Always `"sponsor"` for cards in this schema. |
| `text` | string | Full verbatim card text. `""` only for trivial cases. |
| `notes` | string or null | Optional rulings / FAQ refs. `null` if none. |

### Strength

| Field | Type | Description |
|---|---|---|
| `strength` | integer or null | Sponsor strength / level. The player's current sponsor card sets the maximum strength they may play. `null` if a sponsor has no printed strength. |

### Icons granted on play

| Field | Type | Description |
|---|---|---|
| `icons` | array of enum | Icons the sponsor *grants* to the zoo when played. Drawn from the global `icons` enum (continents, animal categories, plus `rock` / `water` / `science`). **Duplicates encode multiplicity.** `[]` if the sponsor's effect is purely procedural (not modelled as a discrete icon grant). |

### Tags

`requires` and `triggers` both draw exclusively from `ABILITIES.md`.

| Field | Type | Description |
|---|---|---|
| `requires` | array of tag | Prereq tags — most commonly `level-ii-sponsor` / `level-iii-sponsor` gating tags, or named-icon prereqs. Duplicates allowed. `[]` if no prerequisites. |
| `triggers` | array of tag | When the effect fires — typically a subset of `immediate`, `ongoing`, `end`, plus reactive triggers (e.g. `on-play-animal`). Duplicates allowed. `[]` if the sponsor has no fire-time semantics modelled. |

### Marine Worlds wave-trigger sponsors

A small number of Marine Worlds sponsors carry the wave icon:

| Field | Type | Description |
|---|---|---|
| `wave_icon` | boolean | `true` for Marine Worlds wave-trigger sponsors (4 cards in the current dataset). `false` otherwise. |

### Bonus reward (rare)

| Field | Type | Description |
|---|---|---|
| `bonus_reward` | string or null | Verbatim text for any always-fires reward on play (e.g. `"1 reputation"`). `null` for almost all sponsors; populated only for the rare sponsor that grants a direct on-play bonus. |

## Always null/empty for sponsors

These fields are part of every row but are **constant** on sponsor cards:

| Field | Constant | Used by |
|---|---|---|
| `rock_icons` | `0` | animal |
| `water_icons` | `0` | animal |
| `size` | `null` | animal |
| `appeal` | `null` | animal |
| `conservation_points` | `null` | animal |
| `reputation_requirement` | `null` | animal |
| `money_cost` | `null` | animal (sponsors are paid for via the sponsor action's cost track, not a per-card money cost) |
| `standard_size`, `reptile_house_size`, `large_bird_aviary_size`, `petting_zoo_size`, `aquarium_size` | `null` | animal (sponsors aren't placed in enclosures) |
| `reef_ability` | `null` | animal |
| `abilities` | `[]` | animal (sponsors don't carry the named animal-ability keywords; the icons they grant live in `icons`) |
| `alternative_ability` | `null` | animal (alt-ability box is an animal-card feature) |
| `tier_thresholds` | `[]` | conservation-project, final-scoring |
| `tier_rewards` | `[]` | conservation-project, final-scoring |

## Examples

### Activated sponsor — Science Lab (`AN-201`)

Has all three trigger phases (immediate, ongoing, end), a level-II prereq, and grants a science icon:

```json
{
  "id": "AN-201",
  "name": "Science Lab",
  "games": ["base", "marine-worlds"],
  "type": "sponsor",
  "rock_icons": 0,
  "water_icons": 0,
  "icons": ["science"],
  "size": null,
  "abilities": [],
  "requires": ["level-ii-sponsor"],
  "triggers": ["immediate", "ongoing", "end"],
  "appeal": null,
  "conservation_points": null,
  "strength": 5,
  "reputation_requirement": null,
  "bonus_reward": null,
  "money_cost": null,
  "text": "Take 1 card from the deck or in reputation range. / Take 1 card from the deck or in reputation range. / Gain 1 CP / 2 CP for 3 / 6 research icons.",
  "notes": null,
  "standard_size": null,
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

### Reactive sponsor — Spokesperson (`AN-202`)

Ongoing-only trigger (fires whenever a research icon is played):

```json
{
  "id": "AN-202",
  "name": "Spokesperson",
  "games": ["base", "marine-worlds"],
  "type": "sponsor",
  "abilities": [],
  "requires": [],
  "icons": ["science"],
  "triggers": ["ongoing"],
  "strength": 5,
  "text": "Each time you play a research icon into your zoo, gain 1 reputation .",
  "...": "(remaining fields null/empty as per the schema)"
}
```

*(Example 2 is abbreviated. Real rows include every field — see Science Lab above for the full layout.)*
