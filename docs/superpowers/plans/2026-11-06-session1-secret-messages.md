# Session 1 "Secret messages" Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the session 1 demo: a browser chat between two laptops over NATS ("the internet"), Eve on the TV brute-forcing Caesar shifts on everything she sees, and a "VPN" switch that wraps messages with Vault transit so Eve can't read them. Also a printable cipher wheel.

**Architecture:** One Docker Compose stack runs NATS, Vault (dev mode plus a transit key), a `chat` web service and an `eve` web service. It can run on any Docker host, locally or on AWS. Kids open the chat page in a browser. The browser does the Caesar encoding and decoding in JS, so turning the dial re-decodes received messages live. The chat service sends each message to NATS and, if the VPN switch is on, wraps it with Vault transit first. Eve subscribes to the same NATS subject, has no Vault credentials, and pushes what she found to the TV page over a websocket.

**Tech Stack:** Python 3.12, FastAPI + uvicorn, `nats-py`, `hvac`, pytest + pytest-asyncio + httpx. Plain HTML/JS (ES modules, no build step), with `node --test` for JS unit tests. Docker Compose, `nats:2.10`, `hashicorp/vault:1.18`.

**Spec:** `docs/superpowers/specs/2026-11-06-zukunftstag-design.md` (section "Session 1: Secret messages")

**Prior art:** <https://github.com/fatred/exploring-vault/tree/main/transit-demo>. Reuse its transit mount and key names, and its `hvac` encrypt/decrypt pattern (base64-encode the plaintext before `encrypt_data`, base64-decode after `decrypt_data`).

## Global Constraints

- All code lives under `session1-secret-messages/`. Paths below are relative to that directory.
- **Commits:** never run `git commit`. At each commit step, give John the command as a heredoc (`git add <paths>` then `git commit -S -F - <<'EOF' … EOF`). If the folder isn't a git repo yet, ask John to run `git init` first.
- Kids only ever use a browser. No terminal on kid laptops.
- All kid-facing text is in English and lives in one file: `web/strings.en.js`. No kid-facing copy is hard-coded in HTML or other JS files.
- Eve's word list is set by the env var `EVE_WORDLIST` (default `wordlists/en.txt`), so a German list can be swapped in later.
- Caesar works on A–Z and a–z only, keeps upper/lower case, and leaves everything else unchanged (umlauts, ß, digits, spaces, punctuation, emoji). There are 26 wheel settings, 0–25. Shifts are taken mod 26.
- NATS subject: `zukunftstag.chat`. Vault transit mount `transit-nats`, key `demo_key`.
- Eve never gets Vault credentials. Her container has no `VAULT_*` env vars, and `create_eve_app` takes no wrapper.
- Bus payload format: when the VPN is off, a UTF-8 JSON object `{"from": <name>, "text": <caesar text>}`. When the VPN is on, the Vault transit ciphertext string of that JSON (it starts with `vault:`). With the VPN on, even the sender's name is hidden from Eve.

## Review Focus

1. **Vault unavailable while the VPN is on.** The sender sees a kid-friendly error, nothing goes out unwrapped, and the chat service keeps working. (Task 4: `test_vault_down_tells_sender`)
2. **Receiver's dial set differently from the sender's.** The message shows as gibberish, not as an error, and turning the dial fixes it live. (Task 1 JS tests and Task 4 manual check)
3. **Message with no dictionary words** (only names or numbers). Eve shows "couldn't crack it" rather than a confident wrong guess. (Task 3: `test_crack_returns_none_without_words`)
4. **TV page loaded or reloaded mid-session.** Eve shows the recent history, not a blank screen. (Task 5: `test_history_on_connect`)
5. **Garbage on the bus.** Non-JSON bytes or a ciphertext that won't unwrap don't crash chat or Eve. (Task 3: `test_peek_garbage_is_locked`; Task 4: `test_garbage_on_bus_ignored`)

---

### Task 1: Project scaffold + Caesar (Python and JS)

**Files:**
- Create: `pyproject.toml` (package `secretmsgs`; deps `fastapi`, `uvicorn[standard]`, `nats-py`, `hvac`; dev extra `pytest`, `pytest-asyncio`, `httpx`; pytest marker `vault`; `asyncio_mode = "auto"`)
- Create: `secretmsgs/__init__.py`, `secretmsgs/caesar.py`
- Create: `web/caesar.js`
- Test: `tests/test_caesar.py`, `web/caesar.test.js`

**Interfaces:**
- Produces (Python): `encode(text: str, shift: int) -> str`, `decode(text: str, shift: int) -> str`
- Produces (JS, ES module): `export function encode(text, shift)`, `export function decode(text, shift)`

- [ ] **Step 1: Write failing tests.** Use the same vectors in both languages:

```python
def test_uppercase(): assert encode("HELLO", 3) == "KHOOR"
def test_case_kept(): assert encode("Hello", 3) == "Khoor"
def test_wraps(): assert encode("XYZ", 3) == "ABC"
def test_non_letters_unchanged(): assert encode("Grüße 3!", 3) == "Juüßh 3!"
def test_emoji_unchanged(): assert encode("hi 🙂", 1) == "ij 🙂"
def test_shift_mod_26(): assert encode("A", 27) == "B"
def test_zero_is_identity(): assert encode("Meet me", 0) == "Meet me"
def test_decode_inverts_every_setting():
    for s in range(26): assert decode(encode("Meet me at 3!", s), s) == "Meet me at 3!"
def test_wrong_dial_is_gibberish(): assert decode(encode("HELLO", 3), 5) == "FCJJM"
```

`web/caesar.test.js` uses `node:test` and `node:assert/strict` with the same cases.

- [ ] **Step 2: Run, expect FAIL.** Run `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]' && .venv/bin/pytest tests/test_caesar.py -v`, then `node --test web/`. Both should fail because `encode`/`decode` don't exist yet.
- [ ] **Step 3: Implement** `encode`/`decode` in both files. `decode(t, s)` is `encode(t, -s)`.
- [ ] **Step 4: Run both commands again, expect PASS.**
- [ ] **Step 5: Commit.** Hand John the heredoc: `feat(session1): caesar cipher in python and js`.

---

### Task 2: Envelope + Vault transit wrapper ("the VPN")

**Files:**
- Create: `secretmsgs/envelope.py`, `secretmsgs/vault.py`
- Test: `tests/test_envelope.py`, `tests/test_vault.py`, `tests/fakes.py`

**Interfaces:**
- Produces in `envelope.py`:
  - `@dataclass(frozen=True) class Message: sender: str; text: str; vpn: bool`
  - `class VpnUnavailable(Exception)`
  - `class Wrapper(Protocol): def wrap(self, plaintext: bytes) -> str; def unwrap(self, ciphertext: str) -> bytes`
  - `seal(sender: str, text: str, vpn: bool, wrapper: Wrapper | None) -> bytes`
  - `open_(payload: bytes, wrapper: Wrapper | None) -> Message`. Raises `VpnUnavailable` if the payload is wrapped and can't be unwrapped, and `ValueError` if it isn't valid plain JSON.
  - `is_wrapped(payload: bytes) -> bool` (true when the payload starts with `b"vault:"`)
- Produces in `vault.py`: `class VaultTransit(Wrapper)` with `__init__(self, addr: str, token: str, mount: str = "transit-nats", key: str = "demo_key")`. Any `hvac` or connection error is re-raised as `VpnUnavailable`.
- Produces in `tests/fakes.py`: `FakeWrapper` (wrap = `"vault:v1:" + base64(plaintext)`; has a `broken: bool` flag that makes both methods raise `VpnUnavailable`), used by Tasks 4 and 5.

- [ ] **Step 1: Write failing tests** in `tests/test_envelope.py`:
  - `test_plain_seal_is_json`: `json.loads(seal("Alice","KHOOR",False,None)) == {"from":"Alice","text":"KHOOR"}`
  - `test_vpn_seal_hides_everything`: the payload starts with `b"vault:"` and contains neither `b"Alice"` nor `b"KHOOR"`
  - `test_roundtrip_vpn`: `open_(seal("Alice","KHOOR",True,w), w) == Message("Alice","KHOOR",True)`
  - `test_roundtrip_plain`: `open_(...)` gives `vpn=False`
  - `test_vpn_without_wrapper_raises`: `seal(..., True, None)` raises `VpnUnavailable`
  - `test_broken_wrapper_raises`: `seal` and `open_` both raise `VpnUnavailable` when `w.broken = True`

  In `tests/test_vault.py`, add `test_vault_roundtrip`, marked `@pytest.mark.vault` and skipped unless `VAULT_ADDR` is set: `wrap(b"hi")` starts with `"vault:v1:"` and `unwrap(wrap(b"hi")) == b"hi"`.
- [ ] **Step 2: Run `.venv/bin/pytest tests/test_envelope.py -v`, expect FAIL** (import error).
- [ ] **Step 3: Implement** `envelope.py` and `vault.py`. In `VaultTransit`, follow John's `encrypt_string`/`decrypt_string`.
- [ ] **Step 4: Run, expect PASS.** The Vault test is skipped for now and runs in Task 6.
- [ ] **Step 5: Commit.** `feat(session1): message envelope and vault transit vpn`.

---

### Task 3: Eve's cracker

**Files:**
- Create: `secretmsgs/eve.py`, `wordlists/en.txt`
- Test: `tests/test_eve.py`

**Interfaces:**
- Consumes: `caesar.decode`, `envelope.is_wrapped`
- Produces:
  - `load_wordlist(path: str) -> frozenset[str]`: lowercased, one word per line. Drops one-letter entries except `a` and `i`.
  - `@dataclass(frozen=True) class Crack: shift: int; plaintext: str; score: int`
  - `crack(text: str, words: frozenset[str]) -> Crack | None`
  - `@dataclass(frozen=True) class Sighting: locked: bool; sender: str | None; raw: str; crack: Crack | None` with `to_json() -> dict` returning `{"locked", "from", "raw", "shift", "guess"}` (`shift`/`guess` are null when there's no crack)
  - `peek(payload: bytes, words: frozenset[str]) -> Sighting`

**The crack algorithm:**
- For each shift 0–25, decode the text.
- Split the result into lowercase `[a-z]+` tokens.
- Score it as the sum of `len(token)` for each token found in `words`.
- The highest score wins. On a tie, the smallest shift wins.
- If the best score is 0, return `None`.
- `Crack.shift` is the setting the sender used, so decoding with it gives the plaintext.

**Word list:** download `google-10000-english-no-swears.txt` from <https://github.com/first20hours/google-10000-english> into `wordlists/en.txt`. The "no swears" version is deliberate, because this is for kids.

- [ ] **Step 1: Write failing tests** (they use the real `wordlists/en.txt`):
  - `test_crack_finds_setting`: `crack(encode("MEET ME AT THE PARK", 7), W)` gives `shift == 7` and `plaintext == "MEET ME AT THE PARK"`
  - `test_crack_setting_zero`: `crack("hello", W).shift == 0`
  - `test_crack_keeps_case`: `crack(encode("Hello friend", 25), W).plaintext == "Hello friend"`
  - `test_crack_returns_none_without_words`: `crack("1234 5678", W) is None` and `crack("", W) is None`
  - `test_wordlist_single_letters`: `"a" in W and "i" in W and "b" not in W`
  - `test_peek_plain`: `peek(seal("Alice","KHOOR",False,None), W)` gives `locked=False`, `sender="Alice"`, `crack.shift==3`, `crack.plaintext=="HELLO"`
  - `test_peek_wrapped`: `peek(b"vault:v1:abc", W) == Sighting(True, None, "vault:v1:abc", None)`
  - `test_peek_garbage_is_locked`: `peek(b"\xff\xfe", W).locked is True` and nothing is raised
- [ ] **Step 2: Run `.venv/bin/pytest tests/test_eve.py -v`, expect FAIL.**
- [ ] **Step 3: Download the word list and implement `eve.py`.**
- [ ] **Step 4: Run, expect PASS.**
- [ ] **Step 5: Commit.** `feat(session1): eve brute-forces caesar settings`.

---

### Task 4: Bus + chat service + chat page

**Files:**
- Create: `secretmsgs/bus.py`, `secretmsgs/chat_app.py`, `web/chat.html`, `web/chat.js`, `web/strings.en.js`, `web/style.css`
- Test: `tests/test_chat_app.py`

**Interfaces:**
- Consumes: `envelope.seal/open_/VpnUnavailable/Wrapper`, `tests/fakes.FakeWrapper`
- Produces in `bus.py`:
  - `Handler = Callable[[bytes], Awaitable[None]]`
  - `class Bus(Protocol)`: `async start()`, `async stop()`, `async publish(data: bytes)`, `subscribe(handler: Handler)`
  - `NatsBus(url: str, subject: str = "zukunftstag.chat")`
  - `MemoryBus()`: calls handlers directly and records `published: list[bytes]`
- Produces in `chat_app.py`: `create_chat_app(bus: Bus, wrapper: Wrapper | None) -> FastAPI`. The module-level `app` is built from the env vars `NATS_URL` (default `nats://localhost:4222`), `VAULT_ADDR` and `VAULT_TOKEN`. When the Vault vars are unset, `wrapper` is `None`.
  - Static files: `GET /` serves `web/chat.html`, and `web/` is mounted at `/static`.
  - `WS /ws?me=<name>`. The name is trimmed and capped at 20 characters, defaulting to `"Guest"`.
  - Browser to server: `{"text": str, "vpn": bool}`. `text` is already Caesar-encoded, and blank text is ignored.
  - Server to every connected browser, for every readable bus message: `{"type":"message","from":str,"text":str,"vpn":bool}`.
  - Server to the sender only, when sealing fails: `{"type":"error","reason":"vpn"}`.
  - Bus messages that raise in `open_` are logged and skipped.
- Produces in `strings.en.js`: `export default { chat: {...}, eve: {...} }` holding all kid-facing copy for both pages. Task 5 fills in `eve`.

- [ ] **Step 1: Write failing tests** using `TestClient`, `MemoryBus` and `FakeWrapper`:
  - `test_index_serves_page`: `GET /` returns 200 and the body contains `chat.js`
  - `test_message_reaches_other_browser`: Alice sends `{"text":"KHOOR","vpn":false}`, and Bob receives `{"type":"message","from":"Alice","text":"KHOOR","vpn":false}`
  - `test_vpn_message_is_wrapped_on_the_bus`: with `vpn: true`, `bus.published[-1]` starts with `b"vault:"`, and Bob receives `text "KHOOR"` with `vpn true`
  - `test_vault_down_tells_sender`: with `wrapper.broken = True`, Alice gets `{"type":"error","reason":"vpn"}` and `bus.published == []`. A following `vpn:false` message still goes through.
  - `test_blank_message_ignored`: `{"text":"   ","vpn":false}` publishes nothing
  - `test_name_default_and_cap`: no `me` gives `"Guest"`, and `me` set to 30 × `"x"` is cut to 20 characters
  - `test_garbage_on_bus_ignored`: publishing `b"\xff"` straight to the bus sends nothing to browsers, and a following valid message still arrives
- [ ] **Step 2: Run `.venv/bin/pytest tests/test_chat_app.py -v`, expect FAIL.**
- [ ] **Step 3: Implement `bus.py` and `chat_app.py`.**
- [ ] **Step 4: Run, expect PASS.**
- [ ] **Step 5: Build the chat page** (`chat.html`, `chat.js`, `style.css`, `strings.en.js`). It's big and friendly, laid out for a laptop screen, with all copy taken from `strings.en.js`:
  - A header with the kid's name from `?me=`.
  - A text box and a send button. Enter also sends.
  - A **wheel dial** for settings 0–25. It shows the mapping as on the paper wheel, e.g. `A → D` at setting 3.
  - A big **VPN switch** that is clearly on or off.
  - A conversation list:
    - Sent messages show what the kid typed plus "sent as KHOOR".
    - Received messages are shown decoded with the *current* dial, and **re-decode live when the dial moves**.
    - Messages that arrived via the VPN get a lock badge.
    - Incoming messages whose `from` equals your own name are ignored (you already echo your own sends locally).
  - On `{"type":"error"}`, show the VPN error copy, e.g. "The VPN isn't working, your message wasn't sent".
- [ ] **Step 6: Manual check.** Run NATS with `docker run --rm -p 4222:4222 nats:2.10`, then `.venv/bin/uvicorn secretmsgs.chat_app:app --port 8000`. Open `/?me=Alice` and `/?me=Bob` in two windows.
  - Send at setting 3 from Alice. Bob at setting 3 reads the message; at setting 5, gibberish. Moving Bob's dial back to 3 fixes it live.
  - Turn on the VPN with Vault unset: Alice sees the error message.
- [ ] **Step 7: Commit.** `feat(session1): chat service and page`.

---

### Task 5: Eve service + TV page

**Files:**
- Create: `secretmsgs/eve_app.py`, `web/eve.html`, `web/eve.js`
- Modify: `web/strings.en.js` (fill in `eve`)
- Test: `tests/test_eve_app.py`

**Interfaces:**
- Consumes: `bus.Bus/MemoryBus`, `eve.peek/load_wordlist/Sighting.to_json`
- Produces: `create_eve_app(bus: Bus, words: frozenset[str]) -> FastAPI`. The module-level `app` is built from `NATS_URL` and `EVE_WORDLIST`.
  - `GET /` serves `web/eve.html`.
  - `WS /ws`: on connect, sends `{"type":"history","sightings":[...]}` (the last 50, oldest first). After that, it sends `{"type":"sighting", ...Sighting.to_json()}` for each bus message.

- [ ] **Step 1: Write failing tests:**
  - `test_sighting_broadcast`: after publishing `seal("Alice","KHOOR",False,None)`, the socket receives a sighting with `from "Alice"`, `shift 3`, `guess "HELLO"` and `locked false`
  - `test_locked_sighting`: publishing `b"vault:v1:abc"` gives `locked true`, `from null` and `guess null`
  - `test_history_on_connect`: publish 2 messages *before* connecting; the first frame is `history` with 2 sightings in order
  - `test_history_capped_at_50`: publish 60 messages; history has 50, ending with the latest
- [ ] **Step 2: Run `.venv/bin/pytest tests/test_eve_app.py -v`, expect FAIL.**
- [ ] **Step 3: Implement `eve_app.py`.**
- [ ] **Step 4: Run, expect PASS.**
- [ ] **Step 5: Build the TV page.** It must be readable from across a conference room: very large type, high contrast, newest at the top, and a clear "Eve" identity (e.g. a spy persona). Each sighting card shows:
  - **Cracked:** "From: Alice", "I saw: KHOOR", "Wheel setting: 3", "I think you said: HELLO". At setting 0, add a "you didn't even lock it!" line.
  - **No crack** (`guess` null, not locked): "I saw: …" and "I couldn't crack this one".
  - **Locked:** "From: ???", "I saw: vault:v1:8SDd…" (truncated), "I tried all 26 settings… I can't read this!"

  Animating through the 26 settings is left to the builder. All copy comes from `strings.en.js`.
- [ ] **Step 6: Manual check.** With Task 4's setup running, also start `.venv/bin/uvicorn secretmsgs.eve_app:app --port 8001` and open `http://localhost:8001`. Messages from Alice show up cracked with the right setting, and reloading the page keeps the history.
- [ ] **Step 7: Commit.** `feat(session1): eve tv page`.

---

### Task 6: Compose stack + full run-through

**Files:**
- Create: `Dockerfile` (python:3.12-slim, installs the package and copies `web/` and `wordlists/`), `docker-compose.yml`, `vault/init.sh`, `README.md`

**Interfaces:**
- Consumes: `secretmsgs.chat_app:app`, `secretmsgs.eve_app:app`
- Produces these compose services:
  - `nats` (`nats:2.10`, internal only)
  - `vault`: `hashicorp/vault:1.18` in dev mode with `VAULT_DEV_ROOT_TOKEN_ID=zukunftstag-root`, port 8200 published on `127.0.0.1` only (for the Vault test)
  - `vault-init`: one-shot; it runs `vault/init.sh`, which enables transit at `transit-nats` and creates key `demo_key`, and doesn't fail if they already exist
  - `chat`: port 8000, with env `NATS_URL`, `VAULT_ADDR` and `VAULT_TOKEN`; it starts after `vault-init` completes successfully
  - `eve`: port 8001, with env `NATS_URL` and `EVE_WORDLIST` only, and **no `VAULT_*` vars**

- [ ] **Step 1: Write the files.** In `README.md`, explain how to start the stack, which URLs to open on which device (`http://<host>:8000/?me=<name>` on each kid laptop, `http://<host>:8001` on the TV), and that it runs the same locally or on an AWS host.
- [ ] **Step 2: Start the stack.** Run `docker compose up -d --build`. `docker compose ps` should show `nats`, `vault`, `chat` and `eve` running, and `vault-init` exited with code 0.
- [ ] **Step 3: Run the Vault test.** Run `VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN=zukunftstag-root .venv/bin/pytest -m vault -v`. Expect `test_vault_roundtrip` PASSED.
- [ ] **Step 4: Rehearse the session** with two browsers and the TV page:
  1. Alice sends at setting 7. Eve shows "Wheel setting: 7" and the right message.
  2. Bob at the wrong setting sees gibberish, then turns his dial and reads it.
  3. Alice turns on the VPN. Bob still reads her messages, while Eve shows "From: ???" and can't read them.
  4. Run `docker compose stop vault`. Alice sends with the VPN on and sees the error message. Then run `docker compose start vault`.
  5. Run `docker compose down && docker compose up -d` and confirm that VPN messages work again (dev Vault forgets the key, and `vault-init` recreates it).
- [ ] **Step 5: Commit.** `feat(session1): compose stack and runbook`.

---

### Task 7: Printable cipher wheel

**Files:**
- Create: `printables/cipher-wheel.html`

**Interfaces:** none (standalone printable).

- [ ] **Step 1: Build an A4 printable page.**
  - Use inline SVG to draw two discs, each split into 26 equal segments with A–Z clockwise:
    - an outer disc of about 180 mm, labelled "plain";
    - an inner disc of about 130 mm, labelled "secret", with a small arrow at A to read the wheel setting.
  - Mark the centres for a split pin.
  - Add a title ("Secret Message Wheel") and three-line assembly instructions (cut out, pin, turn).
  - Keep all text in one `const TEXT = {...}` block at the top for translation. Leave the styling plain so design can rebrand it later.
- [ ] **Step 2: Check it.** In the browser, print preview at 100% on A4: both discs fit and the letters are legible. Print one, assemble it, and confirm that at setting 3 the plain H lines up with the secret K, matching `encode("H", 3) == "K"`.
- [ ] **Step 3: Commit.** `feat(session1): printable cipher wheel`.
