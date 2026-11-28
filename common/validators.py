"""Contract checkers shared by everyone (owner: Rabia).
They answer one question: "does this dictionary follow the agreed shape?"
If not, they raise ContractError with a plain-English message saying what is wrong.
"""
from common.vocabulary import LABELS


class ContractError(AssertionError):
    pass


def _need(condition, message):
    if not condition:
        raise ContractError(message)


def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate_prediction(p):
    """Contract 1: what the vision part sends (and what the mock stream must imitate)."""
    _need(isinstance(p, dict), "prediction must be a dict")
    for key in ("sign", "confidence", "top3", "timestamp"):
        _need(key in p, f"prediction is missing the key '{key}'")
    _need(p["sign"] in LABELS, f"prediction sign '{p['sign']}' is not one of our 20 labels")
    _need(_is_number(p["confidence"]) and 0 <= p["confidence"] <= 1,
          "prediction confidence must be a number between 0 and 1")
    top3 = p["top3"]
    _need(isinstance(top3, list) and 1 <= len(top3) <= 3, "top3 must be a list of 1 to 3 pairs")
    for pair in top3:
        _need(isinstance(pair, (list, tuple)) and len(pair) == 2, "each top3 item must be [label, confidence]")
        _need(pair[0] in LABELS, f"top3 label '{pair[0]}' is not one of our 20 labels")
        _need(_is_number(pair[1]) and 0 <= pair[1] <= 1, "top3 confidence must be between 0 and 1")
    scores = [pair[1] for pair in top3]
    _need(scores == sorted(scores, reverse=True), "top3 must be sorted from highest to lowest confidence")
    _need(top3[0][0] == p["sign"], "the first item of top3 must be the predicted sign")
    _need(_is_number(p["timestamp"]), "timestamp must be a number (seconds)")
    return True


def validate_context_output(c):
    """Contract 2: what the context engine sends to the website."""
    _need(isinstance(c, dict), "context output must be a dict")
    for key in ("sentence", "suggestions", "raw_signs"):
        _need(key in c, f"context output is missing the key '{key}'")
    _need(isinstance(c["sentence"], str), "sentence must be a string")
    _need(isinstance(c["suggestions"], list), "suggestions must be a list")
    _need(len(c["suggestions"]) <= 3, "suggestions must have at most 3 items")
    _need(len(set(c["suggestions"])) == len(c["suggestions"]), "suggestions must not repeat")
    for s in c["suggestions"]:
        _need(s in LABELS, f"suggestion '{s}' is not one of our 20 labels")
    _need(isinstance(c["raw_signs"], list), "raw_signs must be a list")
    for s in c["raw_signs"]:
        _need(s in LABELS, f"raw sign '{s}' is not one of our 20 labels")
    return True
