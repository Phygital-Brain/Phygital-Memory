// Right-click / "more" menus. Items: {label, fn, cls, check, hint, value, dot, sub: [items], node, sep}.
// A submenu opens beside its row on hover (or click), like the Mac's own menus.
import { el } from "./dom.js";

let panels = [];   // the menu, then each open submenu
let closeTimer = null;
export function closeMenu() { clearTimeout(closeTimer); panels.forEach((p) => p.remove()); panels = []; }
document.addEventListener("mousedown", (e) => { if (panels.length && !panels.some((p) => p.contains(e.target))) closeMenu(); }, true);
document.addEventListener("keydown", (e) => { if (panels.length && e.key === "Escape") { e.stopPropagation(); closeMenu(); } }, true);
window.addEventListener("blur", closeMenu);

// Keep the panels up to `depth` (0 = only the menu itself) and close the rest.
function trim(depth) {
  panels.splice(depth + 1).forEach((p) => p.remove());
  panels[depth] && panels[depth].querySelectorAll(":scope > .menu-item.open").forEach((r) => r.classList.remove("open"));
}

function place(p, x, y, leftEdge) {
  const w = p.offsetWidth, h = p.offsetHeight;
  if (leftEdge != null && x + w > innerWidth - 8) x = leftEdge - w;   // no room on the right: open to the left
  p.style.left = Math.max(8, Math.min(x, innerWidth - w - 8)) + "px";
  p.style.top = Math.max(8, Math.min(y, innerHeight - h - 8)) + "px";
}

function panel(list, depth) {
  const p = el("div", { class: "menu" + (depth ? " menu-sub" : ""), role: "menu" });
  p.addEventListener("mouseenter", () => clearTimeout(closeTimer));
  for (const it of list) {
    if (it.sep) { p.append(el("div", { class: "menu-sep" })); continue; }
    if (it.node) { p.append(it.node); continue; }
    const row = el("button", { class: "menu-item " + (it.cls || ""), role: "menuitem", "aria-haspopup": it.sub ? "menu" : null },
      el("span", { class: "mi-main" }, el("span", {}, it.label), it.hint ? el("span", { class: "mi-hint" }, it.hint) : null),
      el("span", { class: "mi-end" },
        it.value ? el("span", { class: "mi-value" }, it.value) : null,
        it.dot ? el("span", { class: "mi-dot", style: `background:${it.dot}` }) : null,
        it.check ? el("span", { class: "mi-check" }, "✓") : it.sub ? el("span", { class: "mi-more" }, "›") : null));
    const open = () => {
      clearTimeout(closeTimer);
      trim(depth);
      if (!it.sub) return;
      row.classList.add("open");
      const sub = panel(it.sub, depth + 1);
      document.body.append(sub);
      panels.push(sub);
      const r = row.getBoundingClientRect();
      place(sub, r.right + 4, r.top - 5, r.left - 4);
    };
    row.addEventListener("mouseenter", open);
    row.addEventListener("mouseleave", () => { if (it.sub) closeTimer = setTimeout(() => trim(depth), 300); });
    row.addEventListener("click", () => { if (it.sub) open(); else { closeMenu(); it.fn && it.fn(); } });
    p.append(row);
  }
  return p;
}

export function showMenu(items, x, y) {
  closeMenu();
  const p = panel(items, 0);
  document.body.append(p);
  panels.push(p);
  place(p, x, y);
}
