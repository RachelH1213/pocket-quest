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
the machine or the machine is writing the player.

HOW TO WRITE
Flat, plain sentences. No fantasy, no exclamation marks, no addressing the
reader as "adventurer". These are instructions about your prose. They are not
things that exist in the room and must never be described as if they were.

WHAT IS HERE
{here}

THE SITUATION
hp: {hp} — the receipt already prints this. Do not state it in the prose.
already in the player's hands: {inventory}
you may grant an item: {items_allowed}

RULES
- Retell the moment above in your own words. Everything in this room is listed
  under WHAT IS HERE. Do not add an object that is not in it.
- SCENE is two or three short sentences, about 120 characters altogether.
  Write sentences, not lines; the printer decides where they break.
- The two choices are things the player does, written as commands, a few words
  each and never more than 28 characters, and each must act on something listed under
  WHAT IS HERE. Never
  offer to pick up or take something the player is already holding.
- HP_CHANGE is exactly -1, 0 or 1.
- ITEM_ADD is none unless granting an item is allowed above.

Reply with these five fields and nothing else:
SCENE:
<a sentence>
<a sentence>
CHOICE_A: <text>
CHOICE_B: <text>
HP_CHANGE: <number>
ITEM_ADD: none
"""


class NarratorError(RuntimeError):
    """The model could not be reached, or sent something unreadable."""


def build_prompt(state):
    """Note what is absent: the map. The model is told what is in the room it is
    describing, not where the exits lead."""
    return PROMPT.format(
        here=state["here"],
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
    # Anything before the first labelled field is the scene, whether or not the
    # model remembered to write "SCENE:" above it. Reading a reply loosely is
    # not the same as accepting it: the harness still checks every field.
    current = "SCENE"
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


def narrate(state, next_state=None):
    """One scene, as the model wrote it. Nothing here has been checked yet.

    Routing is the program's and happens after the player chooses, so there is
    usually no destination to attach. `next_state` exists for callers that do
    decide up front and want the harness to check their own value too.
    """
    reply = parse(ask_model(build_prompt(state)))
    if next_state is not None:
        reply["NEXT_STATE"] = next_state
    return reply
