#!/usr/bin/env python3
"""
shell.py -- the c00l_OS session leader.

On first boot (no /etc/c00l-os/.setup_done marker) this shows a fullscreen
setup wizard: choose a username, a password, an accent color and whether
sound is on. "Finish" actually creates that Linux user for real
(useradd + chpasswd via passwordless sudo granted to the live bootstrap
account -- see /etc/sudoers.d/c00l-os), copies the themed skeleton into
their home directory, and writes /etc/c00l-os/config.json.

It then turns itself into the desktop panel/taskbar: start menu, running
clock, welcome label and a sound toggle. Openbox (already running,
started by .xinitrc before this script) handles window decoration/moving
for every app window; this process is just the dock + launcher + wizard.

Closing this window ends the X session (this is the xinitrc "session
leader"), same as closing a panel in any minimal WM setup.
"""
import json
import os
import pwd
import re
import subprocess
import sys
import time
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sound_util  # noqa: E402
import theme  # noqa: E402

APPS_DIR = "/opt/c00l-os/apps"
ICONS = theme.ICONS
USERNAME_RE = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")


def linux_user_exists(name):
    try:
        pwd.getpwnam(name)
        return True
    except KeyError:
        return False


def create_or_update_user(username, password):
    """Real account creation. Returns (ok, error_message)."""
    try:
        if linux_user_exists(username):
            subprocess.run(
                ["sudo", "-n", "chpasswd"],
                input=f"{username}:{password}\n",
                text=True,
                check=True,
                capture_output=True,
            )
        else:
            subprocess.run(
                ["sudo", "-n", "useradd", "-m", "-s", "/bin/bash", "-G", "sudo", username],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["sudo", "-n", "chpasswd"],
                input=f"{username}:{password}\n",
                text=True,
                check=True,
                capture_output=True,
            )
        return True, None
    except subprocess.CalledProcessError as e:
        msg = (e.stderr or e.stdout or str(e)).strip()
        return False, msg
    except FileNotFoundError:
        return False, "sudo/useradd not found on this system"


class Wizard:
    """Fullscreen first-boot setup flow."""

    STEPS = ("welcome", "username", "password", "accent", "sound", "working")

    def __init__(self, root, on_done):
        self.root = root
        self.on_done = on_done
        self.data = {"username": "", "password": "", "accent": theme.DEFAULT_ACCENT, "sound": True}
        self.step_index = 0

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        theme.style_window(self.root)

        self.frame = tk.Frame(self.root, bg=theme.BG)
        self.frame.pack(fill="both", expand=True)

        self.show_step("welcome")

    def clear(self):
        for w in self.frame.winfo_children():
            w.destroy()

    def card(self, parent):
        outer = tk.Frame(parent, bg=theme.BG)
        outer.place(relx=0.5, rely=0.5, anchor="center")
        card = tk.Frame(outer, bg=theme.BG2, highlightthickness=2, highlightbackground=self.data["accent"])
        card.pack(padx=4, pady=4)
        inner = tk.Frame(card, bg=theme.BG2)
        inner.pack(padx=48, pady=40)
        return inner

    def nav_button(self, parent, text, command, big=True):
        b = tk.Button(parent, text=text, command=command)
        theme.style_button(b, self.data["accent"], big=big)
        return b

    # ---- steps -------------------------------------------------------
    def show_step(self, name):
        self.clear()
        getattr(self, f"step_{name}")()

    def step_welcome(self):
        box = self.card(self.frame)
        tk.Label(box, text="c00l_OS", fg=self.data["accent"], bg=theme.BG2, font=theme.font(42, True)).pack(pady=(0, 6))
        tk.Label(
            box,
            text="first boot setup",
            fg=theme.GREY,
            bg=theme.BG2,
            font=theme.font(12),
        ).pack(pady=(0, 28))

        def go():
            sound_util.play("button")
            self.show_step("username")

        self.nav_button(box, "Get Started  >", go).pack()

    def step_username(self):
        box = self.card(self.frame)
        tk.Label(box, text="choose a username", fg=theme.FG, bg=theme.BG2, font=theme.font(18, True)).pack(pady=(0, 18))
        entry = tk.Entry(
            box,
            font=theme.font(14),
            bg=theme.BG,
            fg=theme.FG,
            insertbackground=self.data["accent"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=self.data["accent"],
            justify="center",
            width=24,
        )
        entry.pack(ipady=8)
        entry.insert(0, self.data["username"])
        entry.focus_set()
        err = tk.Label(box, text="", fg="#ff5a5a", bg=theme.BG2, font=theme.font(9))
        err.pack(pady=(8, 0))

        def go(_event=None):
            name = entry.get().strip().lower()
            if not USERNAME_RE.match(name):
                err.configure(text="lowercase letters/numbers/_/- only, must start with a letter or _")
                return
            self.data["username"] = name
            sound_util.play("button")
            self.show_step("password")

        entry.bind("<Return>", go)
        self.nav_button(box, "Next  >", go).pack(pady=(20, 0))

    def step_password(self):
        box = self.card(self.frame)
        tk.Label(box, text=f"set a password for {self.data['username']}", fg=theme.FG, bg=theme.BG2, font=theme.font(16, True)).pack(
            pady=(0, 18)
        )

        def mk_entry():
            e = tk.Entry(
                box,
                font=theme.font(14),
                bg=theme.BG,
                fg=theme.FG,
                insertbackground=self.data["accent"],
                relief="flat",
                highlightthickness=2,
                highlightbackground=self.data["accent"],
                justify="center",
                width=24,
                show="*",
            )
            e.pack(ipady=8, pady=6)
            return e

        tk.Label(box, text="password", fg=theme.GREY, bg=theme.BG2, font=theme.font(9)).pack()
        p1 = mk_entry()
        tk.Label(box, text="confirm password", fg=theme.GREY, bg=theme.BG2, font=theme.font(9)).pack()
        p2 = mk_entry()
        p1.focus_set()
        err = tk.Label(box, text="", fg="#ff5a5a", bg=theme.BG2, font=theme.font(9))
        err.pack(pady=(8, 0))

        def go(_event=None):
            a, b = p1.get(), p2.get()
            if len(a) < 4:
                err.configure(text="at least 4 characters")
                return
            if a != b:
                err.configure(text="passwords don't match")
                return
            self.data["password"] = a
            sound_util.play("button")
            self.show_step("accent")

        p2.bind("<Return>", go)
        self.nav_button(box, "Next  >", go).pack(pady=(14, 0))

    def step_accent(self):
        box = self.card(self.frame)
        tk.Label(box, text="pick your accent color", fg=theme.FG, bg=theme.BG2, font=theme.font(16, True)).pack(pady=(0, 18))
        swatches = tk.Frame(box, bg=theme.BG2)
        swatches.pack()
        selected = tk.StringVar(value=self.data["accent"])

        def pick(color):
            selected.set(color)
            self.data["accent"] = color
            sound_util.play("click")
            refresh()

        buttons = []
        for label, color in theme.PALETTE.items():
            b = tk.Button(swatches, text=label, bg=color, fg="#000000", relief="flat", font=theme.font(10, True),
                          activebackground=color, cursor="hand2", width=14, command=lambda c=color: pick(c))
            b.pack(side="top", pady=4)
            buttons.append((b, color))

        def refresh():
            for b, color in buttons:
                b.configure(highlightthickness=3 if color == selected.get() else 0, highlightbackground="#ffffff")

        refresh()

        def go():
            sound_util.play("button")
            self.show_step("sound")

        self.nav_button(box, "Next  >", go).pack(pady=(20, 0))

    def step_sound(self):
        box = self.card(self.frame)
        tk.Label(box, text="sound effects", fg=theme.FG, bg=theme.BG2, font=theme.font(16, True)).pack(pady=(0, 14))
        var = tk.BooleanVar(value=self.data["sound"])
        cb = tk.Checkbutton(
            box,
            text="enable c00l_OS sound effects",
            variable=var,
            bg=theme.BG2,
            fg=theme.FG,
            selectcolor=theme.BG,
            activebackground=theme.BG2,
            activeforeground=theme.FG,
            font=theme.font(11),
        )
        cb.pack(pady=(0, 20))

        def go():
            self.data["sound"] = var.get()
            if self.data["sound"]:
                sound_util.play("button")
            self.finish()

        self.nav_button(box, "Finish  >", go).pack()

    def step_working(self):
        box = self.card(self.frame)
        tk.Label(box, text="setting up c00l_OS ...", fg=theme.FG, bg=theme.BG2, font=theme.font(14)).pack()

    def finish(self):
        self.show_step("working")
        self.root.update()
        self.root.after(100, self._do_finish)

    def _do_finish(self):
        ok, err = create_or_update_user(self.data["username"], self.data["password"])
        if not ok:
            messagebox.showerror("c00l_OS setup", f"Couldn't create the account:\n{err}\n\nPlease try a different username.")
            self.show_step("username")
            return
        cfg = theme.load_config()
        cfg.update(
            {
                "username": self.data["username"],
                "accent": self.data["accent"],
                "sound": self.data["sound"],
                "setup_done": True,
            }
        )
        theme.save_config(cfg)
        try:
            with open("/etc/c00l-os/.setup_done", "w") as f:
                f.write("1")
        except Exception:
            pass
        sound_util.play("boot")
        self.on_done()


class Panel:
    """The always-on bottom taskbar: start menu, launchers, clock."""

    APP_LAUNCHERS = [
        ("Notepad", "notepad.png", [sys.executable, f"{APPS_DIR}/notepad.py"]),
        ("Minesweeper", "minesweeper.png", [sys.executable, f"{APPS_DIR}/minesweeper.py"]),
        ("Terminal", "terminal.png", [f"{APPS_DIR}/start_c00l_term.sh"]),
        ("Browser", "browser.png", [sys.executable, f"{APPS_DIR}/browser.py"]),
    ]

    HEIGHT = 46

    def __init__(self, root):
        self.root = root
        self.cfg = theme.load_config()
        self.accent = self.cfg.get("accent", theme.DEFAULT_ACCENT)
        self.root.overrideredirect(True)
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        self.root.geometry(f"{sw}x{self.HEIGHT}+0+{sh - self.HEIGHT}")
        self.root.attributes("-topmost", True)
        try:
            self.root.attributes("-type", "dock")
        except tk.TclError:
            pass
        theme.style_window(self.root)
        self._set_wallpaper()
        self._build()
        self._tick_clock()

    def _set_wallpaper(self):
        try:
            subprocess.Popen(
                ["feh", "--bg-fill", f"{theme.ASSETS}/wallpaper.png"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            try:
                subprocess.Popen(
                    ["xsetroot", "-solid", theme.BG],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                pass

    def _build(self):
        bar = tk.Frame(self.root, bg=theme.BG2, highlightthickness=1, highlightbackground=self.accent)
        bar.pack(fill="both", expand=True)

        start_btn = tk.Button(bar, text=" c00l_OS ", command=self.toggle_menu)
        theme.style_button(start_btn, self.accent, big=True)
        start_btn.pack(side="left", padx=8, pady=5)

        self.welcome = tk.Label(
            bar,
            text=f"welcome, {self.cfg.get('username', 'user')}",
            bg=theme.BG2,
            fg=theme.GREY,
            font=theme.font(9),
        )
        self.welcome.pack(side="left", padx=14)

        self.clock_lbl = tk.Label(bar, bg=theme.BG2, fg=self.accent, font=theme.font(12, True))
        self.clock_lbl.pack(side="right", padx=16)

        sound_var = tk.BooleanVar(value=self.cfg.get("sound", True))

        def toggle_sound():
            self.cfg["sound"] = sound_var.get()
            theme.save_config(self.cfg)
            if sound_var.get():
                sound_util.play("ping")

        sound_chk = tk.Checkbutton(
            bar,
            text="sound",
            variable=sound_var,
            command=toggle_sound,
            bg=theme.BG2,
            fg=theme.GREY,
            selectcolor=theme.BG,
            activebackground=theme.BG2,
            font=theme.font(9),
        )
        sound_chk.pack(side="right", padx=4)

        self.menu = None

    def _tick_clock(self):
        self.clock_lbl.configure(text=time.strftime("%H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    def toggle_menu(self):
        if self.menu is not None and self.menu.winfo_exists():
            self.menu.destroy()
            self.menu = None
            return
        sound_util.play("click")
        m = tk.Toplevel(self.root)
        m.overrideredirect(True)
        m.attributes("-topmost", True)
        theme.style_window(m)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        width = 220
        m.geometry(f"{width}x{(len(self.APP_LAUNCHERS) + 2) * 44 + 20}+8+{sh - self.HEIGHT - (len(self.APP_LAUNCHERS) + 2) * 44 - 24}")
        frame = tk.Frame(m, bg=theme.BG2, highlightthickness=2, highlightbackground=self.accent)
        frame.pack(fill="both", expand=True)

        for label, _icon, cmd in self.APP_LAUNCHERS:
            b = tk.Button(frame, text=label, anchor="w", command=lambda c=cmd: self.launch(c))
            theme.style_button(b, self.accent)
            b.pack(fill="x", padx=8, pady=4)

        tk.Frame(frame, bg=self.accent, height=1).pack(fill="x", padx=8, pady=4)

        restart_btn = tk.Button(frame, text="Restart", anchor="w", command=lambda: self.power_action("reboot"))
        theme.style_button(restart_btn, self.accent)
        restart_btn.pack(fill="x", padx=8, pady=4)

        poweroff_btn = tk.Button(frame, text="Power Off", anchor="w", command=lambda: self.power_action("poweroff"))
        theme.style_button(poweroff_btn, self.accent)
        poweroff_btn.pack(fill="x", padx=8, pady=4)

        self.menu = m

    def launch(self, cmd):
        sound_util.play("button")
        if self.menu:
            self.menu.destroy()
            self.menu = None
        try:
            subprocess.Popen(cmd)
        except Exception as e:
            messagebox.showerror("c00l_OS", f"Couldn't launch that app:\n{e}")

    def power_action(self, action):
        if self.menu:
            self.menu.destroy()
            self.menu = None
        if not messagebox.askyesno("c00l_OS", f"{action.capitalize()} now?"):
            return
        sound_util.play("slash")
        try:
            subprocess.run(["sudo", "-n", "systemctl", action], check=False)
        except FileNotFoundError:
            pass


def main():
    root = tk.Tk()
    cfg = theme.load_config()

    def start_panel():
        for w in root.winfo_children():
            w.destroy()
        Panel(root)

    if cfg.get("setup_done") and os.path.exists("/etc/c00l-os/.setup_done"):
        Panel(root)
    else:
        Wizard(root, on_done=start_panel)

    root.mainloop()


if __name__ == "__main__":
    main()
