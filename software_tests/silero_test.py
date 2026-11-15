import sounddevice as sd
import torch

from silero_vad import load_silero_vad

SAMPLE_RATE = 16000
BLOCK_SIZE = 512

model = load_silero_vad()

print("Listening. Ctrl-C to stop.")

try:
    while True:
        audio = sd.rec(
            BLOCK_SIZE,
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            device=4
        )
        sd.wait()

        peak = abs(audio).max()
        samples = torch.from_numpy(audio[:, 0])

        probability = model(samples, SAMPLE_RATE).item()

        print(f"peak={peak:.4f}  speech={probability:.3f}")

except KeyboardInterrupt:
    print("\nStopped.")