# Roadmap

What might come next. Nothing here is promised or has a date. If you want one of them, say so in an [issue](https://github.com/Phygital-Brain/Phygital-Memory/issues/new?template=question.yml), or help build it ([CONTRIBUTING.md](../CONTRIBUTING.md)).

## Done

- **Windows and Linux.** Built from the same code as the Mac app, on GitHub, from one tag. Windows retested by hand with 0.1.0.
- **Auto-update.** The app updates itself from the latest GitHub Release. See [updates.md](updates.md).
- **Open memories with the app closed.** An AI app can start the engine itself. See [connect-your-ai.md](connect-your-ai.md#two-ways-in).
- **Your own server.** The same app on a server you own, so the AI on your phone reaches your memories when the computer is off. See [server.md](server.md). Not tried on a real server yet.

## Wanted

- **Code signing for Mac and Windows.** It would remove the one-time **Open Anyway** step on a Mac and the "unknown publisher" warning on Windows.
- **Drop the Intel Mac build in a later release.** The Mac download is one file for Apple and Intel today.
- **Native speakers for the translations.** All 41 languages were made with AI and checked by a script. A person who reads them is worth more than any tool.
- **A security review of the whole app.** Planned.
- **An https address for the AI door.** Some AI agents refuse sign-in pages that are not on https, so sign-in from them fails on the local address. For now, they connect with a key.
- **Shutting out someone you removed from a share.** Changing the memory's key so a removed person cannot read later changes is not built yet.
- **Unlinking a computer, and moving shares to a linked computer.** Not built yet.

## Maybe

- **Passkey unlock.** Replace the Mac-only Touch ID helper on every device. It needs a real web address and a signed app first.
- **A phone app.** Python does not run well on phones, so it would need the core rebuilt in Rust inside the same Tauri app. Encrypted memories are not on phones today.
- **Signed approvals for risky AI actions ("Ask me first").** Phygital Key receipts, so an AI could be made to ask before certain actions.

## Not planned

- **A hosted service run by us.** You keep your notes in your own folders and your own cloud.
- **Telemetry or accounts.** Nothing is collected.
- **Switching a memory between Open and Encrypted.** A lock that turns on and off was dropped as too hard: old plain copies stay in the cloud's history.

## Not supported yet

- **A phone app.** The engine is Python, which does not run well on phones. An Open memory in a cloud folder still shows up in your phone's files.
- **Encrypted memories on phones.** They need the app to open, and there is no phone app.
- **Sign-in from agents that need https.** Some AI agents refuse sign-in pages that are not on https, and the door is a local address. Connect with a key instead.
- **Code signing.** The Mac and Windows downloads are not signed yet, so the first open needs one extra step.
- **Switching a memory between Open and Encrypted.** Old plain copies would stay in your cloud's history, so the app doesn't offer it.
- **Shutting a removed person out of later changes.** Changing a shared memory's key is not built yet.
- **The Finder view and Touch ID off the Mac.** Both are Mac only for now.
- **Dropbox, Google Drive and OneDrive on a server.** Their sync apps run on computers, not servers. A server can use WebDAV or Nextcloud today. iCloud Drive can't run on a Linux server.

