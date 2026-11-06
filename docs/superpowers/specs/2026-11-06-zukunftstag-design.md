# Proton Zukunftstag 2026: Privacy for 10–12 year olds

Date of event: Thursday 12 November 2026, Proton office, Zurich.
Status: draft for review with colleagues (session 2 in particular is to be checked by humans for blind spots; the session 3 "lemonade stand" metaphor is interchangeable).

## Intent

Zukunftstag is a national day where 10–12 year olds spend a day at a workplace. Proton will host a small group (at least 4 kids). They have covered some tech topics at school and are currently doing a lot of Scratch. Each child must write a school report afterwards on what they learned.

The single message of the day:

> **Your privacy is a gift.** Technology and social media reach kids earlier and earlier, and it is very easy to give your privacy away without thinking. By the time you're old enough to care, you may have given it all away already.

The day teaches basic privacy primitives (encryption, profiling, "free" business models) in service of that message, and shows the kids real jobs at Proton along the way.

## Success

- At dinner, each kid tells their parents: "I learned about privacy, and it wasn't boring."
- Each kid has enough concrete material (things they made, did or discovered) to write a substantial school report.

## Goals

- Three hands-on sessions, each led by real Proton teams, so the kids meet several professions.
- Each session can stand on its own, but they build on each other towards the single message.
- The "giving it away without noticing" idea is *experienced*, not lectured.

## Non-goals

- Technical accuracy beyond what a 10–12 year old needs. Simplifications are deliberate (e.g. Vault transit is presented as "the VPN": it wraps the message before it leaves and unwraps it on arrival; NATS is presented as "the internet").
- Teaching the kids to program from scratch within the guided hour.

## Anti-goals (failure even if it "works")

- Lecturing, or scaring the kids.
- Shaming kids who already use TikTok, Roblox, YouTube etc.
- Anything overly personal or creepy about a real child. No inference about where they live, family situation, crushes, etc.
- Proton collecting and keeping data about the kids.

## Constraints

- Group: currently 4 kids aged 10–12, all girls. Numbers may change either way; design for 4 and keep it workable for a few more (e.g. kids take turns or work in pairs on shared laptops).
- Proton provides all hardware.
- Available teams: graphic design, crypto, finance, VPN, systems, network, security, exec. Teams give input and lead or appear in their sessions.
- **Who builds:** John builds everything with an AI assistant, using input from the teams. Graphic design's availability is unknown, so every design item (cipher wheels, data cards, Lena's posts, budget sheet) must have a plain printable version we make ourselves. Design polishes these if they have time.
- **Language:** all materials in English for now, to be translated to German later. Keep every kid-facing string easy to translate (not hard-coded across many files). Eve's word list must be swappable (English now, German after translation).
- **Parent check:** John will discuss the plan, especially session 2, with two parents he knows before the day.
- Lead time: under one week.
- Venue: a conference room with a TV.
- **Hardware assumptions (my call):** two laptops for the chat demo (with 4 kids, two per laptop), one machine driving the TV for Eve, and any browser device for the quiz (laptops are fine if there are no tablets). Scratch free play needs one device per kid or per pair. Check before the day whether the laptops run Scratch online or need the offline Scratch app.

## Schedule

Start and end times are flexible. Each session is a 90-minute slot: 60 minutes guided, then 30 minutes of unstructured free play to explore that session's ideas.

| Time | Block |
|---|---|
| 10:00–11:30 | Session 1: Secret messages |
| 11:30–13:00 | Session 2: The mind reader |
| 13:00–14:00 | Lunch |
| 14:00–15:30 | Session 3: Who pays for free? (ends with the wrap-up of the day) |

Alternative: shift everything 15 minutes earlier (09:45–15:15).

---

## Session 1: Secret messages

**Teams:** Crypto, VPN (plus systems/network for the demo setup).

**Takeaway:** your messages are yours, and there are tools to keep them that way. You can tell a weak lock from a strong one.

### Guided hour (timings approximate)

1. **Intro (10 min).** People have always hidden messages.
2. **Cipher wheels (15 min).** Kids make their own Caesar cipher wheel and encode messages for each other to crack by hand. *Builder's call:* additional paper ciphers (pigpen, scytale) can be offered if time allows or in free play.
3. **Send it over the internet (15 min).** Two laptops chat with each other over NATS. Kids encode each message with a Caesar shift dial that matches their paper wheel. The conference room TV is **Eve**: she brute-forces every Caesar shift and shows the message she worked out *and the wheel setting* (e.g. "Shift 7: TREFFEN UM 3").
4. **Turn on the VPN (10 min).** Flip a switch on the chat page: messages are now wrapped with Vault transit before leaving and unwrapped on receipt. Eve keeps trying her shifts on what she sees and gets nothing.
5. **Padlock box (10 min).** A physical demo of locking a message for someone without ever sharing a key (see below).

### Free play (30 min)

Send messages past Eve, try to trick her, crack each other's paper ciphers. Bonus challenge for sharp kids: the padlock-box "fake lock" trick (below).

### Padlock box

**Props**
- A box that takes two padlocks. Easiest: a **lockout hasp** (steel clip with holes for up to 6 padlocks, about CHF 10–15 from Hornbach, Jumbo, Conrad, Galaxus), clipped through the latch of a small cash box or toolbox. Alternatives: a craft-shop wooden chest with two latches, or a shoebox with two holes punched through lid and box.
- Two padlocks in different colours (red = Alice, blue = Bob), each with its own key. Keys stay in each person's pocket throughout.
- A note to put inside.
- John is sourcing the box.

**How it plays** (Eve is a kid in the middle who carries the box)
1. Alice puts the note in, locks it with **red**, and hands it to Eve to carry. Eve can't open it.
2. Bob can't open it either, so he adds his **blue** lock and sends it back.
3. Alice removes red with her own key. The box is still locked with blue, and she sends it again.
4. Bob removes blue and reads the note.

The box crossed the room three times, Eve never got in, and no key ever left anyone's pocket.

**Free-play bonus:** what if Eve adds her *own* padlock in step 2 and pretends to be Bob? Alice can't tell whose lock it is. So you need to know who you're talking to.

*For adults:* real key exchange uses maths and works differently; this is the classic beginner illustration (Shamir's three-pass idea).

### Demo build: chat + Eve + "VPN"

Builds on John's existing transit demo: <https://github.com/fatred/exploring-vault/tree/main/transit-demo> (NATS via docker compose; Python workers using `nats-py` and `hvac`; Vault userpass auth; transit mount `transit-nats`, key `demo_key`; an `--observer` role that subscribes to the same subject and prints whatever it sees).

**Pieces**
- **NATS** = "the internet". Every message the kids send passes over it.
- **Chat client** on each of two kid laptops:
  - Text box, a Caesar shift dial (0–25) matching the paper wheel, a send button and a conversation view.
  - Received messages are decoded with the receiver's dial setting, so a wrong setting shows gibberish (kids must agree the shift).
  - A clearly visible **"VPN" on/off switch**. When on, the Caesar-encoded text is wrapped with Vault transit before publishing and unwrapped on receipt, before Caesar decoding.
- **Eve** = a service subscribed to the same NATS subject(s), displayed full-screen on the conference room TV:
  - For each message, try all Caesar shifts, pick the most readable, and show the cracked message plus the shift/wheel setting.
  - When the VPN is on, she visibly tries and fails on the wrapped text (e.g. shows `vault:v1:…` and "can't read this").
  - She only ever sees what's on NATS. She is never given Vault access.

**Decided**
- NATS is "the internet". Vault transit wrapping is "the VPN". This simplification is intended.
- Eve's only attack is brute-forcing Caesar shifts on what she sees on NATS.
- Eve's display is the conference room TV and shows the cracked message and the wheel setting.

**My calls (not confirmed by John)**
- The kid-facing chat is a web page; kids never see a terminal. (NATS supports websockets natively, which is one way to do this; how the page reaches Vault is the builder's choice.)
- Eve picks the "most readable" shift by scoring against a word list: **English** for now, swappable to **German** once materials are translated, since the kids will likely write in German on the day. Caesar applies to A–Z only; umlauts, digits, spaces and punctuation pass through unchanged.

**Left to the builder**
- Language/framework, whether there's a small backend per laptop or a shared one, NATS subject layout, how Vault credentials are held.
- Whether Eve animates through the shifts for drama.
- Where NATS, Vault and Eve run: locally in the office, or on servers in AWS. The office has redundant internet paths, so depending on the internet is fine.

---

## Session 2: The mind reader

**Teams:** Security (detective game), graphic design (fake posts, trading cards), systems (quiz app).

**Takeaway:** small, harmless-seeming details add up to a picture of you, and you give some of them away without even noticing.

**Status:** starting point. John will review this with colleagues for blind spots. Given the lead time, building starts now on this version ("we can start with this"). The review is expected to adjust content, not the structure. *(My call.)*

### Guided hour

1. **The quiz (10 min).** Each kid answers ~10 harmless questions on a tablet (cat or dog, favourite emoji, early bird or night owl, which game they play, …). It then makes 4–5 harmless guesses about them (e.g. "you have an older sibling", "you'd click an ad for a new skin"). Getting some wrong is fine ("3 out of 5 from silly questions!").
2. **The twist (5 min).** The quiz reveals what it noticed *without asking*: answers they changed, which question they took longest on, what device they're using. This is the core "giving it away without noticing" moment.
3. **Detective game (25 min).** In teams, kids profile **Lena, 11**, a made-up girl, from her public trail: a few fake social posts, a photo with a school logo in the background, a "home from football!" post at 17:00 every Tuesday. They work out her school, neighbourhood and when her house is empty. Lena is fictional, so the stakes can be real without profiling anyone real.
4. **Your data card (10 min).** Each kid gets a printed Pokémon-style "trading card" of their quiz profile. "This is what companies collect and sell." It comes back in session 3.
5. **Delete ceremony (5 min).** Everyone watches their quiz data being deleted on the big screen. Proton shows how it treats data.

### Free play (30 min)

In Scratch, kids build their own "mind reader" quiz to try on a friend (ask/answer blocks).

### Rules

- Nothing overly personal. Questions and inferences stay at the level of preferences and habits, never home, family circumstances, health, relationships or appearance.
- No real names in the quiz. A nickname or avatar is enough.
- Quiz data is not kept after the delete ceremony.
- Lena's materials must be clearly fictional. No real child's photo, and no school or address that could be mistaken for a real one.
- The group is currently all girls aged 10–12, the same as Lena. That makes her relatable, but "when is her house empty" could feel frightening rather than eye-opening. Frame it as "look how much we figured out", not as danger. Raise this with the two parents.
- **Fallback if the parents have concerns about the quiz:** run the quiz and its hidden tracking on a staged demo profile played by a Proton staffer, rather than on the kids' own answers. Data cards would then be generic or made by the kids by hand.

**Left to the builder:** question set and inference rules (within the rules above), card design, quiz app technology, how the hidden metadata is captured.

---

## Session 3: Who pays for free?

**Teams:** Finance, exec.

**Takeaway:** making things costs a lot. If something is free, someone is still paying, and often it's you, with your time and your data.

**Status:** the lemonade-stand metaphor is a placeholder and may be swapped for something else later. The structure (cost it, make it free, invent how to pay, reveal) should hold whatever the metaphor.

### Guided hour

1. **Build the stand (15 min).** In teams, using a budget sheet from finance, kids cost a lemonade stand: lemons, sugar, cups, table, sign, and their own Saturday time.
2. **The rule (10 min).** "The stand across the street gives lemonade away for free. If you want customers, so must you." How do you still pay for the stand? Kids come up with ideas themselves: ads on cups, selling the list of who came and what they liked, keeping people at the stand until they buy a cookie, free lemonade but paying for the cold one.
3. **The reveal (10 min).** Match each idea to a free app they know (video ads, data selling, games that keep you playing, free games with paid skins). "You just invented how free apps make money." The session 2 data card returns: that's what gets sold.
4. **Exec Q&A (15 min).** "We build things that cost a lot to make, so how does Proton pay for them?" Some people pay, so nobody has to be the product. Then kids ask the exec anything.
5. **Wrap-up of the day (10 min).** Back to the single message: your privacy is a gift, so don't give it away without thinking. Kids note their top three things for their report.

### Free play (30 min)

Build a Scratch "free game" that keeps asking for things, or finish report notes.

---

## My calls across the day (not confirmed by John)

- Each session is led by different teams so the kids meet several professions.
- Graphic design produces take-home items (cipher wheels, data cards) that double as report material.

## Open for later

- Final session 3 metaphor.
- Human review of session 2, and the outcome of John's chat with two parents.
- German translation of all materials, and the German word list for Eve.
- Final head count and confirmed hardware.
- Graphic design's availability.
