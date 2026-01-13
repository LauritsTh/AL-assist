import time
import platform
import subprocess
import re
import al_media


from al_apps import open_app, open_url
import al_media

IDLE_TIMEOUT = 120

ALIASES = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "brave": "Brave Browser",
    "spotify": "Spotify",
    "browser": "Google Chrome"
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
        text = re.sub(r"[^\w\s.:/]", "", text)  # remove odd chars
        text = re.sub(r"\s+", " ", text)       # normalize spaces
        return text

    def resolve(self, name):
        return ALIASES.get(name, name)

    # -------------------------
    # Command handling
    # -------------------------

    def handle(self, raw_text):
        self.last_active = time.time()

        text = self.normalize(raw_text)
        print(f"[DEBUG] parsed command = '{text}'")

        # --- OPEN ---
        if text.startswith("open"):
            target = text.replace("open", "", 1).strip()

            if "go to" in target:
                app, url = target.split("go to", 1)
                app = self.resolve(app.strip())
                url = url.strip()
                self.speak(f"Opening {app}")
                open_app(app)
                self.speak(f"Opening {url}")
                open_url(url)
            else:
                app = self.resolve(target)
                self.speak(f"Opening {app}")
                open_app(app)
            return

        # --- PLAY ---
        
        if text.startswith("play"):
            self.speak("Playing music")
            open_app("Spotify")
            time.sleep(1.2)          # Spotify MUST be ready
            al_media.play()          # <-- NOT toggle
            return


        # --- MEDIA CONTROLS ---
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


        # --- FALLBACK ---
        self.speak("I can open apps and control media.")

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
                if cmd.strip():
                    self.handle(cmd)
            except (EOFError, KeyboardInterrupt):
                break

        self.speak("Goodbye.")


if __name__ == "__main__":
    ALAssistant().run()
