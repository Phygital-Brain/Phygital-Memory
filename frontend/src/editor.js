// The note editor: CodeMirror 6 with live preview. The file stays plain Markdown; the screen hides the markup
// (#, **, [[ ]], fences...) everywhere except where the cursor is, like Obsidian and Baalda.
//
//   createEditor(parent, {
//     text, onChange(text), onSave(),
//     openLink(target),               // a [[wikilink]] was clicked: "Note", "Folder/Note", "Note#Heading"
//     noteNames(),                    // note paths for [[ autocomplete, e.g. ["Ideas/Pocket-Library.md", ...]
//     resolveFile(name),              // "pic.png" or "Folder/pic.png" -> full path in the notes, or null
//     loadImage(path),                // -> Promise of a blob: URL
//     uploadFile(file),               // pasted or dropped file -> Promise of its saved path
//   }) -> { view, getText(), setText(text), focus(), destroy() }
import { EditorState, StateField, StateEffect, RangeSetBuilder, Prec } from "@codemirror/state";
import { EditorView, Decoration, WidgetType, keymap, drawSelection, highlightActiveLine, dropCursor,
         rectangularSelection, placeholder } from "@codemirror/view";
import { defaultKeymap, history, historyKeymap, indentWithTab } from "@codemirror/commands";
import { syntaxTree, ensureSyntaxTree, syntaxHighlighting, HighlightStyle, indentOnInput,
         bracketMatching } from "@codemirror/language";
import { markdown, markdownLanguage, markdownKeymap } from "@codemirror/lang-markdown";
import { languages } from "@codemirror/language-data";
import { autocompletion, closeBrackets, closeBracketsKeymap, completionKeymap } from "@codemirror/autocomplete";
import { searchKeymap, highlightSelectionMatches } from "@codemirror/search";
import { tags as t, styleTags, Tag } from "@lezer/highlight";
import "./editor.css";
// Feature files: each returns { extensions, completions } (see ed/*.js).
import slash from "./ed/slash.js";
import shortcuts from "./ed/shortcuts.js";
import paste from "./ed/paste.js";
import comments from "./ed/comments.js";
import tagsFeature from "./ed/tags.js";
import guides from "./ed/guides.js";
import tables from "./ed/tables.js";
import folding from "./ed/folding.js";
import media from "./ed/media.js";

const FEATURES = [slash, shortcuts, paste, comments, tagsFeature, guides, tables, folding, media];

// ---------- extra Markdown syntax: ==highlight==, [[wikilinks]], ![[embeds]], #tags ----------

const highlightTag = Tag.define(), wikiTag = Tag.define(), tagTag = Tag.define();
const HighlightDelim = { resolve: "Highlight", mark: "HighlightMark" };
const SPACE = /\s/;

const ObsidianSyntax = {
  defineNodes: [
    { name: "Highlight", style: highlightTag }, { name: "HighlightMark", style: t.processingInstruction },
    { name: "WikiLink", style: wikiTag }, { name: "Embed", style: wikiTag }, { name: "WikiMark", style: t.processingInstruction },
    { name: "Tag", style: tagTag },
  ],
  parseInline: [
    {
      name: "Highlight",
      parse(cx, next, pos) {
        if (next !== 61 || cx.char(pos + 1) !== 61 || cx.char(pos + 2) === 61) return -1;
        const before = cx.slice(pos - 1, pos), after = cx.slice(pos + 2, pos + 3);
        return cx.addDelimiter(HighlightDelim, pos, pos + 2, !SPACE.test(after || " "), !SPACE.test(before || " "));
      },
      after: "Emphasis",
    },
    {
      name: "WikiLink",
      parse(cx, next, pos) {
        const embed = next === 33;  // "!"
        const open = embed ? pos + 1 : pos;
        if (cx.char(open) !== 91 || cx.char(open + 1) !== 91) return -1;
        const rest = cx.slice(open + 2, cx.end);
        const close = rest.indexOf("]]");
        if (close <= 0 || rest.slice(0, close).includes("[[")) return -1;
        const end = open + 2 + close + 2;
        return cx.addElement(cx.elt(embed ? "Embed" : "WikiLink", pos, end,
          [cx.elt("WikiMark", pos, open + 2), cx.elt("WikiMark", end - 2, end)]));
      },
      before: "Link",
    },
    {
      name: "Tag",
      parse(cx, next, pos) {
        if (next !== 35) return -1;
        if (pos > cx.offset && !SPACE.test(cx.slice(pos - 1, pos))) return -1;
        const m = /^#[\p{L}\p{N}_][\p{L}\p{N}_/-]*/u.exec(cx.slice(pos, cx.end));
        if (!m || /^#\d+$/.test(m[0])) return -1;
        return cx.addElement(cx.elt("Tag", pos, pos + m[0].length));
      },
      after: "Emphasis",
    },
  ],
};

const syntaxColours = HighlightStyle.define([
  { tag: t.heading, class: "md-heading" },
  { tag: t.strong, class: "md-strong" },
  { tag: t.emphasis, class: "md-em" },
  { tag: t.strikethrough, class: "md-strike" },
  { tag: highlightTag, class: "md-highlight" },
  { tag: wikiTag, class: "md-wiki" },
  { tag: tagTag, class: "md-tag" },
  { tag: t.link, class: "md-link" },
  { tag: t.url, class: "md-url" },
  { tag: t.monospace, class: "md-code" },
  { tag: t.quote, class: "md-quote" },
  { tag: [t.processingInstruction, t.meta], class: "md-mark" },
  // inside code blocks
  { tag: t.keyword, class: "tok-keyword" }, { tag: [t.string, t.special(t.string)], class: "tok-string" },
  { tag: t.comment, class: "tok-comment" }, { tag: [t.number, t.bool, t.null], class: "tok-number" },
  { tag: [t.function(t.variableName), t.function(t.propertyName)], class: "tok-function" },
  { tag: [t.typeName, t.className], class: "tok-type" }, { tag: t.propertyName, class: "tok-property" },
  { tag: [t.operator, t.punctuation], class: "tok-punct" }, { tag: t.tagName, class: "tok-tag" },
  { tag: t.attributeName, class: "tok-attr" },
]);

// ---------- small safe renderer for inline Markdown inside widgets (tables, callout titles) ----------

function inlineDOM(text, parent, opts) {
  const re = /(\*\*|__)(.+?)\1|(\*|_)(.+?)\3|~~(.+?)~~|==(.+?)==|`([^`]+)`|!?\[\[([^\]]+)\]\]|\[([^\]]+)\]\(([^)\s]+)\)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) parent.append(text.slice(last, m.index));
    let el;
    if (m[2] !== undefined) { el = document.createElement("strong"); inlineDOM(m[2], el, opts); }
    else if (m[4] !== undefined) { el = document.createElement("em"); inlineDOM(m[4], el, opts); }
    else if (m[5] !== undefined) { el = document.createElement("s"); inlineDOM(m[5], el, opts); }
    else if (m[6] !== undefined) { el = document.createElement("mark"); inlineDOM(m[6], el, opts); }
    else if (m[7] !== undefined) { el = document.createElement("code"); el.textContent = m[7]; }
    else if (m[8] !== undefined) {
      const [target, alias] = splitWiki(m[8]);
      el = document.createElement("a"); el.className = "md-wiki"; el.textContent = alias;
      el.addEventListener("mousedown", (e) => { e.preventDefault(); opts.openLink(target); });
    } else {
      el = document.createElement("span"); el.className = "md-link"; el.textContent = m[9]; el.title = m[10];
    }
    parent.append(el);
    last = m.index + m[0].length;
  }
  if (last < text.length) parent.append(text.slice(last));
}

function splitWiki(inner) {
  const bar = inner.indexOf("|");
  const target = (bar < 0 ? inner : inner.slice(0, bar)).trim();
  const alias = bar < 0 ? target.split("#")[0].split("/").pop() + (target.includes("#") ? " › " + target.split("#")[1] : "")
                        : inner.slice(bar + 1).trim();
  return [target, alias || target];
}

// ---------- widgets ----------

class CheckboxWidget extends WidgetType {
  constructor(checked, pos) { super(); this.checked = checked; this.pos = pos; }
  eq(o) { return o.checked === this.checked && o.pos === this.pos; }
  toDOM(view) {
    const box = document.createElement("input");
    box.type = "checkbox"; box.className = "md-check"; box.checked = this.checked;
    box.addEventListener("mousedown", (e) => {
      e.preventDefault();
      view.dispatch({ changes: { from: this.pos + 1, to: this.pos + 2, insert: this.checked ? " " : "x" } });
    });
    return box;
  }
  ignoreEvent() { return false; }
}

class BulletWidget extends WidgetType {
  eq() { return true; }
  toDOM() { const s = document.createElement("span"); s.className = "md-bullet"; s.textContent = "•"; return s; }
}

class RuleWidget extends WidgetType {
  eq() { return true; }
  toDOM() { const d = document.createElement("div"); d.className = "md-hr"; return d; }
}

// Images: click opens the full view; drag the corner to resize, and the width is written into the note
// (![[pic.png|300]] or ![alt|300](pic.png)), like Baalda and Obsidian.
class ImageWidget extends WidgetType {
  constructor(src, alt, width, opts) { super(); this.src = src; this.alt = alt; this.width = width; this.opts = opts; }
  eq(o) { return o.src === this.src && o.width === this.width && o.alt === this.alt; }
  toDOM(view) {
    const wrap = document.createElement("span"); wrap.className = "md-embed";
    const path = this.opts.resolveFile(this.src);
    if (!path) { wrap.classList.add("md-missing"); wrap.textContent = `Not found: ${this.src}`; return wrap; }
    const img = document.createElement("img"); img.alt = this.alt || this.src; img.draggable = false;
    if (this.width) img.style.width = `${this.width}px`;
    this.opts.loadImage(path).then((url) => { img.src = url; })
      .catch(() => { wrap.classList.add("md-missing"); wrap.textContent = `Can't open ${this.src}`; });
    const handle = document.createElement("span"); handle.className = "md-resize"; handle.title = "Drag to resize";
    wrap.append(img, handle);

    img.addEventListener("mousedown", (e) => { e.preventDefault(); });
    img.addEventListener("click", (e) => { e.preventDefault(); openLightbox(img.src, img.alt); });
    handle.addEventListener("mousedown", (e) => {
      e.preventDefault(); e.stopPropagation();
      const startX = e.clientX, startW = img.getBoundingClientRect().width;
      const max = view.contentDOM.getBoundingClientRect().width;
      wrap.classList.add("md-resizing");
      const move = (ev) => { img.style.width = `${Math.round(Math.max(48, Math.min(max, startW + ev.clientX - startX)))}px`; };
      const up = () => {
        document.removeEventListener("mousemove", move); document.removeEventListener("mouseup", up);
        wrap.classList.remove("md-resizing");
        setImageWidth(view, view.posAtDOM(wrap), Math.round(img.getBoundingClientRect().width));
      };
      document.addEventListener("mousemove", move); document.addEventListener("mouseup", up);
    });
    return wrap;
  }
  ignoreEvent() { return true; }
}

function setImageWidth(view, pos, width) {
  const line = view.state.doc.lineAt(pos);
  const text = line.text, at = pos - line.from;
  let m = /^!\[\[([^\]|]+)(\|[^\]]*)?\]\]/.exec(text.slice(at));
  if (m) {
    const insert = `![[${m[1]}|${width}]]`;
    view.dispatch({ changes: { from: pos, to: pos + m[0].length, insert } });
    return;
  }
  m = /^!\[([^\]|]*)(\|\d+)?\]\(([^)]*)\)/.exec(text.slice(at));
  if (m) view.dispatch({ changes: { from: pos, to: pos + m[0].length, insert: `![${m[1]}|${width}](${m[3]})` } });
}

function openLightbox(src, alt) {
  if (!src) return;
  const back = document.createElement("div"); back.className = "md-lightbox";
  const img = document.createElement("img"); img.src = src; img.alt = alt || "";
  const cap = document.createElement("div"); cap.className = "md-lightbox-caption"; cap.textContent = alt || "";
  back.append(img, cap);
  const close = () => { back.remove(); document.removeEventListener("keydown", key, true); };
  const key = (e) => { if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(); } };
  img.addEventListener("click", (e) => { e.stopPropagation(); img.classList.toggle("md-lightbox-actual"); });
  back.addEventListener("click", close);
  document.addEventListener("keydown", key, true);
  document.body.append(back);
}

class NoteEmbedWidget extends WidgetType {
  constructor(target, opts) { super(); this.target = target; this.opts = opts; }
  eq(o) { return o.target === this.target; }
  toDOM() {
    const box = document.createElement("span"); box.className = "md-note-embed";
    box.textContent = `↪ ${this.target}`;
    box.addEventListener("mousedown", (e) => { e.preventDefault(); this.opts.openLink(this.target); });
    return box;
  }
  ignoreEvent() { return false; }
}

class WikiWidget extends WidgetType {
  constructor(target, alias, exists, opts) { super(); this.target = target; this.alias = alias; this.exists = exists; this.opts = opts; }
  eq(o) { return o.target === this.target && o.alias === this.alias && o.exists === this.exists; }
  toDOM() {
    const a = document.createElement("a");
    a.className = "md-wiki" + (this.exists ? "" : " md-wiki-missing"); a.textContent = this.alias;
    a.title = this.target;
    a.addEventListener("mousedown", (e) => { e.preventDefault(); this.opts.openLink(this.target); });
    return a;
  }
  ignoreEvent() { return false; }
}

class CodeHeaderWidget extends WidgetType {
  constructor(lang, code) { super(); this.lang = lang; this.code = code; }
  eq(o) { return o.lang === this.lang && o.code === this.code; }
  toDOM() {
    const bar = document.createElement("span"); bar.className = "md-code-header";
    const label = document.createElement("span"); label.textContent = this.lang || "code";
    const copy = document.createElement("button"); copy.type = "button"; copy.className = "md-copy"; copy.textContent = "Copy";
    copy.addEventListener("mousedown", (e) => {
      e.preventDefault(); e.stopPropagation();
      navigator.clipboard.writeText(this.code).then(() => { copy.textContent = "Copied"; setTimeout(() => { copy.textContent = "Copy"; }, 1200); });
    });
    bar.append(label, copy);
    return bar;
  }
  ignoreEvent() { return true; }
}

class CalloutLabelWidget extends WidgetType {
  constructor(kind, title, opts) { super(); this.kind = kind; this.title = title; this.opts = opts; }
  eq(o) { return o.kind === this.kind && o.title === this.title; }
  toDOM() {
    const s = document.createElement("span"); s.className = "md-callout-title";
    const icon = document.createElement("span"); icon.className = "md-callout-icon"; icon.textContent = CALLOUT_ICONS[calloutGroup(this.kind)] || "ℹ";
    const title = document.createElement("span");
    inlineDOM(this.title || this.kind.charAt(0).toUpperCase() + this.kind.slice(1), title, this.opts);
    s.append(icon, title);
    return s;
  }
}

class TableWidget extends WidgetType {
  constructor(text, from, opts) { super(); this.text = text; this.from = from; this.opts = opts; }
  eq(o) { return o.text === this.text; }
  toDOM(view) {
    const lines = this.text.split("\n").filter((l) => l.trim());
    const rows = lines.map(splitRow);
    const aligns = (rows[1] || []).map((c) => (/^:-+:$/.test(c) ? "center" : /-+:$/.test(c) ? "right" : "left"));
    const wrap = document.createElement("div"); wrap.className = "md-table-wrap";
    const table = document.createElement("table"); table.className = "md-table";
    rows.forEach((cells, i) => {
      if (i === 1) return;
      const tr = document.createElement("tr");
      cells.forEach((c, j) => {
        const td = document.createElement(i === 0 ? "th" : "td");
        td.style.textAlign = aligns[j] || "left";
        inlineDOM(c, td, this.opts);
        tr.append(td);
      });
      (i === 0 ? table.createTHead() : (table.tBodies[0] || table.createTBody())).append(tr);
    });
    wrap.append(table);
    wrap.addEventListener("mousedown", (e) => {
      if (e.target.closest("a")) return;
      e.preventDefault();
      view.dispatch({ selection: { anchor: this.from } }); view.focus();
    });
    return wrap;
  }
  ignoreEvent() { return false; }
}

function splitRow(line) {
  const cells = [];
  let cur = "", esc = false, code = false;
  for (const ch of line.trim().replace(/^\|/, "").replace(/\|$/, "")) {
    if (esc) { cur += ch; esc = false; continue; }
    if (ch === "\\") { esc = true; cur += ch; continue; }
    if (ch === "`") code = !code;
    if (ch === "|" && !code) { cells.push(cur.trim()); cur = ""; continue; }
    cur += ch;
  }
  cells.push(cur.trim());
  return cells;
}

const CALLOUT_ICONS = { note: "✎", info: "ℹ", tip: "💡", success: "✓", question: "?", warning: "⚠", failure: "✕",
                        danger: "⚡", bug: "🐞", example: "☰", quote: "❝", todo: "☐", abstract: "≡" };
const CALLOUT_ALIASES = { summary: "abstract", tldr: "abstract", hint: "tip", important: "tip", check: "success",
                          done: "success", help: "question", faq: "question", caution: "warning", attention: "warning",
                          fail: "failure", missing: "failure", error: "danger", cite: "quote" };
function calloutGroup(kind) { kind = kind.toLowerCase(); return CALLOUT_ALIASES[kind] || (CALLOUT_ICONS[kind] ? kind : "note"); }

// ---------- live preview: one pass over the syntax tree builds every decoration ----------

const hidden = Decoration.replace({});
const IMAGE_EXT = /\.(png|jpe?g|gif|webp|svg|avif|bmp)$/i;

// Markup shows again only where the cursor is, and only while the editor has focus (like Baalda).
const setFocused = StateEffect.define();
const focusedField = StateField.define({
  create: () => false,
  update: (v, tr) => tr.effects.reduce((acc, e) => (e.is(setFocused) ? e.value : acc), v),
});

function buildDecorations(state, opts) {
  const tree = ensureSyntaxTree(state, state.doc.length, 200) || syntaxTree(state);
  // Only a plain cursor reveals markup. A drag-selection reveals nothing, or the text would reflow under the
  // mouse and the selection would jump.
  const doc = state.doc, sel = state.field(focusedField, false) ? state.selection.ranges.filter((r) => r.empty) : [];
  const touches = (from, to) => sel.some((r) => r.from <= to && r.to >= from);
  const lineActive = (pos) => { const l = doc.lineAt(pos); return touches(l.from, l.to); };
  const blockActive = (from, to) => touches(doc.lineAt(from).from, doc.lineAt(to).to);
  const names = new Set(opts.noteNames().map((p) => p.replace(/\.md$/i, "").toLowerCase()));
  const baseNames = new Set([...names].map((n) => n.split("/").pop()));
  const exists = (target) => { const n = target.split("#")[0].toLowerCase(); return !n || names.has(n) || baseNames.has(n); };

  const items = [];   // [from, to, decoration]; sorted at the end
  const add = (from, to, deco) => items.push([from, to, deco]);
  const lineClass = (pos, cls) => { const l = doc.lineAt(pos); add(l.from, l.from, Decoration.line({ class: cls })); };

  tree.iterate({
    enter(node) {
      const { name, from, to } = node;
      if (/^ATXHeading(\d)$/.test(name)) {
        lineClass(from, `md-h md-h${name.slice(-1)}`);
        if (!lineActive(from)) {
          const mark = node.node.getChild("HeaderMark");
          if (mark) add(mark.from, Math.min(mark.to + 1, doc.lineAt(from).to), hidden);
        }
        return;
      }
      if (/^SetextHeading(\d)$/.test(name)) { lineClass(from, `md-h md-h${name.slice(-1)}`); return; }
      if (["EmphasisMark", "StrikethroughMark", "HighlightMark"].includes(name)) {
        const parent = node.node.parent;
        if (parent && !touches(parent.from, parent.to)) add(from, to, hidden);
        return;
      }
      if (name === "InlineCode") {
        if (!touches(from, to)) for (const m of node.node.getChildren("CodeMark")) add(m.from, m.to, hidden);
        return false;
      }
      if (name === "Link") {
        // "[!note]" opens a callout and "[^1]" is a footnote: neither is a link
        if (/^\[[!^]/.test(doc.sliceString(from, from + 2)) || touches(from, to)) return false;
        const marks = node.node.getChildren("LinkMark"), url = node.node.getChild("URL");
        if (marks.length >= 2) { add(marks[0].from, marks[0].to, hidden); add(marks[1].from, to, hidden); }
        if (url) add(marks[0].to, marks[1].from, Decoration.mark({ class: "md-link", attributes: { title: doc.sliceString(url.from, url.to) } }));
        return false;
      }
      if (name === "Image") {
        if (touches(from, to)) return false;
        const url = node.node.getChild("URL");
        const src = url ? doc.sliceString(url.from, url.to) : "";
        const label = doc.sliceString(from, to).replace(/^!\[|\]\(.*$/gs, "");
        const sized = /^(.*?)\|(\d+)$/.exec(label);   // ![alt|300](pic.png)
        const alt = sized ? sized[1] : label, width = sized ? parseInt(sized[2], 10) : null;
        if (src && !/^[a-z]+:/i.test(src)) {
          add(from, to, Decoration.replace({ widget: new ImageWidget(decodeURI(src).replace(/^\//, ""), alt, width, opts) }));
        }
        return false;
      }
      if (name === "WikiLink" || name === "Embed") {
        const inner = doc.sliceString(from + (name === "Embed" ? 3 : 2), to - 2);
        const [target, alias] = splitWiki(inner);
        if (touches(from, to)) return false;
        if (name === "Embed") {
          const file = target.split("#")[0];
          const size = /^\d+(x\d+)?$/.test(alias) ? parseInt(alias, 10) : null;
          const widget = IMAGE_EXT.test(file) ? new ImageWidget(file, size ? file : alias, size, opts) : new NoteEmbedWidget(target, opts);
          add(from, to, Decoration.replace({ widget }));
        } else {
          add(from, to, Decoration.replace({ widget: new WikiWidget(target, alias, exists(target), opts) }));
        }
        return false;
      }
      if (name === "ListMark") {
        const item = node.node.parent;
        const isTask = item && item.getChild("Task");
        if (lineActive(from)) return;
        const mark = doc.sliceString(from, to);
        if (isTask) add(from, Math.min(to + 1, doc.lineAt(from).to), hidden);
        else if (/^[-*+]$/.test(mark)) add(from, to, Decoration.replace({ widget: new BulletWidget() }));
        return;
      }
      if (name === "TaskMarker") {
        const checked = /x/i.test(doc.sliceString(from, to));
        if (checked) { const l = doc.lineAt(from); add(to, l.to, Decoration.mark({ class: "md-done" })); }
        if (!lineActive(from)) add(from, to, Decoration.replace({ widget: new CheckboxWidget(checked, from) }));
        return;
      }
      if (name === "Blockquote") {
        const first = doc.lineAt(from);
        const callout = /^>\s*\[!([\w-]+)\]([+-]?)\s*(.*)$/.exec(first.text);
        const kind = callout ? calloutGroup(callout[1]) : null;
        for (let pos = from; pos <= to;) {
          const l = doc.lineAt(pos);
          const cls = callout ? `md-callout md-callout-${kind}${l.from === first.from ? " md-callout-first" : ""}` : "md-blockquote";
          add(l.from, l.from, Decoration.line({ class: cls + (l.to >= to ? " md-block-last" : "") }));
          if (!blockActive(from, to)) {
            const q = /^(\s*>\s?)+/.exec(l.text);
            if (q) add(l.from, l.from + q[0].length, hidden);
          }
          pos = l.to + 1;
        }
        if (callout && !blockActive(from, to)) {
          const start = first.text.indexOf("[!");
          add(first.from + start, first.to, Decoration.replace({ widget: new CalloutLabelWidget(callout[1], callout[3], opts) }));
        }
        return;
      }
      if (name === "FencedCode") {
        const active = blockActive(from, to);
        const firstLine = doc.lineAt(from), lastLine = doc.lineAt(to);
        const info = node.node.getChild("CodeInfo");
        const lang = info ? doc.sliceString(info.from, info.to) : "";
        const text = node.node.getChild("CodeText");
        for (let pos = firstLine.from; pos <= lastLine.to;) {
          const l = doc.lineAt(pos);
          const edge = l.number === firstLine.number ? " md-codeblock-first" : l.number === lastLine.number ? " md-codeblock-last" : "";
          add(l.from, l.from, Decoration.line({ class: "md-codeblock" + edge }));
          pos = l.to + 1;
        }
        if (!active) {
          add(firstLine.from, firstLine.to, Decoration.replace({ widget: new CodeHeaderWidget(lang, text ? doc.sliceString(text.from, text.to) : "") }));
          if (lastLine.number !== firstLine.number && /^\s*(```|~~~)/.test(lastLine.text)) add(lastLine.from, lastLine.to, hidden);
        }
        return false;
      }
      if (name === "HorizontalRule") {
        if (!lineActive(from)) add(from, to, Decoration.replace({ widget: new RuleWidget() }));
        return;
      }
      if (name === "Table") {
        if (!blockActive(from, to)) {
          const a = doc.lineAt(from).from, b = doc.lineAt(to).to;
          add(a, b, Decoration.replace({ widget: new TableWidget(doc.sliceString(a, b), a, opts), block: true }));
        } else {
          for (let pos = from; pos <= to;) { const l = doc.lineAt(pos); add(l.from, l.from, Decoration.line({ class: "md-table-source" })); pos = l.to + 1; }
        }
        return false;
      }
    },
  });

  // Footnote references [^1] and definitions [^1]: (the base parser has no node for them)
  for (const m of doc.toString().matchAll(/\[\^([^\]\s]+)\](:?)/g)) {
    add(m.index, m.index + m[0].length, Decoration.mark({ class: m[2] ? "md-footnote-def" : "md-footnote" }));
  }

  items.sort((a, b) => a[0] - b[0] || startSide(a[2]) - startSide(b[2]) || a[1] - b[1]);
  const builder = new RangeSetBuilder();
  let lastTo = -1;
  for (const [from, to, deco] of items) {
    const replace = deco.spec.widget !== undefined || deco === hidden;
    if (replace && from < lastTo) continue;   // never overlap two replacements
    builder.add(from, to, deco);
    if (replace && to > from) lastTo = Math.max(lastTo, to);
  }
  return builder.finish();
}

function startSide(deco) { return deco.startSide ?? 0; }

function livePreview(opts) {
  return StateField.define({
    create: (state) => buildDecorations(state, opts),
    update(deco, tr) {
      if (tr.docChanged || tr.selection || tr.effects.length || syntaxTree(tr.startState) !== syntaxTree(tr.state)) {
        return buildDecorations(tr.state, opts);
      }
      return deco.map(tr.changes);
    },
    provide: (f) => EditorView.decorations.from(f),
  });
}

// ---------- [[ autocomplete ----------

function wikiCompletion(opts) {
  return (context) => {
    const m = context.matchBefore(/!?\[\[[^\]\n]*/);
    if (!m) return null;
    const start = m.from + m.text.indexOf("[[") + 2;
    const typed = context.state.sliceDoc(start, context.pos);
    const after = context.state.sliceDoc(context.pos, context.pos + 2);
    const files = opts.noteNames().concat(opts.attachmentNames ? opts.attachmentNames() : []);
    return {
      from: start,
      options: files.map((p) => {
        const isNote = /\.md$/i.test(p);
        const label = isNote ? p.replace(/\.md$/i, "").split("/").pop() : p.split("/").pop();
        return { label, detail: p.includes("/") ? p.slice(0, p.lastIndexOf("/")) : "", type: isNote ? "text" : "variable",
                 apply: label + (after === "]]" ? "" : "]]") };
      }),
      validFor: /^[^\]\n]*$/,
      filter: true,
      ...(typed ? {} : {}),
    };
  };
}

// ---------- paste / drop images ----------

function fileDrops(opts) {
  const insertFiles = (view, files, pos) => {
    files.forEach((file) => {
      opts.uploadFile(file).then((path) => {
        const name = path.split("/").pop();
        const at = pos ?? view.state.selection.main.head;
        view.dispatch({ changes: { from: at, insert: `![[${name}]]` } });
      }).catch((e) => console.error(e));
    });
  };
  return EditorView.domEventHandlers({
    paste(e, view) {
      const files = [...(e.clipboardData?.files || [])];
      if (!files.length) return false;
      e.preventDefault(); insertFiles(view, files, null); return true;
    },
    drop(e, view) {
      const files = [...(e.dataTransfer?.files || [])];
      if (!files.length) return false;
      e.preventDefault();
      insertFiles(view, files, view.posAtCoords({ x: e.clientX, y: e.clientY }));
      return true;
    },
  });
}

// ---------- formatting shortcuts ----------

function wrapWith(mark) {
  return (view) => {
    view.dispatch(view.state.changeByRange((r) => {
      const text = view.state.sliceDoc(r.from, r.to);
      const before = view.state.sliceDoc(r.from - mark.length, r.from), after = view.state.sliceDoc(r.to, r.to + mark.length);
      if (before === mark && after === mark) {
        return { changes: [{ from: r.from - mark.length, to: r.from }, { from: r.to, to: r.to + mark.length }],
                 range: { anchor: r.from - mark.length, head: r.to - mark.length } };
      }
      return { changes: { from: r.from, to: r.to, insert: mark + text + mark },
               range: { anchor: r.from + mark.length, head: r.to + mark.length } };
    }));
    return true;
  };
}

// ---------- the editor ----------

export function createEditor(parent, opts) {
  let silent = false;
  const features = FEATURES.map((f) => f(opts));
  const extensions = [
    ...features.flatMap((f) => f.extensions || []),
    history(),
    drawSelection(),
    dropCursor(),
    rectangularSelection(),
    indentOnInput(),
    bracketMatching(),
    closeBrackets(),
    highlightActiveLine(),
    highlightSelectionMatches(),
    EditorView.lineWrapping,
    placeholder("Start writing…"),
    markdown({ base: markdownLanguage, codeLanguages: languages, extensions: [ObsidianSyntax], addKeymap: true }),
    syntaxHighlighting(syntaxColours),
    focusedField,
    EditorView.focusChangeEffect.of((_state, focusing) => setFocused.of(focusing)),
    livePreview(opts),
    EditorView.theme({
      ".cm-scroller": { fontFamily: "var(--font-body)", lineHeight: "1.6" },
      ".cm-content": { fontFamily: "var(--font-body)" },
      ".cm-activeLine": { backgroundColor: "transparent" },
      "&.cm-focused": { outline: "none" },
    }),
    autocompletion({ override: [wikiCompletion(opts), ...features.flatMap((f) => f.completions || [])], icons: false }),
    fileDrops(opts),
    Prec.high(keymap.of([
      { key: "Mod-s", run: () => { opts.onSave?.(); return true; }, preventDefault: true },
      { key: "Escape", run: (view) => { view.contentDOM.blur(); return true; } },   // back to view mode
      { key: "Mod-b", run: wrapWith("**") },
      { key: "Mod-i", run: wrapWith("*") },
      { key: "Mod-Shift-x", run: wrapWith("~~") },
      { key: "Mod-Shift-h", run: wrapWith("==") },
      { key: "Mod-e", run: wrapWith("`") },
    ])),
    keymap.of([...closeBracketsKeymap, ...markdownKeymap, ...completionKeymap, ...searchKeymap, ...historyKeymap,
               ...defaultKeymap, indentWithTab]),
    EditorView.updateListener.of((u) => { if (u.docChanged && !silent) opts.onChange?.(u.state.doc.toString()); }),
    EditorView.contentAttributes.of({ spellcheck: "true", autocorrect: "on", autocapitalize: "sentences" }),
  ];
  const view = new EditorView({ state: EditorState.create({ doc: opts.text || "", extensions }), parent });
  return {
    view,
    getText: () => view.state.doc.toString(),
    setText(text) {
      silent = true;
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: text }, selection: { anchor: 0 } });
      silent = false;
    },
    refresh() { view.dispatch({}); },   // re-draw links after the note list changed
    focus: () => view.focus(),
    destroy: () => view.destroy(),
  };
}
