from mindreader.questions import AVATARS, QUESTIONS

BANNED = [
    "school", "home", "live", "address", "street", "mum", "mom", "dad", "brother", "sister",
    "sibling", "family", "money", "phone number", "birthday", "boyfriend", "girlfriend", "weight",
]


def test_ten_questions_four_options():
    assert len(QUESTIONS) == 10
    assert all(len(q.options) == 4 for q in QUESTIONS)
    assert len({q.key for q in QUESTIONS}) == 10
    for q in QUESTIONS:
        assert len({o.key for o in q.options}) == 4


def test_no_personal_topics():
    texts = [q.prompt for q in QUESTIONS] + [o.label for q in QUESTIONS for o in q.options]
    for text in texts:
        for word in BANNED:
            assert word not in text.lower(), f"{word!r} in {text!r}"


def test_twelve_unique_avatars():
    assert len(AVATARS) == 12
    assert len({k for k, _ in AVATARS}) == 12
    assert len({e for _, e in AVATARS}) == 12
