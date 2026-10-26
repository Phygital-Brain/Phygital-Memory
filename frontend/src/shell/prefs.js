// The note-folder settings (home, pins, order, colours, per-note UI state). They live encrypted inside the notes
// folder, so they follow the notes. Kept in memory after unlock; writes are debounced.
import { api } from "../api.js";

let data = {};
let loaded = false;
let timer = null;

export async function loadPrefs() {
  try { data = (await api("prefs")).prefs || {}; loaded = true; }
  catch (e) { data = {}; loaded = false; if (e.message === "locked") throw e; }
}
export function clearPrefs() { clearTimeout(timer); timer = null; data = {}; loaded = false; }
export const getPref = (k, d) => (data[k] === undefined ? d : data[k]);

export function setPref(k, v) {
  if (v === undefined || v === null) delete data[k]; else data[k] = v;
  schedule();
}
export function setMapPref(k, key, v) {
  const m = data[k] && typeof data[k] === "object" ? data[k] : (data[k] = {});
  if (v === undefined || v === null) delete m[key]; else m[key] = v;
  schedule();
}
function schedule() {
  if (!loaded) return;
  clearTimeout(timer);
  timer = setTimeout(flushPrefs, 600);
}
export async function flushPrefs() {
  clearTimeout(timer); timer = null;
  if (!loaded) return;
  try { await api("saveprefs", { prefs: data }); } catch {}
}

export function noteState(path, key) {
  const s = data.noteState && data.noteState[path];
  return s ? s[key] : undefined;
}
export function setNoteState(path, key, value) {
  if (!data.noteState) data.noteState = {};
  const s = data.noteState[path] || (data.noteState[path] = {});
  if (value === undefined || value === null) delete s[key]; else s[key] = value;
  if (!Object.keys(s).length) delete data.noteState[path];
  schedule();
}

// A note or folder moved: carry its settings along.
export function movePrefs(from, to) {
  const re = (p) => (p === from ? to : p.startsWith(from + "/") ? to + p.slice(from.length) : p);
  for (const k of ["colors", "noteState", "folderSort"]) {
    if (!data[k]) continue;
    const next = {};
    for (const [p, v] of Object.entries(data[k])) next[re(p)] = v;
    data[k] = next;
  }
  if (data.order) {
    const next = {};
    for (const [p, names] of Object.entries(data.order)) next[re(p)] = names;
    // the item itself got a new name inside its own folder's order list
    const oldDir = from.includes("/") ? from.slice(0, from.lastIndexOf("/")) : "";
    const newDir = to.includes("/") ? to.slice(0, to.lastIndexOf("/")) : "";
    const oldName = from.split("/").pop(), newName = to.split("/").pop();
    if (next[oldDir]) {
      const i = next[oldDir].indexOf(oldName);
      if (i >= 0) {
        if (oldDir === newDir) next[oldDir] = next[oldDir].map((n) => (n === oldName ? newName : n));
        else next[oldDir] = next[oldDir].filter((n) => n !== oldName);
      }
    }
    data.order = next;
  }
  if (Array.isArray(data.pins)) data.pins = data.pins.map(re);
  if (data.home) data.home = re(data.home);
  schedule();
}
// A note or folder went to the trash: forget its settings.
export function dropPrefs(path) {
  const gone = (p) => p === path || p.startsWith(path + "/");
  for (const k of ["colors", "noteState", "folderSort", "order"]) if (data[k]) for (const p of Object.keys(data[k])) if (gone(p)) delete data[k][p];
  if (Array.isArray(data.pins)) data.pins = data.pins.filter((p) => !gone(p));
  if (data.home && gone(data.home)) delete data.home;
  schedule();
}
