# Questions people ask

Quick answers. Each one links to the page that goes deeper.

## The basics

<details>
<summary><b>What is Phygital Memory?</b></summary>

A desktop app for Mac, Windows and Linux that keeps your notes as a memory your AI can use. It has an editor, search, version history, a trash, AI tasks, sharing and backups. AI apps reach your notes through one local door on your own computer. See [how it works](how-it-works.md).

</details>

<details>
<summary><b>Is it free?</b></summary>

Yes. It is distributed free. Running it on your computer costs nothing. Your AI app may need its own plan, and a cloud or S3 bucket you choose for backups may cost money. It is open source under the AGPL-3.0 license.

</details>

<details>
<summary><b>Do I need to know how to code?</b></summary>

No. Install the app, answer a few questions, and connect your AI app with one button or one paste. [Setup on your computer](setup-computer.md) takes about 5 minutes.

</details>

<details>
<summary><b>What is the difference between Open and Encrypted?</b></summary>

An Open memory is a plain folder. Any AI app can read it, there is no password, and it can sit in iCloud Drive, Dropbox or Google Drive so your phone gets it too. An Encrypted memory is opened with your password. AI apps can only reach it through this app, and only the ones you allow. You choose when you make the memory and cannot switch later. See [how it works](how-it-works.md#two-kinds-of-memory).

</details>

<details>
<summary><b>Which should I pick?</b></summary>

Pick Open if you want any AI app, and your phone, to read your notes with no setup. Pick Encrypted if the notes are private and you want to decide which AI apps get in. If you are unsure, start with Open and keep private things in an Encrypted memory. You can have both.

</details>

<details>
<summary><b>Which computers does it work on?</b></summary>

Mac (one download for Apple chip and Intel Macs), Windows (x64, and Windows on ARM through emulation) and Linux (x64 and ARM). The Mac app is used every day. Windows was tested by hand on Windows on ARM in a virtual machine. The Intel Mac build will be dropped in a later release. See [what we tested](setup-computer.md#what-we-tested).

</details>

<details>
<summary><b>How do I install it?</b></summary>

Download the file for your computer from the [Releases page](https://github.com/Phygital-Brain/Phygital-Memory/releases). Mac: open the `.dmg` and drag the app into **Applications**. Windows: run the `setup.exe` or the `.msi`. Linux: install the `.deb` or `.rpm`, or run the AppImage. See [setup](setup-computer.md#1-get-the-app).

</details>

<details>
<summary><b>Which AI apps work with it?</b></summary>

Claude Code, Claude Desktop, Cursor and Codex have steps in [connect your AI app](connect-your-ai.md). Any AI app that can use an MCP server over HTTP with a header may work, but we have only tested the ones with steps. Apps on the web or on your phone cannot reach the door yet, because it lives on your computer.

</details>

<details>
<summary><b>Is it affiliated with Cryptomator?</b></summary>

No. Encrypted memories use the Cryptomator vault format 8, so you can open them in Cryptomator too. The app contains no Cryptomator code and is not made by or affiliated with Cryptomator.

</details>

<details>
<summary><b>Which languages does the app speak?</b></summary>

41 languages. English is the source. The translations were made with AI and checked by a script. Native speakers have not read them yet. See [languages](languages.md).

</details>

## Your data and safety

<details>
<summary><b>Does it send my data anywhere?</b></summary>

Not unless you press a button that needs it. There is no account, no tracking and no server of ours. Connecting GitHub, WebDAV, S3 or R2, or sharing a memory with someone, sends data there, and Encrypted memories go out as encrypted files only. See [privacy](privacy.md).

</details>

<details>
<summary><b>What can the AI do with my notes?</b></summary>

Only what the 17 tools allow: search, read, and (if you allowed edits) create, change, move and trash notes, plus your AI tasks. It cannot see a memory you hid from it, cannot ask for your password, and cannot delete anything for good. See [tools](tools.md).

</details>

<details>
<summary><b>What can the AI not do?</b></summary>

It cannot unlock a memory, read a locked one, see your passwords or recovery key, change settings, share a memory, or empty the trash. Only you do those in the app.

</details>

<details>
<summary><b>Can I undo a change the AI made?</b></summary>

Yes. Every AI change shows in the AI activity list with an **Undo** button, and the old text is kept in the note's version history. A note the AI created goes to the trash on Undo. Undo refuses if you changed the note after the AI did, so you do not lose your own work. See [safety](safety.md#if-something-goes-wrong).

</details>

<details>
<summary><b>What happens if I delete a note?</b></summary>

It goes to the trash inside the memory and stays for 7 days. After that it is deleted for good. You can restore it from **Trash** in the app until then.

</details>

<details>
<summary><b>How many old versions are kept?</b></summary>

The app keeps the previous text of a note before it changes: at most one every 5 minutes per note, and the newest 50 per note. AI changes are kept the same way.

</details>

<details>
<summary><b>What is Private for AI?</b></summary>

A folder, note or file you mark so the AI does not open it unless you ask in the chat. Search shows it only as a locked line, and the AI must call again with `private=true`, which its instructions say to do only when you asked. It also covers hidden files such as `.env`. It is a strong request enforced by the tools, not encryption. For real secrets, use an Encrypted memory. See [safety](safety.md#pick-a-safety-level).

</details>

<details>
<summary><b>Can the AI read an Open memory without the app?</b></summary>

Yes. An Open memory is a plain folder, so any AI app that can read files can read it, without a key and without the door. That is what Open means. The app marks hidden files and Private for AI folders for the tools, but a program reading the folder directly is not stopped. See [threat model](threat-model.md).

</details>

<details>
<summary><b>What if an AI follows instructions hidden in a note?</b></summary>

That is called prompt injection and today's AI models can fall for it. The tools label every note as information, never instructions, and an app that may only read cannot change anything. Keep AI apps on read only unless you need edits, and check the AI activity list. See [safety](safety.md).

</details>

<details>
<summary><b>Is it audited?</b></summary>

No. Nobody outside the project has audited it. A security review is planned. See [threat model](threat-model.md#not-audited-yet).

</details>

## Passwords and keys

<details>
<summary><b>What if I forget my password?</b></summary>

Use your recovery key: 44 words, in Cryptomator's own format, shown in **Settings** with your password. It sets a new password. Without the password and the recovery key, nobody can open the memory, including us. An Open memory has no password.

</details>

<details>
<summary><b>Where do I find the recovery key?</b></summary>

Open the Encrypted memory, go to **Settings**, and show the recovery key (it asks for your password). Write it down or keep it in a password manager. Anyone who has the words can open the memory.

</details>

<details>
<summary><b>How does Touch ID work?</b></summary>

Touch ID is Mac only. If you turn it on, the app keeps your password in the Mac's Keychain, where only this app can read it after your fingerprint (or your Mac password if there is no Touch ID). If you change the password, Touch ID keeps working with the new one. See [privacy](privacy.md#whats-kept).

</details>

<details>
<summary><b>Where do AI app keys come from?</b></summary>

From **Settings › AI apps › Connect an AI app**. The key is shown once. The app stores only a fingerprint of it, so the file on disk cannot be used to get in. You can remove an app any time and its key stops working.

</details>

<details>
<summary><b>Will the AI ever ask me for my password?</b></summary>

It should not. Its instructions say never to ask. If an AI asks for a password or recovery key in a chat, do not type it. Unlock memories only in the app.

</details>

## Compatibility

<details>
<summary><b>Can I use my notes in other apps?</b></summary>

Yes. An Open memory is plain Markdown files, so Obsidian and others open it. An Encrypted memory is a standard Cryptomator vault that Cryptomator opens with the same password. The app skips hidden folders such as `.git` and `.obsidian` and leaves them alone.

</details>

<details>
<summary><b>Does it work with iCloud Drive, Dropbox, Google Drive or Nextcloud?</b></summary>

Yes, as folders on your computer. Choose a cloud folder as the place when you make a memory, and that app syncs it. For Encrypted memories the cloud only sees encrypted files. If two devices change the same note, both versions are kept.

</details>

<details>
<summary><b>Can I use it on my phone?</b></summary>

There is no phone app. An Open memory in a cloud folder shows up in your phone's files, and AI apps on your phone connected to that cloud or to a GitHub backup can read it. Encrypted memories are not on phones yet. See [roadmap](roadmap.md).

</details>

<details>
<summary><b>Can two people work in one memory?</b></summary>

Yes. Share a whole memory, one folder or one file from computer to computer, with Can edit or Can view. It goes through Syncthing, with no account and no cloud. Both computers must be online with the app open at the same time. Changes wait until both are on. See [how it works](how-it-works.md) and [privacy](privacy.md#sharing).

</details>

<details>
<summary><b>Why does the app say Phygital Brain?</b></summary>

Phygital Brain is a set of folders, rules and first notes for working with an AI. **Make it a Phygital Brain** builds them for you in a memory. The app builds the skeleton itself and leaves one AI task for your AI to finish the rest. You do not need it.

</details>

## Running it

<details>
<summary><b>Does the app need to stay open?</b></summary>

For Encrypted memories, yes: only unlocked memories can be searched, and quitting the app locks everything. The app asks before it closes. For Open memories, no: an AI app set up to start Phygital Memory itself reaches them with the app closed. See [two ways in](connect-your-ai.md#two-ways-in).

</details>

<details>
<summary><b>Why does macOS say it can't verify the app?</b></summary>

It is distributed free and is not code-signed or notarized by Apple, so macOS asks you to allow it once. Right-click the app and choose **Open**, or open **System Settings › Privacy & Security** and click **Open Anyway**. See [setup](setup-computer.md#2-open-it-the-first-time).

</details>

<details>
<summary><b>Why does Windows say "unknown publisher"?</b></summary>

The Windows app is not code-signed yet, so SmartScreen warns you once. Click **More info**, then **Run anyway**. See [setup](setup-computer.md#2-open-it-the-first-time).

</details>

<details>
<summary><b>How do I update?</b></summary>

The app updates itself. It checks the latest GitHub Release when it opens. If it finds a newer version then, it installs it and restarts. If it finds one later, it installs it when you quit. See [updates](updates.md).

</details>

<details>
<summary><b>How do I remove it?</b></summary>

Quit the app and remove it (on a Mac, drag it out of Applications). Your memories stay where they are because they are your folders. The steps for removing the app's own data are in [setup](setup-computer.md#remove-it).

</details>

<details>
<summary><b>Where are my notes?</b></summary>

In the folder you chose for each memory. The default first memory folder is `~/Phygital Memory`. The app's own information is in the app folder: `~/Library/Application Support/Phygital Memory` on Mac, `%APPDATA%\Phygital Memory` on Windows, `~/.local/share/phygital-memory` on Linux. See [settings](settings.md#files-the-app-keeps).

</details>

<details>
<summary><b>What is an AI task?</b></summary>

A line you give your AI to do later, kept in a hidden note called `AI tasks` inside the memory, under **To do**. When you ask your AI to do your Phygital Memory tasks, it reads them with `handed_notes`, does them, and ticks them off with `finish_handed_note`. Done ones stay for 7 days. The note is never shared. See [examples](examples.md#give-it-a-task).

</details>

<details>
<summary><b>Why do I see hidden folders in my Open memory?</b></summary>

The app keeps `.trash`, `.versions`, `.phygital` and `.ai-tasks` inside each memory. They hold your trash, version history, per-memory settings and AI tasks. Other apps may show them. Leave them in place.

</details>

<details>
<summary><b>Where do I report a bug or a security problem?</b></summary>

A bug goes in the [bug form](https://github.com/Phygital-Brain/Phygital-Memory/issues/new?template=bug_report.yml). A security problem goes in the [private report](https://github.com/Phygital-Brain/Phygital-Memory/security/advisories/new), never in a public issue. See [SECURITY.md](../SECURITY.md).

</details>

## Still have a question?

Open a [Question](https://github.com/Phygital-Brain/Phygital-Memory/issues/new?template=question.yml). If you asked something twice, we will add it here.
