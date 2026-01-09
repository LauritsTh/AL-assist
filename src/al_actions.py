import subprocess
import platform
import shutil

SYSTEM = platform.system().lower()


def open_app(app_name: str):
    app = app_name.lower()

    if SYSTEM == "darwin":
        return subprocess.Popen(["open", "-a", app_name])

    if SYSTEM == "linux":
        if shutil.which(app):
            return subprocess.Popen([app])
        return subprocess.Popen(["xdg-open", app_name])

    raise RuntimeError("Unsupported OS")


def speak(text: str):
    if SYSTEM == "darwin":
        subprocess.Popen(["say", text])
    elif SYSTEM == "linux":
        subprocess.Popen(["espeak", text])
    else:
        print("[AL]", text)
