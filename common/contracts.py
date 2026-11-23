"""The agreed JSON shapes between members. See docs/contracts.md."""


def make_prediction(sign, confidence, top3, timestamp=0.0):
    """Vision -> Context/GUI."""
    return {
        "sign": sign,
        "confidence": round(float(confidence), 3),
        "top3": [[s, round(float(c), 3)] for s, c in top3],
        "timestamp": timestamp,
    }


def make_context_output(sentence, suggestions, raw_signs):
    """Context -> GUI."""
    return {
        "sentence": sentence,
        "suggestions": list(suggestions),
        "raw_signs": list(raw_signs),
    }
