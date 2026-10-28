# Privacy

What is kept, where, and who can see it.

## What leaves your computer

Nothing leaves your Mac unless you press a button that needs it. There is no account, no tracking, no usage reports and no server of ours. The app does not check for updates yet.

These are the only outside calls, and each one starts with you:

| What | When | Where it goes | What it sends |
|---|---|---|---|
| Sign in with GitHub | You press **Sign in with GitHub** | `github.com` (you approve a short code in your browser) | The code request. The key you get back is kept in your Keychain |
| GitHub backup | You turn it on for a memory | A private repo on `github.com` | Open memory: your readable notes and their history. Encrypted memory: encrypted files only |
| WebDAV | You connect a WebDAV server | The server you typed, through rclone | Encrypted files for an Encrypted memory. Readable files for an Open memory |
| S3 or R2 | You connect a bucket | The endpoint you typed, through rclone | Same as WebDAV |
| Sharing and linking a Mac | You invite someone, or link your other Mac | The other Mac, straight, through the app's own Syncthing. Syncthing's public discovery and relays can help the two Macs find each other | Encrypted files only. The relays see encrypted traffic |
| A backup file | You press **Save backup file** | A file you choose on your Mac | Nothing leaves the Mac |
| Cloud folders (iCloud Drive, Dropbox, Nextcloud, Google Drive) | You put a memory in one | That app, not this one | Whatever is in the folder. An Encrypted memory shows as encrypted files |

Syncthing here is the app's own copy, with its own keys. It is off until something is shared, and its usage reports, crash reports and auto-updates are off.

The setup message you can paste into your AI app points your AI at Phygital Brain's setup guide on GitHub. That is your AI app fetching it, not this app.

## What the AI app sees

Whatever the AI reads for you goes to the company that runs your AI app. That includes search results, notes it opens and file text it reads. Phygital Memory cannot take it back. Each AI app only sees the memories you gave it, and only the notes it asks for. Notes marked **Private for AI** reach it only when you ask in the chat. A memory marked **AI can't see this** never reaches it.

An AI app connected to the **Open** memory's folder, or to its GitHub or cloud copy, can read those files without going through this app at all.

## What's kept

| What | Where | Who can read it |
|---|---|---|
| Open memory notes | The folder you chose | Anyone who can open the folder |
| Encrypted memory notes | A Cryptomator vault in the folder you chose | Only you, with the password or recovery key |
| Search index | App memory only, rebuilt on unlock | The running app |
| Version history, trash, AI tasks, per-memory settings | Hidden `.versions`, `.trash`, `.ai-tasks`, `.phygital` folders inside the memory (locked inside an Encrypted memory) | Same as the memory |
| Your memories list | `folders.json` in `~/Library/Application Support/Phygital Memory` | You. Names and places only, never a password or key |
| AI app list | `ai-apps.json` there | You. Fingerprints of keys, not the keys |
| Approvals | `approvals.jsonl` and `approvals-signed.jsonl` there | You. What you said yes to, sealed |
| Your name, your approval key card | `me.json`, `approver.json` there | You. The name others see when you share |
| Passwords and secrets | The Mac's Keychain | You and this app |
| AI activity and Undo | App memory only. Gone when the memory locks or the app quits | The running app |
| Look and language settings | The app window's local storage | You |

Passwords are never written to a file. Touch ID keeps your memory password in the Keychain, readable only by this app after your fingerprint.

## Sharing

When you share a memory, a folder or a file, the shared part goes into its own small locked memory with its own key. Only that travels. The key is locked to your personal key and to each person you let in. Nothing is sent before you press **Let in**. People you share with can see the names you gave things and the name you set in **Settings**. Your AI tasks are never part of a share.

## Logs of the program itself

The local program writes no log files. It prints one line at start-up (the app address) to the terminal it was started from, and nothing from your notes. The AI activity list is kept in memory only and is gone when the memory locks.

## Deleting everything

1. Quit Phygital Memory.
2. Drag the app out of Applications.
3. Delete `~/Library/Application Support/Phygital Memory`.
4. Open **Keychain Access** and delete the items whose names start with "Phygital Memory".
5. Delete your memory folders if you no longer want the notes. They are ordinary folders you chose. The first one is `~/Phygital Memory` unless you picked another place.
6. If you used GitHub, WebDAV or S3, delete the copies there yourself.

## What next

Read [safety.md](safety.md) and [threat-model.md](threat-model.md).
