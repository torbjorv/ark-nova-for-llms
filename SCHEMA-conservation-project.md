# Conservation-project schema

Schema for cards with `"type": "conservation-project"`. **41 cards** in the dataset (base + Marine Worlds).

Conservation projects are mid-game scoring cards: a player who meets the project's prerequisites may "support" it for tiered conservation-point and reputation rewards. The reward tiers shrink as more players support the project.

Read [SCHEMA.md](./SCHEMA.md) first for the global enums, the closed-vocabulary rule for tag fields, and the "every row contains every field" invariant.

## Fields

### Identity & common

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable unique ID. |
| `name` | string | Card name as printed. |
| `set` | enum | One of the global `set` enum. |
| `type` | const | Always `"conservation-project"` for cards in this schema. |
| `text` | string | Full verbatim card text describing the project's prerequisite. `""` only for trivial cases. |
| `notes` | string or null | Optional rulings / FAQ refs. `null` if none. |

### Tiered scoring

This is the conservation-project's defining structure: a list of thresholds with a 1:1 paired list of rewards. The first player to support pays/meets the leading threshold for the leading reward, the next pays the next threshold for the next reward, and so on.

| Field | Type | Description |
|---|---|---|
| `tier_thresholds` | array of int | Required-icon counts per support slot (e.g. `[5, 4, 2]` for `5/4/2`). `[]` if the project has no tiered prerequisite ladder. |
| `tier_rewards` | array of int | CP awarded per support slot, paired 1:1 with `tier_thresholds` (e.g. `[5, 3, 2]` for `5/3/2` CP). Same length as `tier_thresholds` when both are populated. `[]` if none. |

The validator enforces matching lengths when both arrays are non-empty.

### Tags

| Field | Type | Description |
|---|---|---|
| `requires` | array of tag | Prereq tags — typically a category icon (continent, animal class, or `rock` / `water`) the player must have in their zoo. Duplicates allowed. `[]` if the project's prerequisite isn't expressible as a tag. |
| `triggers` | array of tag | When the project's effect / scoring fires (e.g. `end` for end-of-game projects). `[]` for the standard mid-game support path that fires on the support action. |
| `abilities` | array of tag | Category tags on the project itself (used by a small number of projects whose effect maps to a known ability). `[]` for typical projects. |

### Optional iconography (rare)

| Field | Type | Description |
|---|---|---|
| `continents` | array of enum | Continent icons; almost always `[]`. (The project's continent prerequisite is encoded in `requires`, not `continents`.) |

### Reputation reward

| Field | Type | Description |
|---|---|---|
| `reputation_reward` | integer or null | Reputation gained when the player supports this project. `null` if none. |

## Always null/empty for conservation projects

| Field | Constant | Used by |
|---|---|---|
| `rock_icons` | `0` | animal |
| `water_icons` | `0` | animal |
| `size` | `null` | animal |
| `appeal` | `null` | animal |
| `conservation_points` | `null` | animal (CP from a project lives in `tier_rewards`, not `conservation_points`) |
| `strength` | `null` | sponsor |
| `reputation_requirement` | `null` | animal |
| `money_cost` | `null` | animal (projects are supported via the action, not bought) |
| `provides` | `[]` | sponsor |
| `standard_size`, `reptile_house_size`, `large_bird_aviary_size`, `petting_zoo_size`, `aquarium_size`, `large_reptile_house_size` | `null` | animal |
| `reef_ability` | `null` | animal |
| `wave_icon` | `false` | animal, sponsor |
| `ability_levels`, `ability_targets` | `{}` | animal |

## Examples

### Continent project — Africa (`AN-103`, `5/4/2` → `5/3/2`)

Standard tiered project: 5 Africa icons → 5 CP, 4 → 3 CP, 2 → 2 CP. Prerequisite encoded as a `requires` tag.

```json
{
  "id": "AN-103",
  "name": "Africa",
  "set": "base",
  "type": "conservation-project",
  "rock_icons": 0,
  "water_icons": 0,
  "continents": [],
  "size": null,
  "abilities": [],
  "requires": ["collection-activity", "africa"],
  "provides": [],
  "triggers": [],
  "appeal": null,
  "conservation_points": null,
  "strength": null,
  "reputation_requirement": null,
  "reputation_reward": null,
  "money_cost": null,
  "text": "Requires Africa icons in your zoo.",
  "notes": null,
  "standard_size": null,
  "reptile_house_size": null,
  "large_bird_aviary_size": null,
  "petting_zoo_size": null,
  "aquarium_size": null,
  "large_reptile_house_size": null,
  "reef_ability": null,
  "wave_icon": false,
  "ability_levels": {},
  "ability_targets": {},
  "tier_thresholds": [5, 4, 2],
  "tier_rewards": [5, 3, 2]
}
```
