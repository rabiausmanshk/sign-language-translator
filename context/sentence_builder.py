"""Context engine v0 (rule based). Sumaira owns and upgrades this file.
Input : prediction dicts (contract 1).  Output: context dict (contract 2).
"""
from common.contracts import make_context_output

TEMPLATES = {
    ("hello",): "Hello!",
    ("where", "mom"): "Where is Mom?",
    ("where", "dad"): "Where is Dad?",
    ("water", "please"): "Water, please.",
    ("drink", "water"): "I want to drink water.",
    ("hungry", "food"): "I am hungry. I want food.",
    ("hungry", "now"): "I am hungry right now.",
    ("sick", "mom"): "Mom is sick.",
    ("home", "now"): "I want to go home now.",
}

FOLLOW_UPS = {
    "hello": ["please", "thankyou"],
    "water": ["please"],
    "hungry": ["food"],
    "where": ["mom", "dad", "home"],
}


class SentenceBuilder:
    def __init__(self, min_conf=0.6):
        self.min_conf = min_conf
        self.words = []

    def add(self, pred):
        """Accept a prediction; ignore weak guesses and immediate repeats."""
        if pred["confidence"] >= self.min_conf and (not self.words or self.words[-1] != pred["sign"]):
            self.words.append(pred["sign"])
        return self.output()

    def undo(self):
        if self.words:
            self.words.pop()
        return self.output()

    def clear(self):
        self.words = []
        return self.output()

    def _render(self):
        w = self.words
        for n in range(len(w), 0, -1):            # longest matching ending first
            key = tuple(w[-n:])
            if key in TEMPLATES:
                prefix = " ".join(w[:-n])
                return (prefix.capitalize() + ". " if prefix else "") + TEMPLATES[key]
        return (" ".join(w).capitalize() + ".") if w else ""

    def output(self):
        last = self.words[-1] if self.words else None
        return make_context_output(self._render(), FOLLOW_UPS.get(last, []), self.words)
