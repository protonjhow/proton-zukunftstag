from secretmsgs.caesar import decode, encode


def test_uppercase():
    assert encode("HELLO", 3) == "KHOOR"


def test_case_kept():
    assert encode("Hello", 3) == "Khoor"


def test_wraps():
    assert encode("XYZ", 3) == "ABC"


def test_non_letters_unchanged():
    assert encode("Grüße 3!", 3) == "Juüßh 3!"


def test_emoji_unchanged():
    assert encode("hi 🙂", 1) == "ij 🙂"


def test_shift_mod_26():
    assert encode("A", 27) == "B"


def test_zero_is_identity():
    assert encode("Meet me", 0) == "Meet me"


def test_decode_inverts_every_setting():
    for s in range(26):
        assert decode(encode("Meet me at 3!", s), s) == "Meet me at 3!"


def test_wrong_dial_is_gibberish():
    assert decode(encode("HELLO", 3), 5) == "FCJJM"
