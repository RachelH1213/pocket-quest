# Claude Code — Pocket Quest

**Read [`AGENTS.md`](AGENTS.md) first.** It holds the project's working rules and
design constraints, and it applies to you in full. This file only adds the parts
specific to Claude Code.

Kept as two files on purpose: `AGENTS.md` is the vendor-neutral version that any
assistant can read, so the rules live in one place and cannot drift apart.

## Orientation

- `docs/PROJECT.md` — what is being built, the milestones, the open questions,
  and the log of decisions already made. Read it before proposing anything.
- The current milestone is whichever one in `docs/PROJECT.md` is not yet checked
  off. Work on that one, not a later one.

## Session habits

- When context fills up, write `HANDOFF.md` before starting a fresh session:
  what is being built, what is done, what is in progress, what not to change.
  Delete it once the next session has absorbed it.
- Prefer small commits that each do one thing.

## Hardware notes that will bite you

- This is a **Raspberry Pi 5**. `RPi.GPIO` does not work on it. Use `gpiozero`.
- The printer is a **USB ESC/POS** device (Symcode 58mm MJ-5890K), driven with
  `python-escpos`. It is 58mm wide — roughly 32 characters per line at the
  default font, 384 dots for images.
- Development happens on a Mac; the printer and buttons are on the Pi. Code that
  touches hardware must be isolated enough that game logic can run on the laptop.
