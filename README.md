# A multicharacter supernatural radio

This is an expansion of my Malachi haunted radio project, allowing for selectable characters. Right now,
it's just Malachi and Santa, because when Halloween was over, I realized I could repurpose the same 
radio prop as a communicator to the North Pole. 

This is a haunted radio (or whatever suitable appliance you want--he could be a haunted microwave
if you wanted). This project uses OpenAI and ElevenLabs to generate responses to queries from party
guests on the fly. It is designed to run on a Raspberry Pi. Specifically, I have my radio running on a 
Raspberry Pi Zero 2 W. If you want to run it on something else, you'll have to change the Pi specific 
hardware support, including I2S audio, the Pi camera module, and the various linux layers connected
above those. 

## TODO update remainder of README

## How Malachi interacts with a guest
Malachi's basic behavior is handled through the top-level malachi.py module. This module loads Malachi's
Eyes (camera), Ears (mic and I2S audio input), Voice (speech-to-text and I2S audio output), Brain 
(interaction with OpenAI), Presence (laser time of flight sensor), DialLED and DialServo (sorry--no
body metaphor really worked for those without obfuscating their duty).

1. Malachi plays a selection of open-source jazz. I didn't include jazz mp3s in this repo because I
do not own them, but you can find many public domain files at the Internet Archive: https://archive.org/details/1930s-jazz-big-bands.

2. While he plays, he monitors a time of flight sensor (ToF) to detect the presence of a person. 

3. On detection, Malachi takes a photo and begins an iteractive session. The photo will be incorporated in 
all responses for that session for context.

4. Using Silero's voice activity detection (VAD), Malachi will listen for a complete voice prompt or 
tease the guest if they say nothing. 

5. Malachi uses GPT's transcribe model to convert the conversation to text and then sends the text off
to GPT to formulate a response.

6. The response is converted to speech using ElevenLabs and a custom voice. You can create your own 
specter voice or use an existing one. Voices are created by prompting. 

7. Throughout the interaction, Malachi's dial will rotate for emphasis and effect. The dial light will also
ocassionally change as needed. Furthermore, the dial light will follow the level of Malachi's voice. 

At no point should the guest have to touch Malachi, so you can put him in a safe place. My Malachi is in
a reproduction cathedral radio and I disguised the camera and mic in the volume and tone knobs.

## Hardware list
1. Raspberry Pi Zero 2 W
2. Raspberry Pi Camera Module 3 Wide
3. INMP441-based MEMS microphone breakout board
4. MAX98357A mono audio amp
5. 4 inch 4 ohm speaker (came with the radio)
6. Common cathode RGB LED
7. Hobby servo
8. 5A power supply
9. Perfboard and screw terminals for power bus (don't power everything--especially the servo--through 
the raspberry Pi
10. Reproduction cathedral radio

## System Dependencies
1. ffplay
2. python3-picamera2

## Python Dependencies
1. Pathlib
2. Numpy
3. Scipy
4. sounddevice
5. board
6. gpiozero
7. openai
8. elevenlabs
9. rpi-hardware-pwm
10. adafruit-circuitpython-vl53l0x
11. silero-onnx*

*Silero onnx must be installed from source. The version in PyPi doesn't have the lightweight wrapper:
```
python -m pip install onnxruntime

git clone https://github.com/knowl-doc/silero-onnx.git
cd silero-onnx

python -m pip install -e .
```
This will pull among other things the Onnx runtime.

## Quirks to be aware of working on a Raspberry Pi
### Picamera2 needs access to system level libraries
This makes using virtual environments trickier than usual. I'm used to working with conda environments,
but without mangling the enviroment structure, conda is difficult. I used python's built-in venv for
Malachi, because you can access the system python libraries easily that way. In particular, I had to install
OpenCV and PiCamera2 through apt.

```
# Install OS-managed dependencies
sudo apt install python3-picamera2 python3-opencv python3-venv python3-dev build-essential

# Create a python virtual environment
cd ~/YOUR_MALACHI_DIR
/usr/bin/python3 -m venv --system-site-packages .venv

# Activate it
source .venv/bin/activate

# Verify PiCamera2
python -c "from picamera2 import Picamera2; print('Success')"
```

### AI account setup
You'll need an OpenAI API key and an ElevenLabs API key. You will have to pay for those, but I can tell you that on 
Halloween night, I spent a grand total of about 40 cents with people constantly talking to Malachi. About 20 cents for
OpenAI and 20 cents for ElevenLabs. 

You'll have to set two environment variables:

```
OPENAI_API_KEY
ELEVENLABS_API_KEY
```

If you are using a python environment (you should be) and want to run Malachi automatically on startup, add these to your
environment's `.env` file, which I have not included for obvious reasons. They'll be sourced when you activate the python
virtual environment conveniently.

### Music and sound effects
I did not include mine becuase I do not own them. I got the music from the internet archive. I searched for
"public domain 1930's instrumental jazz". The music goes in a folder named `music` and the playlist (which is
randomized) goes in `jazz_playlist.txt`. It has a specific format that `ffplay` uses, and I've included an example
named `jazz_playlist.txt.example`.

The sound effects go in a folder named `fx`. These I got from Freesound, and the filenames are in the source. You can 
search for those on Freesound, but I cannot include them here.

### Sound is a pain
I'm using a MEMS microphone and a mono amp through the Pi's I2S interface. You have to make some changes to your
boot config.txt file to support both. Actually setting up one or the other is not terrible, but to get both to 
work simultaneously, you have to create a single fake device that combines both. I also discovered that capacitors
on the mic and speaker power supplies are crucial or you will get a lot of annoying popping and even barely audible
audio. I'm including the overlays in the repository for the INMP441 based MEMS mic I used and the MAX98357A amp I used. 
These have to be compiled into dtbo files with dtc:
```
dtc -@ -I dts -O dtb \
    -o malachi-audio.dtbo \
    malachi-audio-overlay.dts
```
and then copied to `/boot/firmware/overlays`. In particular, I had to add to `/boot/firmeare/config.txt`:

```
dtparam=i2s=on
dtoverlay=malachi-audio
```
where malachi-audio is the name of the fake composite sound device.

### Setting the voice
I'm not sure actually if my custom Malachi voice will actually work for you. If not, you can select any voice (including a
custom one) at the Eleven Labs website. Set the voice ID at the top of `voice.py`.

### Personalizing
The best places to personalize are renaming `physical_setting_example.txt` to `physical_setting.txt` and editing it to
indicate where Malachi is actually sitting. Check the example file for things to add. The main reason the physical setting
is isolated is so that I could redact my personal information.

The other thing to change is the rest of the prompt in `brain.py`. There's nothing sacred about it.

### Automatically running on startup
To automatically run on startup, you'll need to add Malachi as a system service. Edit the included `malachi.service.example`
and save it as `/etc/systemd/system/malachi.service`. You'll need to have root privilege to do so, but that should be easy 
with a Pi. Obviously remove the arrow notes I left there.

You need to define your `OPENAI_API_KEY` and `ELEVENLABS_API_KEY` variables in your virtual environment's `.env` file.

Then enable the service with:

```
sudo systemctl daemon-reload
sudo systemctl enable --now malachi
```

You can check that Malachi is running with:

```
sudo systemctl status malachi
```

And see his output with:
```
journalctl -u malachi -f
```
