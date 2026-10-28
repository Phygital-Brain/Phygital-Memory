# Roadmap

What might come next. Nothing here is promised or has a date. If you want one of them, say so in an [issue](https://github.com/Phygital-Brain/Phygital-Memory/issues/new?template=question.yml), or help build it ([CONTRIBUTING.md](../CONTRIBUTING.md)).

## Wanted

- **Windows and Linux.** The code is shared. Only a few pieces are Mac only: Touch ID and the Keychain, the folder pickers, Show in Finder, and the Mac's user name. Each is meant to be replaced by one small file per platform.
- **Releases from GitHub, with auto-update.** GitHub would build the Mac, Windows and Linux apps from one tag. Nothing builds on GitHub yet.
- **Tests on Windows and Linux.** On GitHub's own machines, and in virtual machines.
- **Native speakers for the translations.** All 41 languages were made with AI and checked by a script. A person who reads them is worth more than any tool.
- **A security review of the whole app.** Planned before a first release.
- **An https address for the AI door.** The Claude app refuses sign-in pages that are not on https, so sign-in from it fails on the local address. For now, Claude connects with a key.
- **Shutting out someone you removed from a share.** Changing the memory's key so a removed person cannot read later changes is not built yet.
- **Unlinking a Mac, and moving shares to a linked Mac.** Not built yet.

## Maybe

- **Passkey unlock.** Replace the Mac-only Touch ID helper on every device. It needs a real web address and a signed app first.
- **A phone app.** Python does not run well on phones, so it would need the core rebuilt in Rust inside the same Tauri app. Encrypted memories are not on phones today.
- **Apple notarization.** It would remove the one-time **Open Anyway** step.
- **Signed approvals for risky AI actions ("Ask me first").** Phygital Key receipts, so an AI could be made to ask before certain actions.
- **Phone access through a tunnel to your Mac.** Never a server copy that unlocks your notes.

## Not planned

- **A hosted service run by us.** You keep your notes in your own folders and your own cloud.
- **Telemetry or accounts.** Nothing is collected.
- **Switching a memory between Open and Encrypted.** A lock that turns on and off was dropped as too hard: old plain copies stay in the cloud's history.
