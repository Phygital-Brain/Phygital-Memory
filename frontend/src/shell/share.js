// Working together: the Share window (members, invites, who's asking), and pasting an invite to join.
import { t } from "./i18n.js";
import { el, icon } from "./dom.js";
import { modal } from "./dialogs.js";
import { info } from "./panels.js";

const ROLE = { owner: "Owner", edit: t("Can edit"), view: t("Can view") };

// ctx: {name, part (one folder or file, not the whole memory), load() -> shareinfo, invite(role) -> {link, place},
//       answer(id, allow), role(id, role), remove(id), openPart(path), stopPart(share, path), people() -> {people},
//       add(id, role), forget(id, name), history() -> {history}, storage()}
const WHEN = (t) => new Date(t * 1000).toLocaleString([], { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
export function openShare(ctx) {
  return modal((done) => {
    const body = el("div", { class: "cl-body" });
    const err = el("div", { class: "dlg-err" });
    const card = el("div", { class: "dlg storage share", role: "dialog" },
      el("div", { class: "dlg-title" }, t("Share \"{0}\"", ctx.name)), body, err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", type: "button", onclick: () => done(null) }, t("Close"))));
    const btn = (label, fn, cls = "") => el("button", { class: "btn small " + cls, type: "button", onclick: fn }, label);
    const act = async (fn) => { err.textContent = ""; try { await fn(); await draw(); } catch (e) { err.textContent = e.message; } };
    let made = null;   // the invite just made, shown until the window closes

    const draw = async () => {
      let s, people = [], hist = [];
      try { s = await ctx.load(); } catch (e) { err.textContent = e.message; return; }
      const owner = s.role === "owner";
      try { if (owner) people = (await ctx.people()).people || []; } catch {}
      try { hist = (await ctx.history()).history || []; } catch {}
      const addRole = {};
      const role = el("div", { class: "seg", role: "radiogroup" });
      let pick = "edit";
      const drawRole = () => role.replaceChildren(...[["edit", t("Can edit")], ["view", t("Can view")]].map(([k, t]) =>
        el("button", { class: "seg-b" + (pick === k ? " on" : ""), type: "button", onclick: () => { pick = k; drawRole(); } }, t)));
      drawRole();
      body.replaceChildren(...[
        el("div", { class: "st-e2e" }, icon("lock", 14), el("span", {}, ctx.part
          ? t("Only this goes to them, in its own locked copy with its own key. The rest of your memory stays with you.")
          : t("Everyone opens it with their own key. Your password is never shared."))),
        ...(s.requests || []).map((r) => el("div", { class: "share-req" },
          el("span", {}, el("b", {}, r.name), ` wants to join${r.what ? ` "${r.what}"` : ""} · ${ROLE[r.role]}`,
            r.safety ? el("div", { class: "act-folder" }, t("Safety code: {0}", r.safety)) : null),
          el("span", { class: "set-btns" }, btn(t("Say no"), () => act(() => ctx.answer(r.id, false, r.share))), btn(t("Let in"), () => act(() => ctx.answer(r.id, true, r.share)), "primary")))),
        el("div", { class: "set-section" }, t("People")),
        el("div", { class: "act-list" }, ...(s.members.length ? s.members.map((m) => el("div", { class: "todo-row share-row" },
          el("div", { class: "act-main" }, el("div", { class: "act-line" }, m.name + (m.id === s.me ? " (you)" : "")),
            el("div", { class: "act-folder" }, ROLE[m.role])),
          owner && m.role !== "owner" ? el("span", { class: "set-btns" },
            btn(m.role === "edit" ? "Make view only" : t("Let edit"), () => act(() => ctx.role(m.id, m.role === "edit" ? "view" : "edit"))),
            btn(t("Remove"), () => act(() => ctx.remove(m.id)), "danger")) : null))
          : [el("div", { class: "act-empty" }, t("Only you, so far."))])),
        ...((s.parts || []).length ? [el("div", { class: "set-section" }, t("Shared folders and files")),
          el("div", { class: "act-list" }, ...s.parts.map((p) => el("div", { class: "todo-row share-row" },
            el("div", { class: "act-main" }, el("div", { class: "act-line" }, p.path),
              el("div", { class: "act-folder" }, p.people.length ? t("With ") + p.people.join(", ") : t("Nobody has it right now"))),
            el("span", { class: "set-btns" }, btn(t("Open"), () => { done(null); ctx.openPart(p.path); }),
              btn(t("Stop sharing"), () => act(() => ctx.stopPart(p.id, p.path)), "danger")))))] : []),
        ...(owner && people.length ? [el("div", { class: "set-section" }, t("Add someone you already share with")),
          el("div", { class: "act-list" }, ...people.map((p) => {
            addRole[p.id] = "edit";
            const seg = el("div", { class: "seg", role: "radiogroup" });
            const drawSeg = () => seg.replaceChildren(...[["edit", t("Can edit")], ["view", t("Can view")]].map(([k, t]) =>
              el("button", { class: "seg-b" + (addRole[p.id] === k ? " on" : ""), type: "button", onclick: () => { addRole[p.id] = k; drawSeg(); } }, t)));
            drawSeg();
            return el("div", { class: "todo-row share-row" }, el("div", { class: "act-main" }, el("div", { class: "act-line" }, p.name)),
              el("span", { class: "set-btns" }, seg, btn(t("Add"), () => act(() => ctx.add(p.id, addRole[p.id])), "primary"),
                btn(t("Forget"), () => act(() => ctx.forget(p.id, p.name)))));
          })),
          el("div", { class: "mf-hint" }, t("No invite needed: you checked their code the first time. It shows up in their app by itself."))] : []),
        ...(owner ? [
          el("div", { class: "set-section" }, people.length ? "Or invite someone new" : t("Invite someone")),
          el("div", { class: "af-row" }, role, btn(t("Make invite"), () => act(async () => { made = await ctx.invite(pick); }), "primary")),
          made ? el("div", { class: "share-invite" },
            el("code", {}, made.link),
            el("div", { class: "set-btns" }, btn(t("Copy"), (e) => navigator.clipboard.writeText(made.link).then(() => { e.target.textContent = t("Copied"); })))) : null,
          made ? el("div", { class: "mf-hint" }, made.place.startsWith(t("Syncthing"))
            ? t("Send it to them. It works once, for 7 days. Nothing goes to them until you press Let in. Then the files go straight from this Mac to theirs while both apps are open.")
            : `Send it to them. It works once, for 7 days. They also need the files: share "${made.place}" with them there.`,
            info(t("The invite only proves who's asking. You let them in here, and only then does their app get their own key to this memory."))) : null] : [
          el("div", { class: "mf-hint" }, t("Only the owner can invite people or change who can edit."))]),
        ...(hist.length ? [el("div", { class: "set-section" }, t("History")),
          el("div", { class: "act-list share-hist" }, ...hist.slice(0, 30).map((h) => el("div", { class: "todo-row share-row" },
            el("div", { class: "act-main" }, el("div", { class: "act-line" }, el("b", {}, h.who), ` ${h.what} ${h.path.replace(/\.md$/i, "")}`),
              el("div", { class: "act-folder" }, WHEN(h.t))))))] : [])].filter((x) => x != null));
    };
    draw();
    return { card };
  });
}

// Joining: paste the invite, then say where the shared files are on this Mac. Resolves {link, where} or null.
export function joinDialog() {
  return modal((done) => {
    const link = el("textarea", { class: "dlg-input rk-input", rows: "3", spellcheck: "false", placeholder: t("Paste the invite here"), "aria-label": t("Invite") });
    const err = el("div", { class: "dlg-err" });
    const where = el("div", { class: "mf-hint" });
    const read = () => {
      const t = link.value.trim();
      if (!t.startsWith("phygitalmemory://join?")) { err.textContent = t("Paste the whole invite, starting with phygitalmemory://"); return null; }
      return t;
    };
    const ask = el("div", { class: "mf-hint" }, t("Where are the shared files on your side?"));
    const other = [el("button", { class: "btn", type: "button", onclick: () => go("webdav") }, t("On WebDAV")),
      el("button", { class: "btn primary", type: "button", onclick: () => go("mac") }, t("A folder on this Mac"))];
    const direct = el("button", { class: "btn primary hidden", type: "button", onclick: () => go("syncthing") }, t("Join"));
    link.addEventListener("input", () => {
      err.textContent = "";
      let q = null;
      try { q = new URL(link.value.trim()).searchParams; } catch {}
      const st = !!(q && q.get("d"));   // the owner shares straight from their Mac: no cloud to set up
      const w = q && q.get("w");
      const k = q && q.get("k");
      where.textContent = st ? `${k === "file" ? "A file" : k === "folder" ? "A folder" : t("A memory")} from their Mac. It comes once they let you in. No cloud or account needed.`
        : w ? `The files are in: ${w}. Make sure it's shared with you there.` : "";
      ask.classList.toggle("hidden", st);
      other.forEach((b) => b.classList.toggle("hidden", st));
      direct.classList.toggle("hidden", !st);
    });
    const go = (kind) => { const t = read(); if (t) done({ link: t, where: kind }); };
    const card = el("div", { class: "dlg", role: "dialog" }, el("div", { class: "dlg-title" }, t("Join something shared with you")),
      el("div", { class: "mf-hint" }, t("Paste the invite you were sent.")), link, where, err,
      ask,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", type: "button", onclick: () => done(null) }, t("Cancel")), ...other, direct));
    return { card, focus: link };
  });
}
