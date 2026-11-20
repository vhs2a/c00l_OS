#!/usr/bin/env python3
"""c00l_OS Notepad -- a small, real, themed text editor."""
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sound_util  # noqa: E402
import theme  # noqa: E402


class Notepad:
    def __init__(self, root, path=None):
        self.root = root
        self.path = path
        self.dirty = False
        acc = theme.accent()
        theme.style_window(root, "c00l_Notepad", f"{theme.ICONS}/notepad.png", 760, 560)

        menubar = tk.Menu(root, bg=theme.BG2, fg=theme.FG, activebackground=acc, activeforeground="#000", bd=0)
        filemenu = tk.Menu(menubar, tearoff=0, bg=theme.BG2, fg=theme.FG, activebackground=acc, activeforeground="#000")
        filemenu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        filemenu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        filemenu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        filemenu.add_command(label="Save As...", command=self.save_file_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0, bg=theme.BG2, fg=theme.FG, activebackground=acc, activeforeground="#000")
        editmenu.add_command(label="Undo", command=lambda: self.text.event_generate("<<Undo>>"), accelerator="Ctrl+Z")
        editmenu.add_command(label="Redo", command=lambda: self.text.event_generate("<<Redo>>"), accelerator="Ctrl+Y")
        editmenu.add_separator()
        editmenu.add_command(label="Cut", command=lambda: self.text.event_generate("<<Cut>>"))
        editmenu.add_command(label="Copy", command=lambda: self.text.event_generate("<<Copy>>"))
        editmenu.add_command(label="Paste", command=lambda: self.text.event_generate("<<Paste>>"))
        menubar.add_cascade(label="Edit", menu=editmenu)
        root.config(menu=menubar)

        toolbar = tk.Frame(root, bg=theme.BG2, highlightthickness=1, highlightbackground=acc)
        toolbar.pack(fill="x")
        for label, cmd in (("New", self.new_file), ("Open", self.open_file), ("Save", self.save_file)):
            b = tk.Button(toolbar, text=label, command=cmd)
            theme.style_button(b, acc)
            b.pack(side="left", padx=6, pady=6)

        self.title_lbl = tk.Label(toolbar, text="untitled", bg=theme.BG2, fg=theme.GREY, font=theme.font(9))
        self.title_lbl.pack(side="right", padx=10)

        body = tk.Frame(root, bg=theme.BG)
        body.pack(fill="both", expand=True)

        self.linenos = tk.Text(body, width=4, padx=4, takefocus=0, border=0, state="disabled",
                                bg=theme.BG, fg=theme.GREY, font=theme.font(11))
        self.linenos.pack(side="left", fill="y")

        self.text = tk.Text(
            body,
            wrap="word",
            undo=True,
            bg=theme.BG,
            fg=theme.FG,
            insertbackground=acc,
            selectbackground=acc,
            selectforeground="#000000",
            relief="flat",
            font=theme.font(11),
            padx=8,
            pady=6,
        )
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(body, command=self._on_scroll)
        scrollbar.pack(side="right", fill="y")
        self.text.configure(yscrollcommand=scrollbar.set)

        self.status = tk.Label(root, text="ready", bg=theme.BG2, fg=theme.GREY, anchor="w", font=theme.font(9))
        self.status.pack(fill="x", side="bottom")

        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<KeyRelease>", lambda e: self._update_linenos())
        root.bind("<Control-n>", lambda e: self.new_file())
        root.bind("<Control-o>", lambda e: self.open_file())
        root.bind("<Control-s>", lambda e: self.save_file())
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        if path and os.path.isfile(path):
            self._load(path)
        self._update_linenos()

    def _on_scroll(self, *args):
        self.text.yview(*args)
        self.linenos.yview(*args)

    def _update_linenos(self):
        count = int(self.text.index("end-1c").split(".")[0])
        content = "\n".join(str(i) for i in range(1, count + 1))
        self.linenos.configure(state="normal")
        self.linenos.delete("1.0", "end")
        self.linenos.insert("1.0", content)
        self.linenos.configure(state="disabled")
        self.linenos.yview_moveto(self.text.yview()[0])

    def _on_modified(self, _event=None):
        if self.text.edit_modified():
            self.dirty = True
            self._set_title()
            self.text.edit_modified(False)
        self._update_linenos()

    def _set_title(self):
        name = os.path.basename(self.path) if self.path else "untitled"
        mark = "*" if self.dirty else ""
        self.title_lbl.configure(text=f"{mark}{name}")
        self.root.title(f"c00l_Notepad - {name}{mark}")

    def new_file(self):
        if not self._confirm_discard():
            return
        self.path = None
        self.text.delete("1.0", "end")
        self.dirty = False
        self._set_title()
        sound_util.play("button")

    def open_file(self):
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename()
        if path:
            self._load(path)
            sound_util.play("button")

    def _load(self, path):
        try:
            with open(path, "r", errors="replace") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("c00l_Notepad", f"Couldn't open file:\n{e}")
            return
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.path = path
        self.dirty = False
        self._set_title()
        self._update_linenos()

    def save_file(self):
        if not self.path:
            return self.save_file_as()
        self._write(self.path)

    def save_file_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            self._write(path)

    def _write(self, path):
        try:
            with open(path, "w") as f:
                f.write(self.text.get("1.0", "end-1c"))
        except Exception as e:
            messagebox.showerror("c00l_Notepad", f"Couldn't save file:\n{e}")
            return
        self.path = path
        self.dirty = False
        self._set_title()
        self.status.configure(text=f"saved {path}")
        sound_util.play("button")

    def _confirm_discard(self):
        if not self.dirty:
            return True
        resp = messagebox.askyesnocancel("c00l_Notepad", "Save changes before continuing?")
        if resp is None:
            return False
        if resp:
            self.save_file()
        return True

    def on_close(self):
        if self._confirm_discard():
            self.root.destroy()


def main():
    root = tk.Tk()
    path = sys.argv[1] if len(sys.argv) > 1 else None
    Notepad(root, path)
    root.mainloop()


if __name__ == "__main__":
    main()
