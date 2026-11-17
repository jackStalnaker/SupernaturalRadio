import time
import os
import sys
import random
from characters.base_character import BaseCharacter


class Malachi(BaseCharacter):
    QUIET_TEASE_PROB = 0.20
    CALLAFTER_PROB = 0.20

    SPEECH_VOLUME = 80

    # Music
    MUSIC_FOLDER = "./music"
    MUSIC_VOLUME = 50

    # Sweep
    SWEEP_VOLUME = 100
    SWEEP_LENGTH = 73
    SWEEP_FILENAME = "fx/freesound_community-tuning-radio-7150.mp3"

    # Hiss
    HISS_VOLUME = 2
    # Feature rich
    HISS_LENGTH = 148
    HISS_FILENAME = "fx/freesound_community-radio-noise-11-59824.mp3"
    # Plain static
    HISS_LENGTH = 60
    HISS_FILENAME = "fx/freesound_community-radio-static-2-26831.mp3"

    # Breathing
    BREATHING_VOLUME = 100
    BREATHING_LENGTHS = [21, 13, 29]
    BREATHING_FILENAMES = [
        "fx/freesound_community-breathing-6811.mp3",  # Plain
        "fx/freesound_community-male-breathing-slow-14558.mp3",  # Sharp
        "fx/freesound_community-man_breathing_asleep-75120.mp3"  # Asleep
    ]

    def __init__(self):
        print("Initializing Malachi...")
        super().__init__()
        self.hiss_process = None
        self.breathing_process = None
        print("Initializing Malachi done.")

    def play_tuning_sweep(self, duration, callback=None):
        self.voice.play_effect(self.SWEEP_FILENAME, self.SWEEP_LENGTH, duration, volume=self.SWEEP_VOLUME, callback=callback)

    def start_hiss(self):
        start_offset = random.uniform(0, self.HISS_LENGTH)
        self.hiss_process = self.voice.start_effect(self.HISS_FILENAME, volume=self.HISS_VOLUME, start_offset=start_offset, process=self.hiss_process)

    def stop_hiss(self):
        self.voice.stop_effect(self.hiss_process)
        self.hiss_process = None

    def start_breathing(self):
        b_id = random.randint(0, len(self.BREATHING_LENGTHS) - 1)
        filename = self.BREATHING_FILENAMES[b_id]
        length = self.BREATHING_LENGTHS[b_id]
        start_offset = random.uniform(0, length)
        self.breathing_process = self.voice.start_effect(filename, volume=self.BREATHING_VOLUME, start_offset=start_offset, process=self.breathing_process)

    def stop_breathing(self):
        self.voice.stop_effect(self.breathing_process)
        self.breathing_process = None

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
