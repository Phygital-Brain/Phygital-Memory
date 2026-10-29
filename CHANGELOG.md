# Changelog

## Unreleased

- A new update key. Version 0.1.0 can't install the next version by itself: download it once from the Releases page, and updates are automatic again after that.
- A removed memory stays removed. Before, the default `~/Phygital Memory` came back on every start while its folder was still on disk.
- Removing a memory now also stops its GitHub and S3 backups. Before, its last backup kept uploading until the app restarted, and git's files for it stayed behind.
- Clearer descriptions for the AI tools: when to use each one, whether it only reads or needs Allow edits, and what comes back.

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
