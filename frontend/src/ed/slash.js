// Slash menu: "/" at the start of a line (or after only spaces) opens a list of blocks to insert.
import { syntaxTree } from "@codemirror/language";
import "./quick.css";

// text = what to insert, caret = where the caret lands inside it (default: the end)
export const SLASH_ITEMS = [
  { label: "Heading 1", keys: "h1 heading title", text: "# " },
  { label: "Heading 2", keys: "h2 heading subtitle", text: "## " },
  { label: "Heading 3", keys: "h3 heading", text: "### " },
  { label: "Bullet list", keys: "bullet list ul unordered", text: "- " },
  { label: "Numbered list", keys: "numbered ordered list ol 1", text: "1. " },
  { label: "Task", keys: "task todo check checkbox checklist", text: "- [ ] " },
  { label: "Quote", keys: "quote blockquote cite", text: "> " },
  { label: "Callout", keys: "callout note admonition info", text: "> [!note] \n> ", caret: 10 },
  { label: "Code block", keys: "code fence snippet pre", text: "```\n\n```", caret: 4 },
  { label: "Table", keys: "table grid", text: "|  |  |  |\n| --- | --- | --- |\n|  |  |  |", caret: 2 },
  { label: "Divider", keys: "divider hr rule line separator", text: "---\n" },
];

export function matchSlash(items, query) {
  const q = query.toLowerCase();
  if (!q) return items;
  const hit = (it) => {
    const words = (it.label + " " + it.keys).toLowerCase().split(/\s+/);
    return words.some((w) => w.startsWith(q)) || it.label.toLowerCase().includes(q);
  };
  return items.filter(hit);
}

function inCode(state, pos) {
  for (let n = syntaxTree(state).resolveInner(pos, -1); n; n = n.parent) {
    if (n.name === "FencedCode" || n.name === "CodeBlock" || n.name === "InlineCode" || n.name === "CommentBlock") return true;
  }
  return false;
}

export default function slash() {
  const source = (context) => {
    const line = context.state.doc.lineAt(context.pos);
    const before = context.state.sliceDoc(line.from, context.pos);
    const m = /^(\s*)\/([A-Za-z0-9]*)$/.exec(before);
    if (!m) return null;
    const from = line.from + m[1].length;
    if (inCode(context.state, from)) return null;
    const found = matchSlash(SLASH_ITEMS, m[2]);
    if (!found.length) return null;
    return {
      from,
      filter: false,
      options: found.map((it, i) => ({
        label: it.label,
        boost: -i,
        apply: (view, _c, f, to) => {
          view.dispatch({
            changes: { from: f, to, insert: it.text },
            selection: { anchor: f + (it.caret ?? it.text.length) },
            userEvent: "input.complete",
          });
        },
      })),
    };
  };
  return { extensions: [], completions: [source] };
}
