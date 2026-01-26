import platform
import subprocess

SYSTEM = platform.system().lower()


# -------------------------
# Utilities
# -------------------------

def _run(cmd):
    subprocess.run(cmd, check=False)


# -------------------------
# Settings
# -------------------------

def open_settings():
    """Open main System Settings"""
    if SYSTEM == "darwin":
        _run(["open", "-b", "com.apple.systempreferences"])
    elif SYSTEM == "linux":
        _run(["gnome-control-center"])


def open_location_settings():
    """Open Privacy & Security → Location Services"""
    if SYSTEM == "darwin":
        _run([
            "open",
            "x-apple.systempreferences:com.apple.preference.security?Privacy_LocationServices"
        ])
    elif SYSTEM == "linux":
        _run(["gnome-control-center", "privacy"])


# -------------------------
# Location Services
# -------------------------

def disable_location_services():
    """
    macOS does NOT allow programmatic disabling.
    We open the correct pane instead.
    """
    if SYSTEM == "darwin":
        open_location_settings()
        print(
            "[AL] Apple requires manual confirmation to disable Location Services."
        )


def enable_location_services():
    """
    macOS does NOT allow programmatic enabling.
    We open the correct pane instead.
    """
    if SYSTEM == "darwin":
        open_location_settings()
        print(
            "[AL] Apple requires manual confirmation to enable Location Services."
        )


# -------------------------
# Software Updates
# -------------------------

def check_for_updates():
    """Check for available updates via CLI"""
    if SYSTEM == "darwin":
        _run(["softwareupdate", "-l"])
    elif SYSTEM == "linux":
        _run(["sudo", "apt", "update"])


def open_update_settings():
    """Open Software Update UI"""
    if SYSTEM == "darwin":
        _run([
            "open",
            "x-apple.systempreferences:com.apple.preferences.softwareupdate"
        ])
    elif SYSTEM == "linux":
        _run(["gnome-control-center", "updates"])
def location_services_state():
    """
    macOS does not reliably expose Location Services state.
    Returns 'unknown' on purpose.
    """
    return "unknown"

