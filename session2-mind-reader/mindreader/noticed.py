from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from mindreader.questions import BY_KEY, QUESTIONS

ZURICH = ZoneInfo("Europe/Zurich")
# Spelled out so the text doesn't depend on the server's locale (and is easy to translate).
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


@dataclass(frozen=True)
class Tap:
    """One tap on an answer, t = milliseconds since the first question appeared."""

    q: str
    option: str
    t: int


def describe_device(user_agent: str, touch: bool) -> str:
    ua = user_agent or ""
    # iPads in desktop mode say "Macintosh"; only the touch screen gives them away.
    if "iPad" in ua or ("Macintosh" in ua and touch):
        return "an iPad"
    for marker, name in [
        ("iPhone", "an iPhone"),
        ("Android", "an Android tablet or phone"),
        ("CrOS", "a Chromebook"),
        ("Macintosh", "a Mac"),
        ("Windows", "a Windows computer"),
        ("Linux", "a Linux computer"),
    ]:
        if marker in ua:
            return name
    return "a computer"


def _per_question(taps: list[Tap]) -> list[tuple[str, int, int]]:
    """(question, ms spent, changes) in quiz order."""
    out, prev_end = [], 0
    for q in QUESTIONS:
        mine = [t for t in taps if t.q == q.key]
        if not mine:
            continue
        end = mine[-1].t
        out.append((q.key, end - prev_end, len(mine) - 1))
        prev_end = end
    return out


def _prompt(key: str) -> str:
    return f"“{BY_KEY[key].prompt}”"


def noticed(taps: list[Tap], device: str, finished_at: datetime) -> list[str]:
    stats = _per_question(taps)

    most = max(stats, key=lambda s: s[2])
    if most[2] > 0:
        changes = f"You changed your answer to {_prompt(most[0])} {most[2]} time{'s' if most[2] > 1 else ''}"
    else:
        changes = "You never changed an answer. Very decisive!"

    slow = max(stats, key=lambda s: s[1])
    slow_s = max(1, round(slow[1] / 1000))
    slowest = f"You thought longest about {_prompt(slow[0])} ({slow_s} second{'s' if slow_s > 1 else ''})"

    fast = min(stats, key=lambda s: s[1])
    secs = fast[1] / 1000
    fastest = f"You answered {_prompt(fast[0])} in " + ("under a second" if secs < 1 else f"{secs:.1f} seconds")

    total = round(taps[-1].t / 1000)
    minutes, seconds = divmod(total, 60)
    took = f"{minutes} min {seconds} s" if minutes else f"{seconds} s"
    local = finished_at.astimezone(ZURICH)
    when = f"You finished at {local:%H:%M} on a {WEEKDAYS[local.weekday()]}, after {took}"

    return [changes, slowest, fastest, f"You're using {device}", when]
