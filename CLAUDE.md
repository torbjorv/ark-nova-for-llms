# Ark Nova Card Database

Structured data for Ark Nova board game cards, optimized for querying by Claude.

## Source of truth

- `cards.jsonl` — one card per line, all structured fields + full text. This is the data.
- `SCHEMA.md` — every field's name, type, semantics, and controlled-vocabulary enum values.
- `ABILITIES.md` — the closed vocabulary of ability / requires / provides / triggers tags, each with a one-line definition.

## Adding or editing cards

1. Read `SCHEMA.md` and `ABILITIES.md` first — they define the contract.
2. Every row must include every field in the schema. Use `null` or `[]` where a field doesn't apply; never omit.
3. If you find yourself needing a tag that isn't in `ABILITIES.md`, **add it to `ABILITIES.md` with a one-line definition before using it** — don't encode new semantics only in `text`. The guiding rule: if a user might ever filter on it, it's a tag, not prose.
4. Run `python scripts/validate.py` before committing. CI should fail otherwise.

## Querying

End-user query guidance lives in `README.md` (that's the file claude.ai users will fetch first).
