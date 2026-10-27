// The "closing the app" question. It can't be waved away: the window is already on its way out, so the person
// picks: lock everything and quit, or keep the notes open with the app in the Dock. Resolves with 1 (keep) or 0.
import { el } from "./dom.js";

export function askClose() {
  return new Promise((resolve) => {
    const done = (keep) => { back.remove(); resolve(keep); };
    const lock = el("button", { class: "btn primary", onclick: () => done(0) }, "Lock all and close");
    const card = el("div", { class: "dlg close-dlg", role: "alertdialog", "aria-modal": "true", "aria-label": "Close Phygital Memory" },
      el("div", { class: "dlg-title" }, "Lock your notes before closing?"),
      el("div", { class: "dlg-sub" }, "Lock all: everything locks and the app quits. Keep open: your AI apps can still reach your notes, and the app stays in the Dock until you lock or quit it."),
      el("div", { class: "close-actions" }, lock, el("button", { class: "btn", onclick: () => done(1) }, "Keep open")));
    const back = el("div", { class: "overlay modal close-overlay" }, card);
    document.body.append(back);
    lock.focus();
  });
}
