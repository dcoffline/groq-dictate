#!/usr/bin/env python3
import evdev
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from groq import Groq
from evdev import InputDevice, categorize, ecodes
import pyperclip
import threading
import os

GROQ_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_KEY:
    print("Error: GROQ_API_KEY environment variable not set.")
    sys.exit(1)

MODEL = "whisper-large-v3-turbo"
SAMPLE_RATE = 16000
TILDE_KEYCODE = 97  # 97 = right ctl key; 41 = ` key (unshifted ~)

# --- AUTO-DETECT KEYBOARD ---
def find_keyboard():
    # Loop through every input device on the system
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        # 1. Match the base name we know they all share
        if "Telink Macally RFKeyboard" in device.name:
            # 2. EXCLUDE the "fake" keyboards (Mouse, Media Buttons, System Control)
            if "Mouse" not in device.name and "Control" not in device.name:
                return device.path
    return None

# Run the search
DEVICE_PATH = find_keyboard()

# Error handling if it's unplugged or not found
if DEVICE_PATH is None:
    print("ERROR: Could not find 'Telink Macally RFKeyboard' (Main Device).")
    print("Check connection or permissions.")
    sys.exit(1)

print(f"Auto-detected Keyboard at: {DEVICE_PATH}")
# ---------------------

client = Groq(api_key=GROQ_KEY)
recording = False
frames = []

def record():
    global frames
    print("\nRecording... release ``` to stop")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
        while recording:
            data, _ = stream.read(int(SAMPLE_RATE * 0.1))
            frames.append(data.flatten())

def transcribe():
    global frames
    if not frames:
        return
    audio = np.hstack(frames)
    path = "/tmp/grok.wav"
    wavfile.write(path, SAMPLE_RATE, audio.astype(np.int16))
    print("Transcribing…")
    try:
        with open(path, "rb") as f:
            text = client.audio.transcriptions.create(model=MODEL, file=f).text.strip()
        pyperclip.copy(text)
        print(f"COPIED: {text}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(path):
            os.remove(path)
    frames.clear()

# Find your keyboard once
print("Finding keyboard device...")
dev = InputDevice(DEVICE_PATH)
print(f"Using: {dev.name}")

print("GROQ TURBO READY — press and release ``` anywhere")
recording = False

for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        if event.code == TILDE_KEYCODE:
            if event.value == 1 and not recording:  # key down
                recording = True
                frames.clear()
                threading.Thread(target=record, daemon=True).start()
            elif event.value == 0 and recording:  # key up
                recording = False
                threading.Thread(target=transcribe, daemon=True).start()
