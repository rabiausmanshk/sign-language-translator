# AI-Powered Sign Language Translation with Context Awareness
HCI & CG end-semester project. Pipeline: Webcam -> Vision (sign) -> Context (sentence) -> GUI (display + voice).

## Setup (everyone)
1. Install Python 3.11 (python.org). On Windows use normal Python, NOT WSL (webcam access).
2. git clone <repo-url> && cd sign-language-translator
3. python -m venv .venv
   - Windows: .venv\Scripts\activate      - Mac/Linux: source .venv/bin/activate
4. pip install -r requirements.txt            (Rabia also: pip install -r requirements-ml.txt)
5. Always run commands from the repo root, e.g. `python -m vision.collect_data --person rabia`

## Quick checks
- Tests (Sumaira):  pytest
- GUI (Kainat):     uvicorn app.main:app --reload   -> http://127.0.0.1:8000
- Recorder (Rabia): python -m vision.collect_data --person rabia

## Rules
- Never push to main. Branch -> Pull Request into dev -> one reviewer.
- Only edit your own folder. Shared files (common/, docs/) need a team message first.
- Never commit data or .env.
