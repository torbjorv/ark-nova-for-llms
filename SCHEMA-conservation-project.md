# Conservation-project schema

Schema for cards with `"type": "conservation-project"`. **39 cards** in the dataset (base + Marine Worlds).

Conservation projects are mid-game scoring cards: a player who meets the project's prerequisites may "support" it for tiered conservation-point and reputation rewards. The reward tiers shrink as more players support the project.

Read [SCHEMA.md](./SCHEMA.md) first for the global enums, the closed-vocabulary rule for tag fields, and the "every row contains every field" invariant.

## Fields

### Identity & common

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable unique ID. |
| `name` | string | Card name as printed. |
| `games` | array of enum | Non-empty subset of the global `games` enum. See SCHEMA.md for `games` semantics. |
| `type` | const | Always `"conservation-project"` for cards in this schema. |
| `text` | string | Full verbatim card text describing the project's prerequisite. `""` only for trivial cases. |
| `notes` | string or null | Optional rulings / FAQ refs. `null` if none. |

### Tiered scoring

This is the conservation-project's defining structure: a list of thresholds with a 1:1 paired list of rewards. The first player to support pays/meets the leading threshold for the leading reward, the next pays the next threshold for the next reward, and so on.

| Field | Type | Description |
|---|---|---|
| `tier_thresholds` | array of int | Required-icon counts per support slot (e.g. `[5, 4, 2]` for `5/4/2`). `[]` if the project has no tiered prerequisite ladder — for partnership / management-plan cards the gateway lives in `requires` instead. |
| `tier_rewards` | array of string | Reward per support slot, paired 1:1 with `tier_thresholds` when both are populated. Each entry is short text describing the full reward for that slot — base CP plus any per-slot extras. Examples: `"5 CP"` for a plain collection card; `"2 CP + 2 rep"` for a partnership slot that grants reputation; `"2 CP + Hunter 1"` for a management-plan slot that grants an ability. `[]` if none. |

The validator enforces matching lengths when both arrays are non-empty, and that each `tier_rewards` entry is a string.

### Tags

| Field | Type | Description |
|---|---|---|
| `requires` | array of tag | Prereq tags — typically a category icon (continent, animal category, or `rock` / `water`) the player must have in their zoo. Duplicates allowed. `[]` if the project's prerequisite isn't expressible as a tag. |
| `triggers` | array of tag | When the project's effect / scoring fires (e.g. `end` for end-of-game projects). `[]` for the standard mid-game support path that fires on the support action. |
| `abilities` | array of tag | Ability keywords on the project itself (used by a small number of projects whose effect maps to a known ability keyword). `[]` for typical projects. |

### Card-wide bonus reward

A reward that fires once per support, on top of the slot-specific `tier_rewards` entry. On release projects this is reputation; on management plans it can be a build (e.g. kiosk/pavilion), an ability trigger (e.g. sunbathing/digging), or any other always-fires effect.

| Field | Type | Description |
|---|---|---|
| `bonus_reward` | string or null | Verbatim text describing the card-wide bonus (e.g. `"1 reputation"`, `"build 1 kiosk or pavilion"`, `"2 sunbathing"`). `null` if none. Per-tier rewards belong in `tier_rewards`, not here. |

## Always null/empty for conservation projects

| Field | Constant | Used by |
|---|---|---|
| `icons` | `[]` | animal, sponsor (the icon printed on a project card is decorative and does **not** count toward zoo-icon totals — the project's prerequisite goes in `requires`) |
| `rock_icons` | `0` | animal |
| `water_icons` | `0` | animal |
| `size` | `null` | animal |
| `appeal` | `null` | animal |
| `conservation_points` | `null` | animal (CP from a project lives in `tier_rewards`, not `conservation_points`) |
| `strength` | `null` | sponsor |
| `reputation_requirement` | `null` | animal |
| `money_cost` | `null` | animal (projects are supported via the action, not bought) |
| `standard_size`, `reptile_house_size`, `large_bird_aviary_size`, `petting_zoo_size`, `aquarium_size` | `null` | animal |
| `reef_ability` | `null` | animal |
| `wave_icon` | `false` | animal, sponsor |
| `alternative_ability` | `null` | animal |

## Examples

### Continent project — Africa (`AN-103`, `5/4/2` → `5 CP / 3 CP / 2 CP`)

Standard tiered project: 5 Africa icons → 5 CP, 4 → 3 CP, 2 → 2 CP. Prerequisite encoded as a `requires` tag.

```json
{
  "id": "AN-103",
  "name": "Africa",
  "games": ["base", "marine-worlds"],
  "type": "conservation-project",
  "rock_icons": 0,
  "water_icons": 0,
  "icons": [],
  "size": null,
  "abilities": [],
  "requires": ["collection-activity", "africa"],
  "triggers": [],
  "appeal": null,
  "conservation_points": null,
  "strength": null,
  "reputation_requirement": null,
  "bonus_reward": null,
  "money_cost": null,
  "text": "Requires Africa icons in your zoo.",
  "notes": null,
  "standard_size": null,
  "reptile_house_size": null,
  "large_bird_aviary_size": null,
  "petting_zoo_size": null,
  "aquarium_size": null,
  "reef_ability": null,
  "wave_icon": false,
  "alternative_ability": null,
  "tier_thresholds": [5, 4, 2],
  "tier_rewards": ["5 CP", "3 CP", "2 CP"]
}
```

### Management plan — Predator Management Plan (`MW-134`)

Marine Worlds management plans have no escalating threshold ladder — every slot has the same gateway (`requires: ["collection-activity", "predator", "predator"]` for *Requires 2 predator icons*) and slots differ by their per-tier extra reward. `tier_thresholds` is `[]`; the per-slot rewards live in `tier_rewards`.

```json
{
  "id": "MW-134",
  "name": "Predator Management Plan",
  "games": ["marine-worlds"],
  "type": "conservation-project",
  "icons": [],
  "requires": ["collection-activity", "predator", "predator"],
  "triggers": [],
  "bonus_reward": null,
  "tier_thresholds": [],
  "tier_rewards": [
    "2 CP + Hunter 1",
    "2 CP + 1 rep per 2 research",
    "2 CP + search predator"
  ],
  "text": "Requires 2 predator icons.",
  "...": "(remaining fields null/empty as per the schema)"
}
```
