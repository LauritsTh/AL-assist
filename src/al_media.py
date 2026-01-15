import platform
import subprocess

SYSTEM = platform.system().lower()


def _osascript(script: str):
    subprocess.run(
        ["osascript", "-e", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# =========================
# macOS – Spotify control
# =========================

if SYSTEM == "darwin":

    def play():
        _osascript('tell application "Spotify" to play')

    def pause():
        _osascript('tell application "Spotify" to pause')

    def play_pause():
        _osascript('tell application "Spotify" to playpause')

    def next_track():
        _osascript('tell application "Spotify" to next track')

    def previous_track():
        _osascript('tell application "Spotify" to previous track')


# =========================
# Linux – playerctl
# =========================

else:

    def _playerctl(cmd):
        subprocess.run(
            ["playerctl", cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def play():
        _playerctl("play")

    def pause():
        _playerctl("pause")
    def stop():
        _playerctl("pause")

    def play_pause():
        _playerctl("play-pause")

    def next_track():
        _playerctl("next")

    def previous_track():
        _playerctl("previous")
