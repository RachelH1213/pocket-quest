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
Oracle integration · D12 API · local/cloud model routing

None of these are to be built until the must-haves are done.

## Milestones

- [ ] 1. Raspberry Pi -> thermal printer -> print `POCKET QUEST / HELLO PLAYER`
- [ ] 2. Physical buttons -> Raspberry Pi -> different printed outputs
- [ ] 3. Basic branching game state, no AI
- [ ] 4. Story and Item receipt formats
- [ ] 5. One short complete playable adventure
- [ ] 6. AI narrator
- [ ] 7. Harness validating structured AI output
- [ ] 8. Only then: remote AI through Oracle or D12

Milestones 1-5 contain no model calls at all.

## Hardware

| Part | Detail | Status |
| --- | --- | --- |
| Raspberry Pi 5, 4GB | CanaKit bundle: board, case, active cooler, 45W USB-C PSU, 32GB microSD | On hand |
| Thermal printer | Symcode 58mm USB, MJ-5890K | Ordered |
| Thermal paper | MUNBYN 2 1/4" x 50ft, 10 rolls | Ordered |
| Buttons | Not chosen yet | **Open** |

Notes that affect code:

- Raspberry Pi 5 cannot use `RPi.GPIO`. Buttons must use `gpiozero`.
- The printer is USB ESC/POS, driven with `python-escpos`.
- 58mm paper is roughly 32 characters per line at the default font; 384 dots
  wide for images.

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

The course asks for a **single-script MVP first**, and only expands past one
script in week 12. Structure choices should respect that.

Canvas is authoritative for grades and announcements; the syllabus in the course
repo is a mirror.

## Open questions

- [ ] Which buttons, and how many? Milestone 2 cannot start without them.
- [ ] What is the adventure about? Setting, tone, length. Author writes this,
      not the model.
- [ ] Where does the AI narrator run when it arrives? Deferred to milestone 6.
- [ ] GitHub repository name and whether it is public.

## Decisions

| Date | Decision | Why |
| --- | --- | --- |
| 2026-09-30 | Project is Pocket Quest | Replaces an earlier camera concept |
| 2026-09-30 | Own repository, separate from the course repo | Course repo is the whole class's; project code does not belong in it |
| 2026-09-30 | `AGENTS.md` holds the rules, `CLAUDE.md` points at it | One copy of the rules, so the two cannot drift apart |
