// The "closing the app" question. It can't be waved away: the window is already on its way out, so the person
// picks: lock everything and quit, or keep the notes open with the app in the Dock. With no answer in 30 seconds
// everything locks. Resolves with 1 (keep) or 0 (lock).
import { el } from "./dom.js";

const WAIT = 30;

export function askClose() {
  return new Promise((resolve) => {
    let left = WAIT;
    const done = (keep) => { clearInterval(tick); back.remove(); resolve(keep); };
    const lock = el("button", { class: "btn primary", onclick: () => done(0) }, "Lock all and close");
    const count = el("div", { class: "close-count" });
    const show = () => { count.textContent = `No answer? Everything locks in ${left} s.`; };
    const card = el("div", { class: "dlg close-dlg", role: "alertdialog", "aria-modal": "true", "aria-label": "Close Phygital Memory" },
      el("div", { class: "dlg-title" }, "Lock your notes before closing?"),
      el("div", { class: "dlg-sub" }, "Lock all: everything locks and the app quits. Keep open: your AI apps can still reach your notes, and the app stays in the Dock until you lock or quit it. Keep open is remembered for 3 days."),
      el("div", { class: "close-actions" }, lock, el("button", { class: "btn", onclick: () => done(1) }, "Keep open")),
      count);
    const back = el("div", { class: "overlay modal close-overlay" }, card);
    const tick = setInterval(() => { left -= 1; if (left <= 0) done(0); else show(); }, 1000);
    show();
    document.body.append(back);
    lock.focus();
  });
}
