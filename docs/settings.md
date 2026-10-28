# Settings

For when you want to change how the app looks or behaves, or find where something is kept. Phygital Memory has no `.env` file. Settings are buttons in the app, plus a few environment variables for developers.

## Where settings come from

- **In the app:** **Settings** (the window with tabs), and **Storage and backup** for places and backups. Most people only use these.
- **Per computer:** look and language settings live in the app window's local storage, so they belong to this computer, not to your notes.
- **Per memory:** a memory's own choices (home note, pins, colours, which folders are Private for AI) live inside the memory, in its hidden `.phygital` folder, so they follow the notes. In an Encrypted memory they are encrypted.
- **Environment variables:** for developers and tests. The built app sets `PHYGITAL_MEMORY_FOLDER` and `PHYGITAL_MEMORY_PORT` itself.

## General

| Setting | Default | What it does |
|---|---|---|
| Language | System | The app's words. System follows your computer. Note and folder names stay as you wrote them. See [languages.md](languages.md) |
| Theme | System | Light, dark, or follow your computer |
| Editor font size | 16 | Text size in the editor, from 13 to 22 |
| Show properties | On | Shows or hides the info block at the top of a note, like tags and dates |
| Desktop icon | On | While a memory is unlocked, puts a shortcut on your Desktop |
| Finder: Show (Mac only for now) | Off | Shows an unlocked Encrypted memory as a folder in Finder. While it is shown, any app on your Mac can read your notes. It closes when you lock |

## This memory

| Setting | Default | What it does |
|---|---|---|
| Rename | none | Changes the memory's name |
| Show | none | Shows the real files in Finder (in the file manager off the Mac). For an Encrypted memory they are encrypted, and only you can read them with your password |
| Show hidden files | Off | Shows files and folders whose names start with a dot, like `.env`, in **Hidden Notes** at the bottom of the list |
| Unlock with Touch ID | Off | Keeps your password in the Mac's Keychain, readable only by this app after your fingerprint (Encrypted memories, Mac only) |
| Recovery key | none | Shows the 44 words that set a new password if you forget it. It asks for your password first (Encrypted memories) |
| Hide from AI | Off | Turns off AI access to this memory, whatever each app is allowed (Encrypted memories only) |
| Private for AI | none | Set from a folder's or note's menu. The AI opens it only when you ask in the chat |

## You

| Setting | Default | What it does |
|---|---|---|
| Your name | Your account's name | What others see when you share a memory with them or join one |
| Link a computer | none | Makes your other computer, or your own server, become you too, with no cloud and no account. One window with three ways in: **To my server** (type its address and passphrase, the app does the rest), **Send to a computer** (shows a link) and **Receive from a computer** (paste that link). The memories you pick sync between them, through Syncthing. Both must be online at the same time |
| Approvals | Set up the first time you share | How you sign sharing changes: Touch ID with the security chip (Mac only), or an approval password |

## AI apps

| Setting | Default | What it does |
|---|---|---|
| Connect an AI app | none | Makes a key for an AI app and shows the setup to paste. The key is shown once |
| Which memories | All memories, also new ones | The memories this app may reach |
| Allow edits | Off | Lets the app change, add, move and trash notes. You can undo every change |
| Remove | none | Removes the app. Its key stops working at once |

## Storage and backup

| Setting | Default | What it does |
|---|---|---|
| Stored in | This computer | Where a memory lives: this computer, a cloud folder, WebDAV, or any other folder |
| Private GitHub | Off | Keeps a copy and every past version in a private repo. Files over 95 MB stay out, and the memory up to about 5 GB. Uses your computer's own git: a Mac has it with the Command Line Tools, Windows needs Git for Windows, Linux the `git` package |
| WebDAV | Off | Keeps the memory in step with a WebDAV server, or only on it (**WebDAV only**, nothing kept on the computer). WebDAV only is built in on Mac, needs WinFsp on Windows, and FUSE (`fuse3`) on Linux |
| Amazon S3 or Cloudflare R2 | Off | Backs up to a bucket. Any file size, and replaced files are kept in history |
| Backup file | none | Saves one `.zip` you can keep anywhere. Encrypted memories zip as encrypted files |

## Environment variables

| Variable | Default | What it does |
|---|---|---|
| `PHYGITAL_MEMORY_FOLDER` | `~/Phygital Memory` | The folder of the first memory |
| `PHYGITAL_MEMORY_PORT` | `8790` | The port of the local program. The app always uses 8790 |
| `PHYGITAL_MEMORY_STATE` | The app folder (see [below](#files-the-app-keeps)) | Where the app keeps its own information |
| `PHYGITAL_MEMORY_SHARED_COPIES` | `~/Documents/Shared with me` | Where a shared Open memory becomes a normal folder on the other computer |
| `PHYGITAL_MEMORY_TRASH` | Mac: `~/.Trash`. Linux: `~/.local/share/Trash/files`. Windows: `Moved away` in the app folder | Where old copies go when you move a memory |
| `PHYGITAL_MEMORY_MOUNTS` | `~/Library/Application Support/Phygital Memory/Finder` | Where the Finder view is mounted (Mac only) |
| `PHYGITAL_MEMORY_DESKTOP` | `~/Desktop` | Where the Desktop shortcut goes |
| `PHYGITAL_MEMORY_MAC_NAME` | Your Mac's name | The name your other computer sees when linking |
| `PHYGITAL_MEMORY_RCLONE` | the bundled rclone | Path to another rclone |
| `PHYGITAL_MEMORY_TOUCHID` | the bundled helper | Path to another Touch ID helper (Mac only; source runs only, the built app never uses it) |
| `PHYGITAL_MEMORY_GITHUB_CLIENT_ID` | the app's public one | A different GitHub OAuth app, for testing |
| `PHYGITAL_MEMORY_SYNCTHING_HOME` | `STATE/syncthing` | Where the app's Syncthing keeps its files |

Set by the window for the program, never by you: `PHYGITAL_MEMORY_SHELL_TOKEN`, `PHYGITAL_MEMORY_SERVER_PROOF`, `PHYGITAL_MEMORY_APP_PID`.

On a server ([Run it on your own server](server.md)): `PHYGITAL_MEMORY_SERVER` (`1` turns server mode on), `PHYGITAL_MEMORY_URL` (the server's address), `PHYGITAL_MEMORY_PASSPHRASE` (optional: the passphrase as a setting, instead of choosing it on the first visit), `PHYGITAL_MEMORY_DATA` (where memories and settings live), `PHYGITAL_MEMORY_SYNC_PORT` (the one port for syncing with your computers), `PHYGITAL_MEMORY_SYNC_ADDRESS` (where computers reach that port, when it isn't your address's name and the sync port) and `PHYGITAL_MEMORY_VERSION` (set by the image, shown on the page). The server image sets all but the address.

Test hooks, used only by `core/tests/`: `PHYGITAL_MEMORY_OFFLINE`, `PHYGITAL_MEMORY_SYNCTHING_LOCAL`, `PHYGITAL_MEMORY_SYNCTHING_NO_LAN`, and the Keychain item names `PHYGITAL_MEMORY_SEAL_KEYCHAIN`, `PHYGITAL_MEMORY_CLOUD_KEYCHAIN`, `PHYGITAL_MEMORY_APPROVER_KEYCHAIN`, `PHYGITAL_MEMORY_IDENTITY_KEYCHAIN`, `PHYGITAL_MEMORY_TOUCHID_KEYCHAIN`. Do not set these on your real computer.

## Files the app keeps

All in the app folder unless noted:

- Mac: `~/Library/Application Support/Phygital Memory`
- Windows: `%APPDATA%\Phygital Memory`
- Linux: `~/.local/share/phygital-memory`

| File or folder | What it holds |
|---|---|
| `folders.json` | The list of your memories: names and places. Never a password or key |
| `ai-apps.json` | Your AI apps and what each may reach. Key fingerprints only |
| `approvals.jsonl` | The sealed list of your yeses |
| `approvals-signed.jsonl` and `approver.json` | Signed sharing approvals and your approval key card (the public part) |
| `me.json` | Your name and your personal key's public half |
| `shares/` | Shared parts: each is a small locked memory, plus bookkeeping |
| `syncthing/` | The app's own Syncthing |
| `git/`, `webdav/`, `clouds/`, `ai-tasks/` | Bookkeeping for the GitHub backup, WebDAV sync, cloud-only memories, and older AI task files |
| `Finder/` | Where the Finder view is mounted while shown (Mac only) |
| `engine.log` | Errors from the built app's local program. Past 1 MB it starts again and keeps `engine.old.log` |
| Inside each memory: `.trash`, `.versions`, `.phygital`, `.ai-tasks` | Trash, version history, per-memory settings, AI tasks |
| The system's secret store: Keychain (Mac), Credential Manager (Windows), Secret Service such as GNOME Keyring (Linux) | Cloud passwords, the GitHub sign-in, S3 keys, the approvals seal key, your personal key, the Touch ID copy of a password (Mac only) |

## What next

See [privacy.md](privacy.md) for who can read each of these.
