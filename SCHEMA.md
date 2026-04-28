# Schema

Every row in `cards.jsonl` is a single JSON object with **every** field below present. Use `null` or `[]` / `{}` where a field doesn't apply — never omit a field.

The schema is split by card type so each type can be evaluated in isolation:

| `type` value | Schema | Cards in dataset |
|---|---|---|
| `animal` | [SCHEMA-animal.md](./SCHEMA-animal.md) | 160 |
| `sponsor` | [SCHEMA-sponsor.md](./SCHEMA-sponsor.md) | 80 |
| `conservation-project` | [SCHEMA-conservation-project.md](./SCHEMA-conservation-project.md) | 39 |
| `final-scoring` | [SCHEMA-final-scoring.md](./SCHEMA-final-scoring.md) | 17 |

Each per-type schema lists every field that can carry a value on that card type **and** the fields that are constant (always `null` / `[]` / `{}` / `false`) for that type. Together they cover the full row contract.

This document holds the cross-type pieces: global enums, the closed-vocabulary rule for tag fields, and the design rules.

## Global enums

### `set`

Stored as a JSON array of strings, listing the **deck configurations** the card appears in (not a single "this came from product X" label). Element values:

```
base | marine-worlds
```

Allowed combinations and what they mean:

| `set` value | meaning |
|---|---|
| `["base", "marine-worlds"]` | base card with no marine errata — in both pure-base and base+marine decks |
| `["base"]` | base card that the Marine Worlds expansion replaces with errata — only in pure-base decks |
| `["marine-worlds"]` | either a new marine card or the marine errata replacement — only in base+marine decks |

The card's printing source (which physical box it came from) is encoded in the `id` prefix (`AN-` = base box, `MW-` = marine box), not in `set`.

### `type`
```
animal | sponsor | conservation-project | final-scoring
```

### `icons`

The unified "icons this card contributes to your zoo when in play". A single array, populated on animals, sponsors, and conservation-projects (always `[]` on final-scoring). Duplicates encode multiplicity (e.g. `["primate","primate"]` = double-primate; `["africa","africa"]` = Africa ×2).

Closed vocabulary (16 values):

```
# 5 continents
africa | americas | asia | europe | australia

# 8 animal categories (base manual lists 7; Marine Worlds adds sea-animal)
bear | bird | herbivore | petting-zoo | predator | primate | reptile | sea-animal

# 3 named icons (sponsor-granted)
rock | water | science
```

What the field represents per type:
- **animal** — printed continent + category icons on the card itself.
- **sponsor** — icons the sponsor *grants* when played (primate, rock, science, etc.).
- **conservation-project** — always `[]`. Project cards print a category/continent icon for visual cueing, but it does **not** count toward zoo-icon totals; the prerequisite the project demands lives in `requires`.
- **final-scoring** — always `[]`.

Game mechanics that talk about "X icons in your zoo" — conservation-project requirements, sponsor prerequisites, final-scoring tallies — are answered by counting matching values across this field over the cards in a player's zoo (animals + sponsors). The same tag names appear in `requires` (e.g. `["predator","predator"]` = needs 2 predator icons in zoo).

The `type` column distinguishes "is this card an animal vs. a sponsor" when that orthogonal axis matters; `icons` does not encode it.

## Enclosure-requirement icons

Printed enclosure requirements (the `R` / `W` icons the zoo's enclosure must satisfy) are stored as two integer counts:

- `rock_icons` (integer ≥ 0) — number of rock icons printed on the card.
- `water_icons` (integer ≥ 0) — number of water icons printed on the card.

`0` means the card has no icon of that kind.

These are **separate** from the `icons` array — they're enclosure requirements, not icons-in-zoo. A sponsor that *grants* a rock icon to the zoo (e.g. Baboon Rock) puts `"rock"` in its `icons` array. An animal whose enclosure requires rock has `rock_icons: 1` (or `2`).

Sea Animals are an animal *category* (captured by `"sea-animal"` in the `icons` field plus the `aquarium_size` field for placement), not an enclosure requirement. A sea animal that also needs rock in its aquarium will have `rock_icons: 1` *and* `"sea-animal"` in `icons`.

## Tag fields

`abilities`, `requires`, `triggers` each draw from the closed vocabulary in [`ABILITIES.md`](./ABILITIES.md). Each tag must be defined there before it can appear in a row. The validator enforces this.

The semantics differ by tag-field role:
- `abilities` — ability keywords printed on the card itself (e.g. `sprint`, `venom`, `inventive`). Animal-category icons are **not** here — they live in the `icons` field above.
- `requires` — prerequisite tags that must be satisfied to play / support / activate. Many `requires` values reference the same tag names that appear in `icons` (e.g. `requires: ["predator","predator"]` checks for two predator icons in the zoo).
- `triggers` — when the card's effect fires (`immediate`, `ongoing`, `end`, plus reactive triggers).

Per-type schemas document which of these roles apply to which card types.

## Design rules

1. **If a user might filter on it, it's a structured field or tag — not prose.** When a card has a mechanic that isn't yet captured structurally, extend the schema or add a tag, then re-tag affected rows.
2. **Tag vocabularies are closed.** Adding a tag means editing `ABILITIES.md` first.
3. **Enums are closed too.** Don't sneak a new `type`, `set`, or `icons` value into a row without adding it here.
4. **Nulls over omissions.** Every field is always present.
5. **Duplicates encode multiplicity** in `icons`, `abilities`, `requires`. Don't collapse them. (Rock / water enclosure-requirement icon counts are stored as integers, not duplicated tags.)

## Validation

`python scripts/validate.py` enforces field presence, type correctness, enum membership, tag membership, `ability_levels` / `ability_targets` key consistency, and `tier_thresholds` / `tier_rewards` length matching. Run it before committing.
