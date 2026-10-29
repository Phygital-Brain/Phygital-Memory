# Setup on your computer

For when you want to try Phygital Memory on a Mac, Windows or Linux computer, free, with any AI app. About 5 minutes.

## Before you start

- A Mac (Apple chip or Intel), a Windows computer (x64, or Windows on ARM through emulation), or a Linux computer (x64 or ARM). Windows was tested in a virtual machine. See [what we tested](#what-we-tested).
- An AI app that can use MCP tools: Claude Code, Claude Desktop, Cursor or Codex. See [connect-your-ai.md](connect-your-ai.md).
- No other program using port 8790 on your computer.

## 1. Get the app

Download it from the [Releases page](https://github.com/Phygital-Brain/Phygital-Memory/releases). Pick the file for your computer (`<version>` is the version number, for example `0.1.0`):

| Computer | File |
|---|---|
| Mac (Apple chip and Intel, one download) | `Phygital Memory_<version>_universal.dmg` |
| Windows | `Phygital Memory_<version>_x64-setup.exe` (or the `_x64_en-US.msi`) |
| Linux, Debian or Ubuntu | `Phygital Memory_<version>_amd64.deb`, or `_arm64.deb` on ARM |
| Linux, Fedora or openSUSE | the `.rpm` |
| Linux, any other | the `.AppImage` |

Then install it:

- **Mac:** open the `.dmg` and drag **Phygital Memory** into **Applications**.
- **Windows:** open the `setup.exe` (or the `.msi`) and follow the steps.
- **Linux:** open the `.deb` or `.rpm` with your software installer, or in a terminal run `sudo apt install ./<file>.deb` (or `sudo dnf install ./<file>.rpm`). For the AppImage, make it runnable (`chmod +x <file>.AppImage`) and open it. The AppImage needs FUSE. If it does not open, install your system's FUSE 2 package (often called `libfuse2`).

The Intel Mac build will be dropped in a later release.

### Build it yourself

A developer can also build the Mac app from this repository:

```bash
bash rebuild.sh --install
```

You should see a `.dmg` made in `release/` and, with `--install`, the app replaced in Applications and reopened. The first build takes longer, because it fetches the build tools. You need `uv`, `npm`, Rust with `cargo tauri`, `syncthing` and `rclone`. The Windows and Linux apps are built on GitHub.

## 2. Open it the first time

The Mac and Windows apps are distributed free and are not code-signed, so your computer asks you to allow them once.

**Mac:** right-click **Phygital Memory** in Applications and choose **Open**, then **Open** again. If macOS only offers **Done**:

1. Click **Done**.
2. Open **System Settings › Privacy & Security**.
3. Scroll down to the message about Phygital Memory and click **Open Anyway**.
4. Type your Mac password or use Touch ID, then open the app again.

**Windows:** SmartScreen says "Windows protected your PC" and shows "Unknown publisher". Click **More info**, then **Run anyway**.

**Linux:** nothing extra. Open **Phygital Memory** from your app list.

You should see the setup page, **Set up your Phygital Memory**.

## 3. Make your first memory

The setup page asks a few questions, one at a time. Each is only clicks, plus a name and, for Encrypted, a password.

1. **What should your AI call you?** Your name, and the language for folders and rules. Your notes stay in whatever language you write.
2. **What kind of memory?** Pick one. You cannot switch later.
   - **Open** (marked **Recommended**): a normal folder. Any AI reads it, and your phone gets it through iCloud Drive, Dropbox or Google Drive.
   - **Encrypted**: opened with your password. Only the AI apps you allow get in, through this app. Not on phones yet.

   Not sure which? [Find your threat model](find-your-threat-model.md) helps you pick.
3. **Name it and pick its place.** The name, and where to keep it: this computer, a cloud folder the app found, WebDAV, or any other folder. For Encrypted, also a password of 8 or more characters, twice.
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

Keep the app open for AI apps to reach your Encrypted memories. Open memories work with the app closed too, when the AI app starts Phygital Memory itself (see [connect your AI](connect-your-ai.md#two-ways-in)). An Open memory opens straight away when you switch to it. An Encrypted memory stays unlocked until you lock it or close the app. Closing the app asks first.

## Where things are

- Your notes: the folders you chose. The first memory defaults to `~/Phygital Memory` (a folder called Phygital Memory in your home folder).
- The app's own information, the app folder:
  - Mac: `~/Library/Application Support/Phygital Memory`
  - Windows: `%APPDATA%\Phygital Memory`
  - Linux: `~/.local/share/phygital-memory`

  See [settings.md](settings.md#files-the-app-keeps).
- Your secrets: the system's own secret store. That is the Keychain on Mac, Credential Manager on Windows, and the Secret Service (such as GNOME Keyring) on Linux.

## Update

The app updates itself from the latest GitHub Release. See [updates.md](updates.md).

## Remove it

1. Quit Phygital Memory.
2. Remove the app. Mac: drag it out of Applications. Windows: **Settings › Apps › Installed apps**, then **Uninstall**. Linux: remove the package with your software installer, or delete the AppImage.
3. Delete the app folder (see [Where things are](#where-things-are)).
4. Delete the saved secrets whose names start with "Phygital Memory". Mac: in **Keychain Access**. Windows: in **Credential Manager**. Linux: in your keyring app, such as **Passwords and Keys**.
5. Your memory folders stay where they are. Delete them yourself if you no longer want the notes.

## Use it from your phone

There is no phone app, but your AI agent on the phone can still reach your memories: through remote control of an agent on your computer, your cloud, your own server, or a tunnel. See [Use it from your phone](phone.md).

## What we tested

| What | Where | Result |
|---|---|---|
| Mac (Apple chip) | Used every day, built from this repository, with the test scripts in `core/tests/` | Works |
| Linux on ARM | A virtual machine | Works |
| Windows on ARM | A virtual machine | Works (retested with 0.1.0). **Open folder** on Home did not visibly open a window |
| Linux x64, Windows x64, Intel Mac | The engine tests on GitHub's machines only | Not tried by hand yet |
| A real Finder drag, a real Touch ID unlock, a real Nextcloud server | Checked by hand | Not yet fully tested |
