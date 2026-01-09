#!/usr/bin/env python3
import time
import getpass

from al_config import load_config, save_config
from al_actions import open_app, speak
from al_llm import respond

IDLE_TIMEOUT = 120


class ALAssistant:
    def __init__(self):
        self.username = getpass.getuser()
        self.config = load_config()

        # 🔒 Backward-compatible config migration
        if "commands" not in self.config:
            self.config["commands"] = {}
            save_config(self.config)

        self.last_active = time.time()
        self.running = True

    # ----------------------------
    # Core Logic
    # ----------------------------
    def handle_command(self, text: str):
        self.last_active = time.time()
        text = text.strip().lower()

        commands = self.config.get("commands", {})

        # Learned command
        if text in commands:
            app = commands[text]
            speak(f"Opening {app}, {self.username}")
            open_app(app)
            return

        # Explicit open
        if text.startswith("open "):
            app = text.replace("open ", "").strip()
            speak(f"Opening {app}")
            open_app(app)
            return

        # Learning trigger
        if "play" in text or "open" in text:
            self.learn_command(text)
            return

        # Conversation fallback
        speak(respond(text))

    # ----------------------------
    # Learning
    # ----------------------------
    def learn_command(self, phrase: str):
        speak("Which app should I use?")
        app = input("APP > ").strip()

        if not app:
            speak("Okay, skipping.")
            return

        self.config["commands"][phrase] = app
        save_config(self.config)

        speak(f"Learned. I will use {app} for that.")

    # ----------------------------
    # Idle Watchdog
    # ----------------------------
    def idle_check(self):
        if time.time() - self.last_active > IDLE_TIMEOUT:
            speak("Going idle.")
            self.running = False

    # ----------------------------
    # Main Loop
    # ----------------------------
    def run(self):
        speak("AL is ready.")

        while self.running:
            try:
                self.idle_check()
                command = input("AL > ").strip()
                if command:
                    self.handle_command(command)
            except (KeyboardInterrupt, EOFError):
                speak("Goodbye.")
                break


if __name__ == "__main__":
    ALAssistant().run()
