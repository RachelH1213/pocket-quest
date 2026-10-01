# Pocket Quest

**A Raspberry Pi adventure console where the game comes out on paper.**

There is no screen holding the story. A thermal printer hands the player scenes,
clues, quests and items as physical receipts. Three buttons are how they answer.
The Pi keeps the game state and decides what prints next.

```
━━━━━━━━━━━━━━━━━━━━━━━━━
      POCKET QUEST
━━━━━━━━━━━━━━━━━━━━━━━━━

CHAPTER 01
THE LOST SIGNAL

You wake beside a machine
that should not be running.

A red light is blinking
inside the forest.

HP       ♥ ♥ ♥
COINS    03

WHAT DO YOU DO?

[A] FOLLOW THE LIGHT
[B] SEARCH THE AREA
[C] CALL FOR HELP

━━━━━━━━━━━━━━━━━━━━━━━━━
PLAYER 017
━━━━━━━━━━━━━━━━━━━━━━━━━
```

## The inventory is on your desk, not on a screen

When the player finds something, the machine prints it as its own receipt. That
piece of paper is the item.

```
╔══════════════════╗
      ITEM 014
╚══════════════════╝

        /\
       /◇ \
      /____\

   THE GLASS KEY
      RARE ITEM

  DO NOT LOSE THIS.

CODE
     GK-194
```

Twenty minutes later the game asks for it back:

```
THE GLASS DOOR

The door has no handle.
There is only a small
triangular opening.

DO YOU HAVE
THE GLASS KEY?

[A] YES
[B] NO
```

So the loop runs out through the real world and back:

```
game state ──▶ printer ──▶ paper in your hand
    ▲                             │
    └────── you bring it back ◀───┘
```

Lose the paper, lose the key.

## The AI is a narrator, not the game

The program owns the rules. When the AI arrives it is handed the situation —
location, HP, inventory, which exits exist, whether new items are allowed — and
asked for one scene. It answers in a fixed shape, and a harness checks the
answer before a single character reaches the printer:

- Is the next state one that actually exists?
- Is the HP change inside the allowed range?
- Does the item it wants to give the player exist?
- Are there two or three choices, and does it fit on a receipt?

Fails the check, it gets thrown out and asked again. The model cannot grant
itself 999 HP, invent an item, or send the player to a room nobody wrote.

**The game is fully playable before the AI exists.** Milestones 1–5 contain no
model calls at all.

## Receipt types

`STORY` · `ITEM` · `QUEST` · `MAP` · `CLUE` · `CHARACTER` · `ACHIEVEMENT` · `SECRET`

Each one has its own layout, so the paper tells you what you are holding. 58mm,
black and white, monospace — the constraint is the visual language.

## Status

Early. The project documentation is written; the game is not built yet.

- [ ] 1. Pi → printer → print `POCKET QUEST / HELLO PLAYER`
- [ ] 2. Buttons → Pi → different printed output
- [x] 3. Branching game state, no AI
- [ ] 4. Story and Item receipt formats
- [ ] 5. One short complete playable adventure
- [ ] 6. AI narrator
- [ ] 7. Harness validating the narrator
- [ ] 8. Only then: remote AI

## Hardware

Raspberry Pi 5 (4GB) · Symcode 58mm USB thermal printer · 2–3 physical buttons

## More

[`docs/PROJECT.md`](docs/PROJECT.md) — full definition, milestones, open questions, decisions
· [`AGENTS.md`](AGENTS.md) — how AI assistants work on this repo

---

Course project for PSAM 5600 B: Small Linux Devices, Large Language Models —
Parsons School of Design, Fall 2026.
