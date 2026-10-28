# Glossary

The words that matter most in Phygital Memory, what each one means, and how to treat it in your language. Read it with [TRANSLATING.md](TRANSLATING.md) before you translate or review.

There is one glossary for all languages, in English. The app's texts are JSON files, so the chosen word for each language lives in `{code}.json` itself: look up the English text (the key) to see it. Use the same word for the same idea everywhere in that language.

## Names that never change

Phygital Memory, Phygital Key, Phygital Brain, GitHub, iCloud, Finder, Touch ID, Claude, Claude Code, Claude Desktop, Cursor, Codex, Syncthing, rclone, WebDAV, Nextcloud, Amazon S3, Cloudflare R2, Cryptomator.

Keyboard keys (⌘ ⇧ ⌥) stay as they are. On Windows and Linux the app turns them into Ctrl, Shift and Alt by itself.

## The memory and its two kinds

| English | What it means | How to treat it |
|---|---|---|
| memory (`Memory`) | One set of notes the app keeps: a folder, or a locked vault. The person's AI uses it. Not computer memory (RAM) | Pick the everyday word for "something you remember". Never the word for RAM or storage |
| Open (`Open@@kind`) | The kind of memory that is a plain folder, readable by any app. No password | An adjective for the memory. It is a different text from the button "Open" (open a file). The `@@kind` part tells them apart and never shows |
| Open (`Open`) | The button or action: open a note, a file, a folder | The everyday verb your apps use on a button |
| Encrypted (`Encrypted`) | The kind of memory that is a locked vault, readable only with its password | The usual word for encrypted files on your system. Keep Open and Encrypted as a clear pair |
| Unlock, Lock | Open an Encrypted memory with its password or Touch ID, and close it again | The words your system uses for unlocking and locking |
| Recovery key | The 44 words that set a new password if you forget it | The usual phrase for a recovery key or code |

## AI words

| English | What it means | How to treat it |
|---|---|---|
| AI apps | The apps that may use the memories (Claude, Cursor, Codex and others), each with its own key | "AI" as people say it in your language (KI, IA). Keep "app" short |
| AI door | A docs word for the local MCP server at `127.0.0.1:8790/mcp`. The screens say "AI apps" instead | Only in the docs, which stay English. Do not invent it in the screens |
| key | The secret an AI app uses to come in, shown once | The word for a key or access code, not a door key if your language separates them |
| Allow edits | Lets an AI app change, add, move and trash notes | A short yes or no setting |
| Private for AI | A folder or note the AI opens only when the person asks in the chat | Keep "for AI": it is private from the AI, not from the person |
| Hide from AI | Turns off all AI access to a memory | A clear action, not "delete" |
| AI tasks | One note where the person hands work to the AI (To do and Done) | A plain word for tasks or to-dos |
| Activity | The list of what AI apps did, with Undo | The word your apps use for a history or activity list |
| Undo | Puts back what the AI changed | The standard Undo of your system |

## Sharing

| English | What it means | How to treat it |
|---|---|---|
| Share | Send a memory, a folder or a file to another person, from computer to computer | The standard Share of your system |
| Invite | A one-time link that lets a person join something you share. Also the button that makes it | A noun and a verb in English. Check which one each text means |
| Can edit, Can view | The two roles of a person you share with | Short, the way document apps say them |
| Shared with me | The folder where things shared with you show up | Match the wording of popular file apps |
| Link a Mac, Link a computer | Make your own second computer become you too | "Link" as in pairing your own devices, not a web link |
| Approvals | The signed yes for each sharing change (Touch ID or an approval password) | A plain word for approval or permission |

## Places and app parts

| English | What it means | How to treat it |
|---|---|---|
| Trash | Where deleted things wait 7 days | The word your system uses (Papierkorb, Corbeille) |
| Home | The note a memory opens on | The usual word for a start or home page |
| Hidden Notes | Files whose names start with a dot | Plain words, keep "notes" |
| Storage and backup | Where a memory lives, and its backups | Plain words |
| Add memory | Make a new memory or bring one in | A short button text |

## Mac words and computer words

Texts that say "this Mac" or "Finder" have a second English text in `frontend/src/shell/pc-words.js` that says "this computer" or "your file manager". Both are in `en.json`, and both need a translation. The app shows the computer wording on every system, the Mac too, except texts about Finder, the Keychain, Touch ID and the security chip, which keep the Mac words on a Mac.

## Words to avoid

- Em dashes, three dots and the ellipsis character, in every language.
- Technical words where an everyday one works: no "vault", "repository", "token" or "endpoint" in the screens unless the English says so.
- A word that means "delete forever" where English says Trash or Remove.
