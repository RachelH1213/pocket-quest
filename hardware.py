"""Everything that touches real hardware lives in this file.

The game itself never imports gpiozero or python-escpos. It asks for a printer
and a set of buttons, and it cannot tell whether it got the real ones on the Pi
or the stand-ins that run on a laptop. That is what lets the game be written and
played before any hardware arrives.
"""

import os
import time

LINE_WIDTH = 32  # characters per line on 58mm paper

# The Symcode MJ-5890K, as macOS and the Pi both see it. The endpoints are not
# the ones python-escpos assumes: this printer takes data on 0x03, not 0x01,
# and the only way to learn that was to read the device descriptor. Measured
# 2026-10-06 on the actual unit.
PRINTER_VENDOR = 0x0416
PRINTER_PRODUCT = 0x5011
PRINTER_IN_EP = 0x81
PRINTER_OUT_EP = 0x03


class TerminalPrinter:
    """Stand-in printer. 'Prints' to the terminal."""

    def print_lines(self, lines):
        # No border here. The receipt brings its own; this just plays the part
        # of paper coming out, one blank line standing in for the tear.
        print()
        for line in lines:
            print(line)
        print()


class ThermalPrinter:
    """The real Symcode 58mm USB printer, over ESC/POS."""

    def __init__(self):
        from escpos.printer import Usb

        self._device = Usb(
            PRINTER_VENDOR,
            PRINTER_PRODUCT,
            in_ep=PRINTER_IN_EP,
            out_ep=PRINTER_OUT_EP,
        )
        # python-escpos opens the device lazily, on first write. Touch it here
        # so that "no printer attached" fails while we are still choosing
        # hardware, and not halfway through someone's game.
        self._device.device

    def print_lines(self, lines):
        # ESC/POS settings are sticky: they live in the printer, not in this
        # process, and survive until something resets them. One run that turned
        # on double-width left every later receipt wrapping at 16 characters
        # instead of 32. Start every receipt from a known state.
        self._device.hw("INIT")
        self._device.set(align="left", bold=False, width=1, height=1)
        for line in lines:
            self._device.text(line + "\n")
        self._device.text("\n\n\n")  # clear the tear bar before cutting
        try:
            self._device.cut()
        except Exception:
            pass  # some units have no cutter; the feed above is enough


class KeyboardButtons:
    """Stand-in buttons. Press A, B or C and Enter."""

    def wait_for_choice(self, labels):
        # The receipt already lists the choices, the same way the real device
        # will. Here the three buttons are the A, B and C keys.
        letters = "ABC"[: len(labels)]
        while True:
            answer = input(f"  press {' / '.join(letters)} > ").strip().upper()
            if answer in letters:
                return letters.index(answer)


class GpioButtons:
    """The real buttons on the Pi.

    Milestone 2 wires these up; nothing is soldered to these pins yet. Raspberry
    Pi 5 needs gpiozero, because RPi.GPIO does not work on it.
    """

    PINS = (17, 27, 22)  # provisional, until the buttons are chosen

    def __init__(self):
        from gpiozero import Button

        self._buttons = [Button(pin) for pin in self.PINS]

    def wait_for_choice(self, labels):
        while True:
            for index, button in enumerate(self._buttons[: len(labels)]):
                if button.is_pressed:
                    while button.is_pressed:  # one press is one choice
                        time.sleep(0.01)
                    return index
            time.sleep(0.01)  # without this the loop eats a whole CPU core


def on_a_raspberry_pi():
    try:
        with open("/proc/device-tree/model") as f:
            return "Raspberry Pi" in f.read()
    except OSError:
        return False


def get_hardware():
    """Hand back a (printer, buttons) pair that suits whatever is attached.

    The printer is chosen by looking for the printer, not by looking at the
    host: it is just as real plugged into a laptop as into the Pi, and the game
    should use it either way. Buttons still depend on the host, because GPIO
    pins only exist on the Pi.
    """
    try:
        printer = ThermalPrinter()
    except Exception:
        printer = TerminalPrinter()

    # Being on a Pi is not the same as having buttons wired to it. Until
    # milestone 2 puts real buttons on those pins, asking gpiozero to wait for
    # a press is a wait that never ends, so GPIO is opt-in:
    #     POCKETQUEST_BUTTONS=gpio python3 pocketquest.py
    if os.environ.get("POCKETQUEST_BUTTONS") == "gpio":
        buttons = GpioButtons()
    else:
        buttons = KeyboardButtons()
    return printer, buttons
