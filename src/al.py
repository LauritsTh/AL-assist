import time
import platform
import subprocess
import re
import urllib.parse
import difflib
import os

from al_apps import open_app, open_url, close_app
import al_media

IDLE_TIMEOUT = 120

ALIASES = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "brave": "Brave Browser",
    "spotify": "Spotify",
    "browser": "Google Chrome"
}

COMMON_CORRECTIONS = {
    "adn": "and",
    "searf": "search",
    "serch": "search",
    "apotify": "spotify",
}


class ALAssistant:
    def __init__(self):
        self.system = platform.system().lower()
        self.last_active = time.time()
        self.running = True

    # -------------------------
    # Utilities
    # -------------------------

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
        words = text.split()
        corrected = []
        for w in words:
            corrected.append(COMMON_CORRECTIONS.get(w, w))
        return " ".join(corrected)

    def resolve_app(self, name):
        name = name.strip()
        if name in ALIASES:
            return ALIASES[name]

        close_match = difflib.get_close_matches(name, ALIASES.keys(), n=1, cutoff=0.75)
        if close_match:
            return ALIASES[close_match[0]]

        return name

    def expand_repetitions(self, text):
        match = re.match(r"(\d+)\s+(.*)", text)
        if match:
            count = min(int(match.group(1)), 10)
            return [match.group(2)] * count
        return [text]

    def clear_screen(self):
        os.system("clear" if self.system != "windows" else "cls")

    # -------------------------
    # Command handling
    # -------------------------

    def handle(self, raw_text):
        self.last_active = time.time()

        text = self.normalize(raw_text)
        text = self.correct_typos(text)

        print(f"[DEBUG] parsed command = '{text}'")

        # --- CLEAR ---
        if text == "clear":
            self.clear_screen()
            return

        # --- EXIT AL ---
        if text in ("exit", "quit", "bye"):
            self.speak("Goodbye.")
            self.running = False
            return

        # --- CLOSE APP ---
        if text.startswith(("close", "quit")):
            target = text.replace("close", "").replace("quit", "").strip()
            if not target:
                self.speak("Close what?")
                return

            app = self.resolve_app(target)
            self.speak(f"Closing {app}")
            close_app(app)
            return

        # --- OPEN / GO TO ---
        if text.startswith(("open", "go to")):
            target = text.replace("open", "", 1).replace("go to", "", 1).strip()

            # search
            if "search for" in target:
                app_part, query = target.split("search for", 1)
                app = self.resolve_app(app_part.replace("and", "").strip())
                query = query.strip()

                self.speak(f"Opening {app}")
                open_app(app)

                encoded = urllib.parse.quote_plus(query)
                url = f"https://www.google.com/search?q={encoded}"
                self.speak(f"Searching for {query}")
                open_url(url)
                return

            # go to url
            if "go to" in target:
                app_part, url = target.split("go to", 1)
                app = self.resolve_app(app_part.replace("and", "").strip())
                url = url.strip()

                self.speak(f"Opening {app}")
                open_app(app)
                self.speak(f"Opening {url}")
                open_url(url)
                return

            app = self.resolve_app(target)
            self.speak(f"Opening {app}")
            open_app(app)
            return

        # --- PLAY MUSIC ---
        if text.startswith("play"):
            self.speak("Playing music")
            open_app("Spotify")
            time.sleep(1.2)
            al_media.play()
            return

        # --- MEDIA CONTROLS ---
        if text in ("pause", "stop"):
            self.speak("Paused")
            al_media.pause()
            return

        if text in ("resume", "continue"):
            self.speak("Playing")
            al_media.play()
            return

        if text in ("next", "skip"):
            self.speak("Next track")
            al_media.next_track()
            return

        if text in ("previous", "back"):
            self.speak("Previous track")
            al_media.previous_track()
            return

        self.speak("I can open, close apps, and control media.")

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
                if not cmd:
                    continue

                for expanded in self.expand_repetitions(cmd):
                    if self.running:
                        self.handle(expanded)

            except (EOFError, KeyboardInterrupt):
                break

        self.speak("Goodbye.")


if __name__ == "__main__":
    ALAssistant().run()
