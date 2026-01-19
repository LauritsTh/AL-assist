import time
import platform
import subprocess
import re
import urllib.parse
import difflib
import os

import al_media
import al_device
from al_apps import open_app, close_app, open_url_in_app

# -------------------------
# Configuration
# -------------------------

IDLE_TIMEOUT = 120

ALIASES = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "brave": "Brave Browser",
    "brave browser": "Brave Browser",
    "spotify": "Spotify",
    "settings": "System Settings",
}

COMMON_CORRECTIONS = {
    "serttings": "settings",
    "setings": "settings",
    "locaton": "location",
}

CONFIRM_YES = {"yes", "confirm", "ok", "do it"}
CONFIRM_NO = {"no", "cancel", "never mind"}

# -------------------------
# Assistant
# -------------------------

class ALAssistant:
    def __init__(self):
        self.system = platform.system().lower()
        self.running = True
        self.last_active = time.time()

        self.last_app = None
        self.last_search = None

        self.pending_action = None

    # -------------------------
    # Utilities
    # -------------------------

    def touch(self):
        self.last_active = time.time()

    def speak(self, text):
        print(f"[AL] {text}")
        try:
            if self.system == "darwin":
                subprocess.run(["say", text], check=False)
        except Exception:
            pass

    def normalize(self, text):
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        words = text.split()
        return " ".join(COMMON_CORRECTIONS.get(w, w) for w in words)

    def resolve_app(self, name):
        return ALIASES.get(name, name)

    # -------------------------
    # Confirmation
    # -------------------------

    def confirm(self, description, action):
        self.pending_action = action
        self.speak(f"This will {description}. Are you sure?")

    # -------------------------
    # Command handling
    # -------------------------

    def handle(self, raw):
        text = self.normalize(raw)
        print(f"[DEBUG] parsed command = '{text}'")

        # ---- Confirmation response ----
        if self.pending_action:
            if text in CONFIRM_YES:
                self.pending_action()
                self.pending_action = None
            else:
                self.speak("Cancelled.")
                self.pending_action = None
            return

        # ---- Exit ----
        if text in ("exit", "quit"):
            self.running = False
            self.speak("Goodbye.")
            return

        # -------------------------
        # SETTINGS KNOWLEDGE
        # -------------------------

        if text in ("open settings", "settings"):
            self.touch()
            self.speak("Opening system settings")
            al_device.open_settings()
            return

        if "location" in text:
            if any(w in text for w in ("open", "show")):
                self.touch()
                self.speak("Opening location settings")
                al_device.open_location_settings()
                return

            if any(w in text for w in ("turn off", "disable")):
                self.confirm(
                    "turn off location services",
                    al_device.disable_location_services,
                )
                return

            if any(w in text for w in ("turn on", "enable")):
                self.confirm(
                    "turn on location services",
                    al_device.enable_location_services,
                )
                return

        if text in ("check for updates", "system update"):
            self.touch()
            self.speak("Checking for updates")
            al_device.check_for_updates()
            return

        # -------------------------
        # OPEN / CLOSE
        # -------------------------

        if text.startswith("open"):
            app = self.resolve_app(text.replace("open", "").strip())
            self.last_app = app
            self.touch()
            self.speak(f"Opening {app}")
            open_app(app)
            return

        if text.startswith("close"):
            app = self.resolve_app(text.replace("close", "").strip())
            self.touch()
            self.speak(f"Closing {app}")
            close_app(app)
            return

        # -------------------------
        # MEDIA
        # -------------------------

        if text.startswith("play"):
            self.touch()
            open_app("Spotify")
            time.sleep(1)
            al_media.play()
            return

        if text == "pause":
            self.touch()
            al_media.pause()
            return

        # -------------------------
        # Fallback
        # -------------------------

        self.speak("I understand apps, searches, media, and system settings.")

    # -------------------------
    # Main loop
    # -------------------------

    def run(self):
        self.speak("AL is ready.")
        while self.running:
            if time.time() - self.last_active > IDLE_TIMEOUT:
                self.speak("Going idle.")
                break
            try:
                cmd = input("AL > ")
                if cmd:
                    self.handle(cmd)
            except KeyboardInterrupt:
                break
        self.speak("Goodbye.")


if __name__ == "__main__":
    ALAssistant().run()

