from django.core.checks import Warning, register
from gpiozero import DigitalOutputDevice, GPIOZeroError


class DigitDisplay:
    """
     -  A
    / / F/B
     -  G
    / / E/C
     -. D/DP
    """
    a = 1 << 0
    b = 1 << 6
    c = 1 << 5
    d = 1 << 4
    e = 1 << 3
    f = 1 << 1
    g = 1 << 2
    dp = 1 << 7

    digits = {
        '1': b | c,
        '2': a | b | d | e | g,
        '3': a | b | c | d | g,
        '4': f | g | b | c,
        '5': a | f | g | c | d,
        '6': a | f | g | e | c | d,
        '7': a | b | c,
        '8': a | b | c | d | e | f | g,
        '9': a | b | c | d | f | g,
        '0': a | b | c | d | e | f,
        ' ': 0,
        '-': g,
    }

    def __init__(self, clock_pin=25, latch_pin=23, data_pin=24):
        self.clock = DigitalOutputDevice(clock_pin, active_high=False)
        self.latch = DigitalOutputDevice(latch_pin, active_high=False)
        self.data = DigitalOutputDevice(data_pin, active_high=False)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def _display_value(self):
        for digit in self.value:
            segs = self.digits.get(digit, 0)

            for bit in range(8):
                self.clock.active_high = False
                self.data.value = segs & 1 << (7 - bit)
                self.clock.active_high = True

        self.latch.active_high = False
        self.latch.active_high = True


try:
    display = DigitDisplay()
except GPIOZeroError:
    display = None


@register()
def check_display(app_configs, **kwargs):
    errors = []
    if display is None:
        errors.append(
            Warning(
                'No LED display board connected. Check the pins!',
                id='score.E001',
            )
        )
    return errors


def set_display(value):
    if display is None:
        return
    try:
        display.value = value
    except GPIOZeroError:
        pass
