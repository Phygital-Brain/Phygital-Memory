// Per-device settings (theme, editor font size, properties on/off, Desktop icon when unlocked). The editor always uses the full width. They live in localStorage, because they
// belong to this computer, not to the notes.
import { t, LANGUAGES, useLanguage } from "./i18n.js";
import { el, icon, tabbed } from "./dom.js";
import { info } from "./panels.js";
import { toast } from "./toast.js";

const KEY = "phygital-memory-settings";
const DEFAULTS = { theme: "system", size: 16, props: true, desktopIcon: true, lang: "system" };
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

// The app's language: on the lock screen and in Settings › General. Only the app's own words change, never note,
// folder or file names. onPick runs after the language is loaded.
export function languagePicker(onPick) {
  const sel = el("select", { class: "set-select", "aria-label": t("Language") },
    el("option", { value: "system" }, t("System")), ...LANGUAGES.map(([code, name]) => el("option", { value: code }, name)));
  sel.value = cur.lang || "system";
  sel.addEventListener("change", async () => { update({ lang: sel.value }); await useLanguage(sel.value); onPick && onPick(sel.value); });
  return sel;
}

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
  const size = el("input", { type: "range", min: 13, max: 22, step: 1, value: cur.size, "aria-label": t("Editor font size") });
  size.addEventListener("input", () => { update({ size: +size.value }); sizeVal.textContent = cur.size + " px"; });

  const props = el("input", { type: "checkbox", checked: cur.props, "aria-label": t("Show properties") });
  props.addEventListener("change", () => update({ props: props.checked }));
  const onUnlock = el("input", { type: "checkbox", checked: cur.desktopIcon, "aria-label": t("Desktop icon") });
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

  const general = [section(t("Look")),
    row(t("Theme"), null, seg([["system", "System"], ["light", "Light"], ["dark", "Dark"]], () => cur.theme, (v) => update({ theme: v })),
      t("System follows your Mac's light or dark mode.")),
    row(t("Font size"), null, el("div", { class: "set-range" }, size, sizeVal), t("Text size in the editor.")),
    row(t("Show properties"), t("Fields under a note's title."), sw(props), t("The info block at the top of a note, like tags and dates.")),
    row(t("Language"), t("The app's words. Note and folder names stay as you wrote them."),
      languagePicker(() => (me && me.restart ? me.restart() : toast(t("Language changed. Reopen the app to see it everywhere."))))),
    section(t("Finder"))];
  if (f && f.plain) general.push(row(t("Show in Finder"), t("This memory is a normal folder."), btn(t("Show"), f.toggleFinder)));
  else if (f && f.finderAvailable) general.push(row(t("Show in Finder"), t("Your notes as a normal folder."), toggle(t("Show in Finder"), f.finderShown, f.toggleFinder),
    t("While it's open, any app on this Mac can read your notes. It closes when you lock.")));
  if (!f || !f.plain) general.push(row(t("Desktop icon"), t("A shortcut on the Desktop while unlocked."), sw(onUnlock), t("It opens your notes in Finder and goes away when you lock.")));
  if (me && me.licenses) general.push(el("button", { class: "set-lic", type: "button", onclick: () => { close(); me.licenses(); } }, t("Licences")));

  const memory = [];
  if (f) {
    memory.push(el("div", { class: "set-mem" }, f.name),
      row(t("Name"), null, btn(t("Rename"), f.rename)),
      row(t("Stored in"), f.where, btn(t("Change"), f.storage), f.plain ? t("Where the folder lives, and the GitHub backup.") : t("Where the encrypted files live, and the GitHub backup.")));
    if (f.revealVault) memory.push(row(t("Encrypted files"), t("What's stored on disk."), btn(t("Show"), f.revealVault),
      t("These are the real files. Only you can read them, with your password.")));
    if (f.showHidden) memory.push(row(t("Show hidden files"), "⇧⌘.", toggle(t("Show hidden files"), f.showHidden.on, f.showHidden.set),
      t("Files and folders whose names start with a dot, like .env. They show in Hidden Notes at the bottom of the list.")));
    if (f.touchId) memory.push(row(t("Unlock with Touch ID"), t("Your finger instead of your password."), toggle(t("Unlock with Touch ID"), f.touchId.on, f.touchId.set),
      t("Your password is kept in the Mac's Keychain. Only this app can read it, after your fingerprint.")));
    if (f.recoveryKey) memory.push(row(t("Recovery key"), t("44 words that open the memory if you forget the password."), btn(t("Show"), f.recoveryKey),
      t("Write them down or keep them in a password manager. Anyone with these words can open the memory.")));
  }

  const sharing = [];
  if (me) {
    const name = el("input", { class: "dlg-input set-name", value: me.name || "", maxlength: "60", spellcheck: "false", "aria-label": t("Your name") });
    name.addEventListener("change", async () => { name.value = await me.set(name.value.trim()); });
    sharing.push(section(t("Sharing")), row(t("Your name"), null, name, t("What others see when you share a memory with them or join one.")));
    if (me.macs) sharing.push(row(t("Your Macs"), me.macs.list.length ? t("Linked: ") + me.macs.list.map((m) => m.name).join(", ") : t("Only this Mac."),
      btn(t("Link a Mac"), me.macs.link), t("Your other Mac becomes you too: the memories you pick sync between your Macs, still locked with the same password.")));
    if (me.approver) {
      const a = me.approver;
      sharing.push(row(t("Approve sharing with"), a.label, a.setUp ? btn(t("Set up"), a.setUp) : null,
        t("Letting someone in, adding, removing or forgetting a person is signed with your own key (Phygital Key format), so there's a record nobody can change.")));
      if (a.signed.length) sharing.push(el("div", { class: "act-list share-hist" }, ...a.signed.map((x) => el("div", { class: "todo-row share-row" },
        el("div", { class: "act-main" }, el("div", { class: "act-line" }, x.what[0].toUpperCase() + x.what.slice(1)),
          el("div", { class: "act-folder" }, t("Signed · ") + new Date(x.t * 1000).toLocaleString([], { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })))))));
    }
  }
  if (f) {
    sharing.push(section(t("AI")));
    if (f.aiApps) sharing.push(row(t("AI apps"), t("Which AI apps can use your notes."), btn(t("Manage"), f.aiApps),
      t("Each app gets its own key and only reaches memories that are open in the app.")));
    if (!f.plain) sharing.push(row(t("Hide from AI"), t("No AI app can reach this memory."), toggle(t("Hide from AI"), f.aiHidden, f.setAiHidden),   // an Open
      t("Turns off AI access to this memory, whatever each app is allowed.")));   // memory is a normal folder: any AI can read it
  }
  const pages = [{ title: t("General"), rows: general }];
  if (memory.length) pages.push({ title: t("This memory"), rows: memory });
  if (sharing.length) pages.push({ title: me ? "Sharing and AI" : "AI", rows: sharing });
  const card = el("div", { class: "dlg settings", role: "dialog", "aria-label": t("Settings") },
    el("div", { class: "set-head" }, el("div", { class: "dlg-title" }, t("Settings")),
      el("button", { class: "icon-btn", title: t("Close"), "aria-label": t("Close"), onclick: close }, icon("x", 14, 2))),
    tabbed(pages));
  const back = el("div", { class: "overlay modal", onmousedown: (e) => { if (e.target === back) close(); } }, card);
  document.addEventListener("keydown", onKey, true);
  document.body.append(back);
  open = { close };
  card.querySelector(".seg-b.on").focus();
}
