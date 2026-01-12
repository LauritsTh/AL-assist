import subprocess
import platform
import webbrowser
import re

def open_app(app_name):
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        elif system == "Linux":
            subprocess.Popen([app_name])
        return True
    except Exception:
        return False

def extract_url(text):
    match = re.search(r"(https?://\S+|www\.\S+|\b[a-zA-Z0-9-]+\.(com|net|org|io)\b)", text)
    if not match:
        return None
    url = match.group(0)
    if not url.startswith("http"):
        url = "https://" + url
    return url

def open_url_from_text(text):
    url = extract_url(text)
    if url:
        webbrowser.open(url)
        return True
    return False
