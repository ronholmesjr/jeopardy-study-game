#!/usr/bin/env python3
"""
jeopardy.py -- Jeopardy-style study quiz, in Python!

Two games in one file:
  1) Linux Commands -- type the command (from the Linux unit)
  2) AI-901         -- multiple choice, like the real exam

How to play:
  Pick a category and a dollar amount off the board. A right answer
  wins the amount, a wrong answer loses it. Clear the board, or type
  'q' at any prompt to stop early. Missed questions are listed at the
  end for review, and the top 5 scores per game are saved in
  jeopardy_high_scores.json next to this file.

Run it:
  python jeopardy.py              menu
  python jeopardy.py linux        jump straight to the Linux game
  python jeopardy.py ai901        jump straight to the AI-901 game
  QUIZ_SEED=7 python jeopardy.py  same board every run (whole class)
  python jeopardy.py --seed=7     same thing

Needs Python 3 only -- no extra installs, no WSL, works on Windows,
Mac, and Linux as-is.

The questions are original practice questions written for the ITSA
class. The AI-901 set follows Microsoft's published AI-901 skills
outline; they are NOT copies of real exam questions.
"""

import json
import os
import random
import sys
from datetime import date
from pathlib import Path

# ------------------------------------------------------------------
# Question banks. Add your own questions in the same shape!
# Linux: (question, answer) pairs, grouped by board category.
# AI-901: dicts with q / options / answer (1-4, as written) / why.
# ------------------------------------------------------------------

LINUX_BANK = {'Admin & Help': [('Run a command as the superuser (admin)', 'sudo'),
                  ('Change file permissions', 'chmod'),
                  ('Change the owner of a file', 'chown'),
                  ('Install, update, or remove software packages (Mint/Ubuntu)', 'apt'),
                  ('Show your current username', 'whoami'),
                  ('Show where a command lives on the system', 'which'),
                  ('Show the manual page for a command', 'man')],
 'Files & Folders': [('List the contents of a directory', 'ls'),
                     ('Change the working directory', 'cd'),
                     ('Print the current working directory', 'pwd'),
                     ('Copy files and directories', 'cp'),
                     ('Move or rename files and directories', 'mv'),
                     ('Delete files', 'rm'),
                     ('Create a directory', 'mkdir'),
                     ('Remove an empty directory', 'rmdir'),
                     ("Create an empty file (or update a file's timestamp)", 'touch'),
                     ('List files in a tree diagram', 'tree'),
                     ('Create a link to a file', 'ln'),
                     ('Find files in a directory tree', 'find')],
 'Network & Archives': [('Test network connectivity to another host', 'ping'),
                        ('Download a file from the web', 'wget'),
                        ('Transfer data to or from a server', 'curl'),
                        ('Connect to another computer securely over the network', 'ssh'),
                        ('Create or extract archive files (.tar.gz)', 'tar')],
 'System & Terminal': [('Show free disk space on filesystems', 'df'),
                       ('Show disk usage of files and directories', 'du'),
                       ('Show free and used memory', 'free'),
                       ('Show a live, updating list of running processes', 'top'),
                       ('Show a snapshot of currently running processes', 'ps'),
                       ('Stop a process by sending it a signal', 'kill'),
                       ('Show system information (kernel, machine type)', 'uname'),
                       ('Show the current date and time', 'date'),
                       ('Show previously typed commands', 'history'),
                       ('Clear the terminal screen', 'clear'),
                       ('Close the terminal session / log out', 'exit')],
 'Text & Viewing': [('Display the contents of a file', 'cat'),
                    ('View a file one screen at a time, with scrolling', 'less'),
                    ('Show the first lines of a file', 'head'),
                    ('Show the last lines of a file', 'tail'),
                    ('Print text to the screen', 'echo'),
                    ('Search text for a matching pattern', 'grep'),
                    ('Edit a file in a simple terminal text editor', 'nano')]}

AI901_BANK = {'Foundry Portal': [{'answer': 2,
                     'options': ['Write a Python client',
                                 "Use the model's chat playground in the portal",
                                 'Call the REST API from the command line',
                                 'Create an agent first'],
                     'q': 'You just deployed a model in the Microsoft Foundry portal. What is the '
                          'quickest way to try it out before writing any code?',
                     'why': 'The portal playground lets you chat with a deployed model right away, '
                            'no code needed.'},
                    {'answer': 2,
                     'options': ['Store the chat history',
                                 "Set the model's behavior and rules for the conversation",
                                 'Deploy the model',
                                 'Hold the API key'],
                     'q': 'What is the job of a system prompt?',
                     'why': "The system prompt sets the assistant's role, tone, and rules for the "
                            'whole conversation.'},
                    {'answer': 2,
                     'options': ['Write something about orders',
                                 'You are a support agent. Answer using the order status provided, '
                                 'in one short paragraph.',
                                 'Answer the question',
                                 'Be an AI and help'],
                     'q': 'Which prompt is most likely to get a useful answer from a support bot?',
                     'why': 'Effective prompts give the model a role, the material to use, and a '
                            'clear output shape.'},
                    {'answer': 2,
                     'options': ['A second copy of a model for backup',
                                 'A model configured with instructions and tools to handle a task',
                                 'A load balancer for model traffic',
                                 'A type of model deployment'],
                     'q': 'Which best describes a single-agent solution in Microsoft Foundry?',
                     'why': 'An agent combines a model with instructions and tools so it can carry '
                            'out a task.'},
                    {'answer': 1,
                     'options': ['The address of your Foundry project or resource',
                                 'The model to run',
                                 "The signed-in user's location",
                                 'The billing account'],
                     'q': 'In a Foundry SDK client, what does the endpoint identify?',
                     'why': 'The endpoint is where your Foundry resource lives; the deployment '
                            'name says which model to run there.'}],
 'Foundry in Code': [{'answer': 2,
                      'options': ['The public name of the base model',
                                  'Your model deployment name in Foundry',
                                  'Your Azure subscription ID',
                                  'The region the model runs in'],
                      'q': 'In this Python code, what does the model value refer to?\n'
                           '\n'
                           'response = client.chat.completions.create(\n'
                           "    model='sales-gpt',\n"
                           "    messages=[{'role': 'user', 'content': 'Hello'}]\n"
                           ')',
                      'why': 'Chat clients pass your deployment name as the model value, not the '
                             'base model name.'},
                     {'answer': 3,
                      'options': ['The user message',
                                  'The temperature setting',
                                  'The system message',
                                  'The deployment name'],
                      'q': "Which part of this request sets the assistant's overall behavior?\n"
                           'messages=[\n'
                           "  {'role': 'system', 'content': 'You are a support assistant.'},\n"
                           "  {'role': 'user', 'content': 'Reset my password'}\n"
                           ']',
                      'why': 'The system message carries the standing instructions; the user '
                             'message is just the current request.'},
                     {'answer': 2,
                      'options': ['The endpoint',
                                  'The messages array of roles and content',
                                  'The API key',
                                  'The model name'],
                      'q': 'When your app calls a chat model, what carries the conversation so '
                           'far?',
                      'why': 'Each request sends the conversation as an array of messages, each '
                             'with a role and content.'},
                     {'answer': 1,
                      'options': ['Endpoint and deployment name',
                                  'Username and password',
                                  'Resource group and region',
                                  'Subscription ID and invoice number'],
                      'q': 'Which pair must a client app supply to call a deployed model?',
                      'why': 'The client needs the endpoint (where) and the deployment name (which '
                             'model), plus a credential to sign in.'},
                     {'answer': 3,
                      'options': ['Azure Speech',
                                  'Azure AI Search',
                                  'Content Understanding',
                                  'Translator'],
                      'q': 'You need structured fields such as totals, dates, and vendor names '
                           'pulled from thousands of invoices. Which Foundry tool is built for '
                           'that?',
                      'why': 'Content Understanding extracts structured information from documents '
                             'and forms.'}],
 'Language & Text': [{'answer': 3,
                      'options': ['It looks up answers stored in a database',
                                  'It translates the prompt word by word',
                                  'It predicts the most likely next token, one token at a time',
                                  'It follows a fixed script written by developers'],
                      'q': 'How does a large language model produce its response?',
                      'why': 'Generative AI models build responses by predicting the next token '
                             'from patterns learned in training.'},
                     {'answer': 2,
                      'options': ['Max tokens', 'Temperature', 'Deployment name', 'API version'],
                      'q': 'Which model setting controls how random or creative the responses are?',
                      'why': 'Higher temperature means more varied, creative output; lower means '
                             'more focused and predictable.'},
                     {'answer': 2,
                      'options': ['Temperature', 'Max tokens', 'System prompt', 'Region'],
                      'q': "Which setting limits how long the model's response can be?",
                      'why': 'Max tokens caps the length of the generated response.'},
                     {'answer': 3,
                      'options': ['Computer vision',
                                  'Speech synthesis',
                                  'Text analysis',
                                  'Image generation'],
                      'q': 'You need key phrases, named entities, and sentiment from thousands of '
                           'product reviews. Which AI workload is this?',
                      'why': 'Finding key phrases, entities, and sentiment in written text is text '
                             'analysis (NLP).'},
                     {'answer': 4,
                      'options': ['Sentiment analysis',
                                  'Keyword extraction',
                                  'Summarization',
                                  'Entity recognition'],
                      'q': 'Which text analysis technique finds people, places, and organizations '
                           'mentioned in a document?',
                      'why': 'Entity recognition detects named entities such as people, places, '
                             'and organizations.'}],
 'Responsible AI': [{'answer': 2,
                     'options': ['Reliability and safety',
                                 'Fairness',
                                 'Transparency',
                                 'Inclusiveness'],
                     'q': 'A hiring tool consistently rates equally qualified candidates from one '
                          'group lower than another group. Which responsible AI principle is being '
                          'violated?',
                     'why': 'Fairness means the system treats all people equitably and avoids bias '
                            'in its outcomes.'},
                    {'answer': 3,
                     'options': ['Privacy and security',
                                 'Accountability',
                                 'Reliability and safety',
                                 'Transparency'],
                     'q': 'A team stress-tests its AI system with unexpected and malformed inputs '
                          'to make sure it keeps working safely. Which responsible AI principle '
                          'are they checking?',
                     'why': 'Reliability and safety means the system performs reliably and safely, '
                            'even with unexpected inputs.'},
                    {'answer': 1,
                     'options': ['Transparency',
                                 'Fairness',
                                 'Inclusiveness',
                                 'Privacy and security'],
                     'q': 'Users want to understand how an AI system reached its decision. Which '
                          'responsible AI principle covers making the system understandable?',
                     'why': 'Transparency means users can understand how the system works and how '
                            'it makes decisions.'},
                    {'answer': 4,
                     'options': ['Reliability and safety',
                                 'Transparency',
                                 'Privacy and security',
                                 'Inclusiveness'],
                     'q': 'An app adds voice control and screen-reader support so people of all '
                          'abilities can use its AI features. Which responsible AI principle is '
                          'this?',
                     'why': 'Inclusiveness means AI systems should empower and work for people of '
                            'all abilities.'},
                    {'answer': 1,
                     'options': ['Privacy and security',
                                 'Fairness',
                                 'Accountability',
                                 'Transparency'],
                     'q': 'Customer data used by an AI app must be protected from unauthorized '
                          'access. Which responsible AI principle covers this?',
                     'why': 'Privacy and security means personal data used by the system stays '
                            'protected.'}],
 'Vision & Speech': [{'answer': 2,
                      'options': ['Image classification',
                                  'Object detection',
                                  'OCR',
                                  'Image generation'],
                      'q': 'A warehouse app must locate every box in a photo and mark where each '
                           'one is. Which vision capability does it need?',
                      'why': 'Object detection finds individual objects in an image and marks '
                             'their locations.'},
                     {'answer': 2,
                      'options': ['OCR and image generation',
                                  'Speech-to-text and text-to-speech',
                                  'Translation and summarization',
                                  'Search and indexing'],
                      'q': 'Your app must listen to spoken questions and answer out loud. Which '
                           'pairing does it need?',
                      'why': 'Azure Speech in Foundry Tools covers both directions: recognizing '
                             'speech and synthesizing it.'},
                     {'answer': 1,
                      'options': ['A multimodal model that accepts text and images',
                                  'A text-only model',
                                  'OCR alone',
                                  'A translation model'],
                      'q': "A user sends a photo and asks, 'What is wrong with this machine?' "
                           'Which capability handles that in a prompt?',
                      'why': 'Multimodal models can interpret visual input included in a prompt '
                             'alongside text.'},
                     {'answer': 4,
                      'options': ['Image classification',
                                  'Object detection',
                                  'OCR',
                                  'An image-generation model'],
                      'q': 'Marketing wants product images created from text descriptions. Which '
                           'capability do they need?',
                      'why': 'Image-generation models create new visual outputs from a text '
                             'prompt.'},
                     {'answer': 3,
                      'options': ['Documents only',
                                  'Spreadsheets only',
                                  'Documents, images, audio, and video',
                                  'Source code only'],
                      'q': 'Which inputs can Content Understanding extract information from?',
                      'why': 'Content Understanding is multimodal: it extracts information from '
                             'documents, images, audio, and video.'}]}

# ------------------------------------------------------------------
# Game code
# ------------------------------------------------------------------
VALUES = [200, 400, 600, 800, 1000]
LETTERS = ["A", "B", "C", "D"]
SCORE_FILE = Path(__file__).with_name("jeopardy_high_scores.json")


def money(amount):
    """Format a score the Jeopardy way: 1000 -> '$1,000', -400 -> '-$400'."""
    if amount < 0:
        return "-$" + format(-amount, ",")
    return "$" + format(amount, ",")


def ask(prompt):
    """Read one line of input. Ctrl+C / Ctrl+D count as 'q' (quit)."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "q"


def build_board(bank, rng):
    """Pick 5 questions per category and lay them on the board.

    Returns {category: {value: question}} -- one question per dollar
    value, cheapest at $200 up to $1,000.
    """
    board = {}
    for category, pool in bank.items():
        questions = list(pool)
        rng.shuffle(questions)
        board[category] = dict(zip(VALUES, questions[:5]))
    return board


def show_board(board, score, left):
    """Print the board. Used-up squares show as ---."""
    width = 18
    cats = list(board)
    print()
    print("=" * (width * len(cats) + 3 * (len(cats) - 1)))
    print("  Score: " + money(score) + "    Questions left: " + str(left))
    print("=" * (width * len(cats) + 3 * (len(cats) - 1)))
    print(" | ".join(cat.center(width)[:width] for cat in cats))
    print("-|-".join("-" * width for _ in cats))
    for value in VALUES:
        row = []
        for cat in cats:
            cell = money(value) if board[cat][value] is not None else "---"
            row.append(cell.center(width))
        print(" | ".join(row))
    print()


def pick_square(board):
    """Ask the player for a category, then a dollar value.

    Returns (category, value), or None if they quit.
    """
    cats = list(board)
    while True:
        print("Categories:")
        for i, cat in enumerate(cats, start=1):
            open_values = [v for v in VALUES if board[cat][v] is not None]
            if open_values:
                amounts = ", ".join(money(v) for v in open_values)
                print(f"  {i}) {cat}  ({amounts})")
        choice = ask("Pick a category number (or 'q' to quit): ")
        if choice.lower() == "q":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(cats):
            cat = cats[int(choice) - 1]
            if any(board[cat][v] is not None for v in VALUES):
                break
        print("  That category has no questions left -- pick another.")
    while True:
        open_values = [v for v in VALUES if board[cat][v] is not None]
        amounts = " / ".join(str(v) for v in open_values)
        choice = ask(f"{cat} -- pick an amount ({amounts}, or 'q'): ")
        if choice.lower() == "q":
            return None
        choice = choice.replace("$", "").replace(",", "")
        if choice.isdigit() and int(choice) in open_values:
            return cat, int(choice)
        print("  Pick one of the amounts still on the board.")


def play_linux(question, answer):
    """One typed-answer Linux question. Returns True if correct."""
    print("  " + question)
    print("  (type the command)")
    guess = ask("  Your answer: ")
    if guess.lower() == "q":
        return None
    ok = " ".join(guess.lower().split()) == answer.lower()
    if not ok:
        print(f"  Not quite -- the command is: {answer}")
    return ok


def play_ai901(item, rng):
    """One multiple-choice AI-901 question. Returns True if correct."""
    for line in item["q"].splitlines():
        print("  " + line)
    options = list(item["options"])
    correct_text = options[item["answer"] - 1]
    rng.shuffle(options)
    for i, text in enumerate(options):
        print(f"    {LETTERS[i]}) {text}")
    while True:
        pick = ask("  Your answer (A, B, C, or D): ").lower()
        if pick == "q":
            return None
        if pick in ("a", "b", "c", "d"):
            break
        print("  Pick a letter: A, B, C, or D (or 'q' to quit).")
    ok = options[LETTERS.index(pick.upper())] == correct_text
    if not ok:
        letter = LETTERS[options.index(correct_text)]
        print(f"  Not quite -- the answer is {letter}) {correct_text}")
    print("  Why: " + item["why"])
    return ok


def load_scores():
    """Read the high-score file. Any problem -> empty scores."""
    try:
        return json.loads(SCORE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_score(game, name, score, correct, asked):
    """Add a score to the file, keeping the top 5 per game."""
    scores = load_scores()
    entry = {"name": name, "score": score, "correct": correct,
             "asked": asked, "date": date.today().isoformat()}
    table = scores.get(game, []) + [entry]
    table.sort(key=lambda e: e["score"], reverse=True)
    scores[game] = table[:5]
    try:
        SCORE_FILE.write_text(json.dumps(scores, indent=2), encoding="utf-8")
    except Exception:
        print("  (Couldn't save the high score -- folder may be read-only.)")
    return scores[game]


def show_scores(game, table):
    if not table:
        return
    print(f"  Top scores -- {game}:")
    for i, e in enumerate(table, start=1):
        print(f"    {i}. {e['name']:<12} {money(e['score']):>8}   "
              f"({e['correct']}/{e['asked']} correct, {e['date']})")


def play_game(game, bank, kind, rng):
    """Play one full board of Jeopardy. kind is 'linux' or 'ai901'."""
    board = build_board(bank, rng)
    total = sum(len(v) for v in board.values())
    score = 0
    asked = 0
    correct = 0
    missed = []
    print()
    print(f"*** {game} Jeopardy ***")
    print("Pick a category and an amount. Right answer wins the amount,")
    print("wrong answer loses it. Clear the board or quit with 'q'.")

    while asked < total:
        show_board(board, score, total - asked)
        picked = pick_square(board)
        if picked is None:
            break
        cat, value = picked
        item = board[cat][value]
        board[cat][value] = None
        print()
        print(f"--- {cat} for {money(value)} ---")
        if kind == "linux":
            result = play_linux(item[0], item[1])
            right_answer = item[1]
            label = item[0]
        else:
            result = play_ai901(item, rng)
            right_answer = item["options"][item["answer"] - 1]
            label = item["q"].splitlines()[0]
        if result is None:          # player typed q at the question
            break
        asked += 1
        if result:
            score += value
            correct += 1
            print(f"  Correct! +{money(value)}")
        else:
            score -= value
            missed.append(f"{money(value)} -- {label} -> {right_answer}")
        print(f"  Current score: {money(score)}")

    print()
    print("=" * 60)
    if asked == 0:
        print("No questions answered. Run it again when you're ready!")
        return
    pct = correct * 100 // asked
    print(f"Final score: {money(score)}")
    print(f"Correct: {correct} / {asked}  ({pct}%)")
    if pct == 100:
        print("Perfect game! Board cleared, nothing missed.")
    elif pct >= 70:
        print("Solid! A little review and you'll hit 100%.")
    else:
        print("Good start -- review the ones you missed below.")
    if score < 0:
        print(f"Ouch -- you owe the bank {money(-score)}. Run it back!")
    if missed:
        print()
        print("Review these:")
        for line in missed:
            print("  " + line)

    table = load_scores().get(game, [])
    if len(table) < 5 or score > table[-1]["score"]:
        name = ask("New high score! Your name (or Enter for 'Player'): ")
        if not name or name.lower() == "q":
            name = "Player"
        table = save_score(game, name, score, correct, asked)
    print()
    show_scores(game, table)


def main():
    seed_text = os.environ.get("QUIZ_SEED")
    args = [a for a in sys.argv[1:] if not a.startswith("--seed")]
    for a in sys.argv[1:]:
        if a.startswith("--seed="):
            seed_text = a.split("=", 1)[1]
    seed = None
    if seed_text:
        try:
            seed = int(seed_text)
        except ValueError:
            seed = seed_text
    rng = random.Random(seed)

    games = {
        "linux": ("Linux Commands", LINUX_BANK, "linux"),
        "ai901": ("AI-901", AI901_BANK, "ai901"),
    }
    if args and args[0].lower() in games:
        name, bank, kind = games[args[0].lower()]
        play_game(name, bank, kind, rng)
        return

    while True:
        print()
        print("=" * 60)
        print("  JEOPARDY -- study edition")
        print("=" * 60)
        print("  1) Linux Commands")
        print("  2) AI-901")
        choice = ask("Pick a game (1 or 2, or 'q' to quit): ").lower()
        if choice in ("q", ""):
            print("See you next round!")
            return
        if choice in ("1", "2"):
            key = "linux" if choice == "1" else "ai901"
            name, bank, kind = games[key]
            play_game(name, bank, kind, rng)
        else:
            print("  Pick 1 or 2.")


if __name__ == "__main__":
    main()
