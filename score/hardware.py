from django.core.checks import Warning, register
from gpiozero import GPIOZeroError, LEDCharDisplay, LEDMultiCharDisplay

try:
    display = LEDMultiCharDisplay(
        LEDCharDisplay(22, 23, 24, 25, 21, 20, 16, dp=12),
        26, 19, 13, 6
    )
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
