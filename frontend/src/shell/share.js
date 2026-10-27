// Working together: the Share window (members, invites, who's asking), and pasting an invite to join.
import { el, icon } from "./dom.js";
import { modal } from "./dialogs.js";
import { info } from "./panels.js";

const ROLE = { owner: "Owner", edit: "Can edit", view: "Can view" };

// ctx: {name, load() -> shareinfo, invite(role) -> {link, place}, answer(id, allow), role(id, role), remove(id), storage()}
export function openShare(ctx) {
  return modal((done) => {
    const body = el("div", { class: "cl-body" });
    const err = el("div", { class: "dlg-err" });
    const card = el("div", { class: "dlg storage share", role: "dialog" },
      el("div", { class: "dlg-title" }, `Share "${ctx.name}"`), body, err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", type: "button", onclick: () => done(null) }, "Close")));
    const btn = (label, fn, cls = "") => el("button", { class: "btn small " + cls, type: "button", onclick: fn }, label);
    const act = async (fn) => { err.textContent = ""; try { await fn(); await draw(); } catch (e) { err.textContent = e.message; } };
    let made = null;   // the invite just made, shown until the window closes

    const draw = async () => {
      let s;
      try { s = await ctx.load(); } catch (e) { err.textContent = e.message; return; }
      const macOnly = s.place.startsWith("This Mac");
      const owner = s.role === "owner";
      const role = el("div", { class: "seg", role: "radiogroup" });
      let pick = "edit";
      const drawRole = () => role.replaceChildren(...[["edit", "Can edit"], ["view", "Can view"]].map(([k, t]) =>
        el("button", { class: "seg-b" + (pick === k ? " on" : ""), type: "button", onclick: () => { pick = k; drawRole(); } }, t)));
      drawRole();
      body.replaceChildren(
        el("div", { class: "st-e2e" }, icon("lock", 14), el("span", {}, "Everyone opens it with their own key. Your password is never shared.")),
        macOnly ? el("div", { class: "st-warn" }, el("span", {}, "These files are only on this Mac. Share the folder with Syncthing or a shared drive, or move it to a cloud, so others can reach it."),
          btn("Storage and backup", () => { done(null); ctx.storage(); })) : null,
        ...(s.requests || []).map((r) => el("div", { class: "share-req" },
          el("span", {}, el("b", {}, r.name), ` wants to join · ${ROLE[r.role]}`),
          el("span", { class: "set-btns" }, btn("Say no", () => act(() => ctx.answer(r.id, false))), btn("Let in", () => act(() => ctx.answer(r.id, true)), "primary")))),
        el("div", { class: "set-section" }, "People"),
        el("div", { class: "act-list" }, ...(s.members.length ? s.members.map((m) => el("div", { class: "todo-row share-row" },
          el("div", { class: "act-main" }, el("div", { class: "act-line" }, m.name + (m.id === s.me ? " (you)" : "")),
            el("div", { class: "act-folder" }, ROLE[m.role])),
          owner && m.role !== "owner" ? el("span", { class: "set-btns" },
            btn(m.role === "edit" ? "Make view only" : "Let edit", () => act(() => ctx.role(m.id, m.role === "edit" ? "view" : "edit"))),
            btn("Remove", () => act(() => ctx.remove(m.id)), "danger")) : null))
          : [el("div", { class: "act-empty" }, "Only you, so far.")])),
        ...(owner ? [
          el("div", { class: "set-section" }, "Invite someone"),
          el("div", { class: "af-row" }, role, btn("Make invite", () => act(async () => { made = await ctx.invite(pick); }), "primary")),
          made ? el("div", { class: "share-invite" },
            el("code", {}, made.link),
            el("div", { class: "set-btns" }, btn("Copy", (e) => navigator.clipboard.writeText(made.link).then(() => { e.target.textContent = "Copied"; })))) : null,
          made ? el("div", { class: "mf-hint" }, `Send it to them. It works once, for 7 days. They also need the files: share "${made.place}" with them there.`,
            info("The invite only proves who's asking. You let them in here, and only then does their app get their own key to this memory.")) : null] : [
          el("div", { class: "mf-hint" }, "Only the owner can invite people or change who can edit.")]));
    };
    draw();
    return { card };
  });
}

// Joining: paste the invite, then say where the shared files are on this Mac. Resolves {link, where} or null.
export function joinDialog() {
  return modal((done) => {
    const link = el("textarea", { class: "dlg-input rk-input", rows: "3", spellcheck: "false", placeholder: "phygitalmemory://join?…", "aria-label": "Invite" });
    const err = el("div", { class: "dlg-err" });
    const where = el("div", { class: "mf-hint" });
    const read = () => {
      const t = link.value.trim();
      if (!t.startsWith("phygitalmemory://join?")) { err.textContent = "Paste the whole invite, starting with phygitalmemory://"; return null; }
      return t;
    };
    link.addEventListener("input", () => {
      err.textContent = "";
      try { const w = new URL(link.value.trim()).searchParams.get("w"); where.textContent = w ? `The files are in: ${w}. Make sure it's shared with you there.` : ""; } catch { where.textContent = ""; }
    });
    const go = (kind) => { const t = read(); if (t) done({ link: t, where: kind }); };
    const card = el("div", { class: "dlg", role: "dialog" }, el("div", { class: "dlg-title" }, "Join a shared memory"),
      el("div", { class: "mf-hint" }, "Paste the invite you were sent."), link, where, err,
      el("div", { class: "mf-hint" }, "Where are the shared files on your side?"),
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", type: "button", onclick: () => done(null) }, "Cancel"),
        el("button", { class: "btn", type: "button", onclick: () => go("webdav") }, "On WebDAV"),
        el("button", { class: "btn primary", type: "button", onclick: () => go("mac") }, "A folder on this Mac")));
    return { card, focus: link };
  });
}
