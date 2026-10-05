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
        # No border here. The receipt brings its own; this just plays the part
        # of paper coming out, one blank line standing in for the tear.
        print()
        for line in lines:
            print(line)
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
