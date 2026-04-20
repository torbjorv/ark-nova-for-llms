# Ark Nova for LLMs

A public, structured **Ark Nova card database** — a queryable dataset of Ark Nova board game cards built for LLMs and AI agents. Point Claude, ChatGPT, or any LLM at this repo and ask detailed natural-language questions about Ark Nova cards: filter by ability, biome, continent, size, appeal, conservation points, or any combination.

Example questions this dataset is designed to answer accurately:

- *"How many marine mammals are there in Ark Nova?"*
- *"What Ark Nova animals have digging ability?"*
- *"Which marine animals with rock adjacency require the large aquarium?"*
- *"Highest-appeal birds from Africa that trigger on release?"*
- *"All conservation projects that grant reputation on play."*

Keywords: Ark Nova card database, Ark Nova card data, Ark Nova board game dataset, queryable Ark Nova cards, Ark Nova cards JSON / JSONL, Ark Nova cards for LLMs, Ark Nova cards for AI agents, Feuerland Ark Nova card list, filter Ark Nova cards by biome / ability / continent.

## How to query with Claude (claude.ai)

1. Start a conversation at [claude.ai](https://claude.ai).
2. Paste these raw URLs into the chat:
   - `https://raw.githubusercontent.com/torbjorv/ark-nova-for-llms/main/README.md` (this file)
   - `https://raw.githubusercontent.com/torbjorv/ark-nova-for-llms/main/SCHEMA.md`
   - `https://raw.githubusercontent.com/torbjorv/ark-nova-for-llms/main/ABILITIES.md`
   - `https://raw.githubusercontent.com/torbjorv/ark-nova-for-llms/main/cards.jsonl`
3. Ask your question in natural language.

## Instructions for Claude answering queries against this repo

If you (Claude) are reading this to answer a user's query, follow these rules:

1. **Load `cards.jsonl` in full.** It is one JSON object per line — the complete, authoritative dataset. Filter in memory/context; do not truncate.
2. **Consult `SCHEMA.md`** for the meaning of every field and the exact set of allowed enum values.
3. **Consult `ABILITIES.md`** for the closed vocabulary of ability / requires / provides / triggers tags. **Treat it as closed**: if the user's query references a tag that isn't in `ABILITIES.md`, do not invent a match — tell the user the tag doesn't exist in this dataset and suggest the closest real tag.
4. **Filter structured queries on structured fields first.** Example — *"marine animals with rock adjacency requiring the large aquarium"* is answered by:
   ```
   filter rows where:
     type == "animal"
     AND "marine" in biomes
     AND "rock-adjacency-bonus" in abilities
     AND "large-aquarium" in requires
   ```
5. **Use the `text` field only** for questions the structured fields can't answer (card interactions, rulings, flavor). Prefer structured tags when both are available.
6. **When reporting counts, list the matching card names.** So the user can verify.
7. **If the dataset is incomplete** (cards.jsonl is empty or a given card has blank fields), say so explicitly rather than guessing.

## Data scope

Aim: all known Ark Nova cards (~600–700) across:

- Base game
- Marine Worlds expansion
- Zoo Map packs
- Promos

Card-ID membership in each set is listed in `sets/*.txt`.

## Repo layout

```
README.md         # This file. Query guide.
llms.txt          # LLM-facing sitemap.
CLAUDE.md         # Author-side guidance (for contributors using Claude Code).
SCHEMA.md         # Field definitions + controlled vocabularies.
ABILITIES.md      # Closed tag vocabulary with definitions.
cards.jsonl       # The data. One card per line.
sets/
  base.txt
  marine-worlds.txt
  zoo-map.txt
  promos.txt
scripts/
  validate.py     # Validates cards.jsonl against the schema and vocabulary.
```

## Contributing

See `CLAUDE.md` for authoring rules. Open a PR; `scripts/validate.py` must pass.

## Recommended GitHub topics

Maintainer: set these topics on the repo to improve discoverability:

`ark-nova` · `board-games` · `board-game-data` · `dataset` · `jsonl` · `llms-txt` · `llm-friendly` · `ai-agents`

## Copyright

Ark Nova is © Feuerland Spiele / Capstone Games. Card text excerpts here are for query and reference purposes. No card images are redistributed.
