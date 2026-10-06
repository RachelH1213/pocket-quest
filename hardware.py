"""Everything that touches real hardware lives in this file.

The game itself never imports gpiozero or python-escpos. It asks for a printer
and a set of buttons, and it cannot tell whether it got the real ones on the Pi
or the stand-ins that run on a laptop. That is what lets the game be written and
played before any hardware arrives.
"""

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

    def print_lines(self, lines):
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

    buttons = GpioButtons() if on_a_raspberry_pi() else KeyboardButtons()
    return printer, buttons
