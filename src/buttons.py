import RPi.GPIO as GPIO


class Buttons:
    def __init__(self, device, mode):
        self._left = 17
        self._right = 26
        self._setup_gpio()
        self._device = device
        self._mode = mode

    def _setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._left, GPIO.IN)
        GPIO.setup(self._right, GPIO.IN)
        GPIO.add_event_detect(self._left, GPIO.RISING, callback=self._left_callback, bouncetime=250)
        GPIO.add_event_detect(self._right, GPIO.RISING, callback=self._right_callback, bouncetime=250)

    def _left_callback(self, channel):
        print("LEFT")
        pass

    def _right_callback(self, channel):
        self._mode.switch()
