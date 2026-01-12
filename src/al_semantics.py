import re

APP_SYNONYMS = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "brave": "Brave Browser",
    "brave browser": "Brave Browser",
    "spotify": "Spotify"
}

def normalize_app(name):
    return APP_SYNONYMS.get(name.lower().strip(), name)

def split_commands(text):
    parts = re.split(r"\b(and|then)\b", text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip() and p.lower() not in ("and", "then")]
