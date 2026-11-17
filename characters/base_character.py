import os
import sys
from abc import ABC, abstractmethod
from ears import Ears
from eyes import Eyes
from voice import Voice
from brain import Brain
from dial_led import DialLED
from dial_servo import DialServo
from presence import Presence, MockSensor 
from tof_sensor import initialize_vL53l0x


class BaseCharacter(ABC):
    QUIET_TEASE_PROB = 0.20
    CALLAFTER_PROB = 0.20

    MUSIC_VOLUME = 50
    SPEECH_VOLUME = 80
    BREATHING_VOLUME = 100
    SWEEP_VOLUME = 100

    def __init__(self):
        print("Initializing BaseCharacter...")
        self.brain = Brain()
        self.ears = Ears()
        self.voice = Voice()
        self.eyes = Eyes()
        # sensor = MockSensor()
        sensor = initialize_vL53l0x()
        self.presence = Presence(sensor)
        self.dial_led = DialLED()
        self.dial_servo = DialServo()
        self.scene = None
        print("Initializing BaseCharacter done.")
        
    def wait_for_guest(self):
        self.dial_led.center()
        self.dial_servo.center()
        self.voice.start_music(volume=self.MUSIC_VOLUME)
        self.presence.start_monitoring()
        print("Monitoring for presence.")
        self.presence.wait_until_present()
        print("Presence detected. Capturing scene.")
        frame = self.eyes.capture_encoded_frame()
        print("Getting description of scene.")
        self.scene = self.brain.describe_encoded_image(frame)
        print("Stopping music.")
        self.voice.stop_music()
        return True

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
