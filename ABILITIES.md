# Tag Vocabulary

Closed vocabulary for the `abilities`, `requires`, `provides`, and `triggers` arrays in `cards.jsonl`. Every tag used in the data must be defined here, with a one-line definition. `scripts/validate.py` enforces this.

This vocabulary was bootstrapped from the class tokens in the [ssimeonoff Ark Nova cards page](https://github.com/ssimeonoff/ssimeonoff.github.io/blob/master/ark-nova.html). Tags that are icons/keywords on actual cards (as opposed to metadata flags) are grouped for readability. **Some definitions are best-effort and marked `(verify)` — they should be confirmed against the real card text before the dataset is considered authoritative.** When in doubt, read the printed card.

Format: `` `tag-name` — definition ``. Tags use `kebab-case`.

---

## Continent icons

Used in `abilities` to record a continent icon on the card, and in `requires` / `provides` when another card needs or grants such an icon.

- `africa` — Africa continent icon.
- `americas` — Americas continent icon.
- `asia` — Asia continent icon.
- `europe` — Europe continent icon.
- `australia` — Australia continent icon.

## Biome icons

Used in `requires` / `provides` for rock- or water-icon thresholds printed on sponsor cards and elsewhere.

- `water` — water habitat icon (see also the `biomes` field on the card).
- `rock` — rock habitat icon.

## Animal group icons

Tags that indicate the printed "group" icon(s) on an animal or project card.

- `ape` — primate / ape group icon.
- `bear` — bear group icon.
- `bird` — bird group icon.
- `herbivore` — herbivore icon (animals marked as herbivores).
- `lizard` — reptile group icon (generally called "lizard" in the source; covers reptiles).
- `marine` — marine / aquarium group icon (Marine Worlds marine animals).
- `pet` — petting-zoo animal icon (eligible for the petting-zoo enclosure).
- `predator` — predator icon (animals marked as predators).

## Card-has-value flags

Tags used to mark that a card carries a particular scoring or cost icon. The numeric value itself is stored in the corresponding structured field (`appeal`, `conservation_points`, etc.) when known; these flags survive even when the numeric value hasn't been filled in yet.

- `ap` — card has a printed appeal value.
- `cp` — card has a printed conservation-points value.
- `rep` — card has a printed reputation cost or reputation reward.
- `l2` — card has a "release value 2" icon (higher release reward). (verify)
- `science` — card has the science icon.

## Sponsor timing

- `immediate` — effect resolves immediately when the sponsor is played.
- `ongoing` — effect is ongoing while the sponsor is in play.
- `end` — effect resolves at end of round / end of game.

## Sponsor effect categories

Best-effort labels from the source — these describe what kind of effect a sponsor has.

- `income` — sponsor provides money income. (verify)
- `special` — sponsor has a one-off / specialised effect. (verify)
- `max25` — sponsor related to a 25-cap mechanic. (verify)
- `expedition` — expedition-related sponsor. (verify)

## Enclosure / structure requirements

- `aviary` — requires (or interacts with) the aviary special enclosure.
- `petting` — relates to the petting-zoo enclosure (the ability, distinct from the `pet` group icon).

## Threshold requirements

- `reputation` — in `requires`: card has a minimum reputation-track threshold to play. The specific number, when known, goes in `reputation_requirement`; use this tag for cards whose threshold is printed but not yet captured numerically.
- `partner-zoo` — in `requires`: card requires a partner zoo to play.
- `animals-ii` — in `requires`: card requires the level-II animal-action upgrade.
- `level-ii-sponsor` — in `requires`: card requires the level-II sponsor-action upgrade.
- `university` — in `requires`: card requires a university in the zoo.
- `kiosk` — in `requires`: card requires a kiosk in the zoo.
- `max-25-appeal` — in `requires`: card can only be played when appeal is ≤ 25.
- `release-activity` — in `requires`: conservation project is resolved via the Release activity.
- `partnership-activity` — in `requires`: conservation project is resolved via the Partnership activity.
- `collection-activity` — in `requires`: conservation project is resolved via the Collection activity.

## Activity triggers

- `on-release` — triggers when an animal is released into the wild.
- `on-partnership` — triggers when a partnership is formed.

## Sub-type vocabulary (for `ability_targets`)

These strings appear as values in the `ability_targets` map, pairing with parameterised ability tags like `multiplier`, `boost`, `action`, `iconic`, `magnet`.

- `association` — the Association action card.
- `sponsors` — sponsor cards.
- `cards` — general card / deck interactions.
- `build` — the Build action card.
- `animals` — generic "animals" target.
- `africa`, `americas`, `asia`, `europe`, `australia` — continent sub-types (e.g. `iconic`: `europe` = Iconic Animal: Europe).
- `sea-animal` — marine-animal sub-type (for Sea Animal Magnet, etc.).

## Ability keywords (animal cards)

The icon / keyword printed on an animal card that drives its special effect. Most of these correspond to named abilities in the game; definitions here are best-effort and should be confirmed against card text.

- `action` — grants or relates to the action mechanic. (verify)
- `adapt` — adaptation ability (Marine Worlds). (verify)
- `assertion` — territorial / assertive animal ability. (verify)
- `boost` — boost ability (cards or resources). (verify)
- `camouflage` — camouflage ability. (verify)
- `clever` — clever / cunning animal ability. (verify)
- `constriction` — constriction ability (constrictor snakes). (verify)
- `cut-down` — "cut-down" ability. (verify)
- `determination` — determination ability. (verify)
- `digging` — digging ability (burrowing animals).
- `dominance` — dominance ability. (verify)
- `extra-shift` — grants an extra shift action. (verify)
- `flock` — flock ability (interacts with other birds / group animals).
- `full-throated` — loud / vocalising animals ability. (verify)
- `glide` — glide ability (gliding animals). (verify)
- `helpful` — "helpful" ability. (verify)
- `hunter` — hunter ability.
- `hypnosis` — hypnosis ability. (verify)
- `iconic` — iconic-animal ability. (verify)
- `inventive` — inventive / tool-use ability. (verify)
- `jumping` — jumping ability.
- `magnet` — magnet / attractor ability. (verify)
- `marketing` — marketing ability. (verify)
- `multiplier` — multiplier ability (scales another value). (verify)
- `pack` — pack ability (synergises with other pack animals).
- `peacocking` — display / peacocking ability. (verify)
- `perception` — perception / senses ability. (verify)
- `pilfering` — pilfering / stealing ability. (verify)
- `posturing` — posturing / threat-display ability. (verify)
- `pouch` — marsupial pouch ability.
- `reef` — reef ability (Marine Worlds).
- `resistance` — resistance / toughness ability. (verify)
- `scavenging` — scavenger ability.
- `scuba-dive` — scuba-dive ability (Marine Worlds).
- `shark-attack` — shark-attack ability (Marine Worlds).
- `snapping` — snapping-attack ability. (verify)
- `sprint` — sprint ability.
- `sunbathing` — sunbathing ability.
- `symbiosis` — symbiosis ability (Marine Worlds).
- `trade` — trade ability. (verify)
- `venom` — venom / venomous ability.
- `wave` — wave icon (Marine Worlds reef/ocean interaction). (verify)
- `monkey-gang` — monkey-gang ability (Marine Worlds primates). (verify)
- `cut-down` — cut-down ability (Marine Worlds). (verify)
- `mark` — mark-another-card ability (Marine Worlds). (verify)
- `extra-shift` — grants an extra shift action (see also top-level `extra-shift`).
- `sea-animal-magnet` — sea-animal variant of the magnet ability (Marine Worlds). (verify)
- `sponsor-magnet` — sponsor variant of the magnet ability. (verify)
- `no-ability` — explicit placeholder on cards whose ability column is `none` / empty by design.

---

## Rules for extending this file

1. **One tag per bullet, one definition per tag.** No synonyms — pick one canonical tag name.
2. **Keep definitions to a single line.** If a tag needs more nuance, split it into multiple tags.
3. **If in doubt, make a new tag rather than overloading an existing one.** Over-specific tags are cheap; overloaded ones silently corrupt query results.
4. **Never remove or rename a tag without re-tagging every row that uses it.** The validator will fail and tell you exactly where.
5. **Replace `(verify)` markers with confirmed definitions** as you read the actual card text. Unverified definitions are placeholders — queries that rely on them may silently miss matches.
