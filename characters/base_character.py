import os
import sys
from abc import ABC, abstractmethod


class BaseCharacter(ABC):
    CHARACTER_NAME = "BaseCharacter"

    QUIET_TEASE_PROB = 0.20
    CALLAFTER_PROB = 0.20

    MUSIC_VOLUME = 50
    SPEECH_VOLUME = 80
    BREATHING_VOLUME = 100
    SWEEP_VOLUME = 100

    def __init__(self, radio):
        print("Initializing BaseCharacter...")
        self.radio = radio
        self.scene = None
        print("Initializing BaseCharacter done.")
        
    @abstractmethod
    def wait_for_guest(self):
        raise NotImplementedError("interact_with_guest must be implemented in subclasses.")

    def interact_with_guest_text_only(self):
        print("Beginning guest interaction.")
        self.radio.brain.start_new_conversation(self.response_instructions, self.scene_instructions)

        first_words = True

        while True:
            query_text = input("\nVisitor: ")
            if query_text.lower() in ["exit", "quit"]:
                break

            if query_text.lower() in ["reset", "restart"]:
                self.radio.brain.start_new_conversation(self.response_instructions, self.scene_instructions)
                print("Conversation reset.")
                continue

            response_text = self.radio.brain.react_to_text(query_text)

            print(f"{self.CHARACTER_NAME}: ", response_text)

    @abstractmethod
    def interact_with_guest(self):
        raise NotImplementedError("interact_with_guest must be implemented in subclasses.")

    @abstractmethod
    def call_after_guest(self):
        # Call after the guest (trigger ocassionally)
        raise NotImplementedError("call_after_guest must be implemented in subclasses.")

    def reset_for_new_guest(self):
        # Do any cleanup for a new guest
        pass


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
    base_character = BaseCharacter()

    print("running")

    try:
        while True:
            # Right now, this only returns true, but at the risk of violating YAGNI, I can see some
            # cases where false might be useful in the future.
            if base_character.wait_for_guest():
                base_character.interact_with_guest()
    finally:
        base_character.presence.stop_monitoring()
        base_character.voice.cleanup()
        base_character.eyes.close()


if __name__ == "__main__":
    main()
