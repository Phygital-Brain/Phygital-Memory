// Linking your other Mac (server: linking.py). This Mac shows a one-time link; the other Mac pastes it. Both show the
// same four safety words; the person checks them, picks memories and presses Link here, signed with their approval key.
import { el } from "./dom.js";
import { modal } from "./dialogs.js";

// This Mac. ctx: {start(), status(), answer(ids), cancel()}. Resolves {name, memories} once linked, or null.
export function linkMacDialog(ctx) {
  return modal((done) => {
    let timer = null, busy = false;
    const stop = (v) => { clearInterval(timer); if (!v) ctx.cancel(); done(v); };
    const body = el("div", {}, el("div", { class: "mf-hint" }, "Making a link."));
    const err = el("div", { class: "dlg-err" });
    const go = el("button", { class: "btn primary hidden", type: "button" }, "Link");
    const card = el("div", { class: "dlg", role: "dialog" }, el("div", { class: "dlg-title" }, "Link your other Mac"), body, err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", type: "button", onclick: () => stop(null) }, "Cancel"), go));
    const asking = (s) => {
      const boxes = s.memories.map((m) => el("input", { type: "checkbox", checked: true, value: m.id, "aria-label": m.name }));
      body.replaceChildren(
        el("div", { class: "mf-hint" }, `"${s.name}" asks to be linked. Its safety words must match these:`),
        el("div", { class: "link-words" }, s.words),
        el("div", { class: "mf-hint" }, s.memories.length ? "Memories it gets (still locked with the same password):" : "No memories on this Mac to send yet."),
        ...s.memories.map((m, i) => el("label", { class: "link-mem" }, boxes[i], " ", m.name)),
        el("div", { class: "mf-hint" }, "It becomes you: it can open what's shared with you and approve with its own key. Things you share keep running from this Mac."));
      go.classList.remove("hidden");
      go.onclick = async () => {
        if (busy) return;
        busy = true; go.disabled = true; err.textContent = "";
        try { const r = await ctx.answer(boxes.filter((b) => b.checked).map((b) => b.value), s.seen); stop(r); }
        catch (e) { err.textContent = e.message; busy = false; go.disabled = false; }
      };
    };
    ctx.start().then((s) => {
      const link = el("textarea", { class: "dlg-input rk-input link-box", rows: "4", readonly: true, spellcheck: "false", "aria-label": "Link" }, s.link);
      const copy = el("button", { class: "btn small", type: "button", onclick: () => navigator.clipboard.writeText(s.link).then(() => { copy.textContent = "Copied"; }) }, "Copy");
      body.replaceChildren(el("div", { class: "mf-hint" }, `On your other Mac, open Phygital Memory, then Open memory › From my other Mac, and paste this. It works for ${s.minutes} minutes, once.`),
        link, copy, el("div", { class: "mf-hint" }, "Waiting for your other Mac. Keep this window open."));
      let seen = false;
      timer = setInterval(async () => {
        if (seen) return;
        let st;
        try { st = await ctx.status(); } catch { return; }
        if (st.state === "expired") { clearInterval(timer); body.replaceChildren(el("div", { class: "mf-hint" }, "This link ran out. Close and start again.")); }
        if (st.state === "asking") { seen = true; asking(st); }
      }, 2000);
    }, (e) => { err.textContent = e.message; });
    return { card };
  });
}

// The other Mac. ctx: {join(link), wait()}. Resolves {from, memories} once linked, or null.
export function joinMacDialog(ctx) {
  return modal((done) => {
    let timer = null;
    const stop = (v) => { clearInterval(timer); done(v); };
    const link = el("textarea", { class: "dlg-input rk-input link-box", rows: "3", spellcheck: "false", placeholder: "Paste the link from your other Mac", "aria-label": "Link" });
    const err = el("div", { class: "dlg-err" });
    const body = el("div", {}, el("div", { class: "mf-hint" }, "On your other Mac: Settings › Link a Mac. Paste the link it shows."), link);
    const go = el("button", { class: "btn primary", type: "button" }, "Next");
    const card = el("div", { class: "dlg", role: "dialog" }, el("div", { class: "dlg-title" }, "Link to your other Mac"), body, err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", type: "button", onclick: () => stop(null) }, "Cancel"), go));
    const submit = async () => {
      if (go.disabled) return;
      go.disabled = true; err.textContent = "";
      let w;
      try { w = await ctx.join(link.value.trim()); }
      catch (e) { err.textContent = e.message; go.disabled = false; return; }
      go.classList.add("hidden");
      body.replaceChildren(el("div", { class: "mf-hint" }, "Check your other Mac shows these same safety words, then press Link there:"),
        el("div", { class: "link-words" }, w.words), el("div", { class: "mf-hint" }, "Keep this window open."));
      let polling = false;
      timer = setInterval(async () => {
        if (polling) return;
        polling = true;
        let s;
        try { s = await ctx.wait(); } catch (e) { err.textContent = e.message; return; } finally { polling = false; }
        if (s.state === "done") stop(s);
        if (s.state === "none") { clearInterval(timer); err.textContent = "The link stopped. Start again on your other Mac."; }
      }, 2000);
    };
    go.onclick = submit;
    return { card, focus: link };
  });
}
