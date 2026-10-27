// Per-device settings (theme, editor font size, properties on/off, Desktop icon when unlocked). The editor always uses the full width. They live in localStorage, because they
// belong to this computer, not to the notes.
import { el, icon } from "./dom.js";

const KEY = "phygital-memory-settings";
const DEFAULTS = { theme: "system", size: 16, props: true, desktopIcon: true };
let cur = { ...DEFAULTS };
const listeners = new Set();

try { Object.assign(cur, JSON.parse(localStorage.getItem(KEY) || "{}")); } catch {}
cur.size = Math.min(22, Math.max(13, +cur.size || 16));

export const settings = () => cur;
export const onSettings = (fn) => listeners.add(fn);

export function applySettings() {
  const r = document.documentElement;
  if (cur.theme === "light" || cur.theme === "dark") r.dataset.theme = cur.theme; else delete r.dataset.theme;
  r.style.setProperty("--editor-width", "100%");
  r.style.setProperty("--editor-size", cur.size + "px");
  r.classList.toggle("no-props", !cur.props);
}
function update(patch) {
  Object.assign(cur, patch);
  try { localStorage.setItem(KEY, JSON.stringify(cur)); } catch {}
  applySettings();
  listeners.forEach((fn) => fn(cur));
}
applySettings();

let open = null;
export function closeSettings() { if (open) { open.close(); } }

// folderOpts (optional): {name, finderShown, finderAvailable, toggleFinder()} for the "This folder" section.
export function openSettings(folderOpts) {
  if (open) return;
  const prev = document.activeElement;
  const seg = (options, get, set) => {
    const wrap = el("div", { class: "seg", role: "radiogroup" });
    const draw = () => wrap.replaceChildren(...options.map(([v, t]) => el("button", {
      class: "seg-b" + (get() === v ? " on" : ""), role: "radio", "aria-checked": get() === v ? "true" : "false",
      onclick: () => { set(v); draw(); } }, t)));
    draw();
    return wrap;
  };
  const row = (title, hint, ctrl) => el("div", { class: "set-row" }, el("div", { class: "set-text" }, el("div", { class: "set-title" }, title), hint ? el("div", { class: "set-hint" }, hint) : null), ctrl);

  const sizeVal = el("span", { class: "set-val" }, cur.size + " px");
  const size = el("input", { type: "range", min: 13, max: 22, step: 1, value: cur.size, "aria-label": "Editor font size" });
  size.addEventListener("input", () => { update({ size: +size.value }); sizeVal.textContent = cur.size + " px"; });

  const props = el("input", { type: "checkbox", checked: cur.props, "aria-label": "Show properties" });
  props.addEventListener("change", () => update({ props: props.checked }));
  const onUnlock = el("input", { type: "checkbox", checked: cur.desktopIcon, "aria-label": "Desktop icon when unlocked" });
  onUnlock.addEventListener("change", () => update({ desktopIcon: onUnlock.checked }));

  const close = () => { back.remove(); document.removeEventListener("keydown", onKey, true); open = null; prev && prev.focus && prev.focus(); };
  const onKey = (e) => { if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(); } };
  const card = el("div", { class: "dlg settings", role: "dialog", "aria-label": "Settings" },
    el("div", { class: "set-head" }, el("div", { class: "dlg-title" }, "Settings"),
      el("button", { class: "icon-btn", title: "Close", "aria-label": "Close", onclick: close }, icon("x", 14, 2))),
    el("div", { class: "set-note" }, "These stay on this computer."),
    row("Theme", "System follows your Mac.", seg([["system", "System"], ["light", "Light"], ["dark", "Dark"]], () => cur.theme, (v) => update({ theme: v }))),
    row("Font size", null, el("div", { class: "set-range" }, size, sizeVal)),
    row("Show properties", "The fields under a note's title.", el("label", { class: "switch" }, props, el("span", { class: "switch-t" }))),
    row("Desktop icon when unlocked", "A folder icon on the Desktop, with your memory's name, to open your notes in Finder. While it's there, any app on this Mac can read them. It goes away when you lock.",
      el("label", { class: "switch" }, onUnlock, el("span", { class: "switch-t" }))),
    ...(folderOpts && folderOpts.aiApps ? [row("AI apps", "Which AI apps can use your notes, and what each can reach.",
      el("button", { class: "btn small", type: "button", onclick: () => { close(); folderOpts.aiApps(); } }, "Manage…"))] : []),
    ...folderSection());
  // The selected memory: rename, where it's stored, its encrypted files, Finder, lock.
  function folderSection() {
    if (!folderOpts) return [];
    const btn = (label, fn) => el("button", { class: "btn small", type: "button", onclick: () => { close(); fn(); } }, label);
    const rows = [el("div", { class: "set-section" }, `This memory: ${folderOpts.name}`),
      row("Name", null, btn("Rename…", folderOpts.rename)),
      row("Where it's stored", folderOpts.where, el("div", { class: "set-btns" },
        folderOpts.revealVault ? btn("Encrypted files", folderOpts.revealVault) : null, btn("Change…", folderOpts.storage)))];
    if (folderOpts.finderAvailable) {
      const fin = el("input", { type: "checkbox", checked: !!folderOpts.finderShown, "aria-label": "Show in Finder" });
      fin.addEventListener("change", async () => {
        const ok = await folderOpts.toggleFinder();
        fin.checked = !!(ok ?? fin.checked);
      });
      rows.push(row("Show in Finder", "The unlocked notes as a normal folder. While it's open, any app on this Mac can read them. It closes when you lock.",
        el("label", { class: "switch" }, fin, el("span", { class: "switch-t" }))));
    }
    const hide = el("input", { type: "checkbox", checked: !!folderOpts.aiHidden, "aria-label": "AI can't see this" });
    hide.addEventListener("change", async () => { hide.checked = !!(await folderOpts.setAiHidden(hide.checked)); });
    rows.push(row("AI can't see this", "No AI app can reach this memory, whatever its access says.",
      el("label", { class: "switch" }, hide, el("span", { class: "switch-t" }))));
    if (folderOpts.showHidden) {
      const sh = el("input", { type: "checkbox", checked: !!folderOpts.showHidden.on, "aria-label": "Show hidden files" });
      sh.addEventListener("change", () => { sh.checked = !!folderOpts.showHidden.set(sh.checked); });
      rows.push(row("Show hidden files", "⇧⌘.", el("label", { class: "switch" }, sh, el("span", { class: "switch-t" }))));
    }
    if (folderOpts.touchId) {
      const tid = el("input", { type: "checkbox", checked: !!folderOpts.touchId.on, "aria-label": "Unlock with Touch ID" });
      tid.addEventListener("change", async () => { tid.checked = !!(await folderOpts.touchId.set(tid.checked)); });
      rows.push(row("Unlock with Touch ID", null, el("label", { class: "switch" }, tid, el("span", { class: "switch-t" }))));
    }
    rows.push(row("Lock", "Locks this memory now. AI apps can't reach it until you unlock it again.",
      el("div", { class: "set-btns" }, btn("Lock", folderOpts.lock), folderOpts.lockAll ? btn("Lock all", folderOpts.lockAll) : null)));
    return rows;
  }
  const back = el("div", { class: "overlay modal", onmousedown: (e) => { if (e.target === back) close(); } }, card);
  document.addEventListener("keydown", onKey, true);
  document.body.append(back);
  open = { close };
  card.querySelector(".seg-b.on").focus();
}
