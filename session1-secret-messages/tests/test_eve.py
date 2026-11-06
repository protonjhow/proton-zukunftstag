from pathlib import Path

from secretmsgs.caesar import encode
from secretmsgs.envelope import seal
from secretmsgs.eve import Sighting, crack, load_wordlist, peek

W = load_wordlist(str(Path(__file__).parent.parent / "wordlists" / "en.txt"))


def test_crack_finds_setting():
    c = crack(encode("MEET ME AT THE PARK", 7), W)
    assert c.shift == 7
    assert c.plaintext == "MEET ME AT THE PARK"


def test_crack_setting_zero():
    assert crack("hello", W).shift == 0


def test_crack_keeps_case():
    assert crack(encode("Hello friend", 25), W).plaintext == "Hello friend"


def test_crack_returns_none_without_words():
    assert crack("1234 5678", W) is None
    assert crack("", W) is None


def test_sentence_cracks_at_every_setting():
    for s in range(26):
        c = crack(encode("MEET ME AT THE PARK", s), W)
        assert (c.shift, c.plaintext) == (s, "MEET ME AT THE PARK")


def test_name_only_is_not_cracked():
    for s in range(26):
        assert crack(encode("Ella", s), W) is None


def test_short_messages_never_get_a_wrong_setting():
    for text in ["ok", "hi", "no", "Hi Lena"]:
        for s in range(26):
            c = crack(encode(text, s), W)
            assert c is None or c.shift == s, f"{text!r} at {s}: Eve said {c}"


def test_wordlist_drops_two_letter_abbreviations():
    assert {"of", "to", "hi", "ok", "no", "we"} <= W
    assert not {"tp", "uv", "rn", "qr"} & W


def test_wordlist_single_letters():
    assert "a" in W and "i" in W and "b" not in W


def test_peek_plain():
    s = peek(seal("Alice", "KHOOR", False, None), W)
    assert s.locked is False
    assert s.sender == "Alice"
    assert s.crack.shift == 3
    assert s.crack.plaintext == "HELLO"


def test_peek_wrapped():
    assert peek(b"vault:v1:abc", W) == Sighting(True, None, "vault:v1:abc", None)


def test_peek_garbage_is_locked():
    assert peek(b"\xff\xfe", W).locked is True


def test_sighting_to_json():
    assert peek(seal("Alice", "KHOOR", False, None), W).to_json() == {
        "locked": False, "from": "Alice", "raw": "KHOOR", "shift": 3, "guess": "HELLO",
    }
    assert peek(b"vault:v1:abc", W).to_json() == {
        "locked": True, "from": None, "raw": "vault:v1:abc", "shift": None, "guess": None,
    }
