// An editable table for CSV/TSV files. Our own small grid: each cell is a plain-text editable box. Every change
// calls onChange(newText); the caller saves it.
import { t } from "./i18n.js";
import { el, icon } from "./dom.js";

export const CSV_EDIT_MAX_ROWS = 5000;

export function parseCsv(text, sep) {
  const rows = []; let row = [], cur = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { cur += '"'; i++; }
      else if (ch === '"') quoted = false;
      else cur += ch;
    } else if (ch === '"' && cur === "") quoted = true;
    else if (ch === sep) { row.push(cur); cur = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++;
      row.push(cur); rows.push(row); row = []; cur = "";
    } else cur += ch;
  }
  if (cur || row.length) { row.push(cur); rows.push(row); }
  return rows;
}

export function toCsv(rows, sep, eol) {
  const q = (c) => (c.includes(sep) || c.includes('"') || c.includes("\n") || c.includes("\r") ? '"' + c.replace(/"/g, '""') + '"' : c);
  return rows.map((r) => r.map(q).join(sep)).join(eol) + (rows.length ? eol : "");
}

// text: the file's text. Returns the element. The file's own separator and line endings are kept.
export function csvEditor(text, path, onChange) {
  const sep = /\.tsv$/i.test(path) ? "\t" : ",";
  const eol = text.includes("\r\n") ? "\r\n" : "\n";
  let rows = parseCsv(text, sep);
  if (!rows.length) rows = [[""]];
  let at = { r: 0, c: 0 };   // the last cell the person was in

  const table = el("table", { class: "md-table csv-edit" });
  const cap = el("span", { class: "csv-cap" });
  const width = () => Math.max(1, ...rows.map((r) => r.length));
  const changed = () => { cap.textContent = t("{0} rows · {1} columns", rows.length, width()); onChange(toCsv(rows, sep, eol)); };

  function draw(focus) {
    const w = width();
    table.replaceChildren();
    const head = table.createTHead(), body = table.createTBody();
    rows.forEach((cells, r) => {
      const tr = el("tr");
      for (let c = 0; c < w; c++) {
        const cell = el(r === 0 ? "th" : "td", { contenteditable: "plaintext-only", spellcheck: "false" });
        cell.textContent = cells[c] ?? "";
        cell.addEventListener("focus", () => { at = { r, c }; });
        cell.addEventListener("input", () => {
          while (rows[r].length <= c) rows[r].push("");
          rows[r][c] = cell.innerText.replace(/\n$/, "");
          changed();
        });
        cell.addEventListener("keydown", (e) => {   // Enter goes down a row, like a spreadsheet; Shift+Enter is a new line
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            const next = table.rows[r + 1] && table.rows[r + 1].cells[c];
            if (next) next.focus(); else { addRow(r + 1); }
          }
        });
        tr.append(cell);
      }
      (r === 0 ? head : body).append(tr);
    });
    cap.textContent = t("{0} rows · {1} columns", rows.length, w);
    if (focus) { const cell = table.rows[focus.r] && table.rows[focus.r].cells[focus.c]; cell && cell.focus(); }
  }

  function addRow(where) {
    rows.splice(where, 0, Array(width()).fill(""));
    draw({ r: where, c: at.c }); changed();
  }
  function addCol() {
    const c = at.c + 1;
    rows.forEach((r) => { while (r.length < c) r.push(""); r.splice(c, 0, ""); });
    draw({ r: at.r, c }); changed();
  }
  function delRow() {
    if (rows.length <= 1) return;
    rows.splice(at.r, 1);
    draw({ r: Math.min(at.r, rows.length - 1), c: at.c }); changed();
  }
  function delCol() {
    if (width() <= 1) return;
    rows.forEach((r) => r.splice(at.c, 1));
    draw({ r: at.r, c: Math.min(at.c, width() - 1) }); changed();
  }
  const btn = (label, fn, title) => el("button", { class: "btn small", type: "button", title, onclick: fn }, label);
  const bar = el("div", { class: "csv-bar" },
    btn(t("Add row"), () => addRow(at.r + 1), t("Add a row below the selected cell")),
    btn(t("Add column"), addCol, t("Add a column right of the selected cell")),
    btn(t("Delete row"), delRow, t("Delete the selected cell's row")),
    btn(t("Delete column"), delCol, t("Delete the selected cell's column")),
    cap);
  draw();
  return el("div", { class: "csv-editor" }, bar, el("div", { class: "md-table-wrap" }, table));
}
