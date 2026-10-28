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
const initials = (n) => (n || "?").trim().split(/\s+/).slice(0, 2).map((w) => w[0]).join("").toUpperCase();

// The Share window, in the order people need it: how sharing travels (both computers on at once), anyone waiting
// to be let in, who has it now (and what they can do), then inviting someone. Shared parts and the history follow,
// the history folded away.
export function openShare(ctx) {
  return modal((done) => {
    const body = el("div", { class: "sh-body" });
    const err = el("div", { class: "dlg-err", role: "alert" });
    const card = el("div", { class: "dlg sh", role: "dialog", "aria-label": t("Share \"{0}\"", ctx.name) },
      el("div", { class: "sh-head" },
        el("span", { class: "sh-mark" }, icon("share", 18)),
        el("div", { class: "sh-titles" }, el("div", { class: "dlg-title" }, t("Share \"{0}\"", ctx.name)),
          el("div", { class: "sh-sub" }, ctx.part ? t("One folder or file of this memory") : t("The whole memory"))),
        el("button", { class: "icon-btn", type: "button", title: t("Close"), "aria-label": t("Close"), onclick: () => done(null) }, icon("x", 16))),
      body, err);
    const btn = (label, fn, cls = "") => el("button", { class: "btn small " + cls, type: "button", onclick: fn }, label);
    const act = async (fn) => { err.textContent = ""; try { await fn(); await draw(); } catch (e) { err.textContent = e.message; } };
    const seg = (value, onPick) => {   // Can edit / Can view
      const box = el("div", { class: "seg sh-seg", role: "radiogroup", "aria-label": t("What they can do") });
      const paint = (v) => box.replaceChildren(...[["edit", t("Can edit")], ["view", t("Can view")]].map(([k, label]) =>
        el("button", { class: "seg-b" + (v === k ? " on" : ""), type: "button", role: "radio", "aria-checked": String(v === k),
          onclick: () => { if (k !== v) { paint(k); onPick(k); } } }, label)));
      paint(value);
      return box;
    };
    const section = (title, ...kids) => el("section", { class: "sh-sec" }, el("h3", { class: "sh-h" }, title), ...kids);
    const person = (name, sub, right, me) => el("div", { class: "sh-row" },
      el("span", { class: "sh-av" + (me ? " me" : "") }, initials(name)),
      el("div", { class: "sh-who" }, el("div", { class: "sh-name" }, name, me ? el("span", { class: "sh-you" }, t("you")) : null),
        sub ? el("div", { class: "sh-meta" }, sub) : null),
      right || null);
    let made = null;   // the invite just made, shown until the window closes

    const draw = async () => {
      let s, people = [], hist = [];
      try { s = await ctx.load(); } catch (e) { err.textContent = e.message; return; }
      const owner = s.role === "owner";
      try { if (owner) people = (await ctx.people()).people || []; } catch {}
      try { hist = (await ctx.history()).history || []; } catch {}
      let pick = "edit";
      const addRole = {};
      body.replaceChildren(...[
        // How it travels: the one thing people get wrong, said first
        el("div", { class: "sh-how" },
          el("div", { class: "sh-how-line" }, icon("sync", 16),
            el("span", {}, el("b", {}, t("Both computers must be online at the same time.")), " ",
              t("Files go straight from one computer to the other while both apps are open. Changes made while one is off wait, and go across the next time both are on."))),
          el("div", { class: "sh-how-line" }, icon(ctx.plain ? "folder" : "lock", 16), el("span", {}, ctx.plain
            ? (ctx.part ? t("Only this goes to them. It travels locked, then shows on their Mac as a normal folder their AI can read. The rest of your memory stays with you.")
              : t("It travels locked, then shows on their Mac as a normal folder their AI can read."))
            : (ctx.part ? t("Only this goes to them, in its own locked copy with its own key. The rest of your memory stays with you.")
              : t("Everyone opens it with their own key. Your password is never shared."))))),
        // Waiting to be let in
        (s.requests || []).length ? section(t("Waiting for you"), ...s.requests.map((r) => el("div", { class: "sh-req" },
          person(r.name, [r.what ? `"${r.what}"` : "", ROLE[r.role], r.safety ? t("Safety code: {0}", r.safety) : ""].filter(Boolean).join(" · "),
            el("span", { class: "sh-btns" }, btn(t("Say no"), () => act(() => ctx.answer(r.id, false, r.share))),
              btn(t("Let in"), () => act(() => ctx.answer(r.id, true, r.share)), "primary")))))) : null,
        // Who has it
        section(t("People"), el("div", { class: "sh-list" }, ...s.members.map((m) => person(m.name,
          m.role === "owner" ? ROLE.owner : (owner ? null : ROLE[m.role]),
          owner && m.role !== "owner" ? el("span", { class: "sh-btns" }, seg(m.role, (k) => act(() => ctx.role(m.id, k))),
            el("button", { class: "icon-btn sh-x", type: "button", title: t("Remove"), "aria-label": `${t("Remove")} ${m.name}`,
              onclick: () => act(() => ctx.remove(m.id)) }, icon("x", 14))) : null,
          m.id === s.me))),
          s.members.length < 2 ? el("div", { class: "sh-empty" }, t("Only you, so far.")) : null),
        // People you already trust
        owner && people.length ? section(t("Add someone you already share with"),
          el("div", { class: "sh-list" }, ...people.map((p) => {
            addRole[p.id] = "edit";
            return person(p.name, null, el("span", { class: "sh-btns" }, seg("edit", (k) => { addRole[p.id] = k; }),
              btn(t("Add"), () => act(() => ctx.add(p.id, addRole[p.id])), "primary"),
              el("button", { class: "icon-btn sh-x", type: "button", title: t("Forget"), "aria-label": `${t("Forget")} ${p.name}`,
                onclick: () => act(() => ctx.forget(p.id, p.name)) }, icon("x", 14))));
          })),
          el("div", { class: "sh-note" }, t("No invite needed: you checked their code the first time. It shows up in their app by itself."))) : null,
        // Invite
        owner ? section(people.length ? t("Or invite someone new") : t("Invite someone"),
          el("div", { class: "sh-invite" },
            seg(pick, (k) => { pick = k; }),
            btn(made ? t("Make another invite") : t("Make invite"), () => act(async () => { made = await ctx.invite(pick); }), "primary")),
          made ? el("div", { class: "sh-link" }, icon("link", 15),
            el("code", {}, made.link),
            btn(t("Copy"), (e) => navigator.clipboard.writeText(made.link).then(() => { e.target.textContent = t("Copied"); }))) : null,
          made ? el("div", { class: "sh-note" }, made.place.startsWith("Syncthing")
            ? t("Send it to them. It works once, for 7 days. Nothing goes to them until you press Let in. Then the files go straight from this Mac to theirs while both apps are open.")
            : `Send it to them. It works once, for 7 days. They also need the files: share "${made.place}" with them there.`,
            info(t("The invite only proves who's asking. You let them in here, and only then does their app get their own key to this memory."))) : null)
          : el("div", { class: "sh-note" }, t("Only the owner can invite people or change who can edit.")),
        // Parts shared on their own
        (s.parts || []).length ? section(t("Shared folders and files"), el("div", { class: "sh-list" }, ...s.parts.map((p) =>
          el("div", { class: "sh-row" }, el("span", { class: "sh-av part" }, icon("folder", 14)),
            el("div", { class: "sh-who" }, el("div", { class: "sh-name" }, p.path),
              el("div", { class: "sh-meta" }, p.people.length ? t("With ") + p.people.join(", ") : t("Nobody has it right now"))),
            el("span", { class: "sh-btns" }, btn(t("Open"), () => { done(null); ctx.openPart(p.path); }),
              btn(t("Stop sharing"), () => act(() => ctx.stopPart(p.id, p.path)), "danger")))))) : null,
        // What happened, folded away
        hist.length ? el("details", { class: "sh-sec sh-hist" }, el("summary", { class: "sh-h" }, t("History"), el("span", { class: "sh-count" }, String(hist.length))),
          el("div", { class: "sh-list" }, ...hist.slice(0, 30).map((h) => el("div", { class: "sh-hrow" },
            el("span", {}, el("b", {}, h.who), ` ${h.what} ${h.path.replace(/\.md$/i, "")}`), el("time", {}, WHEN(h.t)))))) : null,
      ].filter(Boolean));
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
