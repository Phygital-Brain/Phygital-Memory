# Roadmap

What might come next. Nothing here is promised or has a date. If you want one of them, say so in an [issue](https://github.com/Phygital-Brain/Phygital-Memory/issues/new?template=question.yml), or help build it ([CONTRIBUTING.md](../CONTRIBUTING.md)).

## Done

- **Windows and Linux.** Built from the same code as the Mac app, on GitHub, from one tag.
- **Auto-update.** The app updates itself from the latest GitHub Release. See [updates.md](updates.md).

## Wanted

- **Windows: finish testing and fix known issues.** Waiting for a retest: **Show in folder** could stop the app's engine, the folder picker could open hidden, and the close button once did nothing.
- **Code signing for Mac and Windows.** It would remove the one-time **Open Anyway** step on a Mac and the "unknown publisher" warning on Windows.
- **Drop the Intel Mac build in a later release.** The Mac download is one file for Apple and Intel today.
- **Native speakers for the translations.** All 41 languages were made with AI and checked by a script. A person who reads them is worth more than any tool.
- **A security review of the whole app.** Planned.
- **An https address for the AI door.** The Claude app refuses sign-in pages that are not on https, so sign-in from it fails on the local address. For now, Claude connects with a key.
- **Shutting out someone you removed from a share.** Changing the memory's key so a removed person cannot read later changes is not built yet.
- **Unlinking a computer, and moving shares to a linked computer.** Not built yet.

## Maybe

- **Passkey unlock.** Replace the Mac-only Touch ID helper on every device. It needs a real web address and a signed app first.
- **A phone app.** Python does not run well on phones, so it would need the core rebuilt in Rust inside the same Tauri app. Encrypted memories are not on phones today.
- **Signed approvals for risky AI actions ("Ask me first").** Phygital Key receipts, so an AI could be made to ask before certain actions.
- **Phone access through a tunnel to your computer.** Never a server copy that unlocks your notes.

## Not planned

- **A hosted service run by us.** You keep your notes in your own folders and your own cloud.
- **Telemetry or accounts.** Nothing is collected.
- **Switching a memory between Open and Encrypted.** A lock that turns on and off was dropped as too hard: old plain copies stay in the cloud's history.
