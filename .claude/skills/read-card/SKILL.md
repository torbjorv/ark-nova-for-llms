---
name: read-card
description: "Use this skill whenever interpreting an Ark Nova card image (file under `source_data/card_images/<id>.png`) — verifying printed text, identifying which icons are illustrated, resolving ambiguity that `cards.jsonl` can't answer, or transcribing a card onto a row. Loads the iconography rules (card frame, reward / cost / trigger icons, ability icons, conservation-project bonus structure, Marine Worlds extensions) needed to read images correctly."
context: fork
agent: Explore
---

## Setup
- Read card image file from source_data/card_images/<id>.png, this should be your ONLY input.
- Full schema for output in the ./SCHEMA*.md files.
- Do NOT read cards.jsonl

## Identifying card type

Every card has a horizontal banner across the center of the card with the card's name in the centre — the **title bar**. The title bar's **background colour* is the fastest type discriminator, more reliable than scanning for icons on the body:

| Title-bar background | Card type |
|---|---|
| Orange | **Animal** (`type: "animal"`) | 
| Blue | **Sponsor** (`type: "sponsor"`) | 
| Green | **Conservation project** (`type: "conservation-project"`) |
| Brown/tan | **Final scoring** (`type: "final-scoring"`) | 

## Iconography

| Iconography | Meaning |
|---|---|
| Green/white shield with number | **Conservation point (CP)**. |
| Light Brown ticket (rectangle with notches top and bottom) with black number printed | **Appeal**. | `appeal`. |
| White number on a **gray rounded square with white border** | **Money** (`$`). |
| Black diamond with white number inside | **Reputation**. |
| Black X with small white dots | **X-token**. |
| 3D Cube | **Marker** |
| Lightning bolt | Indicates an immediate effect when the card is played. Card sections with yellow background is a second indicator that this is an immediate effect. |
| Hourglass (often on a brown/tan card section) | **End of game** — counted/scored once at game end. |
| Open hand | **Income phase** — fires during the income/break phase (a flavour of `ongoing`). |
| Blue wave (Marine Worlds only). Always located center right on the card. | **Wave trigger** — fires when a sea-animal icon enters the relevant zoo. | `wave_icon: true` |
| Small Sea Horse silhouette | Card is part of the Marine Expansion |
| Number on a coloured square with a jagged / saw-tooth left edge | Action strength or position |
| Circle with drawing inside | Called an "icon" in the game terminology, see specific types below |
| Bear silhouette, black on white | Bear icon|
| Big cat silhouette, white on read | Predator icon|
| Gazelle silhouette, white on green | Herbivore icon|
| Gorilla silhouette, white on orange| Primate icon|
| Lizard silhoutte, white on purple| Reptile icon|
| Bird silhouette, white on light blue| Bird icon|
| Goat silhouette, black on white| Pet icon|
| Octopus silhouete, white on dark blue| Sea Animal icon|
| Europe, black on light blue| Europe icon|
| Asia, black on light green | Asia icon|
| Africa, black on yellow| Africa icon|
| Americas, black on orange| Americas icon|
| Australia, black on red| Australia icon|
| Hexagon tile, brown with white inside | Enclosure size requirement |
| Blue rectangle with @ symbol | sponsor card reference (does not imply that the card itself is a sponsor card) |
| Microscope silhouette, teal background | Science icon | 
| Parallellogram, brown background with white rock, white border | rock icon|
| Parallellogram, blue background with white water drop, white border | water icon |
| Card with brown hexagon, white "4+" inside | Large animal (size 4 or 5) |
| Card with brown hexagon, white "3" inside | Medium animal (size 3) |
| Card with brown hexagon, white "2-" inside | Small animal (size 1 or 2) |
| Hexagon with yellow background, red border, red hand inside | Pilfering ability |
| Hexagon with yellow background, red border, red snake head silhouette | Venom ability |
| Hexagon with yellow background, red border, red snake in a tree | Constriction ability |
| Hexagon with yellow background, red border, red frontal snake head | Hypnosis ability |
| White hexagon with black pavillion silhouette | Pavillion |
| Red branch/coral/tree-shape on white background | Reef ability trigger. Another icon is often displayed on top, indicating _which_ ability is triggered by the reef |


Multiplicity is critical and may be encoded as requirements, icons or other relevant fields. An animal with two primate icons is `["primate","primate"]`; a sponsor granting two science icons is `["science","science"]`.

## Six enclosure-size fields on animal cards

The `cards.jsonl` schema carries six per-enclosure size fields; populate the one whose icon appears next to the size number:

| Field | Enclosure type | Visual cue near the size dot |
|---|---|---|
| `standard_size` | Standard enclosure (default for most land animals). | Hexagon, brown fill, white border, white number for size requirement |
| `reptile_house_size` | Reptile House | Dog-bone shaped, white border, brown fill, white number indicating reptile house size requirement |
| `large_bird_aviary_size` | Large Bird Aviary | Dome/umbrella shape, white border, brown fill, white number for size requirement |
| `petting_zoo_size` | Petting Zoo | Curve-shaped (three connected hexagons), white border, brown fill, white number for size requirement |
| `aquarium_size` | Aquarium | Several blue connected hexagons, white outline, white number for size requirement |

Most animals populate exactly one of these; some animals can be in either aquarium or reptile house. 

## Animal-card body anatomy (where to look)

Going clockwise around the card frame:

- **Card centre (horizontal title bar)** — card name
- **Top-left** - action strength, money cost, requirements, animal size
- **Top-right** — Animals, continents, science etc, encoded in the "icons" array.
- **Top-right, below icons** — Sea animals _may_ have have a reef icon, indicating a reef trigger.
- **Lower half** - abilities, card behavior/description, rewards, effects, explanations
- **Center left (on the title bar)** - a small sea horse silhoutte for Marine Expansion cards
- **Center right (on the title bar)** - a number, vertically printed, indicating card ID
- **Center right (below the title bar)** - wave icon (only for some Marine Expansion cards)
- **Center right (above the title bar)** - venom/constriction/hypnosis/pilfering icons
- **Bottom-left** — sometimes a `reputation_requirement` icon (the cyan heart-with-wreath) printed as the cost to play.
- **Bottom-right** — appeal value (brown ticket). Below it, sometimes a **conservation-points** value (green shield) — small green-shield value on the bottom-right of an animal card means the animal scores extra CP at game end.
- **Bottom-right (small grey rounded square with white border)** — **money cost** to play this animal as a build action.

## Sponsor-card body anatomy

- **Top-left** — required strength
- **Card centre (horizontal title bar)** — card name
- **Top-right (or middle of body)** — granted icons (`icons` array). Multiplicity by duplication.
- **Body/bottom half** — effect rows with trigger icons in the left margin. Yellow rows = immediate / ongoing; brown rows = end-of-game.

## Conservation-project body anatomy and bonus structure

A conservation-project card has up to **two distinct bonus areas** — don't conflate them:

- **Top left** - requirement
- **Bottom right** - card bonus
- **Card centre (horizontal title bar)** — card name
- **Lower half** - tiered thresholds and rewards. Typically two or three horizontal rows of icons. Top row indicates thresholds, bottom row indicates rewards.

## Final-scoring body anatomy

- **Top left** - Hourglass (to indicate card type) and requirement
- **Card centre (horizontal title bar)** — card name
- Body lists the category being scored (e.g. "Large Animal Zoo") and a tier ladder. Reward icons are CP (green shield).
- The category being scored is captured in `name` and `text`, not as a structured filter.
- **Lower half** - tiered thresholds and rewards. Two rows, top row indicates thresholds, bottom row indicates rewards (always CP).

## Animal-ability icons

Each animal can carry one or more **ability icons** in its body. The icon is a small badge (often coloured to indicate keyword family) with the ability's name spelled out next to it on the printed card. This is why the closed `abilities` vocabulary in `ABILITIES.md` mostly mirrors the printed names. When transcribing, encode the keyword in `abilities`; if the ability has a printed level (e.g. *Hunter 1*, *Sprint 2*), put the integer in `ability_levels` keyed by the keyword. If the ability targets a specific sub-type (e.g. *Iconic Animal: Europe*, *Magnet: sponsors*), put the target in `ability_targets`.

The full closed list of ability keywords is in `ABILITIES.md`. The most common ones, with the visual cue or rule reminder you'd use to confirm them off an image:

## Alternative-ability box

A few animals print a smaller, blue box **below** at the bottom of the card, this is the *alternative ability*. 
