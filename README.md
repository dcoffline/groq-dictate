### Groq Linux Dictation

# A lightweight, global hotkey dictation script for Linux using Groq's Whisper API.
# It listens for a specific key combination (default: Right Control) to record audio and pastes the transcription directly into your active window.

## Features
# - **Global Hotkey:** Works anywhere in the OS (using `evdev`).
# - **Instant Transcription:** Uses Groq's `whisper-large-v3-turbo` for near-instant results.
# - **Auto-Paste:** Automatically types the text where your cursor is.
# - **Smart Hardware Detection:** Automatically finds your specific keyboard device.


## Step 1: Prerequisites

# 1. System Audio Libraries
# You need the PortAudio headers installed on your system for the microphone to work.

# **Arch Linux / Manjaro / EndeavourOS:**
```bash
sudo pacman -Syu
sudo pacman -S portaudio

# **Ubuntu / Debian / Mint:**
# sudo apt-get install libportaudio2

# 2. Groq API Key
# You need an API key from Groq Console. Export it as an environment variable (recommended) or set it in your session:
export GROQ_API_KEY="gsk_your_actual_key_here"


## Step 2: Installation

# 1. Clone the repository:
git clone [https://github.com/YOUR_USERNAME/groq-linux-dictate.git](https://github.com/YOUR_USERNAME/groq-linux-dictate.git)
cd groq-linux-dictate

# 2. Create a Virtual Environment
# It is best to run this in an isolated environment to avoid conflicts with system Python.
python -m venv .venv
source .venv/bin/activate

# 3. Install Dependencies:
pip install -r requirements.txt

# 4. Usage
# Make sure your virtual environment is active:
source .venv/bin/activate

# 5. Run the script:
# Note: sudo is often required to read keyboard events from /dev/input/, unless your user is in the input group
sudo python groq_dictate.py

# 6. Dictate:
# Press and hold Right Control.
# Speak your text.
# Release the key to transcribe and paste.

# 7. Configuration
# You can edit groq_dictate.py to change the settings:

# TILDE_KEYCODE: Change the hotkey (Default is 97 for Right Ctrl).
# MODEL: Change the Whisper model.
