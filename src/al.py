#!/usr/bin/env python3
import os
import time
import json
import subprocess
import threading
import getpass
import platform
from pathlib import Path

CONFIG_PATH = Path.home() / ".config/al/config.json"
IDLE_TIMEOUT = 120  # seconds


class ALAssistant:
    def __init__(self):
        self.username = getpass.getuser()
        self.last_active = time.time()
        self.running = True
        self.system = platform.system().lower()
        self.load_config()
        self.detect_tts()

    # ----------------------------
    # Config
    # ----------------------------
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

    # ----------------------------
    # Text-to-Speech (platform-aware)
    # ----------------------------
    def detect_tts(self):
        """
        Decide which TTS backend to use.
        """
        if self.system == "darwin":
            self.tts_backend = "say"
        elif self.system == "linux":
            self.tts_backend = "espeak"
        else:
            self.tts_backend = None

    def speak(self, text: str):
        if not text:
            return

        try:
            if self.tts_backend == "say":
                subprocess.Popen(["say", text])

            elif self.tts_backend == "espeak":
                subprocess.Popen([
                    "espeak",
                    "-v", self.config.get("language", "en"),
                    text
                ])

            else:
                print(f"[AL] {text}")

        except FileNotFoundError:
            print("[AL] TTS backend not found. Falling back to console output.")
            print(f"[AL] {text}")

    # ----------------------------
    # Command Handling
    # ----------------------------
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
            # UI confirmation handled in overlay

        elif "sleep" in command:
            self.speak("Going to sleep")
            self.running = False

        else:
            self.speak(
                "I didn't recognize that yet. You can teach me which app to use."
            )

    # ----------------------------
    # Idle Watchdog
    # ----------------------------
    def idle_watchdog(self):
        while self.running:
            if time.time() - self.last_active > IDLE_TIMEOUT:
                self.speak("I'm going idle.")
                self.running = False
            time.sleep(5)

    # ----------------------------
    # Main Loop - tempurary for development
    # ----------------------------
    def run(self):
        self.speak(f"Hello {self.username}. AL is ready.")
        threading.Thread(
            target=self.idle_watchdog,
            daemon=True
        ).start()

        while self.running:
            try:
                command = input("AL > ").strip()
                if command:
                    self.handle_command(command)
            except (EOFError, KeyboardInterrupt):
                print("\n[AL] Shutting down.")
                self.running = False


if __name__ == "__main__":
    ALAssistant().run()
