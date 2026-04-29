#!/bin/bash

# uninstall.sh - Uninstaller for containerized groq-dictate

QUADLET_DIR="$HOME/.config/containers/systemd"
QUADLET_FILE="groq.container"

echo "🗑️  Uninstalling groq-dictate..."

# 1. Stop and disable the service
if systemctl --user is-active --quiet groq.service; then
    echo "Stopping groq service..."
    systemctl --user stop groq.service
fi

if systemctl --user is-enabled --quiet groq.service &>/dev/null; then
    echo "Disabling groq service..."
    systemctl --user disable groq.service
fi

# 2. Remove the Quadlet file
if [ -f "$QUADLET_DIR/$QUADLET_FILE" ]; then
    echo "Removing Quadlet file..."
    rm "$QUADLET_DIR/$QUADLET_FILE"
fi

# 3. Reload systemd
echo "Reloading systemd..."
systemctl --user daemon-reload

# 4. Optional: Remove the image
read -p "Do you want to remove the Podman image (groq-dictate)? [y/N]: " remove_image
if [[ "$remove_image" =~ ^[Yy]$ ]]; then
    echo "Removing Podman image..."
    podman rmi groq-dictate
fi

echo "✅ Uninstallation complete."
