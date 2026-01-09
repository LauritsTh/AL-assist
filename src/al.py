from al_config import load_config, save_config
from al_apps import open_app, open_url
from al_semantics import normalize_app, split_commands

class ALAssistant:
    def __init__(self):
        self.config = load_config()

    def speak(self, text):
        print(f"[AL] {text}")

    def run(self):
        self.speak("AL is ready.")
        while True:
            try:
                command = input("AL > ").strip()
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

    def handle_command(self, text):
        lower = text.lower()

        if lower.startswith("open "):
            self.handle_open(text)
        elif lower.startswith("play"):
            self.handle_play(text)
        elif "www." in text or ".com" in text:
            open_url(text)
        else:
            self.speak("I didn't understand that yet.")

    def handle_open(self, text):
        name = text.replace("open", "", 1).strip()
        app = normalize_app(name)

        if open_app(app):
            self.speak(f"Opening {app}")
        else:
            self.speak(f"Unable to find application named '{name}'")

    def handle_play(self, text):
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

        self.speak(f"Opening {app}")
        open_app(app)

if __name__ == "__main__":
    ALAssistant().run()
