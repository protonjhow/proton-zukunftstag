import re
from dataclasses import dataclass

from secretmsgs.caesar import decode
from secretmsgs.envelope import is_wrapped, open_

_TOKEN = re.compile(r"[a-z]+")

# The source list is full of two-letter abbreviations ("tp", "rn"…) that make
# Eve "crack" gibberish, so only real two-letter words are kept.
TWO_LETTER_WORDS = frozenset(
    "am an as at be by do go he hi if in is it me my no of oh ok on or so to up us we".split()
)
# Eve only claims a crack when she matched at least this many letters, covering
# at least half of the message, and no other setting scored as well.
MIN_SCORE = 5


@dataclass(frozen=True)
class Crack:
    shift: int
    plaintext: str
    score: int


@dataclass(frozen=True)
class Sighting:
    locked: bool
    sender: str | None
    raw: str
    crack: Crack | None

    def to_json(self) -> dict:
        return {
            "locked": self.locked,
            "from": self.sender,
            "raw": self.raw,
            "shift": self.crack.shift if self.crack else None,
            "guess": self.crack.plaintext if self.crack else None,
        }


def load_wordlist(path: str) -> frozenset[str]:
    with open(path, encoding="utf-8") as f:
        words = (line.strip().lower() for line in f)
        return frozenset(
            w for w in words
            if len(w) > 2 or w in TWO_LETTER_WORDS or w in ("a", "i")
        )


def crack(text: str, words: frozenset[str]) -> Crack | None:
    letters = sum(len(t) for t in _TOKEN.findall(text.lower()))
    candidates = []
    for shift in range(26):
        plaintext = decode(text, shift)
        score = sum(len(t) for t in _TOKEN.findall(plaintext.lower()) if t in words)
        candidates.append(Crack(shift, plaintext, score))
    candidates.sort(key=lambda c: -c.score)
    best, runner_up = candidates[0], candidates[1]
    if best.score < MIN_SCORE or best.score * 2 < letters or best.score == runner_up.score:
        return None
    return best


def peek(payload: bytes, words: frozenset[str]) -> Sighting:
    raw = payload.decode("utf-8", errors="replace")
    if is_wrapped(payload):
        return Sighting(True, None, raw, None)
    try:
        msg = open_(payload, None)
    except ValueError:
        return Sighting(True, None, raw, None)
    return Sighting(False, msg.sender, msg.text, crack(msg.text, words))
