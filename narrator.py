"""The AI narrator — milestone 6.

The program owns the rules. This file hands the model a description of the
situation and asks for one scene's worth of prose, in a shape the program can
read back. It does not decide anything: what the model sends is parsed here and
checked by the harness before any of it touches the game.

The model is never shown the names of the game's states, and is never asked
where the player should go next. The program knows the map and does the
routing. Measured over five runs each, being shown the state names made the
model write them into the player's choices eight times; not being shown them
made that impossible, and the acceptance rate went from one in five to four in
five at the same speed.

Talks to Ollama over its plain HTTP API, so there is no SDK to install. The
model runs on the author's own Oracle node, which is also what the course asks
for in week 11.
"""

import json
import os
import urllib.error
import urllib.request

ENDPOINT = os.environ.get("POCKETQUEST_OLLAMA", "http://127.0.0.1:11434")
MODEL = os.environ.get("POCKETQUEST_MODEL", "qwen3.5:9b")
TIMEOUT = 180  # the node is CPU-only; a scene takes about 22 seconds

FIELDS = ("SCENE", "CHOICE_A", "CHOICE_B", "HP_CHANGE", "ITEM_ADD")

PROMPT = """\
You write scenes for an adventure game that prints on receipt paper.

The world: someone woke in a forest beside a machine that should not still be
running. The machines print. It is never clear whether the player is reading
the machine or the machine is writing the player. Flat, plain sentences. No
fantasy, no exclamation marks, no addressing the reader as "adventurer".

THE SITUATION
location: {location}
hp: {hp}
inventory: {inventory}
you may grant an item: {items_allowed}

RULES
- SCENE is at most 4 lines, each at most 28 characters. Count them.
- The two choices are things the player does, written as commands, at most 20
  characters.
- HP_CHANGE is exactly -1, 0 or 1.
- ITEM_ADD is none unless granting an item is allowed above.

Reply with these five lines and nothing else:
SCENE:
<line>
<line>
CHOICE_A: <text>
CHOICE_B: <text>
HP_CHANGE: <number>
ITEM_ADD: none
"""


class NarratorError(RuntimeError):
    """The model could not be reached, or sent something unreadable."""


def build_prompt(state):
    """Note what is absent: the map. The model is told where the player is, not
    where they may go."""
    return PROMPT.format(
        location=state["location"],
        hp=state["hp"],
        inventory=", ".join(state["inventory"]) or "empty",
        items_allowed=", ".join(state.get("items_allowed", [])) or "no",
    )


def ask_model(prompt):
    """Send the prompt to Ollama and hand back the raw reply."""
    body = json.dumps(
        {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False,  # qwen3.5 reasons by default and never reaches an answer
            "options": {"temperature": 0.8, "num_predict": 220},
        }
    ).encode()
    request = urllib.request.Request(
        f"{ENDPOINT}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.load(response)["response"]
    except (urllib.error.URLError, TimeoutError, OSError) as problem:
        raise NarratorError(f"could not reach the model at {ENDPOINT}: {problem}")


def parse(reply):
    """Read the model's reply into a dict. Raises if a field is missing.

    SCENE runs over several lines; every other field is one line. Anything the
    model says outside these six fields is dropped.
    """
    found = {}
    scene = []
    current = None
    for line in reply.strip().splitlines():
        label, _, rest = line.partition(":")
        if label.strip() in FIELDS:
            current = label.strip()
            if current == "SCENE":
                if rest.strip():
                    scene.append(rest.strip())
            else:
                found[current] = rest.strip()
        elif current == "SCENE" and line.strip():
            scene.append(line.strip())

    found["SCENE"] = scene
    missing = [f for f in FIELDS if f not in found or found[f] in ("", [])]
    if missing:
        raise NarratorError(f"reply was missing {', '.join(missing)}:\n{reply}")
    return found


def narrate(state, next_state):
    """One scene, as the model wrote it. Nothing here has been checked yet.

    `next_state` is the program's routing decision, attached after the fact so
    the harness can check it like any other field. The model had no part in it.
    """
    reply = parse(ask_model(build_prompt(state)))
    reply["NEXT_STATE"] = next_state
    return reply
