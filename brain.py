import io
import os
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

    def __init__(self):
        print("Brain initializing...")
        self.response_instructions = ""
        self.scene_instructions = ""
        self.client = OpenAI()
        self.conversation = None

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
    
    def start_new_conversation(self, response_instructions, scene_instructions):
        self.response_instructions = response_instructions
        self.scene_instructions = scene_instructions
        self.conversation = self.client.conversations.create()

    def react_to_text(self, ,visitor_input):
        response = self.client.responses.create(
            model="gpt-5.6-luna",
            conversation=self.conversation.id,
            instructions=self.response_instructions,
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
            instructions=self.scene_instructions,
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
