// The app's words in the person's language. The English text is the key: t("Move to trash"). A text with parts in it
// uses {0}, {1}: t("Moved {0} items", n). A language without a text yet shows the English, so nothing is ever blank.
// Only text the app writes goes through here; note, folder and file names never do (they stay as the person wrote them).
// Languages live in core/languages/{code}.json (scripts/i18n.py extracts, checks and translates them).
import { PC } from "./pc-words.js";

let words = {};
let lang = "en";
const MAC = /Mac/.test(navigator.platform || navigator.userAgent);
// Texts that name the Mac use PC's wording on every system ("This computer"), except those about the Mac's own parts,
// which keep their real names on a Mac.
const MAC_ONLY = /Finder|Keychain|Touch ID|security chip/;

// The same English word can mean two things ("Open" the button, "Open" the kind of memory): t("Open@@kind") tells
// them apart for translators, and English shows the word before "@@".
export const t = (text, ...parts) => {
  if (PC[text] && (!MAC || !MAC_ONLY.test(text))) text = PC[text];   // "This computer" everywhere; Finder and the like stay on a Mac
  const s = keys((lang !== "en" && words[text]) || text.split("@@")[0]);
  return parts.length ? s.replace(/\{(\d+)\}/g, (m, i) => (parts[i] !== undefined ? String(parts[i]) : m)) : s;
};

// Shortcuts are written the Mac's way (⇧⌘F); Windows and Linux show Ctrl+Shift+F.
export const keys = (s) => MAC ? s : s.replace(/(⇧?)(⌥?)⌘(\S)/g, (_, sh, alt, k) => `Ctrl+${sh ? "Shift+" : ""}${alt ? "Alt+" : ""}${k}`);

// "5 min ago" and the like, in the person's language. sec: how long ago; null: never.
export const agoText = (sec) => sec == null ? t("not yet") : sec < 60 ? t("just now")
  : sec < 3600 ? t("{0} min ago", Math.round(sec / 60)) : sec < 86400 ? t("{0} h ago", Math.round(sec / 3600))
  : t("{0} days ago", Math.round(sec / 86400));

// The languages the app can show, as [code, its own name]. The build fills this from core/languages/.
export const LANGUAGES = (globalThis.PM_LANGUAGES || [["en", "English"]]);

// "system" follows the Mac's language when the app has it; otherwise English.
export function pickLanguage(choice) {
  if (choice && choice !== "system") return choice;
  const have = LANGUAGES.map(([c]) => c);
  for (const want of navigator.languages || [navigator.language || "en"]) {
    const exact = have.find((c) => c.toLowerCase() === want.toLowerCase());
    const base = have.find((c) => c.split("-")[0] === want.split("-")[0].toLowerCase());
    if (exact || base) return exact || base;
  }
  return "en";
}

// Load a language before the screens draw. English needs nothing.
export async function useLanguage(choice) {
  const code = pickLanguage(choice);
  if (code === "en") { lang = "en"; words = {}; document.documentElement.lang = "en"; return "en"; }
  try {
    const r = await fetch(`/assets/lang-${code}.json`);
    words = r.ok ? await r.json() : {};
    lang = r.ok ? code : "en";
  } catch { words = {}; lang = "en"; }
  document.documentElement.lang = lang;
  document.documentElement.dir = ["ar", "fa", "he", "ur"].includes(lang.split("-")[0]) ? "rtl" : "ltr";
  return lang;
}

export const currentLanguage = () => lang;
