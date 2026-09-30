# Working rules for AI assistants on Pocket Quest

Read this before doing anything in this repository. `docs/PROJECT.md` holds the
full project definition; this file is about *how to work here*.

## What this project is

A physical adventure game. A Raspberry Pi 5 holds the game state, physical
buttons are the player's input, and a thermal receipt printer is the output. An
AI model will later write narrative prose, tightly constrained.

## Non-negotiable design rules

1. **The program owns the rules and the state.** The AI narrator never decides
   what happens, never edits the game state, never invents items or exits. It
   receives structured state and returns prose.
2. **The game works without AI.** Milestones 1-5 contain no model calls at all.
   If the AI is unreachable, the game must still be playable.
3. **All AI output is validated before use.** Nothing reaches the printer until
   the harness has checked it against the expected structure.
4. **Hardware code stays separate from game logic** wherever it is practical, so
   the game can be developed and tested without a printer attached.

## How to work here

- **Work incrementally.** One milestone at a time, in the order in
  `docs/PROJECT.md`. Verify each one before starting the next.
- **Do not add features that were not asked for.** Not "while I was in there",
  not "you'll probably want". If something seems missing, say so and wait.
- **Do not over-engineer.** Prefer the plain, obvious version. This is a course
  project built by someone learning; clever is worse than clear.
- **Explain technical decisions in beginner-friendly language.** The author is
  new to the terminal, git, and Linux. Say what a command does before running it,
  and how to check it worked.
- **Ask before any major architectural change.** Explain why it is needed first.
- **The repository is the project's memory, not the chat.** Decisions,
  constraints and progress belong in `docs/PROJECT.md` and in commit messages —
  not in a conversation that will be closed.
- **Keep documentation current.** When an important decision changes, update
  `docs/PROJECT.md` in the same change.

## Attribution

Course policy: every commit gets a `Co-Authored-By:` trailer naming the specific
model that helped write it.
