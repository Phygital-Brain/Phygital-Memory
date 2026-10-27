// Tiny DOM helpers. Text always goes in as text nodes, never as HTML.
export function el(tag, props = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (v == null || v === false) continue;
    if (k === "class") n.className = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (k === "value" || k === "checked" || k === "draggable") n[k] = v;
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const c of kids.flat()) if (c != null && c !== false) n.append(c.nodeType ? c : document.createTextNode(String(c)));
  return n;
}

const ICONS = {
  file: ["M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z", "M14 3v5h5"],
  folder: ["M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"],
  image: ["M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z", "M8.5 10a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z", "M21 15l-5-5L5 21"],
  plus: ["M12 5v14M5 12h14"],
  folderplus: ["M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z", "M12 10.5v5M9.5 13h5"],
  chevron: ["M9 6l6 6-6 6"],
  collapse: ["M7 20l5-5 5 5M7 4l5 5 5-5"],
  sort: ["M4 7h10M4 12h7M4 17h4M17 5v14M14 16l3 3 3-3"],
  more: ["M5 12h.01M12 12h.01M19 12h.01"],
  x: ["M6 6l12 12M18 6L6 18"],
  lock: ["M6 11h12v9H6z", "M8 11V8a4 4 0 0 1 8 0v3"],
  unlock: ["M6 11h12v9H6z", "M8 11V8a4 4 0 0 1 7.5-2"],
  cloud: ["M7 18h10a4 4 0 0 0 .5-8 6 6 0 0 0-11.5 1.5A3.3 3.3 0 0 0 7 18z"],
  laptop: ["M5 6h14v9H5z", "M3 18h18"],
  sparkle: ["M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z", "M19 16l.7 1.8 1.8.7-1.8.7L19 21l-.7-1.8-1.8-.7 1.8-.7z"],
  grid: ["M4 4h7v7H4z", "M13 4h7v7h-7z", "M4 13h7v7H4z", "M13 13h7v7h-7z"],
  key: ["M8 15a4 4 0 1 1 0-8 4 4 0 0 1 0 8z", "M12 11h9", "M18 11v3", "M15 11v2"],
  gear: ["M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"],
  clock: ["M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z", "M12 7v5l3 2"],
  graph: ["M9.5 12a2.5 2.5 0 1 0 5 0a2.5 2.5 0 1 0-5 0", "M3.4 5a1.6 1.6 0 1 0 3.2 0a1.6 1.6 0 1 0-3.2 0",
          "M17.4 6a1.6 1.6 0 1 0 3.2 0a1.6 1.6 0 1 0-3.2 0", "M3.4 18.5a1.6 1.6 0 1 0 3.2 0a1.6 1.6 0 1 0-3.2 0",
          "M17.4 18a1.6 1.6 0 1 0 3.2 0a1.6 1.6 0 1 0-3.2 0",
          "M10.2 10.2L6.1 6.1M13.9 10.4L17.8 7M10.2 13.7L6.2 17.4M13.9 13.6L17.8 17M19 7.6v8.8"],   // a small network, not a share sign
  home: ["M4 11l8-7 8 7", "M6 10v10h12V10", "M10 20v-5h4v5"],
  undo: ["M9 14L4 9l5-5", "M4 9h10.5a5.5 5.5 0 0 1 0 11H11"],
  redo: ["M15 14l5-5-5-5", "M20 9H9.5a5.5 5.5 0 0 0 0 11H13"],
  trash: ["M4 7h16", "M10 11v6M14 11v6", "M6 7l1 13h10l1-13", "M9 7V4h6v3"],
  pin: ["M9 4h6l-1 6 3 3H7l3-3z", "M12 13v7"],
  check: ["M5 12.5l4.5 4.5L19 7.5"],
  back: ["M15 6l-6 6 6 6"],
  updown: ["M8 9l4-4 4 4M8 15l4 4 4-4"],
  search: ["M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14z", "M21 21l-4.3-4.3"],
};

export function icon(name, size = 16, width = 1.7) {
  const NS = "http://www.w3.org/2000/svg";
  const s = document.createElementNS(NS, "svg");
  s.setAttribute("viewBox", "0 0 24 24");
  s.setAttribute("width", size);
  s.setAttribute("height", size);
  s.setAttribute("fill", "none");
  s.setAttribute("stroke", "currentColor");
  s.setAttribute("stroke-width", name === "more" ? 3 : width);
  s.setAttribute("stroke-linecap", "round");
  s.setAttribute("stroke-linejoin", "round");
  s.setAttribute("aria-hidden", "true");
  for (const d of ICONS[name] || []) {
    const p = document.createElementNS(NS, "path");
    p.setAttribute("d", d);
    s.append(p);
  }
  return s;
}
