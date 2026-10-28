# Updates

For when you want to know how Phygital Memory gets updated. Short answer: it updates itself from the latest GitHub Release.

## Know when there's an update

Each release has a version tag (`vX.Y.Z`), notes on the [releases page](https://github.com/Phygital-Brain/Phygital-Memory/releases), and a file for each computer. What changed is in [CHANGELOG.md](../CHANGELOG.md).

| Computer | Release file |
|---|---|
| Mac (Apple chip and Intel) | `Phygital Memory_<version>_universal.dmg` |
| Windows | `Phygital Memory_<version>_x64-setup.exe`, `Phygital Memory_<version>_x64_en-US.msi` |
| Linux | `Phygital Memory_<version>_amd64.deb` or `_arm64.deb`, the `.rpm`, the `.AppImage` |

- **On GitHub:** **Watch, Custom, Releases** on the repository. GitHub emails you each new release.
- **Your version:** it is in the name of the file you installed, for example `Phygital Memory_0.1.0_universal.dmg`. Compare it with the [latest release](https://github.com/Phygital-Brain/Phygital-Memory/releases/latest).

## Update by itself

The app checks the latest GitHub Release when it opens, and again every 6 hours while it stays open.

- **Found while the app opens:** it installs right away. The opening screen shows "Updating to version X" with a progress bar. Every memory locks, the update goes in, and the app restarts.
- **Found later, while you use the app:** it downloads quietly and installs when you quit. You get the new version the next time you open the app.

An update never goes in while you are working. If anything fails, nothing changes, and it tries again the next time you open the app.

Updates are signed with the project's update key. The app installs only an update signed with that key, so only real releases install.

The check is a request to `github.com` for `latest.json` (a small file that names the newest version) and, when there is an update, the download. Nothing about your notes is sent. See [privacy.md](privacy.md#what-leaves-your-computer).

## Update by hand

1. Download the new file from the releases page.
2. Quit Phygital Memory.
3. Install it the same way as the first time (see [setup](setup-computer.md#1-get-the-app)). On a Mac, drag **Phygital Memory** into **Applications** and replace the old one.
4. Open it. The Mac and Windows apps are not code-signed, so your computer may ask you to allow it again (see [setup](setup-computer.md#2-open-it-the-first-time)).

If macOS asks about the Keychain after an update, type your Mac login password and choose **Always Allow** (Mac only).

## Going back

Install the older file from the releases page over the newer one. Your memories do not change, because they are your own folders. If a newer version changed the app's own information in the app folder (see [settings](settings.md#files-the-app-keeps)), an older version may not understand it. Keep a backup before you update. The app updates itself again the next time it opens and finds a newer release.

## What an update never touches

- Your memory folders and the notes in them.
- Your passwords and recovery keys.
- Your AI app list, your approvals, your shares and your saved secrets.
- Your backups on GitHub, WebDAV or S3.

## What next

See [roadmap.md](roadmap.md) for what is coming.
