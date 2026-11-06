# Session 2 "The mind reader" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the session 2 materials:
- a browser quiz that guesses harmless things about each kid, then reveals what it noticed without asking;
- a big-screen page for the delete ceremony;
- printable data cards;
- Lena's fake social feed with a detective worksheet;
- a Scratch "mind reader" free-play card.

**Architecture:** One FastAPI service keeps quiz results **in memory only**. Nothing is written to disk, and answers are never logged. Kids open the quiz page on any device. The browser records every tap with a timestamp, and the server turns the answers and those raw tap events into guesses and "things I noticed". The facilitator's screen page lists who has finished, prints the cards, and runs the delete ceremony, which clears memory. The printables are standalone HTML pages for A4 printing, in the same style as session 1's cipher wheel. The service runs from a small Docker Compose file, locally or on AWS.

**Tech Stack:** Python 3.12, FastAPI + uvicorn, pytest + httpx2, plain HTML/JS (ES modules), Docker Compose.

**Spec:** `docs/superpowers/specs/2026-11-06-zukunftstag-design.md` (section "Session 2: The mind reader")

> **As built (6 November):**
> - The fictional town is **Zipfelbühl**, not Glitzerbach (a real Glitzerbach stream exists in canton Bern).
> - Lena's "home alone" post is at Tuesday 17:20.
> - The guesses avoid the word "school".
> - When a kid's animal is taken at submit time, her answers are kept.
> - All printables force print colours.
> - Added on John's request: **App detective** (`printables/app-detective.html`). Kids read App Store privacy labels on a Proton tablet, plus a take-home card (`printables/take-home-challenge.html`) for checking app permissions with a grown-up. The Lena game shrinks to 15 min.
> - Data cards: the portrait scales to fit, so long titles can't push the footer out of the card.
> - Added on John's request: an **advertiser facts** page with real, sourced figures on what users are worth to advertisers by region, age, job and data type, plus the rules for minors.
>   - It's served at `/facts` and opened from a low-key 💰 on the big screen.
>   - It fits one 1080p screen and prints on one A4 page as the kids' takeaway, which goes in their session 3 business pack.
>   - Its text lives in `strings.en.js` under `facts`, and it's checked by `rehearsal/check-facts.js`.

## Global Constraints

- All code lives under `session2-mind-reader/`. Paths below are relative to it.
- **Commits:** never run `git commit`. Work on branch `sessions-2-3`, and at the end hand John signed-commit heredocs.
- Kids only use a browser. All kid-facing text is in English and lives in `web/strings.en.js` (for the app) or a `const TEXT = {…}` block at the top of each printable.
- **Nothing overly personal.** Questions and guesses stay at the level of preferences and habits. There must never be a question or guess about home, location, school, route to school, family or siblings, health, relationships, appearance or money.
- **No names.** A kid is identified only by an animal avatar picked from a fixed list. Each avatar can be used by only one kid at a time.
- **Data stays in memory.** Nothing is written to disk and no answers appear in logs. Delete clears everything, and restarting the service clears everything too.
- Lena is fictional, and so are her school, town and street. Clues are framed as "look how much we figured out", followed by "how could Lena post the same moment more safely". They are never framed as danger.
- Times are shown in the `Europe/Zurich` timezone.

## Review Focus

1. **A kid reloads the quiz mid-way, or two kids pick the same avatar.** There's no crash: the second kid is told the avatar is taken, and a reload starts over. (Task 3: `test_avatar_taken_returns_409`)
2. **Malformed submissions** (an unknown question or option, missing answers, events out of order). The server rejects them with 400 and never crashes. (Task 3: `test_bad_submission_400`)
3. **After the delete ceremony**, every API that returns profile data comes back empty, avatars are free again, and printed cards can't be re-rendered. (Task 3: `test_delete_clears_everything`)
4. **Kids who never change an answer, or answer instantly.** The "noticed" lines still read naturally and never say "0 times". (Task 2: `test_noticed_when_never_changed`)
5. **An iPad that identifies itself as a Mac.** The device line still says "an iPad". (Task 2: `test_ipad_desktop_mode`)

---

### Task 1: Questions and guesses

**Files:**
- Create: `pyproject.toml` (package `mindreader`; deps `fastapi`, `uvicorn[standard]`; dev extra `pytest`, `httpx2`; pytest `pythonpath = ["."]`)
- Create: `mindreader/__init__.py`, `mindreader/questions.py`, `mindreader/guesses.py`
- Test: `tests/__init__.py`, `tests/test_questions.py`, `tests/test_guesses.py`

**Interfaces:**
- Produces in `questions.py`:
  - `@dataclass(frozen=True) class Option: key: str; label: str; emoji: str`
  - `@dataclass(frozen=True) class Question: key: str; prompt: str; options: tuple[Option, ...]`
  - `QUESTIONS: tuple[Question, ...]`
  - `AVATARS: tuple[tuple[str, str], ...]` (key and emoji, e.g. `("fox", "🦊")`)
  - `def to_json() -> dict` returning `{"questions": [...], "avatars": [...]}` for the page
- Produces in `guesses.py`: `make_guesses(answers: dict[str, str]) -> list[dict]`. It returns exactly 5 guesses, each shaped `{"label": str, "value": str}`, in a fixed order: best time to notify you, videos we'd recommend, an ad you'd probably click, your type, your weekend.

**Exact content (10 questions × 4 options, keys in brackets):**

| key | prompt | options |
|---|---|---|
| pet | Cat or dog? | cat 🐱, dog 🐶, both 🐾, neither 🦎 |
| snack | Pick a snack | chips 🥔, fruit 🍎, chocolate 🍫, popcorn 🍿 |
| clock | Early bird or night owl? | early 🌅, night 🦉, depends 🤷, sleepy 😴 |
| game | Which would you rather play? | minecraft ⛏️, roblox 🧱, mariokart 🏎️, board 🎲 |
| video | Which video would you click? | animals 🐹, gaming 🎮, music 🎵, crafts ✂️ |
| power | Pick a superpower | fly 🦅, invisible 👻, animals 🗣️, time ⏳ |
| weekend | Saturday morning, first thing? | sleep 🛌, outside ⚽, screens 📱, read 📚 |
| emoji | Pick an emoji | laugh 😂, love 🥰, cool 😎, think 🤔 |
| season | Favourite season | spring 🌷, summer ☀️, autumn 🍂, winter ❄️ |
| colour | Pick a colour | purple 🟣, blue 🔵, green 🟢, orange 🟠 |

**Avatars (12):** fox 🦊, panda 🐼, frog 🐸, owl 🦉, octopus 🐙, unicorn 🦄, tiger 🐯, penguin 🐧, koala 🐨, lion 🦁, turtle 🐢, bee 🐝.

**Guess rules (deterministic):**
- **Notify:** `clock` early gives "Early in the morning, around 7:00". Night gives "In the evening, after 20:00". Depends and sleepy give "In the afternoon, around 16:00".
- **Videos:** a map from `video`. If `pet` isn't neither, append " and cute pet clips".
- **Ad:**
  - Game part: minecraft "a Minecraft skin pack", roblox "Robux", mariokart "a new Mario game", board "a new board game".
  - Snack part: " (and a <snack> advert)". Chips/popcorn/chocolate/fruit are worded naturally, e.g. "a chocolate advert".
- **Type:**
  - Emoji gives the noun: laugh "Joker", love "Friend-Maker", cool "Adventurer", think "Thinker".
  - Superpower gives the adjective: fly "High-Flying", invisible "Mysterious", animals "Wild", time "Curious".
  - Result: "The <adjective> <noun>".
- **Weekend:** a map from `weekend`. If `clock` is night and weekend is sleep, it's "Sleeping in, because you stayed up late".

- [ ] **Step 1: Write failing tests.**
  - `test_ten_questions_four_options`: 10 questions, each with 4 options, and unique keys.
  - `test_no_personal_topics`: no prompt or label contains any of `school, home, live, address, street, mum, mom, dad, brother, sister, sibling, family, money, phone number, birthday, boyfriend, girlfriend, weight`.
  - `test_twelve_unique_avatars`.
  - `test_guesses_exact`: for `{pet: dog, snack: chocolate, clock: night, game: minecraft, video: gaming, power: fly, weekend: sleep, emoji: cool, …}`, the result equals the full expected list of 5 `{label, value}` dicts. The type is "The High-Flying Adventurer" and the weekend is "Sleeping in, because you stayed up late".
  - `test_guesses_never_personal`: for every combination of `clock × game × weekend × emoji × power × video`, no value contains the banned words.
- [ ] **Step 2: Run `.venv/bin/pytest -q`, expect FAIL** (import error).
- [ ] **Step 3: Implement** `questions.py` and `guesses.py`.
- [ ] **Step 4: Run, expect PASS.**

---

### Task 2: "What I noticed without asking"

**Files:**
- Create: `mindreader/noticed.py`
- Test: `tests/test_noticed.py`

**Interfaces:**
- Consumes: `QUESTIONS` (to turn a question key into its prompt)
- Produces:
  - `@dataclass(frozen=True) class Tap: q: str; option: str; t: int`, where `t` is milliseconds since the quiz started. The `Tap` list is what the browser sends: one entry per tap, including re-taps.
  - `describe_device(user_agent: str, touch: bool) -> str`
  - `noticed(taps: list[Tap], device: str, finished_at: datetime) -> list[str]` returning 5 lines in a fixed order: changes, slowest, fastest, device, when.

**Rules:**
- **Per question:**
  - Time spent is the time of the last tap on that question minus the time of the last tap on the previous question. For the first question it's measured from 0.
  - Changes is the number of taps on that question minus 1.
- **Changes line:**
  - Find the question with the most changes, picking the first one on a tie.
  - If that's more than 0: "You changed your answer to “<prompt>” <n> time(s)". Use "time" for 1 and "times" for more.
  - Otherwise: "You never changed an answer. Very decisive!"
- **Slowest line:** "You thought longest about “<prompt>” (<s> seconds)", with seconds rounded to a whole number and at least 1.
- **Fastest line:** "You answered “<prompt>” in <s> seconds". Use one decimal place, or "under a second" when it's less than 1.0 s.
- **Device line:** "You're using <describe_device>".
  - "an iPad" if the UA contains `iPad`, or contains `Macintosh` while `touch` is true.
  - Otherwise "an iPhone", "an Android tablet or phone", "a Chromebook" (`CrOS`), "a Mac", "a Windows computer" or "a Linux computer", checked in that order.
  - Fallback: "a computer".
- **When line:** "You finished at <HH:MM> on a <Weekday>, after <m> min <s> s". Use Zurich local time, and drop "<m> min" when m is 0. The duration is the time of the last tap.

- [ ] **Step 1: Write failing tests.**
  - `test_changes_and_timing`: given hand-built taps where `snack` is tapped 3 times and `power` takes 9.4 s, the lines are "You changed your answer to “Pick a snack” 2 times" and "You thought longest about “Pick a superpower” (9 seconds)".
  - `test_noticed_when_never_changed`: exactly 10 taps, so the line is "You never changed an answer. Very decisive!" and no line contains " 0 time".
  - `test_fastest_under_a_second`.
  - `test_ipad_desktop_mode`: a Macintosh UA with `touch=True` gives "an iPad".
  - `test_device_table`: one parametrized case per device string.
  - `test_when_line`: `datetime(2026, 11, 12, 10, 42, tzinfo=UTC)` and a last tap at 72_000 ms give "You finished at 11:42 on a Thursday, after 1 min 12 s".
- [ ] **Step 2: Run, expect FAIL.**
- [ ] **Step 3: Implement `noticed.py`.**
- [ ] **Step 4: Run, expect PASS.**

---

### Task 3: In-memory store + API

**Files:**
- Create: `mindreader/store.py`, `mindreader/app.py`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: `questions.to_json/QUESTIONS/AVATARS`, `guesses.make_guesses`, `noticed.Tap/noticed/describe_device`
- Produces:
  - `class Store`: `taken() -> set[str]`, `add(avatar: str, profile: dict) -> None` (raises `AvatarTaken`), `all() -> list[dict]`, `count() -> int`, `clear() -> int` (returns how many were removed).
  - `create_app(store: Store, now: Callable[[], datetime]) -> FastAPI`. The module-level `app` uses `Store()` and the current UTC time.
- Routes:
  - `GET /` serves `web/quiz.html`, `GET /screen` serves `web/screen.html` and `GET /cards` serves `web/cards.html`. `/static` serves `web/`.
  - `GET /api/quiz` returns `questions.to_json()` plus `"taken": [...]`.
  - `POST /api/submit` takes `{"avatar": str, "answers": {q: option}, "taps": [{"q","option","t"}], "touch": bool}`.
    - It returns the profile `{"avatar", "emoji", "guesses": [...], "noticed": [...], "card": {...}}`.
    - It reads the user agent from the request header.
    - Errors: 400 for an unknown avatar, question or option, for answers that don't cover all 10 questions, or for taps whose `t` isn't non-decreasing. 409 if the avatar is taken.
  - `GET /api/profiles` returns `{"count": n, "profiles": [...]}` (the screen and cards pages use it).
  - `POST /api/delete` returns `{"deleted": n, "count": 0}`.
- `card` contains:
  - `title` (the type guess), `emoji`, `avatar`;
  - `interests` (the labels of the game, video and snack answers);
  - `notify` (the notify guess) and `ad` (the ad guess);
  - `stars`, from 1 to 5: 3, plus 1 if the game is minecraft or roblox, plus 1 if the weekend is screens.

  Only the card needs these; the full answers are not kept. The store holds just the profile dict.

- [ ] **Step 1: Write failing tests** (TestClient, with `now` fixed):
  - `test_index_and_pages_serve`: `/`, `/screen` and `/cards` all return 200.
  - `test_quiz_lists_questions_and_taken`.
  - `test_submit_returns_profile`: 5 guesses, 5 noticed lines and a card whose stars are in 1..5. The device line for an iPhone UA says "an iPhone".
  - `test_avatar_taken_returns_409`, and after that `/api/quiz` lists the avatar as taken.
  - `test_bad_submission_400`: parametrized over an unknown avatar, an unknown option, a missing answer and taps with a decreasing `t`.
  - `test_delete_clears_everything`: after a submit, `/api/delete` gives `deleted == 1`, `/api/profiles` gives `count == 0` and an empty list, and the avatar can be used again.
  - `test_profile_keeps_no_raw_answers`: the stored profile has no `answers` or `taps` key.
- [ ] **Step 2: Run, expect FAIL.**
- [ ] **Step 3: Implement `store.py` and `app.py`.** Log nothing from request bodies.
- [ ] **Step 4: Run, expect PASS.**

---

### Task 4: Quiz page, screen page, cards page

**Files:**
- Create: `web/quiz.html`, `web/quiz.js`, `web/screen.html`, `web/screen.js`, `web/cards.html`, `web/cards.js`, `web/strings.en.js`, `web/style.css`

**Interfaces:** Consumes the Task 3 routes. All copy comes from `strings.en.js`.

**Quiz page (kid device)**
1. **Pick your animal:** a grid of avatars, with taken ones greyed out. There is no name field.
2. **Questions:** one at a time with big tap targets.
   - Tapping an option selects it, and tapping another option changes it. Every tap is recorded as `{q, option, t}`, with `t` taken from `performance.now()` relative to when the first question appeared.
   - A **Next** button moves on and is enabled once something is selected.
   - A progress indicator shows "3 / 10".
3. **"I think I know you…"** shows the 5 guesses as cards, each with a 👍 / 👎 the kid can tap. The page counts right guesses, then shows the spec's line ("3 out of 5 from silly questions!"). The thumbs stay in the browser and are not sent.
4. **"…and here's what I noticed without asking"** reveals the noticed lines one at a time on a button tap, for drama.

Details:
- A 409 response sends the kid back to the avatar step with the message "Someone just took that animal, pick another!".
- If the network fails, the page shows a retry button.

**Screen page (facilitator, big screen)**
- A title.
- A grid of finished avatars, refreshed by polling `/api/profiles` every 2 s.
- The count, worded "N profiles stored on this computer".
- A "Print data cards" link to `/cards`.
- A big **Delete everything** button with a two-step confirm. It runs a short animation that removes the avatars one by one, calls `/api/delete`, then shows "0 profiles. Nothing about you is stored any more."

**Cards page (print)**
- Four cards per A4 page (2 × 2, each about 95 × 135 mm).
- Pokémon-style layout: the avatar emoji large, the title, interests, "Best time to reach you", "Ad you'd see", an "advertiser value" star bar, and a footer line from strings ("This is what companies collect and sell").
- Includes `@page { size: A4; margin: 8mm }`.
- With no profiles, it shows "No cards. Everything has been deleted."

- [ ] **Step 1: Build the pages.**
- [ ] **Step 2: Browser check** (headless Chrome, `rehearsal/rehearse.js`, in the same style as session 1). With the service running:
  - Two kid contexts (an iPad viewport and a laptop) each complete the quiz, and one of them changes an answer twice.
  - Both see 5 guesses and 5 noticed lines, and the iPad context's device line says "an iPad". Simulate this with an iPad UA.
  - A second kid trying the same avatar gets the "taken" message.
  - The screen shows 2 profiles, and the cards page renders 2 cards on 1 PDF page.
  - Delete leaves the screen at 0, and the cards page shows the "deleted" message.
  - There are no console errors.

  Then look at the screenshots.
- [ ] **Step 3: Commit** (heredoc at the end).

---

### Task 5: Compose + README

**Files:**
- Create: `Dockerfile`, `.dockerignore`, `docker-compose.yml` (service `mindreader` on port 8100), `README.md`

- [ ] **Step 1: Write the files.** The README covers which URL to open on which device (`/` for kids, `/screen` on the big screen), printing cards before the ceremony, the fallback from the spec (a Proton staffer plays a staged demo profile), and that data lives only in memory.
- [ ] **Step 2: Run `docker compose up -d --build`, then the rehearsal against `http://127.0.0.1:8100`.** Expect all PASS.

---

### Task 6: Lena's feed, detective sheet, Scratch card

**Files:**
- Create: `printables/lena-feed.html`, `printables/detective-sheet.html`, `printables/scratch-mind-reader.html`

**Lena's feed:** 8 post cards across 2 A4 pages, as fake social posts by **@lena.loves.biscuit**, 11. Each post has a drawn "photo" (CSS/emoji scene, never a real photo), a caption, a timestamp, a location tag where relevant, likes, and at most one friend comment. Each post hides one clue:

| # | Post | Clue |
|---|---|---|
| 1 | "First day of 5th class!! 🎒", with a backpack badge reading "Primarschule Glitzerbach" in the photo | school and age |
| 2 | "Meet Biscuit 🐶 best dog ever", with the comment "Biscuit is the cutest!! 😍" | pet name (a common password!) |
| 3 | "Best 11th birthday ever 🎂", posted 12 March | birthday |
| 4 | "Home from football ⚽", Tue 17:04, plus "every Tuesday!!" | weekly routine |
| 5 | "View from my room 🌄", with a bus stop sign "Glitzerbach, Sonnenweg" in the scene | street |
| 6 | "Mum and Dad at work till 6, just me and Biscuit 😎", Tue 16:30 | when the house is empty |
| 7 | the comment "see you at Bäckerei Krümel before school!", plus a reply from Lena | morning routine and place |
| 8 | "2 weeks in Italy!! ✈️🇮🇹 leaving tomorrow" | the house is empty for two weeks |

The town "Glitzerbach", its street and the bakery are fictional. Add a footer line: "Lena isn't real. Everything here is made up."

**Detective sheet:** for teams, one A4 page.
- "Detective challenge: what can you find out about Lena?" with 8 blanks (her school, class/age, her dog's name, birthday, which afternoon she's always out, her street, where she goes before school, when the house is empty). Each is worth 1 point.
- Part 2: "Fix Lena's posts". For 3 posts of the team's choice, they write how Lena could share the same fun moment without the clue, e.g. hide the badge, post the holiday photos after she's back, don't post the time.
- A second page is the **facilitator answer key**, one fix idea per post.

**Scratch card:** one A4 page for free play, "Build your own mind reader".
- Step-by-step blocks using Scratch's `ask () and wait`, `answer`, `if <> then else`, `say ()` and `join`.
- The example asks 3 questions and makes one guess, e.g. "If you picked night owl and gaming, I guess you play after dinner!".
- A "level up" ideas box.

Text only, with block names exactly as they appear in Scratch 3.

- [ ] **Step 1: Build the three pages.** Each has `const TEXT = {…}` at the top and `@page { size: A4; margin: 8mm }`.
- [ ] **Step 2: Check them in Chrome by printing to PDF.**
  - Expected page counts: feed 2, detective 2 (sheet plus key), Scratch 1.
  - There are no console errors.
  - Looking at the screenshots, every clue from the table is visible on the feed.
- [ ] **Step 3: Commit** (heredoc at the end).
