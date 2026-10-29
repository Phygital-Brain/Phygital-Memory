#!/usr/bin/env node
// npx phygital-memory: downloads the latest Phygital Memory app from GitHub Releases and installs it,
// the same way as the one-line installs in the README. No dependencies.
"use strict";
const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const BASE = "https://github.com/Phygital-Brain/Phygital-Memory/releases/latest/download/";
const run = (cmd, args) => execFileSync(cmd, args, { stdio: "inherit" });
const has = (cmd) => { try { execFileSync("sh", ["-c", `command -v ${cmd}`], { stdio: "ignore" }); return true; } catch { return false; } };

async function download(name) {
  const file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "pm-")), name);
  console.log(`Downloading ${name}`);
  const res = await fetch(BASE + name);
  if (!res.ok) throw new Error(`Couldn't download ${name} (${res.status}).`);
  fs.writeFileSync(file, Buffer.from(await res.arrayBuffer()));
  return file;
}

async function main() {
  const arm = process.arch === "arm64";
  if (process.platform === "darwin") {
    const dmg = await download("Phygital-Memory-mac.dmg");
    const mount = fs.mkdtempSync(path.join(os.tmpdir(), "pm-mount-"));
    run("hdiutil", ["attach", "-nobrowse", "-quiet", "-mountpoint", mount, dmg]);
    try { run("cp", ["-R", path.join(mount, "Phygital Memory.app"), "/Applications/"]); }
    finally { run("hdiutil", ["detach", "-quiet", mount]); }
    console.log("Installed in Applications. The first time, right-click the app and choose Open.");
  } else if (process.platform === "win32") {
    const exe = await download("Phygital-Memory-windows-setup.exe");
    run(exe, ["/S"]);
    console.log("Installed. Open Phygital Memory from the Start menu.");
  } else if (process.platform === "linux") {
    if (has("apt")) {
      run("sudo", ["apt", "install", "-y", await download(`Phygital-Memory-linux-${arm ? "arm64" : "amd64"}.deb`)]);
    } else if (has("dnf") || has("zypper")) {
      const rpm = await download(`Phygital-Memory-linux-${arm ? "aarch64" : "x86_64"}.rpm`);
      run("sudo", has("dnf") ? ["dnf", "install", "-y", rpm] : ["zypper", "--non-interactive", "install", "--allow-unsigned-rpm", rpm]);
    } else {
      const app = await download(`Phygital-Memory-linux-${arm ? "aarch64" : "amd64"}.AppImage`);
      const dir = path.join(os.homedir(), ".local", "bin");
      fs.mkdirSync(dir, { recursive: true });
      const to = path.join(dir, "phygital-memory");
      fs.copyFileSync(app, to);
      fs.chmodSync(to, 0o755);
      console.log(`Installed as ${to}`);
      return;
    }
    console.log("Installed. Open Phygital Memory from your apps.");
  } else {
    throw new Error("Phygital Memory runs on Mac, Windows and Linux.");
  }
}

main().catch((e) => { console.error(e.message); process.exit(1); });
