// Panels from the sidebar's status icons: where this folder is stored, the AI panel (tasks and activity), the trash.
// Everything from the server is put in as text only.
import { el, icon } from "./dom.js";
import { modal } from "./dialogs.js";
import { shortPath } from "./folders.js";

const ago = (s) => (s < 45 ? "just now" : s < 3600 ? `${Math.round(s / 60)} min ago` : `${Math.round(s / 3600)} h ago`);
const clock = (t) => new Date(t * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

// ctx: {name, storage: {path, cloud, places:[{name, path}], home}, pick(prompt) -> path|null, move(parent) -> Promise,
//       reveal()}
export function openStorage(ctx) {
  return modal((done) => {
    const s = ctx.storage;
    const err = el("div", { class: "dlg-err" });
    const busy = (b) => card.classList.toggle("busy", b);
    const moveTo = async (parent, label) => {
      err.textContent = "";
      busy(true);
      try { if (await ctx.move(parent, label)) done(true); else busy(false); }
      catch (e) { err.textContent = e.message; busy(false); }
    };
    const option = (key, title, text, on, body) => el("div", { class: "st-opt" + (on ? " on" : "") },
      el("div", { class: "st-opt-head" }, el("span", { class: "st-opt-icon" }, icon(key, 16)),
        el("div", {}, el("div", { class: "st-opt-title" }, title), el("div", { class: "st-opt-text" }, text)),
        on ? el("span", { class: "st-opt-now" }, "Now") : null),
      body || null);

    const local = !s.cloud && !s.github;
    const ago = (sec) => sec == null ? "not yet" : sec < 60 ? "just now" : sec < 3600 ? `${Math.round(sec / 60)} min ago` : `${Math.round(sec / 3600)} h ago`;
    const gs = s.githubStatus;
    const githubBody = s.github
      ? el("div", { class: "st-gh" },
          el("div", {}, el("b", {}, s.github), gs && gs.error ? el("span", { class: "st-gh-err" }, ` · ${gs.error}`) : ` · synced ${ago(gs && gs.ago)}`),
          gs && gs.too_big && gs.too_big.length ? el("div", { class: "st-gh-note" }, `${gs.too_big.length} file${gs.too_big.length === 1 ? " is" : "s are"} over 95 MB, so ${gs.too_big.length === 1 ? "it stays" : "they stay"} on this Mac only.`) : null,
          el("div", {}, el("button", { class: "btn small st-stop", type: "button", onclick: async () => {
            err.textContent = ""; busy(true);
            try { if (await ctx.stopGithub(s.github)) done(true); else busy(false); } catch (e) { err.textContent = e.message; busy(false); }
          } }, "Stop GitHub sync…")))
      : el("div", {}, el("div", { class: "st-gh-note" }, "Nothing talks to GitHub until you press the button."),
          el("button", { class: "btn gh-btn", type: "button", onclick: async () => {
            err.textContent = ""; busy(true);
            try { if (await ctx.toGithub()) done(true); else busy(false); } catch (e) { err.textContent = e.message; busy(false); }
          } }, githubMark(), "Sign in with GitHub"));
    const cloudCards = el("div", { class: "st-places" }, ...s.places.map((p) => {
      const here = s.cloud && s.path.startsWith(p.path + "/");
      return el("button", { class: "st-place" + (here ? " on" : ""), type: "button", disabled: here, title: p.path,
                            onclick: async () => {   // the person picks where inside that cloud
                              const where = await ctx.pick(`Choose where in ${p.name} to keep "${ctx.name}"`, p.path);
                              if (where) moveTo(where, p.name);
                            } },
        icon("cloud", 15), el("span", {}, p.name), here ? el("span", { class: "st-here" }, "here") : null);
    }));
    if (!s.places.length) cloudCards.append(el("div", { class: "st-none" }, "No cloud apps found on this Mac (iCloud Drive, Dropbox, Google Drive, OneDrive, Nextcloud…)."));

    const card = el("div", { class: "dlg storage", role: "dialog" },
      el("div", { class: "dlg-title" }, `Where "${ctx.name}" is stored`),
      el("div", { class: "st-where" }, icon(s.cloud ? "cloud" : "laptop", 14), el("span", { title: s.path }, shortPath(s.path)),
        el("button", { class: "btn small", type: "button", onclick: () => ctx.reveal() }, "Show encrypted files")),
      s.offline ? el("div", { class: "st-warn" },
        el("span", {}, `${s.offline} file${s.offline === 1 ? " is" : "s are"} only in the cloud, not on this Mac, so they can't open. `
          + `In Finder, right-click the folder and choose "Keep Downloaded" (iCloud) or "Make available offline".`),
        el("button", { class: "btn small", type: "button", onclick: () => ctx.download() }, "Download now")) : null,
      option("laptop", "Only this Mac", "Your notes stay on this computer.", local,
        local ? null : el("button", { class: "btn small", type: "button", onclick: async () => {
          const p = await ctx.pick("Choose a place on this Mac for the folder"); if (p) moveTo(p, "this Mac");
        } }, "Move to a place on this Mac…")),
      option("cloud", "This Mac + cloud", "Kept on this Mac and synced by your cloud app. The cloud only ever sees scrambled files.", !!s.cloud && !s.github,
        el("div", {}, cloudCards,
          el("button", { class: "btn small st-other", type: "button", onclick: async () => {
            const p = await ctx.pick("Choose any synced folder"); if (p) moveTo(p, "that folder");
          } }, "Other synced folder…"))),
      option("lock", "This Mac + private GitHub", "Kept on this Mac and in a private GitHub repo, in step every few seconds. GitHub only ever sees scrambled files. Best for notes and documents: files over 95 MB stay on this Mac.", !!s.github, githubBody),
      option("sparkle", "Cloud only", "Nothing kept on this Mac: the app talks to your cloud directly (Nextcloud, WebDAV, S3). Coming next.", false),
      el("div", { class: "st-note" }, "Moving locks the folder first, so only scrambled files move. You unlock it again after."),
      err,
      el("div", { class: "dlg-actions" }, el("button", { class: "btn", onclick: () => done(null) }, "Close")));
    return { card };
  });
}

// One AI panel with two tabs: Tasks (notes given to the AI, each with what to do) and Activity (what AI apps did).
// ctx.tasks: {path?, label(path), todo:[{id, path, ask, t, done, by, result}], give(ask) -> todo, set(id, done) -> todo,
//             remove(id) -> todo, load() -> todo, open(path)}   With path, a box on top gives that note.
// ctx.activity: {rows:[{t, ago, app, folderName, what, detail, path, undo, canUndo}], open(path), undo(row), fail(msg)}
export function openAIPanel(ctx, start = "tasks") {
  return modal((done) => {
    const tasks = tasksView(ctx.tasks, done), activity = activityView(ctx.activity, done);
    const views = { tasks, activity };
    const body = el("div", { class: "ai-body" });
    const tools = el("div", { class: "act-tools" });
    const tabs = el("div", { class: "seg", role: "tablist" });
    const show = (k) => {
      for (const b of tabs.children) { const on = b.dataset.k === k; b.classList.toggle("on", on); b.setAttribute("aria-selected", on); }
      body.replaceChildren(...views[k].body);
      tools.replaceChildren(...(views[k].tools || []));
      if (k === "tasks" && tasks.focus) tasks.focus.focus();
    };
    for (const [k, label] of [["tasks", "Tasks"], ["activity", "Activity"]]) {
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
    el("div", { class: "mf-hint" }, "Your AI works through these tasks when you ask it to, for example: \u201cDo my Phygital Memory tasks.\u201d Its changes can be undone from Activity."),
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
    const code = el("div", { class: "gh-code" }, "…");
    const line = el("div", { class: "dlg-sub" }, "Asking GitHub for a sign-in code…");
    const err = el("div", { class: "dlg-err" });
    const copy = el("button", { class: "btn small", type: "button", disabled: true,
      onclick: () => navigator.clipboard.writeText(code.textContent).then(() => { copy.textContent = "Copied"; }) }, "Copy code");
    const card = el("div", { class: "dlg gh-signin", role: "dialog" },
      el("div", { class: "dlg-title" }, "Sign in with GitHub"),
      line, code, el("div", { class: "gh-row" }, copy),
      el("div", { class: "mf-hint" }, "The app gets its own key from GitHub, kept in this Mac's Keychain. You can take it back any time on GitHub, under Settings › Applications."),
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
