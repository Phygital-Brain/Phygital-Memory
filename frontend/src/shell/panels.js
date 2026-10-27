// Panels from the sidebar's status icons: where this folder is stored, the AI panel (tasks and activity), the trash.
// Everything from the server is put in as text only.
import { el, icon } from "./dom.js";
import { modal } from "./dialogs.js";
import { shortPath } from "./folders.js";

const ago = (s) => (s < 45 ? "just now" : s < 3600 ? `${Math.round(s / 60)} min ago` : `${Math.round(s / 3600)} h ago`);
const clock = (t) => new Date(t * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

// Where a memory is stored: this Mac only, or this Mac + cloud (a synced folder, Mac + WebDAV, WebDAV only), and a
// GitHub backup that works with any of them.
// ctx: {name, storage, pick(prompt, start), move(parent, label), toMac(parent, label, keepSync), toWebdav(), toCloudOnly(),
//       stopWebdav(), toGithub(), stopGithub(repo), reveal(), download()}. Each action resolves true when done.
export function openStorage(ctx) {
  return modal((done) => {
    const s = ctx.storage;
    const err = el("div", { class: "dlg-err" });
    const busy = (b) => card.classList.toggle("busy", b);
    const run = async (fn, result) => {
      err.textContent = ""; busy(true);
      try { if (await fn()) done(result); else busy(false); } catch (e) { err.textContent = e.message; busy(false); }
    };
    const btn = (label, fn, cls = "") => el("button", { class: "btn small " + cls, type: "button", onclick: fn }, label);
    const now = (on) => on ? el("span", { class: "st-opt-now" }, "Now") : null;
    const ago = (sec) => sec == null ? "not yet" : sec < 60 ? "just now" : sec < 3600 ? `${Math.round(sec / 60)} min ago` : `${Math.round(sec / 3600)} h ago`;
    const option = (ic, title, tip, on, ...body) => el("div", { class: "st-opt" + (on ? " on" : "") },
      el("div", { class: "st-opt-head" }, el("span", { class: "st-opt-icon" }, icon(ic, 16)),
        el("div", { class: "st-opt-title" }, title, info(tip)), now(on)),
      ...body.filter(Boolean));
    const sub = (label, tip, on, ...body) => el("div", { class: "st-sub" + (on ? " on" : "") },
      el("div", { class: "st-sub-head" }, label, info(tip), now(on)), ...body.filter(Boolean));

    const macOnly = !s.cloud && !s.webdav && !s.cloudOnly;
    const folderSynced = !!s.cloud && !s.webdav;
    // to a place on this Mac (a plain folder, or one a cloud app syncs)
    const toPlace = (where, label) => run(() => s.cloudOnly ? ctx.toMac(where, label, false) : ctx.move(where, label), "moved");

    const chips = el("div", { class: "st-places" }, ...s.places.map((p) => {
      const here = folderSynced && s.path.startsWith(p.path + "/");
      return el("button", { class: "st-place" + (here ? " on" : ""), type: "button", disabled: here, title: p.path,
        onclick: async () => { const w = await ctx.pick(`Choose where in ${p.name} to keep "${ctx.name}"`, p.path); if (w) toPlace(w, p.name); } },
        icon("cloud", 15), el("span", {}, p.name));
    }), btn("Other folder", async () => { const w = await ctx.pick("Choose a folder your cloud app syncs"); if (w) toPlace(w, "that folder"); }));
    if (!s.places.length) chips.prepend(el("div", { class: "st-none" }, "No cloud apps found on this Mac."));

    const webdavNow = s.webdav ? `Mac + WebDAV. Synced with ${s.webdav}` : s.cloudOnly ? `WebDAV only. Opens from ${s.path}` : "";
    const webdavBtns = el("div", { class: "set-btns" },
      s.webdav ? null : btn("Mac + WebDAV", () => run(() => s.cloudOnly
        ? ctx.pick("Choose a place on this Mac for the copy").then((w) => w && ctx.toMac(w, "this Mac", true))
        : ctx.toWebdav(), s.cloudOnly ? "moved" : "changed")),
      s.cloudOnly ? null : btn("WebDAV only", () => run(ctx.toCloudOnly, "tocloud")));

    const gs = s.githubStatus;
    const github = s.github
      ? el("div", { class: "st-gh" },
          el("div", {}, el("b", {}, s.github), gs && gs.error ? el("span", { class: "st-gh-err" }, ` · ${gs.error}`) : ` · saved ${ago(gs && gs.ago)}`),
          gs && gs.too_big && gs.too_big.length ? el("div", { class: "st-gh-note" }, `${gs.too_big.length} file${gs.too_big.length === 1 ? " is" : "s are"} over 95 MB and stay${gs.too_big.length === 1 ? "s" : ""} out of the backup.`) : null,
          el("div", {}, btn("Stop backup", () => run(() => ctx.stopGithub(s.github), "changed"), "st-stop")))
      : el("div", {}, el("button", { class: "btn gh-btn", type: "button", onclick: () => run(ctx.toGithub, "changed") }, githubMark(), "Turn on backup"));

    const card = el("div", { class: "dlg storage", role: "dialog" },
      el("div", { class: "dlg-title" }, `Storage and backup: ${ctx.name}`),
      el("div", { class: "st-where" }, icon(s.cloudOnly || s.cloud || s.webdav ? "cloud" : "laptop", 14), el("span", { title: s.path }, shortPath(s.path)),
        s.cloudOnly ? null : btn("Show encrypted files", () => ctx.reveal())),
      s.offline ? el("div", { class: "st-warn" },
        el("span", {}, `${s.offline} file${s.offline === 1 ? " is" : "s are"} only in the cloud and can't open yet.`),
        btn("Download now", () => ctx.download())) : null,
      el("div", { class: "st-e2e" }, icon("lock", 14), el("span", {}, "Every copy, on the cloud or a backup, is encrypted end to end. Only you can read it, with your password.")),
      el("div", { class: "set-section" }, "Stored in"),
      option("laptop", "This Mac only",
        "A folder on this Mac. It's encrypted: only you can read it, with your password. Nothing goes online unless you add a backup.",
        macOnly,
        macOnly ? null : el("div", {}, s.webdav
          ? btn("Keep on this Mac only", () => run(ctx.stopWebdav, "changed"))
          : btn("Move to this Mac", async () => { const w = await ctx.pick("Choose a place on this Mac"); if (w) toPlace(w, "this Mac"); }))),
      option("cloud", "This Mac + cloud", "Your cloud only gets encrypted files. Only you can read them, with your password.",
        !macOnly,
        sub("Synced folder", "A folder your cloud app keeps in sync, like iCloud Drive or Dropbox.", folderSynced, chips),
        sub("WebDAV", "A server such as Nextcloud. Mac + WebDAV keeps a copy on this Mac that stays in sync. WebDAV only keeps nothing on this Mac: the memory opens from the server.",
          !!(s.webdav || s.cloudOnly), webdavNow ? el("div", { class: "st-gh-note" }, webdavNow) : null, webdavBtns)),
      el("div", { class: "set-section" }, "Backup"),
      option("lock", "Private GitHub", "A private GitHub repo keeps an encrypted copy and every past version. It updates a few seconds after each change, and works with any place above. GitHub takes files up to 95 MB each, and works best when the whole memory is under about 5 GB.",
        !!s.github, el("div", { class: "st-gh-note" }, "Limits: each file up to 95 MB, the whole memory up to about 5 GB. Bigger files stay out of this backup."), github),
      option("cloud", "Amazon S3 or Cloudflare R2", "An encrypted copy in your Amazon S3 or Cloudflare R2 bucket. It updates a few seconds after each change, keeps the files it replaces in a history folder, and takes files of any size.",
        !!s.s3, s.s3
          ? el("div", { class: "st-gh" }, el("div", {}, el("b", {}, s.s3), s.s3Status && s.s3Status.error ? el("span", { class: "st-gh-err" }, ` · ${s.s3Status.error}`) : ` · saved ${ago(s.s3Status && s.s3Status.ago)}`),
              el("div", {}, btn("Stop backup", () => run(ctx.stopS3, "changed"), "st-stop")))
          : el("div", {}, btn("Turn on backup", () => run(ctx.toS3, "changed")))),
      option("file", "Backup file", "One .zip of the encrypted files, to keep on a USB stick, a drive or anywhere. It opens with the same password, or the recovery key: Open memory › From a backup file.",
        false, el("div", {}, btn("Save backup file", () => run(ctx.saveBackup, null)))),
      el("div", { class: "st-note" }, "Moving locks the memory first. Unlock it again after."),
      err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", onclick: () => done(null) }, "Close")));
    return { card };
  });
}

// A small ⓘ: hover shows what the thing does; a click (or Enter) keeps it open until the next click.
let infoPop = null;
function hideInfo() { if (infoPop) { infoPop.el.remove(); infoPop = null; } }
document.addEventListener("mousedown", (e) => { if (infoPop && !e.target.closest(".info-i")) hideInfo(); }, true);
document.addEventListener("keydown", (e) => { if (e.key === "Escape" && infoPop) { hideInfo(); e.stopPropagation(); } }, true);
export function info(text) {
  const i = el("span", { class: "info-i", tabindex: "0", role: "button", "aria-label": text }, "i");
  const show = (pinned) => {
    if (infoPop && infoPop.for === i) { infoPop.pinned ||= pinned; return; }
    hideInfo();
    const pop = el("div", { class: "info-pop", role: "tooltip" }, text);
    document.body.append(pop);
    const r = i.getBoundingClientRect(), w = pop.offsetWidth;
    pop.style.left = Math.max(8, Math.min(innerWidth - w - 8, r.left + r.width / 2 - w / 2)) + "px";
    const below = r.bottom + 6 + pop.offsetHeight < innerHeight;
    pop.style.top = (below ? r.bottom + 6 : r.top - 6 - pop.offsetHeight) + "px";
    infoPop = { el: pop, for: i, pinned };
  };
  i.addEventListener("mouseenter", () => show(false));
  i.addEventListener("mouseleave", () => { if (infoPop && infoPop.for === i && !infoPop.pinned) hideInfo(); });
  i.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); infoPop && infoPop.for === i && infoPop.pinned ? hideInfo() : show(true); });
  i.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); e.stopPropagation(); show(true); } });
  return i;
}

// One AI panel with two tabs: Tasks (notes given to the AI, each with what to do) and Activity (what AI apps did).
// ctx.tasks: {path?, label(path), todo:[{id, path, ask, t, done, by, result}], give(ask) -> todo, set(id, done) -> todo,
//             remove(id) -> todo, load() -> todo, open(path)}   With path, a box on top gives that note.
// ctx.activity: {rows:[{t, ago, app, folderName, what, detail, path, undo, canUndo}], open(path), undo(row), fail(msg)}
export function openAIPanel(ctx, start = "tasks") {
  return modal((done) => {
    const tasks = tasksView(ctx.tasks, done), activity = activityView(ctx.activity, done);
    const views = { tasks, activity, approvals: approvalsView(ctx.approvals) };
    const body = el("div", { class: "ai-body" });
    const tools = el("div", { class: "act-tools" });
    const tabs = el("div", { class: "seg", role: "tablist" });
    const show = (k) => {
      for (const b of tabs.children) { const on = b.dataset.k === k; b.classList.toggle("on", on); b.setAttribute("aria-selected", on); }
      body.replaceChildren(...views[k].body);
      tools.replaceChildren(...(views[k].tools || []));
      if (k === "tasks" && tasks.focus) tasks.focus.focus();
    };
    for (const [k, label] of [["tasks", "Tasks"], ["activity", "Activity"], ["approvals", "Approvals"]]) {
      tabs.append(el("button", { class: "seg-b", type: "button", role: "tab", "data-k": k, onclick: () => show(k) }, label));
    }
    const card = el("div", { class: "dlg activity", role: "dialog" },
      el("div", { class: "act-head" }, el("div", { class: "ai-head-left" }, el("div", { class: "dlg-title" }, "AI"), tabs), tools),
      body,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", onclick: () => done(null) }, "Close")));
    show(start);
    return { card, focus: start === "tasks" ? tasks.focus : null };
  });
}

function activityView(ctx, done) {
  const apps = [...new Set(ctx.rows.map((r) => r.app))];
  const filter = el("select", { class: "act-filter", "aria-label": "Which app" },
    el("option", { value: "" }, "All AI apps"), ...apps.map((a) => el("option", { value: a }, a)));
  const list = el("div", { class: "act-list" });
  const draw = () => {
    const rows = ctx.rows.filter((r) => !filter.value || r.app === filter.value);
    list.replaceChildren(...(rows.length ? rows.map((r) => {
      const pathBtn = r.path ? el("button", { class: "act-path", type: "button", title: "Open this note",
                                              onclick: () => { done(null); ctx.open(r.path); } }, r.path) : null;
      return el("div", { class: "act-row" + (/changed|added|created/.test(r.what) ? " write" : "") },
        el("div", { class: "act-time", title: new Date(r.t * 1000).toLocaleString() }, clock(r.t), el("span", {}, ago(r.ago))),
        el("div", { class: "act-main" },
          el("div", { class: "act-line" }, el("b", {}, r.app), ` ${r.what} `, pathBtn,
            r.canUndo ? el("button", { class: "btn small act-undo", type: "button", title: "Put the note back as it was before this change",
              onclick: async (e) => {
                const b = e.currentTarget; b.disabled = true;
                try { await ctx.undo(r); r.canUndo = false; b.replaceWith(el("span", { class: "act-undone" }, "Undone")); }
                catch (err) { b.disabled = false; b.title = err.message; ctx.fail(err.message); }
              } }, "Undo") : null),
          r.detail ? el("div", { class: "act-detail" }, r.detail) : null,
          el("div", { class: "act-folder" }, r.folderName)));
    }) : [el("div", { class: "act-empty" }, "No AI app has used your notes since they were unlocked.")]));
  };
  filter.addEventListener("change", draw);
  draw();
  return { tools: apps.length > 1 ? [filter] : [],
           body: [el("div", { class: "mf-hint" }, "What AI apps did with your unlocked notes. Kept only until you lock."), list] };
}

// Your yeses (unlocks, AI apps let in, what each may reach), each sealed: a line changed later shows as broken.
function approvalsView(rows) {
  const now = Date.now() / 1000;
  const list = el("div", { class: "act-list" }, ...(rows.length ? rows.map((r) =>
    el("div", { class: "act-row" + (r.sealed ? "" : " broken") },
      el("div", { class: "act-time", title: new Date(r.t * 1000).toLocaleString() }, clock(r.t), el("span", {}, ago(Math.max(0, now - r.t)))),
      el("div", { class: "act-main" },
        el("div", { class: "act-line" }, r.what),
        el("div", { class: "act-folder" }, [r.detail, r.how && `by ${r.how}`].filter(Boolean).join(" · "))),
      el("span", { class: "seal", title: r.sealed ? "Sealed: unchanged since it was written" : "Changed or removed after it was written" },
        r.sealed ? icon("check", 14, 2) : "!")))
    : [el("div", { class: "act-empty" }, "Nothing yet.")]));
  return { tools: [], body: [list] };
}

function tasksView(ctx, done) {
  let todo = ctx.todo;
  const err = el("div", { class: "dlg-err" });
  const list = el("div", { class: "act-list todo-list" });
  const act = async (fn) => {
    err.textContent = "";
    try { todo = await fn(); draw(); } catch (e) { err.textContent = e.message; }
  };
  const draw = () => {
    const items = [...todo].sort((a, b) => (a.done - b.done) || (b.t - a.t));
    list.replaceChildren(...(items.length ? items.map((i) => {
      const box = el("input", { type: "checkbox", class: "todo-check", "aria-label": "Done" });
      box.checked = !!i.done;
      box.addEventListener("change", () => act(() => ctx.set(i.id, box.checked)));
      return el("div", { class: "todo-row" + (i.done ? " done" : "") }, box,
        el("div", { class: "act-main" },
          el("button", { class: "act-path", type: "button", title: i.path, onclick: () => { done(null); ctx.open(i.path); } }, ctx.label(i.path)),
          el("div", { class: "act-detail" }, i.ask || "No request: just read it."),
          i.done ? el("div", { class: "todo-result" }, `${i.by && i.by !== "you" ? i.by : "Ticked off by you"}${i.result ? ": " + i.result : ""}`)
                 : el("div", { class: "act-folder" }, `Given ${ago(Math.max(0, Date.now() / 1000 - i.t))}`)),
        el("button", { class: "icon-btn todo-x", type: "button", title: "Remove from the list", "aria-label": "Remove",
                       onclick: () => act(() => ctx.remove(i.id)) }, icon("x", 14)));
    }) : [el("div", { class: "act-empty" }, "No tasks yet. Open a note and press the sparkle button to give your AI a task.")]));
  };
  draw();
  // Stay current while open: the AI may tick things off meanwhile.
  const tick = setInterval(async () => {
    if (!list.isConnected && !document.querySelector(".ai-body")) { clearInterval(tick); return; }
    if (!list.isConnected) return;
    try { const t = await ctx.load(); if (JSON.stringify(t) !== JSON.stringify(todo)) { todo = t; draw(); } } catch {}
  }, 4000);

  let give = null, ask = null;
  if (ctx.path) {
    ask = el("textarea", { class: "dlg-input todo-ask", rows: "3", spellcheck: "true",
                           placeholder: "What should the AI do with this note? (optional)\nFor example: fix typos and make it shorter." });
    const add = () => act(async () => {
      const t = await ctx.give(ask.value);
      ask.value = "";
      return t;
    });
    ask.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) { e.preventDefault(); add(); } });
    give = el("div", { class: "todo-give" },
      el("div", { class: "dlg-sub" }, "Give AI a task with ", el("b", {}, ctx.label(ctx.path))),
      ask,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn primary", type: "button", onclick: add }, "Add task")));
  }
  return { focus: ask, body: [give,
    el("div", { class: "mf-hint" }, "Ask your AI: \u201cDo my Phygital Memory tasks.\u201d You can undo its changes in Activity."),
    list, err].filter(Boolean) };
}

// The trash: everything moved there stays (encrypted, inside the folder) until restored.
// ctx: {items:[{id, name, path, kind, t}], restore(id) -> {path, items}, open(path)}
export function openTrash(ctx) {
  return modal((done) => {
    let items = ctx.items;
    const err = el("div", { class: "dlg-err" });
    const list = el("div", { class: "act-list" });
    const draw = () => list.replaceChildren(...(items.length ? items.map((i) => el("div", { class: "todo-row trash-row" },
      el("span", { class: "trash-ic" }, icon(i.kind === "folder" ? "folder" : "file", 14)),
      el("div", { class: "act-main" },
        el("div", { class: "act-line" }, i.name.replace(/\.md$/i, "")),
        el("div", { class: "act-folder" }, `Was at ${i.path}${i.t ? " · " + new Date(i.t * 1000).toLocaleString() : ""}`)),
      el("button", { class: "btn small", type: "button", onclick: async () => {
        err.textContent = "";
        try { const j = await ctx.restore(i.id); items = j.items; draw(); if (i.kind !== "folder") { done(null); ctx.open(j.path); } }
        catch (e) { err.textContent = e.message; }
      } }, "Restore"))) : [el("div", { class: "act-empty" }, "The trash is empty.")]));
    draw();
    const card = el("div", { class: "dlg activity", role: "dialog" },
      el("div", { class: "dlg-title" }, "Trash"),
      el("div", { class: "mf-hint" }, "Restore puts it back where it was. Nothing in here is ever overwritten."),
      list, err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", onclick: () => done(null) }, "Close")));
    return { card };
  });
}

// Sign in with GitHub: the app asks GitHub for a short code and opens github.com in the browser; the person types
// the code there and approves. ctx: {start() -> {code, url, interval}, poll() -> {state, account}}.
// Resolves with the GitHub account name, or null if cancelled or refused.
export function openGithubSignIn(ctx) {
  return modal((done) => {
    let alive = true, timer = null;
    const finish = (v) => { alive = false; clearTimeout(timer); done(v); };
    const code = el("div", { class: "gh-code" }, "");
    const line = el("div", { class: "dlg-sub" }, "Asking GitHub for a sign-in code");
    const err = el("div", { class: "dlg-err" });
    const copy = el("button", { class: "btn small", type: "button", disabled: true,
      onclick: () => navigator.clipboard.writeText(code.textContent).then(() => { copy.textContent = "Copied"; }) }, "Copy code");
    const card = el("div", { class: "dlg gh-signin", role: "dialog" },
      el("div", { class: "dlg-title" }, "Sign in with GitHub"),
      line, code, el("div", { class: "gh-row" }, copy),
      el("div", { class: "mf-hint" }, "The app's GitHub key stays in this Mac's Keychain. Remove it on GitHub any time: Settings › Applications."),
      err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", type: "button", onclick: () => finish(null) }, "Cancel")));
    (async () => {
      try {
        const s = await ctx.start();
        code.textContent = s.code; copy.disabled = false;
        line.textContent = `Your browser opened ${s.url.replace(/^https:\/\//, "")}. Type this code there and press Authorize.`;
        let wait = (s.interval || 5) * 1000;
        const tick = async () => {
          if (!alive) return;
          try {
            const r = await ctx.poll();
            if (r.state === "done") { finish(r.account || ""); return; }
            if (r.state === "denied") { err.textContent = "GitHub said no, so nothing was connected."; return; }
            if (r.state === "expired") { err.textContent = "The code ran out. Close this and press Connect GitHub again."; return; }
            if (r.state === "slow") wait += 5000;
          } catch (e) { err.textContent = e.message; }
          timer = setTimeout(tick, wait);
        };
        timer = setTimeout(tick, wait);
      } catch (e) { line.textContent = ""; err.textContent = e.message; }
    })();
    return { card };
  });
}

// GitHub's own mark, for the Sign in with GitHub button (drawn here, nothing loaded from GitHub).
function githubMark() {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 16 16"); svg.setAttribute("width", "16"); svg.setAttribute("height", "16");
  svg.setAttribute("aria-hidden", "true");
  const path = document.createElementNS(ns, "path");
  path.setAttribute("fill", "currentColor");
  path.setAttribute("d", "M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z");
  svg.append(path);
  return svg;
}

// Open from GitHub: the person's memory repos to pick from. Resolves with "owner/name", "" for "Another repo"
// (typed by hand), or null if cancelled.
export function pickRepo(repos) {
  return modal((done) => {
    const when = (t) => t ? new Date(t).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }) : "";
    const list = el("div", { class: "act-list" }, ...(repos.length ? repos.map((r) =>
      el("button", { class: "todo-row repo-row", type: "button", onclick: () => done(r.repo) },
        el("span", { class: "trash-ic" }, githubMark()),
        el("div", { class: "act-main" }, el("div", { class: "act-line" }, r.name), el("div", { class: "act-folder" }, `${r.repo}${r.pushed ? " · last change " + when(r.pushed) : ""}`))))
      : [el("div", { class: "act-empty" }, "No Phygital Memory repos found on this GitHub account.")]));
    const card = el("div", { class: "dlg activity", role: "dialog" },
      el("div", { class: "dlg-title" }, "Open from GitHub"),
      el("div", { class: "mf-hint" }, "Your private Phygital Memory repos. Pick one, then unlock it with its password."),
      list,
      el("div", { class: "dlg-actions" },
        el("button", { class: "btn", type: "button", onclick: () => done("") }, "Another repo"),
        el("button", { class: "btn", type: "button", onclick: () => done(null) }, "Cancel")));
    return { card };
  });
}

// Open from cloud: a memory that lives only in the person's cloud (Nextcloud or WebDAV for now). Steps: pick a cloud
// (one connected before, or a new login), see the memories in it, pick one or make a new one there.
// ctx: {clouds:[{kind,url,user,name,where}], connect({kind,server,user,password}) -> {conn, memories},
//       memories(conn) -> {conn, memories}, move?: {name}}
// Resolves {conn, path} (open), {conn, create: {parent, name, password}} (new), {conn, move: {parent}}, or null.
export function openCloud(ctx) {
  return modal((done) => {
    const body = el("div", { class: "cl-body" });
    const err = el("div", { class: "dlg-err" });
    const actions = el("div", { class: "dlg-actions" });
    const keep = ctx.move && ctx.move.keepMac;   // Mac + WebDAV: a copy goes up and stays in sync, the Mac copy stays
    const top = keep ? `Sync "${ctx.move.name}" with WebDAV` : ctx.move ? `Move "${ctx.move.name}" to WebDAV` : "Open from WebDAV";
    const title = el("div", { class: "dlg-title" }, top);
    let submit = null;
    const card = el("div", { class: "dlg storage cloud-dlg", role: "dialog" }, title, body, err, actions);
    const busy = (b) => card.classList.toggle("busy", b);
    const btn = (label, fn, cls) => el("button", { class: "btn " + (cls || ""), type: "button", onclick: fn }, label);
    const cancel = btn("Cancel", () => done(null));
    const row = (ic, main, sub, fn) => el("button", { class: "todo-row repo-row", type: "button", onclick: fn },
      el("span", { class: "trash-ic" }, icon(ic, 16)),
      el("div", { class: "act-main" }, el("div", { class: "act-line" }, main), el("div", { class: "act-folder" }, sub)));

    const pick = () => {
      if (!ctx.clouds.length) { login(); return; }   // nothing connected yet: straight to the form
      title.textContent = top; err.textContent = ""; submit = null;
      body.replaceChildren(
        el("div", { class: "mf-hint" }, keep ? "Pick the server. Only encrypted files go up. The copy on this Mac stays."
          : ctx.move ? "Pick the server. Only encrypted files go up. Once all have arrived, the copy on this Mac goes to the Trash."
          : "Open a memory that's on a WebDAV server. Nothing is kept on this Mac. The server only gets encrypted files."),
        el("div", { class: "act-list" },
          ...ctx.clouds.map((c) => row("cloud", c.where, `Connected as ${c.user}`, () => look(c))),
          row("plus", "Another server", "Nextcloud, ownCloud, Synology, Koofr or any WebDAV server", () => login())));
      actions.replaceChildren(cancel);
    };

    const login = (prefill = {}) => {
      title.textContent = "Connect to WebDAV";
      err.textContent = ""; err.classList.remove("ok");
      const server = el("input", { class: "dlg-input", spellcheck: "false", autocomplete: "off", value: prefill.server || "",
        placeholder: "Server address, like cloud.example.com", "aria-label": "Server" });
      const user = el("input", { class: "dlg-input", spellcheck: "false", autocomplete: "off", value: prefill.user || "", placeholder: "User name", "aria-label": "User name" });
      const pw = el("input", { class: "dlg-input", type: "password", autocomplete: "off", placeholder: "Password or app password", "aria-label": "Password" });
      const fields = () => {
        if (!server.value.trim() || !user.value.trim() || !pw.value) { err.classList.remove("ok"); err.textContent = "Fill in all three."; return null; }
        return { server: server.value, user: user.value, password: pw.value };
      };
      const test = async () => {
        const f = fields(); if (!f) return;
        err.classList.remove("ok"); err.textContent = ""; busy(true);
        try { const j = await ctx.test(f); err.classList.add("ok"); err.textContent = `Connected to ${j.where}.`; }
        catch (e) { err.textContent = e.message; }
        busy(false);
      };
      submit = async () => {
        const f = fields(); if (!f) return;
        err.classList.remove("ok"); err.textContent = ""; busy(true);
        try {
          const j = await ctx.connect(f);
          pw.value = ""; busy(false); (ctx.move ? moveTo : list)(j.conn, j.memories);
        } catch (e) { err.textContent = e.message; busy(false); }
      };
      body.replaceChildren(server, user, pw,
        el("div", { class: "st-gh-note" }, "For Nextcloud, make an app password: Settings › Security. The password stays in this Mac's Keychain."));
      actions.replaceChildren(ctx.clouds.length ? btn("Back", () => { pw.value = ""; pick(); }) : cancel,
        btn("Test connection", test), btn("Connect", submit, "primary"));
      server.value ? (prefill.user ? pw : user).focus() : server.focus();
    };

    const look = async (c) => {
      err.textContent = ""; busy(true);
      if (ctx.move) { moveTo(c); return; }
      try { const j = await ctx.memories(c); busy(false); list(j.conn, j.memories); }
      catch (e) {
        busy(false);
        login({ server: c.kind === "nextcloud" ? c.url.split("/remote.php/")[0] : c.url, user: c.user });
        err.textContent = e.message;
      }
    };

    const list = (conn, memories) => {
      title.textContent = "Memories in your cloud"; err.textContent = ""; submit = null;
      body.replaceChildren(
        el("div", { class: "mf-hint" }, "Pick one, then unlock it with its password. It opens from the server, nothing is downloaded."),
        el("div", { class: "act-list" }, ...(memories.length
          ? memories.map((m) => row("lock", m.name, m.path, () => done({ conn, path: m.path })))
          : [el("div", { class: "act-empty" }, "No memories found in this cloud yet.")])));
      actions.replaceChildren(btn("Back", pick), btn("New memory here", () => create(conn, memories), "primary"));
    };

    const moveTo = (conn) => {
      title.textContent = top; err.textContent = "";
      const parent = el("input", { class: "dlg-input", spellcheck: "false", placeholder: "Folder on the server (empty: the top)", "aria-label": "Folder on the server" });
      submit = () => done({ conn, move: { parent: parent.value.trim().replace(/^\/+|\/+$/g, "") } });
      body.replaceChildren(parent,
        el("div", { class: "st-gh-note" }, keep ? "A big memory can take a while to upload." : "It locks first. A big memory can take a while to upload. Your password stays the same."));
      actions.replaceChildren(btn("Back", pick), btn(keep ? "Sync" : "Move", submit, "primary"));
      parent.focus();
    };

    const create = (conn, memories) => {
      title.textContent = "New memory in your cloud"; err.textContent = "";
      const name = el("input", { class: "dlg-input", spellcheck: "false", placeholder: "Name", "aria-label": "Name" });
      const parent = el("input", { class: "dlg-input", spellcheck: "false", placeholder: "Folder in the cloud (empty: the top)", "aria-label": "Folder in the cloud" });
      const pw = el("input", { class: "dlg-input", type: "password", autocomplete: "off", placeholder: "Password (8 or more characters)", "aria-label": "Password" });
      const pw2 = el("input", { class: "dlg-input", type: "password", autocomplete: "off", placeholder: "Password again", "aria-label": "Password again" });
      submit = () => {
        const n = name.value.trim();
        if (!n || /[\/\\:*?"<>|]/.test(n) || n.startsWith(".")) { err.textContent = "Pick a simple name (no / \\ : * ? \" < > |)."; return; }
        if (pw.value.length < 8) { err.textContent = "The password needs at least 8 characters."; return; }
        if (pw.value !== pw2.value) { err.textContent = "The two passwords differ."; return; }
        const out = { conn, create: { parent: parent.value.trim().replace(/^\/+|\/+$/g, ""), name: n, password: pw.value } };
        pw.value = pw2.value = "";
        done(out);
      };
      body.replaceChildren(name, parent, pw, pw2,
        el("div", { class: "st-gh-note" }, "This password unlocks the memory. Nobody can reset it, so keep it somewhere safe."));
      actions.replaceChildren(btn("Back", () => { pw.value = pw2.value = ""; list(conn, memories); }), btn("Create", submit, "primary"));
      name.focus();
    };

    pick();
    return { card, submit: () => submit && submit() };
  });
}

// S3 or R2: the keys and the bucket, for a backup (restore: false) or to bring a memory back (restore: true).
// ctx: {restore, test(fields), connect(fields) -> {conn, bucket}, memories(fields) -> {conn, memories}}
// Resolves {conn, bucket} (backup), {conn, path} (restore), or null.
export function openS3(ctx) {
  return modal((done) => {
    let kind = "s3";
    const err = el("div", { class: "dlg-err" });
    const body = el("div", { class: "cl-body" });
    const title = el("div", { class: "dlg-title" }, ctx.restore ? "Open from Amazon S3 or Cloudflare R2" : "Back up to Amazon S3 or Cloudflare R2");
    const actions = el("div", { class: "dlg-actions" });
    const card = el("div", { class: "dlg storage cloud-dlg", role: "dialog" }, title, body, err, actions);
    const busy = (b) => card.classList.toggle("busy", b);
    const btn = (label, fn, cls) => el("button", { class: "btn " + (cls || ""), type: "button", onclick: fn }, label);
    const input = (ph, label, type = "text") => el("input", { class: "dlg-input", type, spellcheck: "false", autocomplete: "off", placeholder: ph, "aria-label": label });
    const bucket = input("Bucket name, like my-notes-backup", "Bucket");
    const keyId = input("Access Key ID", "Access Key ID");
    const secret = input("Secret Access Key", "Secret Access Key", "password");
    const where = input("Region, like eu-west-1", "Region");
    const hint = el("div", { class: "st-gh-note" });
    const drawHint = () => { hint.textContent = kind === "r2"
      ? "Cloudflare shows three values after you make an API token. Use the Access Key ID, the Secret Access Key and the S3 endpoint. You don't need the Token value."
      : "From your IAM user's access key in AWS. The region is where the bucket is, like eu-west-1."; };
    drawHint();
    const tabs = el("div", { class: "seg", role: "radiogroup" });
    const drawTabs = () => tabs.replaceChildren(...[["s3", "Amazon S3"], ["r2", "Cloudflare R2"]].map(([k, t]) =>
      el("button", { class: "seg-b" + (kind === k ? " on" : ""), type: "button", onclick: () => {
        kind = k; drawTabs(); drawHint(); where.placeholder = k === "r2" ? "S3 endpoint, like https://ID.r2.cloudflarestorage.com" : "Region, like eu-west-1";
        where.setAttribute("aria-label", k === "r2" ? "S3 endpoint" : "Region"); } }, t)));
    drawTabs();
    const fields = () => {
      if (![bucket, keyId, secret, where].every((i) => i.value.trim())) { err.classList.remove("ok"); err.textContent = "Fill in all four."; return null; }
      return { kind, bucket: bucket.value.trim(), keyId: keyId.value.trim(), secret: secret.value, where: where.value.trim() };
    };
    const go = async (fn) => {
      const f = fields(); if (!f) return;
      err.classList.remove("ok"); err.textContent = ""; busy(true);
      try { await fn(f); } catch (e) { err.textContent = e.message; }
      busy(false);
    };
    const test = () => go(async (f) => { const j = await ctx.test(f); err.classList.add("ok"); err.textContent = `Connected to ${j.where}.`; });
    const next = () => go(async (f) => {
      if (!ctx.restore) { const j = await ctx.connect(f); secret.value = ""; done({ conn: j.conn, bucket: j.bucket }); return; }
      const j = await ctx.memories(f);
      secret.value = "";
      title.textContent = "Backups in this bucket";
      body.replaceChildren(el("div", { class: "act-list" }, ...(j.memories.length ? j.memories.map((m) =>
        el("button", { class: "todo-row repo-row", type: "button", onclick: () => done({ conn: j.conn, path: m.path }) },
          el("span", { class: "trash-ic" }, icon("lock", 16)), el("div", { class: "act-main" }, el("div", { class: "act-line" }, m.name),
            el("div", { class: "act-folder" }, m.path)))) : [el("div", { class: "act-empty" }, "No backups found in this bucket.")])));
      actions.replaceChildren(btn("Cancel", () => done(null)));
    });
    body.replaceChildren(tabs, bucket, keyId, secret, where, hint,
      el("div", { class: "st-gh-note" }, "The app never makes or deletes buckets. The secret key stays in this Mac's Keychain."));
    actions.replaceChildren(btn("Cancel", () => done(null)), btn("Test connection", test), btn(ctx.restore ? "Find backups" : "Back up", next, "primary"));
    return { card, focus: bucket, submit: next };
  });
}
