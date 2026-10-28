// "Set up your Phygital Memory": its own page over the app. Your name, then Work or Personal (or both). The app builds
// the same simple skeleton for everyone (folders, rules, basic About notes), adds the work parts for work, and hands
// the rest to your AI: one message to paste that has it follow Phygital Brain's own setup guide, always up to date.
// ctx: {api, language(), openAI(tab), done(), files()}.
import { el, icon, knot } from "./dom.js";
import { t } from "./i18n.js";
import { toastOk, toastErr } from "./toast.js";

// The cards' drawings: 24px grid, one stroke weight, like the app's own icons
const ART = {
  work: ["M4 8h16v11H4z", "M9 8V5h6v3", "M4 13h16"],
  personal: ["M4 11l8-7 8 7", "M6 9.5V20h12V9.5", "M12 17s-3-1.8-3-3.7a1.5 1.5 0 0 1 3-.6 1.5 1.5 0 0 1 3 .6c0 1.9-3 3.7-3 3.7z"],
};
const art = (name) => {
  const NS = "http://www.w3.org/2000/svg", s = document.createElementNS(NS, "svg");
  for (const [k, v] of Object.entries({ viewBox: "0 0 24 24", width: "56%", height: "56%", fill: "none", stroke: "currentColor",
    "stroke-width": 1.6, "stroke-linecap": "round", "stroke-linejoin": "round", "aria-hidden": "true" })) s.setAttribute(k, v);
  for (const d of ART[name] || []) { const p = document.createElementNS(NS, "path"); p.setAttribute("d", d); s.append(p); }
  return s;
};

// The one question: what the memory is for. Both is fine
const QUESTIONS = () => [
  { key: "use", q: t("What's this memory for?"), options: [
    ["work", t("Work"), t("Projects, clients, offers and the people you work with.")],
    ["personal", t("Personal"), t("Goals, habits, home, health and side projects.")]] },
];

// The basic About notes, to fill later (your AI does it with the setup guide). Work adds the business ones
function pages(name, work) {
  const TODO = t("To add.");
  const sec = (h) => `## ${h}\n\n${TODO}\n`;
  const page = (desc, tags, ...parts) => ({ desc, tags, body: parts.join("\n") });
  return {
    me: page(t("Who {0} is and how they want their agent to work.", name), ["working-style"], `${name}\n`,
      sec(t("What I do")), sec(t("How I want my agent to work"))),
    goals: page(t("{0}'s goals and priorities.", name), ["priorities"], sec(t("Right now"))),
    tools: page(t("The tools {0} uses and where things live.", name), ["stack"], `## ${t("Tools")}\n\n- Phygital Memory\n`),
    ...(work ? {
      business: page(t("What {0} does for work.", name), ["work"], sec(t("What I do")), sec(t("Who I work with"))),
      services: page(t("What {0} offers.", name), ["offers"], sec(t("Offers")), sec(t("Prices"))),
      customers: page(t("Who {0} works for and how they find each other.", name), ["audience"], sec(t("Who")), sec(t("How they find me"))),
      brand: page(t("{0}'s voice and tone.", name), ["voice"], sec(t("Voice"))),
      cv: page(t("{0}'s work history, education and press.", name), ["history"], sec(t("Work, education and press"))),
    } : {}),
  };
}

export function renderSetup(body, ctx) {
  const Q = QUESTIONS();
  const answers = Object.fromEntries(Q.map((q) => [q.key, []]));
  let name = "", lang = "en", at = 0;
  const total = 1 + Q.length;   // the name screen, then the question

  const bar = el("div", { class: "sp-bar", role: "progressbar", "aria-valuemin": 0, "aria-valuemax": total });
  const drawBar = (i) => {
    bar.setAttribute("aria-valuenow", i);
    bar.replaceChildren(...Array.from({ length: total }, (_, k) => el("span", { class: "sp-seg" + (k < i ? " done" : k === i ? " on" : "") })));
  };
  const stage = el("div", { class: "sp-stage" });
  const back = el("button", { class: "btn sp-back", type: "button", onclick: () => go(at - 1, -1) }, icon("back", 14, 2), t("Back"));
  const next = el("button", { class: "btn primary sp-next", type: "button", onclick: () => go(at + 1, 1) });
  const foot = el("div", { class: "sp-foot" }, back, el("span", { class: "sp-count" }), next);

  // Move to screen i with the page's one motion: the old screen lifts away, the new one rises in
  const go = (i, dir = 1) => {
    if (i < 0) return;
    if (i === 1 && !name.trim()) return;
    if (i >= total) return buildView();
    const old = stage.firstElementChild;
    const show = () => {
      at = i; drawBar(i);
      stage.replaceChildren(i === 0 ? nameView() : questionView(Q[i - 1]));
      stage.firstElementChild.classList.add(dir > 0 ? "in-up" : "in-down");
      back.hidden = i === 0;
      foot.querySelector(".sp-count").textContent = t("{0} of {1}", i + 1, total);
      refreshNext();
      (stage.querySelector("input, .sp-card") || next).focus({ preventScroll: true });
    };
    if (old && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
      old.classList.add(dir > 0 ? "out-up" : "out-down");
      setTimeout(show, 170);
    } else show();
  };
  const refreshNext = () => {
    if (at === 0) { next.textContent = t("Next"); next.disabled = !name.trim(); return; }
    const n = answers[Q[at - 1].key].length;
    next.textContent = at === total - 1 ? t("Set it up") : t("Next");
    next.disabled = !n;   // pick Work, Personal or both
  };

  // Screen 1: the name the AI uses, and the language of the folders and rules
  const nameView = () => {
    const input = el("input", { class: "sp-name", type: "text", value: name, maxlength: 60, autocomplete: "given-name",
      spellcheck: "false", "aria-label": t("Your name") });
    input.addEventListener("input", () => { name = input.value; refreshNext(); });
    input.addEventListener("keydown", (e) => { if (e.key === "Enter" && name.trim()) go(1, 1); });
    const langRow = el("div", { class: "sp-langs", role: "radiogroup", "aria-label": t("Language") });
    const other = el("select", { class: "set-select sp-other hidden", "aria-label": t("Other language") });
    other.addEventListener("change", () => { lang = other.value; });
    ctx.api("brainlanguages").then((j) => {
      if (!name && j.name) { name = j.name; input.value = name; input.select(); refreshNext(); }
      const all = j.languages || [["en", "English"]];
      const title = (c) => (all.find(([x]) => x === c) || [])[1];
      const fit = (want) => (all.find(([c]) => c.toLowerCase() === want.toLowerCase()) || all.find(([c]) => c.split("-")[0] === want.split("-")[0].toLowerCase()) || [])[0];
      const app = fit(ctx.language()), mac = fit(navigator.language || "en");
      other.replaceChildren(...all.map(([c, n]) => el("option", { value: c }, n)));
      const choices = [];
      if (app) choices.push(["app", t("App language ({0})", title(app)), app]);
      if (mac && mac !== app) choices.push(["mac", t("Mac language ({0})", title(mac)), mac]);
      choices.push(["other", t("Other"), null]);
      let picked = choices.find(([, , c]) => c === lang)?.[0] || choices[0][0];
      lang = choices.find(([k]) => k === picked)[2] || lang;
      other.value = lang;
      const draw = () => langRow.replaceChildren(...choices.map(([k, text, code]) => el("button", {
        class: "sp-lang" + (k === picked ? " on" : ""), type: "button", role: "radio", "aria-checked": String(k === picked),
        onclick: () => { picked = k; other.classList.toggle("hidden", k !== "other"); lang = code || other.value; draw(); } },
        k === picked ? icon("check", 12, 2.4) : null, text)));
      draw();
    }).catch(() => {});
    return el("section", { class: "sp-screen" },
      el("h2", { class: "sp-q" }, t("What should your AI call you?")),
      el("p", { class: "sp-hint" }, t("This is the name from your Mac. Change it if you like.")),
      input,
      el("h3", { class: "sp-sub" }, t("Language for folders and rules")),
      langRow, other,
      el("p", { class: "sp-hint" }, t("Your notes stay in whatever language you write.")));
  };

  // A question: cards with a drawing, a name and a line. Click or press its number to pick; many are fine
  const questionView = (q) => {
    const n = q.options.length;   // rows that come out even: 2 and 4 in twos, 5 and 6 in threes, 7 as 4+3
    const grid = el("div", { class: `sp-grid c${n <= 2 || n === 4 ? 2 : n <= 6 ? 3 : 4}` + (q.agent ? " agent" : ""), role: "group", "aria-label": q.q });
    q.options.forEach(([v, label, desc], k) => {
      const on = () => answers[q.key].includes(v);
      const card = el("button", { class: "sp-card" + (on() ? " on" : ""), type: "button", role: "checkbox", "aria-checked": String(on()),
        style: `--i:${k}`,
        onclick: (e) => {
          const list = answers[q.key];
          if (on()) list.splice(list.indexOf(v), 1);
          else {
            if (v === "solo") list.length = 0;   // "mostly on my own" stands alone
            else if (list.includes("solo")) list.splice(list.indexOf("solo"), 1);
            list.push(v);
          }
          grid.querySelectorAll(".sp-card").forEach((c, j) => {
            const yes = answers[q.key].includes(q.options[j][0]);
            c.classList.toggle("on", yes); c.setAttribute("aria-checked", String(yes));
          });
          const r = card.getBoundingClientRect();   // the pick spreads from where it was touched
          card.style.setProperty("--x", `${(e.clientX || r.left + r.width / 2) - r.left}px`);
          card.style.setProperty("--y", `${(e.clientY || r.top + r.height / 2) - r.top}px`);
          card.classList.remove("pop"); void card.offsetWidth; card.classList.add("pop");
          refreshNext();
        } },
        el("span", { class: "sp-art" }, art(v)),
        el("span", { class: "sp-text" }, el("span", { class: "sp-label" }, label), el("span", { class: "sp-desc" }, desc)),
        el("span", { class: "sp-tick" }, icon("check", 12, 2.6)),
        el("kbd", { class: "sp-key" }, String(k + 1)));
      grid.append(card);
    });
    return el("section", { class: "sp-screen" },
      el("h2", { class: "sp-q" }, q.q),
      el("p", { class: "sp-hint" }, t("Pick one or both.")),
      grid);
  };

  // Making it: every folder rolls in while the app writes the rules and About pages
  let ask = "";   // the message for the AI, made by the engine with this memory's name
  const buildView = () => {
    drawBar(total); foot.hidden = true;
    const list = el("ul", { class: "sp-build", "aria-live": "polite" });
    const status = el("h2", { class: "sp-q" }, t("Setting up your memory"));
    const nextBtn = el("button", { class: "btn primary", type: "button", disabled: true, onclick: () => connectView() }, t("Next"));
    const work = answers.use.includes("work"), personal = answers.use.includes("personal");
    const choice = { work, personal, pages: pages(name.trim(), work) };
    stage.replaceChildren(el("section", { class: "sp-screen in-up" }, status, list, el("div", { class: "sp-end" }, nextBtn)));
    (async () => {
      try {
        const plan = (await ctx.api("brainplan", { picks: choice, lang })).folders || [];
        const built = ctx.api("brainbuild", { picks: choice, lang, name: name.trim(), tz: Intl.DateTimeFormat().resolvedOptions().timeZone });
        for (const [i, f] of plan.entries()) {   // a quick roll call: the making itself takes about a second
          await new Promise((r) => setTimeout(r, i ? 55 : 0));
          list.append(el("li", { class: "sp-row" }, icon("folder", 14), el("span", {}, f)));
        }
        const j = await built;
        if (j.error) throw new Error(j.error);
        ask = j.ask || "";
        list.append(el("li", { class: "sp-row sp-done" }, icon("check", 14, 2.4), el("span", {}, t("Rules, today's note and your About notes"))));
        status.textContent = t("Your memory is ready: {0} folders and notes.", (j.made || []).length + plan.length);
        nextBtn.disabled = false; nextBtn.focus();
        ctx.files();
      } catch (e) { status.textContent = e.message; toastErr(e.message); }
    })();
  };

  // Connect an AI, or skip: it only has the projects and people left to ask about
  const connectView = () => {
    const out = el("div", { class: "sp-ok", "aria-live": "polite" });
    const key = async (n, kind) => (await ctx.api("aiappadd", { name: n, kind, folders: "all", write: true })).key;
    const tick = (text) => out.replaceChildren(icon("check", 14, 2.4), text);
    const way = (title, hint, btn, fn) => el("div", { class: "sp-way" },
      el("div", {}, el("div", { class: "sp-label" }, title), el("div", { class: "sp-desc" }, hint)),
      el("button", { class: "btn", type: "button", onclick: async (e) => {
        const b = e.currentTarget; b.disabled = true;
        try { await fn(); } catch (x) { toastErr(x.message); }
        b.disabled = false;
      } }, btn));
    const already = el("p", { class: "sp-hint" });
    ctx.api("aiapps").then((j) => { if ((j.apps || []).length) already.textContent = t("Already connected: {0}.", j.apps.map((a) => a.name).join(", ")); }).catch(() => {});
    stage.replaceChildren(el("section", { class: "sp-screen in-up" },
      el("h2", { class: "sp-q" }, t("Connect your AI")),
      el("p", { class: "sp-hint" }, t("It finishes the setup with you. Or skip and do it later.")),
      already,
      way("Claude Code", t("Adds it for you."), t("Add to Claude Code"), async () => {
        const r = await ctx.api("claudecodeadd", { key: await key("Claude Code", "claude-code") });
        if (!r.ok) throw new Error(r.error || t("Claude Code isn't on this Mac."));
        tick(t("Claude Code is connected."));
      }),
      way("Claude Desktop", t("Saves an extension in Downloads. Double-click it, then paste the key it asks for."), t("Download"), async () => {
        const k = await key("Claude Desktop", "claude-desktop");
        await ctx.api("claudedesktopext");
        await navigator.clipboard.writeText(k).catch(() => {});
        tick(t("Saved in Downloads. Your key is copied: paste it when Claude Desktop asks."));
      }),
      way(t("Another AI app"), t("Codex, Cursor and others: the AI window has the setup."), t("Open"), async () => ctx.openAI("apps")),
      out,
      el("div", { class: "sp-end" },
        el("button", { class: "btn", type: "button", onclick: finishView }, t("Skip")),
        el("button", { class: "btn primary", type: "button", onclick: finishView }, t("Next")))));
  };

  const finishView = () => {
    const copy = el("button", { class: "btn primary", type: "button", onclick: async () => {
      await navigator.clipboard.writeText(ask).catch(() => {});
      copy.textContent = t("Copied"); toastOk(t("Paste it in your AI chat."));
    } }, icon("file", 14), t("Copy"));
    stage.replaceChildren(el("section", { class: "sp-screen in-up" },
      el("h2", { class: "sp-q" }, t("Copy this to your AI")),
      el("p", { class: "sp-hint" }, t("Your AI follows the Phygital Brain setup and fills in the rest.")),
      el("div", { class: "sp-say" }, el("pre", { class: "sp-msg" }, ask), copy),
      el("p", { class: "sp-hint" }, t("It also waits on Home as a task for your AI.")),
      el("div", { class: "sp-end" }, el("button", { class: "btn", type: "button", onclick: () => ctx.done() }, t("Open my memory")))));
  };

  // Keys: 1-9 or Space pick a card, Enter goes on, Escape goes back
  body.addEventListener("keydown", (e) => {
    if (foot.hidden || e.metaKey || e.ctrlKey || e.altKey || e.target.matches("input, textarea, select")) return;
    if (at > 0 && /^[1-9]$/.test(e.key)) { stage.querySelectorAll(".sp-card")[+e.key - 1]?.click(); e.preventDefault(); }
    else if (e.key === "Enter" && at > 0 && (!e.target.closest("button") || e.target.closest(".sp-card"))) { next.click(); e.preventDefault(); }
    else if (e.key === "Escape" && at > 0) { go(at - 1, -1); e.preventDefault(); }
  });

  body.replaceChildren(el("div", { class: "sp" },
    el("div", { class: "win-drag-top", "data-tauri-drag-region": "" }),
    el("header", { class: "sp-head" }, knot(28), el("h1", { class: "sp-title" }, t("Set up your Phygital Memory")),
      el("button", { class: "icon-btn sp-close", type: "button", title: t("Not now"), "aria-label": t("Not now"), onclick: () => ctx.done() }, icon("x", 16))),
    bar, stage, foot));
  go(0);
}
