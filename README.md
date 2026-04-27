# Ark Nova card database (for LLMs)

A queryable dataset of [Ark Nova](https://boardgamegeek.com/boardgame/342942/ark-nova) (Feuerland Spiele / Capstone Games) cards as JSONL, with a small SQL helper. Designed so an LLM agent can answer natural-language questions about the cards — by ability, continent, rock/water requirement, size, appeal, conservation points, enclosure space, or any combination.

**If you're an LLM agent: read [`llms.txt`](llms.txt) — it's the operating manual.**

## What's in here

`cards.jsonl` holds one JSON object per card with structured fields and verbatim text. [`scripts/query.py`](scripts/query.py) wraps it in an in-memory SQLite table called `cards` and runs SQL queries, returning JSONL on stdout. Together that's enough for an agent to answer questions like:

- *"Which Marine Worlds animals require the Animals II upgrade?"*
- *"Which animals have Scavenging level 4 or higher?"*
- *"Which final-scoring cards give 4 CP at their top tier?"*
- *"All conservation projects that grant reputation on play."*

The full SQL schema and query idioms live in [`llms.txt`](llms.txt); the closed-vocabulary tag dictionary lives in [`ABILITIES.md`](ABILITIES.md).

## Scope

Base game (235 cards) and Marine Worlds expansion (77). Zoo Map pack and promos are scoped but not yet populated (~600 cards at full coverage). Tags marked `(verify)` in `ABILITIES.md` are best-effort.

## Contributing

See [`CLAUDE.md`](CLAUDE.md). `python scripts/validate.py` must pass before any PR merges.

## Copyright

Ark Nova © Feuerland Spiele / Capstone Games. Card names and attribute data reproduced for reference and query purposes; no card images redistributed. Not affiliated with Feuerland or Capstone. Rights holders: open an issue to request changes.
