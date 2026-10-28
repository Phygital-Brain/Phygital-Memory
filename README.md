<!-- TODO: put the demo video link here (a GitHub user-attachments link, 30 to 60 seconds). There is no video yet. -->

<p align="center"><img src="docs/images/icon.png" alt="" width="88"></p>

<h1 align="center">Phygital Memory</h1>

<p align="center"><b>Your notes as a memory your AI can use, kept on your own computer.</b><br>A desktop app for Mac, Windows and Linux. Works with Claude Code, Claude Desktop, Codex, Cursor and other AI apps that use MCP.</p>

<p align="center">
<a href="#credits"><img src="https://img.shields.io/badge/-open%20source-4D5BFF" alt="Open source"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0--only-blue" alt="License: AGPL-3.0-only"></a>
<a href="docs/setup-computer.md"><img src="https://img.shields.io/badge/platforms-macOS%20%C2%B7%20Windows%20%C2%B7%20Linux-4D5BFF" alt="Platforms: macOS, Windows and Linux"></a>
<a href="docs/languages.md"><img src="https://img.shields.io/badge/languages-41-C8F031" alt="41 languages"></a>
<a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-built%20in-black" alt="MCP built in"></a>
<a href="docs/connect-your-ai.md"><img src="https://img.shields.io/badge/works%20with-any%20MCP%20app-orange" alt="Works with any MCP app"></a>
<a href="docs/privacy.md"><img src="https://img.shields.io/badge/telemetry-none-0B0D12" alt="No telemetry"></a>
<a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-4D5BFF" alt="Pull requests welcome"></a>
</p>

<p align="center">
<a href="https://github.com/Phygital-Brain/Phygital-Memory/actions/workflows/tests.yml"><img src="https://github.com/Phygital-Brain/Phygital-Memory/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
<a href="https://github.com/Phygital-Brain/Phygital-Memory/releases/latest"><img src="https://img.shields.io/github/v/release/Phygital-Brain/Phygital-Memory" alt="Latest release"></a>
<a href="https://github.com/Phygital-Brain/Phygital-Memory/commits/main"><img src="https://img.shields.io/github/last-commit/Phygital-Brain/Phygital-Memory" alt="Last commit"></a>
<a href="docs/claude-desktop-extension.md"><img src="https://img.shields.io/badge/Claude%20Desktop-extension-d97757" alt="Claude Desktop extension"></a>
</p>

<p align="center"><b>Free and open source under the AGPL-3.0 license.</b> Use it, fork it and change it, share your changes, and keep the credit. See <a href="#credits">Credits</a>.</p>

<p align="center">
<a href="#quick-start-about-5-minutes">Quick start</a> ·
<a href="https://github.com/Phygital-Brain/Phygital-Memory/releases">Download</a> ·
<a href="docs/connect-your-ai.md">Connect your AI app</a> ·
<a href="#safety-and-privacy">Safety and privacy</a> ·
<a href="docs/examples.md">Things to ask</a> ·
<a href="#all-the-guides">All guides</a>
</p>

<details>
<summary><b>Table of contents</b></summary>

- [What it is](#what-it-is)
- [Safety and privacy](#safety-and-privacy)
- [How it works, in one picture](#how-it-works-in-one-picture)
- [Words you'll see](#words-youll-see)
- [What it can do](#what-it-can-do)
- [Languages](#languages)
- [Updating and leaving](#updating-and-leaving)
- [Quick start (about 5 minutes)](#quick-start-about-5-minutes)
- [What we tested](#what-we-tested)
- [All the guides](#all-the-guides)
- [This repository](#this-repository)
- [Not supported yet](#not-supported-yet)
- [Help and feedback](#help-and-feedback)
- [Contributors](#contributors)
- [Credits](#credits)
- [No warranty](#no-warranty)
- [License](#license)

</details>

> [!NOTE]
> Encrypted memories use the Cryptomator vault format (version 8), so Cryptomator can open them too. Not made by or affiliated with Cryptomator or Skymatic.

<table align="center"><tr>
<td align="center"><img src="docs/images/screenshot-1.png" alt="The setup page asks one question at a time: your name, Open or Encrypted, and a name and place for the memory." width="280"><br><sub>Make a memory in a few clicks</sub></td>
<td align="center"><img src="docs/images/screenshot-2.png" alt="The main window shows the folder list on the left and a note open in the editor on the right." width="420"><br><sub>Your notes, with search and history</sub></td>
</tr></table>

## What it is

Phygital Memory keeps your notes as a memory your AI can use. Each memory is one of two kinds, and you pick when you make it. An **Open** memory is a normal folder of notes: any AI app can read it, and a cloud folder puts it on your phone too. An **Encrypted** memory is opened with your password: AI apps reach it only through this app, and only the ones you allow.

On top of your notes, the app adds search, version history, a trash, AI tasks, sharing from computer to computer, and backups. AI apps talk to it through a small door on your own computer (an MCP server, the standard way AI apps use tools). You decide which apps get in, which memories each one sees, and whether it may change anything.

```
You: What did we decide about the pricing last month?
AI:  I searched your "Work" memory. The note from 14 October says you kept
     the old price until January. Want me to open the full note?

You: Add a line to my project note: waiting on the client for the logo.
AI:  Added at the end of "Projects/Logo.md". You can undo it from
     Activity in the app.
```

<p align="center"><img src="docs/images/chat.png" alt="A chat where you ask your AI about a past decision, it searches your memory and quotes the note it found, then adds one line to a project note that you can undo in the app." width="640"></p>

## Safety and privacy

> [!WARNING]
> What your AI reads goes to the company that runs your AI app. Text inside a note can also try to give the AI orders (prompt injection). Start every AI app on read only, and read [docs/safety.md](docs/safety.md) before you allow edits.

- **Read only to start.** An AI app can only search and read until you turn on **Allow edits** for it. The setting is checked on every call.
- **Your password never goes through the chat.** No tool takes a password, a key or a recovery word. You unlock only in the app.
- **Each app sees only what you give it.** Every AI app gets its own key and its own list of memories. **Private for AI** keeps a folder closed unless you ask in the chat, and **Hide from AI** hides an Encrypted memory from every app.
- **Every AI change can be undone.** The old text is kept first, each change shows in **Activity** with **Undo**, a trashed note stays 7 days, and notes keep up to 50 versions.
- **It stays on your computer.** The door listens only on your own computer (`127.0.0.1`). A website or another computer cannot reach it.
- **Nothing collected.** No account, no tracking, no usage reports and no server of ours. The one outside call you did not start is the update check to GitHub. Backups and sharing send data only after you turn them on.
- **Encrypted means encrypted.** An Encrypted memory is a Cryptomator format 8 vault. Its file names are encrypted too, and its backups and shares travel as encrypted files.
- **Sharing waits for you.** Nothing is sent before you press **Let in**, and every sharing change is signed with your own key.
- **Not audited yet.** Nobody outside the project has checked the code. A security review is planned. Tests are not an audit.

More in [docs/safety.md](docs/safety.md), [docs/privacy.md](docs/privacy.md) and [docs/threat-model.md](docs/threat-model.md).

## How it works, in one picture

The app window starts a small local program on your computer, which opens your memories and runs the AI door. Your AI app talks to that door, and the door answers only with the memories that app may reach.

<p align="center"><img src="docs/images/diagram.png" alt="Your AI app talks to the Phygital Memory door on your own computer, which reaches your Open and Encrypted memories. Backups and sharing go out only when you turn them on. No company sits in between." width="640"></p>

More in [docs/how-it-works.md](docs/how-it-works.md).

## Words you'll see

| Word | What it means here |
|---|---|
| **Memory** | One folder of notes the app looks after. You can have several. |
| **Open memory** | A plain folder of readable notes. No password. Any AI app or program that can open the folder can read it. |
| **Encrypted memory** | A locked folder (a Cryptomator format 8 vault). You open it with your password, or Touch ID on a Mac. |
| **Recovery key** | 44 words that let you set a new password for an Encrypted memory. Keep them offline. |
| **AI app** | Claude Code, Claude Desktop, Codex, Cursor or any app that can use tools through MCP. |
| **MCP** | Model Context Protocol: the standard way AI apps plug into tools like this one. |
| **The AI door** | The part of the app that AI apps talk to, at `http://127.0.0.1:8790/mcp`. It exists only while the app is open. |
| **Allow edits** | The switch that lets one AI app change notes. Off means read only. |
| **Private for AI** | A folder or note the AI opens only when you ask in the chat. A rule the tools follow, not encryption. |
| **AI tasks** | A hidden note in each memory where you leave work for your AI. It is never shared. |
| **Phygital Brain** | An optional set of folders, rules and first notes for working with an AI. The app can build it for you. |

## What it can do

- **Write and find.** An editor, search across your memories, a note graph, and **Version history** for every note.
- **Undo.** A trash that keeps things for 7 days, and **Undo** for every change an AI made.
- **Let AI apps in, one by one.** 17 tools for search, read, write, move, trash and AI tasks. See [docs/tools.md](docs/tools.md).
- **AI tasks.** Press **Give AI a task** on a note, then ask your AI *"Do my Phygital Memory tasks."*
- **Back up.** To a private GitHub repo, a WebDAV server, Amazon S3 or Cloudflare R2, or one backup file. Encrypted memories are backed up as encrypted files.
- **Share from computer to computer.** A whole memory, one folder or one file, with **Can edit** or **Can view**, through Syncthing. No account and no cloud. Both computers must be online with the app open at the same time. You link your own second computer the same way.
- **Use cloud folders.** Put a memory in iCloud Drive, Dropbox, Google Drive or Nextcloud. For an Encrypted memory the cloud sees only encrypted files.
- **Make it a Phygital Brain.** One setup page builds folders, rules and first notes, and leaves one AI task for your AI to finish the rest.

Ideas for what to ask are in [docs/examples.md](docs/examples.md).

## Languages

The app's screens come in 41 languages. It follows your computer's language, or you pick one in **Settings › General › Language**. The translations were made with AI and checked by a script. Native speakers have not read them yet, so if something reads oddly, please help fix it: see [docs/languages.md](docs/languages.md) and [core/languages/TRANSLATING.md](core/languages/TRANSLATING.md). The AI tools and these docs stay in English, and your AI app answers you in your own language.

## Updating and leaving

The app updates itself from the latest GitHub Release. It checks when it opens and every 6 hours while it stays open. An update found at opening installs right away; one found later installs when you quit. Updates are signed, so only real releases install. See [docs/updates.md](docs/updates.md).

To leave, remove the app. Your memories are your own folders and stay where they are: plain Markdown for Open memories, standard Cryptomator vaults for Encrypted ones. The full steps are in [Remove it](docs/setup-computer.md#remove-it).

## Quick start (about 5 minutes)

You do not need a terminal for any of this.

1. **Download the app.** Open the [Releases page](https://github.com/Phygital-Brain/Phygital-Memory/releases) and pick the file for your computer:

   | Computer | File |
   |---|---|
   | Mac (Apple chip and Intel, one download) | `Phygital Memory_<version>_universal.dmg` |
   | Windows | `Phygital Memory_<version>_x64-setup.exe` |
   | Linux, Debian or Ubuntu | the `_amd64.deb`, or `_arm64.deb` on ARM |
   | Linux, Fedora or openSUSE | the `.rpm` |
   | Linux, any other | the `.AppImage` |

2. **Install it.**
   - **Mac:** open the `.dmg` and drag **Phygital Memory** into **Applications**.
   - **Windows:** open the `setup.exe` and follow the steps.
   - **Linux:** open the `.deb` or `.rpm` with your software installer. For the AppImage, see [setup](docs/setup-computer.md#1-get-the-app).

3. **Open it the first time.** The app is not code-signed yet, so your computer asks you to allow it once.
   - **Mac:** right-click **Phygital Memory** in Applications, choose **Open**, then **Open** again. If macOS only offers **Done**, click it, open **System Settings › Privacy & Security**, scroll down and click **Open Anyway**.
   - **Windows:** SmartScreen says "Windows protected your PC". Click **More info**, then **Run anyway**.
   - **Linux:** nothing extra. Open **Phygital Memory** from your app list.

   You should see **Set up your Phygital Memory**.

4. **Make your first memory.** Answer the questions one at a time: your name, **Open** or **Encrypted**, a name and a place, a backup (or **Later**), and what it is for. Press **Set it up**. You should see "Your memory is ready".

   > [!IMPORTANT]
   > An Encrypted memory cannot be opened without its password or its recovery key. After setup, open **Settings** and save the 44-word recovery key somewhere offline.

5. **Connect your AI app.** The next screen offers **Add to Claude Code**, and **Download** for Claude Desktop (an extension you double-click, see [docs/claude-desktop-extension.md](docs/claude-desktop-extension.md)). For Codex, Cursor and other apps, follow [docs/connect-your-ai.md](docs/connect-your-ai.md).

6. **Check it works.** Keep the app open and ask your AI app: *"Run status from Phygital Memory."* You should see your memory by name and how many notes it holds.

> [!TIP]
> Leave **Allow edits** off until you have seen your AI app work. The full guide, with where things are kept and how to remove the app, is [docs/setup-computer.md](docs/setup-computer.md).

## What we tested

| What | How | Result |
|---|---|---|
| Mac (Apple chip) | Used every day, with the test scripts in `core/tests/` | Works |
| Linux on ARM | A virtual machine | Works |
| Windows on ARM | A virtual machine | Installs and opens, with known issues waiting for a retest (see [troubleshooting](docs/troubleshooting.md#installing-and-opening-the-app)) |
| Linux x64, Windows x64, Intel Mac | The engine tests on GitHub's machines only | Not tried by hand yet |

> [!CAUTION]
> Windows is built but not fully tested yet. Known issues: **Show in folder** could stop the app's engine, the folder picker could open hidden behind the app, and the close button once did nothing. Keep a backup if you try it.

## All the guides

| Guide | Read it when |
|---|---|
| [Guides index](docs/README.md) | You want every guide on one page |
| [Setup on your computer](docs/setup-computer.md) | You want to install the app and make your first memory |
| [Connect your AI app](docs/connect-your-ai.md) | You want Claude Code, Claude Desktop, Codex, Cursor or another AI app to use your memory |
| [Claude Desktop extension](docs/claude-desktop-extension.md) | You use Claude Desktop and want to connect it with one file |
| [Things to ask](docs/examples.md) | You are not sure what to say to your AI |
| [The AI tools](docs/tools.md) | You want the list of everything an AI app can do |
| [Settings](docs/settings.md) | You want to change how the app works, or find where something is kept |
| [Safety](docs/safety.md) | Before you let an AI read or change your notes |
| [Privacy](docs/privacy.md) | You want to know what leaves your computer and who can see what |
| [Threat model](docs/threat-model.md) | You want to know what the app protects against, and what it cannot |
| [How it works](docs/how-it-works.md) | You want to know what happens inside, in plain words |
| [Updates](docs/updates.md) | You want to know how the app gets updated |
| [Languages](docs/languages.md) | You want the app in another language |
| [Translating](core/languages/TRANSLATING.md) | You want to add a language or fix a translation |
| [Questions people ask](docs/faq.md) | You have a quick question |
| [If something goes wrong](docs/troubleshooting.md) | Something does not work |
| [Roadmap](docs/roadmap.md) | You want to know what might come next |
| [SECURITY.md](SECURITY.md) | You found a security problem |
| [CHANGELOG.md](CHANGELOG.md) | You want to know what changed in each version |
| [CONTRIBUTING.md](CONTRIBUTING.md) | You want to report a bug or send a change |
| [CONTRIBUTORS.md](CONTRIBUTORS.md) | You want to see who helped, or be added |
| [GOVERNANCE.md](GOVERNANCE.md) | You want to know how decisions are made |
| [SUPPORT.md](SUPPORT.md) | You need help and don't know where to ask |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | You want to know how people behave here |
| [TRADEMARKS.md](TRADEMARKS.md) | You want to use the name or the logo |
| [AGENTS.md](AGENTS.md) | You (or your AI coding agent) want to change the code |

## This repository

| Folder or file | What it is |
|---|---|
| [`core/phygital_memory/`](core/phygital_memory) | The engine (Python): memories, encryption, search, sharing, backups, the AI door. |
| [`core/phygital_memory/vault/`](core/phygital_memory/vault) | How a memory is stored: `plain.py` for Open memories, the rest for Encrypted ones. |
| [`core/frontend/`](core/frontend) | The app's screens (JavaScript). They build into `core/phygital_memory/web/`. |
| [`core/languages/`](core/languages) | Every screen text in 41 languages. `en.json` is the source. |
| [`core/tests/`](core/tests) | Every test, the sample notes they use, and `run.sh` to run one. |
| [`core/packaging/`](core/packaging) | Turns the engine into one program, plus the Touch ID and Keychain helper (Mac only). |
| [`core/scripts/`](core/scripts) | Small tools, such as `i18n.py` for the screen texts. |
| [`app/`](app) | The window around it all (Tauri, Rust): starts the engine, draws the menu bar, asks before closing. |
| [`brand/`](brand) | Logo, colours, icons and the brand guide. |
| [`rebuild.sh`](rebuild.sh) | Builds the Mac app and makes the `.dmg`. |

To build the Mac app yourself you need `uv`, `npm`, Rust with `cargo tauri`, `syncthing` and `rclone`. Then run:

```bash
bash rebuild.sh --install
```

You should see a `.dmg` in `release/`, and the app replaced in Applications and reopened. The first build takes longer, because it fetches the build tools. The Windows and Linux apps are built on GitHub. To run one test:

```bash
sh core/tests/run.sh test_open.py
```

You should see PASS or FAIL for each check. More for developers in [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## Not supported yet

- **A phone app.** The engine is Python, which does not run well on phones. An Open memory in a cloud folder still shows up in your phone's files.
- **Encrypted memories on phones.** They need the app to open, and there is no phone app.
- **The Claude website and phone app.** The door lives on your computer at `127.0.0.1`, which a website or a phone cannot reach.
- **Sign-in from the Claude app.** It refuses sign-in pages that are not on https, and the door is a local address. Connect with a key instead.
- **Code signing.** The Mac and Windows downloads are not signed yet, so the first open needs one extra step.
- **Switching a memory between Open and Encrypted.** Old plain copies would stay in your cloud's history, so this was dropped.
- **Shutting a removed person out of later changes.** Changing a shared memory's key is not built yet.
- **The Finder view and Touch ID off the Mac.** Both are Mac only for now.

What might come next is in [docs/roadmap.md](docs/roadmap.md). Nothing there is promised or has a date.

## Help and feedback

| You want to | Go to |
|---|---|
| Fix a problem yourself | [If something goes wrong](docs/troubleshooting.md) |
| Report a bug | [Something doesn't work](https://github.com/Phygital-Brain/Phygital-Memory/issues/new?template=bug_report.yml) |
| Suggest an idea or a feature | [Idea or feature](https://github.com/Phygital-Brain/Phygital-Memory/issues/new?template=feature_request.yml) |
| Ask a question | [Question](https://github.com/Phygital-Brain/Phygital-Memory/issues/new?template=question.yml) |
| Ask for a commercial license | [Open an issue](https://github.com/Phygital-Brain/Phygital-Memory/issues) |
| Report a security problem, privately | [Private report](https://github.com/Phygital-Brain/Phygital-Memory/security/advisories/new) ([SECURITY.md](SECURITY.md)) |

Issues are public, so leave out passwords, keys and private notes.

## Contributors

Thank you to everyone who helped. Code, bug reports, ideas, docs, translations, design and testing all count. A native speaker reading one of the 41 languages helps a lot. See [CONTRIBUTORS.md](CONTRIBUTORS.md), and add yourself when you send a pull request.

## Credits

Phygital Memory was made by Phygital-Brain and the Phygital Memory contributors, under [Phygital-Brain](https://github.com/Phygital-Brain). The vault code and the Finder view come from Encryptor MCP, by the same author, under the same license.

It builds on the work of others:

- **Cryptomator.** Encrypted memories use the Cryptomator vault format (version 8), so Cryptomator can open them. The app contains no Cryptomator code. Not made by or affiliated with Cryptomator or Skymatic. "Cryptomator" is a name and trademark of its owners.
- **Syncthing** (MPL-2.0) for sharing between computers, and **rclone** (MIT) for WebDAV and S3 or R2. The built app bundles both unchanged.
- **Tauri** for the app window, and the libraries listed in [`core/uv.lock`](core/uv.lock) (Python), [`core/frontend/package-lock.json`](core/frontend/package-lock.json) (JavaScript) and [`app/src-tauri/Cargo.lock`](app/src-tauri/Cargo.lock) (Rust), each under its own license. The app lists the bundled programs under **Settings › Licences**.
- **Baalda.** Design and feature ideas, including the style of some sidebar icons, come from [Baalda](https://github.com/naveedharri/baalda) (Apache-2.0). No Baalda code is included.

You're welcome to use, fork, change and build on it under the GNU Affero General Public License, version 3 only (AGPL-3.0-only), and the notices in [NOTICE](NOTICE). In short:

- Keep [LICENSE](LICENSE), [NOTICE](NOTICE) and the copyright lines.
- If you share a changed version, or run one that other people use over a network, offer them its source code under the same license.
- Mark your version as changed.

GitHub's "Cite this repository" button uses [CITATION.cff](CITATION.cff).

## No warranty

Phygital Memory is free software you run yourself. It comes as is, with no warranty: you use it at your own risk, and no author is responsible for lost or damaged data (sections 15 and 16 of the [license](LICENSE) say so in full). Keep a backup anyway.

## License

[GNU Affero General Public License, version 3 only](LICENSE) (AGPL-3.0-only), with the notices in [NOTICE](NOTICE). A commercial license is also available for use without the AGPL's terms: [open an issue](https://github.com/Phygital-Brain/Phygital-Memory/issues) to ask. Copyright (C) 2026 Phygital-Brain and Phygital Memory contributors.
