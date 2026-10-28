// #tag completion: after "#" + letters, offer the tags already used in the notes, most used first.
import { syntaxTree } from "@codemirror/language";

function blocked(state, pos) {
  for (let n = syntaxTree(state).resolveInner(pos, -1); n; n = n.parent) {
    if (["FencedCode", "CodeBlock", "InlineCode", "URL", "Link", "Image", "WikiLink", "Embed"].includes(n.name)) return true;
  }
  return false;
}

export const TAG_BEFORE = /(^|\s)#([\p{L}\p{N}_/-]+)$/u;

export function rankTags(list, query) {
  const q = query.toLowerCase();
  const rows = (list || []).map((r) => (Array.isArray(r) ? r : [r, 0]))
    .map(([name, count]) => [String(name).replace(/^#/, ""), count || 0]).filter(([n]) => n);
  const starts = [], inside = [];
  for (const row of rows) {
    const n = row[0].toLowerCase();
    if (n === q) continue;                      // already typed in full
    (n.startsWith(q) ? starts : n.includes(q) ? inside : []).push(row);
  }
  const byCount = (a, b) => b[1] - a[1] || a[0].localeCompare(b[0]);
  return [...starts.sort(byCount), ...inside.sort(byCount)];
}

export default function tags(opts) {
  const source = (context) => {
    const line = context.state.doc.lineAt(context.pos);
    const m = TAG_BEFORE.exec(context.state.sliceDoc(line.from, context.pos));
    if (!m) return null;
    if (/^\d+$/.test(m[2])) return null;        // "#12" is not a tag
    const from = context.pos - m[2].length;
    if (blocked(context.state, from)) return null;
    let all = [];
    try { all = opts?.tagNames ? opts.tagNames() : []; } catch { all = []; }
    const found = rankTags(all, m[2]);
    if (!found.length) return null;
    return {
      from,
      filter: false,
      options: found.slice(0, 30).map(([name, count], i) => ({
        label: name, detail: count ? String(count) : "", boost: -i, type: "keyword",
      })),
    };
  };
  return { extensions: [], completions: [source] };
}
