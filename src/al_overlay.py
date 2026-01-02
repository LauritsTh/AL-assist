#!/usr/bin/env python3
import gi
import math
import time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
import cairo

class ALOverylay(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_app_paintable(True)
        self.set_default_size(300, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("draw", self.on_draw)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        self.set_visual(visual)

        self.phase = 0
        GLib.timeout_add(30, self.animate)

    def animate(self):
        self.phase += 0.15
        self.queue_draw()
        return True

    def on_draw(self, widget, cr):
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        cx, cy = 150, 150
        for i in range(3):
            radius = 40 + i * 25 + math.sin(self.phase + i) * 10
            cr.set_line_width(4)
            cr.set_source_rgba(0.2, 0.6, 1.0, 0.6)
            cr.arc(cx, cy, radius, 0, 2 * math.pi)
            cr.stroke()

if __name__ == "__main__":
    win = ALOverylay()
    win.show_all()
    Gtk.main()
