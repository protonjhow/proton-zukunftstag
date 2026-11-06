# Session 2: The mind reader (demo)

Each kid picks an animal (no names), answers 10 harmless questions, and the
quiz guesses 5 things about them. Then it reveals what it noticed **without
asking**: answers they changed, which question they thought longest about,
what device they're on, when they finished. On the big screen you print
everyone's data cards, then run the delete ceremony.

## Start it

Runs on any Docker host (a laptop in the room, or AWS):

```sh
docker compose up -d --build
```

| Device | Open |
|---|---|
| Each kid's tablet or laptop | `http://<host>:8100/` |
| Big screen | `http://<host>:8100/screen` |
| Printing (facilitator) | `http://<host>:8100/cards` (the "Print data cards" button on the big screen opens it) |
| Advertiser facts | `http://<host>:8100/facts`: the small 💰 in the corner of the big screen opens it, and ← comes back. Print it from Chrome for the session 3 business pack. |

On AWS, open TCP 8100 to the office only.

## How the session runs

1. **Quiz (10 min):** kids pick an animal and answer the questions. One device
   can be shared: "Next player" at the end starts over.
2. **Guesses:** kids tap 👍 or 👎 on each guess and get "3 out of 5 from silly
   questions!".
3. **The twist (5 min):** "But wait, there's more…" reveals the noticed lines
   one at a time.
4. **Data cards (10 min):** on the big screen, *Print data cards* gives 4 cards
   per A4 page. Print them **before** the delete ceremony.
5. **Delete ceremony (5 min):** *Delete everything* (tap twice). The animals
   vanish one by one and the screen ends on "0 profiles. Nothing about you is
   stored any more." The cards page is empty from then on.

**Fallback** (if parents would rather the kids' own answers aren't used): a
Proton staffer takes the quiz as a staged demo profile on the big screen
while the kids watch, and the kids fill in data cards by hand.

## Privacy of the demo itself

- Profiles live **only in memory**. Nothing is written to disk.
- Restarting the container (`docker compose restart`) also wipes everything.
- Only the derived profile is kept (guesses, noticed lines, card), never the
  raw answers or taps.
- The access log is off (`--no-access-log`), so the server logs no quiz traffic.

## Parts

- `mindreader/questions.py`: the 10 questions and 12 animals (preferences only:
  no home, school, family, health, looks or money)
- `mindreader/guesses.py`: the 5 guesses
- `mindreader/noticed.py`: what the quiz noticed without asking
- `mindreader/app.py`, `store.py`: the API and the in-memory store
- Kid-facing text, for translation, lives in four places:
  - `web/strings.en.js`: all the page text (copy to `strings.de.js` and change the imports in `quiz.js`, `screen.js` and `cards.js`)
  - `mindreader/questions.py`: the questions, options and animals
  - `mindreader/guesses.py`: the guess wording
  - `mindreader/noticed.py`: the "noticed" sentences and weekday names
- `web/facts.*`: the advertiser facts page (real, sourced numbers). It fits one 1080p screen and prints on one A4 page. The text is in `strings.en.js` under `facts`.
- `printables/`: the app detective worksheet, the take-home challenge (2 cards per page), Lena's feed, the detective sheet with answer key, the Scratch mind-reader card

## Tests

```sh
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -e '.[dev]'
.venv/bin/pytest
cd rehearsal && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i --no-save playwright-core && node rehearse.js
```

The rehearsal needs Google Chrome and the stack running. It wipes all profiles
at the start.

`node check-facts.js` (in `rehearsal/`) checks only the facts page: the 💰 link,
the 1080p fit, A4 printing and the ← back. It's read-only, so it's safe at any time.
