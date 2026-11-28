# Team Brief: Sign Language Translator

Read this once, fully. Then read your own sheet in `docs/tasks/` (SUMAIRA.md or KAINAT.md).

## 1. The project in 30 seconds

A person signs ASL words in front of a webcam. Our website shows which sign it saw, builds a proper
sentence from the signs, and can say it out loud.

```
 Webcam ─► [VISION]  ─► [CONTEXT] ─► [WEBSITE]
           Rabia         Sumaira      Kainat
           sees the      turns signs  shows it,
           sign          into a       speaks it
                         sentence
```

We build the three parts separately and plug them together later. That only works if everyone obeys
the **contracts** below. Think of a contract as a plug shape: if both sides use the same shape, they connect.

## 2. Our 20 signs

The left name is the label used everywhere in code (lowercase). It is defined once in `common/vocabulary.py`.

| Group | Labels |
|---|---|
| Greetings and politeness | hello, bye, please, thankyou, sorry |
| Answers | yes, no |
| Pronouns | me, you |
| Verbs | want, need, go, help, eat, drink |
| Nouns | water, home, bathroom |
| Questions | what, where |

ASL Citizen has no "I" sign, so `me` stands for "I". The context engine writes "I" or "me" as grammar needs.

## 3. The contracts

**Contract 1: Prediction** (vision sends it)
```json
{"sign": "water", "confidence": 0.91,
 "top3": [["water", 0.91], ["drink", 0.06], ["eat", 0.02]], "timestamp": 12.4}
```
`top3` is sorted high to low, and its first item is `sign`.

**Contract 2: Context output** (the context engine sends it)
```json
{"sentence": "I want water.", "suggestions": ["please", "thankyou"], "raw_signs": ["me", "want", "water"]}
```
At most 3 suggestions, no repeats, all valid labels.

**Website message** (what the browser receives on the WebSocket `/ws`)
```json
{"prediction": { ...contract 1... }, "context": { ...contract 2... }, "history": ["Hello!"]}
```
`history` (finished sentences) is optional for now.

**Contract 3: Commands from the browser to the server** (Undo, Clear and so on)
```json
{"action": "undo"}     {"action": "clear"}     {"action": "finish"}
```

**Checkers:** `common/validators.py` has `validate_prediction(...)` and `validate_context_output(...)`.
They say in plain English what is wrong with a dictionary. The tests use them.

## 4. Who owns what

| Person | Owns (only edit these) | Never edit |
|---|---|---|
| Rabia (lead) | `vision/`, `scripts/`, `common/`, `docs/` | other people's folders (except at integration) |
| Sumaira | `context/` | `common/`, `vision/`, `app/` |
| Kainat | `app/` | `common/`, `vision/`, `context/` |

If you need a change in someone else's file, message them. This is how we avoid merge conflicts.

## 5. Git workflow (PowerShell, from the project root)

First time (get the latest code and make your own branch):
```powershell
cd "<your project folder>"
git checkout dev
git pull
git checkout -b feature/context        # Kainat: feature/gui
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Every working session:
```powershell
git status                              # what did I change?
pytest -q                               # tests (your own group, see your sheet)
git add context/sentence_builder.py     # add files BY NAME (Kainat: app/...)
git commit -m "Add grammar rules for want/need"
git push -u origin feature/context
```
Then on GitHub press **Compare & pull request**. Set **base: dev**. Rabia reviews and merges.

Rules:
- Never work directly on `main` or `dev`.
- Never run `git add .` (it can grab files you did not mean to share).
- Never commit videos, recordings, `.venv`, `.env`, or model files.
- Commit small and often. Push at least once per day.
- Always run commands from the **project root** (the folder containing `README.md`).

## 6. Working with an AI assistant (ChatGPT, Gemini, Claude, ...)

You are allowed and encouraged to use an AI assistant. But you must be able to **explain every line you submit**,
because the examiners will ask you.

**The loop:**
1. Paste the master prompt from your sheet into a fresh chat. It tells the AI who you are and the rules.
2. Work on **one small thing at a time** (one test group, one UI feature).
3. Paste the failing test output or the error. Ask: "Explain what this means, then show the smallest change."
4. Apply the change. Run the test again.
5. **Green means it worked. Red means it did not.** Do not trust the AI's claim that it works, only the test.
6. Ask the AI: "Explain this code to me line by line as if I am a beginner." Do not continue until you understand.
7. Commit when a group of tests turns green.

**Rules for the AI (they are inside the master prompt):**
- Never rewrite a whole file when a small change is enough.
- Ask to see my current file before changing it.
- Give Windows PowerShell commands, and say which folder to run them in.
- Never edit the test files or files outside my folder.
- Do not add new libraries without telling me why.

**If the AI is stuck in circles:** start a new chat, paste the master prompt, paste the current file and the one failing test, nothing else.

## 7. Daily rhythm

- Post a short status in the group twice a day: *done / doing / stuck*.
- If stuck for more than 45 minutes, ask. Do not wait for the end of the day.
- Run your tests before you push, and paste the last line of the test output in your PR description.

## 8. Lead's review checklist (Rabia)

Before merging a pull request:
1. `git fetch` then check out their branch, then run their tests: `pytest -q`. All their groups are green.
2. Only files in their folder changed (`git diff --stat dev`).
3. No data, no `.env`, no `.venv` in the diff.
4. Ask them to **explain one function** without looking. If they cannot, they are not done.
5. Run the app or the demo once yourself.

## 9. What we honestly claim (for the viva)

- A **limited-vocabulary prototype**: 20 ASL signs, not full ASL grammar or full sentences.
- "Context aware" means: the sentence builder uses earlier signs, grammar rules, confidence, and likely next words.
- Accuracy numbers come only from our own tests, on signers the model has never seen.
- Dataset: ASL Citizen (Microsoft). We read its usage terms and cite it.
