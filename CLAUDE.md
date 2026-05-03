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
- `source_data/arknovaanimals_VM_v2.xlsx` — community-maintained structured spreadsheet (Animals / Sponsors / Conservation / Final Scoring sheets). Historical: was the source the deprecated build pipeline read from. Reference only — `cards.jsonl` is now hand-edited; when in conflict with the printed cards, the cards win.
- `source_data/AN_Cards_E_Front_Low1.pdf`, `source_data/AN_Cards_E_Front_Low2.pdf`, `source_data/AN_Exp_1_AllCards_EN.pdf` — official front-faces PDFs (138 + 107 + 111 pages). Source of every per-card image under `source_data/card_images/`.

## Card images

`source_data/card_images/` holds one PNG per card, named `<id>.png` (`AN-001.png`, `MW-529.png`, …) at 1439×2010 px (~580 DPI), extracted from the official front-faces PDFs above. Use these when a question requires visual confirmation that the structured fields can't resolve (which icons are illustrated on a card, exact printed wording, layout details).

- **Top level (313 files)** — one image per card, full coverage of every id in `cards.jsonl`.
- `action_cards/` (60 files) — player action cards (BUILD / CARDS / ANIMALS / SPONSORS / ASSOCIATION). Not in `cards.jsonl`. Named `an-<action>-L{1,2}.png` for the 10 base-game cards and `mw-<action><variation>-L{1,2}.png` for the 50 marine cards (variation `0` is the marine reprint of base L1/L2 with the seahorse marker; variations `1`–`4` are alternate upgrades introduced by Marine Worlds).
- `_extract_log.jsonl` — per-file provenance log: source PDF page → assigned id, plus reprint-copy notes. `cards.jsonl` is the source of truth; this log is reference only.

**Known reprint pairs.** 17 AN/MW pairs are visually identical and share a single physical card; the MW image is a copy of the AN image:

- Conservation projects: `MW-{001, 003, 005, 008, 009, 010, 011}` ↔ `AN-{001, 003, 005, 008, 009, 010, 011}`
- Final scoring: `MW-{101, 102, 131}` ↔ `AN-{101, 102, 131}`
- Sponsors: `MW-{207, 208, 225, 226, 227, 250, 261}` ↔ `AN-{207, 208, 225, 226, 227, 250, 261}`

If a real visual difference is ever found on one of these (e.g. a wave icon present on only the MW print), update `cards.jsonl` accordingly and split the images.

## Iconography

Reading card images is unreliable without the iconography rules. The two most common reading mistakes — confusing **conservation points** with **appeal**, and confusing the **always-fires bonus** with a **per-tier bonus** on conservation projects — both come from misreading the icon shape/colour. Internalize these before encoding any value off an image.

**Reward icons (the numbers printed on a small shape inside reward strips):**

| Icon | Meaning |
|---|---|
| Green/white pentagon shield, leaf motif | **Conservation point (CP)**. End-game / final scoring currency. The most common reward icon on the bottom-right of conservation-project tier strips and on final-scoring cards. |
| Brown/orange rounded ticket (lozenge) | **Appeal**. Immediate / track-currency icon on sponsors, animals, and the bottom-right of most sponsor cards (the "appeal value of this card"). |
| Yellow/gold coin | **Money** (`$`). |
| Cyan/teal heart-with-wreath | **Reputation**. |
| Purple "X" hexagon | **X-token**. |

The shape, not the number, identifies the currency. A "1" on a green shield is `1 CP`; a "1" on a brown ticket is `1 Appeal`. They are not interchangeable, even when the printed number is the same.

**Trigger / timing icons (left margin of an effect line):**

| Icon | Meaning |
|---|---|
| Yellow lightning bolt | **Immediate** — fires once when the card is played or supported. |
| Yellow infinity / arrow loop | **Ongoing trigger** — fires every time the printed condition occurs (`Each time …`). |
| Green hourglass | **End of game** — counted/scored once at game end. |
| Blue wave (Marine Worlds only) | **Wave trigger** — fires when a sea-animal icon enters the relevant zoo. Encoded as `wave_icon: true` on the card. |

**Conservation-project structural reminder.** A conservation-project card has up to two distinct bonus areas:
- A small icon next to the title strip = the **always-fires** card-wide bonus (`bonus_reward` field). On release projects this is typically `1 reputation`. On management plans it is usually `null`.
- The leftmost (top-tier) reward cell can carry an **extra** per-tier bonus next to its CP value (e.g. tier-1 reef-trigger on `MW-138`). That extra lives inside `tier_rewards[0]`, not in `bonus_reward`. The two coexist; one does not replace the other.

When a value is ambiguous from the image, fall back to the manual PDFs (the rulebook spells out reward currencies in terms of these icons) before guessing.

## Validation

- `scripts/validate.py` — enforces field presence, types, enum membership, tag membership, `ability_levels` / `ability_targets` key consistency, and `tier_thresholds` / `tier_rewards` length matching. **Run before every commit.** CI should fail otherwise.
- `scripts/build_cards.py` — **deprecated.** Historically rebuilt `cards.jsonl` from the spreadsheet. `cards.jsonl` is now edited directly; the script is kept in-tree as historical reference and should not be run.

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
- `cards.jsonl` — hand-edit and rerun `validate.py`.
- **`llms.txt`** — column tables (scalar + JSON-typed), enum block, idioms, and any example queries that reference the changed name. `llms.txt` is the canonical operational manual every LLM consumer reads; drift here means every Claude in the wild writes broken SQL against this dataset. `README.md` only points at `llms.txt`, so it rarely needs an edit, but check it anyway.

After the edit, sanity-check by running the example queries near the top of `llms.txt` through `python scripts/query.py` — they must succeed against the updated `cards.jsonl`. If `llms.txt` documents a column name, `cards.jsonl` must have it; if `cards.jsonl` has a column, `llms.txt` must document it.

## Querying

End-user query guidance lives in `README.md` and `llms.txt` (the latter is the canonical operational manual for LLM consumers; `README.md` mirrors it for the GitHub landing page).

**When the user asks a question about the cards, answer it by running `python scripts/query.py "<SQL>"` rather than by grepping `cards.jsonl` or reading it directly.** The script loads the JSONL into an in-memory SQLite table named `cards` and returns JSONL on stdout. Read `llms.txt` for the column list, JSON-field idioms (`json_each`, `json_extract`), and enum values — it is self-sufficient on the schema. Fall back to `grep` / direct reads only when SQL genuinely cannot express the question (e.g. free-text searches inside `text` are fine in SQL via `LIKE`, so this is rare).
