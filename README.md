<!-- TODO: demo video link (a GitHub user-attachments link, 30 to 60 seconds). -->

<p align="center"><img src="docs/images/icon.png" alt="" width="88"></p>

<h1 align="center">Phygital Memory</h1>

<p align="center"><b>A notes app that becomes your second brain.<br>Open source, private, encrypted when you want it, and every file stays yours.</b></p>

<p align="center">
<a href="LICENSE"><img src="https://img.shields.io/badge/open%20source-AGPL--3.0-4D5BFF" alt="Open source: AGPL-3.0"></a>
<a href="docs/privacy.md"><img src="https://img.shields.io/badge/tracking-none-0B0D12" alt="No tracking"></a>
<a href="docs/how-it-works.md"><img src="https://img.shields.io/badge/encryption-Cryptomator%20format-C8F031" alt="Cryptomator format encryption"></a>
<a href="docs/setup-computer.md"><img src="https://img.shields.io/badge/Mac%20%C2%B7%20Windows%20%C2%B7%20Linux-4D5BFF" alt="Mac, Windows and Linux"></a>
<a href="https://github.com/Phygital-Brain/Phygital-Memory/releases/latest"><img src="https://img.shields.io/github/v/release/Phygital-Brain/Phygital-Memory" alt="Latest release"></a>
</p>

<p align="center">
<a href="https://github.com/Phygital-Brain/Phygital-Memory/releases">Download</a> ·
<a href="docs/setup-computer.md">Get started</a> ·
<a href="docs/connect-your-ai.md">Connect your AI</a> ·
<a href="docs/faq.md">Questions</a> ·
<a href="docs/README.md">All guides</a>
</p>

<table align="center"><tr>
<td align="center"><img src="docs/images/screenshot-1.png" alt="Making a memory: you pick Open or Encrypted, a name and a place." width="280"></td>
<td align="center"><img src="docs/images/screenshot-2.png" alt="The main window: your folders on the left, a note open on the right." width="420"></td>
</tr></table>

## What it is

Phygital Memory is a notes app for your computer. You write notes, and your AI app (Claude, Codex, Cursor and others) can read them, search them and help you keep them in order. Over time it becomes a second brain: what you know, decided and planned, in one place your AI can use.

It's built around four promises:

- 🔓 **Open source.** Every line of code is here to read, check and change.
- 🙈 **Private.** No account, no tracking, no server of ours. Your notes stay on your computer unless you choose a cloud or a backup.
- 🔐 **Encrypted when you want it.** Lock a memory with a password. Without it (or your recovery key), the files are unreadable.
- 🗂️ **You own your data.** Notes are normal files. Stop using the app and they're still yours, readable by anything.

## Two kinds of memory

When you make a memory, you pick one:

| | 📂 Open | 🔒 Encrypted |
|---|---|---|
| What it is | A normal folder of Markdown notes | A locked vault, opened with your password |
| Who can read it | Any app, any AI, your phone through a cloud folder | Only this app, and only the AI apps you let in |
| Good for | Notes you're happy for your AI to see anywhere | Clients, money, health, anything private |

You can have both, side by side.

## Your AI, on your terms

- AI apps start **read only**. They can change notes only after you switch on **Allow edits** for each one.
- You choose which memories each AI app can see.
- Every AI change shows in **Activity**, with **Undo**.

More on how it keeps you safe in [Safety](docs/safety.md).

## Get started

1. **Download** the app for your computer from [Releases](https://github.com/Phygital-Brain/Phygital-Memory/releases).
2. **Open it** and make your first memory. It asks a few questions, all clicks.
3. **Connect your AI app.** The app sets up Claude Code for you, and Claude Desktop on a Mac. For others, see [Connect your AI](docs/connect-your-ai.md).

Then ask your AI: *"What's in my Phygital Memory?"*

The full guide, with the first-open steps for each system, is [Get started](docs/setup-computer.md).

## What else it does

- 🔎 Search, a note graph, and version history for every note
- 🗑️ A trash that keeps things for 7 days
- 🤝 Share a memory, a folder or one file with another computer. No account, no cloud.
- ☁️ Keep a memory in iCloud Drive, Dropbox, Google Drive or Nextcloud
- 💾 Back up to a private GitHub repo, WebDAV, Amazon S3 or Cloudflare R2
- 🧠 Turn a memory into a Phygital Brain: ready-made folders and rules for working with AI
- 🌍 41 languages
- 🔄 Updates itself

## Learn more

| | |
|---|---|
| [Get started](docs/setup-computer.md) | Install, first memory, connect your AI |
| [Questions](docs/faq.md) | Quick answers |
| [Safety](docs/safety.md) and [Privacy](docs/privacy.md) | What the app protects, and what leaves your computer |
| [How it works](docs/how-it-works.md) | What happens inside, in plain words |
| [If something goes wrong](docs/troubleshooting.md) | Fixes for common problems |
| [All guides](docs/README.md) | Everything else |

## Help and contributing

Found a bug, have an idea or a question? [Open an issue](https://github.com/Phygital-Brain/Phygital-Memory/issues/new/choose). For a security problem, use a [private report](https://github.com/Phygital-Brain/Phygital-Memory/security/advisories/new).

Want to help? Fixes, docs and translations are all welcome. A native speaker checking one of the 41 languages helps a lot. Start with [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits and license

Made by [Phygital-Brain](https://github.com/Phygital-Brain) and the [contributors](CONTRIBUTORS.md). Encrypted memories use the [Cryptomator](https://cryptomator.org) vault format, so Cryptomator can open them too. Not made by or affiliated with Cryptomator. Sharing uses [Syncthing](https://syncthing.net), and cloud storage uses [rclone](https://rclone.org). Design ideas come from [Baalda](https://github.com/naveedharri/baalda). No Baalda code is included. More in [NOTICE](NOTICE).

Free and open source under the [AGPL-3.0](LICENSE). A commercial license is available: [open an issue](https://github.com/Phygital-Brain/Phygital-Memory/issues) to ask.
