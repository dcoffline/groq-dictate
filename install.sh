#!/bin/bash

# install.sh - Installer for containerized groq-dictate (Podman Quadlet)

set -e

# --- Configuration ---
IMAGE_NAME="groq-dictate"
CONTAINER_FILE="groq.container"
SECRETS_FILE="$HOME/.secrets"
QUADLET_DIR="$HOME/.config/containers/systemd"

echo "🚀 Installing groq-dictate (containerized)..."

# 1. Check for Podman
if ! command -v podman &> /dev/null; then
    echo "❌ Error: podman is not installed. Please install podman first."
    exit 1
fi

# 2. Build the Podman Image
echo "📦 Building Podman image: $IMAGE_NAME..."
podman build -t "$IMAGE_NAME" .

# 3. Setup Secrets
if [ ! -f "$SECRETS_FILE" ]; then
    echo "🔑 Secrets file not found at $SECRETS_FILE. Creating it..."
    touch "$SECRETS_FILE"
    chmod 600 "$SECRETS_FILE"
fi

if ! grep -q "GROQ_API_KEY" "$SECRETS_FILE"; then
    echo "⚠️  GROQ_API_KEY not found in $SECRETS_FILE."
    read -p "Please enter your Groq API Key: " api_key
    if [ -n "$api_key" ]; then
        echo "GROQ_API_KEY=$api_key" >> "$SECRETS_FILE"
        echo "✅ API Key saved to $SECRETS_FILE"
    else
        echo "❌ Error: API Key is required."
        exit 1
    fi
else
    echo "✅ GROQ_API_KEY already exists in $SECRETS_FILE"
fi

# 4. Install Quadlet
echo "📂 Installing systemd Quadlet..."
mkdir -p "$QUADLET_DIR"
cp "$CONTAINER_FILE" "$QUADLET_DIR/"

# 5. Reload systemd and Start Service
echo "🔄 Reloading systemd and starting groq service..."
systemctl --user daemon-reload
systemctl --user enable --now groq.service

echo ""
echo "🎉 Installation Complete!"
echo "-------------------------------------------------------"
echo "The groq-dictate service is now running in the background."
echo "It will automatically start when you log in."
echo ""
echo "You can check the status with:"
echo "  systemctl --user status groq"
echo ""
echo "To view logs:"
echo "  journalctl --user -u groq -f"
echo "-------------------------------------------------------"
