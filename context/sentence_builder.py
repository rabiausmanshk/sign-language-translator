"""Context engine v1 (rule based). Sumaira owns and upgrades this file.
Input : prediction dicts (contract 1).  Output: context dict (contract 2).

How it works in one line:
    add() decides whether to believe a sign -> words list -> _render() turns the words into a sentence.
"""
from common.contracts import make_context_output

# ---------------------------------------------------------------------------
# Rule tables (all labels are from our 20 signs)
# ---------------------------------------------------------------------------

# Words that form a complete sentence on their own.
FIXED = {
    "hello": "Hello!",
    "bye": "Goodbye!",
    "thankyou": "Thank you!",
    "sorry": "Sorry.",
    "yes": "Yes.",
    "no": "No.",
}

# After want / need, these verbs get "to":  "I want to eat."
TO_VERBS = ("eat", "drink", "go")

# Likely next signs. We look at the last TWO words first, then the last ONE word.
START_SUGGESTIONS = ["me", "you", "where"]

AFTER_TWO = {
    ("me", "want"): ["water", "eat", "drink"],
    ("me", "need"): ["help", "water", "eat"],
    ("you", "want"): ["water", "eat", "drink"],
    ("you", "need"): ["help", "water", "eat"],
}

AFTER_ONE = {
    "me": ["want", "need", "go"],
    "you": ["want", "need", "go"],
    "want": ["water", "eat", "drink"],
    "need": ["help", "water", "eat"],
    "go": ["home", "bathroom"],
    "where": ["bathroom", "home"],
    "what": ["you", "want"],
    "hello": ["me", "you"],
    "sorry": ["me", "you"],
    "yes": ["me", "you"],
    "no": ["me", "you"],
    "water": ["please"],
    "eat": ["please", "thankyou"],
    "drink": ["water", "please"],
    "help": ["please", "thankyou"],
    "home": ["please", "thankyou"],
    "bathroom": ["please"],
    "please": ["thankyou"],
    "thankyou": ["bye"],
    "bye": [],
}


def suggest_next(words):
    """Up to 3 likely next signs for the given list of words."""
    if not words:
        candidates = START_SUGGESTIONS
    elif len(words) >= 2 and tuple(words[-2:]) in AFTER_TWO:
        candidates = AFTER_TWO[tuple(words[-2:])]
    else:
        candidates = AFTER_ONE.get(words[-1], [])
    last = words[-1] if words else None
    result = []
    for s in candidates:
        if s != last and s not in result:     # never repeat the sign just given, no duplicates
            result.append(s)
    return result[:3]


class SentenceBuilder:
    def __init__(self, min_conf=0.6, rescue_conf=0.35, pause_seconds=3.0):
        self.min_conf = min_conf              # at or above this: always believe the sign
        self.rescue_conf = rescue_conf        # below this: never believe the sign
        self.pause_seconds = pause_seconds    # a longer gap means "the sentence is finished"
        self.words = []                       # accepted labels of the current sentence
        self.history = []                     # finished sentences
        self._last_time = None                # timestamp of the last accepted sign

    # ------------------------------------------------------------------ input
    def add(self, pred):
        """Accept or ignore one prediction, then return the Contract 2 dict."""
        sign = pred["sign"]
        conf = pred["confidence"]
        now = pred.get("timestamp")

        # 1. Did the signer pause long enough to start a new sentence?
        pause = (
            self.words
            and now is not None
            and self._last_time is not None
            and now - self._last_time > self.pause_seconds
        )
        current = [] if pause else self.words    # the words this sign would continue from

        # 2. Ignore the same sign twice in a row.
        if current and current[-1] == sign:
            return self.output()

        # 3. Believe the sign?
        if conf >= self.min_conf:
            accepted = True
        elif conf >= self.rescue_conf:
            accepted = sign in suggest_next(current)   # weak guess: only if it fits the context
        else:
            accepted = False

        if not accepted:
            return self.output()

        # 4. Accept it (after closing the old sentence if there was a pause).
        if pause:
            self.finish()
        self.words.append(sign)
        self._last_time = now
        return self.output()

    # --------------------------------------------------------------- controls
    def undo(self):
        """Remove the last word."""
        if self.words:
            self.words.pop()
        return self.output()

    def clear(self):
        """Empty the current words but keep the history."""
        self.words = []
        self._last_time = None
        return self.output()

    def finish(self):
        """Complete the sentence: save it in history, start a new one, return the finished text."""
        if not self.words:
            return ""
        sentence = self._render()
        self.history.append(sentence)
        self.words = []
        self._last_time = None
        return sentence

    # ---------------------------------------------------------------- grammar
    def _render(self):
        """Words -> sentence. Split at the fixed words, render each group, join with spaces."""
        sentences = []
        clause = []                           # ordinary words waiting to become a sentence
        for w in self.words:
            if w in FIXED:
                if clause:
                    sentences.append(self._clause(clause))
                    clause = []
                sentences.append(FIXED[w])
            else:
                clause.append(w)
        if clause:
            sentences.append(self._clause(clause))
        return " ".join(sentences)

    def _clause(self, w):
        """Turn one group of ordinary words into one sentence."""
        # "water please" -> "Water, please."   (render the rest, then add ", please")
        if w[-1] == "please" and len(w) > 1:
            body = self._clause(w[:-1])
            return body[:-1] + ", please" + body[-1]

        first, rest = w[0], w[1:]
        if first == "me":
            return self._me_clause(rest)
        if first == "you":
            return self._you_clause(rest)
        if first == "where":
            return self._where_clause(rest)
        if first == "what":
            return "What?" if not rest else "What " + " ".join(rest) + "?"
        return " ".join(w).capitalize() + "."     # no rule: just join the words

    def _me_clause(self, rest):
        """me ... -> a sentence with "I"."""
        if not rest:
            return "Me."
        verb, tail = rest[0], rest[1:]
        if verb in ("want", "need"):
            start = "I " + verb
            if tail and tail[0] in TO_VERBS:
                start += " to"                # I want TO eat
        elif verb == "go":
            start = "I am going"              # I am going home
        else:
            start = "I " + verb
        return " ".join([start] + tail) + "."

    def _you_clause(self, rest):
        """you ... -> a question."""
        if not rest:
            return "You?"
        verb, tail = rest[0], rest[1:]
        if verb in ("want", "need"):
            start = "Do you " + verb
            if tail and tail[0] in TO_VERBS:
                start += " to"
        elif verb in ("eat", "drink"):
            start = "Did you " + verb
        elif verb == "go":
            start = "Are you going"
        elif verb == "help":
            start = "Can you help"
        else:
            return " ".join(["you"] + rest).capitalize() + "?"
        return " ".join([start] + tail) + "?"

    def _where_clause(self, rest):
        """where ... -> "Where is the bathroom?"."""
        if not rest:
            return "Where?"
        things = ["the bathroom" if x == "bathroom" else x for x in rest]
        return "Where is " + " ".join(things) + "?"

    # ----------------------------------------------------------------- output
    def output(self):
        """Current Contract 2 dict (adds nothing)."""
        return make_context_output(self._render(), suggest_next(self.words), list(self.words))
