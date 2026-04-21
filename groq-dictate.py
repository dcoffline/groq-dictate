#!/usr/bin/env python3
import evdev
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from groq import Groq
from evdev import InputDevice, ecodes
import pyperclip
import threading
import os
import sys
import queue
import subprocess
import shutil

# --- CONFIG ---
GROQ_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "whisper-large-v3-turbo"
SAMPLE_RATE = 48000  # Standard for PipeWire
TILDE_KEYCODE = 97   # Right Ctrl

# Audio Queue
audio_queue = queue.Queue()
recording_event = threading.Event()

# --- HELPER: Send Desktop Notification ---
def notify(title, message, icon="input-microphone"):
    """Sends a desktop notification using notify-send."""
    # Ensure we can find the command
    cmd = shutil.which("notify-send")
    if not cmd:
        print("Error: 'notify-send' not found. Install libnotify.", file=sys.stderr)
        return

    try:
        # We use the synchronous hint to update the existing bubble instead of stacking them
        subprocess.Popen([
            cmd, "-t", "3000",
            "-h", "string:x-canonical-private-synchronous:groq",
            "-i", icon, title, message
        ])
    except Exception as e:
        print(f"Notification Error: {e}", file=sys.stderr)

# --- HELPER: Find Best Keyboard (Score-based) ---
def find_any_keyboard():
    print("Scanning for keyboard...")
    candidates = []

    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            caps = device.capabilities()
            if ecodes.EV_KEY in caps:
                supported_keys = caps[ecodes.EV_KEY]

                # RULE 1: It MUST have the Right-Ctrl key (Code 97)
                if TILDE_KEYCODE in supported_keys:
                    score = 0
                    name = device.name.lower()

                    # RULE 2: Prioritize "Real" Keyboards
                    if "keyboard" in name:
                        score += 10

                    # RULE 3: Penalize Dongles/Receivers/Mice
                    if "receiver" in name:
                        score -= 5
                    if "mouse" in name:
                        score -= 5
                    if "passthrough" in name:
                        score -= 10

                    candidates.append((score, device))

        if candidates:
            # Sort by score (highest first)
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_score, best_device = candidates[0]
            print(f"✔ Selected Best Keyboard: '{best_device.name}' (Score: {best_score})")
            return best_device.path

    except Exception as e:
        print(f"Error scanning input devices: {e}")
    return None

# --- SETUP ---
if not GROQ_KEY:
    print("FATAL: GROQ_API_KEY not set.")
    notify("Groq Error", "API Key not set!", "dialog-error")
    sys.exit(1)

# 1. Auto-Detect Keyboard
DEVICE_PATH = find_any_keyboard()
if DEVICE_PATH is None:
    print("FATAL: No keyboard detected. (Permission issue?)")
    notify("Groq Error", "No keyboard detected.", "dialog-error")
    sys.exit(1)

# 2. Use System Default Mic
print("✔ Using System Default Microphone")

client = Groq(api_key=GROQ_KEY)

def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio Status: {status}", file=sys.stderr)
    if recording_event.is_set():
        audio_queue.put(indata.copy())

def transcribe():
    frames = []
    while not audio_queue.empty():
        frames.append(audio_queue.get())

    if not frames:
        return

    notify("Groq AI", "🧠 Thinking...", "dialog-information")
    print(" -> Transcribing...")

    try:
        audio = np.concatenate(frames)
        path = "/tmp/grok.wav"
        wavfile.write(path, SAMPLE_RATE, audio.astype(np.int16))

        with open(path, "rb") as f:
            text = client.audio.transcriptions.create(model=MODEL, file=f).text.strip()

#        if text:
#            try:
#                subprocess.run(['wl-copy'], input=text.encode('utf-8'), check=True)
#                print(f"COPIED via Wayland: {text}")
#                notify("Groq AI", f"✅ Copied:\n{text}", "edit-copy")
#            except Exception as e:
#                print(f"Clipboard Error: {e}")
#                # Fallback to pyperclip just in case you ever switch back to X11
#                pyperclip.copy(text)
#            print(f"COPIED: {text}")
#            notify("Groq AI", f"✅ Copied:\n{text}", "edit-copy")
#        else:
#            print(" (Silence detected)")
#            notify("Groq AI", "❌ No speech detected.", "dialog-error")

        if text:
            success = False
            # Force the script to use the socket that actually exists
            if os.path.exists("/run/user/1000/wayland-1"):
                os.environ["WAYLAND_DISPLAY"] = "wayland-1"
            # Step 1: Attempt Wayland copy
            try:
                # We don't check the variable here; we just try the command.
                # If wl-copy is installed, it will try to find the socket automatically.
                subprocess.run(['wl-copy'], input=text.encode('utf-8'), check=True, capture_output=True)
                print(f"✔ COPIED (Wayland): {text}")
                success = True
            except Exception as e:
                # If it fails, it's likely because the systemd service doesn't
                # know which Wayland socket to talk to.
                print(f"Wayland Copy Failed: {e}")

            # Step 2: Fallback to pyperclip
            if not success:
                try:
                    pyperclip.copy(text)
                    print(f"✔ COPIED (Pyperclip fallback): {text}")
                    success = True
                except Exception as e:
                    print(f"Clipboard Error: {e}")

            # Step 3: Notify once
            if success:
                notify("Groq AI", f"✅ Copied:\n{text}", "edit-copy")
            else:
                notify("Groq Error", "Failed to copy to clipboard", "dialog-error")

    except Exception as e:
        print(f"API Error: {e}")
        notify("Groq Error", str(e), "dialog-error")

# --- MAIN LOOP ---
print(f"READY. Hold R-CTL on {DEVICE_PATH} to record.")
notify("Groq AI", "Ready to Dictate", "input-keyboard")

try:
    dev = InputDevice(DEVICE_PATH)

    with sd.InputStream(device=None,
                        samplerate=SAMPLE_RATE,
                        channels=1,
                        dtype='int16',
                        callback=audio_callback):

        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY and event.code == TILDE_KEYCODE:
                if event.value == 1 and not recording_event.is_set():
                    # KEY DOWN: Start Recording
                    with audio_queue.mutex:
                        audio_queue.queue.clear()
                    print("Recording...", end="", flush=True)
                    notify("Groq AI", "🎤 Listening...", "input-microphone")
                    recording_event.set()

                elif event.value == 0 and recording_event.is_set():
                    # KEY UP: Stop Recording
                    recording_event.clear()
                    print(" Stop.", end="", flush=True)
                    threading.Thread(target=transcribe, daemon=True).start()

except KeyboardInterrupt:
    print("\nExiting...")
except OSError as e:
    print(f"\nFATAL: Device permission error or disconnect: {e}")
    notify("Groq Error", "Keyboard disconnected or permission denied.", "dialog-error")
