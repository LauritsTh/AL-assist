#!/usr/bin/env python3
import time
import json
import subprocess
import threading
import getpass
import platform
import shutil
from pathlib import Path
import os

# ----------------------------
# Platform-aware config path
# ----------------------------
SYSTEM = platform.system().lower()

if SYSTEM == "darwin":
    CONFIG_DIR = Path.home() / "Library" / "Application Support" / "AL"
elif SYSTEM == "windows":
    CONFIG_DIR = Path(os.getenv("APPDATA", Path.home())) / "AL"
else:  # Linux and others
    CONFIG_DIR = Path.home() / ".config" / "al"

CONFIG_PATH = CONFIG_DIR / "config.json"
IDLE_TIMEOUT = 120  # seconds


# ----------------------------
# Assistant Core
# ----------------------------
class ALAssistant:
    def __init__(self):
        self.username = getpass.getuser()
        self.system = SYSTEM
        self.running = True
        self.last_active = time.time()

        self._load_config()
        self._detect_tts()

    # ----------------------------
    # Config
    # ----------------------------
    def _load_config(self):
        default_config = {
            "language": "en-US",
            "voice": "default",
            "tone": "neutral",
            "allow_online": False,
            "commands": {}
        }

        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH) as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
        except Exception:
            self.config = default_config

        for key, value in default_config.items():
            self.config.setdefault(key, value)

    def _save_config(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)

    # ----------------------------
    # Text-to-Speech
    # ----------------------------
    def _detect_tts(self):
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
                subprocess.Popen(["espeak", text])
            else:
                print(f"[AL] {text}")
        except Exception:
            print(f"[AL] {text}")

    # ----------------------------
    # Intent Parsing
    # ----------------------------
    def parse_intent(self, text: str):
        text = text.lower().strip()

        if text in self.config["commands"]:
            return {
                "intent": "launch_app",
                "app": self.config["commands"][text]
            }

        if text.startswith("open "):
            return {"intent": "launch_app", "app": text.replace("open ", "").strip()}

        if text.startswith("play "):
            return {"intent": "play_media", "query": text.replace("play ", "").strip()}

        if text in ("exit", "quit", "sleep"):
            return {"intent": "sleep"}

        return {"intent": "unknown", "text": text}

    # ----------------------------
    # Actions
    # ----------------------------
    def launch_app(self, app: str):
        try:
            if self.system == "darwin":
                subprocess.Popen(["open", "-a", app])
            elif self.system == "linux":
                if shutil.which(app):
                    subprocess.Popen([app])
                else:
                    subprocess.Popen(["xdg-open", app])
            else:
                self.speak("App launching is not supported on this system.")
                return

            self.speak(f"Opening {app}.")

        except Exception:
            self.speak(f"I couldn't open {app}.")

    def learn_command(self, phrase: str):
        self.speak("Which app should I use?")
        app = input("APP > ").strip()

        if not app:
            self.speak("Okay, I won't save that.")
            return

        self.config["commands"][phrase] = app
        self._save_config()
        self.speak(f"Got it. I'll use {app} next time.")

    # ----------------------------
    # Dispatcher
    # ----------------------------
    def handle_command(self, text: str):
        self.last_active = time.time()
        intent = self.parse_intent(text)

        if intent["intent"] == "launch_app":
            self.launch_app(intent.get("app"))

        elif intent["intent"] == "play_media":
            self.speak(
                "I can open a music app, but song control "
                "requires deeper app integration."
            )
            self.learn_command(text)

        elif intent["intent"] == "sleep":
            self.speak("Going idle.")
            self.running = False

        else:
            self.speak("I don't know how to do that yet.")
            self.learn_command(text)

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
    # Main Loop (Dev)
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


# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    ALAssistant().run()
