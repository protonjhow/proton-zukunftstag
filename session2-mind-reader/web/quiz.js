import strings from "/static/strings.en.js";

const S = strings.quiz;
const $ = (id) => document.getElementById(id);
const app = $("app");

let quiz; // {questions, avatars, taken}
let avatar = null;
let answers = {};
let taps = [];
let t0 = 0;

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function button(cls, text, onClick, disabled = false) {
  const b = el("button", cls, text);
  b.disabled = disabled;
  b.addEventListener("click", onClick);
  return b;
}

function screen(...children) {
  app.replaceChildren(...children);
  window.scrollTo(0, 0);
}

function showError(retry) {
  $("progress").textContent = "";
  screen(el("p", "message", S.error), button("primary", S.retry, retry));
}

// keepAnswers: her animal was taken at submit time, so she only picks a new one.
async function load(message, keepAnswers = false) {
  try {
    quiz = await (await fetch("/api/quiz")).json();
  } catch {
    return showError(() => load(message, keepAnswers));
  }
  pickAvatar(message, keepAnswers);
}

function pickAvatar(message, keepAnswers) {
  avatar = null;
  if (!keepAnswers) {
    answers = {};
    taps = [];
  }
  $("progress").textContent = "";
  const grid = el("div", "avatars");
  for (const a of quiz.avatars) {
    const taken = quiz.taken.includes(a.key);
    const pick = keepAnswers ? () => ((avatar = a.key), submit()) : () => startQuiz(a.key);
    grid.append(button("avatar", a.emoji, pick, taken));
  }
  const parts = [el("h2", null, S.pickAnimal), el("p", "hint", S.pickAnimalHint), grid];
  if (message) parts.splice(1, 0, el("p", "warn", message));
  screen(...parts);
}

function startQuiz(key) {
  avatar = key;
  t0 = performance.now();
  ask(0);
}

function ask(i) {
  const q = quiz.questions[i];
  const last = i === quiz.questions.length - 1;
  $("progress").textContent = S.progress(i + 1, quiz.questions.length);
  const next = button("primary", last ? S.finish : S.next, () => (last ? submit() : ask(i + 1)), !answers[q.key]);
  const grid = el("div", "options");
  for (const o of q.options) {
    const b = button("option", "", () => {
      answers[q.key] = o.key;
      taps.push({ q: q.key, option: o.key, t: Math.round(performance.now() - t0) });
      grid.querySelectorAll(".option").forEach((x) => x.classList.toggle("selected", x === b));
      next.disabled = false;
    });
    b.append(el("span", "emoji", o.emoji), el("span", "label", o.label));
    if (answers[q.key] === o.key) b.classList.add("selected");
    grid.append(b);
  }
  screen(el("h2", "prompt", q.prompt), grid, next);
}

async function submit() {
  $("progress").textContent = "";
  screen(el("p", "message thinking", S.thinking));
  let r;
  try {
    r = await fetch("/api/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ avatar, answers, taps, touch: navigator.maxTouchPoints > 0 }),
    });
  } catch {
    return showError(submit);
  }
  if (r.status === 409) return load(S.taken, true);
  if (!r.ok) return showError(submit);
  showGuesses(await r.json());
}

function showGuesses(profile) {
  const votes = new Map();
  const list = el("ul", "guesses");
  const score = el("p", "score");
  const more = button("primary", S.toNoticed, () => showNoticed(profile));
  more.hidden = true;
  for (const [i, g] of profile.guesses.entries()) {
    const li = el("li", "guess");
    li.append(el("div", "label", g.label), el("div", "value", g.value));
    const thumbs = el("div", "thumbs");
    for (const [vote, icon] of [[true, "👍"], [false, "👎"]]) {
      thumbs.append(
        button("thumb", icon, (ev) => {
          votes.set(i, vote);
          thumbs.querySelectorAll(".thumb").forEach((t) => t.classList.toggle("selected", t === ev.currentTarget));
          if (votes.size === profile.guesses.length) {
            score.textContent = S.score([...votes.values()].filter(Boolean).length, votes.size);
            more.hidden = false;
          }
        }),
      );
    }
    li.append(thumbs);
    list.append(li);
  }
  screen(el("h2", null, `${profile.emoji} ${S.guessesTitle}`), el("p", "hint", S.guessesHint), list, score, more);
}

function showNoticed(profile) {
  const list = el("ul", "noticed");
  let shown = 0;
  const more = button("primary", S.showMore, reveal);
  const done = el("p", "message", S.done);
  const again = button("secondary", S.nextPlayer, () => load());
  done.hidden = again.hidden = true;
  function reveal() {
    list.append(el("li", "fact", profile.noticed[shown++]));
    if (shown === profile.noticed.length) {
      more.hidden = true;
      done.hidden = again.hidden = false;
    }
  }
  screen(el("h2", null, S.noticedTitle), list, more, done, again);
  reveal();
}

document.title = S.title;
$("title").textContent = `🔮 ${S.title}`;
load();
