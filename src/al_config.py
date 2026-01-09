import json
import os
import platform
from pathlib import Path

def get_config_dir():
    if platform.system() == "Darwin":
        return Path.home() / "Library" / "Application Support" / "AL"
    else:
        return Path.home() / ".config" / "al"

CONFIG_DIR = get_config_dir()
CONFIG_PATH = CONFIG_DIR / "al_config.json"

DEFAULT_CONFIG = {
    "roles": {},        # e.g. {"music_player": "Spotify"}
    "apps": {}          # learned app aliases
}

def load_config():
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
