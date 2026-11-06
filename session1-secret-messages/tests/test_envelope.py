import json

import pytest

from secretmsgs.envelope import Message, VpnUnavailable, open_, seal
from tests.fakes import FakeWrapper


def test_plain_seal_is_json():
    assert json.loads(seal("Alice", "KHOOR", False, None)) == {"from": "Alice", "text": "KHOOR"}


def test_vpn_seal_hides_everything():
    payload = seal("Alice", "KHOOR", True, FakeWrapper())
    assert payload.startswith(b"vault:")
    assert b"Alice" not in payload
    assert b"KHOOR" not in payload


def test_roundtrip_vpn():
    w = FakeWrapper()
    assert open_(seal("Alice", "KHOOR", True, w), w) == Message("Alice", "KHOOR", True)


def test_roundtrip_plain():
    assert open_(seal("Alice", "KHOOR", False, None), None) == Message("Alice", "KHOOR", False)


def test_vpn_without_wrapper_raises():
    with pytest.raises(VpnUnavailable):
        seal("Alice", "KHOOR", True, None)


def test_broken_wrapper_raises():
    w = FakeWrapper()
    payload = seal("Alice", "KHOOR", True, w)
    w.broken = True
    with pytest.raises(VpnUnavailable):
        seal("Alice", "KHOOR", True, w)
    with pytest.raises(VpnUnavailable):
        open_(payload, w)
