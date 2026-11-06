import os

import pytest

from secretmsgs.vault import VaultTransit

pytestmark = [
    pytest.mark.vault,
    pytest.mark.skipif(not os.environ.get("ZT_VAULT_ADDR"), reason="ZT_VAULT_ADDR not set"),
]


def test_vault_roundtrip():
    w = VaultTransit(os.environ["ZT_VAULT_ADDR"], os.environ["ZT_VAULT_TOKEN"])
    ciphertext = w.wrap(b"hi")
    assert ciphertext.startswith("vault:v1:")
    assert w.unwrap(ciphertext) == b"hi"
