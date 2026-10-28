// "Set up your Phygital Memory": its own page over the app. One question a screen, every answer a card, more than one
// always allowed. The app then makes every folder, rule and About page from the answers, so the AI only asks what
// needs a conversation (projects and people by name, the "To add" lines). ctx: {api, language(), openAI(tab), done(), files()}.
import { el, icon, knot } from "./dom.js";
import { t } from "./i18n.js";
import { toastOk, toastErr } from "./toast.js";

// The cards' drawings: 24px grid, one stroke weight, like the app's own icons
const ART = {
  freelance: ["M4 20l4-1 11-11-3-3L5 16z", "M14 7l3 3", "M4 20h16"],
  business: ["M4 10h16l-1.5-5h-13z", "M5 10v10h14V10", "M10 20v-5h4v5", "M4 10c0 1.7 1.8 2.5 4 2.5S12 11.7 12 10c0 1.7 1.8 2.5 4 2.5s4-.8 4-2.5"],
  company: ["M4 8h16v11H4z", "M9 8V5h6v3", "M4 13h16"],
  study: ["M2 9l10-5 10 5-10 5z", "M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5", "M21 9v6"],
  personal: ["M4 11l8-7 8 7", "M6 9.5V20h12V9.5", "M12 17s-3-1.8-3-3.7a1.5 1.5 0 0 1 3-.6 1.5 1.5 0 0 1 3 .6c0 1.9-3 3.7-3 3.7z"],
  design: ["M4 4h7v7H4z", "M17.5 4a3.5 3.5 0 1 1 0 7 3.5 3.5 0 0 1 0-7z", "M7.5 14L11 20H4z", "M14 14h6v6h-6z"],
  tech: ["M8 7l-5 5 5 5", "M16 7l5 5-5 5", "M13.5 5l-3 14"],
  strategy: ["M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18z", "M15.5 8.5l-2 5-5 2 2-5z"],
  writing: ["M4 6h10", "M4 10h7", "M4 14h5", "M13 20l1-4 6-6 3 3-6 6z"],
  care: ["M8 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M2.5 20c.5-3.5 2.8-5.5 5.5-5.5s5 2 5.5 5.5", "M16.5 11a2.5 2.5 0 1 0 0-5", "M16 14.5c3 0 5 2 5.5 5.5"],
  craft: ["M14 4l6 6-3 3-6-6z", "M11 7L3 15l3 3 8-8", "M15 20h6"],
  numbers: ["M4 20V10", "M10 20V4", "M16 20v-7", "M3 20h18"],
  clients: ["M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z", "M3 20c.6-3.8 3-6 6-6 1.6 0 3 .6 4 1.7", "M15 18l2 2 4-4.5"],
  collaborators: ["M9 6a6 6 0 1 1 0 12A6 6 0 0 1 9 6z", "M15 6a6 6 0 1 1 0 12 6 6 0 0 1 0-12z"],
  team: ["M12 9a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z", "M5 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z", "M19 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z", "M7.5 19c.4-3.4 2.2-6 4.5-6s4.1 2.6 4.5 6", "M2 19c.3-2.5 1.5-4.3 3-4.3", "M22 19c-.3-2.5-1.5-4.3-3-4.3"],
  partners: ["M4 10v4h3l7 4V6l-7 4z", "M18 9a4 4 0 0 1 0 6", "M7 14l1 5h2.5l-1-4.4"],
  solo: ["M12 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z", "M5 20c.7-4 3.6-6.5 7-6.5s6.3 2.5 7 6.5"],
  target: ["M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18z", "M12 7.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9z", "M12 11.2a.8.8 0 1 1 0 1.6.8.8 0 0 1 0-1.6z"],
  name: ["M12 3l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 16.4 6.7 19.4l1.2-6L3.4 9.3l6-.7z"],
  money: ["M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18z", "M14.8 9c-.4-1-1.5-1.6-2.8-1.6-1.6 0-2.8.9-2.8 2.1 0 2.8 5.8 1.4 5.8 4.4 0 1.2-1.3 2.1-3 2.1-1.4 0-2.6-.7-3-1.7", "M12 6v1.4", "M12 16.6V18"],
  time: ["M6 3h12", "M6 21h12", "M7 3c0 5 10 5 10 9s-10 4-10 9", "M17 3c0 5-10 5-10 9s10 4 10 9"],
  learn: ["M3 5.5c3-1.3 6-1.3 9 .5 3-1.8 6-1.8 9-.5V19c-3-1.3-6-1.3-9 .5-3-1.8-6-1.8-9-.5z", "M12 6v13.5"],
  finish: ["M5 21V4", "M5 4h12l-2.5 4L17 12H5"],
  health: ["M12 20s-8-4.6-8-10.2A4.3 4.3 0 0 1 12 7.5a4.3 4.3 0 0 1 8 2.3C20 15.4 12 20 12 20z", "M7 12h2.5l1.5-2.5 2 5 1.5-2.5H17"],
  switching: ["M4 8h13", "M14 5l3 3-3 3", "M20 16H7", "M10 13l-3 3 3 3"],
  admin: ["M3 6h18v12H3z", "M3 6l9 7 9-7"],
  payments: ["M6 3h12v18l-2-1.5-2 1.5-2-1.5-2 1.5-2-1.5L6 21z", "M9 8h6", "M9 12h6", "M9 16h3"],
  ideas: ["M12 12a2 2 0 1 0 0-.01", "M5 6a1.5 1.5 0 1 0 0-.01", "M19 5a1.5 1.5 0 1 0 0-.01", "M4 17a1.5 1.5 0 1 0 0-.01", "M19 18a1.5 1.5 0 1 0 0-.01", "M6 7l4.5 3.5", "M17.8 6.2l-4.4 4.4", "M5.2 16.2l5-3", "M17.8 17l-4.4-3.6"],
  finding: ["M10.5 4a6.5 6.5 0 1 1 0 13 6.5 6.5 0 0 1 0-13z", "M15.5 15.5L21 21"],
  alone: ["M12 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M6.5 19c.6-3.3 2.8-5.3 5.5-5.3s4.9 2 5.5 5.3", "M3 12a9 9 0 0 1 2.6-6.4", "M18.4 5.6A9 9 0 0 1 21 12"],
  deadlines: ["M12 6a7.5 7.5 0 1 1 0 15 7.5 7.5 0 0 1 0-15z", "M12 9.5v4l2.5 1.5", "M3.5 6L7 3", "M20.5 6L17 3"],
  day: ["M12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8z", "M12 2v2", "M12 20v2", "M4.2 4.2l1.4 1.4", "M18.4 18.4l1.4 1.4", "M2 12h2", "M20 12h2", "M4.2 19.8l1.4-1.4", "M18.4 5.6l1.4-1.4"],
  early: ["M3 18h18", "M7 18a5 5 0 0 1 10 0", "M12 6v3", "M5 10.5l1.8 1.3", "M19 10.5l-1.8 1.3", "M8 21h8"],
  evening: ["M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"],
  weekend: ["M4 5h16v15H4z", "M4 9h16", "M8 3v4", "M16 3v4", "M14 13h3v3h-3z"],
  anytime: ["M7 9c-3 0-4.5 1.5-4.5 3S4 15 7 15c4 0 6-6 10-6 3 0 4.5 1.5 4.5 3S20 15 17 15c-4 0-6-6-10-6z"],
  brief: ["M3 15h18", "M7 15a5 5 0 0 1 10 0", "M12 4v3", "M6 19h12", "M9 22h6"],
  meetings: ["M4 5h16v11H9l-5 4z", "M8 9h8", "M8 12h5"],
  voice: ["M9 3h6v9a3 3 0 0 1-6 0z", "M5.5 11a6.5 6.5 0 0 0 13 0", "M12 17.5V21"],
  import: ["M12 3v11", "M8 10l4 4 4-4", "M4 15v4h16v-4"],
  tidy: ["M15 3l-4.5 9", "M7 12h8l1.5 9h-11z", "M9 16v5", "M12 16v5"],
  think: ["M9 18h6", "M10 21h4", "M12 3a6 6 0 0 1 3.6 10.8c-.7.6-1.1 1.4-1.1 2.2h-5c0-.8-.4-1.6-1.1-2.2A6 6 0 0 1 12 3z"],
  short: ["M4 8h10", "M4 12h7", "M4 16h12"],
  detailed: ["M4 5h16", "M4 9h16", "M4 13h16", "M4 17h16", "M4 21h10"],
  friendly: ["M12 3a9 9 0 1 1 0 18 9 9 0 0 1 0-18z", "M8.5 14c.8 1.4 2 2 3.5 2s2.7-.6 3.5-2", "M9 9.5v.5", "M15 9.5v.5"],
  formal: ["M12 3l3 3-1.5 2 2 10L12 21l-3.5-3 2-10L9 6z"],
  direct: ["M3 12h16", "M14 6l6 6-6 6"],
};
const art = (name) => {
  const NS = "http://www.w3.org/2000/svg", s = document.createElementNS(NS, "svg");
  for (const [k, v] of Object.entries({ viewBox: "0 0 24 24", width: "56%", height: "56%", fill: "none", stroke: "currentColor",
    "stroke-width": 1.6, "stroke-linecap": "round", "stroke-linejoin": "round", "aria-hidden": "true" })) s.setAttribute(k, v);
  for (const d of ART[name] || []) { const p = document.createElementNS(NS, "path"); p.setAttribute("d", d); s.append(p); }
  return s;
};

// The questions. [key, title, description]; every answer can be one or many, or none (then the button says Skip)
const QUESTIONS = () => [
  { key: "work", q: t("What do you do?"), options: [
    ["freelance", t("Freelance or creative"), t("You take on projects for clients.")],
    ["business", t("I run a business"), t("A shop, studio or company of your own.")],
    ["company", t("I work for a company"), t("A job with a team and a manager.")],
    ["study", t("I study"), t("Courses, research, exams.")],
    ["personal", t("My own life and projects"), t("Home, health, hobbies, side projects.")]] },
  { key: "strengths", q: t("What are you good at?"), options: [
    ["design", t("Design and visuals"), t("Images, layout, look and feel.")],
    ["tech", t("Tech and building"), t("Code, tools, making things work.")],
    ["strategy", t("Strategy and ideas"), t("Seeing the plan and finding the angle.")],
    ["writing", t("Writing and stories"), t("Words people read to the end.")],
    ["care", t("People and care"), t("Teaching, helping, bringing people together.")],
    ["craft", t("Making by hand"), t("Objects, food, things you can touch.")],
    ["numbers", t("Numbers and order"), t("Money, data, keeping things on track.")]] },
  { key: "people", q: t("Who do you work with?"), options: [
    ["clients", t("Clients"), t("People and companies you deliver work for.")],
    ["collaborators", t("Collaborators"), t("Partners in the work, no money changing hands.")],
    ["team", t("A team"), t("People who work with or for you.")],
    ["partners", t("Press and partners"), t("Venues, platforms and press you show up with.")],
    ["solo", t("Mostly on my own"), t("Fewer people to keep track of.")]] },
  { key: "goals", q: t("What do you want most right now?"), options: [
    ["target", t("More and better clients"), t("Work you want, from people who value it.")],
    ["name", t("Grow my name"), t("Be known for what you make.")],
    ["money", t("Earn more"), t("Better prices, steadier income.")],
    ["time", t("Time and balance"), t("Room to rest and think.")],
    ["learn", t("Learn something new"), t("A skill, a field, a language.")],
    ["finish", t("Finish what I started"), t("Close the open loops.")],
    ["health", t("Health and energy"), t("Sleep, body, steady days.")]] },
  { key: "drains", q: t("What drains you?"), options: [
    ["switching", t("Switching between things"), t("Losing the thread every time.")],
    ["admin", t("Admin and email"), t("The inbox that never ends.")],
    ["payments", t("Chasing payments"), t("Invoices, reminders, waiting.")],
    ["ideas", t("Too many ideas"), t("Starting more than you finish.")],
    ["finding", t("Finding new work"), t("Where the next project comes from.")],
    ["alone", t("Working alone"), t("No one to think out loud with.")],
    ["deadlines", t("Deadlines"), t("Everything due at once.")]] },
  { key: "hours", q: t("When do you work?"), options: [
    ["early", t("Early mornings"), t("Before the day gets loud.")],
    ["day", t("Weekdays, daytime"), t("Monday to Friday, office hours.")],
    ["evening", t("Evenings"), t("When the house is quiet.")],
    ["weekend", t("Weekends"), t("Saturday and Sunday too.")],
    ["anytime", t("Whenever it fits"), t("No fixed hours.")]] },
  { key: "help", q: t("What should your AI help with?"), agent: true, options: [
    ["brief", t("A morning brief"), t("Today's plan in a few lines, when you ask.")],
    ["meetings", t("Meeting prep"), t("A short brief before each call.")],
    ["voice", t("Writing in my voice"), t("Drafts that sound like you, checked for AI patterns.")],
    ["import", t("Bring in old notes"), t("From other apps, with a plan you approve first.")],
    ["tidy", t("A daily tidy"), t("Fixes small things, asks before big ones.")],
    ["think", t("Thinking partner"), t("Challenges ideas, finds patterns in your notes.")]] },
  { key: "talk", q: t("How should your AI talk to you?"), agent: true, options: [
    ["short", t("Short and plain"), t("A few sentences, everyday words.")],
    ["detailed", t("Detailed"), t("The full reasoning, step by step.")],
    ["friendly", t("Warm and friendly"), t("Like a friendly colleague.")],
    ["formal", t("Formal"), t("Polite and careful.")],
    ["direct", t("Tell me when I'm wrong"), t("Honest pushback, no flattery.")]] },
];

// The About pages, written now from the answers. "To add" marks what only the person or their AI can say.
function pages(name, a, Q) {
  const TODO = t("To add.");
  const pick = (key) => { const q = Q.find((x) => x.key === key); return q.options.filter(([v]) => a[key].includes(v)); };
  const list = (key, withDesc) => pick(key).map(([, l, d]) => `- ${l}${withDesc ? `: ${d.charAt(0).toLowerCase()}${d.slice(1)}` : ""}`).join("\n") || TODO;
  const sec = (h, body) => `## ${h}\n\n${body}\n`;
  const page = (desc, tags, ...parts) => ({ desc, tags, body: parts.join("\n") });
  return {
    me: page(t("Who {0} is and how they want their agent to work.", name), ["working-style"],
      `${name}\n`,
      sec(t("What I do"), list("work")),
      sec(t("What I'm good at"), list("strengths", true)),
      sec(t("When I work"), list("hours")),
      sec(t("What drains me"), list("drains")),
      sec(t("What my AI helps with"), list("help")),
      sec(t("How I want my agent to work"), list("talk", true)),
      sec(t("Life and background"), TODO)),
    goals: page(t("{0}'s goals and priorities.", name), ["priorities"], sec(t("Right now"), list("goals")), sec(t("This year"), TODO)),
    business: page(t("What {0} does for work.", name), ["work"],
      sec(t("What I do"), list("work")), sec(t("Who I work with"), list("people")), sec(t("Current projects"), TODO)),
    services: page(t("What {0} offers.", name), ["offers"],
      sec(t("Built on"), list("strengths", false)), sec(t("Offers"), TODO), sec(t("Prices"), TODO)),
    customers: page(t("Who {0} works for and how they find each other.", name), ["audience"],
      sec(t("Who"), a.people.includes("clients") ? t("Clients: people and companies {0} delivers work for.", name) : TODO),
      sec(t("How they find me"), TODO)),
    "pain-points": page(t("The problems {0} wants solved.", name), ["problems"], sec(t("What gets in the way"), list("drains"))),
    brand: page(t("{0}'s voice and tone.", name), ["voice"], sec(t("Voice"), TODO), sec(t("Words to use"), TODO), sec(t("Words to avoid"), TODO)),
    tools: page(t("The tools {0} uses and where things live.", name), ["stack"], sec(t("Tools"), t("Phygital Memory for notes.")), sec(t("Where things live"), TODO)),
    cv: page(t("{0}'s work history, education and press.", name), ["history"], sec(t("Work"), TODO), sec(t("Education"), TODO), sec(t("Press and awards"), TODO)),
    biography: page(t("{0}'s story.", name), ["story"], TODO),
  };
}

export function renderSetup(body, ctx) {
  const Q = QUESTIONS();
  const answers = Object.fromEntries(Q.map((q) => [q.key, []]));
  let name = "", lang = "en", at = 0;
  const total = Q.length + 1;   // the name screen, then the questions

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
    if (i > Q.length) return buildView();
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
    const q = Q[at - 1], n = answers[q.key].length;
    next.textContent = at === Q.length ? (n ? t("Set it up") : t("Skip and set it up")) : n ? t("Next") : t("Skip");
    next.disabled = false;
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
    const n = q.options.length;   // rows that come out even: 4 as 2+2, 5 and 6 as 3s, 7 as 4+3
    const grid = el("div", { class: `sp-grid c${n === 4 ? 2 : n <= 6 ? 3 : 4}` + (q.agent ? " agent" : ""), role: "group", "aria-label": q.q });
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
      el("p", { class: "sp-hint" }, t("Pick as many as fit.")),
      grid);
  };

  // Making it: every folder rolls in while the app writes the rules and About pages
  const buildView = () => {
    drawBar(total); foot.hidden = true;
    const list = el("ul", { class: "sp-build", "aria-live": "polite" });
    const status = el("h2", { class: "sp-q" }, t("Setting up your memory"));
    const nextBtn = el("button", { class: "btn primary", type: "button", disabled: true, onclick: () => connectView() }, t("Next"));
    const clients = answers.people.includes("clients") || answers.work.some((w) => w === "freelance" || w === "business");
    const choice = { clients, pages: pages(name.trim(), answers, Q) };
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
        list.append(el("li", { class: "sp-row sp-done" }, icon("check", 14, 2.4), el("span", {}, t("Rules, today's note and 10 About pages"))));
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
      el("p", { class: "sp-hint" }, t("It asks about your projects and people by name, then fills the lines marked To add. Or skip and do it later.")),
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
    const say = t("Do my Phygital Memory tasks.");
    const copy = el("button", { class: "btn primary", type: "button", onclick: async () => {
      await navigator.clipboard.writeText(say).catch(() => {});
      copy.textContent = t("Copied"); toastOk(t("Paste it in your AI chat."));
    } }, t("Copy"));
    stage.replaceChildren(el("section", { class: "sp-screen in-up" },
      el("h2", { class: "sp-q" }, t("Last step: tell your AI")),
      el("p", { class: "sp-hint" }, t("Paste this in your AI's chat. Its task already has your answers.")),
      el("div", { class: "sp-say" }, el("span", {}, say), copy),
      el("p", { class: "sp-hint" }, t("No AI yet? Your memory works already. The task waits on Home until you connect one.")),
      el("div", { class: "sp-end" }, el("button", { class: "btn primary", type: "button", onclick: () => ctx.done() }, t("Open my memory")))));
  };

  // Keys: 1-9 or Space pick a card, Enter goes on, Escape goes back
  body.addEventListener("keydown", (e) => {
    if (foot.hidden || e.metaKey || e.ctrlKey || e.altKey) return;
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
