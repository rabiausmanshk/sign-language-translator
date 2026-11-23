"""Fake Vision + Context output so the GUI can be built before the real parts exist."""
import asyncio
from common.contracts import make_prediction, make_context_output

SCRIPT = [
    ("where", 0.92, "Where?", ["mom", "dad", "home"]),
    ("mom", 0.88, "Where is Mom?", []),
    ("hungry", 0.55, "Where is Mom? Hungry.", ["food"]),     # low confidence -> UI should react
    ("food", 0.90, "Where is Mom? I am hungry. I want food.", ["please"]),
]


async def fake_stream():
    raw = []
    while True:
        for sign, conf, sentence, sugg in SCRIPT:
            raw.append(sign)
            yield {
                "prediction": make_prediction(sign, conf, [(sign, conf), ("drink", 0.05), ("water", 0.02)]),
                "context": make_context_output(sentence, sugg, raw[-6:]),
            }
            await asyncio.sleep(1.5)
        raw = []
