jeopardy.py — Jeopardy study game in Python
=============================================

Two games in one file:
  1) Linux Commands — type the command name
  2) AI-901         — multiple choice (A/B/C/D), like the real exam

Each game has a real Jeopardy board: 5 categories across the top
and squares worth $200, $400, $600, $800, and $1,000. Pick a
category and an amount. A right answer wins that amount, a wrong
answer loses it. Clear all 25 squares, or type q at any prompt to
stop early.

At the end you get your final score, the number correct, and a
review list of everything you missed. AI-901 questions also show
a one-line explanation after each answer.

The AI-901 questions are original practice questions written from
Microsoft's published AI-901 skills outline — not real exam
questions.

HIGH SCORES
-----------
The top 5 scores for each game are saved automatically in a file
named jeopardy_high_scores.json in the same folder as jeopardy.py.
Delete that file if you want to start the score tables over.

HOW TO RUN
----------
You only need Python 3. No extra installs, no WSL, and no chmod.
This works on Windows, Mac, and Linux.

1. Put jeopardy.py in a folder on your machine.
2. Open a terminal in that folder.
3. Start the game:

   Windows:
       py jeopardy.py
       (If that does not work, try: python jeopardy.py)

   Mac or Linux:
       python3 jeopardy.py

Jump straight to one game:
       py jeopardy.py linux
       py jeopardy.py ai901

SAME BOARD FOR THE WHOLE CLASS
------------------------------
Use the same seed and everyone gets the same board layout. On
Windows, the option order in AI-901 is also the same:

       py jeopardy.py --seed=7

You can also use QUIZ_SEED=7 in the same ways as the older bash
versions if your terminal supports environment variables.

ADD YOUR OWN QUESTIONS
----------------------
The question banks are near the top of jeopardy.py, grouped by
board category. Add questions in exactly the same shape:

Linux questions are pairs:
       ('Question text', 'answer'),

AI-901 questions are dictionaries with q, options, answer, and
why fields. The answer number is 1-4, counting the options as
written; the game shuffles them before asking.

Important: every board category needs at least 5 questions,
because the game places 5 questions from each category on the
board.
