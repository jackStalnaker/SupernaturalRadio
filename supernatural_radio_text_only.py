import time
import os
import sys
import random
from brain import Brain

#
# This is a text-only interaction. Useful for prompt debugging and testing.
#

class SupernaturalRadio:

    def __init__(self):
        print("Initializing SupernaturalRadio...")
        self.brain = Brain()
        self.character = None
        self.character_name = None
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

    print("running")
    supernatural_radio.select_character("santa")
    supernatural_radio.character.interact_with_guest_text_only()


if __name__ == "__main__":
    main()
