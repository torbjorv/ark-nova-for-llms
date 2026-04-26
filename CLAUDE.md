# Ark Nova Card Database

Structured data for Ark Nova board game cards, optimized for querying by Claude.

## Source of truth

- `cards.jsonl` — one card per line, all structured fields + full text. This is the data.
- `SCHEMA.md` — index, global enums (`set`, `type`, `continents`), the rock/water icon convention, design rules.
- `SCHEMA-animal.md`, `SCHEMA-sponsor.md`, `SCHEMA-conservation-project.md`, `SCHEMA-final-scoring.md` — per-type field semantics. Each lists both the fields applicable to that type and the fields that are constant (always null/empty) on that type, so the contract for one card type can be reviewed in isolation.
- `ABILITIES.md` — the closed vocabulary of ability / requires / provides / triggers tags, each with a one-line definition.

## Adding or editing cards

1. Read `SCHEMA.md`, the matching per-type schema for the card you're touching, and `ABILITIES.md` first — they define the contract.
2. Every row must include every field in the schema. Use `null` or `[]` where a field doesn't apply; never omit.
3. If you find yourself needing a tag that isn't in `ABILITIES.md`, **add it to `ABILITIES.md` with a one-line definition before using it** — don't encode new semantics only in `text`. The guiding rule: if a user might ever filter on it, it's a tag, not prose.
4. Run `python scripts/validate.py` before committing. CI should fail otherwise.

## Querying

End-user query guidance lives in `README.md` (that's the file claude.ai users will fetch first).
