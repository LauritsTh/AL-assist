#!/usr/bin/env bash
set -e

echo "Installing AL Assistant"

sudo apt update
sudo apt install -y python3 python3-gi espeak x11-utils curl

INSTALL_DIR="$HOME/.local/share/al"
mkdir -p "$INSTALL_DIR"

curl -L https://raw.githubusercontent.com/LauritsTh/AL-assist/main/assets/AL_Assist_icon.png \
  -o "$INSTALL_DIR/icon.png"

cp -r src scripts "$INSTALL_DIR"
chmod +x "$INSTALL_DIR"/src/*.py
chmod +x "$INSTALL_DIR"/scripts/*.sh

mkdir -p ~/.local/share/applications

cat <<EOF > ~/.local/share/applications/al.desktop
[Desktop Entry]
Name=AL Assistant
Exec=python3 $INSTALL_DIR/src/al.py
Icon=$INSTALL_DIR/icon.png
Type=Application
Categories=Utility;
EOF

echo "AL installed. Log out & back in to activate."
