import { api, setPass, setFolder, currentFolder, forgetPass, hasPass, onLocked, forgetFiles, fileURL, uploadFile, readFileText, readFileForEdit, writeFileText, decodeStrict } from "./api.js";
import { csvEditor, parseCsv, CSV_EDIT_MAX_ROWS } from "./shell/csvedit.js";
import { docxEditor } from "./shell/docxedit.js";
import { createEditor } from "./editor.js";
import { el, icon } from "./shell/dom.js";
import { splitFM, parseYaml, headFor } from "./shell/frontmatter.js";
import { askText, confirmDialog } from "./shell/dialogs.js";
import { toast, toastOk, toastErr } from "./shell/toast.js";
import { showMenu, closeMenu } from "./shell/menu.js";
import { loadPrefs, clearPrefs, flushPrefs, takePrefs, givePrefs, getPref, setPref, setMapPref, noteState, setNoteState, movePrefs, dropPrefs } from "./shell/prefs.js";
import { openSettings, closeSettings, onSettings, settings } from "./shell/settings.js";
import { openVersions, closeVersions, versionsOpenFor, whenDate } from "./shell/versions.js";
import { createGraph } from "./shell/graph.js";
import { createSearchView } from "./shell/search.js";
import { switcherItems, createFolderForm, manageFolders, folderTile, shortPath } from "./shell/folders.js";
import { openStorage, openAIPanel, openTrash, openGithubSignIn } from "./shell/panels.js";
import { CSV, PDF, VIDEO, AUDIO, csvTable } from "./ed/media.js";
import "./styles.css";

const PALETTE = ["#7c5cff", "#cf3f8e", "#d9773a", "#3f8850", "#23877e", "#2f86bf", "#5262d0", "#c98a12", "#d24d43", "#6f9a2c"];
const BAD_NAME = /[\/\\:*?"<>|]/;

const state = {
  files: [],            // [{path, kind, mtime, size}]
  tabs: [],
  active: null,
  open: new Set(),      // expanded folder paths
  sel: new Set(),       // multi-selected paths in the sidebar
  anchor: null,         // where a Shift-click range starts
  visible: [],          // sidebar rows in order, for Shift ranges
  tags: [],             // [[tag, count]] for the editor's # suggestions
  lastNote: null,       // last note tab the person looked at (the graph's "current" note)
};
const HOME_ID = "::home", GRAPH_ID = "::graph", SEARCH_ID = "::search";   // names can't hold ":", so these never clash with a real path

const isMd = (p) => /\.md$/i.test(p);
const isImg = (p) => /\.(png|jpe?g|gif|webp|svg|avif)$/i.test(p);
const baseName = (p) => p.split("/").pop();
const dirOf = (p) => (p.includes("/") ? p.slice(0, p.lastIndexOf("/")) : "");
const label = (p) => baseName(p).replace(/\.md$/i, "");
const tabLabel = (t) => t.title || label(t.path);
const isSpecial = (t) => t.kind === "graph" || t.kind === "home" || t.kind === "search";
const colorsPref = () => getPref("colors", {});
function folderColor(path) { return colorsPref()[path] || hashColor(baseName(path)); }
function nodeColor(path) { const d = dirOf(path); return d ? folderColor(d) : PALETTE[0]; }
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
const unlockDrag = el("div", { class: "win-drag-top", "data-tauri-drag-region": "" });   // no title bar: drag the window here
const appEl = el("div", { class: "app hidden" });
root.append(unlockEl, appEl);

// ---------- folders ----------
// Every locked folder keeps its own screen in memory while you look at another one: tabs, open tree folders,
// settings, Finder state. Switching back is instant and nothing unsaved is lost.
let folderList = [];          // [{id, name, path, open, exists, finder}] from the server
let loadedFolder = null;      // the folder whose screen is in `state` right now (null on an unlock screen)
const views = new Map();      // folder id -> its screen, while another folder is in front
let backId = null;            // the folder the unlock screen offers to go back to
let sbWidth = "";

const curInfo = () => folderList.find((f) => f.id === currentFolder()) || null;
const unlocked = (id) => hasPass(id) && !!(folderList.find((f) => f.id === id) || {}).open;

async function refreshFolders() {
  try { folderList = (await api("folders")).folders || []; } catch { return folderList; }
  drawSwitcher();
  watchFolders();
  return folderList;
}

function resetState() {
  Object.assign(state, { files: [], tabs: [], active: null, open: new Set(), sel: new Set(), anchor: null, visible: [], tags: [], lastNote: null });
  blToken++; blData = [];
}

// Take a folder's screen out of the window and keep it in memory.
function detachTab(t) {
  clearTimeout(t.timer);
  if (t.kind === "note") { t.editor && t.editor.destroy(); t.editor = null; t.host && t.host.replaceChildren(); }
  else if (t.kind === "graph") { t.onClose && t.onClose(); t.onClose = null; t.graph = null; t.sig = ""; t.stale = true; }
  else if (t.kind === "image") t.stale = true;   // decrypted images are dropped on a switch; they load again on return
  t.pane && t.pane.remove();
}

async function stashLoaded() {
  const fid = loadedFolder;
  await Promise.all(state.tabs.map((t) => saveNow(t)));
  await flushPrefs();
  clearTimeout(linksTimer); clearInterval(finderTimer); finderTimer = null;
  closeSearch(); closeMenu(); closeVersions(); closeSettings(); closeBacklinks();
  sbWidth = sidebarEl ? sidebarEl.style.width : sbWidth;
  const view = { files: state.files, tabs: state.tabs, active: state.active, open: state.open, tags: state.tags, lastNote: state.lastNote, finder, prefs: takePrefs() };
  state.tabs.forEach(detachTab);
  views.delete(fid); views.set(fid, view);
  backId = fid;
  resetState();
  finder = { shown: false, available: false, where: "", confirmed: false };
  loadedFolder = null;
}

function rebuildPane(t) {
  if (t.kind === "graph") makeGraphPane(t);
  else if (t.kind === "search") makeSearchPane(t);
  else t.pane = (t.make === "file" ? makeFileTab(t.path) : makeImageTab(t.path)).pane;
  t.stale = false;
}

function restoreView(fid) {
  const v = views.get(fid);
  views.delete(fid);
  unlockEl.classList.add("hidden");
  appEl.classList.remove("hidden");
  Object.assign(state, { files: v.files, tabs: v.tabs, open: v.open, tags: v.tags, lastNote: v.lastNote, sel: new Set(), anchor: null, active: null });
  givePrefs(v.prefs);
  finder = v.finder;
  loadedFolder = fid;
  for (const t of state.tabs) { if (t.stale) rebuildPane(t); t.pane.classList.add("hidden"); paneHost.append(t.pane); }
  drawSwitcher(); drawFinder(); renderTree();
  const first = state.tabs.includes(v.active) ? v.active : state.tabs[0];
  if (first) activate(first);
  else { paneHost._empty.classList.remove("hidden"); noteTools.classList.add("hidden"); renderTabs(); renderStatus(); refreshBacklinks(); }
  for (const t of state.tabs) if (t.dirty) saveNow(t);
  loadFiles().catch(() => {});
  checkFinder(true);
}

// The folder's screen is gone (locked, or taken off the list).
function clearLoaded() {
  for (const t of state.tabs) { clearTimeout(t.timer); t.editor && t.editor.destroy(); t.onClose && t.onClose(); t.pane && t.pane.remove(); }
  resetState();
  clearInterval(finderTimer); finderTimer = null; clearTimeout(linksTimer);
  finder = { shown: false, available: false, where: "", confirmed: false };
  clearPrefs();
  closeSearch(); closeMenu(); closeVersions(); closeSettings(); closeBacklinks();
  loadedFolder = null;
}
function dropView(fid) {
  const v = views.get(fid);
  if (!v) return;
  views.delete(fid);
  for (const t of v.tabs) { clearTimeout(t.timer); t.editor && t.editor.destroy(); t.onClose && t.onClose(); }
}

function lockedLocally(fid) {
  forgetPass(fid);
  forgetFiles();
  if (fid === loadedFolder) clearLoaded(); else dropView(fid);
  if (backId === fid) backId = null;
  if (fid === currentFolder()) {
    backId = [...views.keys()].filter((k) => hasPass(k)).pop() || null;
    document.querySelectorAll(".toasts").forEach((t) => t.remove());
    showUnlock();
  }
  refreshFolders();
}
onLocked(lockedLocally);

let switching = false;
async function switchTo(id) {
  if (switching || !id) return;
  if (id === currentFolder() && (loadedFolder === id || !hasPass(id))) { if (loadedFolder !== id) showUnlock(); return; }
  switching = true;
  try {
    if (loadedFolder) await stashLoaded();
    setFolder(id);
    forgetFiles();
    if (views.has(id) && hasPass(id)) restoreView(id);
    else if (hasPass(id)) await enterApp();
    else showUnlock();
  } catch (e) { toastErr(e.message); }
  switching = false;
  refreshFolders();
}

async function pickFolder(prompt, start) {
  toast("Choose a folder in the window that opens…");
  return (await api("pickfolder", { prompt, ...(start ? { start } : {}) })).path || null;
}

// Another Mac: bring a private "…-Phygital-Memory" repo down from GitHub, then unlock it with its password.
async function openFromGithub() {
  try {
    if (!(await api("githubaccount")).account
        && !(await openGithubSignIn({ start: () => api("githubsignin"), poll: () => api("githubpoll") }))) return;
  } catch (e) { toastErr(e.message); return; }
  const repo = await askText("Open from GitHub", "", "Open", (v) => /^[\w.-]+\/[\w.-]+$/.test(v.trim().replace(/^https:\/\/github\.com\//, "").replace(/\.git$/, "")) ? "" : 'Like "your-name/Notes-Phygital-Memory".');
  if (repo == null) return;
  try {
    toast("Choose where to keep it on this Mac, in the window that opens…");
    const j = await api("fromgithub", { repo });
    if (j.cancelled) return;
    await refreshFolders();
    toastOk(`Brought "${j.folder.name}" down from GitHub. Unlock it with its password.`);
    await switchTo(j.folder.id);
  } catch (e) { toastErr(e.message); }
}

async function openOtherFolder() {
  try {
    const p = await pickFolder("Choose a locked notes folder");
    if (!p) return;
    const j = await api("addfolder", { path: p });
    await refreshFolders();
    toastOk(`Added "${j.folder.name}".`);
    await switchTo(j.folder.id);
  } catch (e) { toastErr(e.message); }
}

async function createNewFolder() {
  const v = await createFolderForm(() => pickFolder("Choose where to put the new folder"));
  if (!v) return;
  try {
    toast("Making the folder…");
    const j = await api("createfolder", v);
    await refreshFolders();
    await switchTo(j.folder.id);
    if (currentFolder() === j.folder.id) await unlockCurrent(v.password);
    toastOk(`Created "${j.folder.name}".`);
  } catch (e) { toastErr(e.message); }
}

async function renameFolder(id) {
  const info = (id && folderList.find((f) => f.id === id)) || curInfo();
  if (!info) return;
  const v = await askText("Rename folder", info.name, "Rename", (x) => (x.trim() ? "" : "Name can't be empty."));
  if (v == null) return;
  try { await api("renamefolder", { folder: info.id, name: v.trim() }); await refreshFolders(); } catch (e) { toastErr(e.message); }
}

async function forgetFolder(id) {
  const info = (id && folderList.find((f) => f.id === id)) || curInfo();
  if (!info) return;
  const ok = await confirmDialog(`Remove "${info.name}" from the list? Nothing is deleted: the folder and its notes stay where they are. It locks, and you can add it again later.`, "Remove from list", true);
  if (!ok) return;
  const fid = info.id;
  try {
    if (loadedFolder === fid) { await Promise.all(state.tabs.map((t) => saveNow(t))); await flushPrefs(); }
    await api("forgetfolder", { folder: fid });
  } catch (e) { toastErr(e.message); return; }
  lockedLocally(fid);
  await refreshFolders();
  const next = folderList.find((f) => views.has(f.id) && hasPass(f.id)) || folderList[0];
  if (next) await switchTo(next.id); else { setFolder(null); showUnlock(); }
  toast(`Removed "${info.name}" from the list.`);
}

async function lockFolder(id) {
  const fid = typeof id === "string" ? id : currentFolder();
  if (loadedFolder === fid) { await Promise.all(state.tabs.map((t) => saveNow(t))); await flushPrefs(); }
  try { await api("lock", { folder: fid }); } catch {}
  lockedLocally(fid);
}

async function lockAll() {
  if (loadedFolder) { await Promise.all(state.tabs.map((t) => saveNow(t))); await flushPrefs(); }
  for (const f of folderList) if (hasPass(f.id)) { try { await api("lock", { folder: f.id }); } catch {} lockedLocally(f.id); }
  showUnlock();
}

// ---------- unlock ----------
async function unlockCurrent(password) {
  const fid = currentFolder();
  const j = await api("unlock", { password, folder: fid });
  setPass(j.pass, fid);
  await enterApp();
}

function drawUnlock() {
  const info = curInfo();
  const kids = [el("div", { class: "wordmark" }, "Phygital ", el("span", {}, "Memory"))];
  const links = [];
  if (info) {
    const pw = el("input", { type: "password", placeholder: "Password", autocomplete: "off", "aria-label": "Password" });
    const err = el("div", { class: "unlock-err" }, info.exists ? "" : "This folder can't be found. It may have moved, or its drive isn't connected.");
    const btn = el("button", { class: "btn primary", type: "submit" }, "Unlock");
    if (folderList.length > 1) {
      const sel = el("select", { class: "unlock-pick", "aria-label": "Folder" },
        ...folderList.map((f) => el("option", { value: f.id }, f.name + (unlocked(f.id) ? " (unlocked)" : ""))));
      sel.value = info.id;
      sel.addEventListener("change", () => switchTo(sel.value));
      kids.push(sel);
    } else kids.push(el("div", { class: "unlock-folder" }, info.name));
    kids.push(el("div", { class: "unlock-sub" }, folderList.length > 1 ? "This folder is locked." : "Your notes are locked."), pw, btn, err);
    unlockEl._submit = async (e) => {
      e.preventDefault();
      if (!pw.value) return;
      err.textContent = ""; btn.disabled = true;
      try { await unlockCurrent(pw.value); pw.value = ""; }
      catch (x) { err.textContent = x.message; pw.select(); }
      btn.disabled = false;
    };
    unlockEl._focus = () => pw.focus();
  } else {
    kids.push(el("div", { class: "unlock-sub" }, "No locked notes folder yet. Open one you already have, or make a new one."));
    unlockEl._submit = (e) => e.preventDefault();
    unlockEl._focus = null;
  }
  if (backId && backId !== currentFolder() && views.has(backId)) {
    const b = folderList.find((f) => f.id === backId);
    if (b) links.push(el("button", { class: "link-btn", type: "button", onclick: () => switchTo(backId) }, `Back to ${b.name}`));
  }
  links.push(el("button", { class: "link-btn", type: "button", onclick: openOtherFolder }, "Open folder…"),
    el("button", { class: "link-btn", type: "button", onclick: createNewFolder }, "New folder…"));
  kids.push(el("div", { class: "unlock-links" }, ...links));
  const form = el("form", { class: "unlock-card", onsubmit: (e) => unlockEl._submit(e) }, ...kids);
  unlockEl.replaceChildren(unlockDrag, form);
}

function showUnlock() {
  appEl.classList.add("hidden");
  drawUnlock();
  unlockEl.classList.remove("hidden");
  unlockEl._focus && unlockEl._focus();
}

// ---------- app shell ----------
let treeEl, tabsEl, paneHost, statusEl, sidebarEl, homeRowEl, selBarEl, finderBtn, noteTools, blPill, sbName, sbBadge, sbPath, sbTile, graphRowEl = null;

function drawSwitcher() {
  if (!sbName) return;
  const info = curInfo();
  sbName.textContent = info ? info.name : "Phygital Memory";
  sbPath.textContent = info ? shortPath(info.path) : "No folder yet";
  sbPath.title = info ? info.path : "";
  sbTile.replaceChildren(folderTile(info || {}, !!(info && unlocked(info.id)), 34));
  refreshBar();
  sbBadge.classList.toggle("hidden", !folderList.some((f) => f.finder && f.id !== currentFolder()));
}

async function openSwitcher() {
  if (!sbName || appEl.classList.contains("hidden")) return;
  await refreshFolders();
  const head = appEl.querySelector(".sb-head");
  const r = head.getBoundingClientRect();
  showMenu(switcherItems({ list: folderList, currentId: currentFolder(), unlocked, switchTo, openOther: openOtherFolder, fromGithub: openFromGithub,
    createNew: createNewFolder, manage: openManage, rename: () => renameFolder(), lockThis: () => lockFolder(), lockAll,
    home: () => goHome(),
    finder: finder.available && unlocked(currentFolder()) ? { shown: finder.shown, toggle: toggleFinder } : null }), r.left + 6, r.bottom + 2);
}

async function openManage() {
  await refreshFolders();
  manageFolders(folderList, { switchTo, rename: renameFolder, lock: lockFolder, forget: forgetFolder, unlocked,
    createNew: createNewFolder, openOther: openOtherFolder });
}

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

  const ib = (name, title, fn) => el("button", { class: "icon-btn", title, "aria-label": title, onclick: fn }, icon(name, 17));
  const sortBtn = ib("sort", "Sort", (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    const cur = getPref("sortMode", "recent");
    showMenu(SORTS.map(([k, t, hint]) => ({ label: t, hint, check: cur === k, fn: () => { setPref("sortMode", k); renderTree(); } })), r.left, r.bottom + 4);
  });

  sbName = el("div", { class: "sb-name" }, "Phygital Memory");
  sbPath = el("div", { class: "sb-folder" }, "");
  sbTile = el("div", { class: "sb-tile" });
  sbBadge = el("span", { class: "fo-badge hidden", title: "Another folder is open in Finder" }, "Finder");
  const sbHead = el("button", { class: "sb-head sb-switch", title: "Switch folder (⇧⌘O)", "aria-haspopup": "menu", onclick: openSwitcher },
    sbTile,
    el("div", { class: "sb-titles" }, sbName, sbPath),
    sbBadge, el("span", { class: "sb-chev" }, icon("updown", 14)));
  if (sbWidth) sidebarEl.style.width = sbWidth;

  treeEl = el("div", { class: "tree", role: "tree" });
  treeEl.addEventListener("dragover", (e) => { if (dragPath && e.target === treeEl) { e.preventDefault(); treeEl.classList.add("drop"); } });
  treeEl.addEventListener("dragleave", (e) => { if (e.target === treeEl) treeEl.classList.remove("drop"); });
  treeEl.addEventListener("drop", (e) => { if (e.target === treeEl) { e.preventDefault(); treeEl.classList.remove("drop"); moveInto(dragPath, ""); } });
  treeEl.addEventListener("contextmenu", (e) => { if (e.target === treeEl) e.preventDefault(); });

  homeRowEl = el("div", { class: "row home-row", role: "button", tabindex: "0", title: "Home (⇧⌘H)", onclick: () => goHome() },
    el("span", { class: "chev none" }, icon("chevron", 12, 2)), icon("home", 18), el("span", { class: "row-name" }, "Home"));
  homeRowEl.addEventListener("keydown", (e) => { if (e.key === "Enter") goHome(); });
  graphRowEl = el("div", { class: "row nav-graph", role: "button", tabindex: "0", title: "Graph view (⌘G)", onclick: () => openGraph() },
    icon("graph", 18), el("span", { class: "row-name" }, "Graph"));
  graphRowEl.addEventListener("keydown", (e) => { if (e.key === "Enter") openGraph(); });
  selBarEl = el("div", { class: "sel-bar hidden" });
  finderBtn = el("button", { class: "icon-btn hidden", title: "Show in Finder", "aria-label": "Show in Finder", onclick: toggleFinder }, icon("folder", 17));

  sidebarEl.append(
    el("div", { class: "win-drag", "data-tauri-drag-region": "" }),   // the window buttons sit here; drag the window by it
    sbHead,
    el("div", { class: "sb-home" }, homeRowEl, graphRowEl),
    el("div", { class: "sb-section" },
      el("span", {}, "NOTES"),
      el("span", { class: "sb-actions" },
        ib("plus", "New note", () => newNote()),
        ib("folderplus", "New subfolder", () => newFolder()),
        ib("collapse", "Collapse all", () => { state.open.clear(); renderTree(); }),
        sortBtn)),
    selBarEl,
    treeEl,
    el("div", { class: "sb-foot" },
      statusBar(),
      el("span", { class: "sb-foot-btns" }, ib("unlock", "Unlocked. Click to lock this folder", () => lockFolder()), ib("trash", "Trash", openTrashPanel), finderBtn, ib("gear", "Settings (⌘,)", openSettingsHere))),
    resize);

  tabsEl = el("div", { class: "tabs", role: "tablist" });
  new ResizeObserver(() => fitTabs()).observe(tabsEl);
  statusEl = el("div", { class: "status", role: "status", "aria-live": "polite" });   // top right of the note, so the top bar never shifts
  paneHost = el("div", { class: "panes" });
  const empty = el("div", { class: "empty" },
    el("div", { class: "empty-card" }, icon("file", 28, 1.4),
      el("div", { class: "empty-title" }, "Nothing open yet"),
      el("div", { class: "empty-sub" }, "Pick a note on the left, or start a new one."),
      el("div", { class: "empty-actions" },
        el("button", { class: "btn primary", onclick: () => newNote() }, icon("plus", 14, 2), "New note"),
        el("button", { class: "btn", onclick: openSearch }, icon("search", 14), "Find a note")),
      el("div", { class: "empty-keys" }, "⌘N new · ⌘K find · ⌘G graph")));
  paneHost.append(empty);
  paneHost._empty = empty;

  noteTools = el("div", { class: "note-tools hidden" },
    el("button", { class: "icon-btn", title: "Undo (⌘Z)", "aria-label": "Undo", onclick: () => editAct("undo") }, icon("undo", 18)),
    el("button", { class: "icon-btn", title: "Redo (⇧⌘Z)", "aria-label": "Redo", onclick: () => editAct("redo") }, icon("redo", 18)),
    el("button", { class: "icon-btn", title: "Give AI a task with this note", "aria-label": "Give AI a task", onclick: giveToAI }, icon("sparkle", 18)),
    el("button", { class: "icon-btn", title: "Version history", "aria-label": "Version history", onclick: toggleVersions }, icon("clock", 18)));
  blPill = el("button", { class: "bl-pill hidden", onclick: toggleBacklinks });
  paneHost.append(statusEl, noteTools, blPill);

  // A small search bar beside the graph button: typing here opens the search page with what you typed.
  const topSearchInput = el("input", { class: "top-search-input", type: "search", placeholder: "Search", spellcheck: "false", "aria-label": "Search notes" });
  topSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); const q = topSearchInput.value.trim(); topSearchInput.value = ""; topSearchInput.blur(); openSearchView(q); }
    else if (e.key === "Escape") { topSearchInput.value = ""; topSearchInput.blur(); }
  });
  topSearchInput.addEventListener("input", () => {
    const q = topSearchInput.value;
    if (q.trim().length >= 2) { topSearchInput.value = ""; openSearchView(q); }
  });
  const searchBtn = el("label", { class: "top-search", title: "Search every note (⇧⌘F)" },
    icon("search", 14), topSearchInput, el("kbd", {}, "⇧⌘F"));
  appEl.replaceChildren(sidebarEl, el("main", { class: "main" }, el("div", { class: "tabbar" }, tabsEl,
    el("button", { class: "tab-plus", title: "New note (⌘N)", "aria-label": "New note", onclick: () => newNote() }, icon("plus", 17)),
    el("span", { class: "tabbar-gap", "data-tauri-drag-region": "" }), searchBtn), paneHost));
}

async function enterApp() {
  unlockEl.classList.add("hidden");
  appEl.classList.remove("hidden");
  resetState();
  loadedFolder = currentFolder();
  buildApp();
  drawSwitcher();
  try { await loadPrefs(); } catch {}
  await loadFiles();
  renderTabs();
  loadLinks();
  checkFinder(true).then(() => {   // "Desktop icon when unlocked" (on by default, in Settings): no Finder window
    if (settings().desktopIcon && finder.available && !finder.shown && loadedFolder === currentFolder()) desktopIcon();
  });
  goHome();
  refreshFolders();
  preloadGraph();
}

// Build the graph quietly in the background after unlocking (libraries, links and the layout), so opening it
// later is instant. It sits outside the tab bar until it's opened.
let pregraph = null;
function preloadGraph() {
  const fid = loadedFolder;
  pregraph = null;
  setTimeout(() => {
    if (loadedFolder !== fid || state.tabs.some((t) => t.kind === "graph")) return;
    const tab = { path: GRAPH_ID, title: "Graph", kind: "graph", dirty: false, sig: "", folder: fid };
    makeGraphPane(tab);
    pregraph = tab;
    loadGraph(tab);
  }, 1200);
}

async function loadFiles() {
  const fid = loadedFolder;
  const j = await api("files");
  if (fid !== loadedFolder) return;
  state.files = (j.files || []).filter((f) => !baseName(f.path).startsWith("."));
  renderTree();
  for (const c of j.conflicts || []) tellConflict(c.path, c.copy);
}
// A note changed in two places (two devices, or here and an AI app). Both versions are kept; say so once.
const toldConflicts = new Set();
function tellConflict(path, copy) {
  const key = currentFolder() + ":" + copy;
  if (toldConflicts.has(key)) return;
  toldConflicts.add(key);
  toast(`"${label(path)}" was changed in two places. Both versions are kept: the other one is "${label(copy)}".`);
  if (state.active && state.active.path === path) flashStatus("Kept both versions", "warn");
}

async function loadLinks() {
  const fid = loadedFolder;
  try { const j = await api("links"); if (fid === loadedFolder) state.tags = j.tags || []; } catch {}
}
let linksTimer = null;
function scheduleLinksRefresh() {
  clearTimeout(linksTimer);
  linksTimer = setTimeout(() => { loadLinks(); refreshBacklinks(); }, 2500);
}

// ---------- show in Finder ----------
let finder = { shown: false, available: false, where: "", confirmed: false };
let finderTimer = null;

async function checkFinder(first) {
  const fid = loadedFolder;
  try {
    const s = await api("finder", { do: "status" });
    if (fid !== loadedFolder) return;
    const was = finder.shown;
    finder.available = !!s.available || !!s.shown; finder.shown = !!s.shown; finder.where = s.where || "";
    if (!finder.shown && was) { await syncFromDisk(); }
    drawFinder();
    refreshFolders();
  } catch (e) { if (first && fid === loadedFolder) finder.available = false; }
}
function drawFinder() {
  if (!finderBtn) return;
  finderBtn.classList.toggle("hidden", !finder.available);
  finderBtn.classList.toggle("on", finder.shown);
  finderBtn.title = finder.shown ? "Close the Finder folder" : "Show in Finder";
  clearInterval(finderTimer); finderTimer = null;
  if (finder.shown) finderTimer = setInterval(async () => { await checkFinder(); if (finder.shown) syncFromDisk(); }, 10000);
}
// Settings with this folder's options (Show in Finder). Resolves the switch's new state.
function openSettingsHere() {
  const info = curInfo();
  openSettings(info && unlocked(info.id) ? {
    name: info.name, finderShown: finder.shown, finderAvailable: finder.available, where: shortPath(info.path),
    toggleFinder: async () => { await toggleFinder(); return finder.shown; },
    rename: () => renameFolder(), storage: openStoragePanel, lock: () => lockFolder(),
    lockAll: folderList.filter((f) => unlocked(f.id)).length > 1 ? lockAll : null,
    revealVault: () => api("finder", { do: "revealvault" }).catch((e) => toastErr(e.message)),
  } : null);
}

// ---------- the small status icons at the bottom of the sidebar ----------
// Where the folder lives (a cloud, or only this Mac), and a light for AI apps.
let barEls = null, barTimer = null;
function statusBar() {
  const pill = (cls, title) => el("button", { class: "sb-stat " + cls, type: "button", title });
  barEls = {
    cloud: pill("st-cloud", ""),
    ai: pill("st-ai", ""),
  };
  barEls.cloud.style.cursor = barEls.ai.style.cursor = "pointer";
  barEls.cloud.addEventListener("click", openStoragePanel);
  barEls.ai.addEventListener("click", () => openAI(openTasks ? "tasks" : "activity"));
  clearInterval(barTimer);
  barTimer = setInterval(refreshBar, 15000);
  clearInterval(genTimer);
  lastGen = null;
  genTimer = setInterval(watchChanges, 3000);
  setTimeout(refreshBar, 300);
  return el("span", { class: "sb-stats" }, barEls.cloud, barEls.ai);
}

// An AI app or another device changed a note: reload the open notes that have no unsaved edits.
let genTimer = null, lastGen = null;
async function watchChanges() {
  if (!barEls || !barEls.cloud.isConnected) return;
  let g;
  try { g = (await api("gen")).gen; } catch { return; }
  if (g == null) return;
  if (lastGen != null && g !== lastGen) await syncFromDisk();
  lastGen = g;
}

async function refreshBar() {
  watchTodo();
  if (!barEls || !barEls.cloud.isConnected) return;
  let b = null;
  try { b = await api("bar"); } catch { return; }
  barEls.cloud.replaceChildren(icon(b.cloud ? "cloud" : "laptop", 16, 1.8));
  barEls.cloud.classList.toggle("on", !!b.cloud);
  barEls.cloud.title = b.cloud ? `Saved in ${b.cloud}, encrypted. The cloud only sees scrambled files.` : "Only on this Mac.";
  aiApps = b.ai || [];
  drawAI();
}

// The one AI button: glows while an AI app is working, shows how many tasks wait, opens the AI panel.
let aiApps = [], openTasks = 0;
function drawAI() {
  if (!barEls) return;
  const recent = aiApps.filter((a) => a.ago < 120);
  barEls.ai.replaceChildren(icon("pulse", 16, 1.8), ...(openTasks ? [el("span", { class: "ai-count" }, String(openTasks))] : []));
  barEls.ai.classList.toggle("on", recent.length > 0);
  const ago = (s) => (s < 60 ? "just now" : `${Math.round(s / 60)} min ago`);
  barEls.ai.title = "AI: tasks and activity\n"
    + (openTasks ? `${openTasks} task${openTasks === 1 ? "" : "s"} waiting\n` : "No tasks waiting\n")
    + (aiApps.length ? "Using your notes: " + aiApps.map((a) => `${a.name}, ${ago(a.ago)}`).join("; ") : "No AI app is using your notes right now.");
  barEls.ai.setAttribute("aria-label", openTasks ? `AI, ${openTasks} tasks waiting` : "AI");
}

async function openStoragePanel() {
  const info = curInfo();
  if (!info || !unlocked(info.id)) return;
  let storage;
  try { storage = await api("storage"); } catch (e) { toastErr(e.message); return; }
  const moved = await openStorage({
    name: info.name, storage,
    pick: (prompt, start) => pickFolder(prompt, start),
    stopGithub: async (repo) => {
      const sure = await confirmDialog(`Stop keeping "${info.name}" in GitHub? It becomes Mac only: your notes stay here, untouched, and nothing more goes to GitHub. The repo ${repo} is NOT deleted by the app: its scrambled copy stays on GitHub until you delete it there.`, "Stop GitHub sync", true);
      if (!sure) return false;
      await api("stopgithub");
      refreshBar();
      if (await confirmDialog(`GitHub sync stopped. "${info.name}" is on this Mac only. Open ${repo} on GitHub to delete it? (Settings, at the bottom: Delete this repository.)`, "Open on GitHub", false)) {
        await api("openrepo", { repo });
      }
      return true;
    },
    toGithub: async () => {
      let account = (await api("githubaccount")).account;   // the first time the app talks to GitHub
      if (!account) {
        account = await openGithubSignIn({ start: () => api("githubsignin"), poll: () => api("githubpoll") });
        if (!account) return false;
      }
      const sure = await confirmDialog(`Keep "${info.name}" in a new private repo on the GitHub account ${account}? Only scrambled files go up, and the app keeps them in step. The repo always stays private.`, "Use private GitHub", false);
      if (!sure) return false;
      toast("Making the private repo and sending the scrambled files…");
      await api("togithub");
      toastOk("Kept in a private GitHub repo. Changes go up a few seconds after you make them.");
      refreshBar();
      return true;
    },
    download: async () => { const j = await api("download"); toastOk(`Asked your cloud app for ${j.asked} file${j.asked === 1 ? "" : "s"}. They download in the background.`); },
    reveal: () => api("finder", { do: "revealvault" }).catch((e) => toastErr(e.message)),
    move: async (parent, label) => {
      const sure = await confirmDialog(`Move "${info.name}" to ${label}? It locks first, then only the scrambled files move. You unlock it again after.`, `Move to ${label}`, false);
      if (!sure) return false;
      if (loadedFolder === info.id) { await Promise.all(state.tabs.map((t) => saveNow(t))); await flushPrefs(); }
      await api("movefolder", { parent });
      toastOk(`Moved to ${label}. Unlock it again to keep working.`);
      return true;
    },
  });
  if (moved) { lockedLocally(info.id); await refreshFolders(); showUnlock(); }
}

async function openTrashPanel() {
  let items;
  try { items = (await api("trashlist")).items || []; } catch (e) { toastErr(e.message); return; }
  await openTrash({
    items,
    restore: async (id) => {
      const j = await api("trashrestore", { id });
      await loadFiles(); loadLinks();
      toastOk(`Restored "${label(j.path)}".`);
      return { path: j.path, items: (await api("trashlist")).items || [] };
    },
    open: (p) => openPath(p),
  });
}


// Click a note's path: copy it in the form you need.
function copyPathMenu(path, anchor) {
  const r = anchor.getBoundingClientRect();
  const copy = (text, what) => navigator.clipboard.writeText(text)
    .then(() => toastOk(`${what} copied`)).catch(() => toastErr("Couldn't copy."));
  const name = path.split("/").pop().replace(/\.md$/i, "");
  const items = [
    { label: "Copy path", hint: path, fn: () => copy(path, "Path") },
    { label: "Copy link", hint: `[[${name}]]`, fn: () => copy(`[[${name}]]`, "Link") },
  ];
  if (finder.shown && finder.where) {
    const full = `${finder.where}/${path}`;
    items.push({ label: "Copy Finder path", hint: shortPath(full), fn: () => copy(full, "Finder path") });
  }
  showMenu(items, r.left, r.bottom + 4);
}

// Show one note (or file) selected in Finder. Opens the folder in Finder first if needed (with the usual warning).
async function revealInFinder(path) {
  if (!finder.shown) {
    await toggleFinder();
    if (!finder.shown) return;
  }
  try { await api("finder", { do: "reveal", path }); } catch (e) { toastErr(e.message); }
}

async function toggleFinder() {
  if (finder.shown) { hideFinder(); return; }
  if (!finder.confirmed) {
    const ok = await confirmDialog("While the folder is open in Finder, any app on this Mac can read your notes, including AI tools that run commands. It closes when you lock.", "Show in Finder", false);
    if (!ok) return;
    finder.confirmed = true;
  }
  toast("Opening Finder…");
  finderBtn.disabled = true;
  const fid = loadedFolder;
  try {
    const s = await api("finder", { do: "show" });
    if (fid !== loadedFolder) { refreshFolders(); return; }
    finder.shown = !!s.shown; finder.where = s.where || "";
    if (finder.shown) toastOk("Opened in Finder."); else toastErr("Couldn't open Finder.");
  } catch (e) { toastErr(e.message); }
  finderBtn.disabled = false;
  drawFinder();
  refreshFolders();
}
// Mount the Finder view quietly: only its icon on the Desktop, no window and no messages.
async function desktopIcon() {
  const fid = loadedFolder;
  try {
    const s = await api("finder", { do: "show", window: false });
    if (fid !== loadedFolder) return;
    finder.shown = !!s.shown; finder.where = s.where || ""; finder.confirmed = true;
    drawFinder();
    refreshFolders();
  } catch {}
}
async function hideFinder() {
  try { await api("finder", { do: "hide" }); } catch (e) { toastErr(e.message); }
  finder.shown = false;
  drawFinder();
  refreshFolders();
  syncFromDisk();
}
// Changes made in Finder: refresh the tree, and reload open notes that changed (unless they have unsaved edits).
async function syncFromDisk() {
  try { await loadFiles(); } catch { return; }
  for (const t of [...state.tabs]) {
    if (t.docx && t.editable && !t.dirty && !t.saving && exists(t.path)) {
      try { const j = await api("docxread", { path: t.path, folder: t.folder }); if (j.base !== t.base && !t.dirty) t.show(j); } catch {}
      continue;
    }
    if (t.editable && !t.dirty && !t.saving && exists(t.path)) {
      try { const text = await readFileForEdit(t.path); if (text !== null && text !== t.base && !t.dirty) t.show(text); } catch {}
      continue;
    }
    if (t.kind !== "note" || t.dirty || t.saving) continue;
    if (!exists(t.path)) continue;
    try {
      const j = await api("read", { path: t.path });
      if (t.dirty || t.saving || (j.text || "") === compose(t)) continue;
      applyText(t, j.text || "");
    } catch {}
  }
}

// ---------- tree ----------
let dragPath = null;
const SORTS = [
  ["recent", "Recently modified", "Newest edits first"],
  ["az", "Name A–Z", "Alphabetical"],
  ["za", "Name Z–A", "Reverse alphabetical"],
];

function buildTree() {
  const root = { children: new Map(), path: "", mtime: 0 };
  for (const f of state.files) {
    const parts = f.path.split("/");
    let node = root;
    const m = f.mtime || 0;
    parts.forEach((part, i) => {
      const p = parts.slice(0, i + 1).join("/");
      let c = node.children.get(part);
      if (!c) { c = { name: part, path: p, kind: "folder", children: new Map(), mtime: 0 }; node.children.set(part, c); }
      if (i === parts.length - 1) { c.kind = f.kind; if (f.kind === "file") c.mtime = m; }
      else c.mtime = Math.max(c.mtime, m);
      node = c;
    });
  }
  return root;
}

function folderMode(dirPath) { return getPref("folderSort", {})[dirPath] || getPref("sortMode", "recent"); }

// Manual order (set by dragging) wins over the sort mode.
function sortKids(kids, dirPath) {
  const mode = folderMode(dirPath);
  const byName = (a, b) => a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: "base" });
  const arr = [...kids].sort((a, b) => {
    const fa = a.kind === "folder", fb = b.kind === "folder";
    if (fa !== fb) return fa ? -1 : 1;
    if (mode === "recent") return (b.mtime - a.mtime) || byName(a, b);
    return mode === "za" ? -byName(a, b) : byName(a, b);
  });
  const manual = getPref("order", {})[dirPath];
  if (Array.isArray(manual) && manual.length) {
    const idx = new Map(manual.map((n, i) => [n, i]));
    return arr.filter((k) => idx.has(k.name)).sort((a, b) => idx.get(a.name) - idx.get(b.name)).concat(arr.filter((k) => !idx.has(k.name)));
  }
  return arr;
}

function nodeAt(path) {
  let node = buildTree();
  for (const part of path ? path.split("/") : []) { node = node.children.get(part); if (!node) return null; }
  return node;
}

function renderTree() {
  if (!treeEl) return;
  const rows = [];
  state.visible = [];
  const walk = (node, depth) => {
    for (const n of sortKids(node.children.values(), node.path)) {
      rows.push(rowFor(n, depth));
      state.visible.push(n.path);
      if (n.kind === "folder" && state.open.has(n.path)) walk(n, depth + 1);
    }
  };
  walk(buildTree(), 0);
  for (const p of [...state.sel]) if (!exists(p)) state.sel.delete(p);
  treeEl.replaceChildren(...rows);
  drawSelBar();
  if (homeRowEl) {
    const home = getPref("home");
    homeRowEl.classList.toggle("active", !!state.active && (state.active.kind === "home" || (!!home && state.active.path === home)));
  }
}

function drawSelBar() {
  if (!selBarEl) return;
  selBarEl.classList.toggle("hidden", state.sel.size === 0);
  selBarEl.replaceChildren(...(state.sel.size ? [
    el("span", {}, `${state.sel.size} selected`),
    el("span", { class: "sel-btns" },
      el("button", { class: "btn small danger", onclick: () => trashMany([...state.sel]) }, "Move to trash"),
      el("button", { class: "btn small", onclick: () => { state.sel.clear(); renderTree(); } }, "Clear"))] : []));
}

function dropZone(e, row, n) {
  if (!dragPath || dragPath === n.path) return null;
  const same = dirOf(dragPath) === dirOf(n.path);
  const r = row.getBoundingClientRect(), f = (e.clientY - r.top) / r.height;
  if (n.kind === "folder") {
    if (same && f < 0.25) return "before";
    if (same && f > 0.75) return "after";
    return "into";
  }
  return same ? (f < 0.5 ? "before" : "after") : null;
}

function reorder(dragged, target, after) {
  const dir = dirOf(target);
  const node = nodeAt(dir);
  if (!node) return;
  const names = sortKids(node.children.values(), dir).map((k) => k.name).filter((x) => x !== baseName(dragged));
  const i = names.indexOf(baseName(target));
  names.splice(i + (after ? 1 : 0), 0, baseName(dragged));
  setMapPref("order", dir, names);
  renderTree();
}

function rowFor(n, depth) {
  const folder = n.kind === "folder";
  const cur = state.active && state.active.path === n.path;
  const open = state.open.has(n.path);
  const ic = folder ? icon("folder", 18) : icon(isImg(n.name) ? "image" : "file", 18);
  if (folder) ic.style.color = folderColor(n.path);
  const pinned = getPref("pins", []).includes(n.path);
  const more = el("button", { class: "row-more", title: "More", "aria-label": "More", onclick: (e) => { e.stopPropagation(); const r = e.currentTarget.getBoundingClientRect(); rowMenu(n, r.left, r.bottom + 4); } }, icon("more", 15));
  const row = el("div", {
    class: "row" + (cur ? " active" : "") + (state.sel.has(n.path) ? " sel" : ""), role: "treeitem", draggable: true, style: `padding-left:${8 + depth * 14}px`,
    onclick: (e) => {
      if (e.metaKey || e.ctrlKey) {
        state.sel.has(n.path) ? state.sel.delete(n.path) : state.sel.add(n.path);
        state.anchor = n.path; renderTree(); return;
      }
      if (e.shiftKey && state.anchor && state.visible.includes(state.anchor)) {
        const a = state.visible.indexOf(state.anchor), b = state.visible.indexOf(n.path);
        state.sel = new Set(state.visible.slice(Math.min(a, b), Math.max(a, b) + 1)); renderTree(); return;
      }
      state.anchor = n.path;
      if (state.sel.size) { state.sel.clear(); drawSelBar(); treeEl.querySelectorAll(".row.sel").forEach((r) => r.classList.remove("sel")); }
      if (folder) { state.open.has(n.path) ? state.open.delete(n.path) : state.open.add(n.path); renderTree(); }
      else openPath(n.path);
    },
    oncontextmenu: (e) => {
      e.preventDefault();
      if (state.sel.size > 1 && state.sel.has(n.path)) {
        showMenu([{ label: `Move ${state.sel.size} items to trash`, cls: "danger", fn: () => trashMany([...state.sel]) }], e.clientX, e.clientY);
        return;
      }
      if (state.sel.size) { state.sel.clear(); renderTree(); }
      rowMenu(n, e.clientX, e.clientY);
    },
    ondragstart: (e) => { dragPath = n.path; e.dataTransfer.setData("text/plain", n.path); e.dataTransfer.effectAllowed = "move"; },
    ondragend: () => { dragPath = null; clearDropMarks(); },
  },
  el("span", { class: "chev" + (folder ? (open ? " open" : "") : " none") }, icon("chevron", 12, 2)),
  ic,
  el("span", { class: "row-name" }, folder || !isMd(n.name) ? n.name : label(n.name)),
  pinned ? el("span", { class: "row-pin", title: "Pinned" }, icon("pin", 11, 2)) : null,
  more);
  row.addEventListener("dragover", (e) => {
    const z = dropZone(e, row, n);
    if (!z) return;
    e.preventDefault();
    clearDropMarks();
    row.classList.add(z === "into" ? "drop" : "drop-" + z);
  });
  row.addEventListener("dragleave", () => row.classList.remove("drop", "drop-before", "drop-after"));
  row.addEventListener("drop", (e) => {
    const z = dropZone(e, row, n);
    clearDropMarks();
    if (!z) return;
    e.preventDefault(); e.stopPropagation();
    if (z === "into") moveInto(dragPath, n.path); else reorder(dragPath, n.path, z === "after");
  });
  return row;
}
function clearDropMarks() { document.querySelectorAll(".row.drop,.row.drop-before,.row.drop-after,.tree.drop").forEach((r) => r.classList.remove("drop", "drop-before", "drop-after")); }

// context menus
function rowMenu(n, x, y) {
  const folder = n.kind === "folder";
  const pinned = getPref("pins", []).includes(n.path);
  const items = [];
  if (folder) {
    items.push(
      { label: "New note", fn: () => newNote(n.path) },
      { label: "New folder", fn: () => newFolder(n.path) },
      { label: pinned ? "Unpin" : "Pin", fn: () => togglePin(n.path) },
      { sep: true },
      { label: "Import files…", fn: () => importInto(n.path, false) },
      { label: "Import folder…", fn: () => importInto(n.path, true) });
  } else {
    items.push({ label: "Open in new tab", fn: () => openPath(n.path) });
    items.push({ label: pinned ? "Unpin" : "Pin", fn: () => togglePin(n.path) });
    if (isMd(n.path)) items.push({ label: getPref("home") === n.path ? "Unset Home" : "Set as Home", fn: () => setHome(n.path) });
    items.push({ sep: true });
  }
  items.push(
    { label: "Export…", fn: () => exportPath(n.path) },
    { label: "Show in Finder", fn: () => revealInFinder(n.path) },
    { label: "Rename", fn: () => renameDialog(n) });
  if (folder) {
    const swatches = el("div", { class: "swatches" }, ...PALETTE.map((c) =>
      el("button", { class: "swatch" + (colorsPref()[n.path] === c ? " on" : ""), style: `background:${c}`, title: c, "aria-label": "Colour " + c,
        onclick: () => { closeMenu(); setMapPref("colors", n.path, c); renderTree(); } })));
    const mode = folderMode(n.path), own = getPref("folderSort", {})[n.path], manual = (getPref("order", {})[n.path] || []).length;
    items.push(
      { sep: true },
      { label: "Sort by", value: own ? SORTS.find(([k]) => k === own)?.[1] : "Default", sub: [
        ...SORTS.map(([k, t, hint]) => ({ label: t, hint, check: mode === k, fn: () => { setMapPref("folderSort", n.path, k); setMapPref("order", n.path, null); renderTree(); } })),
        ...(own ? [{ sep: true }, { label: "Use the default sort", fn: () => { setMapPref("folderSort", n.path, null); renderTree(); } }] : []),
        ...(manual ? [{ sep: true }, { label: "Reset dragged order", fn: () => { setMapPref("order", n.path, null); renderTree(); } }] : []),
      ] },
      { sep: true },
      { label: "Colour", value: colorsPref()[n.path] ? "" : "Auto", dot: folderColor(n.path), sub: [
        { node: swatches }, { label: "Auto colour", check: !colorsPref()[n.path], fn: () => { setMapPref("colors", n.path, null); renderTree(); } }] });
  }
  items.push({ label: "Move to trash", cls: "danger", fn: () => trashDialog(n) });
  showMenu(items, x, y);
}

// Bring files or a whole folder from the Mac into this folder, encrypted. The Mac's own picker chooses them.
async function importInto(dir, wholeFolder) {
  try {
    const j = await api(wholeFolder ? "importfolder" : "importfiles", { into: dir });
    if (j.cancelled) return;
    if (dir) state.open.add(dir);
    await loadFiles();
    const n = j.imported.length;
    if (n) toastOk(`Imported ${n} file${n === 1 ? "" : "s"}, encrypted.` + (j.skipped ? ` Skipped ${j.skipped} hidden.` : ""));
    else toastErr(j.skipped ? `Nothing imported: only hidden files there.` : "Nothing to import there.");
  } catch (e) { toastErr(e.message); }
}

// A readable (not encrypted) copy of a note, file or folder, to a place picked in the Mac's own box.
async function exportPath(path) {
  await Promise.all(state.tabs.map((t) => saveNow(t)));   // export what's on screen, not an older save
  try {
    const j = await api("export", { path });
    if (j.cancelled) return;
    toastOk(`Exported "${label(path)}". That copy is not encrypted.`);
  } catch (e) { toastErr(e.message); }
}

function togglePin(path) {
  const pins = getPref("pins", []);
  const had = pins.includes(path);
  setPref("pins", had ? pins.filter((p) => p !== path) : [...pins, path]);
  toastOk(had ? `Unpinned "${label(path)}".` : `Pinned "${label(path)}".`);
  renderTree(); refreshHome();
}
function setHome(path) {
  if (getPref("home") === path) { setPref("home", null); toast("Home is back to the built-in page."); }
  else { setPref("home", path); toastOk(`"${label(path)}" is now Home.`); }
  renderTree(); refreshHome();
}

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
  movePrefs(from, j.path || to);
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
  if (exists(to)) { toastErr(`"${baseName(from)}" already exists there.`); return; }
  try { await moveItem(from, to); if (folder) state.open.add(folder); renderTree(); } catch (e) { toastErr(e.message); }
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
  try { await renameTo(n, v); } catch (e) { toastErr(e.message); }
}

async function trashDialog(n) {
  const ok = await confirmDialog(`Move "${isMd(n.name) ? label(n.name) : n.name}" to trash?`, "Move to trash", true);
  if (!ok) return;
  await doTrash([n.path]);
}

async function trashMany(paths) {
  const top = paths.filter((p) => !paths.some((q) => q !== p && p.startsWith(q + "/")));
  const ok = await confirmDialog(`Move ${top.length} item${top.length === 1 ? "" : "s"} to trash?`, "Move to trash", true);
  if (!ok) return;
  state.sel.clear();
  await doTrash(top);
}

async function doTrash(paths) {
  let done = 0;
  for (const p of paths) {
    try {
      await api("trash", { path: p });
      done++;
      dropPrefs(p);
      for (const t of [...state.tabs]) if (t.path === p || t.path.startsWith(p + "/")) closeTab(t, true);
    } catch (e) { toastErr(e.message); }
  }
  try { await loadFiles(); } catch {}
  refreshHome();
  if (done) toastOk(done === 1 ? "Moved to trash." : `Moved ${done} items to trash.`);
}

async function newNote(dir = "", opts = {}) {
  const name = opts.name || uniqueName(dir, "Untitled", ".md");
  if (dir) state.open.add(dir);
  const path = join(dir, name);
  try {
    await api("save", { path, text: opts.text || "", new: true });
    await loadFiles();
    await openPath(path, { focusTitle: !opts.name });
  } catch (e) { toastErr(e.message); }
}

async function newFolder(dir = "") {
  const v = await askText("New subfolder", "", "Create", (val) => validName(val));
  if (v == null) return;
  const path = join(dir, v.trim());
  if (exists(path)) { toastErr(`"${path}" already exists.`); return; }
  try { await api("mkdir", { path }); if (dir) state.open.add(dir); await loadFiles(); } catch (e) { toastErr(e.message); }
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
  if (!t || BAD_NAME.test(t.replace(/\//g, ""))) { toastErr("Can't make a note with that name."); return; }
  const ok = await confirmDialog(`No note called "${t}". Create it?`, "Create", false);
  if (ok) newNote(dirOf(t), { name: baseName(t) + ".md" });
}

// ---------- tabs ----------
function withLoading(promise) {
  let sk = null;
  const timer = setTimeout(() => {
    paneHost._empty.classList.add("hidden");
    sk = el("div", { class: "pane skeleton", "aria-busy": "true", "aria-label": "Opening note" },
      el("div", { class: "note-col" }, el("div", { class: "sk-line sk-title" }),
        ...[92, 100, 84, 96, 60, 0, 88, 97, 72].map((w) => el("div", { class: "sk-line", style: w ? `width:${w}%` : "height:14px;background:none" }))));
    paneHost.append(sk);
  }, 90);
  return promise.finally(() => {
    clearTimeout(timer);
    if (sk) sk.remove();
    if (!state.active && !sk) return;
    if (!state.active) paneHost._empty.classList.remove("hidden");
  });
}

async function openPath(path, opts = {}) {
  let tab = state.tabs.find((t) => t.path === path);
  if (!tab) {
    try {
      if (isMd(path)) tab = await withLoading(makeNoteTab(path));
      else if (isImg(path) && !tooBigToOpen(path)) tab = makeImageTab(path);
      else tab = makeFileTab(path);
    } catch (e) { toastErr(e.message); return; }
    if (state.tabs.some((t) => t.path === path)) { tab.pane.remove(); tab = state.tabs.find((t) => t.path === path); }
    else state.tabs.push(tab);
  }
  activate(tab, opts);
}

function makeImageTab(path) {
  const img = el("img", { class: "img-view", alt: "" });
  fileURL(path).then((u) => { img.src = u; }).catch((e) => toastErr(e.message));
  const pane = el("div", { class: "pane hidden" }, el("div", { class: "note-col" }, el("h1", { class: "img-title" }, baseName(path)), img));
  paneHost.append(pane);
  return { path, kind: "image", make: "img", pane, dirty: false };
}

// Other files open in a tab: CSV/TSV as an editable table, plain text and code in an editable box (both autosave
// like notes), PDF, video and audio as previews, anything else as a card. Decrypted into memory only.
const MAX_OPEN = 25_000_000;   // same as the server's limit for opening a file in the app
const tooBigToOpen = (path) => (state.files.find((f) => f.path === path)?.size || 0) > MAX_OPEN;
const TEXT_EXT = /\.(txt|json|js|mjs|ts|py|rb|go|rs|java|c|h|cpp|css|html|xml|yml|yaml|toml|ini|sh|log|sql)$/i;
function makeFileTab(path) {
  const body = el("div", { class: "file-view" });
  const pane = el("div", { class: "pane hidden" }, el("div", { class: "note-col" }, el("h1", { class: "img-title" }, baseName(path)), body));
  paneHost.append(pane);
  const fail = (e) => { body.replaceChildren(el("p", { class: "file-note" }, `Can't open this file: ${e.message}`)); };
  const tab = { path, kind: "image", make: "file", pane, dirty: false, folder: currentFolder() };
  if (tooBigToOpen(path)) {   // never pulled into the app whole: it opens from Finder, or as an exported copy
    body.replaceChildren(el("p", { class: "file-note" }, "This file is over 25 MB, too big to open inside the app. It's safe and encrypted. Open it from Finder, or export a copy."),
      el("div", { class: "sel-btns" },
        el("button", { class: "btn", type: "button", onclick: () => revealInFinder(path) }, "Show in Finder"),
        el("button", { class: "btn", type: "button", onclick: () => exportPath(path) }, "Export…")));
    return tab;
  }
  if (CSV.test(path) || TEXT_EXT.test(path)) {
    editableFile(tab, body, fail);
    return tab;
  }
  if (/\.docx$/i.test(path)) {
    wordFile(tab, body, fail);
    return tab;
  }
  if (PDF.test(path)) {
    const frame = el("iframe", { class: "file-pdf", title: baseName(path), sandbox: "" });
    fileURL(path).then((u) => { frame.src = u; }).catch(fail);
    body.replaceChildren(frame);
  } else if (VIDEO.test(path) || AUDIO.test(path)) {
    const media = el(VIDEO.test(path) ? "video" : "audio", { class: "file-media", controls: "" });
    fileURL(path).then((u) => { media.src = u; }).catch(fail);
    body.replaceChildren(media);
  } else {
    body.replaceChildren(el("p", { class: "file-note" },
      "This kind of file can't be previewed here. Open it in its own app, or use Show in Finder."),
      el("button", { class: "btn small file-open", type: "button", onclick: () => openInApp(path) }, "Open in its app"));
  }
  return tab;
}

// CSV and text files: shown editable when they are clean UTF-8 and not huge, read-only otherwise.
const EDIT_MAX_CHARS = 2_000_000;
function editableFile(tab, body, fail) {
  const csv = CSV.test(tab.path);
  tab.show = (text) => {
    tab.base = text; tab.text = text;
    const tooBig = text.length > EDIT_MAX_CHARS || (csv && parseCsv(text, /\.tsv$/i.test(tab.path) ? "\t" : ",").length > CSV_EDIT_MAX_ROWS);
    if (tooBig) {
      tab.editable = false;
      body.replaceChildren(el("div", { class: "file-ro" }, "Too big to edit here, shown read-only."),
        csv ? csvTable(text, tab.path) : el("pre", { class: "file-text" }, text.slice(0, EDIT_MAX_CHARS)));
      return;
    }
    tab.editable = true;
    const edited = (t) => { tab.text = t; fileTouch(tab); };
    if (csv) body.replaceChildren(csvEditor(text, tab.path, edited));
    else {
      const box = el("textarea", { class: "file-edit", spellcheck: "false", "aria-label": baseName(tab.path) });
      box.value = text;
      box.addEventListener("input", () => edited(box.value));
      body.replaceChildren(box);
    }
  };
  readFileForEdit(tab.path).then((text) => {
    if (text !== null) { tab.show(text); return; }
    tab.editable = false;   // not clean UTF-8: editing would damage it
    readFileText(tab.path).then((t) => body.replaceChildren(el("div", { class: "file-ro" }, "This file isn't plain UTF-8 text, so it's shown read-only."),
      csv ? csvTable(t, tab.path) : el("pre", { class: "file-text" }, t.slice(0, EDIT_MAX_CHARS)))).catch(fail);
  }).catch(fail);
}

// Word files: change the words of each paragraph; the server keeps the rest of the .docx exactly as it was.
function wordFile(tab, body, fail) {
  tab.docx = true;
  tab.show = (j) => {
    tab.base = j.base; tab.changes = {};
    tab.editable = true;
    body.replaceChildren(docxEditor(j.paragraphs || [], (i, text) => { tab.changes[i] = text; fileTouch(tab); },
                                    () => openInApp(tab.path)));
  };
  api("docxread", { path: tab.path }).then(tab.show).catch(fail);
}

// Open a file in its own Mac app (Word, Pages, Numbers…). Needs the Finder view, which asks first.
async function openInApp(path) {
  const tab = state.tabs.find((t) => t.path === path);
  if (tab && tab.dirty) await saveNow(tab);
  if (!finder.shown) {
    await toggleFinder();
    if (!finder.shown) return;
  }
  try { await api("finder", { do: "openfile", path }); toastOk("Opened. Changes you save there go back into the locked folder."); }
  catch (e) { toastErr(e.message); }
}

function fileTouch(tab) {
  tab.ver = (tab.ver || 0) + 1;
  tab.dirty = true;
  clearTimeout(tab.timer);
  tab.timer = setTimeout(() => saveNow(tab), 800);
  renderStatus(); renderTabs();
}

function saveFileNow(tab) {
  clearTimeout(tab.timer);
  tab.chain = (tab.chain || Promise.resolve()).then(async () => {
    if (!tab.dirty) return;
    const v = tab.ver, text = tab.text;
    tab.saving = true; renderStatus();
    if (tab.docx) {
      const changes = tab.changes; tab.changes = {};
      try {
        const j = await api("docxsave", { path: tab.path, changes, base: tab.base, folder: tab.folder });
        if ("conflict" in j) {
          if (j.conflict) tellConflict(tab.path, j.conflict);
          tab.dirty = false;
          tab.show(await api("docxread", { path: tab.path, folder: tab.folder }));
          loadFiles();
        } else {
          tab.base = j.base;
          if (tab.ver === v) tab.dirty = false;
        }
        tab.err = null;
      } catch (e) { tab.err = e.message; Object.assign(tab.changes, { ...changes, ...tab.changes }); }
      tab.saving = false;
      if (!tab.err && !tab.dirty) tab.savedAt = Date.now();
      renderStatus(); renderTabs();
      return;
    }
    try {
      const j = await writeFileText(tab.path, text, tab.base, tab.folder);
      if (j.conflict) {   // changed somewhere else meanwhile: ours went to a conflict copy, show theirs
        tellConflict(tab.path, j.conflict);
        tab.dirty = false;
        tab.show(decodeStrict(j.base64) ?? "");
        loadFiles();
      } else {
        tab.base = text;
        if (tab.ver === v) tab.dirty = false;
      }
      tab.err = null;
    } catch (e) { tab.err = e.message; }
    tab.saving = false;
    if (!tab.err && !tab.dirty) tab.savedAt = Date.now();
    renderStatus(); renderTabs();
  });
  return tab.chain;
}

function parseFM(text) {
  const sp = splitFM(text);
  let fm = { mode: "none", head: "", props: [], raw: "", changed: false };
  if (sp.yaml !== null) {
    const props = parseYaml(sp.yaml);
    fm = props ? { mode: "props", head: sp.head, props, raw: sp.yaml, changed: false } : { mode: "raw", head: sp.head, props: [], raw: sp.yaml, changed: false };
  }
  return { fm, body: sp.body };
}

// Put new text into an open note (restore a version, or the file changed on disk). Saves only if asked.
function applyText(tab, text) {
  const { fm, body } = parseFM(text);
  tab.fm = fm; tab.body = body; tab.base = text;
  renderProps(tab);
  tab.editor && tab.editor.setText(body);
}

async function makeNoteTab(path) {
  const j = await api("read", { path });
  const { fm, body } = parseFM(j.text || "");
  const tab = { path, kind: "note", folder: currentFolder(), base: j.text || "", fm, body, dirty: false, saving: false, ver: 0, timer: null, chain: Promise.resolve(), err: null, editor: null };
  tab.titleEl = el("input", { class: "title", spellcheck: "false", "aria-label": "Note title", value: label(path) });
  tab.titleErr = el("div", { class: "title-err" });
  tab.crumbText = el("button", { class: "crumb-path", type: "button", title: "Copy path",
                                 onclick: (e) => copyPathMenu(tab.path, e.currentTarget) });
  tab.crumbEl = el("div", { class: "crumb" }, tab.crumbText,
    el("button", { class: "crumb-btn", type: "button", title: "Show this note in Finder",
                   onclick: () => revealInFinder(tab.path) }, icon("folder", 13), "Show in Finder"));
  tab.propsEl = el("div", { class: "props" });
  tab.host = el("div", { class: "editor-host" });
  tab.pane = el("div", { class: "pane hidden" }, el("div", { class: "note-col" }, tab.crumbEl, tab.titleEl, tab.titleErr, tab.propsEl, tab.host));
  // Clicking the empty space under a note puts the cursor at the end, like Obsidian. If the note ends with a
  // table or a code block, a new line is added first so there is somewhere to type.
  tab.pane.addEventListener("mousedown", (e) => {
    const v = tab.editor && tab.editor.view;
    if (!v || e.button !== 0 || e.target.closest("input, textarea, button, select, a, .props, .crumb, .md-table-wrap, .cm-line, .cm-widgetBuffer")) return;
    const doc = v.state.doc;
    const bottom = v.documentTop + v.lineBlockAt(doc.length).bottom;
    if (e.clientY <= bottom) return;
    e.preventDefault();
    const last = doc.line(doc.lines).text;
    const changes = /^\s*\|/.test(last) || /^\s*(```|~~~)/.test(last) ? { from: doc.length, insert: "\n\n" } : undefined;
    v.focus();
    v.dispatch({ changes, selection: { anchor: doc.length + (changes ? 2 : 0) }, scrollIntoView: true });
  });
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
    readFileText: (path) => readFileText(path),
    tagNames: () => state.tags,
    notePath: () => tab.path,
    loadState: (key) => noteState(tab.path, key),
    saveState: (key, value) => setNoteState(tab.path, key, value),
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
  if (tab.editable) return saveFileNow(tab);
  if (tab.kind !== "note") return Promise.resolve();
  clearTimeout(tab.timer);
  tab.chain = tab.chain.then(async () => {
    if (!tab.dirty) return;
    const v = tab.ver;
    tab.saving = true; renderStatus();
    try {
      const text = compose(tab);
      const j = await api("save", { path: tab.path, text, base: tab.base, folder: tab.folder });
      if (j.conflict) {
        // Someone else changed this note since we loaded it: our text went to a conflict copy, theirs stays here.
        if (tab.ver !== v) await api("save", { path: j.conflict, text: compose(tab), folder: tab.folder });
        tellConflict(tab.path, j.conflict);
        applyText(tab, j.text || "");
        tab.dirty = false;
        loadFiles();
      } else if (j.merged != null) {
        // Changed somewhere else meanwhile, in other lines: both edits are in the note now. Show it, unless
        // the person typed on during the save (the next save puts that together the same way).
        if (tab.ver === v) { applyText(tab, j.merged); tab.dirty = false; flashStatus("Merged"); }
        else tab.base = text;
      } else {
        tab.base = text;
        if (tab.ver === v) tab.dirty = false;
      }
      tab.err = null;
      const f = state.files.find((x) => x.path === tab.path);
      if (f) f.mtime = Date.now() / 1000;
      scheduleLinksRefresh();
    } catch (e) { tab.err = e.message; }
    tab.saving = false;
    if (!tab.err && !tab.dirty) tab.savedAt = Date.now();
    renderStatus(); renderTabs();
  });
  return tab.chain;
}

// Short-lived words after an action (Undone, Restored…), then back to the save state.
let statusFlash = null;
function flashStatus(text, tone = "") {
  statusFlash = { text, tone, tab: state.active, until: Date.now() + 2200 };
  renderStatus();
  setTimeout(renderStatus, 2300);
}

const SAVED_SHOWS = 1500;
let savedTimer = null;
function renderStatus() {
  if (!statusEl) return;
  const t = state.active;
  let s = "", cls = "";
  if (t && (t.kind === "note" || t.editable)) {
    if (t.err) { s = "Save failed"; cls = "bad"; }
    else if (statusFlash && statusFlash.tab === t && Date.now() < statusFlash.until) { s = statusFlash.text; cls = statusFlash.tone; }
    else if (t.saving) s = "Saving…";
    else if (t.dirty) s = "Unsaved";
    else {   // "Saved" shows for a moment in green after a save, then fades away
      s = "Saved";
      const left = (t.savedAt || 0) + SAVED_SHOWS - Date.now();
      cls = left > 0 ? "ok" : "gone";
      if (left > 0) { clearTimeout(savedTimer); savedTimer = setTimeout(renderStatus, left + 20); }
    }
  }
  statusEl.textContent = s;
  statusEl.className = "status " + cls;
  if (t && t.err) statusEl.title = t.err; else statusEl.removeAttribute("title");
}

// At most MAX_TABS tabs: opening one more closes the oldest (leftmost) other tab, saving it first.
const MAX_TABS = 6;
function trimTabs(keep) {
  const extra = state.tabs.length - MAX_TABS;
  if (extra <= 0) return;
  for (const t of state.tabs.filter((t) => t !== keep).slice(0, extra)) closeTab(t);
}

function activate(tab, opts = {}) {
  trimTabs(tab);
  state.active = tab;
  for (const t of state.tabs) t.pane.classList.toggle("hidden", t !== tab);
  paneHost._empty.classList.add("hidden");
  if (!isSpecial(tab)) { let p = dirOf(tab.path); while (p) { state.open.add(p); p = dirOf(p); } }
  if (tab.kind === "note") state.lastNote = tab.path;
  if (versionsOpenFor() && versionsOpenFor() !== tab.path) closeVersions();
  closeBacklinks();
  ensureEditor(tab);
  noteTools.classList.toggle("hidden", tab.kind !== "note");
  renderTabs(); renderTree(); renderStatus();
  refreshBacklinks();
  if (tab.kind === "home") renderHome(tab);
  if (tab.kind === "graph") loadGraph(tab);
  if (tab.kind === "search") requestAnimationFrame(() => tab.sv.focus());
  if (tab.kind === "note") {
    requestAnimationFrame(() => {
      tab.editor.refresh();
      // A note opens in view mode (fully formatted, no cursor). Editing starts when you click or type in it.
      if (opts.focusTitle) { tab.titleEl.focus(); tab.titleEl.select(); }
      else if (document.activeElement && document.activeElement.closest(".cm-editor")) document.activeElement.blur();
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
  tab.onClose && tab.onClose();
  tab.pane.remove();
  if (state.active === tab) {
    const next = state.tabs[Math.min(i, state.tabs.length - 1)];
    if (next) activate(next);
    else {
      state.active = null; paneHost._empty.classList.remove("hidden");
      noteTools.classList.add("hidden"); closeVersions(); closeBacklinks(); refreshBacklinks();
      renderTabs(); renderTree(); renderStatus();
    }
  } else renderTabs();
}

async function closeMany(list) { for (const t of list) await closeTab(t); }

function tabMenu(tab, x, y) {
  const i = state.tabs.indexOf(tab);
  showMenu([
    { label: "Close", fn: () => closeTab(tab) },
    { label: "Close others", fn: () => closeMany(state.tabs.filter((t) => t !== tab)) },
    { label: "Close tabs to the right", fn: () => closeMany(state.tabs.slice(i + 1)) },
    ...(isSpecial(tab) ? [] : [{ sep: true }, { label: "Show in Finder", fn: () => revealInFinder(tab.path) }]),
    { sep: true },
    { label: "Close all", fn: () => closeMany([...state.tabs]) },
  ], x, y);
}

function cycleTab(dir) {
  if (state.tabs.length < 2) return;
  const i = state.tabs.indexOf(state.active);
  activate(state.tabs[(i + dir + state.tabs.length) % state.tabs.length]);
}

function renderTabs() {
  if (!tabsEl) return;
  if (graphRowEl) {
    const on = !!(state.active && state.active.kind === "graph" && state.tabs.includes(state.active));
    graphRowEl.classList.toggle("active", on);
    graphRowEl.title = on ? "Close the graph (⌘G)" : "Graph view (⌘G)";
  }
  const fname = (curInfo() || {}).name || "";
  for (const t of state.tabs) if (t.crumbText) t.crumbText.textContent = [fname, ...t.path.split("/")].filter(Boolean).join("  /  ");
  const nodes = state.tabs.map((t) => {
    const on = t === state.active;
    const el1 = el("div", {
      class: "tab" + (on ? " active" : ""), role: "tab", title: isSpecial(t) ? t.title : t.path,
      onclick: () => activate(t),
      oncontextmenu: (e) => { e.preventDefault(); tabMenu(t, e.clientX, e.clientY); },
      onauxclick: (e) => { if (e.button === 1) { e.preventDefault(); closeTab(t); } },
      onmousedown: (e) => { if (e.button === 1) e.preventDefault(); },
    }, isSpecial(t) ? icon(t.kind === "graph" ? "graph" : t.kind === "search" ? "search" : "home", 13) : null,
    el("span", { class: "tab-label" }, tabLabel(t)),
    t.dirty ? el("span", { class: "dot", title: "Unsaved" }) : null,
    el("button", { class: "tab-x", title: "Close", "aria-label": "Close tab", onclick: (e) => { e.stopPropagation(); closeTab(t); } }, icon("x", 12, 2)));
    return el1;
  });
  tabsEl.replaceChildren(...nodes);   // the + button sits outside the strip, so it never scrolls away
  // The Mac's web view sizes a scrolling flex strip too small, so say how wide the tabs want to be; it still
  // shrinks (and scrolls) when the window is narrow.
  tabsEl.style.flexBasis = `${state.tabs.length * 182 + 6}px`;
  fitTabs();
}

// Bring the active tab into view by scrolling the strip only (scrollIntoView also scrolled the window's own layout).
// Runs again whenever the strip changes size: at start the window is still tiny, and a scroll made then used to
// stay, leaving the first tab cut off.
function fitTabs() {
  if (!tabsEl) return;
  if (tabsEl.scrollWidth <= tabsEl.clientWidth + 1) { tabsEl.scrollLeft = 0; return; }
  const a = tabsEl.querySelector(".tab.active");
  if (!a) return;
  const r = a.getBoundingClientRect(), b = tabsEl.getBoundingClientRect();
  if (r.left < b.left) tabsEl.scrollLeft -= b.left - r.left;
  else if (r.right > b.right && b.width >= r.width) tabsEl.scrollLeft += r.right - b.right;
}

// ---------- Home ----------
function goHome() {
  const h = getPref("home");
  if (h && state.files.some((f) => f.path === h)) return openPath(h);
  return openHomeTab();
}

function openHomeTab() {
  let tab = state.tabs.find((t) => t.kind === "home");
  if (!tab) {
    const body = el("div", { class: "note-col home" });
    const pane = el("div", { class: "pane hidden" }, body);
    paneHost.append(pane);
    tab = { path: HOME_ID, title: "Home", kind: "home", pane, body, dirty: false };
    state.tabs.push(tab);
  }
  activate(tab);
}

// A pinned folder on Home: open it (and the folders around it) in the sidebar.
function showFolder(path) {
  const parts = path.split("/");
  parts.forEach((_, i) => state.open.add(parts.slice(0, i + 1).join("/")));
  renderTree();
}

function refreshHome() { const t = state.tabs.find((k) => k.kind === "home"); if (t) renderHome(t); }

function renderHome(tab) {
  const notes = state.files.filter((f) => f.kind === "file" && isMd(f.path));
  const item = (f) => el("button", { class: "home-item", onclick: () => f.kind === "folder" ? showFolder(f.path) : openPath(f.path) }, icon(f.kind === "folder" ? "folder" : "file", 15),
    el("span", { class: "hi-name" }, label(f.path)), dirOf(f.path) ? el("span", { class: "hi-dir" }, dirOf(f.path)) : null,
    f.mtime ? el("span", { class: "hi-time" }, whenDate(new Date(f.mtime * 1000))) : null);
  const recent = [...notes].sort((a, b) => (b.mtime || 0) - (a.mtime || 0)).slice(0, 8);
  const pinned = getPref("pins", []).map((p) => state.files.find((f) => f.path === p)).filter(Boolean);
  tab.body.replaceChildren(
    el("h1", { class: "home-title" }, "Home"),
    el("h2", { class: "home-h" }, "Recent notes"),
    recent.length ? el("div", { class: "home-list" }, ...recent.map(item)) : el("div", { class: "home-none" }, "No notes yet. Press ⌘N to write the first one."),
    el("h2", { class: "home-h" }, "Pinned"),
    pinned.length ? el("div", { class: "home-list" }, ...pinned.map(item)) : el("div", { class: "home-none" }, "Nothing pinned. Right-click a note or folder and choose Pin."),
    el("div", { class: "home-hint" }, icon("home", 14), "Want your own Home page? Open a note's menu and choose Set as Home."));
}

// ---------- Graph ----------
// ---------- search (Engram) ----------
function openSearchView(q) {
  let tab = state.tabs.find((t) => t.kind === "search");
  if (!tab) {
    tab = { path: SEARCH_ID, title: "Search", kind: "search", dirty: false };
    makeSearchPane(tab);
    state.tabs.push(tab);
  }
  activate(tab);
  if (q) tab.sv.setQuery(q);
}

function makeSearchPane(tab) {
  tab.sv = createSearchView({
    api,
    openAt: (path, heading) => openAt(path, heading),
    folders: () => state.files.filter((f) => f.kind === "folder" && !f.path.includes("/")).map((f) => f.path).sort(),
    recent: (n) => state.files.filter((f) => f.kind === "file" && isMd(f.path)).sort((a, b) => (b.mtime || 0) - (a.mtime || 0))
      .slice(0, n).map((f) => f.path),
  });
  tab.pane = el("div", { class: "pane search-pane hidden" }, tab.sv.root);
  paneHost.append(tab.pane);
}

// Open a note and bring one of its sections (by heading text) to the top of the view.
async function openAt(path, heading) {
  await openPath(path);
  const tab = state.tabs.find((t) => t.path === path);
  if (!heading || !tab || !tab.editor) return;
  const view = tab.editor.view, doc = view.state.doc, want = heading.trim().toLowerCase();
  for (let i = 1; i <= doc.lines; i++) {
    const line = doc.line(i);
    const h = /^#{1,6}\s+(.*)$/.exec(line.text);
    if (h && h[1].trim().toLowerCase() === want) {
      requestAnimationFrame(() => {
        view.dispatch({ effects: view.constructor.scrollIntoView(line.from, { y: "start", yMargin: 90 }) });
        const dom = view.domAtPos(line.from).node;
        const elx = dom.nodeType === 1 ? dom : dom.parentElement;
        const row = elx && elx.closest(".cm-line");
        if (row) { row.classList.add("flash-line"); setTimeout(() => row.classList.remove("flash-line"), 1400); }
      });
      return;
    }
  }
}

function editAct(what) {
  const t = state.active;
  if (t && t.editor && t.editor[what]) { t.editor[what](); t.editor.focus(); flashStatus(what === "undo" ? "Undone" : "Redone"); }
}

// ---------- give AI a task with a note (the AI tasks list) ----------
async function giveToAI() {
  const tab = state.active;
  if (!tab || tab.kind !== "note") return;
  await saveNow(tab);
  openTodoList(tab.path);
}

async function openTodoList(path) { return openAI("tasks", path); }

// The AI panel: Tasks and Activity tabs.
async function openAI(start, path) {
  let todo, rows;
  try { [todo, rows] = await Promise.all([api("aitodo").then((j) => j.todo || []), api("aiactivity").then((j) => j.activity || [])]); }
  catch (e) { toastErr(e.message); return; }
  await openAIPanel({
    tasks: {
      path, todo, label,
      give: async (ask) => {
        const j = await api("handtoai", { path, ask });
        navigator.clipboard.writeText("Do my Phygital Memory tasks.").catch(() => {});
        toastOk("Added to AI tasks. \u201cDo my Phygital Memory tasks.\u201d is copied, to paste in your AI chat.");
        return j.todo || [];
      },
      set: async (id, done) => (await api("aitodoset", { id, done })).todo || [],
      remove: async (id) => (await api("aitodoremove", { id })).todo || [],
      load: async () => (await api("aitodo")).todo || [],
      open: (p) => openPath(p),
    },
    activity: {
      rows, open: (p) => openPath(p),
      undo: async (r) => {
        const j = await api("undoai", { id: r.undo, folder: r.folder });
        await syncFromDisk();
        toastOk(j.trashed ? `Moved "${label(j.path)}" to the trash. Restore it from there if you change your mind.`
                          : `"${label(j.path)}" is back as it was. The AI's version is kept in version history.`);
      },
      fail: (m) => toastErr(m),
    },
  }, start);
  watchTodo();
}

// Tell the person when their AI ticks a note off (checked with the status icons).
let todoDone = null;
async function watchTodo() {
  let todo;
  try { todo = (await api("aitodo")).todo || []; } catch { return; }
  const now = new Set(todo.filter((i) => i.done).map((i) => i.id));
  now.folder = currentFolder();
  if (todoDone && todoDone.folder === now.folder) {
    for (const i of todo) if (i.done && !todoDone.has(i.id) && i.by !== "you") toastOk(`${i.by || "Your AI"} finished “${label(i.path)}”.`);
  }
  todoDone = now;
  openTasks = todo.filter((i) => !i.done).length;
  drawAI();
}

function openGraph() {
  if (state.active && state.active.kind === "graph") { closeTab(state.active); return; }   // pressed again: close it
  let tab = state.tabs.find((t) => t.kind === "graph");
  if (!tab && pregraph && pregraph.folder === loadedFolder && pregraph.pane && pregraph.pane.isConnected) {
    tab = pregraph;   // already built in the background
    pregraph = null;
    state.tabs.push(tab);
  }
  if (!tab) {
    tab = { path: GRAPH_ID, title: "Graph", kind: "graph", dirty: false, sig: "" };
    makeGraphPane(tab);
    state.tabs.push(tab);
  }
  activate(tab);
}

function makeGraphPane(tab) {
  const g = createGraph({ onOpen: (p) => state.files.some((f) => f.path === p && f.kind === "folder") ? showFolder(p) : openPath(p),
                          colorFor: nodeColor, labelFor: label });
  tab.pane = el("div", { class: "pane graph-pane hidden" }, g.root);
  paneHost.append(tab.pane);
  tab.graph = g; tab.sig = ""; tab.onClose = () => g.destroy();
}

async function loadGraph(tab) {
  const fid = loadedFolder;
  try {
    const j = await api("links");
    if (fid !== loadedFolder || !tab.graph) return;
    state.tags = j.tags || state.tags;
    const sig = JSON.stringify([j.nodes, j.files, j.folders, j.edges, colorsPref()]);
    if (sig !== tab.sig) { tab.sig = sig; tab.graph.load({ nodes: j.nodes || [], files: j.files || [], folders: j.folders || [], edges: j.edges || [] }, state.lastNote); }
    else tab.graph.setCurrent(state.lastNote);
  } catch (e) { toastErr(e.message); }
}
onSettings(() => { for (const t of state.tabs) if (t.kind === "graph") t.graph.restyle(); });

// ---------- version history ----------
function toggleVersions() {
  const t = state.active;
  if (!t || t.kind !== "note") return;
  openVersions({
    host: paneHost, path: t.path,
    currentText: () => compose(t),
    restore: async (text) => { applyText(t, text); touch(t); await saveNow(t); flashStatus("Restored"); },
  });
}

// ---------- backlinks ----------
let blData = [], blToken = 0, blCard = null;
function closeBacklinks() { if (blCard) { blCard.remove(); blCard = null; } }
document.addEventListener("mousedown", (e) => { if (blCard && !blCard.contains(e.target) && !(blPill && blPill.contains(e.target))) closeBacklinks(); }, true);

async function refreshBacklinks() {
  const t = state.active;
  const my = ++blToken;
  if (!t || t.kind !== "note") { blData = []; drawPill(); return; }
  try {
    const j = await api("backlinks", { path: t.path });
    if (my !== blToken) return;
    blData = j.backlinks || [];
  } catch { if (my !== blToken) return; blData = []; }
  drawPill();
}
function drawPill() {
  if (!blPill) return;
  const t = state.active;
  const show = t && t.kind === "note" && blData.length > 0;
  blPill.classList.toggle("hidden", !show);
  blPill.textContent = blData.length === 1 ? "1 backlink" : `${blData.length} backlinks`;
  if (!show) closeBacklinks();
}
function toggleBacklinks() {
  if (blCard) { closeBacklinks(); return; }
  blCard = el("div", { class: "bl-card", role: "dialog", "aria-label": "Backlinks" },
    el("div", { class: "bl-head" }, "Linked from"),
    ...blData.map((b) => el("button", { class: "bl-item", onclick: () => { closeBacklinks(); openPath(b.path); } },
      el("div", { class: "bl-name" }, label(b.path)), b.line ? el("div", { class: "bl-line" }, b.line) : null)));
  paneHost.append(blCard);
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
  if (e.key === "Escape" && state.sel.size && !document.querySelector(".overlay,.menu")) { state.sel.clear(); renderTree(); return; }
  if (!mod || e.altKey) return;
  if (e.key === ",") { e.preventDefault(); openSettingsHere(); }
  else if (k === "h" && e.shiftKey) { e.preventDefault(); goHome(); }
  else if (k === "o" && e.shiftKey) { e.preventDefault(); openSwitcher(); }
  else if (/^[1-9]$/.test(k) && !e.shiftKey && !e.altKey && folderList[Number(k) - 1]) { e.preventDefault(); switchTo(folderList[Number(k) - 1].id); }
  else if (k === "g" && !e.shiftKey) { e.preventDefault(); openGraph(); }
  else if (k === "k" || k === "p") { e.preventDefault(); openSearch(); }
  else if (k === "f" && e.shiftKey) { e.preventDefault(); openSearchView(); }
  else if (k === "f" && !e.shiftKey) {
    if (e.target.closest && e.target.closest(".cm-editor")) return;   // the editor has its own find
    e.preventDefault(); openSearch();
  }
  else if (k === "n") { e.preventDefault(); if (!e.repeat) newNote(); }   // holding ⌘N must not make a pile of notes
  else if (k === "w") { e.preventDefault(); if (!e.repeat && state.active) closeTab(state.active); }
  else if (k === "s") { e.preventDefault(); if (state.active) saveNow(state.active); }
}, true);
window.addEventListener("beforeunload", (e) => { if (state.tabs.some((t) => t.dirty)) { e.preventDefault(); e.returnValue = ""; } });

// ---------- closing the app ----------
// The Mac app hides the window and asks its own small question (lock all, or keep open). First it calls this, so
// nothing just typed is lost if everything locks.
window.phygitalSaveAll = async () => {
  if (loadedFolder) { await Promise.all(state.tabs.map((t) => saveNow(t))); await flushPrefs(); }
};

// Notice a Finder view that ended by itself.
let foldersTimer = null;
function watchFolders() {
  if (!foldersTimer) foldersTimer = setInterval(refreshFolders, 15000);
}

// ---------- start ----------
// Double-clicking the opener file inside a locked folder: the Mac app asks the server to add that folder, then
// calls this (or, on a cold start, the page finds it through "wanted").
window.phygitalOpenFolder = async (id) => {
  if (!/^[0-9a-f]{1,32}$/.test(String(id))) return;
  await refreshFolders();
  await switchTo(id);
};

(async function start() {
  await refreshFolders();
  if (folderList.length) {
    let first = folderList[0].id;
    try { const w = await api("wanted"); if (w.id && folderList.some((f) => f.id === w.id)) first = w.id; } catch {}
    setFolder(first);
    try {
      const j = await api("devunlock");
      if (j && j.pass) { setPass(j.pass); await enterApp(); return; }
    } catch {}
  }
  showUnlock();
})();
