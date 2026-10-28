// Keyboard shortcuts: Cmd+K link, Cmd+Alt+0..6 headings, Cmd+L task, Shift+Enter soft break, Tab / Shift+Tab list indent.
import { Prec, EditorSelection } from "@codemirror/state";
import { keymap } from "@codemirror/view";
import { syntaxTree, ensureSyntaxTree } from "@codemirror/language";

const URL_RE = /^(https?:\/\/|www\.|mailto:)\S+$/i;
const LIST_RE = /^(\s*)([-*+]|\d+[.)])(\s+)/;
const TASK_RE = /^(\s*)([-*+]|\d+[.)])(\s+)\[([ xX])\](\s|$)/;
const HEAD_RE = /^ {0,3}#{1,6}[ \t]+/;

const tree = (state) => ensureSyntaxTree(state, state.doc.length, 200) || syntaxTree(state);
function ancestor(state, pos, names) {
  for (let n = tree(state).resolveInner(pos, -1); n; n = n.parent) if (names.includes(n.name)) return n;
  return null;
}
const inCode = (state, pos) => !!ancestor(state, pos, ["FencedCode", "CodeBlock"]);

// Line numbers touched by the selection. A range ending at the very start of a line does not include that line.
function selectedLines(state) {
  const seen = new Set(), lines = [];
  for (const r of state.selection.ranges) {
    const a = state.doc.lineAt(r.from);
    let b = state.doc.lineAt(r.to);
    if (!r.empty && r.to === b.from && b.number > a.number) b = state.doc.line(b.number - 1);
    for (let i = a.number; i <= b.number; i++) if (!seen.has(i)) { seen.add(i); lines.push(state.doc.line(i)); }
  }
  return lines;
}

export function linkCommand(view) {
  const { state } = view;
  view.dispatch(state.changeByRange((r) => {
    let { from, to } = r;
    if (r.empty) {
      const w = state.wordAt(r.head);
      if (!w) return { changes: { from, insert: "[]()" }, range: EditorSelection.cursor(from + 1) };
      ({ from, to } = w);
    }
    const text = state.sliceDoc(from, to);
    if (URL_RE.test(text.trim())) {
      return { changes: { from, to, insert: `[](${text})` }, range: EditorSelection.cursor(from + 1) };
    }
    return { changes: { from, to, insert: `[${text}]()` }, range: EditorSelection.cursor(from + text.length + 3) };
  }), { userEvent: "input", scrollIntoView: true });
  return true;
}

export const headingCommand = (level) => (view) => {
  const { state } = view;
  if (inCode(state, state.selection.main.head)) return false;
  const changes = [];
  for (const line of selectedLines(state)) {
    const m = HEAD_RE.exec(line.text);
    const strip = m ? m[0].length : 0;
    const prefix = level ? "#".repeat(level) + " " : "";
    if (m && m[0].trim() === prefix.trim() && level) continue;   // already this level
    changes.push({ from: line.from, to: line.from + strip, insert: prefix });
  }
  if (changes.length) view.dispatch({ changes, userEvent: "input" });
  return true;
};

export function taskCommand(view) {
  const { state } = view;
  if (inCode(state, state.selection.main.head)) return false;
  const changes = [];
  for (const line of selectedLines(state)) {
    let m = TASK_RE.exec(line.text);
    if (m) {
      const at = line.from + m[1].length + m[2].length + m[3].length + 1;
      changes.push({ from: at, to: at + 1, insert: m[4] === " " ? "x" : " " });
    } else if ((m = LIST_RE.exec(line.text))) {
      const at = line.from + m[0].length;
      changes.push({ from: at, insert: "[ ] " });
    } else {
      const at = line.from + /^\s*/.exec(line.text)[0].length;
      changes.push({ from: at, insert: "- [ ] " });
    }
  }
  if (changes.length) view.dispatch({ changes, userEvent: "input" });
  return true;
}

// Shift+Enter inside a list item: new line, lined up with the item text, no new bullet.
export function softBreak(view) {
  const { state } = view;
  const r = state.selection.main;
  if (inCode(state, r.head)) return false;
  const item = ancestor(state, r.head, ["ListItem"]);
  if (!item) return false;
  const first = state.doc.lineAt(item.from);
  const m = LIST_RE.exec(state.sliceDoc(item.from, first.to));   // the item starts at its bullet
  if (!m) return false;
  const width = item.from - first.from + m[0].length;
  view.dispatch({
    changes: { from: r.from, to: r.to, insert: "\n" + " ".repeat(width) },
    selection: { anchor: r.from + 1 + width }, userEvent: "input", scrollIntoView: true,
  });
  return true;
}

export function indentList(view) {
  const { state } = view;
  const lines = selectedLines(state);
  if (!lines.some((l) => LIST_RE.test(l.text)) || inCode(state, state.selection.main.head)) return false;
  view.dispatch({ changes: lines.filter((l) => LIST_RE.test(l.text)).map((l) => ({ from: l.from, insert: "  " })), userEvent: "input.indent" });
  return true;
}

export function outdentList(view) {
  const { state } = view;
  const lines = selectedLines(state);
  if (!lines.some((l) => LIST_RE.test(l.text)) || inCode(state, state.selection.main.head)) return false;
  const changes = [];
  for (const l of lines) {
    if (!LIST_RE.test(l.text)) continue;
    const m = /^(\t| {1,2})/.exec(l.text);
    if (m) changes.push({ from: l.from, to: l.from + m[0].length });
  }
  if (changes.length) view.dispatch({ changes, userEvent: "delete.dedent" });
  return true;
}

export default function shortcuts() {
  const keys = [
    { key: "Mod-k", run: linkCommand, preventDefault: true },
    { key: "Mod-l", run: taskCommand, preventDefault: true },
    { key: "Mod-Alt-0", run: headingCommand(0), preventDefault: true },
    { key: "Shift-Enter", run: softBreak },
    { key: "Tab", run: indentList },
    { key: "Shift-Tab", run: outdentList },
  ];
  for (let i = 1; i <= 6; i++) keys.push({ key: `Mod-Alt-${i}`, run: headingCommand(i), preventDefault: true });
  return { extensions: [Prec.high(keymap.of(keys))], completions: [] };
}
