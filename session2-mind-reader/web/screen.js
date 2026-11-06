import strings from "/static/strings.en.js";

const S = strings.screen;
const $ = (id) => document.getElementById(id);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let polling = true;
let armed = false;
let gone = false;

function render(data) {
  const board = $("avatars");
  board.replaceChildren();
  if (!data.count && !gone) {
    const p = document.createElement("p");
    p.className = "empty";
    p.textContent = S.empty;
    board.append(p);
  }
  for (const p of data.profiles) {
    const d = document.createElement("div");
    d.className = "tile";
    d.textContent = p.emoji;
    board.append(d);
  }
  $("count").textContent = gone && !data.count ? S.gone : S.count(data.count);
  if (data.count) gone = false;
}

async function poll() {
  while (true) {
    if (polling) {
      try {
        render(await (await fetch("/api/profiles")).json());
      } catch {
        /* keep showing the last state */
      }
    }
    await sleep(2000);
  }
}

$("delete").addEventListener("click", async () => {
  const btn = $("delete");
  if (!armed) {
    armed = true;
    btn.textContent = S.confirm;
    setTimeout(() => {
      armed = false;
      if (btn.textContent === S.confirm) btn.textContent = S.delete;
    }, 4000);
    return;
  }
  armed = false;
  polling = false;
  btn.disabled = true;
  btn.textContent = S.deleting;
  for (const tile of [...document.querySelectorAll(".tile")]) {
    tile.classList.add("vanish");
    await sleep(450);
    tile.remove();
  }
  const data = await (await fetch("/api/delete", { method: "POST" })).json();
  gone = true;
  render({ count: data.count, profiles: [] });
  btn.textContent = S.delete;
  btn.disabled = false;
  polling = true;
});

document.title = S.title;
$("title").textContent = `🔮 ${S.title}`;
$("subtitle").textContent = S.subtitle;
$("print").textContent = S.print;
$("delete").textContent = S.delete;
poll();
