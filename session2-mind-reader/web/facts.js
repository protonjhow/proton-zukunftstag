import strings from "/static/strings.en.js";

const T = strings.facts;

const el = (tag, cls, text) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
};

function bars(rows, fmt, cls) {
  const max = Math.max(...rows.map((r) => r[1]));
  const d = el("div", "bars");
  for (const [label, v] of rows) {
    const row = el("div", `bar ${cls || ""}`);
    const fill = el("div", "fill");
    fill.style.width = `${(v / max) * 100}%`;
    const track = el("div");
    track.append(fill);
    row.append(el("span", null, label), track, el("span", "val", fmt(v)));
    d.append(row);
  }
  return d;
}

function box(cls, b, ...extra) {
  const d = el("div", `box ${cls}`);
  d.append(el("h2", null, b.title), ...extra, el("p", "src", b.src));
  return d;
}

const root = document.getElementById("root");
const { where: w, age: a, job: j, bits: b, kids: k, rules: r } = T;
const grid = el("div", "grid");
grid.append(
  box("where", w, el("p", null, w.text), bars(w.bars, (v) => `$${v.toFixed(2)}`), el("p", null, w.after)),
  box("age", a, el("p", "big", a.big), el("p", null, a.text), el("p", null, a.barsTitle), bars(a.bars, (v) => `${v}%`, "red")),
  box("job", j, el("p", null, j.text), el("p", null, j.text2)),
  box("bits", b, el("p", null, b.text), el("p", null, b.text2)),
  box("kids", k, el("p", "big", k.big), el("p", null, k.text)),
  box("rules", r, el("p", null, r.text)),
);
const ol = el("ol", "sources");
for (const s of T.sources) ol.append(el("li", null, s));
root.append(el("h1", null, T.title), el("p", "sub", T.sub), grid, el("p", "end", T.end), el("p", "note", T.sourcesTitle), ol);
document.title = T.title.replace(/^\S+ /, "");
