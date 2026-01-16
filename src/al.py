import time
import platform
import subprocess
import re
import urllib.parse
import difflib
import os
import al_device



from al_apps import open_app, open_url, close_app, open_url_in_app
import al_media

IDLE_TIMEOUT = 120

ALIASES = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "brave": "Brave Browser",
    "spotify": "Spotify",
    "browser": "Google Chrome",
}

COMMON_CORRECTIONS = {
    "adn": "and",
    "searf": "search",
    "serch": "search",
    "apotify": "spotify",
}

NUMBER_WORDS = {
    "once": 1,
    "twice": 2,
    "thrice": 3,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


class ALAssistant:
    def __init__(self):
        self.system = platform.system().lower()
        self.last_active = time.time()
        self.running = True

        # ---- CONTEXT MEMORY ----
        self.last_app = None
        self.last_search = None
        self.last_media_action = None

    # -------------------------
    # Utilities
    # -------------------------

    def touch(self):
        """Update activity timestamp ONLY when something meaningful happens"""
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
        if name in ALIASES:
            return ALIASES[name]
        match = difflib.get_close_matches(name, ALIASES.keys(), n=1, cutoff=0.75)
        if match:
            return ALIASES[match[0]]
        return name

    def extract_count(self, text):
        words = text.split()
        count = 1
        for w in words:
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
    # Command handling
    # -------------------------

    def handle(self, raw_text):
        text = self.correct_typos(self.normalize(raw_text))
        text, count = self.extract_count(text)

        print(f"[DEBUG] parsed command = '{text}', count={count}")

        # --- EXIT ---
        if text in ("exit", "quit", "bye"):
            self.touch()
            self.running = False
            self.speak("Goodbye.")
            return
        # --- DEVICE / SETTINGS ---
        if text in ("open settings", "settings"):
            self.speak("Opening system settings")
            al_device.open_settings()
            return

        if text in (
            "open location settings",
            "location settings",
            "privacy location"
        ):
            self.speak("Opening location services settings")
            al_device.open_location_settings()
            return

        if text in (
            "check for updates",
            "check updates",
            "software update",
            "system update"
        ):
            self.speak("Checking for system updates")
            al_device.check_for_updates()
            return

        if text in (
            "open update settings",
            "open software update"
        ):
            self.speak("Opening software update settings")
            al_device.open_update_settings()
            return

        # --- CLEAR ---
        if text == "clear":
            self.touch()
            os.system("clear" if self.system != "windows" else "cls")
            return

        # --- SEARCH FOR (contextual)  ✅ NEW ---
        if text.startswith("search for"):
            query = text.replace("search for", "", 1).strip()
            if not self.last_app:
                self.speak("Which browser should I use?")
                return

            self.last_search = (
                f"https://www.google.com/search?q="
                f"{urllib.parse.quote_plus(query)}"
            )

            self.touch()
            self.speak(f"Searching for {query}")
            open_url_in_app(self.last_app, self.last_search)
            return

        # --- SEARCH AGAIN ---
        if text in ("search again", "search it again"):
            if self.last_search and self.last_app:
                self.touch()
                self.speak("Searching again")
                for _ in range(count):
                    open_url_in_app(self.last_app, self.last_search)
            else:
                self.speak("Nothing to search again.")
            return

        # --- CLOSE ---
        if text.startswith("close"):
            target = text.replace("close", "", 1).strip() or self.last_app
            if not target:
                self.speak("Close what?")
                return

            app = self.resolve_app(target)
            self.touch()
            self.last_app = app
            self.speak(f"Closing {app}")
            close_app(app)
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

        # --- PLAY MUSIC ---
        if text.startswith("play"):
            self.touch()
            self.speak("Playing music")
            open_app("Spotify")
            time.sleep(1.2)
            al_media.play()
            self.last_media_action = al_media.play
            return

        # --- MEDIA CONTROLS ---
        if text in ("pause", "stop"):
            self.touch()
            for _ in range(count):
                al_media.pause()
            self.last_media_action = al_media.pause
            return

        if text in ("resume", "continue"):
            self.touch()
            for _ in range(count):
                al_media.play()
            self.last_media_action = al_media.play
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

        self.speak("I can open, close apps, search, and control media.")

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
