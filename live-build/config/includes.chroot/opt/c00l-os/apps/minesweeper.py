#!/usr/bin/env python3
"""c00l_OS Minesweeper -- a complete, themed, fully playable minesweeper."""
import os
import random
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sound_util  # noqa: E402
import theme  # noqa: E402

DIFFICULTIES = {
    "Beginner (9x9, 10)": (9, 9, 10),
    "Intermediate (16x16, 40)": (16, 16, 40),
    "Expert (30x16, 99)": (30, 16, 99),
}

NUMBER_COLORS = {
    1: "#4da6ff",
    2: "#4dff88",
    3: "#ff5a5a",
    4: "#b84dff",
    5: "#ffcf4d",
    6: "#4dfff2",
    7: "#ffffff",
    8: "#8a8a8c",
}


class Cell:
    __slots__ = ("mine", "revealed", "flagged", "count", "btn")

    def __init__(self):
        self.mine = False
        self.revealed = False
        self.flagged = False
        self.count = 0
        self.btn = None


class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.accent = theme.accent()
        theme.style_window(root, "c00l_Minesweeper", f"{theme.ICONS}/minesweeper.png")

        self.rows = self.cols = self.mines = 0
        self.cells = []
        self.first_click_done = False
        self.game_over_flag = False
        self.flag_count = 0
        self.elapsed = 0
        self.timer_job = None

        self._build_chrome()
        self.new_game(*DIFFICULTIES["Beginner (9x9, 10)"])

    # ------------------------------------------------------------------
    def _build_chrome(self):
        menubar = tk.Menu(self.root, bg=theme.BG2, fg=theme.FG, activebackground=self.accent, activeforeground="#000", bd=0)
        game_menu = tk.Menu(menubar, tearoff=0, bg=theme.BG2, fg=theme.FG, activebackground=self.accent, activeforeground="#000")
        for label, dims in DIFFICULTIES.items():
            game_menu.add_command(label=label, command=lambda d=dims: self.new_game(*d))
        game_menu.add_separator()
        game_menu.add_command(label="Restart", command=lambda: self.new_game(self.rows, self.cols, self.mines))
        menubar.add_cascade(label="Game", menu=game_menu)
        self.root.config(menu=menubar)

        top = tk.Frame(self.root, bg=theme.BG2, highlightthickness=1, highlightbackground=self.accent)
        top.pack(fill="x")
        self.mine_lbl = tk.Label(top, text="010", bg=theme.BG2, fg="#ff5a5a", font=theme.font(16, True), width=4)
        self.mine_lbl.pack(side="left", padx=10, pady=6)

        self.smiley = tk.Button(top, text=":)", command=lambda: self.new_game(self.rows, self.cols, self.mines))
        theme.style_button(self.smiley, self.accent, big=True)
        self.smiley.pack(side="left", padx=10)

        self.timer_lbl = tk.Label(top, text="000", bg=theme.BG2, fg=self.accent, font=theme.font(16, True), width=4)
        self.timer_lbl.pack(side="right", padx=10, pady=6)

        self.board_frame = tk.Frame(self.root, bg=theme.BG)
        self.board_frame.pack(padx=10, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _close(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.root.destroy()

    # ------------------------------------------------------------------
    def new_game(self, rows, cols, mines):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.rows, self.cols, self.mines = rows, cols, mines
        self.first_click_done = False
        self.game_over_flag = False
        self.flag_count = 0
        self.elapsed = 0
        self.smiley.configure(text=":)")
        self.timer_lbl.configure(text="000")
        self._update_mine_label()

        for w in self.board_frame.winfo_children():
            w.destroy()

        self.cells = [[Cell() for _ in range(cols)] for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                cell = self.cells[r][c]
                btn = tk.Button(
                    self.board_frame,
                    text="",
                    width=2,
                    height=1,
                    bg=theme.BG3,
                    fg=theme.FG,
                    activebackground=self.accent,
                    relief="raised",
                    bd=1,
                    font=theme.font(10, True),
                )
                btn.grid(row=r, column=c)
                btn.bind("<Button-1>", lambda e, rr=r, cc=c: self.on_left_click(rr, cc))
                btn.bind("<Button-3>", lambda e, rr=r, cc=c: self.on_right_click(rr, cc))
                cell.btn = btn

    def _update_mine_label(self):
        remaining = max(0, self.mines - self.flag_count)
        self.mine_lbl.configure(text=f"{remaining:03d}")

    def _tick(self):
        if self.game_over_flag:
            return
        self.elapsed += 1
        self.timer_lbl.configure(text=f"{min(self.elapsed, 999):03d}")
        self.timer_job = self.root.after(1000, self._tick)

    # ------------------------------------------------------------------
    def _place_mines(self, exclude_r, exclude_c):
        safe = {
            (exclude_r + dr, exclude_c + dc)
            for dr in (-1, 0, 1)
            for dc in (-1, 0, 1)
            if 0 <= exclude_r + dr < self.rows and 0 <= exclude_c + dc < self.cols
        }
        candidates = [
            (r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) not in safe
        ]
        if len(candidates) < self.mines:
            candidates = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) != (exclude_r, exclude_c)]
        for r, c in random.sample(candidates, min(self.mines, len(candidates))):
            self.cells[r][c].mine = True

        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c].mine:
                    continue
                self.cells[r][c].count = sum(
                    1
                    for dr in (-1, 0, 1)
                    for dc in (-1, 0, 1)
                    if (dr or dc) and 0 <= r + dr < self.rows and 0 <= c + dc < self.cols and self.cells[r + dr][c + dc].mine
                )

    def _neighbors(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    # ------------------------------------------------------------------
    def on_left_click(self, r, c):
        if self.game_over_flag:
            return
        cell = self.cells[r][c]
        if cell.flagged or cell.revealed:
            return

        if not self.first_click_done:
            self._place_mines(r, c)
            self.first_click_done = True
            self._tick()

        sound_util.play("click")

        if cell.mine:
            self._lose(r, c)
            return

        self._reveal_flood(r, c)
        self._check_win()

    def _reveal_flood(self, r, c):
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            cell = self.cells[cr][cc]
            if cell.revealed or cell.flagged:
                continue
            cell.revealed = True
            self._paint_revealed(cr, cc)
            if cell.count == 0:
                for nr, nc in self._neighbors(cr, cc):
                    if not self.cells[nr][nc].revealed and not self.cells[nr][nc].mine:
                        stack.append((nr, nc))

    def _paint_revealed(self, r, c):
        cell = self.cells[r][c]
        btn = cell.btn
        btn.configure(relief="sunken", bg=theme.BG, state="disabled",
                       disabledforeground=NUMBER_COLORS.get(cell.count, theme.GREY))
        btn.configure(text=str(cell.count) if cell.count else "")

    def on_right_click(self, r, c):
        if self.game_over_flag:
            return
        cell = self.cells[r][c]
        if cell.revealed:
            return
        cell.flagged = not cell.flagged
        sound_util.play("snap")
        if cell.flagged:
            cell.btn.configure(text="F", fg="#ff5a5a")
            self.flag_count += 1
        else:
            cell.btn.configure(text="", fg=theme.FG)
            self.flag_count -= 1
        self._update_mine_label()

    def _check_win(self):
        total = self.rows * self.cols
        revealed = sum(1 for row in self.cells for cell in row if cell.revealed)
        if revealed == total - self.mines:
            self._win()

    def _win(self):
        self.game_over_flag = True
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.smiley.configure(text="8)")
        for row in self.cells:
            for cell in row:
                if cell.mine and not cell.flagged:
                    cell.btn.configure(text="F", fg="#4dff88")
        self.flag_count = self.mines
        self._update_mine_label()
        sound_util.play("victory")

    def _lose(self, br, bc):
        self.game_over_flag = True
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.smiley.configure(text="X(")
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[r][c]
                if cell.mine:
                    is_hit = (r, c) == (br, bc)
                    cell.btn.configure(
                        text="*",
                        bg="#ff5a5a" if is_hit else theme.BG3,
                        fg="#000000" if is_hit else "#ff5a5a",
                        disabledforeground="#000000" if is_hit else "#ff5a5a",
                        state="disabled",
                    )
                elif cell.flagged:
                    cell.btn.configure(text="X", fg="#ffcf4d")
        sound_util.play("hit")
        self.root.after(450, lambda: sound_util.play("ouch"))


def main():
    root = tk.Tk()
    Minesweeper(root)
    root.mainloop()


if __name__ == "__main__":
    main()
