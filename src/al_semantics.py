import re


def split_commands(text: str):
    parts = re.split(r"\band\b|\bthen\b", text)
    return [p.strip() for p in parts if p.strip()]


def normalize(text: str):
    return text.lower().strip()
