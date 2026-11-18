import time
import os
import sys
import random
from brain import Brain

#
# This is a text-only interaction. Useful for prompt debugging and testing.
#

class Malachi:

    def __init__(self):
        print("Initializing Malachi...")
        self.brain = Brain()
        print("Initializing Malachi done.")
        
    def interact_with_guest(self):
        print("Beginning guest interaction.")
        self.brain.start_new_conversation()

        first_words = True

        while True:
            visitor = input("\nVisitor: ")
            if visitor.lower() in ["exit", "quit"]:
                break

            if visitor.lower in ["reset", "restart"]:
                self.brain.start_new_conversation()
                print("Conversation reset.")
                continue

            response = self.brain.react_to_text(visitor)

            print("Malachi: ", response)


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
    malachi = Malachi()

    print("running")
    malachi.interact_with_guest()


if __name__ == "__main__":
    main()
