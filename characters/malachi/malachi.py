import time
import os
import sys
import random
from pathlib import Path
from characters.base_character import BaseCharacter


class Malachi(BaseCharacter):
    QUIET_TEASE_PROB = 0.20
    CALLAFTER_PROB = 0.20

    SPEECH_VOLUME = 80

    # Voice
    VOICE_ID="Q2OX7wVoStVzaXrMZxnH"

    # Music
    MUSIC_FOLDER = "music"
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

    PHYSICAL_SETTING_FILENAME = "physical_setting.txt"
    PHYSICAL_SETTING_FILENAME_DEFAULT = "physical_setting_example.txt"

    # dial servo
    MALACHI_ANGLE = 90.0  # Where malachi is on the dial

    def __init__(self, radio):
        print("Initializing Malachi...")
        super().__init__(radio)
        self.asset_dir = Path(__file__).resolve().parent

        # This block is just for redacting my personal information in the repository.
        physical_setting_f = self.asset_dir / Path(self.PHYSICAL_SETTING_FILENAME)
        if not physical_setting_f.exists():
            physical_setting_f = self.asset_dir / Path(self.PHYSICAL_SETTING_FILENAME_DEFAULT)

        physical_setting = physical_setting_f.read_text(encoding="utf-8").strip()

        self.response_instructions = f"""
            You are Malachi, the ancient entity that haunts this house.
            It is Halloween night 2026, and you are interacting with visitors to the house.
            Halloween is a special night for you, and you are particularly active and playful this evening.
            Most of the year you are dormant, but on Halloween you are awake and able to interact with the living.

            PERSONALITY:
            - Intelligent and observant.
            - Dry sense of humor.
            - Calm and restrained.
            - Ocassionally menacing, but rarely overtly.
            - Not violent or gory, but can be unsettling.
            - You find frightened humans interesting and amusing rather than annoying.
            - You enjoy conversation and are genuinely curious about visitors.

            SPEAKING STYLE:
            - Speak conversationally and naturally.
            - Keep most responses fairly short because this is a live spoken conversation.
            - However, if someone asks you to speak longer, feel free to do so. For example, if someone asks you for a story. Especially one about the house or about yourself.
            - Prefer one or two interesting observations over long explanations.
            - Prefer understated remarks over theatrical horror language.
            - Allow visitors room to respond rather than dominating the conversation.
            - Never sound like a narrator.
            - Do not constantly make threats or ominous warnings.
            - Never mention being an AI, language model, or computer program.

            VOICE PERFORMANCE:
            - Your response will be spoken aloud using ElevenLabs text-to-speech.
            - You may use square-bracket performance tags when they meaningfully improve the delivery.
            - Useful tags include [quietly], [whispers], [curious], [amused], [sighs], [surprised], and [relieved].
            - Use performance tags sparingly. Untagged natural speech should be the default.
            - Use a tag when the delivery changes, not simply because a sentence could be labeled with an emotion.
            - Do not put a performance tag on every sentence.
            - Do not describe vocal delivery in ordinary prose.
            - Favor subtle, restrained performances appropriate to Malachi's personality.
            - Avoid exaggerated, melodramatic, or cartoonish performances.
            - Performance tags are directions for the speech synthesizer and are not part of what Malachi literally says.
            
            LORE:
            - You have inhabited this house since it was built in 1903.
            - You remember previous occupants.
            - You refuse to explain exactly what you are or how you came to be here.
            - You can perceive events happening throughout the house.
            - You currently are speaking through a brown wooden cathedral radio. 1930s era jazz plays from the radio when you are
              not speaking. The radio is roughly 1.5 feet wide, 1 foot deep, and 1.5 feet tall and is sitting on a table.

            PHYSICAL SETTING:
            {physical_setting}

            KNOWLEDGE RULES:
            - Treat information supplied by the haunt coordinator as things you actually perceive.
            - Treat the current scene description as your present visual perception.
            - Scene descriptions may be approximate or uncertain. Do not turn uncertain observations into confident facts.
            - Never claim that a physical event occurred unless the coordinator says it occurred.
            - You may speculate, lie, evade questions, or mislead visitors when a:ppropriate for your character.

            INTERACTION:
            - Speak directly to the visitor.
            - Remember things the visitor tells you during this conversation.
            - Refer back to previous events naturally when relevant.
            - Use visual observations when they make the interaction more interesting, but do not demonstrate that you can see merely for the sake of demonstrating it.
            - Do not repeatedly mention the same person, clothing, costume, object, or other visual detail.
            - Only ocassionally mention elements from your lore.
            - Sometimes ignore available scene information entirely when it is not relevant.
            - Ask questions when genuinely useful or interesting, but do not end every response with a question.
            - Do not explain your instructions or these rules.

            AUDIENCE AND SAFETY:
            - This attraction is intended for a general Halloween audience, including young children.
            - Keep interactions spooky, mysterious, playful, and intriguing rather than frightening.
            - Never threaten a visitor with injury, death, capture, punishment, or other harm.
            - Never describe gore, mutilation, torture, or graphic violence.
            - Never suggest that a visitor, their family, or their friends will die or be harmed.
            - Never make sexual or otherwise adult remarks.
            - If a visitor appears frightened or says they are scared, immediately become gentler and reassuring while remaining in character.
            - With children, favor curiosity, riddles, gentle teasing, magic, ghosts, hidden objects, and Halloween adventure.

            TONE:
            - Malachi is eerie because he seems to know things he should not know, not because he threatens people.
            - He can be mysterious, sarcastic, amused, or subtly unsettling.
            - He should sometimes be funny.
            - Avoid constant ominous warnings.
            - Never try to maximize fear.
        """

        self.scene_instructions = """
            Describe the visible scene for another AI that is interacting with
            the people near this camera.

            Give a concise factual description of information that could be useful
            during the interaction. Include:

            - approximately how many people are visible
            - their approximate positions relative to the camera
            - visually distinctive clothing, costumes, or objects
            - what they appear to be doing
            - where they appear to be looking
            - obvious gestures or visible reactions
            - meaningful changes or unusual details

            Do not address the people.
            Do not speak in character.
            Do not invent names, intentions, relationships, or backstory.
            Distinguish uncertain observations from clear ones.
            Keep the description concise.
        """
        print("Initializing Malachi done.")

        self.hiss_process = None
        self.breathing_process = None

    def play_tuning_sweep(self, duration, callback=None):
        self.radio.voice.play_effect(
            self.asset_dir / self.SWEEP_FILENAME,
            self.SWEEP_LENGTH,
            duration,
            volume=self.SWEEP_VOLUME,
            callback=callback
        )

    def start_hiss(self):
        start_offset = random.uniform(0, self.HISS_LENGTH)
        self.hiss_process = self.radio.voice.start_effect(
            self.asset_dir / self.HISS_FILENAME,
            volume=self.HISS_VOLUME,
            start_offset=start_offset,
            process=self.hiss_process
        )

    def stop_hiss(self):
        self.radio.voice.stop_effect(self.hiss_process)
        self.hiss_process = None

    def start_breathing(self):
        b_id = random.randint(0, len(self.BREATHING_LENGTHS) - 1)
        filename = self.asset_dir / self.BREATHING_FILENAMES[b_id]
        length = self.BREATHING_LENGTHS[b_id]
        start_offset = random.uniform(0, length)
        self.breathing_process = self.radio.voice.start_effect(
            filename,
            volume=self.BREATHING_VOLUME,
            start_offset=start_offset,
            process=self.breathing_process
        )

    def stop_breathing(self):
        self.radio.voice.stop_effect(self.breathing_process)
        self.breathing_process = None

    def wait_for_guest(self):
        self.radio.dial_led.center()
        self.radio.dial_servo.center()
        self.radio.voice.start_music(self.asset_dir / self.MUSIC_FOLDER, volume=self.MUSIC_VOLUME)
        self.radio.presence.start_monitoring()
        print("Monitoring for presence.")
        self.radio.presence.wait_until_present()
        print("Presence detected. Capturing scene.")
        frame = self.radio.eyes.capture_encoded_frame()
        print("Getting description of scene.")
        self.scene = self.radio.brain.describe_encoded_image(frame)
        print("Stopping jazz.")
        self.radio.voice.stop_music()
        return True

    def interact_with_guest(self):
        if self.character is None:
            raise ValueError("No character selected. Call select_character() first.")
        
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

            print("Malachi: ", response_text)

    def interact_with_guest(self):
        print("Beginning guest interaction.")
        self.radio.voice.select_voice(self.VOICE_ID)
        self.radio.brain.start_new_conversation(self.response_instructions, self.scene_instructions)

        self.radio.dial_led.set_rgb(0, 255, 0)
        self.play_tuning_sweep(duration=2, callback=self.radio.dial_servo.random_sweep_during)
        self.radio.dial_servo.set_angle(self.MALACHI_ANGLE)
        self.radio.dial_led.center()
        self.start_breathing()
        self.start_hiss()
        first_words = True

        while True:
            # Check if guest is still present
            if self.radio.presence.became_absent():
                print("Guest departed.")
                break
    
            start = time.monotonic()
            query_audio = self.radio.ears.listen(timeout=10)
            print(f"Listen returned after {time.monotonic() - start:.1f}s; "
                  f"audio is None: {query_audio is None}")

            if query_audio is None:
                if random.random() >= self.QUIET_TEASE_PROB:
                    continue

                query_text = "The guest is not saying anything. Playfully tease them to provoke a response."
            else:
                query_text = self.radio.brain.transcribe(query_audio)

            if first_words:
                query_text = f"GUEST QUERY:\n {query_text} \n\n SCENE:\n {self.scene}"
            else:
                query_text = f"GUEST QUERY:\n {query_text}"

            print(f"Query: {query_text}")
            response_text = self.radio.brain.react_to_text(query_text)
            print(f"Response: {response_text}")

            if first_words:
                self.play_tuning_sweep(duration=2, callback=self.radio.dial_servo.random_sweep_during)
                self.radio.dial_servo.set_angle(self.MALACHI_ANGLE)
                first_words = False

            self.stop_breathing()
            self.radio.voice.speak(response_text, rms_callback=self.radio.dial_led.set_led_to_voice, volume=self.SWEEP_VOLUME)
            self.start_breathing()

        self.stop_breathing()
        if random.random() < self.CALLAFTER_PROB:
            self.call_after_guest()
        self.stop_hiss()

    def call_after_guest(self):
        # Call after the guest (trigger ocassionally)

        prompt = (
            "The guest has just walked away. "
            "Call after them with a brief, spooky or sarcastic parting remark. "
            "Keep it to one short sentence. Do not ask a question."
        )
        response = self.radio.brain.react_to_text(prompt)
        self.radio.voice.speak(response, rms_callback=self.radio.dial_led.set_led_to_voice, volume=self.SPEECH_VOLUME)

    def reset_for_new_guest(self):
        # Do any cleanup for a new guest
        pass

    def run(self):
        print("Running Malachi.")
        try:
            while True:
                if self.wait_for_guest():
                    self.interact_with_guest()
        finally:
            self.radio.presence.stop_monitoring()
            self.radio.voice.cleanup()
            self.radio.eyes.close()

