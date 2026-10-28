# Changelog

## 0.1.0 (unreleased)

- First version of Phygital Memory for Mac. It keeps your notes as a memory your AI can use, in one of two kinds: **Open** (a plain folder any AI app can read, no password) or **Encrypted** (a Cryptomator format 8 vault, opened with your password or Touch ID).
- The app has an editor, search, version history for every note, a trash that keeps things for 7 days, a note graph, and a Finder view of an unlocked memory.
- AI apps reach your memories through one local door (an MCP server on your own Mac). Each app gets its own key, can be read only or allowed to edit, and sees only the memories you pick. Every AI change can be undone. 17 tools: search, read, write, move, trash, and your AI tasks.
- AI tasks: a hidden note in each memory (`.ai-tasks/AI tasks.md`, To do and Done) where you hand work to your AI. It is never shared.
- Backups to a private GitHub repo, a WebDAV server, Amazon S3 or Cloudflare R2, or one backup file. Encrypted memories are backed up as encrypted files.
- Sharing from Mac to Mac with no account and no cloud: a whole memory, one folder or one file, with Can edit or Can view. Link your own second Mac the same way.
- Make it a Phygital Brain: one setup page builds the folders, rules and first notes, connects an AI app, and leaves one AI task to finish the rest.
- The screens come in 41 languages. The translations were made with AI and checked by a script. Native speakers have not read them yet.
- Mac only for now. Windows and Linux versions are being ported from the same code. The repository is private and has no license yet.
