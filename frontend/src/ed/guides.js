// Faint vertical lines for nested list items, drawn at the parent bullet's column. They paint on the existing
// indent spaces (an inset shadow), so no text moves.
import { RangeSetBuilder } from "@codemirror/state";
import { Decoration, ViewPlugin } from "@codemirror/view";
import { syntaxTree } from "@codemirror/language";
import "./quick.css";

const guide = Decoration.mark({ class: "cm-md-guide" });

export function guidePositions(state) {
  const doc = state.doc, found = new Set();
  syntaxTree(state).iterate({
    enter(node) {
      if (node.name !== "ListItem") return;
      const parents = [];
      for (let p = node.node.parent; p; p = p.parent) if (p.name === "ListItem") parents.push(p);
      if (!parents.length) return;
      const first = doc.lineAt(node.from).number, last = doc.lineAt(node.to).number;
      for (let n = first; n <= last; n++) {
        const line = doc.line(n);
        const lead = /^[ \t]*/.exec(line.text)[0].length;
        for (const p of parents) {
          const col = p.from - doc.lineAt(p.from).from;          // where the parent's bullet sits
          if (col < lead) found.add(line.from + col);
        }
      }
    },
  });
  return [...found].sort((a, b) => a - b);
}

function build(view) {
  const b = new RangeSetBuilder();
  for (const pos of guidePositions(view.state)) b.add(pos, pos + 1, guide);
  return b.finish();
}

export default function guides() {
  const plugin = ViewPlugin.fromClass(class {
    constructor(view) { this.decorations = build(view); }
    update(u) {
      if (u.docChanged || syntaxTree(u.startState) !== syntaxTree(u.state)) this.decorations = build(u.view);
    }
  }, { decorations: (v) => v.decorations });
  return { extensions: [plugin], completions: [] };
}
