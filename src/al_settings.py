#!/usr/bin/env python3
import gi, json, os, subprocess
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

CONFIG = os.path.expanduser("~/.config/al_config.json")

DEFAULT = {
    "voice_model": "~/.local/share/piper/en_US-amy-low.onnx",
    "speed": 1.0,
    "pitch": 1.0,
    "language": "en-US",
    "online_permission_default": "ask",
    "personality": "neutral",
    "waveform_color": "#50B4FF",
    "remember_permissions": True,
    "app_integrations": {"spotify":"playerctl -p spotify play","brave":"brave"}
}

def load_config():
    if not os.path.exists(CONFIG):
        return DEFAULT.copy()
    with open(CONFIG) as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG,"w") as f:
        json.dump(cfg,f,indent=2)

class ALSettings(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="io.pairofpears.al.settings")
        self.cfg = load_config()

    def do_activate(self):
        win = Gtk.ApplicationWindow(application=self)
        win.set_title("AL Settings")
        win.set_default_size(520,600)

        stack = Gtk.Stack()
        sidebar = Gtk.StackSidebar(stack=stack)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.append(sidebar)
        box.append(stack)
        win.set_child(box)

        stack.add_titled(self.voice_page(),"voice","Voice")
        stack.add_titled(self.visual_page(),"visual","Visuals")
        stack.add_titled(self.apps_page(),"apps","Apps")
        stack.add_titled(self.security_page(),"security","Permissions")
        stack.add_titled(self.personality_page(),"persona","Personality")
        win.present()

    # ---------------- PAGES ----------------
    def voice_page(self):
        b = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        b.set_margin_all(16)
        voice = Gtk.Entry(text=self.cfg.get("voice_model",""))
        speed = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0.5,1.5,0.1)
        pitch = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0.5,1.5,0.1)
        speed.set_value(self.cfg.get("speed",1.0))
        pitch.set_value(self.cfg.get("pitch",1.0))
        preview = Gtk.Button(label="Preview voice")
        def play(_):
            subprocess.Popen(["aplay"],stdin=subprocess.PIPE)
        preview.connect("clicked",play)
        b.append(Gtk.Label(label="Voice model")); b.append(voice)
        b.append(Gtk.Label(label="Speed")); b.append(speed)
        b.append(Gtk.Label(label="Pitch")); b.append(pitch)
        b.append(preview)
        self.bind_save(b,{"voice_model":voice.get_text,"speed":speed.get_value,"pitch":pitch.get_value})
        return b

    def visual_page(self):
        b = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        b.set_margin_all(16)
        picker = Gtk.ColorDialogButton()
        rgba = Gdk.RGBA(); rgba.parse(self.cfg.get("waveform_color","#50B4FF"))
        picker.set_rgba(rgba)
        b.append(Gtk.Label(label="Waveform color"))
        b.append(picker)
        self.bind_save(b,{"waveform_color": lambda: picker.get_rgba().to_string()})
        return b

    def apps_page(self):
        b = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        b.set_margin_all(16)
        text = Gtk.TextView()
        buf = text.get_buffer()
        buf.set_text(json.dumps(self.cfg.get("app_integrations",{}),indent=2))
        self.bind_save(b,{"app_integrations": lambda: json.loads(buf.get_text(*buf.get_bounds(),True))})
        b.append(Gtk.Label(label="App integrations (JSON)"))
        b.append(text)
        return b

    def security_page(self):
        b = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        b.set_margin_all(16)
        remember = Gtk.Switch(active=self.cfg.get("remember_permissions",True))
        b.append(Gtk.Label(label="Remember online permissions"))
        b.append(remember)
        self.bind_save(b,{"remember_permissions":remember.get_active})
        return b

    def personality_page(self):
        b = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        b.set_margin_all(16)
        personalities = ["neutral","concise","friendly","professional","playful"]
        dd = Gtk.DropDown.new_from_strings(personalities)
        dd.set_selected(personalities.index(self.cfg.get("personality","neutral")))
        b.append(Gtk.Label(label="AL Personality"))
        b.append(dd)
        self.bind_save(b,{"personality": lambda: dd.get_selected_item().get_string()})
        return b

    def bind_save(self,box,fields):
        btn = Gtk.Button(label="Save")
        box.append(btn)
        def save_click(_):
            for k,v in fields.items(): self.cfg[k]=v()
            save_config(self.cfg)
        btn.connect("clicked",save_click)

ALSettings().run()
