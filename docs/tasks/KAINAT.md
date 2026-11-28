# Kainat: the "Face" (website, HCI, and the Computer Graphics part)

**Analogy:** the vision and context parts are the engine of a car. You build the dashboard: what the driver
sees, trusts and controls. A good dashboard shows what is happening, admits when it is unsure, and lets the user fix mistakes.

Read `docs/TEAM_BRIEF.md` first (contracts, Git, rules for using an AI assistant).

## Your files
| You own | Do not touch |
|---|---|
| `app/static/index.html` (and any CSS/JS you add in `app/static/`) | `app/tests/*` (they are the exam) |
| `app/mock/fake_stream.py` (fake data for you to build against) | `common/`, `vision/`, `context/` |
| `app/main.py` (serving the page only; Rabia connects the real model later, together with you) | |
| `docs/gui_notes.md`, `docs/usability/` (you create them) | |

## How the website works (so you know what you are touching)
```
Browser page  ◄── /video (camera with skeleton, MJPEG)  ── Python (FastAPI)
              ◄── /ws    (JSON messages, WebSocket)     ──
              ──► {"action":"undo"} etc. (Contract 3)   ──►
```
Right now `/ws` sends **fake** messages from `app/mock/fake_stream.py`. Later the real model sends the same shapes.
That is why your mock must follow the contracts exactly. The tests check this.

## Step by step (about 6 working days)

**Day 1: setup, run it, and see red tests**
```powershell
git checkout dev
git pull
git checkout -b feature/gui
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install httpx
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000. You should see your camera with a skeleton, and a fake sentence changing. Stop with **Ctrl+C**.
Then:
```powershell
pytest app/tests -q
```
Expect about 14 failed and 14 passed. **That is correct.** The red tests are your to-do list. Post the last line in the group.

**Day 1 to 2: fix the mock (first real task)**
```powershell
pytest app/tests/test_mock_contract.py -q
```
The starter mock uses old words (`mom`, `hungry`...) that are not in our 20 labels. Rewrite `app/mock/fake_stream.py` so that
it tells a short story using only our 20 labels, for example: me, want, drink (low confidence 0.5), water, please, thankyou.
Needed: a low-confidence message (<0.6), a high one (>=0.85), at least 6 different signs, a sentence that grows, and some
messages with empty suggestions. Goal: `test_mock_contract.py` all green.

**Day 2: page structure (all required ids)**
```powershell
pytest app/tests/test_gui_elements.py -q
```
The page must contain these element ids (exact spelling):
`video, sign, confidence-bar, confidence-text, sentence, suggestions, history, status, btn-speak, btn-undo, btn-clear, btn-camera`.
Also `<html lang="en">`, a `<title>`, the viewport meta tag, `aria-live` on the sentence, alt text on the camera image, a dark-mode
`@media (prefers-color-scheme: dark)` section, and every button with visible text or an `aria-label`.
Before coding, sketch the layout on paper (two options), choose one with the team, save the photos in `docs/design/`.

**Day 3: show system state (HCI: visibility of system status)**
The `status` area and the confidence bar must clearly show three states, driven by the incoming data:
1. **Confident** (confidence >= 0.6): green bar, sign shown.
2. **Not sure** (< 0.6): amber bar, text like "Not sure. Did you mean X or Y?" using `top3`.
3. **No data / disconnected**: "Waiting for camera..." or "Connection lost. Reconnecting...".
Use more than colour: also use words or icons (colour-blind users).

**Day 4: controls and history (HCI: user control and freedom)**
- Suggestion buttons appear in `#suggestions` (tap a suggestion = it is highlighted; real adding comes at integration).
- Undo, Clear and Finish send `{"action": "undo"}` etc. over the WebSocket (the mock may ignore them for now; it must not crash).
- `#history` lists finished sentences (newest first). Speak reads `#sentence` aloud using `speechSynthesis`.
- `#btn-camera` toggles the video (hide/show the image is enough for now).

**Day 5: accessibility and polish (HCI: accessibility, consistency, aesthetics)**
Large readable text, contrast that passes WCAG AA, keyboard use (Tab order, Enter on buttons), responsive on a phone width,
dark mode, focus outlines visible. Test with the browser's zoom at 200%.

**Day 6: usability test plan**
Create `docs/usability/plan.md`: 5 test users, 3 tasks (for example "say that you want water", "undo a mistake", "make the
computer speak a sentence"), what you will observe, and the 10 SUS questions. Save the questionnaire.

**Day 7: notes**
Create `docs/gui_notes.md`: for each of these heuristics, one sentence on where it appears in your page: visibility of system
status, match with the real world, user control, consistency, error prevention, recognition over recall, flexibility,
aesthetic design, error recovery, help. These notes feed the HCI report.

## Manual checklist (the tests cannot check these, so you do)
Open the page and tick each one honestly:

| Do this | You should see |
|---|---|
| Open http://127.0.0.1:8000 | camera + skeleton + sentence area, no console errors (press F12) |
| Wait 10 seconds | sign, confidence and sentence change by themselves |
| Look at the low-confidence message | amber state and a "did you mean" text |
| Press Tab repeatedly | focus moves through all buttons in a sensible order with a visible outline |
| Shrink the window to phone width | nothing overlaps, nothing is cut off, no sideways scrolling |
| Switch your computer to dark mode | the page is still readable |
| Zoom the browser to 200% | still usable |
| Press Speak | the sentence is spoken (use Chrome or Edge) |
| Stop the server (Ctrl+C), wait | the page shows a connection-lost message instead of silently freezing |

## How to check your own work (every time)
| Check | Command | Good result |
|---|---|---|
| Data contracts | `pytest app/tests/test_mock_contract.py -q` | all passed |
| Page basics | `pytest app/tests/test_gui_elements.py -q` | all passed |
| Everything | `pytest app/tests -q` | 28 passed |
| Only your files changed | `git status` | only `app/...` and `docs/...` |

## Pull request
When a day's work is green: commit (by file name), push, open a PR into `dev`, paste the last pytest line and a screenshot.

## Master prompt: paste this into your AI assistant at the start of every new chat
```text
I am Kainat, a beginner. I am building the website (UI and HCI) for our university HCI & Computer Graphics project
"AI-Powered Sign Language Translation with Context Awareness" (ASL, 20 signs, webcam, Python FastAPI backend,
plain HTML/CSS/JavaScript frontend, no framework). Teammates build the vision model (Rabia) and the sentence engine (Sumaira).

My files: app/static/index.html (plus CSS/JS in app/static/), app/mock/fake_stream.py, app/main.py (serving only).
My exam: app/tests/test_mock_contract.py and app/tests/test_gui_elements.py. I must NOT edit tests or files outside app/ and docs/.
The 20 labels are: hello, bye, please, thankyou, sorry, yes, no, me, you, want, need, go, help, eat, drink, water, home, bathroom, what, where.

The browser receives JSON on WebSocket /ws: {"prediction": {"sign","confidence","top3":[[label,conf],...],"timestamp"},
"context": {"sentence","suggestions","raw_signs"}, "history": [..optional..]}. The camera is <img src="/video">.
The browser can send {"action":"undo"|"clear"|"finish"}.

Required element ids: video, sign, confidence-bar, confidence-text, sentence, suggestions, history, status, btn-speak,
btn-undo, btn-clear, btn-camera. HCI goals: visibility of system status, honest confidence ("not sure, did you mean X or Y"),
user control (undo/clear), accessibility (contrast, keyboard, aria-live, dark mode, responsive).

Rules for you:
1. I am on Windows PowerShell with a venv. Give PowerShell commands and say which folder to run them in (the project root).
2. Ask to see my current file before changing it. Never rewrite the whole file if a small change works.
3. Work on ONE feature at a time. I will paste the failing pytest output or describe what I see in the browser.
4. Explain each change in simple language. I must be able to explain it to an examiner.
5. Do not add libraries or frameworks. Do not change the tests. Do not claim it works: I will run it and tell you.
6. If a test seems wrong, tell me to ask Rabia instead of changing it.
```

## Done means
- `pytest app/tests -q` shows 28 passed, the manual checklist is fully ticked, only your files changed, PR merged into `dev`,
  `docs/usability/plan.md` and `docs/gui_notes.md` exist, and you can explain how the page gets its data.
