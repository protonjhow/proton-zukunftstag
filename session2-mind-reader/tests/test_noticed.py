from datetime import UTC, datetime

import pytest

from mindreader.noticed import Tap, describe_device, noticed
from mindreader.questions import QUESTIONS

KEYS = [q.key for q in QUESTIONS]
FINISHED = datetime(2026, 11, 12, 10, 42, tzinfo=UTC)
MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"


def one_tap_each(step_ms=3000):
    return [Tap(k, "x", (i + 1) * step_ms) for i, k in enumerate(KEYS)]


def test_changes_and_timing():
    # pet 2s, snack tapped 3 times (last at 6s), clock 7s, game 8s, video 9s,
    # power takes 9.4s, then 1s each for the rest
    taps = [
        Tap("pet", "cat", 2000),
        Tap("snack", "chips", 3000), Tap("snack", "fruit", 4500), Tap("snack", "chips", 6000),
        Tap("clock", "early", 7000), Tap("game", "board", 8000), Tap("video", "music", 9000),
        Tap("power", "fly", 18400),
        Tap("weekend", "read", 19400), Tap("emoji", "love", 20400), Tap("season", "spring", 21400),
        Tap("colour", "blue", 22400),
    ]
    lines = noticed(taps, "a Mac", FINISHED)
    assert lines[0] == "You changed your answer to “Pick a snack” 2 times"
    assert lines[1] == "You thought longest about “Pick a superpower” (9 seconds)"
    assert lines[2] == "You answered “Early bird or night owl?” in 1.0 seconds"


def test_one_change_is_singular():
    taps = one_tap_each()
    taps.insert(1, Tap("pet", "dog", 3500))
    assert noticed(taps, "a Mac", FINISHED)[0] == "You changed your answer to “Cat or dog?” 1 time"


def test_noticed_when_never_changed():
    lines = noticed(one_tap_each(), "a Mac", FINISHED)
    assert lines[0] == "You never changed an answer. Very decisive!"
    assert not any(" 0 time" in line for line in lines)
    assert len(lines) == 5


def test_fastest_under_a_second():
    taps = one_tap_each()
    taps[3] = Tap(KEYS[3], "x", taps[2].t + 400)
    taps[4:] = [Tap(t.q, t.option, t.t + 1000) for t in taps[4:]]
    assert noticed(taps, "a Mac", FINISHED)[2] == "You answered “Which would you rather play?” in under a second"


def test_ipad_desktop_mode():
    assert describe_device(MAC, touch=True) == "an iPad"


@pytest.mark.parametrize("ua,touch,expected", [
    ("Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X)", True, "an iPad"),
    ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)", True, "an iPhone"),
    ("Mozilla/5.0 (Linux; Android 14; SM-X200)", True, "an Android tablet or phone"),
    ("Mozilla/5.0 (X11; CrOS x86_64 14541.0.0)", False, "a Chromebook"),
    (MAC, False, "a Mac"),
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)", False, "a Windows computer"),
    ("Mozilla/5.0 (X11; Linux x86_64)", False, "a Linux computer"),
    ("curl/8.0", False, "a computer"),
])
def test_device_table(ua, touch, expected):
    assert describe_device(ua, touch) == expected


def test_device_line():
    assert noticed(one_tap_each(), "an iPad", FINISHED)[3] == "You're using an iPad"


def test_when_line():
    taps = one_tap_each(step_ms=7200)  # last tap at 72 000 ms
    assert noticed(taps, "a Mac", FINISHED)[4] == "You finished at 11:42 on a Thursday, after 1 min 12 s"


def test_when_line_under_a_minute():
    taps = one_tap_each(step_ms=4500)  # 45 s
    assert noticed(taps, "a Mac", FINISHED)[4] == "You finished at 11:42 on a Thursday, after 45 s"


def test_one_second_is_singular():
    lines = noticed(one_tap_each(step_ms=1000), "a Mac", FINISHED)
    assert "(1 second)" in lines[1]
    assert lines[2].endswith("in 1.0 seconds") or lines[2].endswith("under a second")
