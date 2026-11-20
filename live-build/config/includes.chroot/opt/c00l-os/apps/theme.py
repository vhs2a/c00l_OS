#!/usr/bin/env python3
"""Shared color palette, fonts and small Tk helpers for every c00l_OS app."""
import json
import os

CONFIG_PATH = "/etc/c00l-os/config.json"
ASSETS = "/opt/c00l-os/assets"
ICONS = f"{ASSETS}/icons"

DEFAULT_ACCENT = "#cd1c26"

PALETTE = {
    "c00l Red": "#cd1c26",
    "Toxic Green": "#1fcf6c",
    "Cyber Blue": "#1c8ecd",
    "Signal Purple": "#8a1ccd",
    "Amber Alert": "#cd8a1c",
}

BG = "#0a0a0c"
BG2 = "#101013"
BG3 = "#17171a"
FG = "#e8e8e8"
GREY = "#8a8a8c"
BORDER_DARK = "#5a0e13"

FONT_FAMILY = "DejaVu Sans Mono"


def font(size=10, bold=False):
    return (FONT_FAMILY, size, "bold" if bold else "normal")


def load_config():
    defaults = {
        "username": "user",
        "accent": DEFAULT_ACCENT,
        "sound": True,
        "setup_done": False,
    }
    try:
        with open(CONFIG_PATH) as f:
            data = json.load(f)
        defaults.update(data)
    except Exception:
        pass
    return defaults


def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cfg, f, indent=2)
    os.replace(tmp, CONFIG_PATH)


def accent():
    return load_config().get("accent", DEFAULT_ACCENT)


def style_button(btn, accent_color=None, big=False):
    """Apply the flat black/red bordered look used everywhere in c00l_OS."""
    acc = accent_color or accent()
    btn.configure(
        bg=BG2,
        fg=FG,
        activebackground=acc,
        activeforeground="#000000",
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=acc,
        highlightcolor=acc,
        font=font(12 if big else 10, bold=big),
        cursor="hand2",
        padx=10,
        pady=6,
    )

    def on_enter(_e):
        btn.configure(bg=acc, fg="#000000")

    def on_leave(_e):
        btn.configure(bg=BG2, fg=FG)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


def style_window(win, title=None, icon_path=None, w=None, h=None):
    win.configure(bg=BG)
    if title:
        win.title(title)
    if w and h:
        win.geometry(f"{w}x{h}")
    try:
        if icon_path and os.path.isfile(icon_path):
            from tkinter import PhotoImage

            win.iconphoto(True, PhotoImage(file=icon_path))
    except Exception:
        pass
