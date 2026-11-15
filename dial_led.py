import time
import numpy as np
from gpiozero import PWMLED
from rpi_hardware_pwm import HardwarePWM

class DialLED:
    RED_PIN = 13
    GREEN_PIN = 6
    BLUE_PIN = 5

    MIN_VOICE_BRIGHTNESS = 3  # Min voice follower brightness
    MAX_VOICE_BRIGHTNESS = 100 # Min voice follower brightness

    MIN_VOICE_DB = -110.0
    MAX_VOICE_DB = -25.0

    def __init__(self):
        print("Initializing DialLED...")
        self.red = PWMLED(self.RED_PIN)
        self.green = PWMLED(self.GREEN_PIN)
        self.blue = PWMLED(self.BLUE_PIN)
        print("Initializing DialLED done.")

    def __del__(self):
        self.red.close()
        self.blue.close()
        self.green.close()

    def set_rgb(self, r, g, b):
        self.red.value = r / 255.0
        self.green.value = g / 255.0
        self.blue.value = b / 255.0

    def match_brightness_to_voice(self, voice_db):
        level = (voice_db - self.MIN_VOICE_DB) / (self.MAX_VOICE_DB - self.MIN_VOICE_DB)
        level = max(0.0, min(1.0, level))  # Clip to 0, 1

        brightness = self.MIN_VOICE_BRIGHTNESS + level * (self.MAX_VOICE_BRIGHTNESS - self.MIN_VOICE_BRIGHTNESS)
        brightness = int(brightness)
        return brightness

    def set_led_to_voice(self, voice_db, hue=(1.0, 1.0, 1.0)):
        brightness = self.match_brightness_to_voice(voice_db)
        self.set_rgb(hue[0]*brightness, hue[1]*brightness, hue[2]*brightness)

    def center(self):
        self.set_rgb(128, 128, 128)

def main():
    dial_led = DialLED()

    rmss = np.loadtxt("test_rms.txt")
    try:
        #while True:
        #    dial.set_rgb(100, 0, 0)
        #    time.sleep(1)
        #    dial.set_rgb(0, 100, 0)
        #    time.sleep(1)
        #    dial.set_rgb(0, 0, 100)
        #    time.sleep(1)
        print("Test brightness and set_rgb separately")
        for i, rms in enumerate(rmss):
            brightness = dial_led.match_brightness_to_voice(rms)
            print(brightness)
            dial_led.set_rgb(brightness, brightness, brightness)
            time.sleep(0.01)

        print("Test set_led_to_voice")
        for i, rms in enumerate(rmss):
            dial_led.set_led_to_voice(rms)
            time.sleep(0.01)

        print("Test hue")
        for i, rms in enumerate(rmss):
            dial_led.set_led_to_voice(rms, hue=(1.0, 0.3, 0.0))
            time.sleep(0.01)
    finally:
        print("Off")
        dial_led.set_rgb(0, 0, 0)           


if __name__ == "__main__":
    main()
