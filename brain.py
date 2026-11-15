import io
import os
import Path
from scipy.io.wavfile import write, read
from openai import OpenAI

class Brain():
    # GPT-5.6 Sol pricing per million tokens September 2026 
    INPUT_PRICE = 4.00
    CACHED_PRICE = 0.40
    OUTPUT_PRICE = 20.00

    # GPT-5.6 Luna pricing per million tokens September 2026 
    INPUT_PRICE = 0.20
    CACHED_PRICE = 0.02
    OUTPUT_PRICE = 1.20

    PHYSICAL_SETTING_FILENAME = "physical_setting.txt"
    PHYSICAL_SETTING_FILENAME_DEFAULT = "physical_setting_example.txt"

    def __init__(self):
        print("Brain initializing...")
        self.client = OpenAI()
        self.conversation = None

        # This block is just for redacting my personal information in the repository.
        physical_setting_f = Path(PHYSICAL_SETTING_FILENAME)
        if not physical_setting_f.exists():
            physical_setting_f = Path(PHYSICAL_SETTING_FILENAME_DEFAULT)

        physical_setting = physical_setting_f.read_text(encoding="utf-8").strip()

        self.RESPONSE_INSTRUCTIONS = f"""
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

        self.SCENE_INSTRUCTIONS = """
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

        self.input_tokens = 0
        self.output_tokens = 0
        self.cached_tokens = 0
        self.total_tokens = 0
        print("Brain done initializing.")

    def transcribe(self, audio, audio_rate=44100):
        # Fake a wav file in memory because that's what OpenAI's transcribe API expects
        wav = io.BytesIO() 
        write(wav, audio_rate, audio)
        wav.seek(0)
        wav.name = "speech.wav"

        transcription = self.client.audio.transcriptions.create(
            model="gpt-transcribe",
            file=wav,
        )
        return transcription.text
    
    def start_new_conversation(self):
        self.conversation = self.client.conversations.create()

    def react_to_text(self, visitor_input):
        response = self.client.responses.create(
            model="gpt-5.6-luna",
            conversation=self.conversation.id,
            instructions=self.RESPONSE_INSTRUCTIONS,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": visitor_input
                        }
                    ]
                }
            ]
        )

        self.track_token_usage(response)
        return response.output_text

    def describe_encoded_image(self, encoded_image):
        image_url = "data:image/jpeg;base64," + encoded_image

        response = self.client.responses.create(
            model="gpt-5.6-luna",
            instructions=self.SCENE_INSTRUCTIONS,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": image_url
                        }
                    ]
                }
            ]
        )
        self.track_token_usage(response)
        return response.output_text

    def track_token_usage(self, response):
        usage = response.usage
        self.input_tokens = usage.input_tokens
        self.output_tokens = usage.output_tokens
        self.total_tokens = usage.total_tokens
        cached_tokens = 0
        if usage.input_tokens_details:
            cached_tokens = usage.input_tokens_details.cached_tokens or 0
        self.cached_tokens += cached_tokens

    @property
    def input_tokens_cost(self):
        return (self.input_tokens / 1_000_000) * self.INPUT_PRICE

    @property
    def output_tokens_cost(self):
        return (self.output_tokens / 1_000_000) * self.OUTPUT_PRICE

    @property
    def cached_tokens_cost(self):
        return (self.cached_tokens / 1_000_000) * self.CACHED_PRICE

    @property
    def total_cost(self):
        return self.input_tokens_cost + self.output_tokens_cost + self.cached_tokens_cost

    def print_cost(self):
        print(f"Input tokens: {self.input_tokens} at {self.input_tokens_cost:.6f}")
        print(f"Output tokens: {self.output_tokens} at {self.output_tokens_cost:.6f}")
        print(f"Cached tokens: {self.cached_tokens} at ${self.cached_tokens_cost:.6f}")
        print(f"Total tokens:  {self.total_tokens} at ${self.total_cost:.6f}")


def environment_check():
    if "OPENAI_API_KEY" not in os.environ:
        print("You need to set the OpenAI auth key environment variable first.")
        sys.exit(1)


if __name__ == "__main__":
    environment_check()
    brain = Brain() 
    sample_rate, audio = read("test_speech.wav")
    text = brain.transcribe(audio, audio_rate=sample_rate)
    print(text)
    brain.start_new_conversation()
    response = brain.react_to_text(text)
    print(response)

    with open("test_encoded_image.txt", "r") as f:
        encoded_image = f.read()
    response = brain.describe_encoded_image(encoded_image)
    print(response)
    brain.print_cost()
