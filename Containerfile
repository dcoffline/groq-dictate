# Use a lightweight Python base
FROM python:3.11-slim

# Install system libraries for audio, Wayland, notifications, AND evdev build tools
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    portaudio19-dev \
    alsa-utils \
    libnotify-bin \
    wl-clipboard \
    dbus \
    gcc \
    linux-libc-dev \
    libpulse0 \
    libasound2-plugins \
    && rm -rf /var/lib/apt/lists/*

# Force ALSA to route through the PulseAudio plugin
RUN printf "pcm.!default {\n    type pulse\n}\nctl.!default {\n    type pulse\n}\n" > /etc/asound.conf

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual script
COPY groq-dictate.py .

# Run unbuffered so logs flow directly to journalctl
CMD ["python", "-u", "groq-dictate.py"]
