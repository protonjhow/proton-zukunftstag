# Proton Zukunftstag 2026

Materials for a day of hands-on privacy sessions for 10–12 year olds at Proton, Zurich, on **Thursday 12 November 2026** ([Zukunftstag](https://www.nationalerzukunftstag.ch/), the national day when kids spend a day at a workplace).

The one message of the day:

> **Your privacy is a gift.** Technology and social media reach kids earlier and earlier, and it is very easy to give your privacy away without thinking. By the time you're old enough to care, you may have given it all away already.

## The day

| Time | Session | What the kids do | Folder |
|---|---|---|---|
| 10:00–11:30 | **1. Secret messages** | Make cipher wheels, chat between laptops while "Eve" on the TV cracks every message, then flip a "VPN" switch and blind her. A padlock box shows how to lock something without sharing a key. | [`session1-secret-messages/`](session1-secret-messages/) |
| 11:30–13:00 | **2. The mind reader** | A quiz guesses things about them, then reveals what it noticed *without asking*. They read App Store privacy labels for apps they know, play detective on a made-up girl's posts, get a printed data card, and watch all their data get deleted. | [`session2-mind-reader/`](session2-mind-reader/) |
| 13:00–14:00 | Lunch | | |
| 14:00–15:30 | **3. The lemonade company** | Borrow CHF 10 from "the bank", shop at Migros, survey prices, sell lemonade to the office, repay the loan and split the profit. Then: how could you give it away for free, and what would you have to take from people? | [`session3-who-pays/`](session3-who-pays/) |

**Running the day:** start with [`day/facilitator-guide.md`](day/facilitator-guide.md). It has:
- the run sheets;
- the setup checklist;
- the props and kitchen kit;
- what to do when something breaks;
- the full print list.

## Quick start

The two demos run on any Docker host, either a laptop in the room or a server on AWS:

```sh
cd session1-secret-messages && docker compose up -d --build   # chat :8000, Eve :8001
cd session2-mind-reader && docker compose up -d --build       # quiz :8100, big screen :8100/screen
```

Which URL to open on which device is in each session's README. Session 3 has no software, only printables.

**Printables** are standalone HTML pages. Open them in Chrome and print at 100 % on A4, single-sided:

| Folder | Printables |
|---|---|
| `session1-secret-messages/printables/` | cipher wheel |
| `session2-mind-reader/printables/` | app detective, take-home challenge, Lena's feed, detective sheet with answer key, Scratch mind-reader card |
| `session3-who-pays/printables/` | loan slip, company logbook, stand sign, give-it-away worksheet, reveal cards |
| `day/printables/` | kids' report notes |

## Tests and rehearsals

Each demo has unit tests and a headless-Chrome rehearsal of the whole session. **Run the rehearsals the day before, never during the day**, because they wipe quiz profiles and restart Vault.

```sh
cd session1-secret-messages   # or session2-mind-reader
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -e '.[dev]'
.venv/bin/pytest
cd rehearsal && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i --no-save playwright-core && node rehearse.js
```

## Privacy of the materials themselves

- The quiz keeps profiles **only in memory**. Nothing is written to disk and nothing is logged. The delete ceremony, or a restart, wipes everything.
- Kids are identified by an animal, never by name.
- Questions and guesses stay on harmless preferences: never home, school, family, health, looks or money.
- Lena, her town (Zipfelbühl), school, street and bakery are made up.

## Translation

Everything is in English for now. Kid-facing text is kept in one place per part, ready for German:
- `session1-secret-messages/web/strings.en.js`, plus Eve's word list in `wordlists/`;
- `session2-mind-reader/web/strings.en.js`, plus the quiz text in `mindreader/questions.py`, `guesses.py` and `noticed.py`;
- the `TEXT` block at the top of each printable.

## Background

- Design: [`docs/superpowers/specs/2026-11-06-zukunftstag-design.md`](docs/superpowers/specs/2026-11-06-zukunftstag-design.md)
- Build plans: [`docs/superpowers/plans/`](docs/superpowers/plans/)
