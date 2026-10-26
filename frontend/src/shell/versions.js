// Version history: a slide-in panel listing earlier copies of a note, a read-only view of one, a line diff
// against the current text, and "Restore this version".
import { api } from "../api.js";
import { el, icon } from "./dom.js";
import { confirmDialog } from "./dialogs.js";
import { toast, toastOk } from "./toast.js";

let panel = null;
let owner = null;   // path of the note the panel belongs to
export const versionsOpenFor = () => (panel ? owner : null);
export function closeVersions() { if (panel) { panel.remove(); panel = null; owner = null; } }

const pad = (n) => String(n).padStart(2, "0");
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
export function whenWords(id, now = new Date()) {
  const m = /^(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})$/.exec(id);
  if (!m) return id;
  return whenDate(new Date(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +m[6]), now);
}
export function whenDate(d, now = new Date()) {
  const time = `${pad(d.getHours())}:${pad(d.getMinutes())}`;
  const day = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
  const diff = Math.round((day(now) - day(d)) / 86400000);
  if (diff === 0) return "Today " + time;
  if (diff === 1) return "Yesterday " + time;
  return `${d.getDate()} ${MONTHS[d.getMonth()]}${d.getFullYear() !== now.getFullYear() ? " " + d.getFullYear() : ""} ${time}`;
}
export function sizeWords(n) { return n < 1024 ? n + " B" : n < 1048576 ? (n / 1024).toFixed(1).replace(/\.0$/, "") + " KB" : (n / 1048576).toFixed(1) + " MB"; }

// Tiny line diff: trim the shared start and end, then a longest-common-subsequence table for the middle.
export function lineDiff(oldText, newText) {
  const a = oldText.split("\n"), b = newText.split("\n");
  let s = 0;
  while (s < a.length && s < b.length && a[s] === b[s]) s++;
  let ea = a.length, eb = b.length;
  while (ea > s && eb > s && a[ea - 1] === b[eb - 1]) { ea--; eb--; }
  const out = [];
  for (let i = 0; i < s; i++) out.push({ t: " ", s: a[i] });
  const n = ea - s, m = eb - s;
  if (n * m > 2_000_000) {                       // too big for the table: show the middle as replaced
    for (let i = s; i < ea; i++) out.push({ t: "-", s: a[i] });
    for (let j = s; j < eb; j++) out.push({ t: "+", s: b[j] });
  } else {
    const w = m + 1, L = new Uint32Array((n + 1) * w);
    for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--)
      L[i * w + j] = a[s + i] === b[s + j] ? L[(i + 1) * w + j + 1] + 1 : Math.max(L[(i + 1) * w + j], L[i * w + j + 1]);
    let i = 0, j = 0;
    while (i < n && j < m) {
      if (a[s + i] === b[s + j]) { out.push({ t: " ", s: a[s + i] }); i++; j++; }
      else if (L[(i + 1) * w + j] >= L[i * w + j + 1]) out.push({ t: "-", s: a[s + i++] });
      else out.push({ t: "+", s: b[s + j++] });
    }
    while (i < n) out.push({ t: "-", s: a[s + i++] });
    while (j < m) out.push({ t: "+", s: b[s + j++] });
  }
  for (let i = ea; i < a.length; i++) out.push({ t: " ", s: a[i] });
  return out;
}

// ctx: { host (element to attach to), path, currentText(), restore(text) -> Promise }
export async function openVersions(ctx) {
  if (panel && owner === ctx.path) { closeVersions(); return; }
  closeVersions();
  owner = ctx.path;
  const body = el("div", { class: "vh-body" });
  const head = el("div", { class: "vh-head" }, el("div", { class: "vh-title" }, "Version history"),
    el("button", { class: "icon-btn", title: "Close", "aria-label": "Close", onclick: closeVersions }, icon("x", 14, 2)));
  panel = el("aside", { class: "vh", "aria-label": "Version history" }, head, body);
  ctx.host.append(panel);
  const mine = panel;
  const alive = () => panel === mine;

  const showList = async () => {
    body.replaceChildren(el("div", { class: "vh-empty" }, "Loading…"));
    let list = [];
    try { list = (await api("versions", { path: ctx.path })).versions || []; } catch (e) { toast(e.message, "error"); }
    if (!alive()) return;
    if (!list.length) {
      body.replaceChildren(el("div", { class: "vh-empty" }, "No earlier versions yet.", el("br"), "A copy is kept as you edit, at most one every few minutes."));
      return;
    }
    body.replaceChildren(el("div", { class: "vh-list" }, ...list.map((v) =>
      el("button", { class: "vh-item", onclick: () => showOne(v) }, el("span", {}, whenWords(v.id)), el("span", { class: "vh-size" }, sizeWords(v.size))))));
  };

  const showOne = async (v) => {
    body.replaceChildren(el("div", { class: "vh-empty" }, "Loading…"));
    let text;
    try { text = (await api("version", { path: ctx.path, id: v.id })).text || ""; } catch (e) { toast(e.message, "error"); showList(); return; }
    if (!alive()) return;
    const view = el("div", { class: "vh-view" });
    let mode = "diff";
    const tabs = el("div", { class: "seg small" });
    const draw = () => {
      tabs.replaceChildren(...[["diff", "Changes"], ["text", "Text"]].map(([k, t]) => el("button", { class: "seg-b" + (mode === k ? " on" : ""), onclick: () => { mode = k; draw(); } }, t)));
      if (mode === "text") { view.replaceChildren(el("pre", { class: "vh-text" }, text)); return; }
      const rows = lineDiff(text, ctx.currentText());
      if (!rows.some((r) => r.t !== " ")) { view.replaceChildren(el("div", { class: "vh-empty" }, "Same as the note now.")); return; }
      const frag = [];
      let i = 0;
      while (i < rows.length) {
        if (rows[i].t === " ") {
          let j = i; while (j < rows.length && rows[j].t === " ") j++;
          const run = rows.slice(i, j), first = i === 0, last = j === rows.length;
          const keepHead = first ? 0 : 2, keepTail = last ? 0 : 2;
          if (run.length > keepHead + keepTail + 1) {
            run.slice(0, keepHead).forEach((r) => frag.push(r));
            frag.push({ t: "…", s: `${run.length - keepHead - keepTail} unchanged lines` });
            run.slice(run.length - keepTail).forEach((r) => frag.push(r));
          } else run.forEach((r) => frag.push(r));
          i = j;
        } else frag.push(rows[i++]);
      }
      view.replaceChildren(el("div", { class: "vh-diff" }, ...frag.map((r) =>
        el("div", { class: "dl " + (r.t === "+" ? "add" : r.t === "-" ? "del" : r.t === "…" ? "gap" : "") }, el("span", { class: "dl-m" }, r.t === " " || r.t === "…" ? "" : r.t), el("span", { class: "dl-t" }, r.s || " ")))));
    };
    draw();
    const restore = el("button", { class: "btn primary small", onclick: async () => {
      const ok = await confirmDialog(`Restore the version from ${whenWords(v.id)}? This replaces the text of the note.`, "Restore", false);
      if (!ok) return;
      try { await ctx.restore(text); toastOk("Version restored."); closeVersions(); } catch (e) { toast(e.message, "error"); }
    } }, "Restore this version");
    body.replaceChildren(
      el("div", { class: "vh-bar" }, el("button", { class: "btn small", onclick: showList }, icon("back", 12, 2), "All"), el("span", { class: "vh-when" }, whenWords(v.id)), restore),
      el("div", { class: "vh-sub" }, "Read-only. ", tabs), view);
  };
  showList();
}
