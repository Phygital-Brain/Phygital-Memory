# If something goes wrong

Find what you see, then follow the fix. Each part covers one place where things can fail.

## Installing and opening the app

**What you see (Mac):** macOS says the app "can't be opened because Apple cannot check it for malicious software", or that it is from an unidentified developer.
**Why:** the app is distributed free and is not code-signed or notarized by Apple.
**Fix:** right-click the app in Applications, choose **Open**, then **Open** again. If macOS only offers **Done**:

1. Click **Done** (not Move to Trash) on the warning.
2. Open **System Settings › Privacy & Security**.
3. Scroll down to the message about Phygital Memory and click **Open Anyway**.
4. Type your Mac password or use Touch ID, then open the app again.

You do this once for each version you install by hand.

**What you see (Windows):** "Windows protected your PC", with "Unknown publisher".
**Why:** SmartScreen warns about apps that are not code-signed. The Windows app is not code-signed yet.
**Fix:** click **More info**, then **Run anyway**.

**What you see (Linux):** the AppImage does not open, or says it needs FUSE.
**Why:** an AppImage needs FUSE to run.
**Fix:** install your system's FUSE 2 package (often called `libfuse2`), then open it again. Or use the `.deb` or `.rpm` instead.

**What you see (Windows):** the folder picker takes a few seconds to appear.
**Why:** Windows opens its folder picker slowly the first time.
**Fix:** wait about 10 seconds. If it still does not appear, look in the taskbar, and tell us in a [bug form](https://github.com/Phygital-Brain/Phygital-Memory/issues/new?template=bug_report.yml).

**What you see:** "Another program is using this app's port (8790). Quit it, then open Phygital Memory again."
**Why:** the app's local program needs port 8790 on your computer, and something else holds it. The app refuses to talk to a program on that port that cannot prove it is the app's own.
**Fix:** quit the other program. If you do not know which it is, restart your computer and open Phygital Memory first.

**What you see:** the window opens but stays blank, or says the program stopped.
**Why:** the local program could not start.
**Fix:** quit the app fully, wait a few seconds, and open it again. If it keeps happening, open a [bug form](https://github.com/Phygital-Brain/Phygital-Memory/issues/new?template=bug_report.yml) and say what you did right before. The app's error log, `engine.log` in the app folder (see [settings](settings.md#files-the-app-keeps)), helps too. Check it holds nothing private before you post it.

## Updates

**What you see:** the update didn't finish, or the app still shows the old version.
**Why:** the download or the install failed, for example because the connection dropped. When that happens, nothing changes.
**Fix:** nothing to do. The app tries again the next time you open it. You can also update by hand: see [updates](updates.md#update-by-hand).

## Unlocking

**What you see:** "Wrong password."
**Why:** the password does not fit this memory. Passwords are case sensitive.
**Fix:** try again. If you turned on Touch ID, use the Touch ID button instead.

**What you see:** "Too many wrong tries. Wait a minute."
**Why:** after 5 wrong tries the app pauses unlocking for a minute.
**Fix:** wait a minute, then try again with the right password.

**What you see:** you forgot the password.
**Fix:** use **Forgot it? Use your recovery key** on the unlock screen and type the 44 words. It lets you set a new password. If you have neither the password nor the recovery key, nobody can open that memory. An Open memory has no password, so this only applies to Encrypted ones.

**What you see (Mac):** "Touch ID didn't confirm. Use your password."
**Why:** the fingerprint did not match, or macOS has not allowed the app to read its Keychain item yet.
**Fix:** use your password. If macOS asks about the Keychain, type your Mac login password and choose **Always Allow**. After an app update macOS may ask again.

## Connecting your AI app

**What you see:** the AI app says the server failed to connect.
**Why:** the Phygital Memory app is not running, or the key is wrong.
**Fix:**

1. Open Phygital Memory and keep it open.
2. In **Settings › AI apps**, check the app is listed. If it is not, add it again. Each key is shown once, so make a new one.
3. Check the address is exactly `http://127.0.0.1:8790/mcp`.

**What you see:** "This AI app isn't connected. The person connects it in Phygital Memory: Settings › AI apps."
**Why:** the key does not match any app in the list (it was removed, or mistyped).
**Fix:** connect the app again from **Settings › AI apps**.

**What you see:** "No memory this app may use is unlocked."
**Why:** the memory is locked, hidden from AI, or this app was not given that memory.
**Fix:** unlock the memory in the app. In **Settings › AI apps**, check the app may reach it. An Encrypted memory marked **AI can't see this** is hidden from every app.

**What you see:** "This AI app may only read."
**Why:** you connected it as read only.
**Fix:** if you want edits, turn on **Allow edits** for that app in **Settings › AI apps**.

**What you see:** the AI cannot open a note and says it is private.
**Why:** the note or folder is **Private for AI**, or is a hidden file such as `.env`. The AI may open it only if you ask for it in the chat.
**Fix:** ask the AI for that note directly. Or remove the Private for AI mark from the folder's menu.

**What you see:** "old_text must appear exactly once in the note."
**Why:** the AI tried to change text that is not in the note, or that appears more than once.
**Fix:** ask the AI to read the note again and pick a longer piece of text. Nothing was changed.

**What you see:** Claude on the web or on your phone cannot connect.
**Why:** the door lives on your computer at `127.0.0.1`, which a website or phone cannot reach. This is not supported yet.
**Fix:** use Claude Code, Claude Desktop, Cursor or Codex on the computer. See [connect your AI app](connect-your-ai.md).

## Notes and search

**What you see:** search finds nothing, but you know the note exists.
**Why:** the memory is locked, the note is bigger than about 2 MB (those are not searched), or the note was newly added from outside the app.
**Fix:** unlock the memory. Wait a few seconds for changes from a cloud drive to be picked up. Search needs words that are in the note.

**What you see:** a note named like `Plan (1).md` or `Plan (shared copy).md` next to `Plan.md`.
**Why:** two devices or people changed the same lines, so the app kept both versions. It also makes an AI task so your AI can merge them.
**Fix:** open both, keep what you want, and delete the other.

**What you see:** "That change can't be undone any more."
**Why:** the app keeps the last 50 AI changes in memory only, and they are gone after you lock the memory or quit.
**Fix:** open the note's **Version history** and restore the version you want.

**What you see:** "The note changed after the AI's edit, so Undo would lose that work."
**Why:** Undo only goes ahead while the note is exactly as the AI left it.
**Fix:** use the note's **Version history** to pick what to keep. The AI's version is in it.

## Backups and cloud

**What you see:** the GitHub backup stops and says the repo turned public.
**Why:** the app only syncs to a private repo. If GitHub says the repo is public, it stops.
**Fix:** make the repo private again on GitHub, then turn the backup on again.

**What you see:** a file is listed as not backed up.
**Why:** GitHub does not take files over 95 MB in this backup.
**Fix:** that file stays on your computer. Use an S3 or R2 backup, or a backup file, for big files.

**What you see:** the GitHub backup says git is missing, or will not start.
**Why:** the GitHub backup uses your computer's own git, and it is not installed.
**Fix:** install git. Mac: install Apple's Command Line Tools (run `xcode-select --install` in Terminal). Windows: install Git for Windows. Linux: install the `git` package. Then turn the backup on again.

**What you see:** "WebDAV only" will not start.
**Why:** WebDAV only (nothing kept on the computer) shows the server as a folder through a system helper. It is built in on Mac, but Windows needs WinFsp and Linux needs FUSE.
**Fix:** Windows: install WinFsp, a free helper from `winfsp.dev`. Linux: install the `fuse3` package. Then try again.

**What you see:** WebDAV or S3 will not connect.
**Why:** the address, user name or password is wrong, or the server is down.
**Fix:** check the address starts with `https://` and try the connection again from **Storage and backup**.

**What you see (Mac):** "Sharing needs your sharing key from the Keychain, and macOS hasn't allowed it yet."
**Why:** macOS has not let the app read the key it keeps for sharing.
**Fix:** quit and reopen the app. When macOS asks, type your Mac login password and choose **Always Allow**.

## Sharing and linking a computer

**What you see:** the other person never gets in.
**Why:** an invite works once and for 7 days, and nothing goes to them until you press **Let in**.
**Fix:** check their request shows in the app and press **Let in**. Both computers must be online with the app open at the same time. Make a new invite if the old one ran out.

**What you see:** a shared change does not arrive.
**Why:** both computers must be online with the app open at the same time for changes to travel. Changes wait until both are on.
**Fix:** open the app on both computers and wait a few seconds.

## Still stuck?

Open a [Something doesn't work](https://github.com/Phygital-Brain/Phygital-Memory/issues/new?template=bug_report.yml) issue. Include the version, which kind of memory you use, your AI app, and the exact error. Leave out passwords, recovery words, keys and the contents of your notes. For a security problem, use the [private report](https://github.com/Phygital-Brain/Phygital-Memory/security/advisories/new) instead.
