import os
import sys
import subprocess
import random
import time
import re
import threading
from pathlib import Path
from elevenlabs.client import ElevenLabs

class Voice:
    """Handle speaking."""
    TTS_MODEL_ID = "eleven_v3_conversational"
    # TTS_MODEL_ID = "eleven_v3"
    TTS_OUTPUT_FORMAT="mp3_44100_128"
    TTS_VOICE_ID="Q2OX7wVoStVzaXrMZxnH" # This is the one we used previously
    # TTS_VOICE_ID = "oAOAwbMjOHfvazPLHDRc" 

    SWEEP_LENGTH = 73
    SWEEP_FILENAME = "fx/freesound_community-tuning-radio-7150.mp3"

    # Feature rich
    HISS_LENGTH = 148
    HISS_FILENAME = "fx/freesound_community-radio-noise-11-59824.mp3"
    # Plain static
    # HISS_LENGTH = 60
    # HISS_FILENAME = "fx/freesound_community-radio-static-2-26831.mp3"

    # Breathing
    BREATHING_LENGTHS = [21, 13, 29]
    BREATHING_FILENAMES = [
        "fx/freesound_community-breathing-6811.mp3",  # Plain
        "fx/freesound_community-male-breathing-slow-14558.mp3",  # Sharp
        "fx/freesound_community-man_breathing_asleep-75120.mp3"  # Asleep
    ]

    JAZZ_PLAYLIST_FILE = "jazz_playlist.txt"
    JAZZ_FOLDER = Path("./music")

    def __init__(self):
        print("Voice initializing...")
        self.tts_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

        self.jazz_files = list(self.JAZZ_FOLDER.glob("*.mp3"))
        self.create_jazz_playlist()
        self.jazz_process = None
        self.hiss_process = None
        self.breathing_process = None
        print("Voice done initializing.")

    def speak(self, text, rms_callback=None, volume=100):
        """Stream ElevenLabs MP3 directly through ffplay and support a
        callback that acts on the RMS value."""
        stream = self.tts_client.text_to_speech.stream(
            voice_id=self.TTS_VOICE_ID,
            model_id=self.TTS_MODEL_ID,
            text=text,
        )

        player = subprocess.Popen(
            [
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-loglevel", "info",
                "-volume", str(volume),
                "-af",
                (
                    "highpass=f=400,"
                    "lowpass=f=3000,"
                    "astats="
                        "metadata=1:"
                        "reset=1:"
                        "measure_perchannel=none:"
                        "measure_overall=RMS_level,"
                    "ametadata="
                        "print:"
                        "key=lavfi.astats.Overall.RMS_level"
                ),
                "-i", "pipe:0",
            ],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
        )

        # Pattern for finding the actual RMS leve in the stderr stream
        RMS_PATTERN = re.compile(
            r"lavfi\.astats\.Overall\.RMS_level=(-?[\d.]+)"
        )

        # Closure that reads the lines in stderr and parses them for RMS
        def read_levels():
            for raw_line in player.stderr:
                # Decode line from bytes (because we used text=False)
                line = raw_line.decode("utf-8", errors="replace")

                match = RMS_PATTERN.search(line)

                if match:
                    rms_db = float(match.group(1))
                    if rms_callback is not None:
                        rms_callback(rms_db)

        # Run the meter concurrently with the player to get real time RMS
        meter_thread = threading.Thread(target=read_levels, daemon=True)
        meter_thread.start()

        # Consume the stream
        try:
            for chunk in stream:
                player.stdin.write(chunk)
                player.stdin.flush()

        finally:
            player.stdin.close()
            player.wait()
            meter_thread.join()

    def play_tuning_sweep(self, duration=3.0, volume=100, callback=None):
        start = random.uniform(0, self.SWEEP_LENGTH - duration)

        player = subprocess.Popen([
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-loglevel", "error",
            "-ss", str(start),
            "-t", str(duration),
            "-volume", str(volume),
            self.SWEEP_FILENAME
        ])

        if callback is not None:
            callback(player)

        player.wait()

    def create_jazz_playlist(self):
        """Create a randomized playlist of jazz files."""
        random.shuffle(self.jazz_files)
        with open(self.JAZZ_PLAYLIST_FILE, "w") as f:
            for filepath in self.jazz_files:
                # Handle apostrophes in the filename
                filename = str(filepath.resolve()).replace("'", r"'\''")
                f.write(f"file '{filename}'\n")

    def start_jazz(self, volume=100):
        """Create and play a jazz playlist"""
        # Popen is still open
        if self.jazz_process is not None:
            # And process is still alive
            if self.jazz_process.poll() is None:
                return

            self.jazz_process = None

        self.create_jazz_playlist()
        self.jazz_process = subprocess.Popen([
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-loglevel", "error",
            "-f", "concat",
            "-safe", "0",
            "-volume", str(volume),
            "jazz_playlist.txt",
        ])

    def stop_jazz(self):
        """Stop playing jazz."""
        if self.jazz_process is not None:
            if self.jazz_process.poll() is None:
                self.jazz_process.terminate()

                try:
                    self.jazz_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.jazz_process.kill()
                    self.jazz_process.wait()

            self.jazz_process = None

    def start_hiss(self, volume=8):
        # Popen is still open
        if self.hiss_process is not None:
            # And process is still alive
            if self.hiss_process.poll() is None:
                return

            self.hiss_process = None
        
        # Start at some random location
        start = random.uniform(0, self.HISS_LENGTH)

        self.hiss_process = subprocess.Popen([
            "ffplay",
            "-nodisp",
            "-loglevel", "error",
            "-loop", "0",
            "-ss", str(start),
            "-volume", str(volume),
            self.HISS_FILENAME
        ])

    def stop_hiss(self):
        if self.hiss_process is not None:
            if self.hiss_process.poll() is None:
                self.hiss_process.terminate()

                try:
                    self.hiss_process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.hiss_process.kill()
                    self.hiss_process.wait()

        self.hiss_process = None

    def start_breathing(self, volume=100):
        # Popen is still open
        if self.breathing_process is not None:
            # And process is still alive
            if self.breathing_process.poll() is None:
                return

            self.breathing_process = None

        # Pick a random breathing noise
        b_id = random.randint(0, len(self.BREATHING_LENGTHS) - 1)

        # Start at some random location
        start = random.uniform(0, self.BREATHING_LENGTHS[b_id])

        self.breathing_process = subprocess.Popen([
            "ffplay",
            "-nodisp",
            "-loglevel", "error",
            "-loop", "0",
            "-ss", str(start),
            "-volume", str(volume),
            self.BREATHING_FILENAMES[b_id]
        ])

    def stop_breathing(self):
        if self.breathing_process is not None:
            if self.breathing_process.poll() is None:
                self.breathing_process.terminate()

                try:
                    self.breathing_process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.breathing_process.kill()
                    self.breathing_process.wait()

        self.breathing_process = None


    def cleanup(self):
        self.stop_jazz()
        self.stop_hiss()
        self.stop_breathing()

def main():
    if "ELEVENLABS_API_KEY" not in os.environ:
        print("You need to set the ElevenLabs auth key environment variable first.")
        sys.exit(1)

    all_rms = []
    def test_callback(rms):
        all_rms.append(rms)
        print(f"Dial level: {rms:.1f} dB")

    voice = Voice()
    try:
        voice.start_jazz(volume=10)
        text="[quietly] Well. Someone has come to visit.  [curious] I don't believe we've met before. Or perhaps we have. [whispers] Be careful that you do not look behind you now. [relieved] Okay. It's gone."
        time.sleep(5)
        voice.stop_jazz()

        voice.play_tuning_sweep(volume=10)
        voice.start_hiss(volume=2)
        voice.speak(text, rms_callback=test_callback, volume=30)
        time.sleep(1)
        voice.stop_hiss()
        with open("test_rms.txt", "w") as f:
            for rms in all_rms:
                f.write(f"{rms:1f}\n")

        # voice.start_jazz()
        # time.sleep(3)
        # voice.stop_jazz()

        # voice.start_breathing()
        # time.sleep(3)
        # voice.stop_breathing()

    finally:
        voice.cleanup()


if __name__ == "__main__":
    main()
