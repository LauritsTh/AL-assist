import time
import platform
import subprocess

from al_config import load_config, save_config
from al_apps import open_app, open_url_from_text
from al_semantics import normalize_app, split_commands

IDLE_SECONDS = 120

class ALAssistant:
    def __init__(self):
        self.config = load_config()
        self.last_activity = time.time()

    # -----------------------
    # Voice + output
    # -----------------------
    def speak(self, text):
        print(f"[AL] {text}")
        system = platform.system()
        try:
            if system == "Darwin":
                subprocess.Popen(["say", text])
            elif system == "Linux":
                subprocess.Popen(["espeak", text])
        except Exception:
            pass

    # -----------------------
    # Main loop
    # -----------------------
    def run(self):
        self.speak("AL is ready.")

        while True:
            if time.time() - self.last_activity > IDLE_SECONDS:
                self.speak("Going idle.")
                self.last_activity = time.time()

            try:
                command = input("AL > ").strip()
                self.last_activity = time.time()

                if not command:
                    continue
                if command in ("exit", "quit"):
                    self.speak("Goodbye.")
                    break

                for part in split_commands(command):
                    self.handle_command(part)

            except KeyboardInterrupt:
                self.speak("Goodbye.")
                break

    # -----------------------
    # Intent routing
    # -----------------------
    def handle_command(self, text):
        lower = text.lower()

        if lower.startswith("open "):
            self.handle_open(text)
        elif lower.startswith("play"):
            self.handle_play()
        elif open_url_from_text(text):
            self.speak("Opening website.")
        else:
            self.speak("I didn't understand that yet.")

    # -----------------------
    # Actions
    # -----------------------
    def handle_open(self, text):
        name = text.replace("open", "", 1).strip()
        app = normalize_app(name)

        if open_app(app):
            self.speak(f"Opening {app}")
        else:
            self.speak(f"Unable to find application named {name}")

    def handle_play(self):
        role = "music_player"
        app = self.config["roles"].get(role)

        if not app:
            self.speak("Which app should I use for music?")
            app = input("APP > ").strip()
            if not app:
                return
            self.config["roles"][role] = app
            save_config(self.config)
            self.speak(f"Got it. {app} is your music app.")

        self.speak(f"Opening {app}. I can't control playback yet.")
        open_app(app)

if __name__ == "__main__":
    ALAssistant().run()
