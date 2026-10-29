# Changelog

## Unreleased

- `search_notes` takes an optional `inside`, like `Projects`: only notes in that subfolder come back.
- `status` shows a folder map that makes itself: each main folder, its note count, and the first line of its `README.md`, `AGENTS.md` or `CLAUDE.md` (or its recent notes). Private folders are counted, never described.

## 0.1.4 (2026-10-29)

- **Check for updates** in the Phygital Memory menu: it looks right away, and installs a new version or says you have the latest.
- Coloured labels written as `<span style="...">` (like the badges Obsidian shows) are drawn as labels. Click into one to edit its code.
- An AI agent connected to the app waits for it while it restarts, for an update say, instead of failing.

## 0.1.3 (2026-10-29)

- Home shows the two latest daily notes side by side, not only the newest.
- The Claude Code command the app shows, and its **Add to Claude Code for me** button, put the server's name first. Before, Claude Code read the name as part of the key setting and refused the command.

## 0.1.2 (2026-10-29)

- A tidier start screen: the three tags on one line, smaller New memory and Open memory buttons, and the language picker the same width.

## 0.1.1 (2026-10-29)

- AI agents can start Phygital Memory themselves. With the app closed, they reach your Open memories (search, read and, with Allow edits, write). With the app open, they go through it as before. The setup the app shows uses this when it can. See [docs/connect-your-ai.md](docs/connect-your-ai.md#two-ways-in).
- A new memory marks **Open** as Recommended, and a new guide, [Find your threat model](docs/find-your-threat-model.md), says who needs Encrypted.
- The start screen grows with the window, says what the app is (notes app, open source, encrypted when you want), and has two clear buttons: **New memory** and **Open memory**, with a tidier language picker.
- **AI › Connect an AI app**: its own window, like Link a computer, with a tab for AI agents on this computer and one for the web and phones, which shows the four ways in. A new guide, [Use it from your phone](docs/phone.md), has the steps.
- A new update key. Version 0.1.0 can't install the next version by itself: download it once from the Releases page, and updates are automatic again after that.
- A removed memory stays removed. Before, the default `~/Phygital Memory` came back on every start while its folder was still on disk.
- Removing a memory now also stops its GitHub and S3 backups. Before, its last backup kept uploading until the app restarted, and git's files for it stayed behind.
- Clearer descriptions for the AI tools: when to use each one, whether it only reads or needs Allow edits, and what comes back.
- Windows retested by hand with 0.1.0: Show in folder, the folder picker and the close button all work now. The docs no longer list them as known issues.

## 0.1.0 (2026-10-29)

- First version of Phygital Memory, for Mac, Windows and Linux. It keeps your notes as a memory your AI can use, in one of two kinds: **Open** (a plain folder any AI app can read, no password) or **Encrypted** (a Cryptomator format 8 vault, opened with your password, or Touch ID on a Mac).
- The app has an editor, search, version history for every note, a trash that keeps things for 7 days, a note graph, and a Finder view of an unlocked memory (Mac only for now).
- AI apps reach your memories through one local door (an MCP server on your own computer). Each app gets its own key, can be read only or allowed to edit, and sees only the memories you pick. Every AI change can be undone. 17 tools: search, read, write, move, trash, and your AI tasks.
- AI tasks: a hidden note in each memory (`.ai-tasks/AI tasks.md`, To do and Done) where you hand work to your AI. It is never shared.
- Backups to a private GitHub repo, a WebDAV server, Amazon S3 or Cloudflare R2, or one backup file. Encrypted memories are backed up as encrypted files.
- Sharing from computer to computer with no account and no cloud, through Syncthing: a whole memory, one folder or one file, with Can edit or Can view. Both computers must be online with the app open at the same time. Link your own second computer the same way.
- Make it a Phygital Brain: one setup page builds the folders, rules and first notes, connects an AI app, and leaves one AI task to finish the rest.
- The screens come in 41 languages. The translations were made with AI and checked by a script. Native speakers have not read them yet.
- Runs on Mac (one universal download for Apple and Intel), Windows (x64, and Windows on ARM through emulation) and Linux (x64 and ARM: `.deb`, `.rpm` and AppImage). Windows is built but not fully tested yet. The Mac and Windows downloads are not code-signed.
- Phygital Memory Server: the same app on your own server, with a passphrase login, and the AI door at your own https address, so AI apps on the web and on phones can connect, and a Docker image built with each release. It keeps in step with your computer through Link my computer or the same WebDAV storage. See [docs/server.md](docs/server.md).
- Updates itself from the latest GitHub Release. Updates are signed with the project's update key, so only real releases install.
- License: AGPL-3.0-only.
