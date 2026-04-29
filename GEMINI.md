# Groq Dictate - Gemini AI Assistant Context

## Project Overview
`groq-dictate` is a lightweight, global hotkey dictation script for Linux. It uses Groq's Whisper API (`whisper-large-v3-turbo`) for near-instant transcription and auto-pastes the result into the active window. It listens for a specific keycode (default: Right Control - 97) using `evdev`.

## Architecture & Requirements
- **Input:** Reads raw keyboard events from `/dev/input/`. The user must be in the `input` group.
- **Audio:** Uses `sounddevice` and `portaudio` (or ALSA/PulseAudio mapped in containers) to record the mic.
- **Output:** Uses `wl-clipboard` (`wl-copy`) for Wayland and falls back to `pyperclip` (X11) to copy text, then relies on the user pasting or the system context.
- **Notifications:** Uses `notify-send` for desktop feedback.

## Installation Methods
The project supports two main execution paths:
1. **Containerized (Recommended):** Uses Podman and systemd Quadlets. 
   - Files: `Containerfile`, `groq.container`, `install.sh`, `uninstall.sh`.
   - The container maps hardware devices (`/dev/input`), DBus, Wayland sockets, and PulseAudio/PipeWire sockets to run seamlessly in the background.
2. **Manual (Python venv):** Native execution using a Python virtual environment.
   - Files: `requirements.txt`, `start-groq` (legacy wrapper).

## Recent Work (April 29, 2026)
- **Containerization Installer:** Added `install.sh` and `uninstall.sh` to automate the Podman build, prompt for the `GROQ_API_KEY` (saving to `~/.secrets`), and set up the systemd Quadlet (`~/.config/containers/systemd/groq.container`).
- **Documentation:** Rewrote `README.md` to clearly present both the Containerized (Recommended) and Manual (venv) installation methods so no user base is excluded.

## Future Development Notes
- If modifying dependencies, remember to update both `requirements.txt` and the system packages in the `Containerfile`.
- When updating `groq-dictate.py`, the container image needs to be rebuilt (`podman build ...`) for changes to reflect in the background service.
- The default system Wayland display is assumed as `wayland-0` but has fallback logic in `groq-dictate.py` for `wayland-1`.
