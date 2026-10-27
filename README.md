# Jeopardy Study Game (Python)

A Jeopardy-style study game built for ITSA classmates, with two ways to play:

- **Terminal version** — `jeopardy.py`
- **GUI version** — `jeopardy_gui.py` (clickable board, forest-green CRT TV style)

Both versions play the same two games:

1. **Linux Commands** — type the command name
2. **AI-901** — multiple choice (A/B/C/D), like the real exam

Each game is a real Jeopardy board: 5 categories across the top, squares worth
$200, $400, $600, $800, and $1,000. A right answer wins the amount, a wrong
answer loses it. At the end you get your final score, the number correct, and
a review list of everything you missed.

## High scores

The top 5 scores for each game save automatically to
`jeopardy_high_scores.json` in the same folder. Delete that file to reset
the score tables.

## How to run

You only need Python 3 — no extra installs.

```text
py jeopardy.py        # terminal version (Windows)
py jeopardy_gui.py    # GUI version (Windows)
python3 jeopardy.py   # Mac or Linux
