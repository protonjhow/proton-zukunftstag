import base64

from secretmsgs.envelope import VpnUnavailable


class FakeWrapper:
    def __init__(self):
        self.broken = False

    def wrap(self, plaintext: bytes) -> str:
        if self.broken:
            raise VpnUnavailable("fake vault is down")
        return "vault:v1:" + base64.b64encode(plaintext).decode()

    def unwrap(self, ciphertext: str) -> bytes:
        if self.broken:
            raise VpnUnavailable("fake vault is down")
        return base64.b64decode(ciphertext.removeprefix("vault:v1:"))
