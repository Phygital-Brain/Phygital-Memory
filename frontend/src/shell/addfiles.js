// "Add to your memory": the one window for files coming in, whether they were dropped, or picked through Import.
// ctx: {folders: [paths], dir, what: string|null (a drop), pick(folder) -> {label} | null}
// Resolves {how: "add" | "ai", dir} or null.
import { t } from "./i18n.js";
import { el } from "./dom.js";
import { modal } from "./dialogs.js";
import { info } from "./panels.js";

export function openAddFiles(ctx) {
  return modal((done) => {
    const what = el("div", { class: "af-what" }, ctx.what || t("Nothing chosen yet"));
    const err = el("div", { class: "dlg-err" });
    const where = el("select", { class: "af-where", "aria-label": t("Where") },
      el("option", { value: "" }, t("Top of the memory")), ...ctx.folders.map((p) => el("option", { value: p }, p)));
    where.value = ctx.dir || "";
    let ready = !!ctx.what;
    const choose = async (folder) => {
      err.textContent = "";
      try {
        const got = await ctx.pick(folder);
        if (got) { what.textContent = got.label; ready = true; sync(); }
      } catch (e) { err.textContent = e.message; }
    };
    const ai = el("button", { class: "btn", type: "button", onclick: () => ready && done({ how: "ai", dir: where.value }) }, t("Let AI sort them"));
    const add = el("button", { class: "btn primary", type: "button", onclick: () => ready && done({ how: "add", dir: where.value }) }, t("Add"));
    const sync = () => { ai.disabled = add.disabled = !ready; };
    sync();
    const card = el("div", { class: "dlg add-files", role: "dialog" },
      el("div", { class: "dlg-title" }, t("Add to your memory")),
      el("div", { class: "af-row" }, el("div", { class: "af-label" }, t("What")), what),
      ctx.what ? null : el("div", { class: "set-btns" },
        el("button", { class: "btn small", type: "button", onclick: () => choose(false) }, t("Choose files")),
        el("button", { class: "btn small", type: "button", onclick: () => choose(true) }, t("Choose a folder"))),
      el("div", { class: "af-row" }, el("div", { class: "af-label" }, t("Where")), where),
      el("div", { class: "mf-hint" }, t("Encrypted as they come in. The originals stay where they are."),
        info(t("Let AI sort them puts everything in an Inbox folder and gives your AI one task: file each one where it belongs."))),
      err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", type: "button", onclick: () => done(null) }, t("Cancel")), ai, add));
    if (ctx.start != null) setTimeout(() => choose(ctx.start), 50);   // Import files / Import folder: the chooser opens at once
    return { card, focus: add, submit: () => ready && done({ how: "add", dir: where.value }) };
  });
}
