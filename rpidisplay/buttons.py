import logging

import RPi.GPIO as GPIO


class Buttons:
    def __init__(self, mode, brightness):
        self._left = 17
        self._right = 26
        self._mode = mode
        self._brightness = brightness
        self._setup_gpio()

    def _setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._left, GPIO.IN)
        GPIO.setup(self._right, GPIO.IN)
        GPIO.add_event_detect(self._left, GPIO.RISING, callback=self._left_callback, bouncetime=250)
        GPIO.add_event_detect(self._right, GPIO.RISING, callback=self._right_callback, bouncetime=250)

    def cleanup_gpio(self):
        GPIO.cleanup()
        logging.info("Cleaned up GPIO")

    def _left_callback(self, channel):
        self._brightness.on_click()

    def _right_callback(self, channel):
        self._mode.switch()
