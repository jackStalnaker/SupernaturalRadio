import time
import os
import sys
import random
from ears import Ears
from eyes import Eyes
from voice import Voice
from brain import Brain
from dial_led import DialLED
from dial_servo import DialServo
from presence import Presence, MockSensor 
from tof_sensor import initialize_vL53l0x


class Malachi:
    QUIET_TEASE_PROB = 0.20
    CALLAFTER_PROB = 0.20

    MUSIC_VOLUME = 50
    HISS_VOLUME = 2
    SPEECH_VOLUME = 80
    BREATHING_VOLUME = 100
    SWEEP_VOLUME = 100

    def __init__(self):
        print("Initializing Malachi...")
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
        print("Initializing Malachi done.")
        
    def wait_for_guest(self):
        self.dial_led.center()
        self.dial_servo.center()
        self.voice.start_jazz(volume=self.MUSIC_VOLUME)
        self.presence.start_monitoring()
        print("Monitoring for presence.")
        self.presence.wait_until_present()
        print("Presence detected. Capturing scene.")
        frame = self.eyes.capture_encoded_frame()
        print("Getting description of scene.")
        self.scene = self.brain.describe_encoded_image(frame)
        print("Stopping jazz.")
        self.voice.stop_jazz()
        return True

    def interact_with_guest(self):
        print("Beginning guest interaction.")
        self.brain.start_new_conversation()

        self.dial_led.set_rgb(0, 255, 0)
        self.voice.play_tuning_sweep(duration=2, callback=self.dial_servo.random_sweep_during, volume=self.SWEEP_VOLUME)
        self.dial_servo.go_to_malachi()
        self.dial_led.center()
        self.voice.start_breathing(volume=self.BREATHING_VOLUME)
        self.voice.start_hiss(volume=self.HISS_VOLUME)
        first_words = True

        while True:
            # Check if guest is still present
            if self.presence.became_absent():
                print("Guest departed.")
                break
    
            start = time.monotonic()
            query_audio = self.ears.listen(timeout=10)
            print(f"Listen returned after {time.monotonic() - start:.1f}s; "
                  f"audio is None: {query_audio is None}")

            if query_audio is None:
                if random.random() >= self.QUIET_TEASE_PROB:
                    continue

                query_text = "The guest is not saying anything. Playfully tease them to provoke a response."
            else:
                query_text = self.brain.transcribe(query_audio)

            if first_words:
                query_text = f"GUEST QUERY:\n {query_text} \n\n SCENE:\n {self.scene}"
            else:
                query_text = f"GUEST QUERY:\n {query_text}"

            print(f"Query: {query_text}")
            response_text = self.brain.react_to_text(query_text)
            print(f"Response: {response_text}")

            if first_words:
                self.voice.play_tuning_sweep(duration=2, callback=self.dial_servo.random_sweep_during, volume=self.SWEEP_VOLUME)
                self.dial_servo.go_to_malachi()
                first_words = False

            self.voice.stop_breathing()
            self.voice.speak(response_text, rms_callback=self.dial_led.set_led_to_voice, volume=self.SWEEP_VOLUME)
            self.voice.start_breathing()

        self.voice.stop_breathing()
        if random.random() < self.CALLAFTER_PROB:
            self.call_after_guest()
        self.voice.stop_hiss()

    def call_after_guest(self):
        # Call after the guest (trigger ocassionally)

        prompt = (
            "The guest has just walked away. "
            "Call after them with a brief, spooky or sarcastic parting remark. "
            "Keep it to one short sentence. Do not ask a question."
        )
        response = self.brain.react_to_text(prompt)
        self.voice.speak(response, rms_callback=self.dial_led.set_led_to_voice, volume=self.SPEECH_VOLUME)

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
    malachi = Malachi()

    print("running")

    try:
        while True:
            # Right now, this only returns true, but at the risk of violating YAGNI, I can see some
            # cases where false might be useful in the future.
            if malachi.wait_for_guest():
                malachi.interact_with_guest()
    finally:
        malachi.presence.stop_monitoring()
        malachi.voice.cleanup()
        malachi.eyes.close()


if __name__ == "__main__":
    main()
