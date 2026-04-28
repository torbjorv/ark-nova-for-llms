# Ark Nova Card Database

Structured data for Ark Nova board game cards, optimized for querying by Claude.

## Data and schema

- `cards.jsonl` — one card per line, all structured fields + full text. This is the data.
- `SCHEMA.md` — index, global enums (`games`, `type`, `icons`), the rock/water icon convention, design rules.
- `SCHEMA-animal.md`, `SCHEMA-sponsor.md`, `SCHEMA-conservation-project.md`, `SCHEMA-final-scoring.md` — per-type field semantics. Each lists both the fields applicable to that type and the fields that are constant (always null/empty) on that type, so the contract for one card type can be reviewed in isolation.
- `ABILITIES.md` — the closed vocabulary of ability / requires / triggers tags, each with a one-line definition.

## Authoritative sources

When in doubt about a card's text, an icon's meaning, or a rules edge case, consult these before guessing. The PDFs are scanned/searchable rulebooks; the spreadsheet is the structured-data master that `cards.jsonl` is built from.

- `source_data/Manual - Ark Nova.pdf` — official base-game rulebook. Authoritative for terminology and rules.
- `source_data/Manual - Marine expansion.pdf` — official Marine Worlds rulebook. Authoritative for wave-trigger, reef-ability, aquarium / large-reptile-house, and Sea Animal mechanics.
- `source_data/arknovaanimals_VM_v2.xlsx` — community-maintained structured spreadsheet (Animals / Sponsors / Conservation / Final Scoring sheets). The build pipeline reads this; the column "Enclosure size (Rock/Water)" is the source for `rock_icons` / `water_icons` / `*_size` fields. Does not include card text.

## Build and validation pipeline

- `scripts/build_cards.py` — rebuild `cards.jsonl` from the spreadsheet. Animal text is derived from spreadsheet ability columns; sponsor / project / final-scoring text is assembled from spreadsheet effect columns. Hand-written text in the existing `cards.jsonl` is **not** preserved across rebuilds.
- `scripts/validate.py` — enforces field presence, types, enum membership, tag membership, `ability_levels` / `ability_targets` key consistency, and `tier_thresholds` / `tier_rewards` length matching. **Run before every commit.** CI should fail otherwise.

## Adding or editing cards

1. Read `SCHEMA.md`, the matching per-type schema for the card you're touching, and `ABILITIES.md` first — they define the contract.
2. Every row must include every field in the schema. Use `null` or `[]` / `{}` / `0` where a field doesn't apply; never omit.
3. If you find yourself needing a tag that isn't in `ABILITIES.md`, **add it to `ABILITIES.md` with a one-line definition before using it** — don't encode new semantics only in `text`. The guiding rule: if a user might ever filter on it, it's a tag, not prose.
4. When in doubt about a card's printed text or icon meaning, check the manual PDFs in `source_data/`.
5. Run `python scripts/validate.py` before committing. CI should fail otherwise.

## Changing the schema

Renaming or adding/removing a column, changing a JSON shape, changing an enum value, or adding/renaming a tag is a **schema change**, not a data edit. Every schema change must update all of the following in the same commit:

- `SCHEMA.md` and the affected per-type schema (`SCHEMA-animal.md` / `SCHEMA-sponsor.md` / `SCHEMA-conservation-project.md` / `SCHEMA-final-scoring.md`).
- `ABILITIES.md` if a tag is added, removed, or renamed.
- `scripts/validate.py` — column list (`REQUIRED_FIELDS`), enums (`SET_ENUM` / `TYPE_ENUM` / `ICON_ENUM`), and per-field checks.
- `scripts/build_cards.py` — so the next rebuild emits the new shape.
- `cards.jsonl` — rebuild via `build_cards.py` (or hand-edit) and rerun `validate.py`.
- **`llms.txt`** — column tables (scalar + JSON-typed), enum block, idioms, and any example queries that reference the changed name. `llms.txt` is the canonical operational manual every LLM consumer reads; drift here means every Claude in the wild writes broken SQL against this dataset. `README.md` only points at `llms.txt`, so it rarely needs an edit, but check it anyway.

After the edit, sanity-check by running the example queries near the top of `llms.txt` through `python scripts/query.py` — they must succeed against the rebuilt `cards.jsonl`. If `llms.txt` documents a column name, `cards.jsonl` must have it; if `cards.jsonl` has a column, `llms.txt` must document it.

## Querying

End-user query guidance lives in `README.md` and `llms.txt` (the latter is the canonical operational manual for LLM consumers; `README.md` mirrors it for the GitHub landing page).

**When the user asks a question about the cards, answer it by running `python scripts/query.py "<SQL>"` rather than by grepping `cards.jsonl` or reading it directly.** The script loads the JSONL into an in-memory SQLite table named `cards` and returns JSONL on stdout. Read `llms.txt` for the column list, JSON-field idioms (`json_each`, `json_extract`), and enum values — it is self-sufficient on the schema. Fall back to `grep` / direct reads only when SQL genuinely cannot express the question (e.g. free-text searches inside `text` are fine in SQL via `LIKE`, so this is rare).
