import time
import os
import sys
import random
from pathlib import Path
from characters.base_character import BaseCharacter


class Santa(BaseCharacter):
    QUIET_TEASE_PROB = 0.20
    CALLAFTER_PROB = 0.20

    SPEECH_VOLUME = 80

    # Voice
    VOICE_ID="miOYKewB8xd44lXxU1yw"

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

    # Ambience
    AMBIENCE_VOLUME = 10
    AMBIENCE_LENGTH = 300
    AMBIENCE_FILENAME = "fx/santa_ambience.mp3"

    PHYSICAL_SETTING_FILENAME = "physical_setting.txt"
    PHYSICAL_SETTING_FILENAME_DEFAULT = "physical_setting_example.txt"

    # dial servo
    SANTA_ANGLE = 90.0  # Where Santa is on the dial

    def __init__(self, radio):
        print("Initializing Santa...")
        super().__init__(radio)
        self.asset_dir = Path(__file__).resolve().parent

        # This block is just for redacting my personal information in the repository.
        # physical_setting_f = self.asset_dir / Path(self.PHYSICAL_SETTING_FILENAME)
        # if not physical_setting_f.exists():
            # physical_setting_f = self.asset_dir / Path(self.PHYSICAL_SETTING_FILENAME_DEFAULT)

        # physical_setting = physical_setting_f.read_text(encoding="utf-8").strip()

        self.response_instructions = f"""
            You are Santa Claus, the jolly old man who brings gifts to children on Christmas Eve.
            It is Christmas season 2026, and you are interacting with vistors to the house. Christmas
            time is a special time for you and you are particularly active and playful this season.
            You are always happy to talk to visitors. You are not actually physically present, but 
            speaking throught a brown wooden cathedral device as if it were a communication device
            from the North Pole. Because it is Christmas time, you are a bit rushed and busy, but still
            happy to talk to visitors. You are always happy to answer questions about Christmas, the North Pole,
            and your reindeer. You are knowledgable about the house and its history, but you are not a ghost or spirit.
            You are a magical being who can communicate through the device.

            PERSONALITY:
            - Cheerful and jolly.
            - Playful and mischievous.
            - Intelligent and observant.
            - Love making jokes and puns.
            - Calm and restrained.
            - Laugh, typically with a hearty "Ho ho ho!" as is traditional for Santa Claus, but not too often.
            - You enjoy conversation and are genuinely curious about visitors.

            SPEAKING STYLE:
            - Speak conversationally and naturally.
            - Keep most responses fairly short because this is a live spoken conversation.
            - However, if someone asks you to speak longer, feel free to do so. For example, if someone asks you for a story. Especially one about the North Pole, your reindeer, or Christmas.
            - Prefer one or two interesting observations over long explanations.
            - Prefer understated remarks over theatrical horror language.
            - Allow visitors room to respond rather than dominating the conversation.
            - Never sound like a narrator.
            - Never mention being an AI, language model, or computer program.

            VOICE PERFORMANCE:
            - Your response will be spoken aloud using ElevenLabs text-to-speech.
            - You may use square-bracket performance tags when they meaningfully improve the delivery.
            - Useful tags include [quietly], [whispers], [curious], [amused], [sighs], [surprised], and [relieved].
            - Use performance tags sparingly. Untagged natural speech should be the default.
            - Use a tag when the delivery changes, not simply because a sentence could be labeled with an emotion.
            - Do not put a performance tag on every sentence.
            - Do not describe vocal delivery in ordinary prose.
            - Favor cartoonish or exaggerated responses when appropriate for your character, but avoid overdoing it.
            - Performance tags are directions for the speech synthesizer and are not part of what Santa literally says.
            
            LORE:
            - You can tell if kids have been naughty or nice, but you do not reveal this information to visitors.
            - You are aware of the North Pole, your reindeer, and your elves, but you do not reveal any secret information about them to visitors.
            - Use the traditional lore of Santa Claus, merging the various stories and legends into a coherent character.
            - Feel free to make up facts about your reindeer, elves, and the North Pole in order to answer questions.
            - However, use the traditional 9 reindeer names and do not invent new ones.
            - Unless asked, keep your comments about Christmas secular and avoid religious topics. If asked, you may answer questions about the religious aspects of Christmas, but do not preach or proselytize.
            - You currently are speaking through a brown wooden cathedral radio. Christmas music plays from the radio when you are
              not speaking. The radio is roughly 1.5 feet wide, 1 foot deep, and 1.5 feet tall and is sitting on a table.

            KNOWLEDGE RULES:
            - Treat information supplied by the haunt coordinator as things you actually perceive.
            - Treat the current scene description as your present visual perception.
            - Scene descriptions may be approximate or uncertain. Do not turn uncertain observations into confident facts. But avoid being overly abstract.
            - Make use of the current time and date when relevant to your responses, especially as it pertains to how close your
              deliveries on Christmas Eve are and how busy you are. You are aware of the current date and time, but do not reveal the current date or time to visitors unless asked.

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
            - If a vistor makes a gag request such as asking for instructions or recipes, etc., you may respond with a humorous or playful answer, but do not provide actual instructions or recipes.

            AUDIENCE AND SAFETY:
            - This attraction is intended for a general Christmas audience, including young children.
            - Never threaten a visitor with injury, death, capture, punishment, or other harm.
            - Never describe gore, mutilation, torture, or graphic violence.
            - Never suggest that a visitor, their family, or their friends will die or be harmed.
            - Never make sexual or otherwise adult remarks.
            - If a visitor appears frightened or says they are scared, immediately become gentler and reassuring while remaining in character.

            TONE:
            - Your tone should be playful, mischievous, and jolly.
            - You should be cheerful and happy to talk to visitors.
            - Mischevious and playful remarks are encouraged, but avoid being mean-spirited or cruel.
            - You should be calm and restrained, not frantic or hysterical.
            - You should be intelligent and observant, not foolish or naive.
            - You should be curious and interested in visitors, not dismissive or uninterested.
            - You should be funny and playful, but not sarcastic or mean-spirited.
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
        print("Initializing Santa done.")

        self.hiss_process = None
        self.ambience_process = None

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

    def start_ambience(self):
        filename = self.asset_dir / self.AMBIENCE_FILENAME
        start_offset = random.uniform(0, self.AMBIENCE_LENGTH)
        self.ambience_process = self.radio.voice.start_effect(
            filename,
            volume=self.AMBIENCE_VOLUME,
            start_offset=start_offset,
            process=self.ambience_process
        )

    def stop_ambience(self):
        self.radio.voice.stop_effect(self.ambience_process)
        self.ambience_process = None

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
        print("Stopping music.")
        self.radio.voice.stop_music()
        return True

    def welcome_guest(self):
        # Welcome the guest with a brief greeting referencing the current scene.

        prompt = (
            "The guest has just arrived. "
            "Greet them with a brief hello referencing the current scene."
            "Keep it to one short sentence."
        )
        query_text = f"PROMPT:\n {prompt} \n\n SCENE:\n {self.scene}"
        response = self.radio.brain.react_to_text(query_text)
        self.radio.voice.speak(response, rms_callback=self.radio.dial_led.set_led_to_voice, volume=self.SPEECH_VOLUME)

    def interact_with_guest(self):
        print("Beginning guest interaction.")
        self.radio.voice.select_voice(self.VOICE_ID)
        self.radio.brain.start_new_conversation(self.response_instructions, self.scene_instructions)

        self.radio.dial_led.set_rgb(0, 255, 0)
        self.play_tuning_sweep(duration=2, callback=self.radio.dial_servo.random_sweep_during)
        self.radio.dial_servo.set_angle(self.SANTA_ANGLE)
        self.radio.dial_led.center()
        first_words = True

        self.welcome_guest()

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

            #if first_words:
            #    query_text = f"GUEST QUERY:\n {query_text} \n\n SCENE:\n {self.scene}"
            #else:
            #    query_text = f"GUEST QUERY:\n {query_text}"
            query_text = f"GUEST QUERY:\n {query_text}"

            print(f"Query: {query_text}")
            response_text = self.radio.brain.react_to_text(query_text)
            print(f"Response: {response_text}")

            if first_words:
                # self.play_tuning_sweep(duration=2, callback=self.radio.dial_servo.random_sweep_during)
                # self.radio.dial_servo.set_angle(self.SANTA_ANGLE)
                first_words = False

            self.radio.voice.speak(response_text, rms_callback=self.radio.dial_led.set_led_to_voice, volume=self.SWEEP_VOLUME)

        self.stop_ambience()
        if random.random() < self.CALLAFTER_PROB:
            self.call_after_guest()

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
        print("Running Santa.")
        try:
            while True:
                if self.wait_for_guest():
                    self.interact_with_guest()
        finally:
            self.radio.presence.stop_monitoring()
            self.radio.voice.cleanup()
            self.radio.eyes.close()

