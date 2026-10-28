// First run: pick a password, then the app creates the locked folder (the password goes straight to the
// local program over stdin, never to disk).
const f = document.getElementById("f"), a = document.getElementById("a"), b = document.getElementById("b"), m = document.getElementById("m");
f.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (a.value !== b.value) { m.textContent = "The two passwords differ."; return; }
  if (a.value.length < 8) { m.textContent = "Use at least 8 characters."; return; }
  m.textContent = "Working…";
  try { await window.__TAURI__.core.invoke("create_vault", { password: a.value }); }
  catch (x) { m.textContent = String(x); }
});
