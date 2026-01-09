import subprocess
import platform
import webbrowser

def open_app(app_name):
    system = platform.system()

    try:
        if system == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        elif system == "Linux":
            subprocess.Popen([app_name])
        else:
            raise RuntimeError("Unsupported OS")
        return True
    except Exception:
        return False

def open_url(url):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
