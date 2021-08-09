from gpiozero import LEDCollection, LEDBoard, OutputDeviceError, DigitalOutputDevice
from gpiozero.threads import GPIOThread
from gpiozero.exc import OutputDeviceError
from itertools import cycle
from time import sleep

class SevenSegmentDisplay(LEDBoard):
    """
    Extends :class:`LEDBoard` for a 7 segment LED display
    7 segment displays have either 7 or 8 pins, 7 pins for the digit display
    and an optional 8th pin for a decimal point. 7 segment displays
    typically have either a common anode or common cathode pin, when
    using a common anode display 'active_high' should be set to False.
    Instances of this class can be used to display characters or control
    individual leds on the display. For example::
        from gpiozero import SevenSegmentDisplay
        seven = SevenSegmentDisplay(1,2,3,4,5,6,7,8,active_high=False)
        seven.display("7")

    :param int \*pins:
        Specify the GPIO pins that the 7 segment display is attached to.
        Pins should be in the LED segment order A,B,C,D,E,F,G,decimal_point
        (the decimal_point is optional).
    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances for each pin. If
        ``False`` (the default), construct regular :class:`LED` instances. This
        parameter can only be specified as a keyword parameter.
    :param bool active_high:
        If ``True`` (the default), the :meth:`on` method will set all the
        associated pins to HIGH. If ``False``, the :meth:`on` method will set
        all pins to LOW (the :meth:`off` method always does the opposite). This
        parameter can only be specified as a keyword parameter.
    :param bool initial_value:
        If ``False`` (the default), all LEDs will be off initially. If
        ``None``, each device will be left in whatever state the pin is found
        in when configured for output (warning: this can be on). If ``True``,
        the device will be switched on initially. This parameter can only be
        specified as a keyword parameter.

    """
    def __init__(self, *pins, **kwargs):
        # 7 segment displays must have 7 or 8 pins
        if len(pins) == 7:
            self._has_decimal_point = False
        elif len(pins) == 8:
            self._has_decimal_point = True
        else:
            raise ValueError('SevenSegmentDisplay must have 7 or 8 pins')
        # Don't allow 7 segments to contain collections
        for pin in pins:
            assert not isinstance(pin, LEDCollection)

        pwm = kwargs.pop('pwm', False)
        active_high = kwargs.pop('active_high', True)
        initial_value = kwargs.pop('initial_value', False)
        if kwargs:
            raise TypeError('unexpected keyword argument: %s' % kwargs.popitem()[0])

        self._layouts = {
            '1': (False, True, True, False, False, False, False),
            '2': (True, True, False, True, True, False, True),
            '3': (True, True, True, True, False, False, True),
            '4': (False, True, True, False, False, True, True),
            '5': (True, False, True, True, False, True, True),
            '6': (True, False, True, True, True, True, True),
            '7': (True, True, True, False, False, False, False),
            '8': (True, True, True, True, True, True, True),
            '9': (True, True, True, True, False, True, True),
            '0': (True, True, True, True, True, True, False),
            'A': (True, True, True, False, True, True, True),
            'B': (False, False, True, True, True, True, True),
            'C': (True, False, False, True, True, True, False),
            'D': (False, True, True, True, True, False, True),
            'E': (True, False, False, True, True, True, True),
            'F': (True, False, False, False, True, True, True),
            'G': (True, False, True, True, True, True, False),
            'H': (False, True, True, False, True, True, True),
            'I': (False, False, False, False, True, True, False),
            'J': (False, True, True, True, True, False, False),
            'K': (True, False, True, False, True, True, True),
            'L': (False, False, False, True, True, True, False),
            'M': (True, False, True, False, True, False, False),
            'N': (True, True, True, False, True, True, False),
            'O': (True, True, True, True, True, True, False),
            'P': (True, True, False, False, True, True, True),
            'Q': (True, True, False, True, False, True, True),
            'R': (True, True, False, False, True, True, False),
            'S': (True, False, True, True, False, True, True),
            'T': (False, False, False, True, True, True, True),
            'U': (False, False, True, True, True, False, False),
            'V': (False, True, True, True, True, True, False),
            'W': (False, True, False, True, False, True, False),
            'X': (False, True, True, False, True, True, True),
            'Y': (False, True, True, True, False, True, True),
            'Z': (True, True, False, True, True, False, True),
            '-': (False, False, False, False, False, False, True),
            ' ': (False, False, False, False, False, False, False),
            '=': (False, False, False, True, False, False, True)
        }

        super(SevenSegmentDisplay, self).__init__(*pins, pwm=pwm, active_high=active_high, initial_value=initial_value)

    def display(self, char):
        """
        Display a character on the 7 segment display
        :param string char:
            A single character to be displayed
        """
        char = str(char).upper()
        if len(char) > 1:
            raise ValueError('only a single character can be displayed')
        if char not in self._layouts:
            raise ValueError('there is no layout for character - %s' % char)
        layout = self._layouts[char]
        for led in range(7):
            self[led].value = layout[led]

    def display_hex(self, hexnumber):
        """
        Display a hex number (0-F) on the 7 segment display
        :param int hexnumber:
            The number to be displayed in hex
        """
        self.display(hex(hexnumber)[2:])

    @property
    def decimal_point(self):
        """
        Represents the status of the decimal point led
        """
        # does the 7seg display have a decimal point (i.e pin 8)
        if self.has_decimal_point:
            return self[7].value
        else:
            raise OutputDeviceError('there is no 8th pin for the decimal point')

    @decimal_point.setter
    def decimal_point(self, value):
        """
        Sets the status of the decimal point led
        """
        if self.has_decimal_point:
            self[7].value = value
        else:
            raise OutputDeviceError('there is no 8th pin for the decimal point')

    @property
    def has_decimal_point(self):
        """
        Represents whether the seven segment display has a decimal point
        """
        return self._has_decimal_point

    def set_char_layout(self, char, layout):
        """
        Create or update a custom character layout, which can be used with the
        `display` method.
        :param string char:
            A single character to be displayed

        :param tuple layout:
            A 7 bool tuple of LED values in the segment order A, B, C, D, E, F, G
        """
        char = str(char).upper()
        if len(char) != 1:
            raise ValueError('only a single character can be used in a layout')
        if len(layout) != 7:
            raise ValueError('a character layout must have 7 segments')
        self._layouts[char] = layout

class MultiSevenSegmentDisplay(SevenSegmentDisplay):
    """
    Extends :class:`SevenSegmentDisplay` for a multi digit 7 segment LED display
    7 segment displays have either 7 or 8 pins, 7 pins for the digit display
    and an optional 8th pin for a decimal point. 7 segment displays
    typically have either a common anode or common cathode pin, when
    using a common anode display 'active_high' should be set to False.

    Multi digit 7 segment displays have additional pins for each digit which
    when set low for common anode or high for common cathode will light that
    digit.

    Different values are displayed on different digits by multiplexing the display.

    Instances of this class can be used to display numbers, messages or control
    individual leds and digits on the display. For example::
        from gpiozero import MultiSevenSegmentDisplay
        multi_seven = MultiSevenSegmentDisplay((1,2,3,4,5,6,7,8)(9,10,11,12))
        multi_seven.display("leds")

    :param tuple led_pins:
        Specify the GPIO pins that the 7 segment display's leds are attached to.
        Pins should be in the LED segment order A,B,C,D,E,F,G,decimal_point
        (the decimal_point is optional).
    :param tuple digit_pins:
        Specify the GPIO pins that the 7 segment display's digits are attached to.
    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances for each LED pin. If
        ``False`` (the default), construct regular :class:`LED` instances. This
        parameter can only be specified as a keyword parameter.
    :param bool active_high:
        If ``True`` (the default), the :meth:`on` method will set all the
        associated pins to HIGH. If ``False``, the :meth:`on` method will set
        all pins to LOW (the :meth:`off` method always does the opposite). This
        parameter can only be specified as a keyword parameter.
    :param bool initial_value:
        If ``False`` (the default), all LEDs and digits will be off initially. If
        ``None``, each device will be left in whatever state the pin is found
        in when configured for output (warning: this can be on). If ``True``,
        the device will be switched on initially. This parameter can only be
        specified as a keyword parameter.

    """
    def __init__(self, led_pins, digit_pins, **kwargs):
        pwm = kwargs.pop('pwm', False)
        active_high = kwargs.pop('active_high', True)
        initial_value = kwargs.pop('initial_value', False)
        if kwargs:
            raise TypeError('unexpected keyword argument: %s' % kwargs.popitem()[0])
        if len(digit_pins) < 2:
            raise ValueError('a MultiSevenSegmentDisplay must have more than 1 digit')
        self.digits = []
        for digit_pin in digit_pins:
            self.digits.append(DigitalOutputDevice(digit_pin, active_high=not active_high))
        self._display_thread = None

        super(MultiSevenSegmentDisplay, self).__init__(*led_pins, pwm=pwm, active_high=active_high)
        if initial_value:
            self.on()

    def display(self, message, align_left=True, refresh_delay=0.007):
        """
        Display a message on the multi 7 segment display
        :param string message:
            The message to be displayed. If the 7 segment display has
            a decimal points, they will be used in replacement for
            full stops in the message.

        :param bool align_left:
            If 'True' (the default) the message will be aligned to the left
            on the display. If 'False' the message will be aligned to the
            right.

        :param float refresh_delay:
            The time in seconds that each digit will be turned on when
            multiplexing the display.
            The defalut of 0.007 was chosen by trial and error, short enough
            so there was no flicker, long enough to still be bright, this
            value may need to be modified depending on the display.
        """
        self._stop_display()
        message = self._format_message(str(message), align_left)
        self._display_thread = GPIOThread(
            target=self._display, args=(message, align_left, refresh_delay)
        )
        self._display_thread.start()

    def _display(self, message, align_left, refresh_delay):

        for digit in cycle(range(len(self.digits))):
            #if we are at the start of the digits, go to the start of the message
            if digit == 0:
                i = 0

            #display the digit
            super(MultiSevenSegmentDisplay, self).display(message[i])
            #is the next digit a full stop?
            if self.has_decimal_point:
                if message[i+1:i+2] == ".":
                    self.decimal_point = True
                    i += 1
                else:
                    self.decimal_point = False

            #turn the digit on and wait
            self.digits[digit].on()
            if self._display_thread.stopping.wait(refresh_delay):
                break
            self.digits[digit].off()

            i += 1

    def _format_message(self, message, align_left):
        #add spaces to decimal points if needed
        if self.has_decimal_point:
            output = ""
            for i in range(len(message)):
                if message[i] == '.' and (message[i-1] == '.' or i == 0):
                    output += ' '
                output += message[i]
            message = output

        #validate the messages length
        if (self.has_decimal_point and len(message) - message.count('.') > len(self.digits)) or (not self.has_decimal_point and len(message) > len(self.digits)):
            raise ValueError('the message is too long: %s' % message)

        #align the message
        max_len = len(self.digits) + message.count(".") if self.has_decimal_point else len(self.digits)
        message = message.ljust(max_len) if align_left else message.rjust(max_len)

        return message

    def _stop_display(self):
        if self._display_thread:
            self._display_thread.stop()
            self._display_thread = None

    def on(self):
        """
        Turns on all LEDs on all digits.
        """
        self._stop_display()
        super(MultiSevenSegmentDisplay, self).on()
        for digit in self.digits:
            digit.on()

    def off(self):
        """
        Turns off all LEDs on all digits
        """
        self._stop_display()
        super(MultiSevenSegmentDisplay, self).off()
        for digit in self.digits:
            digit.off()

    @property
    def value(self):
        """
        Represents the value of the displays pins, returning a tuple of
        2 tuples for LED values and digit values.
        """
        digits_value = []
        for digit in self.digits:
            digits_value.append(digit.value)

        leds_value = []
        for led in self:
            leds_value.append(led.value)

        return((tuple(leds_value), tuple(digits_value)))

    @value.setter
    def value(self, value):
        """
        Sets the value of the displays pins, passing a tuple of
        2 tuples for LED values and digit values.
        e.g. ``((A, B, C, D, E, F, G, decimal_point),
        (1, 2, 3, 4))``
        """
        self._stop_display()
        leds_value = value[0]
        digits_value = value[1]

        if len(digits_value) != len(self.digits):
            raise ValueError('expected %s digit values' % len(self.digits))

        for i in range(len(self.digits)):
            self.digits[i].value = digits_value[i]

        for i in range(len(leds_value)):
            self[i].value = leds_value[i]
