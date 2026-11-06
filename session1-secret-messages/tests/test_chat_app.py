import pytest
from fastapi.testclient import TestClient

from secretmsgs.bus import MemoryBus
from secretmsgs.chat_app import create_chat_app
from tests.fakes import FakeWrapper


@pytest.fixture
def setup():
    bus, wrapper = MemoryBus(), FakeWrapper()
    with TestClient(create_chat_app(bus, wrapper)) as client:
        yield client, bus, wrapper


def test_index_serves_page(setup):
    client, _, _ = setup
    r = client.get("/")
    assert r.status_code == 200
    assert "chat.js" in r.text


def test_message_reaches_other_browser(setup):
    client, bus, _ = setup
    with client.websocket_connect("/ws?me=Alice") as alice, client.websocket_connect("/ws?me=Bob") as bob:
        alice.send_json({"text": "KHOOR", "vpn": False})
        assert bob.receive_json() == {"type": "message", "from": "Alice", "text": "KHOOR", "vpn": False}
        assert not bus.published[-1].startswith(b"vault:")


def test_vpn_message_is_wrapped_on_the_bus(setup):
    client, bus, _ = setup
    with client.websocket_connect("/ws?me=Alice") as alice, client.websocket_connect("/ws?me=Bob") as bob:
        alice.send_json({"text": "KHOOR", "vpn": True})
        assert bob.receive_json() == {"type": "message", "from": "Alice", "text": "KHOOR", "vpn": True}
        assert bus.published[-1].startswith(b"vault:")


def test_vault_down_tells_sender(setup):
    client, bus, wrapper = setup
    wrapper.broken = True
    with client.websocket_connect("/ws?me=Alice") as alice:
        alice.send_json({"text": "KHOOR", "vpn": True, "id": 7})
        assert alice.receive_json() == {"type": "error", "reason": "vpn", "id": 7}
        assert bus.published == []
        alice.send_json({"text": "KHOOR", "vpn": False})
        assert alice.receive_json()["text"] == "KHOOR"
        assert len(bus.published) == 1


def test_blank_message_ignored(setup):
    client, bus, _ = setup
    with client.websocket_connect("/ws?me=Alice") as alice:
        alice.send_json({"text": "   ", "vpn": False})
        alice.send_json({"text": "KHOOR", "vpn": False})
        assert alice.receive_json()["text"] == "KHOOR"
        assert len(bus.published) == 1


def test_name_default_and_cap(setup):
    client, _, _ = setup
    with client.websocket_connect("/ws") as guest:
        guest.send_json({"text": "HI", "vpn": False})
        assert guest.receive_json()["from"] == "Guest"
    with client.websocket_connect("/ws?me=" + "x" * 30) as long:
        long.send_json({"text": "HI", "vpn": False})
        assert long.receive_json()["from"] == "x" * 20


def test_garbage_on_bus_ignored(setup):
    client, bus, _ = setup
    with client.websocket_connect("/ws?me=Bob") as bob:
        client.portal.call(bus.publish, b"\xff")
        client.portal.call(bus.publish, b"vault:v1:not-really")
        client.portal.call(bus.publish, b'{"from": "Alice", "text": "KHOOR"}')
        assert bob.receive_json()["text"] == "KHOOR"
