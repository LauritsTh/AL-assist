#!/usr/bin/env python3
import os
import time
import json
import subprocess
import threading
import getpass
from pathlib import Path

CONFIG_PATH = Path.home() / ".config/al/config.json"
IDLE_TIMEOUT = 120  # seconds

class ALAssistant:
    def __init__(self):
        self.username = getpass.getuser()
        self.last_active = time.time()
        self.running = True
        self.load_config()

    def load_config(self):
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "language": "en-US",
                "voice": "default",
                "tone": "neutral",
                "allow_online": False
            }

    def speak(self, text):
        subprocess.Popen([
            "espeak",
            "-v", self.config["language"],
            text
        ])

    def handle_command(self, command: str):
        self.last_active = time.time()
        command = command.lower()

        if "open email" in command:
            subprocess.Popen(["xdg-open", "mailto:"])
            self.speak(f"Opening email for you, {self.username}")

        elif "open browser" in command:
            subprocess.Popen(["brave-browser"])
            self.speak("Opening Brave browser")

        elif "play" in command and "spotify" in command:
            subprocess.Popen(["spotify"])
            self.speak("Opening Spotify")

        elif "go online" in command:
            self.speak("May I go online to search?")
            # UI confirmation handled elsewhere

        elif "sleep" in command:
            self.speak("Going to sleep")
            self.running = False

        else:
            self.speak("I didn't recognize that yet. You can teach me which app to use.")

    def idle_watchdog(self):
        while self.running:
            if time.time() - self.last_active > IDLE_TIMEOUT:
                self.speak("I'm going idle.")
                self.running = False
            time.sleep(5)

    def run(self):
        self.speak(f"Hello {self.username}. AL is ready.")
        threading.Thread(target=self.idle_watchdog, daemon=True).start()

        while self.running:
            time.sleep(0.1)

if __name__ == "__main__":
    ALAssistant().run()
