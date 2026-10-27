// In-page dialogs (prompt() and confirm() don't work in the Mac app window).
import { el } from "./dom.js";

export function modal(build) {
  return new Promise((resolve) => {
    const prev = document.activeElement;
    const done = (v) => { back.remove(); document.removeEventListener("keydown", onKey, true); prev && prev.focus && prev.focus(); resolve(v); };
    const { card, focus, submit } = build(done);
    const back = el("div", { class: "overlay modal", onmousedown: (e) => { if (e.target === back) done(null); } }, card);
    const onKey = (e) => {
      if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); done(null); }
      else if (e.key === "Enter" && submit) { e.preventDefault(); e.stopPropagation(); submit(); }
    };
    document.addEventListener("keydown", onKey, true);
    document.body.append(back);
    focus && focus.focus();
    focus && focus.select && focus.select();
  });
}

export function askText(title, value, okLabel, validate) {
  return modal((done) => {
    const input = el("input", { class: "dlg-input", value, spellcheck: "false", "aria-label": title });
    const err = el("div", { class: "dlg-err" });
    const submit = () => {
      const bad = validate ? validate(input.value) : "";
      if (bad) { err.textContent = bad; return; }
      done(input.value);
    };
    const card = el("div", { class: "dlg", role: "dialog" }, el("div", { class: "dlg-title" }, title), input, err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", onclick: () => done(null) }, "Cancel"), el("button", { class: "btn primary", onclick: submit }, okLabel)));
    return { card, focus: input, submit };
  });
}

export function askPassword(title, okLabel) {
  return modal((done) => {
    const input = el("input", { class: "dlg-input", type: "password", autocomplete: "off", "aria-label": "Password", placeholder: "Password" });
    const submit = () => { if (input.value) done(input.value); };
    const card = el("div", { class: "dlg", role: "dialog" }, el("div", { class: "dlg-title" }, title), input,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", onclick: () => done(null) }, "Cancel"), el("button", { class: "btn primary", onclick: submit }, okLabel)));
    return { card, focus: input, submit };
  });
}

// A question with several answers: buttons [[key, label, cls]], the last one is the main one (Enter). Resolves the key, or null.
export function choiceDialog(message, detail, buttons) {
  return modal((done) => {
    const els = buttons.map(([k, label, cls]) => el("button", { class: "btn " + (cls || ""), onclick: () => done(k) }, label));
    const card = el("div", { class: "dlg", role: "dialog" }, el("div", { class: "dlg-title" }, message),
      detail ? el("div", { class: "mf-hint" }, detail) : null,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", onclick: () => done(null) }, "Cancel"), ...els));
    return { card, focus: els[els.length - 1], submit: () => done(buttons[buttons.length - 1][0]) };
  });
}

export function confirmDialog(message, okLabel, danger, detail) {
  return modal((done) => {
    const ok = el("button", { class: "btn " + (danger ? "danger" : "primary"), onclick: () => done(true) }, okLabel);
    const card = el("div", { class: "dlg", role: "dialog" }, el("div", { class: "dlg-title" }, message),
      detail ? el("div", { class: "mf-hint" }, detail) : null,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", onclick: () => done(null) }, "Cancel"), ok));
    return { card, focus: ok, submit: () => done(true) };
  }).then((v) => v === true);
}

export { toast, toastOk, toastErr } from "./toast.js";
