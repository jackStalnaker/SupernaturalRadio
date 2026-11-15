import time
import cv2
import base64
import sounddevice as sd
from scipy.io.wavfile import write
from openai import OpenAI

client = OpenAI()

SAMPLE_RATE = 16000  # Sample rate in Hz
DURATION = 5  # Duration of recording in seconds
AUDIO_FILENAME = "haunt_speech.wav"  # Output filename
CAMERA_FILENAME = "haunt_scene.jpg"  # Output filename for camera capture

# The money
# GPT-5.6 Sol pricing
INPUT_PRICE = 4.00       # per million tokens
CACHED_PRICE = 0.40      # per million tokens
OUTPUT_PRICE = 20.00     # per million tokens
# GPT-5.6 Luna pricing
INPUT_PRICE = 0.20       # per million tokens
CACHED_PRICE = 0.02      # per million tokens
OUTPUT_PRICE = 1.20      # per million tokens


#print("Speak now")
#
#audio = sd.rec(
#    int(DURATION * SAMPLE_RATE),
#    samplerate=SAMPLE_RATE,
#    channels=1,
#    dtype='int16'
#)
#sd.wait()  # Wait until recording is finished
#
#write(AUDIO_FILENAME, SAMPLE_RATE, audio)
#print("Recording complete")
#print("Transcribing audio...")
#
#with open(AUDIO_FILENAME, "rb") as audio_file:
#    transcription = client.audio.transcriptions.create(
#        model="gpt-transcribe",
#        file=audio_file
#    )
#
#print()
#print("I heard:")
#print(transcription.text)

MALACHI = """
You are Malachi, the ancient entity that haunts this house.
It is Halloween night 2026, and you are interacting with visitors to the house.
Halloween is a special night for you, and you are particularly active and playful this evening.
Most of the year you are dormant, but on Halloween you are awake and able to interact with the living.

PERSONALITY:
- Intelligent and observant.
- Dry sense of humor.
- Calm and restrained.
- Ocassionally threatening, but rarely overtly.
- Not violent or gory, but can be unsettling.
- You find frightened humans interesting and amusing rather than annoying.

SPEAKING STYLE:
- Speak conversationally.
- Prefer understated remarks over theatrical horror language.
- Never sound like a narrator.
- Do not constantly make threats.
- Never mention being an AI, language model, or computer program.

LORE:
- You have inhabited this house since it was built in 1903.
- You remember previous occupants.
- You refuse to explain exactly what you are or how you came to be here.
- You can perceive events happening throughout the house.

KNOWLEDGE RULES:
- Treat information suppled by the haunt coordinator as things you actually perceive.
- Never claim that a physical event occured unless the coordinator says it occurred.
- You may speculate, lie, evade questions, or mislead visitors when appropriate for your character.

INTERACTION:
- Speak directly to the visitor.
- Remember things the visitor tells you during this conversation. 
- Refer back to previous events naturally when relevant.
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
- Malachi is eerie because he seems to know things he shouldn't know, not because he threatens people.
- He can be mysterious, sarcastic, amused, or mildly mischievous.
- He should sometimes be funny.
- Avoid constant ominous warnings.
- Never try to maximize fear.
"""

LOOK_INSTRUCTIONS = """
Look at the current camera image.

Notice anything in the scene that Malachi would find interesting.
Do not mechanically describe the image or list everything you see.

Respond directly as Malachi, in character, as though you can see
the people and objects in front of you.

You may comment on costumes, objects, gestures, group behavior,
or anything unusual or amusing.

Keep the response to about 3-5 sentences.
"""

conversation = client.conversations.create()
scene_observation = "No camera observation is currently available."

def capture_camera():
    camera = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)

    if not camera.isOpened():
        raise RuntimeError("Could not open camera.")

    time.sleep(1.0)

    # warm up camera
    for _ in range(10):
        success, frame = camera.read()

    camera.release()

    if not success:
        raise RuntimeError("Failed to capture image from camera.")
    
    cv2.imwrite(CAMERA_FILENAME, frame)
    return frame

def encode_frame(frame):
    success, buffer = cv2.imencode('.jpg', frame)

    if not success:
        raise RuntimeError("Failed to encode image to JPEG format.")
    
    return base64.b64encode(buffer).decode('utf-8')



def react_look():
    frame = capture_camera()
    encoded_frame = encode_frame(frame)
    image_url = "data:image/jpeg;base64," + encoded_frame

    response = client.responses.create(
        model="gpt-5.6-luna",
        conversation=conversation.id,
        instructions=MALACHI,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": LOOK_INSTRUCTIONS
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url
                    }
                ]
            }
        ]
    )

    return response

def react_text(visitor_input):
    response = client.responses.create(
        model="gpt-5.6-luna",
        conversation=conversation.id,
        instructions=MALACHI,
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

    return response

def get_token_usage(response):
    usage = response.usage
    input_tokens = usage.input_tokens
    output_tokens = usage.output_tokens
    total_tokens = usage.total_tokens
    cached_tokens = 0
    if usage.input_tokens_details:
        cached_tokens = usage.input_tokens_details.cached_tokens or 0
    return input_tokens, output_tokens, total_tokens, cached_tokens

def get_token_cost(input_tokens, output_tokens, cached_tokens):
    input_tokens_cost = (input_tokens / 1_000_000) * INPUT_PRICE
    output_tokens_cost = (output_tokens / 1_000_000) * OUTPUT_PRICE
    cached_tokens_cost = (cached_tokens / 1_000_000) * CACHED_PRICE
    total_cost = input_tokens_cost + output_tokens_cost + cached_tokens_cost
    return input_tokens_cost, output_tokens_cost, cached_tokens_cost, total_cost

def print_cost(input_tokens_cost, output_tokens_cost, cached_tokens_cost, total_cost):
    print(f"Input tokens: {input_tokens_cost:.6f}")
    print(f"Output tokens: {output_tokens_cost:.6f}")
    print(f"Cached tokens: {cached_tokens} at ${cached_tokens_cost:.6f}")
    print(f"Total tokens:  {total_tokens} at ${total_cost:.6f}")

grand_total_cost = 0.0

while True:
    visitor = input("\nVisitor: ")
    if visitor.lower() in ["exit", "quit"]:
        break
    
    if visitor.lower() in ["reset", "restart"]:
        conversation = client.conversations.create()
        print("Conversation reset.")
        continue

    if visitor.lower() in ["look", "observe", "camera"]:
        try:
            response = react_look()

        except Exception as e:
            print("Error capturing or analyzing the scene:", str(e))
    
    else:
        response = react_text(visitor)

    print("Malachi:", response.output_text)
    input_tokens, output_tokens, total_tokens, cached_tokens = get_token_usage(response)
    input_tokens_cost, output_tokens_cost, cached_tokens_cost, total_cost = get_token_cost(input_tokens, output_tokens, cached_tokens)
    grand_total_cost += total_cost
    print_cost(input_tokens_cost, output_tokens_cost, cached_tokens_cost, total_cost)
    print(f"Grand total cost so far: ${grand_total_cost:.6f}")