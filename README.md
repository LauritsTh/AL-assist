# AL Assistant

Self-hosted, GNOME desktop voice assistant with Siri-style animation, Piper TTS, Ollama LLM, and customizable settings.

## Installation

Run `install.sh` to set up all dependencies.

AL-assist/
├── install.sh                # Main installer script (calls src/scripts)
├── README.md                 # Project description
├── assets/
│   └── AL_Assist_icon.png    # Custom icon (Siri-style)
├── config/
│   └── al_config.json        # Default config for AL
├── desktop/
│   ├── al.desktop            # AL assistant autostart
│   └── al-settings.desktop   # AL Settings app
├── src/
│   ├── al.py                 # Core assistant engine
│   ├── al_overlay.py         # Siri-style pulsing animation
│   └── al_settings.py        # GTK settings app
└── scripts/
    ├── install_deps.sh       # Install system dependencies
    ├── install_ollama.sh     # Install Ollama + model
    ├── install_tts.sh        # Install Piper TTS
    └── post_install.sh       # Any post-install steps (permissions, icons)
