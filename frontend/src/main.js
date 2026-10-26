import { api, setPass, onLocked, forgetFiles, fileURL, uploadFile } from "./api.js";
import { createEditor } from "./editor.js";
import { el, icon } from "./shell/dom.js";
import { splitFM, parseYaml, headFor } from "./shell/frontmatter.js";
import { askText, confirmDialog, toast } from "./shell/dialogs.js";
import "./styles.css";

const PALETTE = ["#7c5cff", "#cf3f8e", "#d9773a", "#3f8850", "#23877e", "#2f86bf", "#5262d0", "#c98a12", "#d24d43", "#6f9a2c"];
const BAD_NAME = /[\/\\:*?"<>|]/;

const state = {
  files: [],            // [{path, kind}]
  tabs: [],
  active: null,
  open: new Set(),      // expanded folder paths
  sortDesc: false,
};

const isMd = (p) => /\.md$/i.test(p);
const isImg = (p) => /\.(png|jpe?g|gif|webp|svg|avif)$/i.test(p);
const baseName = (p) => p.split("/").pop();
const dirOf = (p) => (p.includes("/") ? p.slice(0, p.lastIndexOf("/")) : "");
const label = (p) => baseName(p).replace(/\.md$/i, "");
const join = (d, n) => (d ? d + "/" + n : n);
const exists = (p) => state.files.some((f) => f.path.toLowerCase() === p.toLowerCase());
function hashColor(name) {
  let h = 5381;
  for (const c of name) h = ((h << 5) + h + c.charCodeAt(0)) >>> 0;
  return PALETTE[h % PALETTE.length];
}
function uniqueName(dir, base, ext) {
  let n = 1, name;
  do { name = n === 1 ? base + ext : `${base} ${n}${ext}`; n++; } while (exists(join(dir, name)));
  return name;
}

// ---------- page skeleton ----------
const root = document.getElementById("app");
const unlockEl = el("div", { class: "unlock hidden" });
const appEl = el("div", { class: "app hidden" });
root.append(unlockEl, appEl);

// ---------- unlock ----------
function buildUnlock() {
  const pw = el("input", { type: "password", placeholder: "Password", autocomplete: "off", "aria-label": "Password" });
  const err = el("div", { class: "unlock-err" });
  const btn = el("button", { class: "btn primary", type: "submit" }, "Unlock");
  const form = el("form", { class: "unlock-card", onsubmit: async (e) => {
    e.preventDefault();
    err.textContent = "";
    btn.disabled = true;
    try {
      const j = await api("unlock", { password: pw.value });
      setPass(j.pass);
      pw.value = "";
      await enterApp();
    } catch (x) { err.textContent = x.message; pw.select(); }
    btn.disabled = false;
  } },
  el("div", { class: "wordmark" }, "Phygital ", el("span", {}, "Memory")),
  el("div", { class: "unlock-sub" }, "Your notes are locked."),
  pw, btn, err);
  unlockEl.replaceChildren(form);
  unlockEl._focus = () => pw.focus();
}

function showUnlock() {
  appEl.classList.add("hidden");
  unlockEl.classList.remove("hidden");
  unlockEl._focus && unlockEl._focus();
}

function teardown() {
  for (const t of state.tabs) { clearTimeout(t.timer); t.editor && t.editor.destroy(); }
  state.tabs = []; state.active = null; state.files = [];
  forgetFiles();
  setPass(null);
  closeSearch();
  closeMenu();
  showUnlock();
}
onLocked(teardown);

async function doLock() {
  await Promise.all(state.tabs.map((t) => saveNow(t)));
  try { await api("lock"); } catch {}
  teardown();
}

// ---------- app shell ----------
let treeEl, tabsEl, paneHost, statusEl, sidebarEl;

function buildApp() {
  sidebarEl = el("aside", { class: "sidebar" });
  const resize = el("div", { class: "sb-resize", title: "Drag to resize" });
  resize.addEventListener("pointerdown", (e) => {
    resize.setPointerCapture(e.pointerId);
    resize.classList.add("on");
    const move = (ev) => { sidebarEl.style.width = Math.max(200, Math.min(420, ev.clientX)) + "px"; };
    const up = () => { resize.classList.remove("on"); resize.removeEventListener("pointermove", move); resize.removeEventListener("pointerup", up); };
    resize.addEventListener("pointermove", move);
    resize.addEventListener("pointerup", up);
  });

  const ib = (name, title, fn) => el("button", { class: "icon-btn", title, "aria-label": title, onclick: fn }, icon(name, 15));
  const sortBtn = ib("sort", "Sort: Name A–Z", () => {
    state.sortDesc = !state.sortDesc;
    sortBtn.title = state.sortDesc ? "Sort: Name Z–A" : "Sort: Name A–Z";
    renderTree();
  });

  treeEl = el("div", { class: "tree", role: "tree" });
  treeEl.addEventListener("dragover", (e) => { if (dragPath && e.target === treeEl) { e.preventDefault(); treeEl.classList.add("drop"); } });
  treeEl.addEventListener("dragleave", (e) => { if (e.target === treeEl) treeEl.classList.remove("drop"); });
  treeEl.addEventListener("drop", (e) => { if (e.target === treeEl) { e.preventDefault(); treeEl.classList.remove("drop"); moveInto(dragPath, ""); } });
  treeEl.addEventListener("contextmenu", (e) => { if (e.target === treeEl) e.preventDefault(); });

  sidebarEl.append(
    el("div", { class: "sb-head" },
      el("div", { class: "app-icon" }, icon("file", 16, 2)),
      el("div", { class: "sb-titles" }, el("div", { class: "sb-name" }, "Phygital Memory"), el("div", { class: "sb-folder" }, "Locked notes"))),
    el("div", { class: "sb-section" },
      el("span", {}, "NOTES"),
      el("span", { class: "sb-actions" },
        ib("plus", "New note", () => newNote()),
        ib("folderplus", "New folder", newFolder),
        ib("collapse", "Collapse all", () => { state.open.clear(); renderTree(); }),
        sortBtn)),
    treeEl,
    el("div", { class: "sb-foot" },
      el("span", { class: "sb-note" }, "🔒 Encrypted · AI reads through Engram"),
      el("button", { class: "btn small", onclick: doLock }, icon("lock", 13), "Lock")),
    resize);

  tabsEl = el("div", { class: "tabs", role: "tablist" });
  statusEl = el("div", { class: "status" });
  paneHost = el("div", { class: "panes" });
  const empty = el("div", { class: "empty" }, "Cmd+N for a new note, Cmd+K to find one.");
  paneHost.append(empty);
  paneHost._empty = empty;

  appEl.replaceChildren(sidebarEl, el("main", { class: "main" }, el("div", { class: "tabbar" }, tabsEl, statusEl), paneHost));
}

async function enterApp() {
  unlockEl.classList.add("hidden");
  appEl.classList.remove("hidden");
  buildApp();
  await loadFiles();
  renderTabs();
}

async function loadFiles() {
  const j = await api("files");
  state.files = (j.files || []).filter((f) => !baseName(f.path).startsWith("."));
  renderTree();
}

// ---------- tree ----------
let dragPath = null;

function buildTree() {
  const root = { children: new Map(), path: "" };
  for (const f of state.files) {
    const parts = f.path.split("/");
    let node = root;
    parts.forEach((part, i) => {
      const p = parts.slice(0, i + 1).join("/");
      let c = node.children.get(part);
      if (!c) { c = { name: part, path: p, kind: "folder", children: new Map() }; node.children.set(part, c); }
      if (i === parts.length - 1) c.kind = f.kind;
      node = c;
    });
  }
  return root;
}

function renderTree() {
  if (!treeEl) return;
  const rows = [];
  const walk = (node, depth) => {
    const kids = [...node.children.values()].sort((a, b) => {
      const fa = a.kind === "folder", fb = b.kind === "folder";
      if (fa !== fb) return fa ? -1 : 1;
      const c = a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: "base" });
      return state.sortDesc ? -c : c;
    });
    for (const n of kids) {
      rows.push(rowFor(n, depth));
      if (n.kind === "folder" && state.open.has(n.path)) walk(n, depth + 1);
    }
  };
  walk(buildTree(), 0);
  treeEl.replaceChildren(...rows);
}

function rowFor(n, depth) {
  const folder = n.kind === "folder";
  const cur = state.active && state.active.path === n.path;
  const open = state.open.has(n.path);
  const ic = folder ? icon("folder", 16) : icon(isImg(n.name) ? "image" : "file", 16);
  if (folder) ic.style.color = hashColor(n.name);
  const more = el("button", { class: "row-more", title: "More", "aria-label": "More", onclick: (e) => { e.stopPropagation(); const r = e.currentTarget.getBoundingClientRect(); showMenu(n, r.left, r.bottom + 4); } }, icon("more", 15));
  const row = el("div", {
    class: "row" + (cur ? " active" : ""), role: "treeitem", draggable: true, style: `padding-left:${8 + depth * 14}px`,
    onclick: () => {
      if (folder) { state.open.has(n.path) ? state.open.delete(n.path) : state.open.add(n.path); renderTree(); }
      else openPath(n.path);
    },
    oncontextmenu: (e) => { e.preventDefault(); showMenu(n, e.clientX, e.clientY); },
    ondragstart: (e) => { dragPath = n.path; e.dataTransfer.setData("text/plain", n.path); e.dataTransfer.effectAllowed = "move"; },
    ondragend: () => { dragPath = null; document.querySelectorAll(".row.drop").forEach((r) => r.classList.remove("drop")); },
  },
  el("span", { class: "chev" + (folder ? (open ? " open" : "") : " none") }, icon("chevron", 12, 2)),
  ic,
  el("span", { class: "row-name" }, folder || !isMd(n.name) ? n.name : label(n.name)),
  more);
  if (folder) {
    row.addEventListener("dragover", (e) => { if (dragPath) { e.preventDefault(); row.classList.add("drop"); } });
    row.addEventListener("dragleave", () => row.classList.remove("drop"));
    row.addEventListener("drop", (e) => { e.preventDefault(); e.stopPropagation(); row.classList.remove("drop"); moveInto(dragPath, n.path); });
  }
  return row;
}

// context menu
let menuEl = null;
function closeMenu() { if (menuEl) { menuEl.remove(); menuEl = null; } }
function showMenu(n, x, y) {
  closeMenu();
  const item = (text, fn, cls) => el("button", { class: "menu-item " + (cls || ""), onclick: () => { closeMenu(); fn(); } }, text);
  menuEl = el("div", { class: "menu", role: "menu" }, item("Rename", () => renameDialog(n)), item("Move to trash", () => trashDialog(n), "danger"));
  document.body.append(menuEl);
  const w = menuEl.offsetWidth, h = menuEl.offsetHeight;
  menuEl.style.left = Math.min(x, innerWidth - w - 8) + "px";
  menuEl.style.top = Math.min(y, innerHeight - h - 8) + "px";
}
document.addEventListener("mousedown", (e) => { if (menuEl && !menuEl.contains(e.target)) closeMenu(); });

// ---------- file operations ----------
function validName(name) {
  if (!name.trim()) return "Name can't be empty.";
  if (BAD_NAME.test(name)) return 'Names can\'t have / \\ : * ? " < > |';
  if (name.trim().startsWith(".")) return "Name can't start with a dot.";
  return "";
}

function retarget(from, to) {
  for (const t of state.tabs) {
    if (t.path === from) t.path = to;
    else if (t.path.startsWith(from + "/")) t.path = to + t.path.slice(from.length);
  }
  const reopen = [...state.open].filter((p) => p === from || p.startsWith(from + "/"));
  for (const p of reopen) { state.open.delete(p); state.open.add(to + p.slice(from.length)); }
}

async function moveItem(from, to) {
  const affected = state.tabs.filter((t) => t.path === from || t.path.startsWith(from + "/"));
  await Promise.all(affected.map((t) => saveNow(t)));
  const j = await api("move", { from, to });
  retarget(from, j.path || to);
  await loadFiles();
  renderTabs();
  syncTitle();
  return j.path || to;
}

async function moveInto(from, folder) {
  if (!from) return;
  if (folder === from || folder.startsWith(from + "/")) return;
  if (dirOf(from) === folder) return;
  const to = join(folder, baseName(from));
  if (exists(to)) { toast(`"${baseName(from)}" already exists there.`); return; }
  try { await moveItem(from, to); if (folder) state.open.add(folder); renderTree(); } catch (e) { toast(e.message); }
}

async function renameTo(n, input) {
  const name = input.trim();
  const bad = validName(name);
  if (bad) throw new Error(bad);
  const isNote = n.kind !== "folder" && isMd(n.path);
  const finalName = isNote ? name.replace(/\.md$/i, "") + ".md" : name;
  const to = join(dirOf(n.path), finalName);
  if (to === n.path) return n.path;
  if (exists(to) && to.toLowerCase() !== n.path.toLowerCase()) throw new Error(`"${finalName}" already exists.`);
  return moveItem(n.path, to);
}

async function renameDialog(n) {
  const isNote = n.kind !== "folder" && isMd(n.path);
  const v = await askText("Rename", isNote ? label(n.path) : baseName(n.path), "Rename", (val) => validName(val));
  if (v == null) return;
  try { await renameTo(n, v); } catch (e) { toast(e.message); }
}

async function trashDialog(n) {
  const ok = await confirmDialog(`Move "${isMd(n.name) ? label(n.name) : n.name}" to trash?`, "Move to trash", true);
  if (!ok) return;
  try {
    await api("trash", { path: n.path });
    for (const t of [...state.tabs]) if (t.path === n.path || t.path.startsWith(n.path + "/")) closeTab(t, true);
    await loadFiles();
  } catch (e) { toast(e.message); }
}

async function newNote(dir = "", opts = {}) {
  const name = opts.name || uniqueName(dir, "Untitled", ".md");
  const path = join(dir, name);
  try {
    await api("save", { path, text: opts.text || "", new: true });
    await loadFiles();
    await openPath(path, { focusTitle: !opts.name });
  } catch (e) { toast(e.message); }
}

async function newFolder() {
  const v = await askText("New folder", "", "Create", (val) => validName(val));
  if (v == null) return;
  const path = v.trim();
  if (exists(path)) { toast(`"${path}" already exists.`); return; }
  try { await api("mkdir", { path }); await loadFiles(); } catch (e) { toast(e.message); }
}

// ---------- links ----------
function findNote(target, cur) {
  const t = target.split("#")[0].trim().replace(/^\/+/, "");
  if (!t) return cur ? cur.path : null;
  const lc = t.toLowerCase().replace(/\.md$/, "");
  const notes = state.files.filter((f) => f.kind === "file" && isMd(f.path));
  const exact = notes.find((n) => n.path.toLowerCase().replace(/\.md$/, "") === lc);
  if (exact) return exact.path;
  const b = lc.split("/").pop();
  const hit = notes.find((n) => baseName(n.path).toLowerCase().replace(/\.md$/, "") === b);
  return hit ? hit.path : null;
}

async function followLink(target, tab) {
  const found = findNote(target, tab);
  if (found) return openPath(found);
  const t = target.split("#")[0].trim().replace(/\.md$/i, "");
  if (!t || BAD_NAME.test(t.replace(/\//g, ""))) { toast("Can't make a note with that name."); return; }
  const ok = await confirmDialog(`No note called "${t}". Create it?`, "Create", false);
  if (ok) newNote(dirOf(t), { name: baseName(t) + ".md" });
}

// ---------- tabs ----------
async function openPath(path, opts = {}) {
  let tab = state.tabs.find((t) => t.path === path);
  if (!tab) {
    try {
      if (isMd(path)) tab = await makeNoteTab(path);
      else if (isImg(path)) tab = makeImageTab(path);
      else { toast("This file type can't be opened here."); return; }
    } catch (e) { toast(e.message); return; }
    state.tabs.push(tab);
  }
  activate(tab, opts);
}

function makeImageTab(path) {
  const img = el("img", { class: "img-view", alt: "" });
  fileURL(path).then((u) => { img.src = u; }).catch((e) => toast(e.message));
  const pane = el("div", { class: "pane hidden" }, el("div", { class: "note-col" }, el("h1", { class: "img-title" }, baseName(path)), img));
  paneHost.append(pane);
  return { path, kind: "image", pane, dirty: false };
}

async function makeNoteTab(path) {
  const j = await api("read", { path });
  const text = j.text || "";
  const sp = splitFM(text);
  let fm = { mode: "none", head: "", props: [], raw: "", changed: false };
  if (sp.yaml !== null) {
    const props = parseYaml(sp.yaml);
    fm = props ? { mode: "props", head: sp.head, props, raw: sp.yaml, changed: false } : { mode: "raw", head: sp.head, props: [], raw: sp.yaml, changed: false };
  }
  const tab = { path, kind: "note", fm, body: sp.body, dirty: false, saving: false, ver: 0, timer: null, chain: Promise.resolve(), err: null, editor: null };
  tab.titleEl = el("input", { class: "title", spellcheck: "false", "aria-label": "Note title", value: label(path) });
  tab.titleErr = el("div", { class: "title-err" });
  tab.propsEl = el("div", { class: "props" });
  tab.host = el("div", { class: "editor-host" });
  tab.pane = el("div", { class: "pane hidden" }, el("div", { class: "note-col" }, tab.titleEl, tab.titleErr, tab.propsEl, tab.host));
  paneHost.append(tab.pane);
  wireTitle(tab);
  renderProps(tab);
  return tab;
}

function wireTitle(tab) {
  const t = tab.titleEl;
  let busy = false;
  const commit = async () => {
    if (busy) return;
    const val = t.value.trim();
    if (val === label(tab.path)) { tab.titleErr.textContent = ""; return; }
    busy = true;
    try {
      await renameTo({ path: tab.path, kind: "file", name: baseName(tab.path) }, val);
      tab.titleErr.textContent = "";
    } catch (e) {
      tab.titleErr.textContent = e.message;
      t.focus();
    }
    busy = false;
  };
  t.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); commit().then(() => { if (!tab.titleErr.textContent && tab.editor) tab.editor.focus(); }); }
    else if (e.key === "Escape") { t.value = label(tab.path); tab.titleErr.textContent = ""; tab.editor && tab.editor.focus(); }
  });
  t.addEventListener("blur", commit);
}

function syncTitle() {
  for (const t of state.tabs) if (t.titleEl && document.activeElement !== t.titleEl) t.titleEl.value = label(t.path);
}

function ensureEditor(tab) {
  if (tab.editor || tab.kind !== "note") return;
  tab.editor = createEditor(tab.host, {
    text: tab.body,
    onChange: (text) => { tab.body = text; touch(tab); },
    onSave: () => saveNow(tab),
    openLink: (target) => followLink(target, tab),
    noteNames: () => state.files.filter((f) => f.kind === "file" && isMd(f.path)).map((f) => f.path),
    attachmentNames: () => state.files.filter((f) => f.kind === "file" && !isMd(f.path)).map((f) => f.path),
    resolveFile: (name) => {
      const lc = name.toLowerCase();
      const files = state.files.filter((f) => f.kind === "file");
      const full = files.find((f) => f.path.toLowerCase() === lc);
      if (full) return full.path;
      const b = baseName(lc);
      const hit = files.find((f) => baseName(f.path).toLowerCase() === b);
      return hit ? hit.path : null;
    },
    loadImage: (path) => fileURL(path),
    uploadFile: async (file) => {
      const dir = dirOf(tab.path);
      const folder = join(dir, "attachments");
      const dot = file.name.lastIndexOf(".");
      const base = dot > 0 ? file.name.slice(0, dot) : file.name, ext = dot > 0 ? file.name.slice(dot) : "";
      const path = join(folder, uniqueName(folder, base, ext));
      try { await api("mkdir", { path: folder }); } catch {}
      const j = await uploadFile(path, file);
      loadFiles().catch(() => {});
      return (j && j.path) || path;
    },
  });
}

function touch(tab) {
  tab.ver++;
  tab.dirty = true;
  clearTimeout(tab.timer);
  tab.timer = setTimeout(() => saveNow(tab), 800);
  renderStatus();
  renderTabs();
}

function compose(tab) {
  const head = tab.fm.changed ? headFor(tab.fm.props) : tab.fm.head;
  return head + tab.body;
}

function saveNow(tab) {
  if (tab.kind !== "note") return Promise.resolve();
  clearTimeout(tab.timer);
  tab.chain = tab.chain.then(async () => {
    if (!tab.dirty) return;
    const v = tab.ver;
    tab.saving = true; renderStatus();
    try {
      await api("save", { path: tab.path, text: compose(tab) });
      if (tab.ver === v) tab.dirty = false;
      tab.err = null;
    } catch (e) { tab.err = e.message; }
    tab.saving = false;
    renderStatus(); renderTabs();
  });
  return tab.chain;
}

function renderStatus() {
  if (!statusEl) return;
  const t = state.active;
  let s = "", cls = "";
  if (t && t.kind === "note") {
    if (t.err) { s = "Save failed"; cls = "bad"; }
    else if (t.saving) s = "Saving…";
    else if (t.dirty) s = "Unsaved";
    else s = "Saved";
  }
  statusEl.textContent = s;
  statusEl.className = "status " + cls;
  if (t && t.err) statusEl.title = t.err; else statusEl.removeAttribute("title");
}

function activate(tab, opts = {}) {
  state.active = tab;
  for (const t of state.tabs) t.pane.classList.toggle("hidden", t !== tab);
  paneHost._empty.classList.add("hidden");
  if (isMd(tab.path)) { let p = dirOf(tab.path); while (p) { state.open.add(p); p = dirOf(p); } }
  else { let p = dirOf(tab.path); while (p) { state.open.add(p); p = dirOf(p); } }
  ensureEditor(tab);
  renderTabs(); renderTree(); renderStatus();
  if (tab.kind === "note") {
    requestAnimationFrame(() => {
      tab.editor.refresh();
      if (opts.focusTitle) { tab.titleEl.focus(); tab.titleEl.select(); } else tab.editor.focus();
    });
  }
}

async function closeTab(tab, force) {
  if (!force) await saveNow(tab);
  clearTimeout(tab.timer);
  const i = state.tabs.indexOf(tab);
  if (i < 0) return;
  state.tabs.splice(i, 1);
  tab.editor && tab.editor.destroy();
  tab.pane.remove();
  if (state.active === tab) {
    const next = state.tabs[Math.min(i, state.tabs.length - 1)];
    if (next) activate(next);
    else { state.active = null; paneHost._empty.classList.remove("hidden"); renderTabs(); renderTree(); renderStatus(); }
  } else renderTabs();
}

function cycleTab(dir) {
  if (state.tabs.length < 2) return;
  const i = state.tabs.indexOf(state.active);
  activate(state.tabs[(i + dir + state.tabs.length) % state.tabs.length]);
}

function renderTabs() {
  if (!tabsEl) return;
  const nodes = state.tabs.map((t) => {
    const on = t === state.active;
    const el1 = el("div", {
      class: "tab" + (on ? " active" : ""), role: "tab", title: t.path,
      onclick: () => activate(t),
      onauxclick: (e) => { if (e.button === 1) { e.preventDefault(); closeTab(t); } },
      onmousedown: (e) => { if (e.button === 1) e.preventDefault(); },
    }, el("span", { class: "tab-label" }, label(t.path)),
    t.dirty ? el("span", { class: "dot", title: "Unsaved" }) : null,
    el("button", { class: "tab-x", title: "Close", "aria-label": "Close tab", onclick: (e) => { e.stopPropagation(); closeTab(t); } }, icon("x", 12, 2)));
    return el1;
  });
  nodes.push(el("button", { class: "tab-plus", title: "New note (Cmd+N)", "aria-label": "New note", onclick: () => newNote() }, icon("plus", 15)));
  tabsEl.replaceChildren(...nodes);
  const a = tabsEl.querySelector(".tab.active");
  if (a) a.scrollIntoView({ block: "nearest", inline: "nearest" });
}

// ---------- properties ----------
const KEY_OK = /^[A-Za-z0-9_][A-Za-z0-9_\- ]*$/;

function renderProps(tab) {
  const host = tab.propsEl;
  host.replaceChildren();
  const fm = tab.fm;
  if (fm.mode === "raw") {
    host.append(el("div", { class: "props-label" }, "Properties (shown as written, read-only)"), el("pre", { class: "props-raw" }, fm.raw));
    return;
  }
  const changed = () => { fm.changed = true; fm.mode = "props"; touch(tab); };
  const rows = fm.props.map((p) => {
    const keyIn = el("input", { class: "prop-key", value: p.key, spellcheck: "false", "aria-label": "Property name" });
    keyIn.addEventListener("change", () => {
      const k = keyIn.value.trim();
      if (!KEY_OK.test(k) || fm.props.some((q) => q !== p && q.key === k)) { keyIn.value = p.key; return; }
      p.key = k; changed();
    });
    let val;
    if (p.kind === "list") {
      const chips = p.items.map((it, i) => el("span", { class: "chip" }, (p.key === "tags" ? "#" : "") + it,
        el("button", { class: "chip-x", "aria-label": "Remove", onclick: () => { p.items.splice(i, 1); changed(); renderProps(tab); } }, "×")));
      const add = el("input", { class: "chip-add", placeholder: "Add", "aria-label": "Add item" });
      const commit = () => {
        const v = add.value.trim().replace(/^#/, "").replace(/,$/, "");
        if (!v) return false;
        p.items.push(v); changed(); renderProps(tab); return true;
      };
      add.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === ",") { e.preventDefault(); if (commit()) host.querySelectorAll(".chip-add")[fm.props.indexOf(p)]?.focus(); }
        else if (e.key === "Backspace" && !add.value && p.items.length) { p.items.pop(); changed(); renderProps(tab); host.querySelectorAll(".chip-add")[fm.props.indexOf(p)]?.focus(); }
      });
      add.addEventListener("blur", commit);
      val = el("div", { class: "prop-val chips" }, ...chips, add);
    } else if (p.value === "true" || p.value === "false") {
      val = el("div", { class: "prop-val" }, el("input", { type: "checkbox", checked: p.value === "true", onchange: (e) => { p.value = e.target.checked ? "true" : "false"; changed(); } }));
    } else {
      const inp = el("input", { class: "prop-text", value: p.value, spellcheck: "false", "aria-label": p.key });
      inp.addEventListener("input", () => { p.value = inp.value; changed(); });
      val = el("div", { class: "prop-val" }, inp);
    }
    return el("div", { class: "prop" }, keyIn, val,
      el("button", { class: "prop-rm", title: "Remove property", "aria-label": "Remove property", onclick: () => { fm.props.splice(fm.props.indexOf(p), 1); changed(); renderProps(tab); } }, icon("x", 12, 2)));
  });
  const addBtn = el("button", { class: "prop-add" + (rows.length ? "" : " faint"), onclick: () => {
    const inp = el("input", { class: "prop-key new", placeholder: "Property name", spellcheck: "false" });
    const done = (ok) => {
      const k = inp.value.trim();
      if (ok && KEY_OK.test(k) && !fm.props.some((q) => q.key === k)) {
        fm.props.push(["tags", "aliases"].includes(k) ? { key: k, kind: "list", items: [], style: "inline" } : { key: k, kind: "scalar", value: "" });
        changed(); renderProps(tab);
        const rowsNow = host.querySelectorAll(".prop");
        const last = rowsNow[rowsNow.length - 1];
        last && last.querySelector(".prop-text, .chip-add") && last.querySelector(".prop-text, .chip-add").focus();
      } else renderProps(tab);
    };
    inp.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); inp.removeEventListener("blur", onBlur); done(true); } else if (e.key === "Escape") { inp.removeEventListener("blur", onBlur); done(false); } });
    const onBlur = () => done(false);
    inp.addEventListener("blur", onBlur);
    addBtn.replaceWith(inp); inp.focus();
  } }, "+ Add property");
  host.append(...rows, addBtn);
}

// ---------- search overlay ----------
let searchEl = null;
function closeSearch() { if (searchEl) { searchEl.remove(); searchEl = null; } }

function openSearch() {
  if (searchEl) { searchEl.querySelector("input").focus(); return; }
  let items = [], sel = 0, token = 0, timer = null;
  const input = el("input", { class: "s-input", placeholder: "Search notes or jump to one…", spellcheck: "false", "aria-label": "Search" });
  const list = el("div", { class: "s-list" });
  const box = el("div", { class: "s-box", role: "dialog" }, el("div", { class: "s-bar" }, icon("search", 16), input), list);
  searchEl = el("div", { class: "overlay", onmousedown: (e) => { if (e.target === searchEl) closeSearch(); } }, box);
  document.body.append(searchEl);
  input.focus();

  const draw = () => {
    list.replaceChildren(...(items.length ? items.map((it, i) => el("div", {
      class: "s-item" + (i === sel ? " sel" : ""), onmousemove: () => { if (sel !== i) { sel = i; mark(); } }, onclick: () => choose(it),
    }, icon("file", 15),
    el("div", { class: "s-text" },
      el("div", { class: "s-title" }, label(it.path), it.heading ? el("span", { class: "s-head" }, " › " + it.heading) : null, dirOf(it.path) ? el("span", { class: "s-path" }, dirOf(it.path)) : null),
      it.snippet ? el("div", { class: "s-snip" }, it.snippet) : null))) : [el("div", { class: "s-none" }, input.value ? "Nothing found." : "No notes yet.")]));
  };
  const mark = () => {
    [...list.children].forEach((c, i) => c.classList.toggle("sel", i === sel));
    const c = list.children[sel]; c && c.scrollIntoView({ block: "nearest" });
  };
  const choose = (it) => { if (!it) return; closeSearch(); openPath(it.path); };

  const update = () => {
    const q = input.value.trim().toLowerCase();
    const words = q.split(/\s+/).filter(Boolean);
    const names = state.files.filter((f) => f.kind === "file" && isMd(f.path))
      .filter((f) => words.every((w) => f.path.toLowerCase().includes(w)))
      .sort((a, b) => label(a.path).localeCompare(label(b.path)))
      .slice(0, q ? 8 : 50).map((f) => ({ path: f.path }));
    items = names; sel = 0; draw();
    clearTimeout(timer);
    if (q.length >= 2) {
      const my = ++token;
      timer = setTimeout(async () => {
        try {
          const j = await api("search", { q: input.value.trim() });
          if (my !== token || !searchEl) return;
          const seen = new Set(names.map((n) => n.path));
          items = names.concat((j.results || []).map((r) => ({ path: r.path, heading: r.heading, snippet: r.snippet })).filter((r) => r.heading || r.snippet || !seen.has(r.path)));
          draw();
        } catch {}
      }, 180);
    } else token++;
  };
  input.addEventListener("input", update);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { e.preventDefault(); closeSearch(); }
    else if (e.key === "ArrowDown") { e.preventDefault(); if (items.length) { sel = (sel + 1) % items.length; mark(); } }
    else if (e.key === "ArrowUp") { e.preventDefault(); if (items.length) { sel = (sel - 1 + items.length) % items.length; mark(); } }
    else if (e.key === "Enter") { e.preventDefault(); choose(items[sel]); }
  });
  update();
}

// ---------- keyboard ----------
window.addEventListener("keydown", (e) => {
  if (appEl.classList.contains("hidden")) return;
  const mod = e.metaKey || e.ctrlKey;
  const k = e.key.toLowerCase();
  if (e.ctrlKey && e.key === "Tab") { e.preventDefault(); cycleTab(e.shiftKey ? -1 : 1); return; }
  if (!mod || e.altKey) return;
  if (k === "k" || k === "p") { e.preventDefault(); openSearch(); }
  else if (k === "f" && !e.shiftKey) {
    if (e.target.closest && e.target.closest(".cm-editor")) return;   // the editor has its own find
    e.preventDefault(); openSearch();
  }
  else if (k === "n") { e.preventDefault(); newNote(); }
  else if (k === "w") { e.preventDefault(); if (state.active) closeTab(state.active); }
  else if (k === "s") { e.preventDefault(); if (state.active) saveNow(state.active); }
}, true);
window.addEventListener("beforeunload", (e) => { if (state.tabs.some((t) => t.dirty)) { e.preventDefault(); e.returnValue = ""; } });

// ---------- start ----------
(async function start() {
  buildUnlock();
  try {
    const j = await api("devunlock");
    if (j && j.pass) { setPass(j.pass); await enterApp(); return; }
  } catch {}
  showUnlock();
})();
