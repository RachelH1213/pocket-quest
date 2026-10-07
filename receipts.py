"""Turning game state into paper.

Every printed object has a type, and each type has its own layout. This file
builds the lines; it does not know how they get printed.

A note on characters: the mockups use box-drawing glyphs and hearts. Thermal
printers do not all carry those, and this one has not been tested yet, so
everything here stays inside plain ASCII, which every ESC/POS printer has. The
glyphs live in one place below — once milestone 1 proves what the Symcode can
actually render, change them there and nothing else moves.
"""

WIDTH = 32  # characters per line on 58mm paper

HEAVY = "="
LIGHT = "-"
HEART = "*"


def centre(text):
    return text.center(WIDTH).rstrip()


def rule(char=HEAVY):
    return char * WIDTH


def _status(player):
    return [
        f"HP       {(HEART + ' ') * player.hp}".rstrip(),
        f"COINS    {player.coins:02d}",
    ]


def story(scene, player, choices):
    """A STORY receipt: a scene, the player's state, and what they can do."""
    lines = [rule(), centre("POCKET QUEST"), rule(), ""]
    lines.extend(scene["title"].split("\n"))
    lines.append("")
    lines.extend(scene["text"])
    lines.append("")
    lines.extend(_status(player))

    if choices:
        lines.extend(["", "WHAT DO YOU DO?", ""])
        for letter, choice in zip("ABC", choices):
            lines.append(f"[{letter}] {choice['label']}")

    lines.extend(["", rule(LIGHT), f"PLAYER {player.number}", rule()])
    return lines


DEFAULT_ART = ["/\\", "/  \\", "/____\\"]


def item(item_data, number):
    """An ITEM receipt. This piece of paper is the object."""
    lines = [
        rule(),
        centre(f"ITEM {number:02d}"),
        rule(),
        "",
    ]
    lines.extend(centre(row) for row in item_data.get("art", DEFAULT_ART))
    lines.extend([
        "",
        centre(item_data["name"]),
        centre(item_data["rarity"]),
        "",
        centre("DO NOT LOSE THIS."),
        "",
        "CODE",
        centre(item_data["code"]),
        "",
        rule(),
    ])
    return lines


def ending(scene, player):
    """The last receipt of a run."""
    lines = [rule(), centre("POCKET QUEST"), rule(), ""]
    lines.extend(scene["title"].split("\n"))
    lines.append("")
    lines.extend(scene["text"])
    lines.extend(["", rule(LIGHT), f"PLAYER {player.number}"])
    lines.append(f"ITEMS    {len(player.inventory):02d}")
    lines.extend([rule()])
    return lines
