def encode(text: str, shift: int) -> str:
    shift %= 26
    out = []
    for ch in text:
        if "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        elif "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)


def decode(text: str, shift: int) -> str:
    return encode(text, -shift)
