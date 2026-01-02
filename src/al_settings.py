#!/usr/bin/env python3
import gi
import json
from pathlib import Path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

CONFIG_PATH = Path.home() / ".config/al/config.json"

class ALSettings(Gtk.Window):
    def __init__(self):
        super().__init__(title="AL Settings")
        self.set_default_size(300, 200)

        self.config = self.load_config()

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)
        self.add(box)

        self.lang = Gtk.ComboBoxText()
        for l in ["en-US", "en-GB", "de-DE"]:
            self.lang.append_text(l)
        self.lang.set_active(0)

        box.pack_start(Gtk.Label(label="Language"), False, False, 0)
        box.pack_start(self.lang, False, False, 0)

        save = Gtk.Button(label="Save")
        save.connect("clicked", self.save)
        box.pack_end(save, False, False, 0)

    def load_config(self):
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text())
        return {}

    def save(self, _):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump({
                "language": self.lang.get_active_text()
            }, f)
        Gtk.main_quit()

if __name__ == "__main__":
    win = ALSettings()
    win.show_all()
    Gtk.main()
