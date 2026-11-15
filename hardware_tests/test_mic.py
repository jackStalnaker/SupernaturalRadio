import time
import sounddevice as sd
from scipy.io.wavfile import write


def find_audio_device(name, direction="input"):
    channel_key = (
        "max_input_channels"
        if direction == "input"
        else "max_output_channels"
    )

    for index, device in enumerate(sd.query_devices()):
        if (
            name.lower() in device["name"].lower()
            and device[channel_key] > 0
        ):
            return index

    raise RuntimeError(f"No {direction} device named '{name}' found")

class Ears():
    def __init__(self):

        self.SAMPLE_RATE = 44100  # Sample rate in Hz
        self.DURATION = 5  # Duration of recording in seconds
        self.AUDIO_FILENAME = "haunt_speech.wav"  # Output filename
        self.INPUT_DEVICE = find_audio_device("Malachi Audio", direction="input")

    def record(self):
        audio = sd.rec(
            int(self.DURATION * self.SAMPLE_RATE),
            samplerate=self.SAMPLE_RATE,
            channels=2,
            dtype='int16',
            device=self.INPUT_DEVICE
        )
        sd.wait()  # Wait until recording is finished

        write(self.AUDIO_FILENAME, self.SAMPLE_RATE, audio)


def main():
    ears = Ears()
    print("Speak now")
    ears.record()
    print("Recording complete")


if __name__ == "__main__":
    main()
