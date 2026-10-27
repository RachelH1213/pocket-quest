"""The harness — milestone 7.

Everything the model sends passes through here before the game believes any of
it. Nothing in this file talks to a model or to a printer: it is given a parsed
reply and the situation it was asked about, and it answers with a list of what
is wrong. An empty list means the reply may be used.

The checks are not hypothetical. The first real reply from the narrator broke
three of them, against a prompt that had spelled all three out.
"""

import receipts

MAX_SCENE_CHARS = 160  # five lines of paper, once the program has wrapped it
MAX_SCENE_LINES = 5  # counted after wrapping, not as the model typed it
# A choice prints as "[A] " plus its text, so the paper decides this, not taste.
MAX_CHOICE = receipts.WIDTH - len("[A] ")
MAX_RECEIPT = 400  # characters, so one scene stays one receipt
HP_LIMIT = 1  # the model may move HP by one, in either direction


class HarnessFailure(RuntimeError):
    """The model never produced a usable reply."""


def check(reply, state, known_states, known_items):
    """Everything wrong with this reply, as plain sentences. Empty means fine."""
    problems = []

    scene = reply.get("SCENE") or []
    if not scene:
        problems.append("the scene is empty")
    # Line breaks are the program's job — receipts.py wraps to the paper. What
    # is checked here is length, which is a question about the writing and not
    # about typesetting: too much prose is too much however it is broken up.
    written = sum(len(line) for line in scene)
    if written > MAX_SCENE_CHARS:
        problems.append(f"the scene is {written} characters, the limit is {MAX_SCENE_CHARS}")
    wrapped = receipts.wrap(scene)
    if len(wrapped) > MAX_SCENE_LINES:
        problems.append(f"the scene fills {len(wrapped)} lines of paper, the limit is {MAX_SCENE_LINES}")

    for field in ("CHOICE_A", "CHOICE_B"):
        choice = reply.get(field, "")
        if not choice:
            problems.append(f"{field} is empty; a scene needs two choices")
            continue
        if len(choice) > MAX_CHOICE:
            problems.append(f"{field} is {len(choice)} characters, the limit is {MAX_CHOICE}")
        named = [s for s in known_states if s.lower() in choice.lower()]
        if named:
            problems.append(f"{field} names the game state {named[0]!r}; choices are what the player does")

    hp = reply.get("HP_CHANGE", "")
    try:
        if abs(int(hp)) > HP_LIMIT:
            problems.append(f"HP_CHANGE is {hp}, the limit is {HP_LIMIT} either way")
    except (TypeError, ValueError):
        problems.append(f"HP_CHANGE is {hp!r}, which is not a number")

    item = reply.get("ITEM_ADD", "none")
    if item.lower() != "none":
        if item not in known_items:
            problems.append(f"ITEM_ADD is {item!r}, which is not an item that exists")
        elif item not in state.get("items_allowed", []):
            problems.append(f"ITEM_ADD is {item!r}, which this scene was not allowed to grant")

    # Routing belongs to the program now, so most replies carry no destination
    # at all. When a caller does decide one up front, it gets checked like
    # anything else — against programmer error rather than model misbehaviour.
    if "NEXT_STATE" in reply:
        nxt = reply["NEXT_STATE"]
        if nxt not in state["allowed_next"]:
            problems.append(f"NEXT_STATE is {nxt!r}, which is not one of {state['allowed_next']}")

    length = sum(len(line) + 1 for line in wrapped) + len(reply.get("CHOICE_A", "")) + len(reply.get("CHOICE_B", ""))
    if length > MAX_RECEIPT:
        problems.append(f"the receipt would be {length} characters, the limit is {MAX_RECEIPT}")

    return problems


def validated(state, known_states, known_items, narrate, attempts=3, log=None):
    """A reply that passed every check, or HarnessFailure after enough tries.

    Rejected replies are thrown away whole. Nothing partially correct is kept,
    and nothing is quietly repaired: a reply either earns its way in or the
    game falls back on what the author wrote.
    """
    complaints = []
    for attempt in range(1, attempts + 1):
        reply = narrate(state)
        problems = check(reply, state, known_states, known_items)
        if not problems:
            if log:
                log(f"attempt {attempt}: accepted")
            return reply
        complaints.append((attempt, problems))
        if log:
            for problem in problems:
                log(f"attempt {attempt}: rejected — {problem}")
    raise HarnessFailure(
        f"{attempts} attempts, none usable: "
        + "; ".join(p for _, ps in complaints for p in ps)
    )
