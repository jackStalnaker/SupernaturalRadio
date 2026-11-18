import time
import os
import sys
import random
from pathlib import Path
from ears import Ears
from eyes import Eyes
from voice import Voice
from brain import Brain
from dial_led import DialLED
from dial_servo import DialServo
from presence import Presence, MockSensor 
from tof_sensor import initialize_vL53l0x


class SupernaturalRadio:
    def __init__(self):
        print("Initializing SupernaturalRadio...")
        self.brain = Brain()
        self.ears = Ears()
        self.voice = Voice()
        self.eyes = Eyes()
        # sensor = MockSensor()
        sensor = initialize_vL53l0x()
        self.presence = Presence(sensor)
        self.dial_led = DialLED()
        self.dial_servo = DialServo()
        self.character = None
        print("Initializing SupernaturalRadio done.")

    def select_character(self, character_name):
        if character_name == "malachi":
            from characters.malachi.malachi import Malachi
            self.character = Malachi(self)
        elif character_name == "santa":
            from characters.santa.santa import Santa
            self.character = Santa(self)
        else:
            raise ValueError(f"Unknown character: {character_name}")

    def run(self):
        if self.character is None:
            raise ValueError("No character selected. Call select_character() first.")
        self.character.run()

def environment_check():
    if "ELEVENLABS_API_KEY" not in os.environ:
        print("You need to set the ElevenLabs auth key environment variable first.")
        sys.exit(1)

    if "OPENAI_API_KEY" not in os.environ:
        print("You need to set the OpenAI auth key environment variable first.")
        sys.exit(1)


def main():
    print("checking environment")
    environment_check()

    print("initializing")
    supernatural_radio = SupernaturalRadio()
    supernatural_radio.select_character("malachi")

    print("running")
    try:
        supernatural_radio.run()
    except KeyboardInterrupt:
        print("Interrupted.")


if __name__ == "__main__":
    main()
