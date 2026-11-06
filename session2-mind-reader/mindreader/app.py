from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from mindreader import questions
from mindreader.guesses import make_guesses
from mindreader.noticed import Tap, describe_device, noticed
from mindreader.store import AvatarTaken, Store

WEB = Path(__file__).parent.parent / "web"
AVATAR_EMOJI = dict(questions.AVATARS)


class TapIn(BaseModel):
    q: str
    option: str
    t: int


class Submission(BaseModel):
    avatar: str
    answers: dict[str, str]
    taps: list[TapIn]
    touch: bool = False


def _validate(s: Submission) -> None:
    if s.avatar not in AVATAR_EMOJI:
        raise HTTPException(400, "unknown avatar")
    if set(s.answers) != set(questions.BY_KEY):
        raise HTTPException(400, "answers must cover every question")
    for q, option in s.answers.items():
        if option not in {o.key for o in questions.BY_KEY[q].options}:
            raise HTTPException(400, f"unknown option for {q}")
    if not s.taps or any(t.q not in questions.BY_KEY for t in s.taps):
        raise HTTPException(400, "bad taps")
    if any(b.t < a.t for a, b in zip(s.taps, s.taps[1:])) or s.taps[0].t < 0:
        raise HTTPException(400, "taps out of order")


def _card(s: Submission, guesses: list[dict]) -> dict:
    a = s.answers
    stars = 3 + (a["game"] in ("minecraft", "roblox")) + (a["weekend"] == "screens")
    return {
        "avatar": s.avatar,
        "emoji": AVATAR_EMOJI[s.avatar],
        "title": guesses[3]["value"],
        "interests": [questions.label(q, a[q]) for q in ("game", "video", "snack")],
        "notify": guesses[0]["value"],
        "ad": guesses[2]["value"],
        "stars": stars,
    }


def create_app(store: Store, now: Callable[[], datetime]) -> FastAPI:
    app = FastAPI()

    @app.exception_handler(RequestValidationError)
    async def bad_request(request, exc):
        return JSONResponse({"detail": "bad submission"}, status_code=400)

    app.mount("/static", StaticFiles(directory=WEB), name="static")

    pages = [("/", "quiz.html"), ("/screen", "screen.html"), ("/cards", "cards.html"), ("/facts", "facts.html")]
    for path, page in pages:
        app.add_api_route(path, lambda page=page: FileResponse(WEB / page), methods=["GET"])

    @app.get("/api/quiz")
    def quiz():
        return {**questions.to_json(), "taken": sorted(store.taken())}

    @app.post("/api/submit")
    def submit(s: Submission, request: Request):
        _validate(s)
        guesses = make_guesses(s.answers)
        taps = [Tap(t.q, t.option, t.t) for t in s.taps]
        device = describe_device(request.headers.get("user-agent", ""), s.touch)
        profile = {
            "avatar": s.avatar,
            "emoji": AVATAR_EMOJI[s.avatar],
            "guesses": guesses,
            "noticed": noticed(taps, device, now()),
            "card": _card(s, guesses),
        }
        try:
            store.add(s.avatar, profile)
        except AvatarTaken:
            raise HTTPException(409, "avatar taken")
        return profile

    @app.get("/api/profiles")
    def profiles():
        return {"count": store.count(), "profiles": store.all()}

    @app.post("/api/delete")
    def delete():
        return {"deleted": store.clear(), "count": store.count()}

    return app


app = create_app(Store(), now=lambda: datetime.now(UTC))
