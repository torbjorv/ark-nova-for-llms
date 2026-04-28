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

### `continents`
Five continent icons. Use `[]` for cards with no continent attribution. Duplicates encode multiplicity (e.g. `["africa","africa"]` = Africa ×2).

```
africa | americas | asia | europe | australia
```

### `categories`
The 8 official animal categories from the rulebook (base manual page 13 lists 7; Marine Worlds adds `sea-animal`). Used on animal and conservation-project cards to record category icons printed on the card itself. `[]` for cards with no category icon. Duplicates encode multiplicity.

```
bear | bird | herbivore | petting-zoo | predator | primate | reptile | sea-animal
```

The same tag names appear in `requires` (e.g. `["predator","predator"]` = needs 2 predator icons in zoo) and in `provides` on sponsor cards (icons granted on play). The `categories` field is the per-card "what icons are printed here" list; `requires` / `provides` reference those icons in zoo-state context.

## Enclosure-requirement icons

The Ark Nova rulebook talks about cards carrying "1 or 2 rock and/or water icons" — printed enclosure requirements that the zoo's `R` / `W` spaces must satisfy. There is no umbrella term in the rulebook, so the schema stores them as two integer counts:

- `rock_icons` (integer ≥ 0) — number of rock icons printed on the card.
- `water_icons` (integer ≥ 0) — number of water icons printed on the card.

`0` means the card has no icon of that kind. `["water","water"]` from the legacy schema is now `water_icons: 2`.

There is no "marine" enclosure-requirement icon. Sea Animals are an animal *category* (captured by `"sea-animal"` in the `categories` field on animal cards and by the `aquarium_size` field for placement), not an enclosure requirement. A sea animal that also needs rock in its aquarium will have `rock_icons: 1` *and* `"sea-animal"` in `categories`.

## Tag fields

`abilities`, `requires`, `provides`, `triggers` each draw from the closed vocabulary in [`ABILITIES.md`](./ABILITIES.md). Each tag must be defined there before it can appear in a row. The validator enforces this.

The semantics differ by tag-field role:
- `abilities` — ability keywords printed on the card itself (e.g. `sprint`, `venom`, `inventive`). Animal-category icons are **not** here — they live in `categories` (see above).
- `requires` — prerequisite tags that must be satisfied to play / support / activate.
- `provides` — icons / effects the card *grants* when played (sponsor-specific).
- `triggers` — when the card's effect fires (`immediate`, `ongoing`, `end`, plus reactive triggers).

Per-type schemas document which of these roles apply to which card types.

## Design rules

1. **If a user might filter on it, it's a structured field or tag — not prose.** When a card has a mechanic that isn't yet captured structurally, extend the schema or add a tag, then re-tag affected rows.
2. **Tag vocabularies are closed.** Adding a tag means editing `ABILITIES.md` first.
3. **Enums are closed too.** Don't sneak a new `type`, `set`, or `continent` value into a row without adding it here.
4. **Nulls over omissions.** Every field is always present.
5. **Duplicates encode multiplicity** in `continents`, `abilities`, `requires`, and `provides`. Don't collapse them. (Rock / water icon counts are stored as integers, not duplicated tags.)

## Validation

`python scripts/validate.py` enforces field presence, type correctness, enum membership, tag membership, `ability_levels` / `ability_targets` key consistency, and `tier_thresholds` / `tier_rewards` length matching. Run it before committing.
