jeopardy_gui.py — the Jeopardy study game with graphics
=========================================================

Same games, same questions, and same scoring as jeopardy.py —
this version opens a window with a clickable board. Forest green
squares (our own color), white category names, gold dollar
amounts, and everything happens in one window: the board, the
question, the results, and the high scores.

The terminal version (jeopardy.py) still works exactly as
before. This is just the graphics version alongside it.

IMPORTANT — TWO FILES, SAME FOLDER
----------------------------------
jeopardy_gui.py needs jeopardy.py in the SAME folder. All the
questions live in jeopardy.py; the gui file imports them. Keep
the two files together and it just works.

HOW TO RUN
----------
You only need Python 3 (Tkinter comes with it on Windows).
No extra installs.

1. Put jeopardy_gui.py and jeopardy.py in the same folder.
2. Open a terminal in that folder.
3. Start the game:

   Windows:
       py jeopardy_gui.py

   Mac or Linux:
       python3 jeopardy_gui.py
   (On Linux you may also need: sudo apt install python3-tk)

HOW TO PLAY
-----------
Click Linux Commands or AI-901, then click a dollar square.
Linux questions: type the command and click Submit (or press
Enter). AI-901 questions: click one of the four answers.
Right answer adds the amount, wrong answer subtracts it, and
the square greys out. "End game" finishes early whenever you
want. At the end you get your score, the review list of what
you missed, and a spot on the high-score table.

High scores are shared with the terminal version — both games
save to jeopardy_high_scores.json in the same folder.

SAME BOARD FOR THE WHOLE CLASS
------------------------------
       py jeopardy_gui.py --seed=7
