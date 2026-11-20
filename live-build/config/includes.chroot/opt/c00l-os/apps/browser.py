#!/usr/bin/env python3
"""
c00l_browser -- c00l_OS's own web browser.

A real, working browser: its own chrome (address bar, back/forward/reload,
home button) written with GTK, rendering pages with WebKitGTK underneath --
exactly how every desktop browser (Chrome, Edge, Safari, GNOME Web...) is
built: an original front-end over a standard, battle-tested engine, because
writing a rendering engine from scratch is not something any one project
reasonably does.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sound_util  # noqa: E402
import theme  # noqa: E402

import gi  # noqa: E402

gi.require_version("Gtk", "3.0")
try:
    gi.require_version("WebKit2", "4.1")
except ValueError:
    gi.require_version("WebKit2", "4.0")

from gi.repository import Gdk, GLib, Gtk, WebKit2  # noqa: E402

HOME_URL = "file:///opt/c00l-os/www/home.html"


def build_css(accent):
    return f"""
    window {{ background-color: {theme.BG}; }}
    .c00l-toolbar {{
        background-color: {theme.BG2};
        border-bottom: 2px solid {accent};
        padding: 6px;
    }}
    .c00l-toolbar button {{
        background-color: {theme.BG2};
        color: {theme.FG};
        border: 1px solid {accent};
        border-radius: 4px;
        padding: 4px 10px;
    }}
    .c00l-toolbar button:hover {{
        background-color: {accent};
        color: #000000;
    }}
    entry.c00l-address {{
        background-color: {theme.BG};
        color: {theme.FG};
        border: 1px solid {accent};
        border-radius: 4px;
        caret-color: {accent};
        padding: 4px 8px;
    }}
    """


class Browser(Gtk.Window):
    def __init__(self):
        super().__init__(title="c00l_browser")
        self.accent = theme.accent()
        self.set_default_size(1100, 720)
        try:
            self.set_icon_from_file(f"{theme.ICONS}/browser.png")
        except GLib.Error:
            pass

        provider = Gtk.CssProvider()
        provider.load_from_data(build_css(self.accent).encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(root_box)

        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        toolbar.get_style_context().add_class("c00l-toolbar")
        root_box.pack_start(toolbar, False, False, 0)

        self.back_btn = self._nav_button("<", self.on_back)
        self.fwd_btn = self._nav_button(">", self.on_forward)
        self.reload_btn = self._nav_button("R", self.on_reload)
        self.home_btn = self._nav_button("Home", self.on_home)
        toolbar.pack_start(self.back_btn, False, False, 2)
        toolbar.pack_start(self.fwd_btn, False, False, 2)
        toolbar.pack_start(self.reload_btn, False, False, 2)
        toolbar.pack_start(self.home_btn, False, False, 2)

        self.address = Gtk.Entry()
        self.address.get_style_context().add_class("c00l-address")
        self.address.connect("activate", self.on_navigate)
        toolbar.pack_start(self.address, True, True, 4)

        go_btn = self._nav_button("Go", self.on_navigate)
        toolbar.pack_start(go_btn, False, False, 2)

        self.webview = WebKit2.WebView()
        self.webview.connect("notify::uri", self.on_uri_changed)
        self.webview.connect("notify::title", self.on_title_changed)
        self.webview.load_uri(HOME_URL)
        root_box.pack_start(self.webview, True, True, 0)

        self.connect("destroy", Gtk.main_quit)
        self.show_all()

    def _nav_button(self, label, handler):
        b = Gtk.Button(label=label)
        b.connect("clicked", handler)
        return b

    def navigate_to(self, text):
        text = text.strip()
        if not text:
            return
        if "." in text and " " not in text and not text.startswith("search:"):
            if not text.startswith(("http://", "https://", "file://")):
                text = "https://" + text
            self.webview.load_uri(text)
        else:
            query = text[len("search:"):] if text.startswith("search:") else text
            from urllib.parse import quote_plus

            self.webview.load_uri(f"https://duckduckgo.com/html/?q={quote_plus(query)}")

    def on_navigate(self, _widget):
        sound_util.play("button")
        self.navigate_to(self.address.get_text())

    def on_back(self, _widget):
        sound_util.play("click")
        if self.webview.can_go_back():
            self.webview.go_back()

    def on_forward(self, _widget):
        sound_util.play("click")
        if self.webview.can_go_forward():
            self.webview.go_forward()

    def on_reload(self, _widget):
        sound_util.play("click")
        self.webview.reload()

    def on_home(self, _widget):
        sound_util.play("button")
        self.webview.load_uri(HOME_URL)

    def on_uri_changed(self, webview, _param):
        uri = webview.get_uri() or ""
        self.address.set_text(uri)

    def on_title_changed(self, webview, _param):
        title = webview.get_title() or "c00l_browser"
        self.set_title(f"{title} - c00l_browser")


def main():
    Browser()
    Gtk.main()


if __name__ == "__main__":
    main()
