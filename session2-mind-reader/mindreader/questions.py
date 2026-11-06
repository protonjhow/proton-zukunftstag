from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Option:
    key: str
    label: str
    emoji: str


@dataclass(frozen=True)
class Question:
    key: str
    prompt: str
    options: tuple[Option, ...]


def _q(key: str, prompt: str, *options: tuple[str, str, str]) -> Question:
    return Question(key, prompt, tuple(Option(*o) for o in options))


# Harmless preferences and habits only. Never home, location, school, family,
# health, relationships, appearance or money.
QUESTIONS: tuple[Question, ...] = (
    _q("pet", "Cat or dog?",
       ("cat", "Cat", "🐱"), ("dog", "Dog", "🐶"), ("both", "Both!", "🐾"), ("neither", "Neither", "🦎")),
    _q("snack", "Pick a snack",
       ("chips", "Chips", "🥔"), ("fruit", "Fruit", "🍎"), ("chocolate", "Chocolate", "🍫"), ("popcorn", "Popcorn", "🍿")),
    _q("clock", "Early bird or night owl?",
       ("early", "Early bird", "🌅"), ("night", "Night owl", "🦉"), ("depends", "It depends", "🤷"),
       ("sleepy", "Always sleepy", "😴")),
    _q("game", "Which would you rather play?",
       ("minecraft", "Minecraft", "⛏️"), ("roblox", "Roblox", "🧱"), ("mariokart", "Mario Kart", "🏎️"),
       ("board", "A board game", "🎲")),
    _q("video", "Which video would you click?",
       ("animals", "Funny animals", "🐹"), ("gaming", "Gaming", "🎮"), ("music", "Music", "🎵"),
       ("crafts", "Crafts and DIY", "✂️")),
    _q("power", "Pick a superpower",
       ("fly", "Flying", "🦅"), ("invisible", "Being invisible", "👻"), ("animals", "Talking to animals", "🗣️"),
       ("time", "Time travel", "⏳")),
    _q("weekend", "Saturday morning, first thing?",
       ("sleep", "Sleep in", "🛌"), ("outside", "Play outside", "⚽"), ("screens", "Screens", "📱"),
       ("read", "Read or draw", "📚")),
    _q("emoji", "Pick an emoji",
       ("laugh", "Laughing", "😂"), ("love", "Hearts", "🥰"), ("cool", "Cool", "😎"), ("think", "Thinking", "🤔")),
    _q("season", "Favourite season",
       ("spring", "Spring", "🌷"), ("summer", "Summer", "☀️"), ("autumn", "Autumn", "🍂"), ("winter", "Winter", "❄️")),
    _q("colour", "Pick a colour",
       ("purple", "Purple", "🟣"), ("blue", "Blue", "🔵"), ("green", "Green", "🟢"), ("orange", "Orange", "🟠")),
)

AVATARS: tuple[tuple[str, str], ...] = (
    ("fox", "🦊"), ("panda", "🐼"), ("frog", "🐸"), ("owl", "🦉"), ("octopus", "🐙"), ("unicorn", "🦄"),
    ("tiger", "🐯"), ("penguin", "🐧"), ("koala", "🐨"), ("lion", "🦁"), ("turtle", "🐢"), ("bee", "🐝"),
)

BY_KEY = {q.key: q for q in QUESTIONS}


def label(question: str, option: str) -> str:
    return next(o.label for o in BY_KEY[question].options if o.key == option)


def to_json() -> dict:
    return {
        "questions": [asdict(q) for q in QUESTIONS],
        "avatars": [{"key": k, "emoji": e} for k, e in AVATARS],
    }
