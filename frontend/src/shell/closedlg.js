// The "closing the app" question. It can't be waved away: the window is already on its way out, so the person
// picks how long the notes may stay open in Finder. Resolves with the number of minutes (0 = lock now).
import { el } from "./dom.js";

export function askClose() {
  return new Promise((resolve) => {
    const done = (min) => { back.remove(); resolve(min); };
    const keep = (label, min) => el("button", { class: "btn", onclick: () => done(min) }, label);
    const now = el("button", { class: "btn primary", onclick: () => done(0) }, "Close and lock now");
    const card = el("div", { class: "dlg close-dlg", role: "alertdialog", "aria-modal": "true", "aria-label": "Close Phygital Memory" },
      el("div", { class: "dlg-title" }, "Keep your notes open in Finder after closing?"),
      el("div", { class: "dlg-sub" }, "While they stay open, any app on this Mac can read them. After the time you pick, everything locks and the app quits."),
      el("div", { class: "close-actions" }, now, el("div", { class: "close-keep" }, keep("Keep open 15 min", 15), keep("1 hour", 60), keep("4 hours", 240))));
    const back = el("div", { class: "overlay modal close-overlay" }, card);
    document.body.append(back);
    now.focus();
  });
}
