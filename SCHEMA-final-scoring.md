# Final-scoring schema

Schema for cards with `"type": "final-scoring"`. **17 cards** in the dataset.

Final-scoring cards are the end-of-game bonus tiles drawn at game start. Each describes a category of zoo content that earns CP in tiered amounts at game end. They aren't played from hand — they sit in the open and apply to all players, or to a specific player depending on the variant — but they're modelled as cards in this dataset because they share the prereq + tiered-reward structure.

Read [SCHEMA.md](./SCHEMA.md) first for the global enums and invariants.

## Fields

### Identity & common

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable unique ID. |
| `name` | string | Card name as printed. |
| `games` | array of enum | Non-empty subset of the global `games` enum. See SCHEMA.md for `games` semantics. |
| `type` | const | Always `"final-scoring"` for cards in this schema. |
| `text` | string | Full verbatim card text. `""` only in trivial cases. |
| `notes` | string or null | Optional rulings / FAQ refs. `null` if none. |

### Tiered scoring

| Field | Type | Description |
|---|---|---|
| `tier_thresholds` | array of int | Required-count thresholds at game end, ascending (e.g. `[3, 6, 8, 10]`). `[]` for cards whose payoff isn't a simple tiered ladder (e.g. cards that score per-icon without a threshold). |
| `tier_rewards` | array of string | CP per threshold, paired 1:1 with `tier_thresholds`. Each entry is the slot's reward as text — typically `"<N> CP"` for plain final-scoring cards. `[]` if none. |

The validator enforces matching lengths when both arrays are non-empty, and that each `tier_rewards` entry is a string.

## Always null/empty for final-scoring cards

Final-scoring cards are extremely sparse: aside from the common identity fields and the tiered-scoring pair, every other schema field is constant.

| Field | Constant |
|---|---|
| `icons`, `abilities`, `requires`, `triggers` | `[]` |
| `rock_icons`, `water_icons` | `0` |
| `size`, `appeal`, `conservation_points`, `strength`, `reputation_requirement`, `bonus_reward`, `money_cost` | `null` |
| `standard_size`, `reptile_house_size`, `large_bird_aviary_size`, `petting_zoo_size`, `aquarium_size`, `reef_ability` | `null` |
| `wave_icon` | `false` |
| `ability_levels`, `ability_targets` | `{}` |
| `alternative_ability` | `null` |

The category being scored is captured in `name` and `text` (e.g. "Large Animal Zoo" → animals of size 4–5); it is not encoded as a structured filter.

## Examples

### Per-icon scoring without thresholds — Large Animal Zoo (`AN-001`)

```json
{
  "id": "AN-001",
  "name": "Large Animal Zoo",
  "games": ["base"],
  "type": "final-scoring",
  "rock_icons": 0,
  "water_icons": 0,
  "icons": [],
  "size": null,
  "abilities": [],
  "requires": [],
  "triggers": [],
  "appeal": null,
  "conservation_points": null,
  "strength": null,
  "reputation_requirement": null,
  "bonus_reward": null,
  "money_cost": null,
  "text": "Gain CP for large animals in your zoo.",
  "notes": null,
  "standard_size": null,
  "reptile_house_size": null,
  "large_bird_aviary_size": null,
  "petting_zoo_size": null,
  "aquarium_size": null,
  "reef_ability": null,
  "wave_icon": false,
  "ability_levels": {},
  "ability_targets": {},
  "alternative_ability": null,
  "tier_thresholds": [],
  "tier_rewards": []
}
```

### Tiered scoring — Small Animal Zoo (`AN-002`, 3/6/8/10 → 1/2/3/4 CP)

```json
{
  "id": "AN-002",
  "name": "Small Animal Zoo",
  "games": ["base", "marine-worlds"],
  "type": "final-scoring",
  "text": "Gain CP for small animals in your zoo.",
  "tier_thresholds": [3, 6, 8, 10],
  "tier_rewards": ["1 CP", "2 CP", "3 CP", "4 CP"],
  "...": "(remaining fields null/empty as per the schema)"
}
```

*(Example 2 is abbreviated. Real rows include every field — see Large Animal Zoo above for the full layout.)*
