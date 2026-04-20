# Schema

Every row in `cards.jsonl` is a single JSON object with **every** field below present. Use `null` or `[]` where a field doesn't apply — never omit a field.

## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Stable unique ID. Format: `AN-###` for base, `MW-###` for Marine Worlds, `ZM-###` for zoo-map pack, `PR-###` for promos. |
| `name` | string | yes | Card name as printed. |
| `set` | enum | yes | One of `set` enum below. |
| `type` | enum | yes | One of `type` enum below. |
| `biomes` | array of enum | yes | Zero or more from `biomes` enum. `[]` if the card has no biome. |
| `continents` | array of enum | yes | Zero or more from `continents` enum. `[]` if none. |
| `size` | integer or null | yes | Animal size (1–5). `null` for non-animal cards. |
| `abilities` | array of tag | yes | Tags from `ABILITIES.md`. `[]` if none. |
| `requires` | array of tag | yes | Prerequisite tags from `ABILITIES.md` (enclosure, adjacency, other prereqs). `[]` if none. |
| `provides` | array of tag | yes | Effect tags from `ABILITIES.md` (what the card grants when played/active). `[]` if none. |
| `triggers` | array of tag | yes | When effects fire. Tags from `ABILITIES.md`. `[]` if none. |
| `appeal` | integer or null | yes | Appeal value. `null` if the card has no appeal. |
| `conservation_points` | integer or null | yes | Conservation points. `null` if none. |
| `strength` | integer or null | yes | Strength value. `null` if the card has no strength. |
| `reputation_cost` | integer or null | yes | Reputation required to play. `null` if none. |
| `money_cost` | integer or null | yes | Money cost to play. `null` if free / non-playable. |
| `text` | string | yes | Full verbatim card text. Empty string `""` if the card has no effect text. |
| `notes` | string or null | yes | Optional rulings / clarifications / FAQ references. `null` if none. |

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
Ark Nova has five continent icons. Use `[]` for cards with no continent attribution. Use multiple entries for animals native to multiple continents.
```
africa | americas | asia | europe | australia
```

## Tag fields

`abilities`, `requires`, `provides`, `triggers` each draw from the closed vocabulary in `ABILITIES.md`. Each tag must be defined there before it can appear in a row. The validator enforces this.

## Example row

```json
{
  "id": "AN-023",
  "name": "Polar Bear",
  "set": "marine-worlds",
  "type": "animal",
  "biomes": ["marine", "rock"],
  "continents": ["americas", "asia", "europe"],
  "size": 3,
  "abilities": ["predator", "large-animal"],
  "requires": ["large-aquarium", "rock-adjacent-enclosure"],
  "provides": ["reputation-on-release"],
  "triggers": ["on-release"],
  "appeal": 7,
  "conservation_points": 2,
  "strength": 5,
  "reputation_cost": null,
  "money_cost": 14,
  "text": "(Full card text goes here, verbatim.)",
  "notes": null
}
```

*(Values above are illustrative — verify against the real card when authoring.)*

## Design rules

1. **If a user might filter on it, it's a structured field or tag — not prose.** When a card has a mechanic that isn't yet captured structurally, extend the schema or add a tag, then re-tag affected rows.
2. **Tag vocabularies are closed.** Adding a tag means editing `ABILITIES.md` first.
3. **Enums are closed too.** Don't sneak a new `type` or `biome` into a row without adding it here.
4. **Nulls over omissions.** Every field is always present.
