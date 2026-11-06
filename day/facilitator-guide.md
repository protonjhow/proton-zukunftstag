# Zukunftstag at Proton: facilitator guide

**Thursday 12 November 2026 · Proton, Zurich · kids aged 10–12 (currently four)**

## The one message

Every session builds towards this. Say it at the end of the day (it's quoted from the design):

> **Your privacy is a gift.** Technology and social media reach kids earlier and earlier, and it is very easy to give your privacy away without thinking. By the time you're old enough to care, you may have given it all away already.

The aim is for every kid to tell their parents tonight: *"I learned about privacy, and it wasn't boring."*

**Ground rules for everyone:** no lecturing, no scary stories, and no making kids feel bad about apps they already use.

## Day timeline

| Time | Block | Room needs |
|---|---|---|
| 10:00–11:30 | Session 1: Secret messages (60 min guided + 30 min free play) | TV, 2 chat laptops, padlock box |
| 11:30–13:00 | Session 2: The mind reader (60 min guided + 30 min free play) | Big screen, a device per kid (or shared), printer nearby |
| 13:00–14:00 | Lunch | |
| 14:00–15:30 | Session 3: The lemonade company (90 min, no free play; ends with the wrap-up) | Kitchen corner, a table for the stand, CHF 10 loan, 2 adults for Migros |

## Before the day

- [ ] **Print** everything on the print list (bottom of this page). Print **single-sided**, so answer keys and card sets don't end up on the backs of the kids' sheets. Cut out the reveal cards.
- [ ] **Session 1 stack:** in `session1-secret-messages/`, run `docker compose up -d --build`. `docker compose ps` should show nats, chat and eve running and vault healthy.
- [ ] **Session 2 stack:** in `session2-mind-reader/`, run `docker compose up -d --build`.
- [ ] **Rehearse both stacks the day before, never during the day.** The rehearsals wipe session 2's profiles and restart session 1's Vault. In each `rehearsal/` folder, run `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i --no-save playwright-core && node rehearse.js`. Everything should say PASS.
- [ ] Make sure every laptop and tablet can reach the host. If the stacks run on AWS, open ports 8000, 8001 and 8100 to the office only.
- [ ] Check Scratch works on the kids' devices (online, or the offline app).
- [ ] **Session 1 props:** the padlock box with lockout hasp, 2 coloured padlocks with their keys, a note, split pins, scissors.
- [ ] **Session 3:**
  - [ ] **The bank** (finance): CHF 10 in coins or a note, a loan slip and a pen.
  - [ ] **The TWINT adult:** a phone with TWINT, plus about CHF 30 in coins and small notes, to swap TWINT money for cash at count-up.
  - [ ] **Two adults** free for the Migros trip, 14:05–14:25.
  - [ ] **Kitchen kit** ready (see Session 3), and cups from the office kitchen. Check with facilities.
  - [ ] **A spot for the stand** that people walk past, e.g. near the coffee machine.
  - [ ] Post the **office chat announcement** (draft in Session 3) at lunchtime.
- [ ] Send `session3-who-pays/exec-brief.md` to the exec.

---

## Session 1: Secret messages (10:00–11:30)

**Teams:** Crypto (leads), VPN (runs the laptops and the "turn on the VPN" moment).

**Setup**
- Kid laptop 1: `http://<host>:8000/?me=<kid's name>`
- Kid laptop 2: `http://<host>:8000/?me=<another kid's name>`. **Names must differ.**
- TV: `http://<host>:8001`, full screen.
- Between groups: `docker compose restart eve` clears Eve's screen.

**Run sheet**

| Min | Block | Say / do |
|---|---|---|
| 0–10 | Intro | "People have hidden messages for thousands of years. Today you'll be spies." Show a cipher wheel. |
| 10–25 | Cipher wheels | Kids cut and pin their wheels, agree a setting, and encode a message for a partner to crack. "Setting 3 means A → D." |
| 25–40 | Send it over the internet | Two kids chat on the laptops with the dial set to their wheel setting. Point at the TV: "Meet Eve. She sees everything on the internet." Eve cracks each message and shows the setting. Let them try to beat her. |
| 40–50 | Turn on the VPN | "Flip the VPN switch." Friends still read the messages; Eve sees `From: ???` and "I can't read this!". "The VPN wraps your message before it leaves and unwraps it when it arrives." |
| 50–60 | Padlock box | Alice locks the box with red and sends it via Eve. Bob adds blue and sends it back. Alice removes red and sends it again. Bob removes blue and opens it. "No key ever left anyone's pocket." |

**Free play (30 min):** send messages past Eve, try to fool her (short words and names she can't crack), and crack each other's paper ciphers. Bonus: what if Eve adds her *own* padlock and pretends to be Bob?

**If something breaks**
- Kid sees "The VPN isn't working": run `docker compose restart vault` in `session1-secret-messages/`.
- Eve says "I couldn't crack this one" a lot: the messages are too short, or in German (her word list is English for now). Ask for a sentence.
- A laptop sees no messages: the two laptops have the same name. Change `?me=` on one of them.

---

## Session 2: The mind reader (11:30–13:00)

**Teams:** Security (leads the detective game), Systems (quiz and big screen), Design (if available).

**Setup**
- Each kid's device: `http://<host>:8100/`. One device can be shared; "Next player" restarts.
- Big screen: `http://<host>:8100/screen`.
- On paper: Lena's feed and a detective sheet (page 1) per team, plus the answer key (page 2) for you only.

**Run sheet**

| Min | Block | Say / do |
|---|---|---|
| 0–10 | The quiz | "This quiz can read your mind." Kids pick an animal (no names) and answer 10 questions. Then they tap 👍 or 👎 on each guess. "3 out of 5 from silly questions!" |
| 10–15 | The twist | "But wait, there's more…" The quiz reveals what it noticed *without asking*. "You never told it any of that. Grown-ups call this **metadata**: information about *how* you did something, not *what* you said." |
| 15–40 | Detective game | Teams study Lena's posts and fill in the sheet. Celebrate: "Wow, you're great detectives!" Then go straight to **Part 2: fix Lena's posts**. Keep it about how much we worked out, not about danger. |
| 40–50 | Data cards | On the big screen, **Print data cards**. Hand them out: "This is what companies collect and sell. You get to keep yours." |
| 50–55 | Delete ceremony | First, kids tap **Next player** on their devices so their results go off screen. Then **Delete everything** (tap twice). The animals vanish; "0 profiles. Nothing about you is stored any more." |
| 55–60 | Bridge | "After lunch you'll run a real business. Who pays for free apps?" |

**Free play (30 min):** build a mind reader in Scratch (`scratch-mind-reader.html` card) and try it on a friend.

**If something breaks**
- The quiz won't load: run `docker compose restart` in `session2-mind-reader/`. This wipes any profiles.
- Two kids pick the same animal: the second one is asked to pick another, and her answers are kept.
- **Fallback** if parents raise concerns: a Proton colleague takes the quiz as a staged demo profile on the big screen while the kids watch, and the kids draw their own data cards by hand.

---

## Session 3: The lemonade company (14:00–15:30)

**Teams:** Finance (leads, and plays **the bank**), the TWINT adult, two adults for Migros. The **exec** drops in any time; the best moment is buying a cup during the sale.

**One company:** all the kids together. Give out jobs, and swap them around:

| Job | Does |
|---|---|
| Shopper | Finds things at Migros and pays |
| Accountant | Writes every cost and the money left (logbook page 1), and does the count-up (page 3) |
| Surveyor | Asks staff what they'd pay (page 2) |
| Maker | Squeezes, mixes and tastes |
| Seller | Runs the stand and crosses off a box per cup (page 3) |

With more than about six kids, run two companies, each with its own loan slip and logbook.

**Shopping list for CHF 10** (for about 30 cups of 1.5–2 dl). Migros prices are approximate:
- about 2 kg of lemons (about 15), around CHF 6–7;
- 1 kg of sugar, around CHF 1.50;
- ice only if the office freezer has none.

If money's tight, buy fewer lemons; the kids decide. Cups come from the office kitchen. *Point out that someone is giving them the cups for free. That's a sponsor!*

**Recipe** (makes about 6 litres):
1. An adult cuts the lemons in half, and the kids squeeze them.
2. Stir 500 g of sugar into 1 litre of warm water until it disappears.
3. Mix in the lemon juice and 4–5 litres of cold water. Add ice.
4. Taste, and add more sugar or water if needed.

**Kitchen kit:** 2 big jugs or a drinks dispenser, a lemon squeezer (2 if possible), a knife and board (adults only), a big spoon, a measuring jug, cups, a cash tin, paper towels, the stand sign and markers, and a table.

**Hygiene:** everyone washes their hands first. The sign lists the ingredients (lemons, sugar, water), so anyone with an allergy can check.

**Office chat announcement** (post at lunch, again at 14:40):

> 🍋 **The Zukunftstag kids are opening a lemonade stand!** Today 14:45–15:10 at [place]. Homemade lemonade. They'll set the price after asking some of you 😉 Cash or TWINT. Come and buy a cup!

**Run sheet**

| Min | Time | Block | Say / do |
|---|---|---|---|
| 0–5 | 14:00 | Kick-off | "Today you're running a real business. First you need money." The bank lends CHF 10, and the company signs the loan slip: CHF 11 back by 15:20. "Interest is what the bank charges for lending you money." Hand out jobs and the logbook. |
| 5–25 | 14:05 | Migros | Two adults go with them. They buy ingredients, and the accountant writes each price and the money left. Then the price check: what do ready-made lemonade, iced tea, juice and water cost? |
| 25–33 | 14:25 | Ask the staff | The surveyor (with a friend) asks around the office: "How much would you pay for a cup of homemade lemonade?" Tally on page 2. Then they choose their price and write it on the sign. |
| 33–45 | 14:33 | Make it | Wash hands, squeeze, mix, taste. Finish the sign: price and ingredients. Set up the stand. |
| 45–68 | 14:45 | Sell it | Open the stand. The seller crosses off a box per cup and ticks cash or TWINT. "Watch your customers: what do you notice?" (Fill in the "noticed" lines.) The exec ideally drops in now to buy a cup. |
| 68–73 | 15:08 | Count it | Follow the count-up on page 3. Put the Migros change in the tin, and the TWINT adult swaps TWINT for cash. Count, pay the bank CHF 11 (the bank ticks "Paid back"), and deal out the profit coin by coin. |
| 73–85 | 15:13 | Give it away? | Hand out the worksheet: "Tomorrow every cup is FREE. The bank still wants its money." Work through the four boxes with today's numbers, then match the reveal cards (Set A to Set B). End on the fair price: "Your customers pay you, so you never have to sell them. That's how Proton works." |
| 85–90 | 15:25 | Wrap-up of the day | Say the one message (top of this page). Hand out the report notes: kids write their top 3 things. |

**Reveal-card answer key** (stand idea → real app)

| Set A (stand idea) | Set B (real app) |
|---|---|
| 📢 Adverts on the cups | 📺 Adverts before videos and sponsored posts |
| 🗂️ Sell what you noticed about customers | 📊 Apps that collect what you like and sell it |
| 🧊 Pay extra for ice and the big cup | 💎 Free games with paid skins and coins |
| 🏦 Borrow more, give it away until hooked, then charge | 🤖 Apps and AI tools that are free or cheap while investors pay, then cost more or show adverts |
| ⭐ A sticker for coming back every day | 📱 Streaks, autoplay and notifications |
| 🏷️ Just charge a fair price | 🔒 Paid apps: you're the customer (Proton) |

If a team makes a different match and can explain it, count it.

**If something breaks**
- **Migros has no lemons:** buy bottled lemon juice, or switch to iced tea. Keep tracking the costs.
- **Running late:** shorten the staff survey (ask 5 people) and the sale. Keep the count-up and "give it away".
- **They make a loss** (less than CHF 11 in the tin): a great lesson. "Who pays the bank now?" The bank lets them pay back what they have. **Kids never pay from their own pocket.**
- **Nobody comes:** post the announcement again, and send the seller with a tray to the nearest desks.

---

## Print list (for 4 kids, one company, with spares; single-sided)

| What | File | Copies |
|---|---|---|
| Cipher wheel (thick paper if you have it) | `session1-secret-messages/printables/cipher-wheel.html` | 6 |
| Lena's feed (2 pages) | `session2-mind-reader/printables/lena-feed.html` | 2 sets |
| Detective sheet | `session2-mind-reader/printables/detective-sheet.html` | page 1 × 2, page 2 (answer key) × 1 |
| Scratch mind reader | `session2-mind-reader/printables/scratch-mind-reader.html` | 4 |
| Data cards | printed live from the big screen in session 2 | 1 per kid |
| Loan slip (2 per page) | `session3-who-pays/printables/loan-slip.html` | 1 |
| Company logbook (3 pages) | `session3-who-pays/printables/company-logbook.html` | 1 (+1 spare) |
| Stand sign | `session3-who-pays/printables/stand-sign.html` | 1 (+1 spare) |
| Give it away? | `session3-who-pays/printables/give-it-away.html` | 1 (+1 spare) |
| Reveal cards (2 pages, cut out) | `session3-who-pays/printables/reveal-cards.html` | 1 set |
| Report notes (2 pages) | `day/printables/report-notes.html` | 6 |

Open each file in Chrome and print at 100 % on A4.
