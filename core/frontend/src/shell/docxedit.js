// Word files: each paragraph is an editable line of text. The server changes only those words in the .docx, so
// fonts, styles, tables and pictures stay as they were. New paragraphs, tables and pictures: Open in Word.
import { t } from "./i18n.js";
import { el } from "./dom.js";

const HEADING = /^(Title|Subtitle|Heading\s?([1-6]))$/i;

// paras: [{i, text, style, table}]. onEdit(i, text) on every change. openApp() opens the file in its own app.
export function docxEditor(paras, onEdit, openApp) {
  const page = el("div", { class: "docx-page" });
  for (const p of paras) {
    const m = HEADING.exec(p.style || "");
    const level = m ? (/^title$/i.test(p.style) ? 0 : Number(m[2] || 3)) : null;
    const cls = ["docx-p"];
    if (level !== null) cls.push("docx-h", "docx-h" + level);
    if (p.list || /list/i.test(p.style || "")) cls.push("docx-li");
    if (p.table) cls.push("docx-cell");
    const line = el("div", { class: cls.join(" "), contenteditable: "plaintext-only", spellcheck: "true" });
    line.textContent = p.text;
    line.addEventListener("input", () => onEdit(p.i, line.innerText.replace(/\n/g, " ")));
    line.addEventListener("keydown", (e) => {   // one box per paragraph: Enter moves on instead of splitting it
      if (e.key === "Enter") { e.preventDefault(); const next = line.nextElementSibling; next && next.focus(); }
    });
    page.append(line);
  }
  const bar = el("div", { class: "docx-bar" },
    el("span", {}, t("Change the words here; the file keeps its look. For new paragraphs, tables or pictures:")),
    el("button", { class: "btn small", type: "button", onclick: openApp }, t("Open in Word")));
  return el("div", { class: "docx-editor" }, bar, page);
}
