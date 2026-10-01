"""Everything that touches real hardware lives in this file.

The game itself never imports gpiozero or python-escpos. It asks for a printer
and a set of buttons, and it cannot tell whether it got the real ones on the Pi
or the stand-ins that run on a laptop. That is what lets the game be written and
played before any hardware arrives.
"""

LINE_WIDTH = 32  # characters per line on 58mm paper


class TerminalPrinter:
    """Stand-in printer. 'Prints' to the terminal."""

    def print_lines(self, lines):
        print()
        print("=" * LINE_WIDTH)
        for line in lines:
            print(line)
        print("=" * LINE_WIDTH)
        print()


class ThermalPrinter:
    """The real Symcode 58mm USB printer, over ESC/POS.

    Not used yet — milestone 1 wires this up and tests it.
    """

    def __init__(self):
        from escpos.printer import Usb

        self._device = Usb(0x0416, 0x5011)  # confirm with lsusb on the Pi

    def print_lines(self, lines):
        for line in lines:
            self._device.text(line + "\n")
        self._device.cut()


class KeyboardButtons:
    """Stand-in buttons. Press 1, 2 or 3 and Enter."""

    def wait_for_choice(self, labels):
        for number, label in enumerate(labels, start=1):
            print(f"  [{number}] {label}")
        while True:
            answer = input("> ").strip()
            if answer.isdigit() and 1 <= int(answer) <= len(labels):
                return int(answer) - 1
            print(f"  Type a number from 1 to {len(labels)}.")


class GpioButtons:
    """The real buttons on the Pi.

    Not used yet — milestone 2 wires these up. Raspberry Pi 5 needs gpiozero;
    RPi.GPIO does not work on it.
    """

    PINS = (17, 27, 22)  # provisional, until the buttons are chosen

    def __init__(self):
        from gpiozero import Button

        self._buttons = [Button(pin) for pin in self.PINS]

    def wait_for_choice(self, labels):
        while True:
            for index, button in enumerate(self._buttons[: len(labels)]):
                if button.is_pressed:
                    return index


def on_a_raspberry_pi():
    try:
        with open("/proc/device-tree/model") as f:
            return "Raspberry Pi" in f.read()
    except OSError:
        return False


def get_hardware():
    """Hand back a (printer, buttons) pair that suits wherever this is running."""
    if on_a_raspberry_pi():
        return ThermalPrinter(), GpioButtons()
    return TerminalPrinter(), KeyboardButtons()
