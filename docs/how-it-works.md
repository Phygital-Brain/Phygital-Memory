# How it works

For when you want to know what happens inside Phygital Memory, in plain words.

## The pieces

Four pieces work together on your computer.

- **The app window.** The screens you click: the editor, search, Settings. It is a small Tauri app (Rust) that shows a web page from the local program. It also draws the menu bar and asks before it closes.
- **The local program.** A Python program the window starts. It does the real work: opens memories, searches, saves, keeps versions, backs up, shares. It listens only on your own computer, at `127.0.0.1` port `8790`. Nothing outside your computer can reach it.
- **Your memories.** Folders of notes you chose. Each one is either **Open** (a plain folder) or **Encrypted** (a vault opened with a password).
- **The AI door.** A part of the local program at `/mcp` that speaks MCP (Model Context Protocol, the standard way AI apps use tools). An AI app with a key can call the 17 tools in [tools.md](tools.md). Nothing else.

Helper programs the app ships with: Syncthing (sharing between computers) and rclone (WebDAV and S3 or R2). The GitHub backup uses your computer's own git: a Mac has it with the Command Line Tools, Windows needs Git for Windows, Linux the `git` package. They only run when you turn on the feature that needs them.

## Two kinds of memory

| | Open | Encrypted |
|---|---|---|
| What it is | A plain folder of readable files | A Cryptomator format 8 vault |
| Password | None | Yours, or Touch ID (Mac only) |
| Who can read the files | Any program or AI app that can open the folder | Nobody without the password. AI apps only through the app's door |
| Search and history | Added by the app | Added by the app, kept inside the lock |
| On your phone | Yes, if the folder is in iCloud Drive, Dropbox or Google Drive | Not yet |
| Colours | Purple with lime | Lime with purple |

You choose the kind when you make a memory. You cannot switch it later.

## What happens when you ask

1. You type a question to your AI app, for example *"What did we decide about the pricing?"*
2. Your AI app calls `search_notes` on the door, sending its key.
3. The door checks the key. It must belong to a connected app, and the memory must be unlocked, not hidden from AI, and one that app may reach.
4. The app searches the memory's index and sends back a short list: an id, the note's path, its heading and a snippet. The text starts with a label that says it is information, never instructions.
5. Your AI app calls `open_result` with an id to read that section, or `read_note` for the whole note.
6. Your AI app answers you. The text it read goes to the company that runs it.

## A change, step by step

1. You say *"Add this to my project note."*
2. Your AI app calls `read_note`, then `append_to_note` or `replace_in_note`. It can only do this if you allowed that app to edit.
3. The app keeps the old text first, as a version, and remembers how to undo the change.
4. The app writes the note. In an Encrypted memory it is encrypted as it is saved.
5. The change shows in the AI activity list (the small AI light) with an **Undo** button.
6. If you press **Undo**, the note goes back exactly as it was. If the note changed again after the AI's edit, Undo refuses, so you never lose later work. Pick an older version from the note's version history instead.

## What's stored

| What | Where | Who can read it |
|---|---|---|
| Open memory notes | The folder you chose | Anyone who can open the folder |
| Encrypted memory notes | A Cryptomator vault in the folder you chose, encrypted | Only you, with the password or recovery key |
| The search index | Memory only, rebuilt on each unlock | The running app |
| Version history | Hidden `.versions` folder inside the memory (locked in an Encrypted one) | Same as the memory |
| Trash | Hidden `.trash` folder inside the memory, kept 7 days | Same as the memory |
| AI tasks | Hidden `.ai-tasks/AI tasks.md` inside the memory | Same as the memory. Never shared |
| Per-memory settings (home note, pins, colours, Private for AI list) | Hidden `.phygital` folder inside the memory | Same as the memory |
| The list of your memories | `folders.json` in the app folder (names and places, no passwords). See [settings](settings.md#files-the-app-keeps) | You |
| AI app keys | Only a fingerprint, in `ai-apps.json` in that folder | Nobody can get the key back from it |
| Secrets (cloud passwords, GitHub sign-in, S3 keys, your personal key) | The system's secret store: Keychain (Mac), Credential Manager (Windows), Secret Service (Linux) | You, and this app |
| AI activity and Undo | Memory only, gone when the memory locks or the app quits | The running app |

## The code

- `core/phygital_memory/`: the Python program (memories, the AI door, backups, sharing).
- `core/frontend/`: the screens.
- `core/languages/`: the 41 languages.
- `app/`: the window (Tauri, Rust).
- `core/tests/`: test scripts.

To change the code, read [AGENTS.md](../AGENTS.md).

## What next

Pick another page in [the guides](README.md).

## Words you'll see

| Word | What it means here |
|---|---|
| **Memory** | One folder of notes the app looks after. You can have several. |
| **Open memory** | A plain folder of readable notes. No password. Any AI app or program that can open the folder can read it. |
| **Encrypted memory** | A locked folder (a Cryptomator format 8 vault). You open it with your password, or Touch ID on a Mac. |
| **Recovery key** | 44 words that let you set a new password for an Encrypted memory. Keep them offline. |
| **AI app** | Claude Code, Claude Desktop, Codex, Cursor or any app that can use tools through MCP. |
| **MCP** | Model Context Protocol: the standard way AI apps plug into tools like this one. |
| **The AI door** | The part of the app that AI apps talk to, at `http://127.0.0.1:8790/mcp`. It exists only while the app is open. AI apps can also start the engine themselves, which reaches Open memories with the app closed. |
| **Allow edits** | The switch that lets one AI app change notes. Off means read only. |
| **Private for AI** | A folder or note the AI opens only when you ask in the chat. The tools follow this rule. The folder itself stays readable. |
| **AI tasks** | A hidden note in each memory where you leave work for your AI. It is never shared. |
| **Phygital Brain** | An optional set of folders, rules and first notes for working with an AI. The app can build it for you. |
