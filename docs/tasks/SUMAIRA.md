# Sumaira: the "Brain" (context-aware sentence engine)

**Analogy:** a human interpreter does not say "ME WANT WATER". They say "I want water." You build the part
that does this. It receives one sign at a time (with a confidence score) and keeps a live sentence.

Read `docs/TEAM_BRIEF.md` first (contracts, Git, rules for using an AI assistant).

## Your files
| You own | Do not touch |
|---|---|
| `context/sentence_builder.py` (your main file) | `context/tests/test_acceptance.py` (it is the exam) |
| `docs/context_notes.md` (you create it) | `common/`, `vision/`, `app/` |

## What you receive and what you must send
**In:** one prediction at a time (Contract 1), for example `{"sign": "want", "confidence": 0.88, "top3": [...], "timestamp": 3.2}`
**Out:** a Contract 2 dictionary after every sign: `{"sentence": "...", "suggestions": [...], "raw_signs": [...]}`

## The class you must provide (names must match exactly)
```python
b = SentenceBuilder(min_conf=0.6, rescue_conf=0.35, pause_seconds=3.0)
b.add(prediction)   # -> Contract 2 dict
b.undo()            # removes the last word -> Contract 2 dict
b.clear()           # empties the current words, keeps history -> Contract 2 dict
b.finish()          # completes the sentence: returns it as a string, saves it in b.history, empties the words
b.output()          # current Contract 2 dict, without adding anything
b.words             # list of accepted labels so far
b.history           # list of finished sentences
```

## Rules the engine must follow (the tests check all of these)

1. **Accept or ignore each prediction**
   - `confidence >= min_conf` -> accept.
   - Between `rescue_conf` and `min_conf` -> accept **only if that sign is one of the current suggestions** (this is the context-aware part: a weak guess is believed when it fits what usually comes next).
   - Below `rescue_conf` -> ignore.
   - The same sign twice in a row -> ignore the second one.
2. **Grammar** (labels: hello, bye, please, thankyou, sorry, yes, no, me, you, want, need, go, help, eat, drink, water, home, bathroom, what, where)
   - `me want water` -> "I want water." `me need help` -> "I need help."
   - `me want eat` -> "I want to eat." (eat and drink after want or need get "to")
   - `me want go home` -> "I want to go home." `me go home` -> "I am going home."
   - `you ...` becomes a question: "Do you want water?", "Did you eat?", "Are you going home?"
   - `where bathroom` -> "Where is the bathroom?" `what` -> "What?"
   - `water please` -> "Water, please." `please help` -> "Please help."
   - Fixed words form their own sentence: hello "Hello!", bye "Goodbye!", thankyou "Thank you!", sorry "Sorry.", yes "Yes.", no "No."
     so `hello me need help` -> "Hello! I need help."
   - No rule for the words? Join them: `water home` -> "Water home."
   - Every sentence starts with a capital and ends with `.`, `!` or `?`, for **any** sequence of 1 to 3 signs.
   - The full list of examples is in `test_acceptance.py` (the `SENTENCES` table).
3. **Suggestions**: up to 3 likely next signs, valid labels, no repeats, never the sign just given. At the start: include `me`. After `me`: `want` and `need`. After `me want`: `water`, `eat`, `drink`. After `where`: `bathroom`, `home`. After `hello`: `me`.
4. **Pause = sentence finished**: if the gap between two accepted predictions (using their `timestamp`) is more than `pause_seconds`, the current sentence is moved to `history` and a new one starts.

## Step by step (about 5 working days)

**Day 1: setup and baseline**
```powershell
git checkout dev
git pull
git checkout -b feature/context
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest context/tests/test_acceptance.py -q
```
Expect many failures (about 31 failed, 16 passed with the starter file). **That is correct.** Red tests are your to-do list.
Write the last line of the output in the group chat. The old file `test_sentence_builder.py` is gone on purpose (it used our old vocabulary). Read `context/sentence_builder.py` and `test_acceptance.py` and be ready to explain what each does.

**Day 2: grammar**
```powershell
pytest context/tests/test_acceptance.py -k grammar -q
```
Goal: all `grammar` tests green. Tip: do not write 23 separate if-statements. Think of it as: split at the fixed words, then render each clause. Ask your AI to help you design it first, code second.

**Day 3: filtering and rescue**
```powershell
pytest context/tests/test_acceptance.py -k "filtering or rescue" -q
```

**Day 4: suggestions**
```powershell
pytest context/tests/test_acceptance.py -k suggestions -q
```

**Day 5: pause, undo, clear, then everything**
```powershell
pytest context/tests/test_acceptance.py -k "pause or undo or clear or contract" -q
pytest context/tests/test_acceptance.py -q
```
Goal: **47 passed**. Then write `docs/context_notes.md`: 10 to 15 lines in your own words: how a sentence is built, what the rescue rule does, one example walk-through, and one limitation.

**Days 6 to 7 (after everything is green): stretch, optional**
- Write ten more test sentences of your own (a new file `context/tests/test_extra.py`) that a real user might sign.
- Think: what would break the engine? (Write the weirdest sign order you can and see.) Report the findings to Rabia.

## How to check your own work (do this every time)
| Check | Command | Good result |
|---|---|---|
| Your tests | `pytest context/tests/test_acceptance.py -q` | no "FAILED", ends with "passed" |
| You touched only your files | `git status` | only `context/...` and `docs/context_notes.md` |
| You understand it | explain `add()` aloud without looking | you can |

## Pull request
When a day's group is green: commit, push, open a PR into `dev`, and paste the last line of the pytest output in the description.

## Master prompt: paste this into your AI assistant at the start of every new chat
```text
I am Sumaira, a beginner. I am building the context-aware sentence engine for our university HCI & Computer Graphics
project "AI-Powered Sign Language Translation with Context Awareness" (ASL, 20 signs, webcam, Python).
My teammates build the vision model (Rabia) and the website (Kainat). We connect through fixed data contracts.

My file: context/sentence_builder.py (class SentenceBuilder). My exam: context/tests/test_acceptance.py (47 tests).
I must NOT edit the tests or any file outside context/. The 20 labels are: hello, bye, please, thankyou, sorry, yes,
no, me, you, want, need, go, help, eat, drink, water, home, bathroom, what, where.

Input: a dict {"sign", "confidence", "top3", "timestamp"}. Output: {"sentence", "suggestions", "raw_signs"}.
Constructor: SentenceBuilder(min_conf=0.6, rescue_conf=0.35, pause_seconds=3.0).
Methods: add(pred), undo(), clear(), finish(), output(); attributes: words, history.

Rules for you:
1. I am on Windows PowerShell with a venv. Give commands for PowerShell and say which folder to run them in (the project root).
2. Ask to see my current file before changing it. Never rewrite the whole file if a small change works.
3. Work on ONE test group at a time. I will paste the failing pytest output.
4. Explain every change in simple language. I must be able to explain it to an examiner.
5. Do not add new libraries. Do not change the tests. Do not claim something works: I will run pytest and tell you.
6. If a test seems wrong, tell me to ask Rabia instead of changing it.
```

## Done means
- 47 tests green, only your files changed, PR merged into `dev`, notes written, and you can explain `add()`, `render` and the rescue rule without notes.
