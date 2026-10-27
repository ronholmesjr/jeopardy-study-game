#!/usr/bin/env python3
"""
jeopardy_gui.py -- the Jeopardy study game with a Tkinter window!

Same games, same questions, and same scoring as jeopardy.py -- this
file is only the graphics front end. The terminal version still
works exactly as before; this one just gives you a clickable board.

Look: forest green (our own color, not TV blue), white category
names, gold dollar amounts, everything in ONE window -- board,
question, feedback, results, and high scores. Every separate box
is drawn as a square little old-style TV screen: dark bezel,
rounded screen, a hint of glare and scanlines.

Run it:
  python jeopardy_gui.py            (Windows: py jeopardy_gui.py)
  QUIZ_SEED=7 / --seed=7            same board every run, like the
                                    terminal version

IMPORTANT: jeopardy.py must be in the SAME folder as this file.
All the questions and the high-score helpers live there; this file
imports them.
"""

import os
import random
import sys
import tkinter as tk

try:
    import jeopardy
except ImportError:
    print("jeopardy_gui.py needs jeopardy.py in the same folder.")
    raise SystemExit(1)

# ------------------------------------------------------------------
# Colors and fonts -- change these lines to restyle the whole game.
# ------------------------------------------------------------------
WINDOW_BG = "#10291a"      # very dark green window background
HEADER_BG = "#14532d"      # darker forest green for category headers
SQUARE_BG = "#228B22"      # forest green squares
SQUARE_HOVER = "#2eb82e"   # lighter green while a question is open
USED_BG = "#3a4a3e"        # grey-green for used-up squares
USED_FG = "#9db3a4"
GOLD = "#FFCC00"           # dollar amounts
WHITE = "white"
GOOD = "#8bf79b"           # feedback: right answer
BAD = "#ff9d9d"            # feedback: wrong answer

TITLE_FONT = ("Arial", 20, "bold")
SCORE_FONT = ("Arial", 14, "bold")
CAT_FONT = ("Arial", 10, "bold")
VALUE_FONT = ("Arial", 15, "bold")
QUESTION_FONT = ("Arial", 13)
BUTTON_FONT = ("Arial", 12, "bold")

# Every board box is a square TV screen, all the same size.
TILE_SIZE = 98
TILE_GAP = 7
BEZEL_BG = "#223028"       # dark grey-green TV casing
BEZEL_EDGE = "#060d08"

VALUES = jeopardy.VALUES
GAMES = {
    "linux": ("Linux Commands", jeopardy.LINUX_BANK, "linux"),
    "ai901": ("AI-901", jeopardy.AI901_BANK, "ai901"),
}


def _rounded_points(x1, y1, x2, y2, r):
    """Points for a rounded rectangle, drawn as a smooth polygon."""
    return [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]


class TVScreen(tk.Canvas):
    """A box drawn like a little old-style TV screen.

    Dark rounded bezel, a green screen with faint scanlines and a
    glare streak, and the text sitting on the glass. Give it a
    command and it clicks like a button.
    """

    def __init__(self, parent, text, font, fg, screen_bg, command=None,
                 width=TILE_SIZE, height=TILE_SIZE, wraplength=None,
                 line_color="#0d3d20", text_anchor="center"):
        super().__init__(parent, width=width, height=height, bg=WINDOW_BG,
                         highlightthickness=0, bd=0,
                         cursor="hand2" if command else "")
        self.text = text
        self.font = font
        self.fg = fg
        self.screen_bg = screen_bg
        self.base_bg = screen_bg
        self.line_color = line_color
        self.command = command
        self.text_anchor = text_anchor
        self.wraplength = wraplength or width - 22
        self.enabled = True
        self.used = False
        self.draw()
        self.bind("<Button-1>", self._click)

    def draw(self, bg=None):
        bg = bg or self.screen_bg
        w = int(self.cget("width"))
        h = int(self.cget("height"))
        self.delete("all")
        # Casing shadow, then the bezel, then the glass screen.
        self.create_polygon(_rounded_points(3, 5, w - 1, h - 1, 16),
                            smooth=True, fill="#040a06", outline="")
        self.create_polygon(_rounded_points(1, 1, w - 4, h - 4, 16),
                            smooth=True, fill=BEZEL_BG, outline=BEZEL_EDGE,
                            width=2)
        self.create_polygon(_rounded_points(8, 8, w - 11, h - 11, 12),
                            smooth=True, fill=bg, outline="#6f8a73", width=1)
        # Faint scanlines across the glass.
        for y in range(16, h - 14, 5):
            self.create_line(14, y, w - 17, y, fill=self.line_color)
        # A soft glare streak across the top-left corner of the glass.
        self.create_polygon([14, 10, w * 0.42, 10, w * 0.24, h * 0.46,
                             12, h * 0.38],
                            fill="#eaffea", stipple="gray12", outline="")
        # The text, with a slight shadow like light on glass.
        if self.text_anchor == "w":
            self.create_text(19, h / 2 + 1, text=self.text, font=self.font,
                             fill="#062b12", anchor="w", width=self.wraplength,
                             justify="left")
            self.create_text(18, h / 2, text=self.text, font=self.font,
                             fill=self.fg, anchor="w", width=self.wraplength,
                             justify="left")
        else:
            self.create_text(w / 2, h / 2 + 1, text=self.text, font=self.font,
                             fill="#062b12", anchor="center",
                             width=self.wraplength, justify="center")
            self.create_text(w / 2, h / 2, text=self.text, font=self.font,
                             fill=self.fg, anchor="center",
                             width=self.wraplength, justify="center")

    def _click(self, _event=None):
        if self.command is not None and self.enabled and not self.used:
            self.command()

    def invoke(self):
        """Same as clicking -- used by the automated GUI tests."""
        self._click()

    def set_enabled(self, enabled):
        self.enabled = enabled
        self.config(cursor="hand2" if enabled and self.command else "")

    def set_active(self):
        self.draw(SQUARE_HOVER)

    def set_used(self):
        self.used = True
        self.enabled = False
        self.text = "---"
        self.fg = USED_FG
        self.line_color = "#2c3a31"
        self.config(cursor="")
        self.draw(USED_BG)


class JeopardyApp(tk.Tk):
    """One window, three screens swapped in and out: start, game,
    results. Only one is packed (visible) at a time."""

    def __init__(self, rng):
        super().__init__()
        self.rng = rng
        self.title("Jeopardy -- Study Edition")
        self.configure(bg=WINDOW_BG)
        self.geometry("1040x1020")
        self.minsize(980, 940)

        # Scoreboard strip across the top, always visible.
        top = tk.Frame(self, bg=WINDOW_BG)
        top.pack(fill="x", padx=12, pady=10)
        tk.Label(top, text="JEOPARDY", font=TITLE_FONT,
                 bg=WINDOW_BG, fg=GOLD).pack(side="left")
        self.score_label = tk.Label(top, text="", font=SCORE_FONT,
                                     bg=WINDOW_BG, fg=WHITE)
        self.score_label.pack(side="right")

        self.start_frame = tk.Frame(self, bg=WINDOW_BG)
        self.game_frame = tk.Frame(self, bg=WINDOW_BG)
        self.results_frame = tk.Frame(self, bg=WINDOW_BG)
        self.build_start_screen()
        self.show(self.start_frame)

        # Game state (filled in by start_game).
        self.game_name = ""
        self.kind = ""
        self.board = {}
        self.square_tiles = {}
        self.current = None        # (category, value, item) being asked
        self.score = 0
        self.asked = 0
        self.correct_count = 0
        self.missed = []

    # ---------------- screen switching ----------------
    def show(self, frame):
        for f in (self.start_frame, self.game_frame, self.results_frame):
            f.pack_forget()
        frame.pack(fill="both", expand=True, padx=12, pady=6)

    def update_scoreboard(self):
        left = sum(1 for cat in self.board
                   for v in VALUES if self.board[cat][v] is not None)
        self.score_label.config(
            text=f"Score: {jeopardy.money(self.score)}    "
                 f"Questions left: {left}")

    # ---------------- start screen ----------------
    def build_start_screen(self):
        f = self.start_frame
        tk.Label(f, text="Pick a game", font=TITLE_FONT,
                 bg=WINDOW_BG, fg=WHITE).pack(pady=30)
        row = tk.Frame(f, bg=WINDOW_BG)
        row.pack()
        for key, (name, _bank, _kind) in GAMES.items():
            TVScreen(row, text=name, font=("Arial", 16, "bold"), fg=WHITE,
                     screen_bg=SQUARE_BG, width=190, height=190,
                     line_color="#17661c",
                     command=lambda k=key: self.start_game(k)
                     ).pack(side="left", padx=14)
        tk.Label(f, text="Forest green board, gold dollars -- same\n"
                         "questions as the terminal version.",
                 font=QUESTION_FONT, bg=WINDOW_BG, fg=USED_FG).pack(pady=24)

    # ---------------- game screen ----------------
    def start_game(self, key):
        self.game_name, bank, self.kind = GAMES[key]
        self.board = jeopardy.build_board(bank, self.rng)
        self.score = 0
        self.asked = 0
        self.correct_count = 0
        self.missed = []
        self.current = None

        # Rebuild the game frame from scratch for the new game.
        for child in self.game_frame.winfo_children():
            child.destroy()
        f = self.game_frame

        # The board sits in a big casing frame, like one wall of TVs.
        casing = tk.Frame(f, bg=BEZEL_BG, bd=5, relief="ridge")
        casing.pack()
        board_frame = tk.Frame(casing, bg="#07130c")
        board_frame.pack(padx=6, pady=6)
        self.square_tiles = {}
        cats = list(self.board)
        for c, cat in enumerate(cats):
            TVScreen(board_frame, text=cat, font=CAT_FONT, fg=WHITE,
                     screen_bg=HEADER_BG, line_color="#0a3319"
                     ).grid(row=0, column=c, padx=TILE_GAP // 2,
                            pady=TILE_GAP // 2)
            for r, value in enumerate(VALUES, start=1):
                tile = TVScreen(
                    board_frame, text=jeopardy.money(value),
                    font=VALUE_FONT, fg=GOLD, screen_bg=SQUARE_BG,
                    line_color="#17661c",
                    command=lambda cat=cat, value=value:
                        self.open_square(cat, value))
                tile.grid(row=r, column=c, padx=TILE_GAP // 2,
                          pady=TILE_GAP // 2)
                self.square_tiles[(cat, value)] = tile

        # Question area under the board -- same window, board stays up.
        self.question_frame = tk.Frame(f, bg=WINDOW_BG)
        self.question_frame.pack(fill="x", pady=14)
        self.hint_label = tk.Label(
            self.question_frame,
            text="Click a dollar square to get a question.",
            font=QUESTION_FONT, bg=WINDOW_BG, fg=USED_FG)
        self.hint_label.pack()

        tk.Button(f, text="End game", font=BUTTON_FONT, bg=USED_BG,
                  fg=WHITE, command=self.finish_game).pack(pady=4)
        self.update_scoreboard()
        self.show(f)

    def set_board_enabled(self, enabled):
        for (cat, value), tile in self.square_tiles.items():
            if self.board[cat][value] is not None:
                tile.set_enabled(enabled)

    def clear_question_area(self):
        for child in self.question_frame.winfo_children():
            child.destroy()

    def open_square(self, cat, value):
        item = self.board[cat][value]
        if item is None or self.current is not None:
            return
        self.current = (cat, value, item)
        self.set_board_enabled(False)
        self.square_tiles[(cat, value)].set_active()
        self.clear_question_area()
        f = self.question_frame
        tk.Label(f, text=f"{cat} for {jeopardy.money(value)}",
                 font=SCORE_FONT, bg=WINDOW_BG, fg=GOLD).pack(pady=4)
        if self.kind == "linux":
            question, _answer = item
            tk.Label(f, text=question, font=QUESTION_FONT, bg=WINDOW_BG,
                     fg=WHITE, wraplength=950, justify="center").pack(pady=4)
            tk.Label(f, text="(type the command)", font=QUESTION_FONT,
                     bg=WINDOW_BG, fg=USED_FG).pack()
            row = tk.Frame(f, bg=WINDOW_BG)
            row.pack(pady=8)
            self.answer_entry = tk.Entry(row, font=QUESTION_FONT, width=24,
                                         bg=HEADER_BG, fg=WHITE,
                                         insertbackground=WHITE, relief="sunken",
                                         bd=3)
            self.answer_entry.pack(side="left", padx=6)
            self.answer_entry.focus_set()
            self.answer_entry.bind("<Return>", lambda _e: self.submit())
            TVScreen(row, text="Submit", font=BUTTON_FONT, fg=WHITE,
                     screen_bg=SQUARE_BG, width=120, height=44,
                     line_color="#17661c",
                     command=self.submit).pack(side="left")
        else:
            tk.Label(f, text=item["q"], font=QUESTION_FONT, bg=WINDOW_BG,
                     fg=WHITE, wraplength=950, justify="left").pack(pady=4)
            options = list(item["options"])
            self.rng.shuffle(options)
            self.current_options = options
            self.option_tiles = []
            for text in options:
                tile = TVScreen(f, text=text, font=QUESTION_FONT, fg=WHITE,
                                screen_bg=HEADER_BG, width=940, height=48,
                                wraplength=890, line_color="#0a3319",
                                text_anchor="w",
                                command=lambda t=text: self.submit(t))
                tile.pack(pady=3)
                self.option_tiles.append(tile)
        self.feedback_label = tk.Label(f, text="", font=SCORE_FONT,
                                       bg=WINDOW_BG, fg=WHITE,
                                       wraplength=950, justify="center")
        self.feedback_label.pack(pady=8)

    def submit(self, picked_text=None):
        cat, value, item = self.current
        if self.kind == "linux":
            question, answer = item
            guess = self.answer_entry.get().strip()
            if guess.lower() == "q":
                self.finish_game()
                return
            ok = " ".join(guess.lower().split()) == answer.lower()
            right_text = answer
            label = question
        else:
            correct_text = item["options"][item["answer"] - 1]
            ok = picked_text == correct_text
            right_text = correct_text
            label = item["q"].splitlines()[0]

        self.asked += 1
        if ok:
            self.score += value
            self.correct_count += 1
            msg = f"Correct! +{jeopardy.money(value)}"
            color = GOOD
        else:
            self.score -= value
            self.missed.append(
                f"{jeopardy.money(value)} -- {label} -> {right_text}")
            msg = f"Not quite -- the answer is: {right_text}"
            color = BAD
        if self.kind == "ai901":
            msg += "\nWhy: " + item["why"]
        self.feedback_label.config(text=msg, fg=color)

        # The square is spent either way.
        self.board[cat][value] = None
        self.square_tiles[(cat, value)].set_used()
        self.current = None
        self.update_scoreboard()

        # Swap the answer controls for a Continue screen.
        for child in self.question_frame.winfo_children():
            if isinstance(child, (tk.Entry, tk.Button, tk.Canvas, tk.Frame)):
                child.destroy()
        TVScreen(self.question_frame, text="Continue", font=BUTTON_FONT,
                 fg=WHITE, screen_bg=SQUARE_BG, width=170, height=48,
                 line_color="#17661c",
                 command=self.after_answer).pack(pady=4)
        self.update_scoreboard()

    def after_answer(self):
        left = sum(1 for cat in self.board
                   for v in VALUES if self.board[cat][v] is not None)
        if left == 0:
            self.finish_game()
            return
        self.clear_question_area()
        self.hint_label = tk.Label(
            self.question_frame,
            text="Click a dollar square to get a question.",
            font=QUESTION_FONT, bg=WINDOW_BG, fg=USED_FG)
        self.hint_label.pack()
        self.set_board_enabled(True)

    # ---------------- results screen ----------------
    def finish_game(self):
        self.current = None
        if self.asked == 0:
            self.show(self.start_frame)
            self.score_label.config(text="")
            return
        f = self.results_frame
        for child in f.winfo_children():
            child.destroy()
        pct = self.correct_count * 100 // self.asked
        tk.Label(f, text=f"Final score: {jeopardy.money(self.score)}",
                 font=TITLE_FONT, bg=WINDOW_BG, fg=GOLD).pack(pady=8)
        tk.Label(f, text=f"Correct: {self.correct_count} / {self.asked}"
                         f"  ({pct}%)",
                 font=SCORE_FONT, bg=WINDOW_BG, fg=WHITE).pack(pady=4)
        if pct == 100:
            note = "Perfect game! Board cleared, nothing missed."
        elif pct >= 70:
            note = "Solid! A little review and you'll hit 100%."
        else:
            note = "Good start -- review the ones you missed below."
        if self.score < 0:
            note += f"\nOuch -- you owe the bank " \
                    f"{jeopardy.money(-self.score)}. Run it back!"
        tk.Label(f, text=note, font=QUESTION_FONT, bg=WINDOW_BG,
                 fg=WHITE).pack(pady=4)

        if self.missed:
            tk.Label(f, text="Review these:", font=SCORE_FONT,
                     bg=WINDOW_BG, fg=WHITE).pack(pady=(10, 2))
            casing = tk.Frame(f, bg=BEZEL_BG, bd=5, relief="ridge")
            casing.pack(pady=2)
            box = tk.Text(casing, height=7, width=95, font=("Consolas", 10),
                          bg=HEADER_BG, fg=WHITE, wrap="word",
                          relief="flat", bd=0)
            box.pack(padx=6, pady=6)
            for line in self.missed:
                box.insert("end", line + "\n")
            box.config(state="disabled")

        self.score_area = tk.Frame(f, bg=WINDOW_BG)
        self.score_area.pack(pady=12)
        table = jeopardy.load_scores().get(self.game_name, [])
        if len(table) < 5 or self.score > table[-1]["score"]:
            tk.Label(self.score_area, text="New high score! Your name:",
                     font=QUESTION_FONT, bg=WINDOW_BG, fg=WHITE).pack()
            row = tk.Frame(self.score_area, bg=WINDOW_BG)
            row.pack(pady=4)
            self.name_entry = tk.Entry(row, font=QUESTION_FONT, width=20)
            self.name_entry.pack(side="left", padx=6)
            tk.Button(row, text="Save score", font=BUTTON_FONT,
                      bg=SQUARE_BG, fg=WHITE,
                      command=self.save_my_score).pack(side="left")
        else:
            self.show_score_table(self.score_area)

        tk.Button(f, text="Back to games", font=BUTTON_FONT, bg=USED_BG,
                  fg=WHITE,
                  command=lambda: self.show(self.start_frame)).pack(pady=8)
        self.show(f)

    def save_my_score(self):
        name = self.name_entry.get().strip() or "Player"
        jeopardy.save_score(self.game_name, name, self.score,
                            self.correct_count, self.asked)
        for child in self.score_area.winfo_children():
            child.destroy()
        self.show_score_table(self.score_area)

    def show_score_table(self, parent):
        table = jeopardy.load_scores().get(self.game_name, [])
        if not table:
            return
        tk.Label(parent, text=f"Top scores -- {self.game_name}:",
                 font=SCORE_FONT, bg=WINDOW_BG, fg=GOLD).pack(pady=4)
        for i, e in enumerate(table, start=1):
            tk.Label(parent,
                     text=f"{i}. {e['name']:<12} "
                          f"{jeopardy.money(e['score']):>8}   "
                          f"({e['correct']}/{e['asked']} correct, "
                          f"{e['date']})",
                     font=("Consolas", 11), bg=WINDOW_BG,
                     fg=WHITE).pack()


def main():
    seed_text = os.environ.get("QUIZ_SEED")
    for a in sys.argv[1:]:
        if a.startswith("--seed="):
            seed_text = a.split("=", 1)[1]
    seed = None
    if seed_text:
        try:
            seed = int(seed_text)
        except ValueError:
            seed = seed_text
    app = JeopardyApp(random.Random(seed))
    app.mainloop()


if __name__ == "__main__":
    main()
