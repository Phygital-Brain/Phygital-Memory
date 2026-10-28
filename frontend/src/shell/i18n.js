// The app's words in the person's language. The English text is the key: t("Move to trash"). A text with parts in it
// uses {0}, {1}: t("Moved {0} items", n). A language without a text yet shows the English, so nothing is ever blank.
// Only text the app writes goes through here; note, folder and file names never do (they stay as the person wrote them).
// Languages live in core/languages/{code}.json (scripts/i18n.py extracts, checks and translates them).
let words = {};
let lang = "en";

export const t = (text, ...parts) => {
  const s = (lang !== "en" && words[text]) || text;
  return parts.length ? s.replace(/\{(\d+)\}/g, (m, i) => (parts[i] !== undefined ? String(parts[i]) : m)) : s;
};

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
