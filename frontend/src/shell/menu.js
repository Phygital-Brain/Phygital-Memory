// Right-click / "more" menus. Items: {label, fn, cls, check, hint, sub: [items], node, sep}.
import { el } from "./dom.js";

let menuEl = null;
export function closeMenu() { if (menuEl) { menuEl.remove(); menuEl = null; } }
document.addEventListener("mousedown", (e) => { if (menuEl && !menuEl.contains(e.target)) closeMenu(); }, true);
document.addEventListener("keydown", (e) => { if (menuEl && e.key === "Escape") { e.stopPropagation(); closeMenu(); } }, true);
window.addEventListener("blur", closeMenu);

export function showMenu(items, x, y) {
  closeMenu();
  menuEl = el("div", { class: "menu", role: "menu" });
  document.body.append(menuEl);
  const place = () => {
    const w = menuEl.offsetWidth, h = menuEl.offsetHeight;
    menuEl.style.left = Math.max(8, Math.min(x, innerWidth - w - 8)) + "px";
    menuEl.style.top = Math.max(8, Math.min(y, innerHeight - h - 8)) + "px";
  };
  const draw = (list, back) => {
    const kids = [];
    if (back) kids.push(el("button", { class: "menu-item menu-back", onclick: () => draw(back.items, back.up) }, "‹ Back"), el("div", { class: "menu-sep" }));
    for (const it of list) {
      if (it.sep) { kids.push(el("div", { class: "menu-sep" })); continue; }
      if (it.node) { kids.push(it.node); continue; }
      kids.push(el("button", {
        class: "menu-item " + (it.cls || ""), role: "menuitem",
        onclick: () => { if (it.sub) draw(it.sub, { items: list, up: back }); else { closeMenu(); it.fn && it.fn(); } },
      }, el("span", { class: "mi-main" }, el("span", {}, it.label), it.hint ? el("span", { class: "mi-hint" }, it.hint) : null),
      it.check ? el("span", { class: "mi-check" }, "✓") : it.sub ? el("span", { class: "mi-check" }, "›") : null));
    }
    menuEl.replaceChildren(...kids);
    place();
  };
  draw(items, null);
}
