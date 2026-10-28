// Toasts: small messages stacked bottom-right that fade away by themselves.
import { t } from "./i18n.js";
import { el } from "./dom.js";

let stack = null;
export function toast(text, tone = "neutral") {
  if (!stack || !stack.isConnected) { stack = el("div", { class: "toasts", "aria-live": "polite" }); document.body.append(stack); }
  const box = el("div", { class: "toast " + tone, role: tone === "error" ? "alert" : "status" },
    el("span", { class: "toast-dot" }), el("span", { class: "toast-text" }, text),
    el("button", { class: "toast-x", "aria-label": t("Dismiss"), onclick: () => kill() }, "×"));
  let timer = null;
  const kill = () => { clearTimeout(timer); box.classList.add("out"); setTimeout(() => box.remove(), 180); };
  stack.append(box);
  while (stack.children.length > 4) stack.firstChild.remove();
  timer = setTimeout(kill, tone === "error" ? 6000 : 3500);
}
export const toastOk = (text) => toast(text, "success");
export const toastErr = (text) => toast(text, "error");
