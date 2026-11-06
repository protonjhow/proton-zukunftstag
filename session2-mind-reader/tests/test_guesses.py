import itertools

from mindreader.guesses import make_guesses
from mindreader.questions import QUESTIONS
from tests.test_questions import BANNED

BASE = {
    "pet": "dog", "snack": "chocolate", "clock": "night", "game": "minecraft", "video": "gaming",
    "power": "fly", "weekend": "sleep", "emoji": "cool", "season": "winter", "colour": "blue",
}


def test_guesses_exact():
    assert make_guesses(BASE) == [
        {"label": "Best time to send you a notification", "value": "In the evening, after 20:00"},
        {"label": "Videos we'd recommend", "value": "Gaming videos and cute pet clips"},
        {"label": "An ad you'd probably click", "value": "A Minecraft skin pack (and a chocolate advert)"},
        {"label": "Your type", "value": "The High-Flying Adventurer"},
        {"label": "Your weekend", "value": "Sleeping in, because you stayed up late"},
    ]


def test_guesses_never_personal():
    opts = {q.key: [o.key for o in q.options] for q in QUESTIONS}
    keys = ["clock", "game", "weekend", "emoji", "power", "video", "pet", "snack"]
    for combo in itertools.product(*(opts[k] for k in keys)):
        guesses = make_guesses({**BASE, **dict(zip(keys, combo))})
        assert len(guesses) == 5
        for g in guesses:
            for word in BANNED:
                assert word not in g["value"].lower(), f"{word!r} in {g}"
