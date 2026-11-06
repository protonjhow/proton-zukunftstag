from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from secretmsgs.bus import MemoryBus
from secretmsgs.envelope import seal
from secretmsgs.eve import load_wordlist
from secretmsgs.eve_app import create_eve_app

W = load_wordlist(str(Path(__file__).parent.parent / "wordlists" / "en.txt"))


@pytest.fixture
def setup():
    bus = MemoryBus()
    with TestClient(create_eve_app(bus, W)) as client:
        yield client, bus


def test_index_serves_page(setup):
    client, _ = setup
    r = client.get("/")
    assert r.status_code == 200
    assert "eve.js" in r.text


def test_sighting_broadcast(setup):
    client, bus = setup
    with client.websocket_connect("/ws") as tv:
        assert tv.receive_json() == {"type": "history", "sightings": []}
        client.portal.call(bus.publish, seal("Alice", "KHOOR", False, None))
        s = tv.receive_json()
        assert s["type"] == "sighting"
        assert (s["from"], s["shift"], s["guess"], s["locked"]) == ("Alice", 3, "HELLO", False)


def test_locked_sighting(setup):
    client, bus = setup
    with client.websocket_connect("/ws") as tv:
        tv.receive_json()
        client.portal.call(bus.publish, b"vault:v1:abc")
        s = tv.receive_json()
        assert (s["locked"], s["from"], s["guess"]) == (True, None, None)


def test_history_on_connect(setup):
    client, bus = setup
    client.portal.call(bus.publish, seal("Alice", "KHOOR", False, None))
    client.portal.call(bus.publish, b"vault:v1:abc")
    with client.websocket_connect("/ws") as tv:
        h = tv.receive_json()
        assert h["type"] == "history"
        assert [s["raw"] for s in h["sightings"]] == ["KHOOR", "vault:v1:abc"]


def test_history_capped_at_50(setup):
    client, bus = setup
    for i in range(60):
        client.portal.call(bus.publish, seal("Alice", f"msg {i}", False, None))
    with client.websocket_connect("/ws") as tv:
        h = tv.receive_json()["sightings"]
        assert len(h) == 50
        assert h[-1]["raw"] == "msg 59"
