// %%comments%% (inline, or a block fenced by lines that hold only %%): faint italic, marks hidden until the cursor is inside.
import { RangeSetBuilder } from "@codemirror/state";
import { Decoration, ViewPlugin } from "@codemirror/view";
import { syntaxTree } from "@codemirror/language";
import "./quick.css";

const hide = Decoration.replace({});
const faint = Decoration.mark({ class: "cm-md-comment" });
const faintLine = Decoration.line({ class: "cm-md-comment" });
export const INLINE_COMMENT = /%%(?!%)(.+?)%%/g;

// Finds comments in a text. Returns [{from, to, markEnds: [[a,b],[c,d]], line: bool}] with doc offsets.
export function findComments(state, code) {
  const doc = state.doc, out = [];
  let open = null;
  for (let i = 1; i <= doc.lines; i++) {
    const line = doc.line(i);
    if (code(line.from) && !open) continue;
    const text = line.text, trimmed = text.trim();
    if (trimmed === "%%") {
      const at = line.from + text.indexOf("%%");
      if (open) { out.push({ from: open.from, to: line.to, marks: [open.mark, [at, at + 2]], block: [open.line, i] }); open = null; }
      else open = { from: line.from, mark: [at, at + 2], line: i };
      continue;
    }
    if (open) continue;
    INLINE_COMMENT.lastIndex = 0;
    let m;
    while ((m = INLINE_COMMENT.exec(text))) {
      const from = line.from + m.index, to = from + m[0].length;
      if (code(from)) continue;
      out.push({ from, to, marks: [[from, from + 2], [to - 2, to]] });
    }
  }
  return out;
}

function build(view) {
  const state = view.state;
  const tree = syntaxTree(state);
  const code = (pos) => {
    for (let n = tree.resolveInner(pos, 1); n; n = n.parent) {
      if (n.name === "FencedCode" || n.name === "CodeBlock" || n.name === "InlineCode") return true;
    }
    return false;
  };
  const focus = view.hasFocus;
  const cursors = focus ? state.selection.ranges.filter((r) => r.empty) : [];
  const items = [];
  for (const c of findComments(state, code)) {
    const active = cursors.some((r) => r.from >= c.from && r.to <= c.to);
    if (c.block) {
      for (let i = c.block[0]; i <= c.block[1]; i++) items.push([state.doc.line(i).from, state.doc.line(i).from, faintLine, -1]);
    } else items.push([c.from, c.to, faint, 0]);
    if (!active) for (const [a, b] of c.marks) items.push([a, b, hide, 1]);
  }
  items.sort((x, y) => x[0] - y[0] || x[3] - y[3] || x[1] - y[1]);
  const b = new RangeSetBuilder();
  for (const [from, to, deco] of items) b.add(from, to, deco);
  return b.finish();
}

export default function comments() {
  const plugin = ViewPlugin.fromClass(class {
    constructor(view) { this.decorations = build(view); }
    update(u) {
      if (u.docChanged || u.selectionSet || u.focusChanged || syntaxTree(u.startState) !== syntaxTree(u.state)) {
        this.decorations = build(u.view);
      }
    }
  }, { decorations: (v) => v.decorations });
  return { extensions: [plugin], completions: [] };
}
