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

    # SWEEP_LENGTH = 73
    # SWEEP_FILENAME = "fx/freesound_community-tuning-radio-7150.mp3"

    # Feature rich
    # HISS_LENGTH = 148
    # HISS_FILENAME = "fx/freesound_community-radio-noise-11-59824.mp3"
    # Plain static
    # HISS_LENGTH = 60
    # HISS_FILENAME = "fx/freesound_community-radio-static-2-26831.mp3"

    # Breathing
    # BREATHING_LENGTHS = [21, 13, 29]
    # BREATHING_FILENAMES = [
        # "fx/freesound_community-breathing-6811.mp3",  # Plain
        # "fx/freesound_community-male-breathing-slow-14558.mp3",  # Sharp
        # "fx/freesound_community-man_breathing_asleep-75120.mp3"  # Asleep
    # ]

    MUSIC_PLAYLIST_FILE = "music_playlist.txt"

    def __init__(self):
        print("Voice initializing...")
        self.tts_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.voice_id = None

        self.music_process = None
        self.hiss_process = None
        self.breathing_process = None
        print("Voice done initializing.")

    def select_voice(self, voice_id):
        self.voice_id = voice_id

    def speak(self, text, rms_callback=None, volume=100):
        """Stream ElevenLabs MP3 directly through ffplay and support a
        callback that acts on the RMS value."""
        if self.voice_id is None:
            raise ValueError("Must select a voice first")

        stream = self.tts_client.text_to_speech.stream(
            voice_id=self.voice_id,
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

    def play_effect(self, filename, length, sample_duration, volume=100, callback=None):
        start = random.uniform(0, length - sample_duration)

        player = subprocess.Popen([
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-loglevel", "error",
            "-ss", str(start),
            "-t", str(sample_duration),
            "-volume", str(volume),
            filename
        ])

        if callback is not None:
            callback(player)

        player.wait()

    def create_music_playlist(self, music_folder):
        """Create a randomized playlist of music files."""
        music_files = list(Path(music_folder).glob("*.mp3"))
        random.shuffle(music_files)
        with open(self.MUSIC_PLAYLIST_FILE, "w") as f:
            for filepath in music_files:
                # Handle apostrophes in the filename
                filename = str(filepath.resolve()).replace("'", r"'\''")
                f.write(f"file '{filename}'\n")

    def start_music(self, music_folder, volume=100):
        """Create and play a music playlist"""
        # Popen is still open
        if self.music_process is not None:
            # And process is still alive
            if self.music_process.poll() is None:
                return

            self.music_process = None

        self.create_music_playlist(music_folder)
        self.music_process = subprocess.Popen([
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-loglevel", "error",
            "-f", "concat",
            "-safe", "0",
            "-volume", str(volume),
            "music_playlist.txt",
        ])

    def stop_music(self):
        """Stop playing music."""
        if self.music_process is not None:
            if self.music_process.poll() is None:
                self.music_process.terminate()

                try:
                    self.music_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.music_process.kill()
                    self.music_process.wait()

            self.music_process = None

    def start_effect(self, filename, volume=8, start_offset=0, process=None):
        # Popen is still open
        if process is not None:
            # And process is still alive
            if process.poll() is None:
                return

            process = None
        
        process = subprocess.Popen([
            "ffplay",
            "-nodisp",
            "-loglevel", "error",
            "-loop", "0",
            "-ss", str(start_offset),
            "-volume", str(volume),
            filename
        ])
        return process

    def stop_effect(self, process):
        if process is not None:
            if process.poll() is None:
                process.terminate()

                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

        process = None

    def cleanup(self):
        self.stop_music()

def main():
    if "ELEVENLABS_API_KEY" not in os.environ:
        print("You need to set the ElevenLabs auth key environment variable first.")
        sys.exit(1)

    all_rms = []
    def test_callback(rms):
        all_rms.append(rms)
        print(f"Dial level: {rms:.1f} dB")

    MALACHI_VOICE_ID="Q2OX7wVoStVzaXrMZxnH"
    voice = Voice()
    voice.select_voice(MALACHI_VOICE_ID)
    try:
        voice.start_music(music_folder="characters/malachi/music", volume=10)
        text="[quietly] Well. Someone has come to visit.  [curious] I don't believe we've met before. Or perhaps we have. [whispers] Be careful that you do not look behind you now. [relieved] Okay. It's gone."
        time.sleep(5)
        voice.stop_music()

        SWEEP_LENGTH = 73
        SWEEP_FILENAME = "characters/malachi/fx/freesound_community-tuning-radio-7150.mp3"
        voice.play_effect(SWEEP_FILENAME, SWEEP_LENGTH, 3, volume=10, callback=None)
        HISS_LENGTH = 148
        HISS_FILENAME = "characters/malachi/fx/freesound_community-radio-noise-11-59824.mp3"
        hiss_process = voice.start_effect(HISS_FILENAME, volume=2, start_offset=5, process=None)

        voice.speak(text, rms_callback=test_callback, volume=30)
        time.sleep(1)
        voice.stop_effect(hiss_process)
        with open("test_rms.txt", "w") as f:
            for rms in all_rms:
                f.write(f"{rms:1f}\n")

        # voice.start_music()
        # time.sleep(3)
        # voice.stop_music()

        # voice.start_breathing()
        # time.sleep(3)
        # voice.stop_breathing()

    finally:
        voice.cleanup()


if __name__ == "__main__":
    main()
