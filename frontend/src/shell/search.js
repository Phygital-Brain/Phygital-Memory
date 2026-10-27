// The search view: Engram search over the open folder, as a tab. Results on the left (note, section, a snippet
// with the words marked, why it matched), the whole matching section on the right. Enter opens the note at that
// section. Everything from notes is put in as text only.
import { el, icon } from "./dom.js";

const WORD = /[\p{L}\p{N}][\p{L}\p{N}'_-]*/gu;

// Put text in `parent`, wrapping every word of the question in <mark>.
function marked(parent, text, words) {
  if (!words.length) { parent.append(text); return; }
  const re = new RegExp(`(${words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`, "giu");
  let last = 0;
  for (const m of text.matchAll(re)) {
    if (m.index > last) parent.append(text.slice(last, m.index));
    parent.append(el("mark", {}, m[0]));
    last = m.index + m[0].length;
  }
  if (last < text.length) parent.append(text.slice(last));
}

// Engram marks the matched words of a snippet with \x02 and \x03; those become <mark>s.
function engramMarks(parent, text) {
  const parts = text.split(/\x02|\x03/);
  parts.forEach((part, i) => { if (part) parent.append(i % 2 ? el("mark", {}, part) : part); });
}

// (older Engram snippets used [brackets] around matches)
function unbracket(text, words) {
  const low = words.map((w) => w.toLowerCase());
  return text.replace(/\[([^\[\]\n]{1,60})\]/g, (m, inner) => (low.some((w) => inner.toLowerCase().includes(w)) ? inner : m));
}

const when = (ts) => {
  if (!ts) return "";
  const d = new Date(ts * 1000), now = new Date();
  return d.toDateString() === now.toDateString() ? "Today" : d.toLocaleDateString([], { day: "numeric", month: "short", year: d.getFullYear() === now.getFullYear() ? undefined : "numeric" });
};

// opts: {api(action, body), openAt(path, heading), folders() -> ["Projects", ...], recent(n) -> [paths]}
export function createSearchView(opts) {
  const input = el("input", { class: "sv-input", type: "search", placeholder: "Search your notes", spellcheck: "false",
                              "aria-label": "Search notes" });
  const within = el("select", { class: "sv-within", "aria-label": "Search inside" });
  const order = el("select", { class: "sv-order", "aria-label": "Order" },
    el("option", { value: "best" }, "Best match"), el("option", { value: "new" }, "Newest first"));
  const count = el("span", { class: "sv-count" });
  const list = el("div", { class: "sv-list", role: "listbox", "aria-label": "Results" });
  const preview = el("div", { class: "sv-preview" });
  const root = el("div", { class: "sv" },
    el("div", { class: "sv-bar" }, el("span", { class: "sv-icon" }, icon("search", 17)), input),
    el("div", { class: "sv-filters" }, within, order, count),
    el("div", { class: "sv-body" }, list, preview));

  let rows = [], sel = -1, timer = 0, seq = 0, words = [];

  function fillWithin() {
    const cur = within.value;
    within.replaceChildren(el("option", { value: "" }, "Everywhere"), ...opts.folders().map((f) => el("option", { value: f }, `In ${f}`)));
    within.value = [...within.options].some((o) => o.value === cur) ? cur : "";
  }

  async function run() {
    const q = input.value.trim(), mine = ++seq;
    words = q.match(WORD) || [];
    if (!q) { rows = []; draw(); return; }
    let got = [];
    try { got = (await opts.api("search", { q, within: within.value, n: 30 })).results || []; } catch { got = []; }
    if (mine !== seq) return;
    rows = order.value === "new" ? got.slice().sort((a, b) => (b.date || 0) - (a.date || 0)) : got;
    sel = rows.length ? 0 : -1;
    draw();
  }

  function draw() {
    count.textContent = input.value.trim() ? `${rows.length} result${rows.length === 1 ? "" : "s"}` : "";
    if (!input.value.trim()) {
      const recent = opts.recent(8);
      list.replaceChildren(el("div", { class: "sv-hint" }, "Type to search every note in this folder. Words, names, phrases; "
        + "put a phrase in \"quotes\" to match it exactly."),
        ...(recent.length ? [el("div", { class: "sv-sub" }, "Recent notes"),
          ...recent.map((p) => el("button", { class: "sv-recent", type: "button", onclick: () => opts.openAt(p, "") },
            icon("file", 14), p.replace(/\.md$/i, "")))] : []));
      preview.replaceChildren();
      return;
    }
    if (!rows.length) {
      list.replaceChildren(el("div", { class: "sv-hint" }, "Nothing found. Try fewer or different words."));
      preview.replaceChildren();
      return;
    }
    list.replaceChildren(...rows.map((r, i) => {
      const parts = r.heading.split(" > ");
      const title = parts[0], section = parts.slice(1).join(" › ");
      const item = el("div", { class: "sv-item" + (i === sel ? " on" : ""), role: "option", "aria-selected": i === sel ? "true" : "false",
                               onclick: () => { sel = i; draw(); }, ondblclick: () => open(i) });
      const head = el("div", { class: "sv-title" });
      marked(head, title.replace(/[-_]/g, " "), words);
      const meta = el("div", { class: "sv-meta" }, el("span", { class: "sv-path" }, r.path.replace(/\.md$/i, "")),
        r.date ? el("span", {}, when(r.date)) : null, r.exact ? el("span", { class: "sv-exact" }, "exact") : null);
      const snip = el("div", { class: "sv-snippet" });
      engramMarks(snip, r.snippet || "");
      item.append(head, section ? el("div", { class: "sv-section" }, "› " + section) : null, snip, meta,
        r.why ? el("div", { class: "sv-why", title: "Why this result" }, r.why) : null);
      return item;
    }));
    list.querySelector(".sv-item.on")?.scrollIntoView({ block: "nearest" });
    showPreview();
  }

  async function showPreview() {
    const r = rows[sel];
    if (!r) { preview.replaceChildren(); return; }
    const mine = seq;
    preview.replaceChildren(el("div", { class: "sv-loading" }, ""));
    let full = null;
    try { full = await opts.api("result", { id: r.id }); } catch {}
    if (mine !== seq || rows[sel] !== r) return;
    const body = el("div", { class: "sv-text" });
    marked(body, (full && full.text) || r.snippet || "", words);
    preview.replaceChildren(
      el("div", { class: "sv-ptitle" }, r.heading.split(" > ").join(" › ")),
      el("div", { class: "sv-ppath" }, r.path),
      body,
      el("div", { class: "sv-pactions" },
        el("button", { class: "btn primary small", type: "button", onclick: () => open(sel) }, "Open note ↵")));
  }

  function open(i) {
    const r = rows[i];
    if (r) opts.openAt(r.path, r.heading.split(" > ").slice(1).pop() || "");
  }

  input.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(run, 90); });
  within.addEventListener("change", run);
  order.addEventListener("change", run);
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" && rows.length) { e.preventDefault(); sel = Math.min(rows.length - 1, sel + 1); draw(); }
    else if (e.key === "ArrowUp" && rows.length) { e.preventDefault(); sel = Math.max(0, sel - 1); draw(); }
    else if (e.key === "Enter") { e.preventDefault(); open(sel); }
  });

  return {
    root,
    focus() { fillWithin(); input.focus(); const n = input.value.length; input.setSelectionRange(n, n); if (!input.value) draw(); },   // caret at the end: typing carries on
    setQuery(q) { input.value = q; run(); },
    refresh() { fillWithin(); if (input.value.trim()) run(); else draw(); },
  };
}
