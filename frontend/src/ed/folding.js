// Editor feature: folding. A chevron next to a heading, a list item with children, a callout or a code block
// collapses it. Folds are remembered per note (by the line's text, so edits above don't break them), and a
// callout written `> [!note]-` starts folded, like Obsidian.
import { ViewPlugin, EditorView } from "@codemirror/view";
import { foldService, foldGutter, foldKeymap, foldEffect, unfoldEffect, foldedRanges, codeFolding } from "@codemirror/language";
import { keymap } from "@codemirror/view";

const LIST = /^(\s*)([-*+]|\d+[.)])\s/;

function rangeFor(state, lineStart) {
  const doc = state.doc, line = doc.lineAt(lineStart), text = line.text;
  const endAt = (lastLine) => (lastLine > line.number ? { from: line.to, to: doc.line(lastLine).to } : null);
  const trimBlank = (n) => { while (n > line.number && !doc.line(n).text.trim()) n--; return n; };

  const h = /^(#{1,6})\s/.exec(text);
  if (h) {
    let n = line.number;
    while (n < doc.lines) {
      const next = /^(#{1,6})\s/.exec(doc.line(n + 1).text);
      if (next && next[1].length <= h[1].length) break;
      n++;
    }
    return endAt(trimBlank(n));
  }
  const fence = /^\s*(```|~~~)/.exec(text);
  if (fence) {
    for (let n = line.number + 1; n <= doc.lines; n++) {
      if (doc.line(n).text.trim().startsWith(fence[1])) return endAt(n);
    }
    return null;
  }
  if (/^>\s*\[!/.test(text)) {
    let n = line.number;
    while (n < doc.lines && /^\s*>/.test(doc.line(n + 1).text)) n++;
    return endAt(n);
  }
  const li = LIST.exec(text);
  if (li) {
    const indent = li[1].length;
    let n = line.number, last = n;
    while (n < doc.lines) {
      const t = doc.line(n + 1).text;
      if (!t.trim()) { n++; continue; }
      if (t.length - t.trimStart().length <= indent) break;
      n++; last = n;
    }
    return endAt(last);
  }
  return null;
}

const chevron = (open) => {
  const s = document.createElement("span");
  s.className = "md-fold" + (open ? "" : " md-fold-closed");
  s.textContent = "›";
  s.title = open ? "Fold" : "Unfold";
  return s;
};

export default function folding(opts) {
  const save = (view) => {
    if (!opts.saveState) return;
    const lines = [];
    foldedRanges(view.state).between(0, view.state.doc.length, (from) => {
      lines.push(view.state.doc.lineAt(from).text);
    });
    opts.saveState("folds", lines);
  };

  // Restore saved folds (or `[!x]-` callouts) once the note has been drawn.
  const restore = ViewPlugin.fromClass(class {
    constructor(view) {
      requestAnimationFrame(() => {
        const saved = opts.loadState ? opts.loadState("folds") : null;
        const effects = [];
        for (let n = 1; n <= view.state.doc.lines; n++) {
          const line = view.state.doc.line(n);
          const want = Array.isArray(saved) ? saved.includes(line.text) : /^>\s*\[![\w-]+\]-/.test(line.text);
          if (!want) continue;
          const r = rangeFor(view.state, line.from);
          if (r) effects.push(foldEffect.of(r));
        }
        if (effects.length) view.dispatch({ effects });
      });
    }
  });

  return {
    extensions: [
      codeFolding({
        placeholderDOM(view, onclick) {
          const p = document.createElement("span"); p.className = "md-fold-placeholder"; p.textContent = "more";
          p.title = "Unfold"; p.onclick = onclick; return p;
        },
      }),
      foldService.of((state, from) => rangeFor(state, from)),
      foldGutter({ markerDOM: chevron }),
      EditorView.theme({
        ".cm-gutters": { backgroundColor: "transparent", border: "none", color: "var(--text-faint)" },
        ".cm-activeLineGutter": { backgroundColor: "transparent" },
      }),
      keymap.of(foldKeymap),
      restore,
      EditorView.updateListener.of((u) => {
        if (u.transactions.some((tr) => tr.effects.some((e) => e.is(foldEffect) || e.is(unfoldEffect)))) save(u.view);
      }),
    ],
    completions: [],
  };
}
