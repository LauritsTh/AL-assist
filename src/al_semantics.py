import re

APP_SYNONYMS = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "brave": "Brave Browser",
    "brave browser": "Brave Browser",
    "spotify": "Spotify"
}

def normalize_app(name):
    key = name.lower().strip()
    return APP_SYNONYMS.get(key, name)

def split_commands(text):
    # split on "and", "then"
    parts = re.split(r"\b(and|then)\b", text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip() and p.lower() not in ("and", "then")]
