# Claude Desktop extension

For when you use Claude Desktop and want it to read your memories. When you finish, Claude Desktop can search and read your unlocked memories through one file you double-click. About 2 minutes, no terminal.

## What you need

- Phygital Memory, open, with at least one memory unlocked.
- Claude Desktop, the latest version, on the same computer.
- A Mac. The extension is made for macOS only for now: its file says so, and Claude Desktop on Windows or Linux will not install it. On Windows and Linux, connect Claude Desktop another way, or use Claude Code, Cursor or Codex: see [connect your AI app](connect-your-ai.md).

The extension is not on GitHub Releases. The app makes it for you, so it always points to your own app.

## Install

1. In Phygital Memory, open **Settings › AI apps** and press **Connect an AI app**.
2. Choose **Claude Desktop**. Pick **Which memories** it may reach, and turn on **Allow edits** only if you want it to change notes. Press **Make the key**.
3. The app shows your key once. Press **Copy** to copy it.
4. Press **Download for Claude Desktop**. The app saves `Phygital Memory.mcpb` in your Downloads folder and shows it in Finder.
5. Double-click `Phygital Memory.mcpb`. Claude Desktop opens and offers to install it.
6. Claude Desktop asks for two things:
   - **Key from Phygital Memory**: paste the key you copied.
   - **Address**: leave it as it is (`http://127.0.0.1:8790/mcp`, the app's door on your own computer).
7. Press **Install**.

> [!TIP]
> The first time you open the app, its setup page has a **Connect your AI** step with a **Download** button for Claude Desktop. That does steps 1 to 4 at once: it makes a key that may reach all your memories and edit them, saves the file in Downloads and copies the key for you. You can change what it may reach later in **Settings › AI apps**.

> [!IMPORTANT]
> The key shows only once. If you lose it before you paste it, remove the app in **Settings › AI apps** and connect it again. Never paste the key into a chat.

## First use

Open a new chat in Claude Desktop and ask:

*"Run status from Phygital Memory."*

Claude lists the memories it may use, which are unlocked, and whether it may read only or edit. Then try a real question, like *"What did I decide about the kitchen paint? Search my memory."*

## Change the settings

What Claude Desktop may reach is set in Phygital Memory, not in Claude Desktop: **Settings › AI apps**, then the Claude Desktop row. You can change the memories and **Allow edits** at any time. The change works on the next call.

To use a new key, open Claude Desktop's **Settings › Extensions › Phygital Memory** and paste it there.

## Where things are

- The file: `Phygital Memory.mcpb` in your Downloads folder. You can delete it after you install. It holds no key.
- The key: Claude Desktop keeps it as a secret in its own settings. Phygital Memory keeps only a fingerprint of it, so its own files cannot be used to get in.
- Inside the extension: a small bridge (`server/index.js`) that Claude Desktop runs with its own Node, an icon, and `manifest.json`. The bridge passes each message to the app's door on `127.0.0.1` and refuses any other address.

## Update

The extension changes rarely. If a new version of Phygital Memory says to, press **Download for Claude Desktop** again in **Settings › AI apps** and double-click the new file to install it again. Your key stays the same: paste it again if Claude Desktop asks.

## Remove

- In Claude Desktop: **Settings › Extensions**, then remove **Phygital Memory**.
- In Phygital Memory: **Settings › AI apps**, then **Remove** on the Claude Desktop row. Its key stops working at once, even if the extension is still installed.

## If it doesn't work

**Claude says "Phygital Memory isn't open on this Mac."** Open the app, unlock a memory, then ask again.

**Claude says Phygital Memory refused the key.** The key was removed or mistyped. Make a new one in **Settings › AI apps**, then paste it in Claude Desktop's **Settings › Extensions › Phygital Memory**.

**Claude says the program at Phygital Memory's address isn't your app.** Before it sends your key, the bridge checks that the app on port 8790 really is your Phygital Memory. This message means another program answered, or the app was closed. Quit other programs that use port 8790, open Phygital Memory, then try again.

**Claude Desktop will not install the file.** Update Claude Desktop to the latest version. On Windows or Linux the extension is not supported yet: see [What you need](#what-you-need).

**Claude finds nothing.** Only unlocked memories can be searched, and only the ones you picked for Claude Desktop. Check both in the app.

More in [If something goes wrong](troubleshooting.md).

## How it's built

The app writes the extension when you press the button: `_claude_desktop_ext` in `core/phygital_memory/server.py` zips `manifest.json`, the bridge from `core/phygital_memory/claude_ext/index.js` and its icon into `Phygital Memory.mcpb`. The manifest asks for the key on install and marks it as sensitive, so Claude Desktop keeps it as a secret. The bridge uses no packages. Before every message it asks the app to prove it holds this key's fingerprint (`/mcp-proof`), so a program that takes the port while the app is closed never sees the key. The extension is not built on GitHub and not checked with the official validator yet.
