import time
import queue
from collections import deque
from enum import Enum, auto
import sounddevice as sd
import numpy as np
from scipy.signal import resample_poly
from silero_onnx import load_silero_vad
from scipy.io.wavfile import write


class GuestSpeakState(Enum):
    SPEAKING = auto()
    SILENT_CANDIDATE = auto()
    SILENT = auto()

class Ears:
    """Malachi's Ears.
    
    This class handles listening for speech from the default sound input device.
    It uses a voice activity detector (VAD) to determine the start and end of 
    speech automatically.
    """
    SPEECH_THRESHOLD = 0.25     # Silero probability of speech
    END_SILENCE = 1.0           # seconds

    # Sound device sampling
    HARDWARE_RATE = 48000       # samples/sec
    BLOCK_SIZE = 7680           # 7680/48000 = 160 msec which divides into 5 Silero blocks

    # VAD sampling. It's different: mono and lower rate
    VAD_RATE = 16000            # samples/sec
    VAD_BLOCK_SIZE = 512        # 512/16000 = 32 msec
    END_SILENCE_FRAMES = round(END_SILENCE * VAD_RATE / VAD_BLOCK_SIZE)

    # Recorded speech
    AUDIO_FILENAME = "haunt_speech.wav"  # Output filename

    # Voting
    TOTAL_VOTES = 5
    PASSING_VOTES = 3

    def __init__(self):
        print("Ears initializing...")
        self.model = load_silero_vad()   # VAD model
        self.audio_queue = queue.Queue() # audio stream MT queue
        self.vad_buffer = np.array([], dtype=np.float32)  # buffer for VAD processing

        # Keep a buffer to capture any missed speech just before detection
        # using a deque automatically pushes the oldest off conveniently
        self.pre_roll = deque(maxlen=10)  # 10 blocks at 160 msec
        self.speech_audio = []           # recorded speech

        # Voting
        self.votes = deque(maxlen=self.TOTAL_VOTES)     # Deque for voting 

        # State
        self.speak_state = GuestSpeakState.SILENT

        # hardware config
        self.find_audio_device("Malachi Audio")
        print("Ears done initializing.")

    def find_audio_device(self, name, direction="input"):
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
                self.hardware_device = index
                self.hardware_channels = device[channel_key]
                return index, device[channel_key]

        raise RuntimeError(f"No {direction} device named '{name}' found")

    def listen(self, timeout=None):
        """Listen to audio device and process each block for speech. Returns if speech is recorded.

        Args:
            timeout (Number):
                Seconds of listening to silence before giving up
        
        Returns:
            (np.array or None): Audio as blocks in a numpy array or None
        """
        start = time.monotonic()
        with sd.InputStream(
            device=self.hardware_device,
            samplerate=self.HARDWARE_RATE,
            channels=self.hardware_channels,
            dtype="int16",                # Need this for compatibility with simultaneous playback
            blocksize=self.BLOCK_SIZE,
            callback=self.audio_callback
        ):
            while True:
                audio_block = self.audio_queue.get()
                speech = self.process_audio(audio_block)
                if speech is not None:
                    break
                if timeout is not None and (time.monotonic() - start) > timeout:
                    break
        return speech

    def audio_callback(self, indata, frames, time_info, status):
        """Put this block of audio in a queue to be processed."""
        if status:
            print(status)
        self.audio_queue.put(indata.copy())

    def process_audio(self, block):
        """Process a block of audio, looking for speech and recording any that is present."""
        # Save pre-roll
        self.pre_roll.append(block)

        # If the guest is currently speaking or potentially pausing, save this block
        if self.speak_state in [GuestSpeakState.SPEAKING, GuestSpeakState.SILENT_CANDIDATE]:
            self.speech_audio.append(block)

        # INMP441 is on the left I2S channel
        audio_mono = block[:, 0].astype(np.float32) / 32768.0  # 7056 samples (0.16 s) normalized

        # Resample 44.1 kHz -> 16 kHz
        audio_16k = resample_poly(audio_mono, 1, 3) # 2560 samples (0.16 s)

        # Add the new samples to what Silero hasn't consumed yet
        # This is an artifact of when the samples did not align in VAD space and in 
        # device audio space, but I'm keeping it in case we need to go back. With 
        # aligned sizes, this could just be a range loop through audio_16k
        self.vad_buffer = np.concatenate((self.vad_buffer, audio_16k))

        # Give Silero a block of size VAD_BLOCK_SIZE at a time
        while len(self.vad_buffer) >= self.VAD_BLOCK_SIZE:
            block = self.vad_buffer[:self.VAD_BLOCK_SIZE]
            self.vad_buffer = self.vad_buffer[self.VAD_BLOCK_SIZE:]

            # See if Silero thinks the VAD frame is speech
            probability = self.model(block, self.VAD_RATE).item()
            self.votes.append(probability >= self.SPEECH_THRESHOLD)

            # Speech detected with a voting scheme
            if len(self.votes) == self.TOTAL_VOTES and sum(self.votes) >= self.PASSING_VOTES:
                if self.speak_state == GuestSpeakState.SILENT:
                    self.speech_audio = list(self.pre_roll)

                self.speak_state = GuestSpeakState.SPEAKING
                self.silent_frames = 0
                # print(f"Speech detected: {sum(self.votes)} out of {self.TOTAL_VOTES}")

            # Speech has possibly stopped, but not sure yet
            elif self.speak_state == GuestSpeakState.SPEAKING:
                self.speak_state = GuestSpeakState.SILENT_CANDIDATE
                self.silent_frames = 1
                # print(f"Speech has possibly stopped {self.votes}")

            # Speech is still stopped, so let's check if it's been stopped long enough to move on.
            elif self.speak_state == GuestSpeakState.SILENT_CANDIDATE:
                self.silent_frames += 1
                if self.silent_frames >= self.END_SILENCE_FRAMES:
                    # speaking is officially done. 
                    self.speak_state = GuestSpeakState.SILENT
                    audio = np.concatenate(self.speech_audio, axis=0)
                    self.speech_audio = []
                    self.votes.clear()
                    # print(f"heading off to transcribe")
                    return audio
        return None

    def write_audio(self, audio):
        write(self.AUDIO_FILENAME, self.HARDWARE_RATE, audio)


def main():
    ears = Ears()
    while True:
        audio = ears.listen()
        ears.write_audio(audio)
        print(f"heading off to transcribe")
        time.sleep(2)

if __name__ == "__main__":
    main()
