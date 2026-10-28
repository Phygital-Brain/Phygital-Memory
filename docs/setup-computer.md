# Setup on your computer

For when you want to try Phygital Memory on a Mac, free, with any AI app. About 5 minutes.

## Before you start

- A Mac. The first builds are for Apple silicon. Windows and Linux are not supported yet.
- An AI app that can use MCP tools: Claude Code, Claude Desktop, Cursor or Codex. See [connect-your-ai.md](connect-your-ai.md).
- No other program using port 8790 on your Mac.

## 1. Get the app

Releases will come from the GitHub Releases page of this repository, with auto-update. There is no release yet, and the repository is private. Until there is one, a developer builds the `.dmg`:

```bash
bash rebuild.sh --install
```

You should see a `.dmg` made in `release/` and, with `--install`, the app replaced in Applications and reopened. The first build takes longer, because it fetches the build tools. You need `uv`, `npm`, Rust with `cargo tauri`, `syncthing` and `rclone`.

When a release exists: download the `.dmg`, open it, and drag **Phygital Memory** into **Applications**.

## 2. Open it the first time

The app is distributed free and is not notarized by Apple, so macOS asks you to allow it once.

1. Open **Phygital Memory** from Applications. macOS says it cannot check the app. Click **Done**.
2. Open **System Settings › Privacy & Security**.
3. Scroll down to the message about Phygital Memory and click **Open Anyway**.
4. Type your Mac password or use Touch ID, then open the app again.

You should see the setup page, **Set up your Phygital Memory**.

On Windows, when there is a Windows version, SmartScreen will show a warning once. Click **More info › Run anyway**.

## 3. Make your first memory

The setup page asks a few questions, one at a time. Each is only clicks, plus a name and, for Encrypted, a password.

1. **What should your AI call you?** Your name, and the language for folders and rules. Your notes stay in whatever language you write.
2. **What kind of memory?** Pick one. You cannot switch later.
   - **Open**: a normal folder. Any AI reads it, and your phone gets it through iCloud Drive, Dropbox or Google Drive.
   - **Encrypted**: locked with your password. Only the AI apps you allow get in, through this app. Not on phones yet.
3. **Name it and pick its place.** The name, and where to keep it: this Mac, a cloud folder the app found, WebDAV, or any other folder. For Encrypted, also a password of 8 or more characters, twice.
4. **Back it up?** A private GitHub repo now, or **Later**. You can change this any time in **Storage and backup**.
5. **What's this memory for?** Work, Personal, or both. This only decides which starter notes the app writes.

Press **Set it up**. The app makes the memory and writes folders, rules, today's note and a few About notes. You should see a list of folders appear, then "Your memory is ready".

> [!WARNING]
> For an Encrypted memory there is no way back in without the password. After setup, open **Settings** and write down or save the 44-word recovery key.

## 4. Connect your AI app

The next screen offers **Add to Claude Code** and **Download** (Claude Desktop). Another app: **Open**. Or press **Skip** and use [connect-your-ai.md](connect-your-ai.md) later.

The last screen gives you a message to copy and paste into your AI chat. It has your AI follow Phygital Brain's setup guide and finish the notes. It also waits on Home as an AI task.

## 5. Check it works

Ask your AI app: *"Run status from Phygital Memory."*

You should see your memory by name and how many notes it holds. For an Encrypted memory, it must be unlocked in the app first.

## 6. Make it safer (2 minutes)

- Leave **Allow edits** off for each AI app until you have seen it work.
- Give each app only the memories it needs.
- Mark sensitive folders **Private for AI** from their menu.
- Write down your recovery key and keep it offline.
- Turn on a backup in **Storage and backup**.

## Keep it running

Keep the app open for AI apps to reach your memories. An Open memory opens straight away when you switch to it. An Encrypted memory stays unlocked until you lock it or close the app. Closing the app asks first.

## Where things are

- Your notes: the folders you chose. The first memory defaults to `~/Phygital Memory`.
- The app's own information: `~/Library/Application Support/Phygital Memory`. See [settings.md](settings.md#files-the-app-keeps).
- Your secrets: the Mac's Keychain.

## Update

No release exists yet, so there is nothing to update. Releases will come from GitHub Releases with auto-update. See [updates.md](updates.md).

## Remove it

1. Quit Phygital Memory.
2. Drag the app out of Applications.
3. Delete `~/Library/Application Support/Phygital Memory`.
4. Open **Keychain Access** and delete the items whose names start with "Phygital Memory".
5. Your memory folders stay where they are. Delete them yourself if you no longer want the notes.

## Use it from your phone

There is no phone app. An **Open** memory kept in iCloud Drive, Dropbox or Google Drive shows up in your phone's files. AI apps on your phone that are connected to that cloud, or to a private GitHub backup, can read it. Encrypted memories are not on phones yet.

## What we tested

| What | Where | When |
|---|---|---|
| The test scripts in `core/tests/` (open and encrypted memories, the AI door, sharing, backups with offline stand-ins for WebDAV, S3 and GitHub) | A Mac, built from this repository | October 2026 |
| A real Finder drag, a real Touch ID unlock, a real Nextcloud server | Checked by hand | Not yet fully tested |
| Windows, Linux | Not tested | Not supported yet |
| Intel Macs | Not tested | Not supported yet |
| A clean Mac that never had the app | Not tested | Not yet |
