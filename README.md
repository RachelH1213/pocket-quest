# Pocket Quest

Pocket Quest is a Raspberry Pi-powered adventure console where the game unfolds
through physical receipts that become stories, clues, quests and collectible
objects. The player chooses with physical buttons; the Pi holds the game state
and prints what comes next.

Course project for PSAM 5600 B: Small Linux Devices, Large Language Models
(Parsons, Fall 2026).

## Status

Pre-implementation. This repository currently holds project documentation only —
no game code has been written yet.

## How it is meant to play

A receipt comes out of the printer carrying a scene and a set of choices. The
player presses a button to choose. The Pi updates the game state and prints
whatever comes next — the following scene, an item, a clue, a map fragment.
Items print as their own receipts, so the player's inventory is a physical pile
of paper.

Later, an AI model writes the prose for those scenes. It never decides what
happens: the program owns the rules and the state, hands the model a structured
description of the situation, and validates whatever comes back before any of it
reaches the printer.

## Hardware

| Part | What it is | Status |
| --- | --- | --- |
| Raspberry Pi 5 (4GB) | Runs the game | On hand (CanaKit bundle) |
| Symcode 58mm USB thermal printer (MJ-5890K) | Prints every receipt | Ordered |
| Thermal paper, 2 1/4" x 50ft | Consumable | Ordered |
| Physical buttons | Player input | **Not chosen yet** |

## Design principle

The game must be a complete, playable branching adventure *before* any AI is
added. If the model is unavailable, the game still runs.

## Milestones

1. Raspberry Pi -> thermal printer -> print `POCKET QUEST / HELLO PLAYER`
2. Physical buttons -> Raspberry Pi -> different printed outputs
3. A basic branching game state, no AI
4. Story and Item receipt formats
5. One short complete playable adventure
6. AI narrator
7. A harness that validates structured AI output
8. Only then: remote AI via Oracle or D12

## Documentation

- [`docs/PROJECT.md`](docs/PROJECT.md) — full project definition, decisions, open questions
- [`AGENTS.md`](AGENTS.md) — working rules for AI assistants
- [`CLAUDE.md`](CLAUDE.md) — Claude Code specifics
