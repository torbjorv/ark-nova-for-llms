# Tag Vocabulary

Closed vocabulary for the `abilities`, `requires`, `provides`, and `triggers` arrays in `cards.jsonl`. Every tag used in the data must be defined here, with a one-line definition. `scripts/validate.py` enforces this.

When authoring a card that needs a tag not listed here, **add the tag here first**, with its definition, before using it in `cards.jsonl`. The purpose is to keep every filterable semantic explicit and stable across the dataset.

Format: `` `tag-name` — definition ``. Tags use `kebab-case`.

---

## `abilities` — intrinsic qualities of a card

Starter set. Extend as you encounter new abilities while authoring. Verify each against the real card text.

- `predator` — The animal is a predator (as indicated by the predator icon).
- `herbivore` — Explicitly marked herbivore.
- `large-animal` — Size category marked "large" (size 4+).
- `small-animal` — Size category marked "small" (size 1).
- `bird` — The card depicts a bird / has the bird grouping.
- `reptile` — The card depicts a reptile / has the reptile grouping.
- `primate` — Primate grouping.
- `nocturnal` — Nocturnal trait.
- `social` — Group/swarm animal (multiple individuals per tile).
- `petting-zoo` — Eligible for the petting-zoo enclosure.

## `requires` — prerequisites to play or place the card

- `rock-adjacent-enclosure` — Must be placed in an enclosure adjacent to rock terrain.
- `water-adjacent-enclosure` — Must be placed in an enclosure adjacent to water terrain.
- `large-aquarium` — Requires the large aquarium special enclosure.
- `small-aquarium` — Requires the small aquarium special enclosure.
- `reptile-house` — Requires the reptile house special enclosure.
- `aviary` — Requires the aviary special enclosure.
- `petting-zoo-enclosure` — Requires the petting-zoo special enclosure.

## `provides` — effects the card grants

- `reputation-on-release` — Grants reputation when the animal is released (for conservation points).
- `conservation-points-on-play` — Grants conservation points when played.
- `appeal-on-play` — Grants appeal (beyond the printed appeal value) on play.
- `money-on-play` — Grants money on play.

## `triggers` — when effects fire

- `on-play` — Effect fires when the card is played.
- `on-build` — Effect fires when building (choosing the build action).
- `on-release` — Effect fires when the card is released.
- `on-snap` — Effect fires when the action card is in the "snap" slot.
- `continuous` — Ongoing effect while card is in play.

---

## Rules for extending this file

1. **One tag per bullet, one definition per tag.** No synonyms — pick one canonical tag name.
2. **Keep definitions to a single line.** If a tag needs more nuance, split it into multiple tags.
3. **If in doubt, make a new tag rather than overloading an existing one.** Over-specific tags are cheap; overloaded ones silently corrupt query results.
4. **Never remove or rename a tag without re-tagging every row that uses it.** The validator will fail and tell you exactly where.
