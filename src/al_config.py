import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".al_config.json"


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)

    return {
        "roles": {},
        "aliases": {
            "chrome": "Google Chrome",
            "google chrome": "Google Chrome",
            "brave": "Brave Browser",
            "browser": "Google Chrome",
            "spotify": "Spotify",
        }
    }


def save_config(config):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass
