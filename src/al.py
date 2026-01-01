#!/usr/bin/env python3
import os, json, subprocess, time
from pathlib import Path

CONFIG_PATH = Path.home() / ".config/al_config.json"

def load_config():
    if CONFIG_PATH.exists():
        return json.load(open(CONFIG_PATH))
    else:
        # default fallback
        return {
            "voice_model": "~/.local/share/piper/en_US-amy-low.onnx",
            "speed": 1.0,
            "pitch": 1.0,
            "language": "en-US",
            "online_permission_default": "ask",
            "personality": "neutral",
            "waveform_color": "#50B4FF",
            "remember_permissions": True,
            "app_integrations": {}
        }

cfg = load_config()

def speak(text):
    """Use Piper TTS to speak a string"""
    voice_path = os.path.expanduser(cfg["voice_model"])
    output_file = "/tmp/al_speak.wav"
    subprocess.run([
        "piper",
        "--model", voice_path,
        "--speed", str(cfg.get("speed",1.0)),
        "--pitch", str(cfg.get("pitch",1.0)),
        "--output_file", output_file
    ], input=text.encode())
    subprocess.run(["aplay", output_file])

def open_app(name):
    """Open an app using integration"""
    cmd = cfg.get("app_integrations", {}).get(name.lower())
    if cmd:
        subprocess.Popen(cmd, shell=True)
        return True
    return False

def ask_online_permission():
    if cfg.get("online_permission_default","ask")=="ask":
        resp = input("AL wants to go online. Allow? [y/N]: ").strip().lower()
        return resp=="y"
    return cfg.get("online_permission_default")=="always"

def main():
    user = os.getenv("USER","User")
    print(f"Hello {user}, AL is awake!")
    while True:
        try:
            cmd = input("You: ").strip()
            if cmd.lower() in ["quit","exit"]: break
            if open_app(cmd):
                print(f"AL: Opening {cmd}")
                continue
            if "search" in cmd.lower() or "google" in cmd.lower():
                if ask_online_permission():
                    subprocess.Popen(["brave","https://www.google.com/search?q="+cmd.replace(" ","+")])
                    print("AL: Opening browser search")
                else:
                    print("AL: Online access denied")
                continue
            # Placeholder for LLM answer integration
            print(f"AL ({cfg.get('personality','neutral')}): Sorry, I am still learning to answer '{cmd}'")
        except KeyboardInterrupt:
            print("AL: Shutting down")
            break

if __name__ == "__main__":
    main()
