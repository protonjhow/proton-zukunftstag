import strings from "/static/strings.en.js";

const S = strings.eve;
const $ = (id) => document.getElementById(id);
const RAW_MAX = 40;
const SPIN_MS = 1200;

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function line(label, value, cls) {
  const d = el("div", `line ${cls || ""}`);
  d.append(el("span", "label", `${label}: `), el("span", "value", value));
  return d;
}

function short(raw) {
  return raw.length > RAW_MAX ? raw.slice(0, RAW_MAX) + "…" : raw;
}

function result(s) {
  const out = [];
  if (s.locked) {
    out.push(el("div", "verdict locked", `🔒 ${S.locked}`));
  } else if (s.guess === null) {
    out.push(el("div", "verdict nocrack", S.noCrack));
  } else {
    out.push(line(S.setting, String(s.shift), "setting"));
    out.push(line(S.guess, s.guess, "guess"));
    if (s.shift === 0) out.push(el("div", "verdict unlocked", S.unlocked));
  }
  return out;
}

function card(s, animate) {
  const li = el("li", s.locked ? "locked" : s.guess === null ? "nocrack" : "cracked");
  li.append(line(S.from, s.from ?? S.unknownSender, "from"));
  li.append(line(S.saw, short(s.raw), "raw"));
  const body = el("div", "result");
  li.append(body);
  if (!animate) {
    body.append(...result(s));
    return li;
  }
  li.classList.add("spinning");
  const start = performance.now();
  const spin = () => {
    const n = Math.min(26, Math.floor(((performance.now() - start) / SPIN_MS) * 26) + 1);
    body.replaceChildren(el("div", "trying", `${S.trying} ${n}…`));
    if (performance.now() - start < SPIN_MS) return requestAnimationFrame(spin);
    li.classList.remove("spinning");
    body.replaceChildren(...result(s));
  };
  spin();
  return li;
}

function add(s, animate) {
  $("sightings").querySelector(".waiting")?.remove();
  $("sightings").prepend(card(s, animate));
}

function showStatus(text) {
  $("status").hidden = !text;
  $("status").textContent = text || "";
}

function connect() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${location.host}/ws`);
  ws.onopen = () => showStatus("");
  ws.onclose = () => {
    showStatus(S.disconnected);
    setTimeout(connect, 2000);
  };
  ws.onmessage = (ev) => {
    const data = JSON.parse(ev.data);
    if (data.type === "history") {
      $("sightings").replaceChildren();
      if (!data.sightings.length) $("sightings").append(el("li", "waiting", S.waiting));
      for (const s of data.sightings) add(s, false);
    } else if (data.type === "sighting") {
      add(data, true);
    }
  };
}

document.title = S.title;
$("title").textContent = S.title;
$("subtitle").textContent = S.subtitle;
connect();
