# Session 3 "The lemonade company" + Whole-day Materials Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The printed materials for a real lemonade business that the kids run for the office: the bank loan slip, a company logbook (shopping and price survey, staff survey, sales and profit), a stand sign, a "give it away" worksheet and reveal cards. Plus the exec's drop-in brief, and the whole-day materials: the kids' report notes and the facilitator guide for all three sessions.

**Architecture:** No software. Printables are standalone A4 HTML pages in the same style as session 1's cipher wheel:
- a `const TEXT = {…}` block at the top for translation;
- `@page { size: A4; margin: 8mm }`;
- `print-color-adjust: exact`, so colours survive Chrome's default print settings;
- plain styling that design can rebrand.

Briefs for adults are Markdown.

**Tech Stack:** HTML/CSS (plus inline JS to render `TEXT`), Markdown. Verified by printing to PDF in headless Chrome with background graphics off.

**Spec:** `docs/superpowers/specs/2026-11-06-zukunftstag-design.md` (Session 3 "The lemonade company", Schedule, Success)

> Replaces the 6 November first version of this plan (budget sheet, rule card, Scratch free-game card), which John redesigned into a real business. Those files are deleted.

## Global Constraints

- Session 3 files live under `session3-who-pays/`, and whole-day files under `day/`.
- **Commits:** never run `git commit`. Work on branch `sessions-2-3`, and hand John heredocs at the end.
- All kid-facing text is in English, in one `TEXT` block per page.
- **No sum needs a calculator.** Use tallies, numbered boxes to cross off, and coins dealt out one by one. The only arithmetic is "take away 11" and money left from 10.
- **No shaming.** Using free apps isn't bad; it's smart to know how they pay. Every sheet that names real apps carries that line.
- **Money:** a CHF 10 loan from the bank (finance team), with CHF 11 paid back. Payment is cash, or TWINT to an adult who gives cash back at count-up.
- **Hygiene:** the sign lists the ingredients.

## Review Focus

1. **Printing on default Chrome settings.** Colours survive and nothing spills onto an extra page. Each task checks the page count with backgrounds off.
2. **Profit maths with Migros change.** The tin holds sales plus the change left from the CHF 10, so "everything in the tin − 11 = profit" must be the only sum. Check that the sales sheet says to put the change in the tin.
3. **Spoilers.** No kid sheet shows the "give it away" options before that step. The reveal cards print single-sided as two separate sets, with the answer key only in the guide.
4. **10-year-old reading level.** Short sentences, and no jargon without an explanation.
5. **A different number of kids.** The logbook works for one company of 4, and for two companies with one copy each.

---

### Task 1: Loan slip and stand sign

**Files:** Create `session3-who-pays/printables/loan-slip.html` and `session3-who-pays/printables/stand-sign.html`

- **Loan slip (1 page, two slips, one per company):**
  - Headed "🏦 Bank of Proton: loan agreement".
  - Body: "We, the ______ Lemonade Company, borrowed **CHF 10** from the Bank of Proton on 12 November. We promise to pay back **CHF 11** (10 + 1 interest) by 15:20."
  - Signature lines for each company member and for the bank.
  - A "✅ Paid back" box for the bank to tick at count-up.
  - A one-line explainer: "Interest is what the bank charges for lending you money."
- **Stand sign (1 page):**
  - "🍋 Fresh lemonade".
  - A big blank: "CHF ____ a cup".
  - "Made by the ______ Lemonade Company".
  - An "Ingredients:" list with 4 blank lines.
  - "We take cash and TWINT (ask a grown-up)".
  - Room to decorate.
- [ ] **Step 1: Build both.** Each PDF should be 1 page.

### Task 2: Company logbook

**Files:** Create `session3-who-pays/printables/company-logbook.html`, 3 pages, one per job:

- **Page 1, Shopping (shopper and accountant):**
  - A table with the columns: what we bought, how many, price, money left. The first row is "Start: our loan", with money left 10.00.
  - Suggested buys: lemons, sugar, ice if the office freezer has none.
  - Below: "Migros price check", a table of ready-made drinks (ready-made lemonade, iced tea, juice, water) with the columns size and price.
  - Then: "Will our cup be cheaper or more expensive than these?".
- **Page 2, Ask the staff (surveyor):**
  - "How much would you pay for a cup of homemade lemonade?" with tally boxes for CHF 0.50 / 1.00 / 1.50 / 2.00 / 2.50 or more / "nothing".
  - "Would you buy one today?" with yes and no tally boxes.
  - Then: "The price with the most ticks: ___", "Our price: CHF ___", and "Why?".
- **Page 3, Sales and profit (seller and accountant):**
  - 60 numbered cup boxes, crossed off one per cup sold.
  - Tally boxes for paid by cash and paid by TWINT.
  - "What we noticed about our customers (without asking!)", with 3 lines.
  - Count-up steps:
    1. Put the change left from Migros in the tin.
    2. The grown-up swaps the TWINT money for cash and adds it.
    3. Everything in the tin: CHF ___
    4. Pay the bank: − 11
    5. Our profit: CHF ___
    6. Share it out: deal the coins one by one. Each of us gets CHF ___
- [ ] **Step 1: Build it.** The PDF should be 3 pages, and the count-up must say to put the Migros change in the tin.

### Task 3: "Give it away" worksheet and reveal cards

**Files:** Create `session3-who-pays/printables/give-it-away.html`, and rewrite `session3-who-pays/printables/reveal-cards.html`

- **Worksheet (1 page):**
  - At the top: "Today we sold ___ cups at CHF ___. Our profit: CHF ___."
  - The premise: "Tomorrow every cup is FREE. The bank still wants its money. How will you pay?"
  - Four option boxes, each with prompts and lines:
    - 📢 **Adverts:** who in the office would pay to put an advert on the cups or the sign, and what would customers think?
    - 🗂️ **Sell what you know:** use "what we noticed about our customers". Who would pay for it, and how would customers feel?
    - 🧊 **Pay for extras:** what could cost extra?
    - 🏦 **Borrow more and hook them:** the bank lends CHF 20, so you pay back 22. Lemonade is free for a week and everyone gets used to it, then you charge. How many cups at CHF 1, and at CHF 2? What if people stop coming?
  - Then: "Which would you choose? Why?".
  - It ends with the fair-price box: "charge a fair price from the start: your customers pay you, so you never have to sell them. That's how Proton works."
- **Reveal cards (2 pages):** Set A is the stand ideas and Set B is the real apps, printed shuffled.

  | Set A (stand ideas) | Set B (real apps) |
  |---|---|
  | Adverts on the cups | Adverts before videos and sponsored posts |
  | Sell what you noticed about customers | Apps that collect what you like and sell it |
  | Free lemonade, pay for ice and the big cup | Free games with paid skins, coins or Robux |
  | Borrow more, give it away until people are hooked, then charge | Apps and AI tools that are free or cheap now while investors pay the bills, then the price goes up or the adverts arrive |
  | A sticker for coming back every day | Streaks, autoplay and notifications |
  | A fair price | Paid apps: you're the customer, not the product (Proton) |

- [ ] **Step 1: Build both.** The worksheet PDF should be 1 page and the reveal-cards PDF 2 pages.

### Task 4: Exec drop-in brief, README, remove old files

**Files:**
- Rewrite `session3-who-pays/exec-brief.md`. There's no fixed slot. It covers the best moments to drop in (buy a cup during the sale and ask how they set the price and who lent them money; or join "give it away"), the kid-sized "how does Proton pay?" answer tied to their stand and their loan, the likely questions, and the don'ts.
- Rewrite `session3-who-pays/README.md`.
- Delete `budget-sheet.html` and `scratch-free-game.html`.
- [ ] **Step 1: Write and delete.**

### Task 5: Report notes and facilitator guide

**Files:** Modify `day/printables/report-notes.html` and `day/facilitator-guide.md`

- **Report notes:** the session 3 prompt becomes "Your lemonade company: what you bought, your price, your profit, how you'd give it away", and the glossary gains "Loan" and "Profit". It stays 2 pages.
- **Facilitator guide:**
  - Session 3 is rewritten to the spec's run table, with no free play. Its sections are setup, a shopping list for the CHF 10 with a recipe, kitchen kit, an office chat announcement draft, roles, cash and TWINT handling, a run sheet, the reveal-card key, and what to do if something breaks.
  - The print list and the "before the day" checklist are updated: cash for the loan, a cash tin, an adult with TWINT, two adults for Migros.
  - Fixes from the 6 November review:
    - the one message is quoted exactly from the spec;
    - "metadata" is introduced in session 2;
    - the rehearsal steps get their install command and a "never during the day" warning;
    - "kids tap *Next player* before the delete ceremony";
    - single-sided printing, with detective sheet page 2 printed once.
- [ ] **Step 1: Update both.** The report-notes PDF should be 2 pages. Check the guide's commands against the session READMEs.
