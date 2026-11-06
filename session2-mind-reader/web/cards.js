import strings from "/static/strings.en.js";

const S = strings.cards;
const $ = (id) => document.getElementById(id);

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function field(label, value) {
  const d = el("div", "field");
  d.append(el("div", "flabel", label), el("div", "fvalue", value));
  return d;
}

function portrait(emoji) {
  const d = el("div", "portrait");
  d.append(el("span", null, emoji));
  return d;
}

function card(c) {
  const d = el("div", "card");
  const top = el("div", "top");
  top.append(el("div", "name", c.title), el("div", "kind", S.kind));
  d.append(
    top,
    portrait(c.emoji),
    field(S.interests, c.interests.join(" · ")),
    field(S.notify, c.notify),
    field(S.ad, c.ad),
    field(S.value, "★".repeat(c.stars) + "☆".repeat(5 - c.stars)),
    el("div", "footer", S.footer),
  );
  return d;
}

async function main() {
  const { profiles } = await (await fetch("/api/profiles")).json();
  const sheets = $("sheets");
  if (!profiles.length) {
    sheets.append(el("p", "none", S.none));
    return;
  }
  for (let i = 0; i < profiles.length; i += 4) {
    const sheet = el("div", "sheet");
    for (const p of profiles.slice(i, i + 4)) sheet.append(card(p.card));
    sheets.append(sheet);
  }
}

$("print").textContent = `🖨️ ${S.print}`;
$("print").addEventListener("click", () => window.print());
main();
