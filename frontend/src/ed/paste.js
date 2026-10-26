// Paste: URL over a selection becomes a link; HTML from a web page becomes clean Markdown. Files and plain text are left alone.
import { EditorView } from "@codemirror/view";
import { syntaxTree } from "@codemirror/language";

const SAFE_HREF = /^(https?:|mailto:|tel:|#|\/|\.{1,2}\/|[^:]*$)/i;
const SAFE_SRC = /^(https?:|\/|\.{1,2}\/|[^:]*$)/i;
const SKIP = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE", "HEAD", "META", "LINK", "IFRAME", "OBJECT", "EMBED", "SVG", "CANVAS", "BUTTON", "SELECT", "TEXTAREA", "FORM", "TITLE"]);
const BLOCK = new Set(["P", "DIV", "SECTION", "ARTICLE", "MAIN", "HEADER", "FOOTER", "ASIDE", "NAV", "FIGURE", "FIGCAPTION", "DETAILS", "SUMMARY", "ADDRESS", "BODY", "HTML", "DL", "DD", "DT"]);

const urlSafe = (u) => u.trim().replace(/ /g, "%20").replace(/\(/g, "%28").replace(/\)/g, "%29");

function inline(node, ctx) {
  return [...node.childNodes].map((c) => convert(c, ctx)).join("");
}

// no stray spaces at the edges of a block or after a line break
const tidy = (t) => t.replace(/^ +| +$/g, "").replace(/(  \n) +/g, "$1");

function wrap(mark, text) {
  const m = /^(\s*)([\s\S]*?)(\s*)$/.exec(text);
  return m[2] ? m[1] + mark + m[2] + mark + m[3] : text;
}

function tableToMd(table, ctx) {
  const rows = [...table.querySelectorAll("tr")].filter((tr) => tr.closest("table") === table).map((tr) =>
    [...tr.children].filter((c) => /^(TD|TH)$/.test(c.tagName)).map((c) =>
      inline(c, ctx).replace(/\s*\n\s*/g, " ").replace(/\|/g, "\\|").trim()));
  const cols = Math.max(0, ...rows.map((r) => r.length));
  if (!rows.length || !cols) return "";
  const pad = (r) => { while (r.length < cols) r.push(""); return "| " + r.join(" | ") + " |"; };
  return "\n\n" + [pad(rows[0]), "| " + Array(cols).fill("---").join(" | ") + " |", ...rows.slice(1).map(pad)].join("\n") + "\n\n";
}

function listToMd(list, ctx) {
  const ordered = list.tagName === "OL";
  let n = parseInt(list.getAttribute("start") || "1", 10) || 1;
  const out = [];
  for (const li of list.children) {
    if (li.tagName !== "LI") continue;
    const marker = ordered ? `${n++}. ` : "- ";
    let text = "";
    for (const c of li.childNodes) {
      if (c.nodeType === 1 && (c.tagName === "UL" || c.tagName === "OL")) text += "\n" + listToMd(c, ctx);
      else if (c.nodeType === 1 && c.tagName === "INPUT" && c.getAttribute("type") === "checkbox") text += c.hasAttribute("checked") ? "[x] " : "[ ] ";
      else if (c.nodeType === 1 && (BLOCK.has(c.tagName) || /^H[1-6]$/.test(c.tagName))) text += "\n" + inline(c, ctx) + "\n";
      else text += convert(c, ctx);
    }
    text = tidy(text.replace(/[ \t]*\n[ \t]*\n+/g, "\n").trim());
    const pad = " ".repeat(marker.length);
    out.push(marker + text.split("\n").map((l, i) => (i && l.trim() ? pad + l : l)).join("\n"));
  }
  return out.join("\n");
}

function convert(node, ctx) {
  if (node.nodeType === 3) {
    const t = node.nodeValue;
    return ctx.pre ? t : t.replace(/[ \t\r\n\u00a0]+/g, " ");
  }
  if (node.nodeType !== 1) return "";               // comments and the rest
  const tag = node.tagName.toUpperCase();
  if (SKIP.has(tag)) return "";
  const style = (node.getAttribute("style") || "").toLowerCase();
  if (/display\s*:\s*none/.test(style)) return "";
  if (/^H[1-6]$/.test(tag)) {
    const text = inline(node, ctx).replace(/\s+/g, " ").trim();
    return text ? `\n\n${"#".repeat(+tag[1])} ${text}\n\n` : "";
  }
  switch (tag) {
    case "BR": return "  \n";
    case "HR": return "\n\n---\n\n";
    case "STRONG": return wrap("**", inline(node, ctx));
    case "B": return /font-weight\s*:\s*(normal|400)/.test(style) ? inline(node, ctx) : wrap("**", inline(node, ctx));
    case "EM": case "I": return wrap("*", inline(node, ctx));
    case "DEL": case "S": case "STRIKE": return wrap("~~", inline(node, ctx));
    case "MARK": return wrap("==", inline(node, ctx));
    case "CODE": case "KBD": case "SAMP": {
      if (ctx.pre) return inline(node, ctx);
      const text = node.textContent.replace(/\s+/g, " ").trim();
      if (!text) return "";
      const fence = "`".repeat((Math.max(0, ...(text.match(/`+/g) || []).map((s) => s.length))) + 1);
      return fence + (text.startsWith("`") || text.endsWith("`") ? ` ${text} ` : text) + fence;
    }
    case "PRE": {
      const code = node.querySelector("code");
      const lang = ((code || node).getAttribute("class") || "").match(/(?:language|lang)-([\w+#-]+)/)?.[1] || "";
      const text = (code || node).textContent.replace(/\r/g, "").replace(/\n+$/, "");
      const fence = "`".repeat(Math.max(3, ...(text.match(/`{3,}/g) || []).map((s) => s.length + 1)));
      return `\n\n${fence}${lang}\n${text}\n${fence}\n\n`;
    }
    case "A": {
      const href = node.getAttribute("href") || "";
      const text = inline(node, ctx).replace(/\s+/g, " ").trim();
      if (!href || !SAFE_HREF.test(href.trim())) return text;
      if (!text) return href.trim();
      if (text === href.trim()) return href.trim();
      return `[${text}](${urlSafe(href)})`;
    }
    case "IMG": {
      const src = node.getAttribute("src") || "";
      const alt = (node.getAttribute("alt") || "").replace(/[\[\]\n]/g, " ").trim();
      return src && SAFE_SRC.test(src.trim()) ? `![${alt}](${urlSafe(src)})` : alt;
    }
    case "UL": case "OL": return "\n\n" + listToMd(node, ctx) + "\n\n";
    case "LI": return "\n- " + inline(node, ctx).trim() + "\n";   // stray <li> outside a list
    case "BLOCKQUOTE": {
      const inner = clean(inline(node, ctx));
      return inner ? "\n\n" + inner.split("\n").map((l) => (l ? "> " + l : ">")).join("\n") + "\n\n" : "";
    }
    case "TABLE": return tableToMd(node, ctx);
    case "INPUT": return node.getAttribute("type") === "checkbox" ? (node.hasAttribute("checked") ? "[x] " : "[ ] ") : "";
    default: {
      const inner = inline(node, ctx);
      return BLOCK.has(tag) ? `\n\n${tidy(inner)}\n\n` : inner;
    }
  }
}

function clean(md) {
  return md.replace(/\u00a0/g, " ").replace(/[ \t]+\n/g, (m) => (/ {2}\n$/.test(m) ? "  \n" : "\n"))
    .replace(/\n{3,}/g, "\n\n").replace(/^\n+|\s+$/g, "");
}

// html string -> Markdown string. Uses DOMParser: nothing in the HTML is run, and no HTML is ever kept.
export function htmlToMarkdown(html, parser = new DOMParser()) {
  const doc = parser.parseFromString(html, "text/html");
  const body = doc.body || doc.documentElement;
  return clean(convert(body, { pre: false }));
}

const inCode = (state, pos) => {
  for (let n = syntaxTree(state).resolveInner(pos, -1); n; n = n.parent) {
    if (n.name === "FencedCode" || n.name === "CodeBlock" || n.name === "InlineCode") return true;
  }
  return false;
};

function onPaste(event, view) {
  const data = event.clipboardData;
  if (!data) return false;
  if (data.files && data.files.length) return false;            // images etc.: the upload handler takes it
  const text = data.getData("text/plain") || "";
  const sel = view.state.selection.main;
  if (!sel.empty && /^(https?:\/\/|mailto:)\S+$/i.test(text.trim()) && !inCode(view.state, sel.head)) {
    const label = view.state.sliceDoc(sel.from, sel.to);
    const insert = `[${label}](${urlSafe(text)})`;
    event.preventDefault();
    view.dispatch({ changes: { from: sel.from, to: sel.to, insert }, selection: { anchor: sel.from + insert.length }, userEvent: "input.paste", scrollIntoView: true });
    return true;
  }
  const html = data.getData("text/html");
  if (!html || inCode(view.state, sel.head)) return false;
  if ([...(data.types || [])].includes("vscode-editor-data")) return false;   // copied from a code editor
  let md;
  try { md = htmlToMarkdown(html); } catch { return false; }
  if (!md) return false;
  if (md.replace(/\s+/g, " ").trim() === text.replace(/\s+/g, " ").trim()) return false;   // plain text anyway
  event.preventDefault();
  view.dispatch({ ...view.state.replaceSelection(md), userEvent: "input.paste", scrollIntoView: true });
  return true;
}

export default function paste() {
  return { extensions: [EditorView.domEventHandlers({ paste: onPaste })], completions: [] };
}
