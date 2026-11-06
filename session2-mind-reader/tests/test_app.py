from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from mindreader.app import create_app
from mindreader.questions import QUESTIONS
from mindreader.store import Store

IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"
ANSWERS = {
    "pet": "dog", "snack": "chocolate", "clock": "night", "game": "minecraft", "video": "gaming",
    "power": "fly", "weekend": "screens", "emoji": "cool", "season": "winter", "colour": "blue",
}


def body(avatar="fox", answers=None, taps=None):
    answers = ANSWERS if answers is None else answers
    if taps is None:
        taps = [{"q": q.key, "option": ANSWERS[q.key], "t": (i + 1) * 2000} for i, q in enumerate(QUESTIONS)]
    return {"avatar": avatar, "answers": answers, "taps": taps, "touch": True}


@pytest.fixture
def client():
    app = create_app(Store(), now=lambda: datetime(2026, 11, 12, 10, 42, tzinfo=UTC))
    with TestClient(app) as c:
        yield c


def submit(client, **kw):
    return client.post("/api/submit", json=body(**kw), headers={"User-Agent": IPHONE})


@pytest.mark.parametrize("path,marker", [("/", "quiz.js"), ("/screen", "screen.js"), ("/cards", "cards.js")])
def test_index_and_pages_serve(client, path, marker):
    r = client.get(path)
    assert r.status_code == 200
    assert marker in r.text


def test_quiz_lists_questions_and_taken(client):
    data = client.get("/api/quiz").json()
    assert len(data["questions"]) == 10
    assert len(data["avatars"]) == 12
    assert data["taken"] == []


def test_submit_returns_profile(client):
    r = submit(client)
    assert r.status_code == 200
    p = r.json()
    assert (p["avatar"], p["emoji"]) == ("fox", "🦊")
    assert len(p["guesses"]) == 5
    assert len(p["noticed"]) == 5
    assert p["noticed"][3] == "You're using an iPhone"
    card = p["card"]
    assert card["title"] == "The High-Flying Adventurer"
    assert card["interests"] == ["Minecraft", "Gaming", "Chocolate"]
    assert card["stars"] == 5
    assert 1 <= card["stars"] <= 5


def test_avatar_taken_returns_409(client):
    assert submit(client).status_code == 200
    assert submit(client).status_code == 409
    assert client.get("/api/quiz").json()["taken"] == ["fox"]


@pytest.mark.parametrize("change", [
    {"avatar": "dragon"},
    {"answers": {**ANSWERS, "pet": "hamster"}},
    {"answers": {k: v for k, v in ANSWERS.items() if k != "colour"}},
    {"taps": [{"q": "pet", "option": "dog", "t": 5000}, {"q": "snack", "option": "chocolate", "t": 1000}]},
    {"taps": []},
    {"taps": "nope"},
])
def test_bad_submission_400(client, change):
    r = submit(client, **change)
    assert r.status_code == 400
    assert client.get("/api/profiles").json()["count"] == 0


def test_delete_clears_everything(client):
    submit(client)
    submit(client, avatar="owl")
    assert client.get("/api/profiles").json()["count"] == 2
    assert client.post("/api/delete").json() == {"deleted": 2, "count": 0}
    assert client.get("/api/profiles").json() == {"count": 0, "profiles": []}
    assert client.get("/api/quiz").json()["taken"] == []
    assert submit(client).status_code == 200


def test_profile_keeps_no_raw_answers(client):
    submit(client)
    stored = client.get("/api/profiles").json()["profiles"][0]
    assert "answers" not in stored and "taps" not in stored
