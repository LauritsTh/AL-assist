import subprocess
import platform

SYSTEM = platform.system().lower()

# -------------------------
# Settings
# -------------------------

def open_settings():
    if SYSTEM == "darwin":
        subprocess.run(
            ["open", "x-apple.systempreferences:"],
            check=False
        )
    elif SYSTEM == "linux":
        subprocess.run(
            ["gnome-control-center"],
            check=False
        )

def open_location_settings():
    if SYSTEM == "darwin":
        subprocess.run(
            [
                "open",
                "x-apple.systempreferences:com.apple.preference.security?Privacy_LocationServices"
            ],
            check=False
        )

def open_update_settings():
    if SYSTEM == "darwin":
        subprocess.run(
            [
                "open",
                "x-apple.systempreferences:com.apple.preferences.softwareupdate"
            ],
            check=False
        )

# -------------------------
# Info / checks
# -------------------------

def check_for_updates():
    if SYSTEM == "darwin":
        subprocess.run(
            ["softwareupdate", "-l"],
            check=False
        )
    elif SYSTEM == "linux":
        subprocess.run(
            ["bash", "-c", "apt list --upgradable 2>/dev/null"],
            check=False
        )
