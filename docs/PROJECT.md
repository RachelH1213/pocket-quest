# Pocket Quest — project definition

The long-term memory for this project. When an important decision changes,
change it here.

## What it is

An AI-powered physical adventure game. The player reads the story on printed
receipts and chooses with physical buttons. A Raspberry Pi 5 holds the game
state and drives a thermal receipt printer.

Receipts can carry story scenes, choices, quests, clues, maps, collectible items
and other game objects. Items print as their own receipts, so the player's
inventory is a physical pile of paper.

The Raspberry Pi maintains the actual game state: current scene, inventory,
player status, progression.

## Design principles

1. **The program owns the rules.** The AI narrator does not control the game
   rules and does not change the game state. It receives structured game state
   and generates narrative content inside rules the program defines.
2. **The game works before AI exists.** It must be a complete, playable
   branching physical game before any model is added.
3. **All AI output is validated.** A harness checks structured model output
   before anything is accepted or printed.
4. **Hardware code stays separate from game logic** where practical.

## Must-have

- Raspberry Pi 5
- Thermal receipt printer
- Physical player input
- Persistent game state
- Branching choices
- Story receipts
- Item receipts / physical inventory
- One complete playable adventure
- Constrained AI narrator

## Nice-to-have — not required initially

Small display · sound · QR codes · save codes · multiple players · local AI ·
Oracle integration · D12 API · local/cloud model routing · procedural world

None of these are to be built until the must-haves are done.

## Milestones

- [x] 1. Raspberry Pi -> thermal printer -> print `POCKET QUEST / HELLO PLAYER`
- [ ] 2. Physical buttons -> Raspberry Pi -> different printed outputs
- [x] 3. Basic branching game state, no AI — playable on a laptop with stand-in hardware
- [x] 4. Story and Item receipt formats
- [ ] 5. One short complete playable adventure
- [ ] 6. AI narrator
- [ ] 7. Harness validating structured AI output
- [ ] 8. Only then: remote AI through Oracle or D12

Milestones 1-5 contain no model calls at all.

## Hardware

| Part | Detail | Status |
| --- | --- | --- |
| Raspberry Pi 5, 4GB | CanaKit bundle: board, case, active cooler, 45W USB-C PSU, 32GB microSD | On hand |
| Thermal printer | Symcode 58mm USB, MJ-5890K | **Working** — prints from a laptop over USB, 2026-10-06 |
| Thermal paper | MUNBYN 2 1/4" x 50ft, 10 rolls | Ordered |
| Buttons | MakerSpot 6mm tactile, pre-wired with female Dupont ends | **Not ordered yet** |

## Running on the Pi

The Pi is set up and prints. Reaching it and running the game:

```
ssh rachel@pocketquest.local        # key-based, no password is set
cd ~/pocket-quest && git pull
~/pocketquest-venv/bin/python pocketquest.py
```

- Hostname `pocketquest`, user `rachel`, SSH key only, passwordless sudo.
- Raspberry Pi OS Debian 13 (trixie), kernel 6.12, root grown to 29G.
- Dependencies live in `~/pocketquest-venv` — Debian will not let pip install
  into the system Python, so the venv is made with `--system-site-packages` to
  keep gpiozero visible.
- `/etc/udev/rules.d/99-pocketquest-printer.rules` gives the logged-in user the
  printer, so none of this needs sudo.
- Provisioned from cloud-init files on the boot partition (`user-data`,
  `network-config`). Two things that cost an hour and are worth knowing:
  installing an SSH key does **not** start the SSH server on Raspberry Pi OS —
  it ships disabled, and either an empty `ssh` file on the boot partition or a
  `runcmd` entry is needed. And cloud-init skips its whole first-boot config if
  `instance_id` in `meta-data` has not changed, so re-provisioning a card means
  changing that value too.
- Buttons are opt-in: `POCKETQUEST_BUTTONS=gpio`. Without it the keyboard
  stands in, because being on a Pi does not mean buttons are wired to it.

Notes that affect code:

- Raspberry Pi 5 cannot use `RPi.GPIO`. Buttons must use `gpiozero`.
- The printer is USB ESC/POS, driven with `python-escpos`. It enumerates as
  `POS58 Printer USB`, vendor `0x0416`, product `0x5011` — but **its bulk OUT
  endpoint is `0x03`, not the `0x01` python-escpos assumes**, so constructing
  `Usb()` without `out_ep=0x03` fails with `Invalid endpoint address 0x1`. The
  IN endpoint is `0x81`. Read off the device descriptor on 2026-10-06; the
  values live in `hardware.py`.
- 58mm paper is roughly 32 characters per line at the default font; 384 dots
  wide for images.

## Receipt types

Not every receipt is a wall of prose. Each printed object has a type with its
own layout, so the paper itself tells the player what they are holding.

| Type | Carries |
| --- | --- |
| STORY | A scene and its choices |
| ITEM | A collectible object, with a code |
| QUEST | An objective |
| MAP | An ASCII map fragment |
| CLUE | A hint, often needed later |
| CHARACTER | An NPC the player meets |
| ACHIEVEMENT | A marker of progress |
| SECRET | Hidden content |

Thermal printing is black and white at 58mm. That constraint is the visual
language, not a limitation to work around.

## The physical inventory loop

The idea the project is built around: in an ordinary RPG the inventory lives on
a screen. Here it lives on the player's desk.

```
digital state -> printer -> physical object -> player keeps it
      ^                                              |
      |                                              v
   digital state <- player brings it back to the machine
```

An ITEM receipt carries a code. Later the game asks whether the player has that
item. The paper has to come back to the machine for the story to continue, so
the loop closes through the real world.

## The AI narrator contract

The narrator is the last thing built (milestone 6) and the most tightly bound.
The program sends it the current situation as structured state — location, HP,
inventory, current quest, allowed exits, whether new items are permitted — and
asks for one encounter.

The model must answer in a fixed shape, roughly:

```
SCENE:        prose
CHOICE_A:     text
CHOICE_B:     text
HP_CHANGE:    0
ITEM_ADD:     none
NEXT_STATE:   forest_04
```

The harness (milestone 7) checks the answer before anything is printed:

- Is `NEXT_STATE` a state that actually exists?
- Is `HP_CHANGE` inside the allowed range?
- Does every item named in `ITEM_ADD` exist in the item table?
- Is the receipt short enough to print? (working limit: ~400 characters)
- Are there 2-3 choices, no more and no fewer?

Pass means print. Fail means reject and regenerate. The model can never grant
itself 999 HP, invent an item, or send the player to a room that does not exist.

## World and visual direction

Not swords-and-dragons fantasy. The direction is a retro-futuristic terminal:
monospace, ASCII, barcodes, system-log typography, black on white.

The premise under consideration: the player finds a machine that should not
still be running, printing messages from somewhere unclear — leaving it open
whether the player is playing a game inside the machine, or the machine is
using the game to reach the player.

The specific chapters, items and puzzles are still to be written.


## Course context

PSAM 5600 B, Parsons, Fall 2026. Course repo: `mfadt/sld-fall-2026`
(a sibling directory locally; read-only reference, never a place to put game code).

| Date | Due |
| --- | --- |
| 10/7 | Single-script MVP · midterm pitch |
| 10/14 | Bootstrap + harness files pushed to GitHub |
| 10/21 | Testing process and tooling |
| 11/4 | Cloud node running a self-hosted model |
| 11/11 | Expand beyond the monolithic script |
| 12/9 | Final release and showcase |

The syllabus dates are a guide, not a contract — the instructor does not hold
to them strictly. Treat them as direction, not deadlines, and confirm anything
load-bearing in class or on Canvas.

**Midterm pitch, 10/7.** Three to five minutes, informal — no slide deck
expected. The instructor opens the class project page, finds the student's
card, and clicks through to the project repository, so **the card and this
repository are the presentation surface**. The baseline question is "what are
you making?". Anything runnable, photographed or recorded is a bonus, not a
requirement. What the midterm does require is commitment: the project is
settled from here, and only the implementation keeps moving.

Canvas is authoritative for grades and announcements; the syllabus in the course
repo is a mirror.

## Open questions

- [ ] Which buttons, and how many? 2-3 is the design target. Milestone 2 cannot
      start without them.
- [ ] **How does a player enter an item code with only three buttons?** The
      concept shows the player typing `GK-194`, but there is no keyboard. Either
      the game asks a yes/no question and trusts the player, or codes get short
      enough to punch in on three buttons, or a scanner becomes a nice-to-have.
      This decides how milestone 5 is built.
- [ ] What is the adventure about, concretely? Chapters, items, puzzles. The
      author writes this, not the model.
- [ ] Where does the AI narrator run when it arrives? Deferred to milestone 6.

## Decisions

| Date | Decision | Why |
| --- | --- | --- |
| 2026-09-30 | Project is Pocket Quest | Replaces an earlier camera concept |
| 2026-09-30 | Own repository, separate from the course repo | Course repo is the whole class's; project code does not belong in it |
| 2026-09-30 | `AGENTS.md` holds the rules, `CLAUDE.md` points at it | One copy of the rules, so the two cannot drift apart |
| 2026-09-30 | Repo is public, named `pocket-quest`, tagged `sldllm-f26` | The course class-showcase page only finds public repos carrying that topic |
| 2026-09-30 | Receipt types, the physical inventory loop, the narrator contract and the retro-terminal direction adopted | From the expanded concept; recorded here so the repo, not a chat, holds them |
