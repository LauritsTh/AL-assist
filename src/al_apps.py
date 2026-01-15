import platform
import subprocess

SYSTEM = platform.system().lower()

def open_app(name):
    if SYSTEM == "darwin":
        subprocess.run([
            "osascript",
            "-e",
            f'tell application "{name}" to activate'
        ], check=False)
    elif SYSTEM == "linux":
        subprocess.run(["xdg-open", name], check=False)

def open_url(url):
    if not url.startswith("http"):
        url = "https://" + url

    subprocess.run(
        ["open" if SYSTEM == "darwin" else "xdg-open", url],
        check=False
    )



def close_app(app_name):
    if SYSTEM == "darwin":
        subprocess.run(["osascript", "-e", f'quit app "{app_name}"'], check=False)
    elif SYSTEM == "linux":
        subprocess.run(["pkill", "-f", app_name], check=False)
