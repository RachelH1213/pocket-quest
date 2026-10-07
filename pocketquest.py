"""Pocket Quest — the game.

Milestone 3: a branching game state, no AI anywhere in it.

Nothing in this file knows whether it is talking to a thermal printer or a
terminal. It asks hardware.py for a printer and some buttons and gets on with
the game.

Chapter 01 is a draft. It extends the world set out in the concept document —
the machine that should not be running, the red light, the glass key, the glass
door — and it is the author's to rewrite.
"""

import hardware
import receipts

# ---------------------------------------------------------------- the world

ITEMS = {
    "glass_key": {
        "name": "THE GLASS KEY",
        "rarity": "RARE ITEM",
        "code": "GK-194",
        "art": ["/\\", "/ o \\", "/_____\\"],
    },
    "the_page": {
        "name": "THE PAGE",
        "rarity": "EVIDENCE",
        "code": "PG-001",
        "art": ["+-------+", "| ~~~~~ |", "| ~~~~  |", "+-------+"],
    },
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
                "goto": "corridor_01",
                "requires": "glass_key",
            },
            {"label": "KNOCK", "goto": "ending_knock"},
            {"label": "WALK AWAY", "goto": "ending_away"},
        ],
    },
    "corridor_01": {
        "title": "BEHIND THE DOOR",
        "text": [
            "A corridor of machines,",
            "all of them printing.",
            "",
            "The nearest one stops",
            "as you reach it.",
            "",
            "A page hangs from it,",
            "still warm.",
        ],
        "choices": [
            {"label": "READ THE PAGE", "goto": "page_01"},
            {"label": "WALK PAST", "goto": "room_01"},
        ],
    },
    "page_01": {
        "title": "THE PAGE",
        "text": [
            "It describes someone waking",
            "in a forest beside a machine.",
            "",
            "It describes the leaves,",
            "the key, the door.",
            "",
            "It stops at the line where",
            "you are standing.",
        ],
        "give": "the_page",
        "choices": [
            {"label": "GO ON", "goto": "room_01"},
        ],
    },
    "room_01": {
        "title": "THE SIGNAL ROOM",
        "text": [
            "One machine, older than",
            "the others, still warm.",
            "",
            "This is where the red light",
            "was coming from.",
            "",
            "It is printing your name.",
        ],
        "choices": [
            {"label": "PULL THE CORD", "goto": "ending_off"},
            {
                "label": "FEED IT THE PAGE",
                "goto": "ending_page",
                "requires": "the_page",
            },
            {"label": "SIT DOWN AND WAIT", "goto": "ending_wait"},
        ],
    },
    "ending_off": {
        "title": "YOU PULL THE CORD",
        "text": [
            "The printing stops.",
            "The forest goes quiet.",
            "",
            "The receipts in your hand",
            "are still warm.",
            "",
            "   END OF CHAPTER 01",
        ],
        "ending": True,
    },
    "ending_page": {
        "title": "YOU FEED IT THE PAGE",
        "text": [
            "The machine takes it back",
            "and starts again from the",
            "line where you stood.",
            "",
            "This time it prints what",
            "you are going to do next.",
            "",
            "   END OF CHAPTER 01",
        ],
        "ending": True,
    },
    "ending_wait": {
        "title": "YOU SIT DOWN",
        "text": [
            "You let it work.",
            "",
            "It prints until morning.",
            "",
            "None of it is about you.",
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
        self.number = "017"  # placeholder until save codes exist

    def has(self, item_id):
        return item_id in self.inventory


# ---------------------------------------------------------------- the game


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

        if "hp" in scene:
            player.hp = max(0, player.hp + scene["hp"])

        picked_up = None
        if "give" in scene and not player.has(scene["give"]):
            player.inventory.append(scene["give"])
            picked_up = scene["give"]

        run_is_over = scene.get("ending") or player.hp <= 0
        choices = [] if run_is_over else available_choices(scene, player)

        if scene.get("ending"):
            printer.print_lines(receipts.ending(scene, player))
        else:
            printer.print_lines(receipts.story(scene, player, choices))

        # The item is a second piece of paper. That piece of paper is the object.
        if picked_up:
            printer.print_lines(
                receipts.item(ITEMS[picked_up], len(player.inventory))
            )

        if run_is_over:
            if player.hp <= 0:
                printer.print_lines(
                    [receipts.rule(), receipts.centre("GAME OVER"), receipts.rule()]
                )
            return

        picked = buttons.wait_for_choice([c["label"] for c in choices])
        scene_id = choices[picked]["goto"]


if __name__ == "__main__":
    play()
