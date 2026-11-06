import base64

import hvac

from secretmsgs.envelope import VpnUnavailable


class VaultTransit:
    """The "VPN": wraps a message with Vault transit before it leaves, unwraps it on arrival."""

    def __init__(self, addr: str, token: str, mount: str = "transit-nats", key: str = "demo_key"):
        self._client = hvac.Client(url=addr, token=token, timeout=3)
        self._mount = mount
        self._key = key

    def wrap(self, plaintext: bytes) -> str:
        try:
            resp = self._client.secrets.transit.encrypt_data(
                name=self._key,
                mount_point=self._mount,
                plaintext=base64.b64encode(plaintext).decode(),
            )
            return resp["data"]["ciphertext"]
        except Exception as e:
            raise VpnUnavailable(str(e)) from e

    def unwrap(self, ciphertext: str) -> bytes:
        try:
            resp = self._client.secrets.transit.decrypt_data(
                name=self._key, mount_point=self._mount, ciphertext=ciphertext
            )
            return base64.b64decode(resp["data"]["plaintext"])
        except Exception as e:
            raise VpnUnavailable(str(e)) from e
