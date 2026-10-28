# Updates

For when you want to know how Phygital Memory gets updated. Short answer: there is no release yet.

## Know when there's an update

Each release will have a version tag (`vX.Y.Z`), notes on the [releases page](https://github.com/Phygital-Brain/Phygital-Memory/releases), and a `.dmg` for the Mac. What changed is in [CHANGELOG.md](../CHANGELOG.md).

- **On GitHub:** **Watch, Custom, Releases** on the repository. GitHub emails you each new release.
- **Your version:** it is in the name of the file you installed, for example `Phygital Memory_0.1.0_aarch64.dmg`. Compare it with the [latest release](https://github.com/Phygital-Brain/Phygital-Memory/releases/latest).

The app does not check for updates yet. It sends nothing to look for them.

## Update by hand

1. Download the new `.dmg` from the releases page.
2. Quit Phygital Memory.
3. Open the `.dmg` and drag **Phygital Memory** into **Applications**, replacing the old one.
4. Open it. The app is not notarized by Apple, so macOS may ask you to allow it again with **System Settings › Privacy & Security › Open Anyway**.

If macOS asks about the Keychain after an update, type your Mac login password and choose **Always Allow**.

## Update by itself

Planned. Releases will come from GitHub Releases, and the app will update itself from there. It is not built yet. When it is, this page will say how to turn it off.

## Staying on one version

Do not replace the app. Until auto-update exists, the app never changes by itself.

## Going back

Install the older `.dmg` from the releases page over the newer one. Your memories do not change, because they are your own folders and the app only reads them. If a newer version changed the app's own information in `~/Library/Application Support/Phygital Memory`, an older version may not understand it. Keep a backup before you update.

## What an update never touches

- Your memory folders and the notes in them.
- Your passwords and recovery keys.
- Your AI app list, your approvals, your shares and your Keychain items.
- Your backups on GitHub, WebDAV or S3.

## What next

See [roadmap.md](roadmap.md) for what is coming.
