### Groq Linux Dictation

A lightweight, global hotkey dictation script for Linux using Groq's Whisper API.
It listens for a specific key combination (default: Right Control) to record audio and pastes the transcription directly into your active window.

## Features

- **Global Hotkey:** Works anywhere in the OS (using `evdev`).
- **Instant Transcription:** Uses Groq's `whisper-large-v3-turbo` for near-instant results.
- **Auto-Paste:** Automatically types the text where your cursor is (supports Wayland and X11 via fallback).
- **Smart Hardware Detection:** Automatically finds your specific keyboard device.

---

## Pre-requisite: Input Group Access
For the script to read global keyboard events without requiring `root`/`sudo`, your user must be in the `input` group. Run this on your host machine:

```bash
sudo usermod -aG input $USER
```
*(Note: You will need to log out and log back in, or reboot, for this group change to take effect).*

---

## Installation Options

You can install this tool using **Podman (Containerized - Recommended)** or **Manually (Python venv)**.

### Method 1: Containerized (Recommended)

This method isolates all dependencies inside a Podman container and runs the script continuously in the background using a systemd user service.

**Prerequisites:** `podman`, `systemd`

1. Clone the repository:
```bash
git clone https://github.com/dcoffline/groq-dictate.git
cd groq-dictate
```

2. Run the installer script:
```bash
./install.sh
```
*The script will prompt you for your Groq API key, build the container, and start the background service.*

**Managing the Service:**
- **Check Status:** `systemctl --user status groq`
- **View Logs:** `journalctl --user -u groq -f`
- **Uninstall:** Run `./uninstall.sh` from the repository folder.

---

### Method 2: Manual (Python venv)

Best if you want to modify the script directly, are developing new features, or do not use Podman/systemd.

**Prerequisites:** Python 3, System Audio Libraries

Arch Linux / Manjaro / EndeavourOS:
```bash
sudo pacman -Syu
sudo pacman -S portaudio
```
Ubuntu / Debian / Mint:
```bash
sudo apt-get update
sudo apt-get install libportaudio2 portaudio19-dev
```

1. Clone the repository:
```bash
git clone https://github.com/dcoffline/groq-dictate.git
cd groq-dictate
```

2. Set your Groq API Key:
Export it as an environment variable in your `~/.bashrc` or `~/.zshrc`:
```bash
export GROQ_API_KEY="gsk_your_actual_key_here"
```

3. Create a Virtual Environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Run the script:
Make sure your virtual environment is active, then run:
```bash
python groq-dictate.py
```
*(Note: If you skipped adding your user to the `input` group, you will need to run this with `sudo python groq-dictate.py`, which requires installing the dependencies globally or explicitly running the venv python binary as root).*

---

## Usage

1. Press and hold the **Right Control** key.
2. Speak your text.
3. Release the key. The tool will transcribe your audio and automatically paste it wherever your cursor currently is.

## Configuration

You can edit `groq-dictate.py` to change the following settings (if using the containerized version, you will need to re-run `./install.sh` to rebuild the image after making changes):

- `TILDE_KEYCODE`: Change the hotkey (Default is `97` for Right Ctrl). You can use the `evtest` command on Linux to find other keycodes.
- `MODEL`: Change the Whisper model (Default is `whisper-large-v3-turbo`).