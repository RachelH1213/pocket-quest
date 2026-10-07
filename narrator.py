"""The AI narrator — milestone 6.

The program owns the rules. This file hands the model a description of the
situation and asks for one scene's worth of prose, in a shape the program can
read back. It does not decide anything: what the model sends is parsed here and
checked by the harness (milestone 7) before any of it touches the game.

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

FIELDS = ("SCENE", "CHOICE_A", "CHOICE_B", "HP_CHANGE", "ITEM_ADD", "NEXT_STATE")

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
you may send the player to: {allowed_next}
you may grant an item: {items_allowed}

RULES
- SCENE is at most 4 lines, each at most 28 characters. Count them.
- The two choices are things the player does, written as commands, at most 20
  characters. Never name a game state in a choice.
- HP_CHANGE is exactly -1, 0 or 1.
- ITEM_ADD is none unless granting an item is allowed above.
- NEXT_STATE is copied exactly from the list above.

Reply with these six lines and nothing else:
SCENE:
<line>
<line>
CHOICE_A: <text>
CHOICE_B: <text>
HP_CHANGE: <number>
ITEM_ADD: none
NEXT_STATE: <state>
"""


class NarratorError(RuntimeError):
    """The model could not be reached, or sent something unreadable."""


def build_prompt(state):
    return PROMPT.format(
        location=state["location"],
        hp=state["hp"],
        inventory=", ".join(state["inventory"]) or "empty",
        allowed_next=", ".join(state["allowed_next"]),
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


def narrate(state):
    """One scene, as the model wrote it. Nothing here has been checked yet."""
    return parse(ask_model(build_prompt(state)))
