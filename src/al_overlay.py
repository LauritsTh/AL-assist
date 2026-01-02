#!/usr/bin/env python3
import gi, time, math
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GObject, cairo

CONFIG_PATH = "~/.config/al_config.json"
import json, os
cfg = json.load(open(os.path.expanduser(CONFIG_PATH)))

class ALOverlay(Gtk.Window):
    def __init__(self):
        super().__init__(title="AL Overlay")
        self.set_default_size(200,200)
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_keep_above(True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.override_background_color(Gtk.StateFlags.NORMAL,Gdk.RGBA(0,0,0,0))

        self.drawing = Gtk.DrawingArea()
        self.drawing.set_draw_func(self.on_draw)
        self.add(self.drawing)

        GLib.timeout_add(50,self.tick)
        self.phase = 0

    def tick(self):
        self.phase += 0.1
        self.drawing.queue_draw()
        return True

    def on_draw(self, da, ctx, width, height, data):
        ctx.set_line_width(3)
        color = Gdk.RGBA()
        color.parse(cfg.get("waveform_color","#50B4FF"))
        ctx.set_source_rgba(color.red, color.green, color.blue, 0.8)
        for r in range(1,6):
            radius = 20 + math.sin(self.phase + r) * 10
            ctx.arc(width//2, height//2, radius, 0, 2*math.pi)
            ctx.stroke()

if __name__=="__main__":
    win = ALOverlay()
    win.show_all()
    Gtk.main()
#test