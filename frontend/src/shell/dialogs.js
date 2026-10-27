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
export function choiceDialog(message, detail, buttons, cancel = "Cancel") {
  return modal((done) => {
    const els = buttons.map(([k, label, cls]) => el("button", { class: "btn " + (cls || ""), onclick: () => done(k) }, label));
    const card = el("div", { class: "dlg", role: "dialog" }, el("div", { class: "dlg-title" }, message),
      detail ? el("div", { class: "mf-hint" }, detail) : null,
      el("div", { class: "dlg-actions" }, cancel ? el("button", { class: "btn", onclick: () => done(null) }, cancel) : null, ...els));
    return { card, focus: els[els.length - 1], submit: () => done(buttons[buttons.length - 1][0]) };
  });
}

// The recovery key: 44 words, shown once on request, with a Copy button.
export function showRecoveryKey(words) {
  return modal((done) => {
    const list = el("ol", { class: "rk-words" }, ...words.split(" ").map((w) => el("li", {}, w)));
    const copy = el("button", { class: "btn", type: "button", onclick: () => navigator.clipboard.writeText(words).then(() => { copy.textContent = "Copied"; }) }, "Copy");
    const card = el("div", { class: "dlg rk", role: "dialog" }, el("div", { class: "dlg-title" }, "Your recovery key"),
      el("div", { class: "mf-hint" }, "These 44 words open this memory if you forget the password. Keep them somewhere safe and private. Anyone with them can open it."),
      list, el("div", { class: "dlg-actions" }, copy, el("button", { class: "btn primary", type: "button", onclick: () => done(true) }, "Done")));
    return { card };
  });
}

// The open-source licences of the programs the app includes, as their authors wrote them.
export function showLicenses(text) {
  return modal((done) => {
    const ok = el("button", { class: "btn primary", type: "button", onclick: () => done(true) }, "Done");
    const card = el("div", { class: "dlg", role: "dialog" }, el("div", { class: "dlg-title" }, "Open-source licences"),
      el("pre", { class: "lic-text" }, text), el("div", { class: "dlg-actions" }, ok));
    return { card, focus: ok };
  });
}

// Forgot the password: the recovery key, and a new password twice. Resolves {words, password, again} or null.
export function recoveryDialog() {
  return modal((done) => {
    const words = el("textarea", { class: "dlg-input rk-input", rows: "4", spellcheck: "false", placeholder: "The 44 words, in order", "aria-label": "Recovery key" });
    const pw = el("input", { class: "dlg-input", type: "password", autocomplete: "new-password", placeholder: "New password (8 or more characters)", "aria-label": "New password" });
    const again = el("input", { class: "dlg-input", type: "password", autocomplete: "new-password", placeholder: "New password again", "aria-label": "New password again" });
    const err = el("div", { class: "dlg-err" });
    const submit = () => {
      if (words.value.trim().split(/\s+/).length !== 44) { err.textContent = "A recovery key has 44 words."; return; }
      if (pw.value.length < 8) { err.textContent = "Use at least 8 characters."; return; }
      if (pw.value !== again.value) { err.textContent = "The two passwords don't match."; return; }
      done({ words: words.value.trim(), password: pw.value, again: again.value });
    };
    const card = el("div", { class: "dlg", role: "dialog" }, el("div", { class: "dlg-title" }, "Use your recovery key"),
      el("div", { class: "mf-hint" }, "Type the 44 words, then choose a new password."), words, pw, again, err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", type: "button", onclick: () => done(null) }, "Cancel"),
        el("button", { class: "btn primary", type: "button", onclick: submit }, "Set new password")));
    return { card, focus: words };
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
