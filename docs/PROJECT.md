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
- [x] 5. One short complete playable adventure — Chapter 01, a draft
- [x] 6. AI narrator
- [x] 7. Harness validating structured AI output
- [ ] 8. Only then: remote AI through Oracle or D12

Milestones 1-5 contain no model calls at all.

## Hardware

| Part | Detail | Status |
| --- | --- | --- |
| Raspberry Pi 5, 4GB | CanaKit bundle: board, case, active cooler, 45W USB-C PSU, 32GB microSD | On hand |
| Thermal printer | Symcode 58mm USB, MJ-5890K | **Working** — prints from a laptop over USB, 2026-10-06 |
| Thermal paper | MUNBYN 2 1/4" x 50ft, 10 rolls | Ordered |
| Buttons | 2 x EG STARTS 100mm LED dome, already owned | On hand |
| Button wiring | Twidec 4.8mm female spade leads, already owned | On hand |

The buttons were left over from an earlier project, so nothing had to be bought.
Their 12V LEDs cannot be driven from the Pi, which has 5V and 3.3V, and do not
need to be: the lamp and the microswitch are separate circuits and only the
switch matters. The spade leads end in bare wire, which goes into a female
Dupont jumper to reach the header.

100mm is large — three side by side would be 30cm — which the enclosure will
have to answer for in November.

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
- 58mm paper is **32 characters** per line, measured on the unit with a printed
  ruler on 2026-10-07, and 384 dots wide for images.
- ESC/POS settings are sticky — they live in the printer and survive the process
  that sent them. One run that turned on double-width left every later receipt
  wrapping at 16 characters until the printer was reset, which looked like a
  layout bug in the code and was not. `ThermalPrinter.print_lines` now sends
  `INIT` before every receipt.

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

## The narrator's model

`qwen3.5:9b`, served by Ollama on the author's own Oracle Ampere node — which is
also what the course asks for in week 11, so the assignment and the project are
the same piece of work.

Measured on the node, 2026-10-07:

| | |
| --- | --- |
| Speed | 5.6 tokens/sec, CPU only — the node has no GPU |
| One scene | 22–36 seconds |
| `qwen3.5:0.8b` | 37 tok/s but cannot hold the format; it invented an item and ran every field onto one line |

Two things that are easy to lose a morning to:

- **qwen3.5 reasons by default.** Left alone it spends the whole token budget
  thinking and returns an empty `response`. `"think": false` turns that off.
- **Ollama listens on `127.0.0.1` only.** Nothing outside the node can reach it,
  which is the right default. Development goes through an SSH tunnel —
  `ssh -N -L 11435:127.0.0.1:11434 mynode` — and 11435 because the author's Mac
  is already running an empty Ollama on 11434. How the Pi reaches the node is
  still open.

The narrator talks to Ollama's plain HTTP API through `urllib`, so there is no
SDK to install on the Pi.

## What the model actually does with the rules

First run, against a prompt that spelled all of this out:

- asked for at most 28 characters a line, wrote 32
- asked for up to 4 lines, wrote 1
- told never to name a game state in a choice, wrote `open door_01`

Nothing here is a bug to fix in the prompt. It is the reason milestone 7 exists.

## The model is not shown the map

Settled 2026-10-25. The narrator is told where the player is, never where they
may go, and is not asked for `NEXT_STATE`. The program routes and attaches the
destination afterwards, so the harness still checks it like any other field.

This started as a rule the prompt asked for and the model kept breaking. It is
now something the model cannot do, because it has never seen a state name.

Five runs each, same world, same situation, same checks, only the prompt
differing:

| | shown the map | not shown the map |
| --- | --- | --- |
| accepted | 1/5 | 4/5 |
| wrote a state name into a choice | 8 | 0 |
| seconds per scene | 13 | 13 |

A second run of five after the change: 3 accepted, and again no state names.
What still fails is length — a choice at 21 characters against a 20 character
limit, a line at 36 against 32. The harness rejects those and asks again.

The argument was never only the numbers. The first design principle says the
narrator does not change the game state; letting it choose the next room was
letting it do exactly that, with the harness catching it afterwards instead of
the design preventing it.

## The narrator inside the game

A scene opens itself to the model by carrying `narrate: True`. It still carries
the author's own text and choices, because that is what prints when the model
is unreachable or when nothing it sends survives three attempts. A scene that
can be narrated is the author's scene plus permission to try, which makes "the
game works without AI" a thing the code cannot do otherwise.

The narrator is off unless asked for:

```
POCKETQUEST_NARRATOR=on python3 pocketquest.py
```

Off, the game answers instantly and is exactly the written chapter. On, a
narrated scene costs about 12 seconds, or nothing at all when the model cannot
be reached — a refused connection fails immediately rather than waiting out the
timeout.

What the model may change is the prose, the two choice labels, HP by one, and
an item where the scene allows one. What it may never change is where those
choices lead. The labels are painted onto the program's own routing.

**Grounding, fixed 2026-10-27.** The model used to be handed the scene's title
and nothing else, so for `corridor_01` it knew only "behind the door" and
described a door the player had already walked through, offering to check a
keypad that exists nowhere in this world. It is now handed the author's own
lines as WHAT IS HERE, and told not to add an object that is not in them. Five
runs afterwards: every one about the corridor, the machines, the page and the
key, every choice acting on something real. The invention stopped.

**Typesetting moved to the program, 2026-10-27.** Six of seven rejections were
line width — 33, 34, 35 against a paper that fits 32 — and asking a model to
count characters does not work however plainly the prompt says to. The model is
now asked for sentences and `receipts.py` wraps them, which is where the
question of how text meets paper already lived. The harness no longer measures
lines; it measures how much was written, because length is a question about the
writing and too much prose is too much however it is broken up.

This is not the harness quietly repairing a reply. What it refuses to repair are
decisions — HP, items, where a choice leads. A line break is not a decision.

The choice limit was also wrong. Twenty characters was a number picked by
feel; a choice prints as `[A] ` plus its text, so the paper allows 28. It is
now derived rather than guessed.

**Two prompt faults found by reading the output.** The model described "flat
sentences that do not explain what they mean" as a thing present in the room —
it was reading the house style as scenery, so the style instructions are now
under their own heading that says they are not things that exist. And it
offered to take the glass key the player was already holding, so the inventory
is now labelled as already in the player's hands.

**A parser that was too strict.** One reply was thrown away whole for omitting
the `SCENE:` label above otherwise perfect prose. Anything before the first
labelled field is now read as the scene. Reading loosely is not accepting
loosely: every field still goes through the harness.

Acceptance across these changes, same scene, same model: 1 in 5 when the model
was shown the map, 2 in 5 once it was grounded but still typesetting, 6 in 6
once typesetting moved to the program and the choice limit came from the paper.

## What the harness caught

Twelve kinds of bad reply were fed to it by hand — an invented item, a real item
granted where it was not allowed, a destination that does not exist, a
destination that exists but was not offered, HP moved by five, HP that was not a
number, a line wider than the paper, six scene lines, no scene, a missing
choice, a choice longer than the button strip. It caught all twelve and passed
the one good reply.

Then it was pointed at the live model, three attempts:

| | |
| --- | --- |
| attempt 1 | two lines at 34 and 35 characters against a 32 character paper |
| attempt 2 | both choices named game states |
| attempt 3 | a choice named a game state |
| accepted | none |

The game fell back on the author's scene, which is what it is supposed to do,
and the model never touched the game state. The system worked. The narrator,
however, contributed nothing, and a narrator with a zero percent acceptance
rate is not yet a feature. See the open question below.

## Open questions

- [ ] Is a third button worth buying later? Two is settled for now, and the
      chapter is built so that no scene ever needs a third.
- [ ] How does the Pi reach Ollama on the node? SSH tunnel, Tailscale, or
      something else. Development uses a tunnel from the laptop.
- [ ] **How does a player enter an item code with only three buttons?** The
      concept shows the player typing `GK-194`, but there is no keyboard. Either
      the game asks a yes/no question and trusts the player, or codes get short
      enough to punch in on three buttons, or a scanner becomes a nice-to-have.
      This decides how milestone 5 is built.
- [ ] Chapter 01 is drafted but not the author.s. Rewrite the prose, and decide
      whether COINS means anything — it is printed on every receipt and never
      changes.


## Decisions

| Date | Decision | Why |
| --- | --- | --- |
| 2026-09-30 | Project is Pocket Quest | Replaces an earlier camera concept |
| 2026-09-30 | Own repository, separate from the course repo | Course repo is the whole class's; project code does not belong in it |
| 2026-09-30 | `AGENTS.md` holds the rules, `CLAUDE.md` points at it | One copy of the rules, so the two cannot drift apart |
| 2026-09-30 | Repo is public, named `pocket-quest`, tagged `sldllm-f26` | The course class-showcase page only finds public repos carrying that topic |
| 2026-09-30 | Receipt types, the physical inventory loop, the narrator contract and the retro-terminal direction adopted | From the expanded concept; recorded here so the repo, not a chat, holds them |
