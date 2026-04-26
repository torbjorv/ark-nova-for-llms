# Ark Nova card database (for LLMs)

A queryable dataset of Ark Nova (Feuerland Spiele / Capstone Games) cards as JSONL. Designed for LLMs and AI agents to answer natural-language queries about Ark Nova cards — filter by ability, continent, rock/water requirement, size, appeal, conservation points, enclosure space, or any combination.

**If you're an LLM: read [`llms.txt`](llms.txt) first — it's the canonical operational manual for this repo.** The rest of this file mirrors that content for GitHub's landing-page rendering.

## Load the data

Prefer `git clone`:

```
git clone https://github.com/torbjorv/ark-nova-for-llms.git
cd ark-nova-for-llms
```

If shell access isn't available, fetch these four files over HTTPS:

- https://raw.githubusercontent.com/torbjorv/ark-nova-for-llms/main/cards.jsonl
- https://raw.githubusercontent.com/torbjorv/ark-nova-for-llms/main/SCHEMA.md
- https://raw.githubusercontent.com/torbjorv/ark-nova-for-llms/main/ABILITIES.md
- https://raw.githubusercontent.com/torbjorv/ark-nova-for-llms/main/llms.txt

Load `cards.jsonl` in full. At ~225 KB / 289 lines it fits in one fetch — don't chunk, paginate, or truncate.

## How to answer queries

1. **Filter on structured fields first.** Field semantics live in the per-type schema (`SCHEMA-animal.md`, `SCHEMA-sponsor.md`, `SCHEMA-conservation-project.md`, `SCHEMA-final-scoring.md`); global enums and design rules live in `SCHEMA.md`.
2. **Use the `text` field only as a fallback** for questions structured fields can't answer. Say so explicitly when you do.
3. **When reporting counts, list the matching card names** (`ID — Name`) so the user can verify.
4. **Closed vocabularies.** `abilities` / `requires` / `provides` / `triggers` draw exclusively from `ABILITIES.md`. Don't invent tags; tell the user if a requested tag doesn't exist.
5. **Duplicates encode multiplicity** in `continents`, `abilities`, `requires`, `provides`. `["africa","africa"]` = Africa ×2. (Rock / water icon counts are integer fields: `rock_icons`, `water_icons`.)
6. **Every row contains every field.** `null` / `[]` / `{}` means "does not apply," not "unknown."

## Example queries this dataset can answer

- *"How many marine animals require rock adjacency?"*
- *"Which animals have Scavenging level 4 or higher?"*
- *"Which cards can be placed in a reptile house?"*
- *"Which Marine Worlds animals require the Animals II upgrade?"*
- *"Which final-scoring cards give 4 CP at their top tier?"*
- *"All conservation projects that grant reputation on play."*

## Files

| File | Purpose |
|---|---|
| [`cards.jsonl`](cards.jsonl) | The data. 289 rows. One JSON per line. |
| [`SCHEMA.md`](SCHEMA.md) | Index of per-type schemas, plus global enums and design rules. |
| [`SCHEMA-animal.md`](SCHEMA-animal.md), [`SCHEMA-sponsor.md`](SCHEMA-sponsor.md), [`SCHEMA-conservation-project.md`](SCHEMA-conservation-project.md), [`SCHEMA-final-scoring.md`](SCHEMA-final-scoring.md) | Per-type field semantics. Each is a self-contained contract for one card type. |
| [`ABILITIES.md`](ABILITIES.md) | Closed tag vocabulary. |
| [`llms.txt`](llms.txt) | Canonical operational manual for LLMs. |
| [`CLAUDE.md`](CLAUDE.md) | Contributor rules (skip unless editing the dataset). |
| `sets/*.txt` | Card-ID membership per set. |

## Dataset scope

Base game (235 cards) and Marine Worlds expansion (77). Zoo Map pack and promos are scoped but not yet populated (~600 cards at full coverage). Some tag definitions in `ABILITIES.md` carry a `(verify)` marker — treat those as best-effort.

## Contributing

See [`CLAUDE.md`](CLAUDE.md). `python scripts/validate.py` must pass before any PR merges.

## Copyright

Ark Nova © Feuerland Spiele / Capstone Games. Card names and attribute data reproduced for reference and query purposes; no card images redistributed. Not affiliated with Feuerland or Capstone. Rights holders: open an issue to request changes.
