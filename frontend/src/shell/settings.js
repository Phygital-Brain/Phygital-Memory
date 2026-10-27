// Per-device settings (theme, editor font size, properties on/off, Desktop icon when unlocked). The editor always uses the full width. They live in localStorage, because they
// belong to this computer, not to the notes.
import { el, icon } from "./dom.js";
import { info } from "./panels.js";

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
export function openSettings(folderOpts, me) {
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
  const row = (title, hint, ctrl, tip) => el("div", { class: "set-row" },
    el("div", { class: "set-text" }, el("div", { class: "set-title" }, title, tip ? info(tip) : null), hint ? el("div", { class: "set-hint" }, hint) : null), ctrl);

  const sizeVal = el("span", { class: "set-val" }, cur.size + " px");
  const size = el("input", { type: "range", min: 13, max: 22, step: 1, value: cur.size, "aria-label": "Editor font size" });
  size.addEventListener("input", () => { update({ size: +size.value }); sizeVal.textContent = cur.size + " px"; });

  const props = el("input", { type: "checkbox", checked: cur.props, "aria-label": "Show properties" });
  props.addEventListener("change", () => update({ props: props.checked }));
  const onUnlock = el("input", { type: "checkbox", checked: cur.desktopIcon, "aria-label": "Desktop icon" });
  onUnlock.addEventListener("change", () => update({ desktopIcon: onUnlock.checked }));

  const close = () => { back.remove(); document.removeEventListener("keydown", onKey, true); open = null; prev && prev.focus && prev.focus(); };
  const onKey = (e) => { if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(); } };
  const sw = (input) => el("label", { class: "switch" }, input, el("span", { class: "switch-t" }));
  const toggle = (label, on, set) => {
    const box = el("input", { type: "checkbox", checked: !!on, "aria-label": label });
    box.addEventListener("change", async () => { box.checked = !!(await set(box.checked)); });
    return sw(box);
  };
  const btn = (label, fn) => el("button", { class: "btn small", type: "button", onclick: () => { close(); fn(); } }, label);
  const section = (title) => el("div", { class: "set-section" }, title);
  const f = folderOpts;

  const rows = [section("Look"),
    row("Theme", null, seg([["system", "System"], ["light", "Light"], ["dark", "Dark"]], () => cur.theme, (v) => update({ theme: v })),
      "System follows your Mac's light or dark mode."),
    row("Font size", null, el("div", { class: "set-range" }, size, sizeVal), "Text size in the editor."),
    row("Show properties", "Fields under a note's title.", sw(props), "The info block at the top of a note, like tags and dates.")];
  if (me) {
    const name = el("input", { class: "dlg-input set-name", value: me.name || "", maxlength: "60", spellcheck: "false", "aria-label": "Your name" });
    name.addEventListener("change", async () => { name.value = await me.set(name.value.trim()); });
    rows.push(section("Sharing"), row("Your name", null, name, "What others see when you share a memory with them or join one."));
    if (me.approver) {
      const a = me.approver;
      rows.push(row("Approve sharing with", a.label, a.setUp ? btn("Set up", a.setUp) : null,
        "Letting someone in, adding, removing or forgetting a person is signed with your own key (Phygital Key format), so there's a record nobody can change."));
      if (a.signed.length) rows.push(el("div", { class: "act-list share-hist" }, ...a.signed.map((x) => el("div", { class: "todo-row share-row" },
        el("div", { class: "act-main" }, el("div", { class: "act-line" }, x.what[0].toUpperCase() + x.what.slice(1)),
          el("div", { class: "act-folder" }, "Signed · " + new Date(x.t * 1000).toLocaleString([], { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })))))));
    }
  }
  if (f) {
    rows.push(section(`This memory: ${f.name}`),
      row("Name", null, btn("Rename", f.rename)),
      row("Stored in", f.where, btn("Change", f.storage), "Where the encrypted files live, and the GitHub backup."));
    if (f.revealVault) rows.push(row("Encrypted files", "What's stored on disk.", btn("Show", f.revealVault),
      "These are the real files. Only you can read them, with your password."));
    if (f.showHidden) rows.push(row("Show hidden files", "⇧⌘.", toggle("Show hidden files", f.showHidden.on, f.showHidden.set),
      "Files and folders whose names start with a dot, like .env. They show in Hidden Notes at the bottom of the list."));
  }
  rows.push(section("Finder"));
  if (f && f.finderAvailable) rows.push(row("Show in Finder", "Your notes as a normal folder.", toggle("Show in Finder", f.finderShown, f.toggleFinder),
    "While it's open, any app on this Mac can read your notes. It closes when you lock."));
  rows.push(row("Desktop icon", "A shortcut on the Desktop while unlocked.", sw(onUnlock), "It opens your notes in Finder and goes away when you lock."));
  if (f) {
    rows.push(section("Security and AI"));
    if (f.touchId) rows.push(row("Unlock with Touch ID", "Your finger instead of your password.", toggle("Unlock with Touch ID", f.touchId.on, f.touchId.set),
      "Your password is kept in the Mac's Keychain. Only this app can read it, after your fingerprint."));
    if (f.recoveryKey) rows.push(row("Recovery key", "44 words that open the memory if you forget the password.", btn("Show", f.recoveryKey),
      "Write them down or keep them in a password manager. Anyone with these words can open the memory."));
    if (f.aiApps) rows.push(row("AI apps", "Which AI apps can use your notes.", btn("Manage", f.aiApps),
      "Each app gets its own key and only reaches unlocked memories."));
    rows.push(row("Hide from AI", "No AI app can reach this memory.", toggle("Hide from AI", f.aiHidden, f.setAiHidden),
      "Turns off AI access to this memory, whatever each app is allowed."));
  }
  const card = el("div", { class: "dlg settings", role: "dialog", "aria-label": "Settings" },
    el("div", { class: "set-head" }, el("div", { class: "dlg-title" }, "Settings"),
      el("button", { class: "icon-btn", title: "Close", "aria-label": "Close", onclick: close }, icon("x", 14, 2))),
    ...rows);
  const back = el("div", { class: "overlay modal", onmousedown: (e) => { if (e.target === back) close(); } }, card);
  document.addEventListener("keydown", onKey, true);
  document.body.append(back);
  open = { close };
  card.querySelector(".seg-b.on").focus();
}
