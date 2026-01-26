import time
import platform
import subprocess
import re
import urllib.parse
import difflib
import os

import al_media
import al_device
from al_apps import open_app, open_url, close_app, open_url_in_app

IDLE_TIMEOUT = 120

ALIASES = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "brave": "Brave Browser",
    "spotify": "Spotify",
    "browser": "Google Chrome",
    "system settings": "System Settings",
    "settings": "System Settings",
}

COMMON_CORRECTIONS = {
    "adn": "and",
    "searf": "search",
    "serch": "search",
    "apotify": "spotify",
    "sertings": "settings",
}

NUMBER_WORDS = {
    "once": 1,
    "twice": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


class ALAssistant:
    def __init__(self):
        self.system = platform.system().lower()
        self.running = True
        self.last_active = time.time()

        # --- CONTEXT MEMORY ---
        self.last_app = None
        self.last_search = None
        self.last_media_action = None

        # --- SETTINGS CONTEXT ---
        self.settings_state = {
            "open": False,
            "section": None,
            "subsection": None,
        }

        # --- INTENT CONTEXT ---
        self.intent = {
            "domain": None,
            "target": None,
            "action": None,
        }

        # --- CONFIRMATION ---
        self.pending_confirmation = None

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
            elif self.system == "linux":
                subprocess.run(["espeak", text], check=False)
        except Exception:
            pass

    def normalize(self, text):
        text = text.lower().strip()
        text = re.sub(r"[^\w\s.:/]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def correct_typos(self, text):
        return " ".join(COMMON_CORRECTIONS.get(w, w) for w in text.split())

    def resolve_app(self, name):
        if not name:
            return None
        if name in ALIASES:
            return ALIASES[name]
        match = difflib.get_close_matches(name, ALIASES.keys(), n=1, cutoff=0.75)
        if match:
            return ALIASES[match[0]]
        return name.title()

    def extract_count(self, text):
        words = text.split()
        count = 1
        for w in words[:]:
            if w.isdigit():
                count = int(w)
                words.remove(w)
                break
            if w in NUMBER_WORDS:
                count = NUMBER_WORDS[w]
                words.remove(w)
                break
        return " ".join(words), max(1, min(count, 10))

    # -------------------------
    # Confirmation handling
    # -------------------------

    def ask_confirmation(self, prompt, action):
        self.pending_confirmation = action
        self.speak(prompt)

    def handle_confirmation(self, text):
        self.touch()

        if text in ("yes", "ok", "okay", "sure"):
            if self.pending_confirmation:
                action = self.pending_confirmation
                self.pending_confirmation = None
                action()
            return True

        if text in ("no", "cancel"):
            self.pending_confirmation = None
            self.speak("Cancelled.")
            return True

        return False

    # -------------------------
    # Command handling
    # -------------------------

    def handle(self, raw_text):
        text = self.correct_typos(self.normalize(raw_text))
        text, count = self.extract_count(text)

        print(f"[DEBUG] parsed command = '{text}', count={count}")

        # --- CONFIRMATION FIRST ---
        if self.pending_confirmation:
            if self.handle_confirmation(text):
                return

        # --- EXIT ---
        if text in ("exit", "quit", "bye"):
            self.touch()
            self.running = False
            self.speak("Goodbye.")
            return

        # --- CLEAR ---
        if text == "clear":
            self.touch()
            os.system("clear" if self.system != "windows" else "cls")
            return

        # --- LOCATION SERVICES ---
        if "location services" in text:
            self.intent.update({
                "domain": "settings",
                "target": "location services",
                "action": "open",
            })

            self.settings_state.update({
                "open": True,
                "section": "privacy",
                "subsection": "location services",
            })

            self.ask_confirmation(
                "This affects all apps. Should I open Location Services settings now?",
                al_device.open_location_settings
            )
            return

        # --- FOLLOW-UP TURN OFF ---
        if text in ("turn off", "disable"):
            if self.intent["target"] == "location services":
                self.ask_confirmation(
                    "Apple requires manual confirmation. Open Location Services settings now?",
                    al_device.open_location_settings
                )
                return

        # --- OPEN SETTINGS ---
        if text in ("open settings", "settings"):
            self.touch()
            self.intent.update({
                "domain": "settings",
                "target": "system settings",
                "action": "open",
            })
            self.settings_state.update({
                "open": True,
                "section": None,
                "subsection": None,
            })
            self.speak("Opening system settings")
            al_device.open_settings()
            return

        # --- CHECK UPDATES ---
        if text in ("check for updates", "software update", "system update"):
            self.touch()
            self.intent.update({
                "domain": "settings",
                "target": "software update",
                "action": "check",
            })
            self.speak("Checking for system updates")
            al_device.check_for_updates()
            return

        # --- OPEN SOFTWARE UPDATE UI ---
        if text in ("open software update", "open update settings"):
            self.touch()
            self.speak("Opening software update settings")
            al_device.open_update_settings()
            return

        # --- SEARCH ---
        if text.startswith("search for"):
            query = text.replace("search for", "", 1).strip()
            if not self.last_app:
                self.speak("Which app should I search in?")
                return

            self.last_search = (
                f"https://www.google.com/search?q="
                f"{urllib.parse.quote_plus(query)}"
            )
            self.touch()
            self.speak(f"Searching for {query}")
            open_url_in_app(self.last_app, self.last_search)
            return

        if text in ("search again", "again"):
            if self.last_search and self.last_app:
                self.touch()
                self.speak("Searching again")
                for _ in range(count):
                    open_url_in_app(self.last_app, self.last_search)
                return

        # --- CLOSE ---
        if text.startswith("close"):
            target = text.replace("close", "", 1).strip()

            if not target:
                if self.settings_state["open"]:
                    target = "system settings"
                else:
                    target = self.last_app or self.intent.get("target")

            if not target:
                self.speak("Close what?")
                return

            app = self.resolve_app(target)
            self.touch()
            self.speak(f"Closing {app}")
            close_app(app)

            if app == "System Settings":
                self.settings_state = {
                    "open": False,
                    "section": None,
                    "subsection": None,
                }

            self.last_app = None
            self.intent["target"] = None
            return

        # --- OPEN / OPEN + SEARCH ---
        if text.startswith(("open", "go to")):
            target = (
                text.replace("open", "", 1)
                .replace("go to", "", 1)
                .strip()
            )

            if "search for" in target:
                app_part, query = target.split("search for", 1)
                app = self.resolve_app(app_part.replace("and", "").strip())
                query = query.strip()

                self.last_app = app
                self.last_search = (
                    f"https://www.google.com/search?q="
                    f"{urllib.parse.quote_plus(query)}"
                )

                self.touch()
                self.speak(f"Opening {app}")
                open_app(app)
                self.speak(f"Searching for {query}")
                open_url_in_app(app, self.last_search)
                return

            app = self.resolve_app(target)
            self.touch()
            self.last_app = app
            self.speak(f"Opening {app}")
            open_app(app)
            return

        # --- MEDIA ---
        if text.startswith("play"):
            self.touch()
            self.speak("Playing music")
            open_app("Spotify")
            time.sleep(1.2)
            al_media.play()
            self.last_media_action = al_media.play
            return

        if text in ("pause", "stop"):
            self.touch()
            for _ in range(count):
                al_media.pause()
            self.last_media_action = al_media.pause
            return

        if text in ("next", "skip"):
            self.touch()
            for _ in range(count):
                al_media.next_track()
            self.last_media_action = al_media.next_track
            return

        if text in ("previous", "back"):
            self.touch()
            for _ in range(count):
                al_media.previous_track()
            self.last_media_action = al_media.previous_track
            return

        self.speak(
            "I can open and close apps, search, control media, "
            "and guide you through system settings."
        )

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
                cmd = input("AL > ").strip()
                if cmd:
                    self.handle(cmd)
            except (EOFError, KeyboardInterrupt):
                break
        self.speak("Goodbye.")


if __name__ == "__main__":
    ALAssistant().run()
