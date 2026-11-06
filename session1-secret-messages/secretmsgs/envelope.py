import json
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Message:
    sender: str
    text: str
    vpn: bool


class VpnUnavailable(Exception):
    pass


class Wrapper(Protocol):
    def wrap(self, plaintext: bytes) -> str: ...

    def unwrap(self, ciphertext: str) -> bytes: ...


def is_wrapped(payload: bytes) -> bool:
    return payload.startswith(b"vault:")


def seal(sender: str, text: str, vpn: bool, wrapper: Wrapper | None) -> bytes:
    body = json.dumps({"from": sender, "text": text}).encode()
    if not vpn:
        return body
    if wrapper is None:
        raise VpnUnavailable("no VPN configured")
    return wrapper.wrap(body).encode()


def open_(payload: bytes, wrapper: Wrapper | None) -> Message:
    vpn = is_wrapped(payload)
    if vpn:
        if wrapper is None:
            raise VpnUnavailable("no VPN configured")
        payload = wrapper.unwrap(payload.decode())
    try:
        data = json.loads(payload)
        return Message(str(data["from"]), str(data["text"]), vpn)
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as e:
        raise ValueError(f"not a chat message: {e}") from e
