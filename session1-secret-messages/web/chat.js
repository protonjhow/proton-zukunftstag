import { encode, decode } from "/static/caesar.js";
import { chatName } from "/static/names.js";
import strings from "/static/strings.en.js";

const S = strings.chat;
const $ = (id) => document.getElementById(id);
const me = chatName(new URLSearchParams(location.search).get("me"));

// {mine: true, id, plain, cipher, failed} | {mine: false, from, cipher, vpn}
const messages = [];
let ws;
let nextId = 1;

function dial() {
  return Number($("dial").value);
}

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function render() {
  $("dial-value").textContent = dial();
  $("dial-map").textContent = `A → ${encode("A", dial())}`;
  $("vpn-label").textContent = $("vpn").checked ? `${S.vpnOn} 🔒` : S.vpnOff;
  document.body.classList.toggle("vpn-on", $("vpn").checked);

  const list = $("messages");
  list.replaceChildren();
  if (!messages.length) list.append(el("li", "empty", S.empty));
  for (const m of messages) {
    const li = el("li", m.mine ? "mine" : "theirs");
    if (m.mine) {
      li.append(el("div", "text", m.plain));
      li.append(el("div", "meta", m.failed ? `⚠️ ${S.notSent}` : `${S.sentAs} ${m.cipher}`));
    } else {
      li.append(el("div", "from", m.from));
      li.append(el("div", "text", decode(m.cipher, dial())));
      li.append(el("div", "meta", m.vpn ? `🔒 ${S.lockBadge} · ${m.cipher}` : m.cipher));
    }
    list.append(li);
  }
  list.scrollTop = list.scrollHeight;
}

function showStatus(text) {
  $("status").hidden = !text;
  $("status").textContent = text || "";
}

function connect() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws?me=${encodeURIComponent(me)}`);
  ws.onopen = () => showStatus("");
  ws.onclose = () => {
    showStatus(S.disconnected);
    setTimeout(connect, 2000);
  };
  ws.onmessage = (ev) => {
    const data = JSON.parse(ev.data);
    if (data.type === "error") {
      const failed = messages.find((m) => m.mine && m.id === data.id);
      if (failed) failed.failed = true;
      showStatus(S.vpnError);
    } else if (data.type === "message" && data.from !== me) {
      messages.push({ mine: false, from: data.from, cipher: data.text, vpn: data.vpn });
    }
    render();
  };
}

$("compose").addEventListener("submit", (ev) => {
  ev.preventDefault();
  const plain = $("text").value;
  if (!plain.trim() || ws.readyState !== WebSocket.OPEN) return;
  const cipher = encode(plain, dial());
  const id = nextId++;
  ws.send(JSON.stringify({ id, text: cipher, vpn: $("vpn").checked }));
  messages.push({ mine: true, id, plain, cipher, failed: false });
  $("text").value = "";
  showStatus("");
  render();
});
$("dial").addEventListener("input", render);
$("vpn").addEventListener("change", render);

document.title = S.title;
$("title").textContent = `🔐 ${S.title}`;
$("me").textContent = `${S.youAre}: ${me}`;
$("dial-label").textContent = S.dialLabel;
$("text").placeholder = S.placeholder;
$("send").textContent = S.send;
render();
connect();
