// Editor feature: files other than images inside a note, and ```mermaid diagrams.
//   ![[report.pdf]]  ![[clip.mp4]]  ![[voice.m4a]]  ![[data.csv]]  -> a viewer in the note
//   any other file   -> a file card
// Everything is decrypted into memory only (blob URLs), never written to disk.
import { WidgetType } from "@codemirror/view";

export const VIDEO = /\.(mp4|m4v|mov|webm)$/i;
export const AUDIO = /\.(mp3|m4a|aac|wav|ogg|oga|flac)$/i;
export const PDF = /\.pdf$/i;
export const CSV = /\.(csv|tsv)$/i;

export default function media() {
  return { extensions: [], completions: [] };
}

// The widget for a non-image embed, or null when the name isn't a file (then it's a note embed).
export function mediaWidget(name, opts) {
  if (VIDEO.test(name)) return new PlayerWidget(name, "video", opts);
  if (AUDIO.test(name)) return new PlayerWidget(name, "audio", opts);
  if (PDF.test(name)) return new PdfWidget(name, opts);
  if (CSV.test(name)) return new CsvWidget(name, opts);
  if (/\.[a-z0-9]{1,6}$/i.test(name) && !/\.md$/i.test(name)) return new FileCardWidget(name, opts);
  return null;
}

function missing(wrap, text) { wrap.classList.add("md-missing"); wrap.textContent = text; return wrap; }

class PlayerWidget extends WidgetType {
  constructor(name, kind, opts) { super(); this.name = name; this.kind = kind; this.opts = opts; }
  eq(o) { return o.name === this.name && o.kind === this.kind; }
  toDOM() {
    const wrap = document.createElement("div"); wrap.className = `md-media md-media-${this.kind}`;
    const path = this.opts.resolveFile(this.name);
    if (!path) return missing(wrap, `Not found: ${this.name}`);
    const el = document.createElement(this.kind); el.controls = true; el.preload = "metadata";
    this.opts.loadImage(path).then((url) => { el.src = url; }).catch(() => missing(wrap, `Can't open ${this.name}`));
    const cap = document.createElement("div"); cap.className = "md-media-caption"; cap.textContent = this.name.split("/").pop();
    wrap.append(el, cap);
    return wrap;
  }
  ignoreEvent() { return true; }
}

class PdfWidget extends WidgetType {
  constructor(name, opts) { super(); this.name = name; this.opts = opts; }
  eq(o) { return o.name === this.name; }
  toDOM() {
    const wrap = document.createElement("div"); wrap.className = "md-media md-pdf";
    const path = this.opts.resolveFile(this.name);
    if (!path) return missing(wrap, `Not found: ${this.name}`);
    const frame = document.createElement("iframe");
    frame.title = this.name; frame.setAttribute("sandbox", "");   // a PDF needs no scripts or forms
    this.opts.loadImage(path).then((url) => { frame.src = url; }).catch(() => missing(wrap, `Can't open ${this.name}`));
    const cap = document.createElement("div"); cap.className = "md-media-caption"; cap.textContent = this.name.split("/").pop();
    wrap.append(frame, cap);
    return wrap;
  }
  ignoreEvent() { return true; }
}

class CsvWidget extends WidgetType {
  constructor(name, opts) { super(); this.name = name; this.opts = opts; }
  eq(o) { return o.name === this.name; }
  toDOM() {
    const wrap = document.createElement("div"); wrap.className = "md-media md-csv";
    const path = this.opts.resolveFile(this.name);
    if (!path || !this.opts.readFileText) return missing(wrap, `Not found: ${this.name}`);
    this.opts.readFileText(path).then((text) => {
      const rows = parseCsv(text, /\.tsv$/i.test(path) ? "\t" : ",");
      const shown = rows.slice(0, 200).map((r) => r.slice(0, 50));
      const table = document.createElement("table"); table.className = "md-table";
      shown.forEach((cells, i) => {
        const tr = document.createElement("tr");
        cells.forEach((c) => { const td = document.createElement(i === 0 ? "th" : "td"); td.textContent = c; tr.append(td); });
        (i === 0 ? table.createTHead() : (table.tBodies[0] || table.createTBody())).append(tr);
      });
      const scroller = document.createElement("div"); scroller.className = "md-table-wrap"; scroller.append(table);
      const cap = document.createElement("div"); cap.className = "md-media-caption";
      cap.textContent = `${this.name.split("/").pop()} · ${rows.length} rows${rows.length > 200 ? " (first 200 shown)" : ""}`;
      wrap.append(scroller, cap);
    }).catch(() => missing(wrap, `Can't open ${this.name}`));
    return wrap;
  }
  ignoreEvent() { return true; }
}

// A whole CSV/TSV file as a table (the file preview tab). Built with textContent only.
export function csvTable(text, path) {
  const rows = parseCsv(text, /\.tsv$/i.test(path) ? "\t" : ",");
  const shown = rows.slice(0, 5000);
  const table = document.createElement("table"); table.className = "md-table";
  shown.forEach((cells, i) => {
    const tr = document.createElement("tr");
    cells.forEach((c) => { const td = document.createElement(i === 0 ? "th" : "td"); td.textContent = c; tr.append(td); });
    (i === 0 ? table.createTHead() : (table.tBodies[0] || table.createTBody())).append(tr);
  });
  const wrap = document.createElement("div"); wrap.className = "md-table-wrap"; wrap.append(table);
  const cap = document.createElement("div"); cap.className = "md-media-caption";
  cap.textContent = `${rows.length} rows${rows.length > 5000 ? " (first 5,000 shown)" : ""}`;
  const out = document.createElement("div"); out.append(wrap, cap);
  return out;
}

function parseCsv(text, sep) {
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

class FileCardWidget extends WidgetType {
  constructor(name, opts) { super(); this.name = name; this.opts = opts; }
  eq(o) { return o.name === this.name; }
  toDOM() {
    const card = document.createElement("span"); card.className = "md-file-card";
    const path = this.opts.resolveFile(this.name);
    const ext = (this.name.split(".").pop() || "").toUpperCase();
    const badge = document.createElement("span"); badge.className = "md-file-ext"; badge.textContent = ext;
    const label = document.createElement("span"); label.textContent = this.name.split("/").pop();
    card.append(badge, label);
    if (!path) card.classList.add("md-missing");
    return card;
  }
}

// ```mermaid blocks: drawn as an SVG image. Shown through <img>, so nothing in the diagram can run.
let mermaidReady = null;
function loadMermaid() {
  mermaidReady ??= import("mermaid").then(({ default: m }) => {
    const theme = document.documentElement.dataset.theme;
    const dark = theme ? theme === "dark" : !matchMedia("(prefers-color-scheme: light)").matches;
    m.initialize({ startOnLoad: false, securityLevel: "strict", theme: dark ? "dark" : "default",
                   flowchart: { htmlLabels: false }, htmlLabels: false, maxTextSize: 20000 });
    return m;
  });
  return mermaidReady;
}
let diagramCount = 0;

export class MermaidWidget extends WidgetType {
  constructor(code, from) { super(); this.code = code; this.from = from; }
  eq(o) { return o.code === this.code; }
  toDOM(view) {
    const wrap = document.createElement("div"); wrap.className = "md-mermaid";
    wrap.textContent = "Drawing diagram";
    if (this.code.length > 20000) return missing(wrap, "This diagram is too big to draw.");
    loadMermaid().then((m) => m.render(`pm-diagram-${++diagramCount}`, this.code)).then(({ svg }) => {
      const img = document.createElement("img"); img.alt = "Diagram";
      img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
      wrap.textContent = ""; wrap.append(img);
    }).catch((e) => { wrap.textContent = ""; missing(wrap, `Diagram error: ${String(e.message || e).split("\n")[0]}`); });
    wrap.addEventListener("mousedown", (e) => {   // click: edit the diagram's text
      e.preventDefault(); view.dispatch({ selection: { anchor: this.from + 1 } }); view.focus();
    });
    return wrap;
  }
  ignoreEvent() { return false; }
}
