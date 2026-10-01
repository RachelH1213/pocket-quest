"""Pocket Quest — the game.

Milestone 3: a branching game state, no AI anywhere in it.

Nothing in this file knows whether it is talking to a thermal printer or a
terminal. It asks hardware.py for a printer and some buttons and gets on with
the game.

The story below is placeholder, lifted from the concept document so there is
something to walk through. It is meant to be replaced.
"""

import hardware

# ---------------------------------------------------------------- the world

ITEMS = {
    "glass_key": {"name": "THE GLASS KEY", "code": "GK-194"},
}

SCENES = {
    "forest_01": {
        "title": "CHAPTER 01\nTHE LOST SIGNAL",
        "text": [
            "You wake beside a machine",
            "that should not be running.",
            "",
            "A red light is blinking",
            "inside the forest.",
        ],
        "choices": [
            {"label": "FOLLOW THE LIGHT", "goto": "door_01"},
            {"label": "SEARCH THE AREA", "goto": "clearing_01"},
            {"label": "CALL FOR HELP", "goto": "silence_01"},
        ],
    },
    "clearing_01": {
        "title": "YOU SEARCH THE AREA",
        "text": [
            "Under a pile of leaves,",
            "you find a small glass key.",
            "",
            "Something moves behind you.",
        ],
        "give": "glass_key",
        "choices": [
            {"label": "TURN AROUND", "goto": "turn_01"},
            {"label": "RUN", "goto": "door_01"},
        ],
    },
    "turn_01": {
        "title": "YOU TURN AROUND",
        "text": [
            "Nothing is there.",
            "",
            "The red light is closer",
            "than it was.",
        ],
        "hp": -1,
        "choices": [
            {"label": "GO TO THE LIGHT", "goto": "door_01"},
        ],
    },
    "silence_01": {
        "title": "YOU CALL FOR HELP",
        "text": [
            "Your voice goes nowhere.",
            "",
            "The machine beside you",
            "prints a single line:",
            "",
            "   NOBODY IS LISTENING",
        ],
        "hp": -1,
        "choices": [
            {"label": "WALK TO THE LIGHT", "goto": "door_01"},
        ],
    },
    "door_01": {
        "title": "THE GLASS DOOR",
        "text": [
            "The door has no handle.",
            "",
            "There is only a small",
            "triangular opening.",
        ],
        "choices": [
            {
                "label": "USE THE GLASS KEY",
                "goto": "ending_open",
                "requires": "glass_key",
            },
            {"label": "KNOCK", "goto": "ending_knock"},
            {"label": "WALK AWAY", "goto": "ending_away"},
        ],
    },
    "ending_open": {
        "title": "THE DOOR OPENS",
        "text": [
            "The key fits the opening",
            "exactly, as though the door",
            "had been waiting for it.",
            "",
            "Behind it, the signal.",
            "",
            "   END OF CHAPTER 01",
        ],
        "ending": True,
    },
    "ending_knock": {
        "title": "YOU KNOCK",
        "text": [
            "Something on the other side",
            "knocks back, in the same",
            "rhythm, a moment too late.",
            "",
            "You do not knock again.",
            "",
            "   END OF CHAPTER 01",
        ],
        "ending": True,
    },
    "ending_away": {
        "title": "YOU WALK AWAY",
        "text": [
            "The forest closes behind you.",
            "",
            "Somewhere back there the",
            "machine is still printing.",
            "",
            "   END OF CHAPTER 01",
        ],
        "ending": True,
    },
}

START = "forest_01"
STARTING_HP = 3


# ---------------------------------------------------------------- the player


class Player:
    def __init__(self):
        self.hp = STARTING_HP
        self.coins = 3
        self.inventory = []

    def has(self, item_id):
        return item_id in self.inventory

    def status_lines(self):
        return [
            f"HP       {'* ' * self.hp}".rstrip(),
            f"COINS    {self.coins:02d}",
        ]


# ---------------------------------------------------------------- the game


def build_receipt(scene, player):
    """Turn a scene plus the player's state into lines of paper."""
    lines = scene["title"].split("\n")
    lines.append("")
    lines.extend(scene["text"])
    if not scene.get("ending"):
        lines.append("")
        lines.extend(player.status_lines())
    return lines


def available_choices(scene, player):
    """Choices the player can actually take right now."""
    return [
        choice
        for choice in scene["choices"]
        if "requires" not in choice or player.has(choice["requires"])
    ]


def play():
    printer, buttons = hardware.get_hardware()
    player = Player()
    scene_id = START

    while True:
        scene = SCENES[scene_id]

        if "give" in scene and not player.has(scene["give"]):
            player.inventory.append(scene["give"])

        if "hp" in scene:
            player.hp = max(0, player.hp + scene["hp"])

        printer.print_lines(build_receipt(scene, player))

        if scene.get("ending") or player.hp <= 0:
            if player.hp <= 0:
                printer.print_lines(["YOU ARE OUT OF HP", "", "   GAME OVER"])
            return

        choices = available_choices(scene, player)
        picked = buttons.wait_for_choice([c["label"] for c in choices])
        scene_id = choices[picked]["goto"]


if __name__ == "__main__":
    play()
