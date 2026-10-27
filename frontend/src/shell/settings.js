// Per-device settings (theme, editor font size, properties on/off, open in Finder when unlocked). The editor always uses the full width. They live in localStorage, because they
// belong to this computer, not to the notes.
import { el, icon } from "./dom.js";

const KEY = "phygital-memory-settings";
const DEFAULTS = { theme: "system", size: 16, props: true, finderOnUnlock: true };
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
  const onUnlock = el("input", { type: "checkbox", checked: cur.finderOnUnlock, "aria-label": "Open in Finder when unlocked" });
  onUnlock.addEventListener("change", () => update({ finderOnUnlock: onUnlock.checked }));

  const close = () => { back.remove(); document.removeEventListener("keydown", onKey, true); open = null; prev && prev.focus && prev.focus(); };
  const onKey = (e) => { if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(); } };
  const card = el("div", { class: "dlg settings", role: "dialog", "aria-label": "Settings" },
    el("div", { class: "set-head" }, el("div", { class: "dlg-title" }, "Settings"),
      el("button", { class: "icon-btn", title: "Close", "aria-label": "Close", onclick: close }, icon("x", 14, 2))),
    el("div", { class: "set-note" }, "These stay on this computer."),
    row("Theme", "System follows your Mac.", seg([["system", "System"], ["light", "Light"], ["dark", "Dark"]], () => cur.theme, (v) => update({ theme: v }))),
    row("Font size", null, el("div", { class: "set-range" }, size, sizeVal)),
    row("Show properties", "The fields under a note's title.", el("label", { class: "switch" }, props, el("span", { class: "switch-t" }))),
    row("Open in Finder when unlocked", "While a folder is open in Finder, any app on this Mac can read its notes. It closes when you lock.",
      el("label", { class: "switch" }, onUnlock, el("span", { class: "switch-t" }))),
    ...folderSection());
  function folderSection() {
    if (!folderOpts || !folderOpts.finderAvailable) return [];
    const fin = el("input", { type: "checkbox", checked: !!folderOpts.finderShown, "aria-label": "Show in Finder" });
    fin.addEventListener("change", async () => {
      const ok = await folderOpts.toggleFinder();
      fin.checked = !!(ok ?? fin.checked);
    });
    return [el("div", { class: "set-section" }, `This folder: ${folderOpts.name}`),
      row("Show in Finder", "Opens the unlocked notes as a normal folder. While it's open, any app on this Mac can read them. It closes when you lock.",
          el("label", { class: "switch" }, fin, el("span", { class: "switch-t" })))];
  }
  const back = el("div", { class: "overlay modal", onmousedown: (e) => { if (e.target === back) close(); } }, card);
  document.addEventListener("keydown", onKey, true);
  document.body.append(back);
  open = { close };
  card.querySelector(".seg-b.on").focus();
}
