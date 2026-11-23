from context.sentence_builder import SentenceBuilder


def p(sign, conf=0.9):
    return {"sign": sign, "confidence": conf, "top3": [[sign, conf]], "timestamp": 0}


def test_template():
    b = SentenceBuilder()
    b.add(p("where"))
    assert b.add(p("mom"))["sentence"] == "Where is Mom?"


def test_ignores_repeat_and_weak():
    b = SentenceBuilder()
    b.add(p("water"))
    b.add(p("water"))
    b.add(p("please", 0.2))
    assert b.words == ["water"]


def test_fallback_and_undo():
    b = SentenceBuilder()
    b.add(p("yes"))
    out = b.add(p("no"))
    assert out["sentence"] == "Yes no."
    assert b.undo()["raw_signs"] == ["yes"]
