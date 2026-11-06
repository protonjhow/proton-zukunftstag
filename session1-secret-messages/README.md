# Session 1: Secret messages (demo)

Kids chat between two laptops. Every message crosses "the internet" (NATS), where
**Eve** (the TV) listens and tries all 26 Caesar wheel settings on it. Turn on
the **VPN** (Vault transit wraps the message before it leaves and unwraps it on
arrival) and Eve can't read anything, not even who sent it.

## Start it

Any Docker host works: a laptop in the room, or a server on AWS.

```sh
docker compose up -d --build
docker compose ps          # nats, chat, eve running; vault healthy
```

| Device | Open |
|---|---|
| Kid laptop 1 | `http://<host>:8000/?me=Alice` |
| Kid laptop 2 | `http://<host>:8000/?me=Bob` |
| Conference room TV | `http://<host>:8001` (full screen) |

Use the kids' own names in `?me=` (max 20 characters). Every laptop needs a
**different** name, because a page hides messages sent under its own name.

On AWS, open TCP 8000 and 8001 to the office only. Vault (8200) is bound to
localhost and NATS isn't published at all.

## How the session runs

1. Both kids pick the same **wheel setting** as their paper wheels and chat.
   Eve cracks every message on the TV and shows the setting she found.
2. If a kid's dial doesn't match, the message looks like gibberish. Turning
   the dial re-decodes it live.
3. Flip the **VPN** switch: the friend still reads the message, Eve shows
   `From: ???` and "I can't read this!".

Resetting between groups: `docker compose restart eve` clears Eve's history.

## Parts

- `secretmsgs/caesar.py`, `web/caesar.js`: the wheel (A–Z only, everything else unchanged)
- `secretmsgs/envelope.py`: what goes on the wire (plain JSON, or `vault:v1:…` with the VPN on)
- `secretmsgs/vault.py`: the "VPN" (Vault transit, mount `transit-nats`, key `demo_key`)
- `secretmsgs/eve.py`, `eve_app.py`: Eve. She only ever sees NATS and has no Vault settings.
- `secretmsgs/chat_app.py`: the chat service
- `web/strings.en.js`: **all kid-facing text**. Translate by copying to `strings.de.js` and changing the imports in `chat.js` and `eve.js`.
- `wordlists/en.txt`: Eve's dictionary ([google-10000-english, no swears](https://github.com/first20hours/google-10000-english)). For German, add `wordlists/de.txt` and set `EVE_WORDLIST` in `docker-compose.yml`.
- `printables/cipher-wheel.html`: paper wheel to print on A4

## Tests

```sh
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -e '.[dev]'
.venv/bin/pytest                      # unit tests
node --test web/                      # caesar.js
ZT_VAULT_ADDR=http://127.0.0.1:8200 ZT_VAULT_TOKEN=zukunftstag-root .venv/bin/pytest -m vault   # against the running stack
```

The demo reads `ZT_VAULT_*`, not `VAULT_*`, so it never picks up a real Vault from your shell.

Full rehearsal in headless Chrome (needs Google Chrome installed and the stack
running; it stops and restarts Vault once):

```sh
cd rehearsal && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i --no-save playwright-core && node rehearse.js
```
