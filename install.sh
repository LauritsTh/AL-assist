#!/bin/bash
set -e

# ---------------- CONFIG ----------------
REPO="https://raw.githubusercontent.com/LauritsTh/AL-assist/main"
AL_DIR="$HOME/AL-assist"
CONFIG_DIR="$HOME/.config"
ICON_DIR="$HOME/.local/share/icons"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "=== Installing AL Assistant ==="

# ---------------- CREATE FOLDERS ----------------
mkdir -p "$AL_DIR"/{src,assets,desktop,scripts}
mkdir -p "$CONFIG_DIR"
mkdir -p "$ICON_DIR"
mkdir -p "$DESKTOP_DIR"

# ---------------- DEPENDENCIES ----------------
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-gi gir1.2-gtk-4.0 playerctl aplay curl

# Optional: Ollama & Piper installation (assuming Linux)
bash -c "$(curl -fsSL $REPO/scripts/install_ollama.sh)"
bash -c "$(curl -fsSL $REPO/scripts/install_tts.sh)"

# ---------------- FETCH FILES ----------------
echo "Downloading AL files..."

# SRC files
for f in al.py al_overlay.py al_settings.py; do
    curl -fsSL $REPO/src/$f -o "$AL_DIR/src/$f"
done

# Scripts
for f in install_deps.sh install_ollama.sh install_tts.sh post_install.sh; do
    curl -fsSL $REPO/scripts/$f -o "$AL_DIR/scripts/$f"
    chmod +x "$AL_DIR/scripts/$f"
done

# Assets
curl -fsSL $REPO/assets/AL_Assist_icon.png -o "$ICON_DIR/al.png"

# Desktop entries
curl -fsSL $REPO/desktop/al.desktop -o "$DESKTOP_DIR/al.desktop"
curl -fsSL $REPO/desktop/al-settings.desktop -o "$DESKTOP_DIR/al-settings.desktop"

# Config
if [ ! -f "$CONFIG_DIR/al_config.json" ]; then
    curl -fsSL $REPO/config/al_config.json -o "$CONFIG_DIR/al_config.json"
fi

# Make main AL engine executable
chmod +x "$AL_DIR/src/al.py"
chmod +x "$AL_DIR/src/al_overlay.py"
chmod +x "$AL_DIR/src/al_settings.py"

# ---------------- FINISH ----------------
echo
echo "✅ AL Assistant installation complete!"
echo "AL files installed in $AL_DIR"
echo "Config file: $CONFIG_DIR/al_config.json"
echo "Desktop shortcuts installed. You can search for 'AL Assistant' and 'AL Settings' in GNOME."
echo
echo "To start AL, run:"
echo "python3 $AL_DIR/src/al.py"
echo "To configure AL, run:"
echo "python3 $AL_DIR/src/al_settings.py"
