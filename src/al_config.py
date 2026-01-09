import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".al"
CONFIG_PATH = CONFIG_DIR / "config.json"


DEFAULT_CONFIG = {
    "language": "en-US",
    "allow_online": False,
    "commands": {}   # learned phrases → actions
}


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)

    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
