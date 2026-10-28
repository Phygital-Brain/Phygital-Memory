# Tools the AI can use

For anyone who wants to know exactly what an AI app can do with a memory. The list below is every MCP tool the app offers. There are 17.

An AI app reaches these through the door at `http://127.0.0.1:8790/mcp`, with its own key. Only unlocked memories can be searched. Every answer that carries note text starts with a label saying it is information, never instructions.

## The 17 tools

| Tool | What it does | Changes anything? |
|---|---|---|
| `status` | Lists the memories this app may use, which are unlocked, how many notes each holds, and which folders are private. Also says if the app may read only or edit | No |
| `search_notes` | Searches every unlocked memory for a question in plain words. Returns ranked results: an id, the folder, the note path, a heading and a snippet. Private notes show only as a locked line | No |
| `open_result` | Reads one search result: its section, or the whole note | No |
| `around_result` | Shows the sections right before and after a result, and other notes from the same day | No |
| `read_note` | Returns the exact text of the note behind a result, as saved, with its info block. Use it before changing the note | No |
| `list_notes` | Lists a memory's notes, files and subfolders by path (up to 500), or what is inside one subfolder | No |
| `recent_changes` | Lists the notes and files changed most recently, newest first | No |
| `read_file_text` | Reads the text inside a note or file: Markdown, plain text, CSV, Word (`.docx`) or PDF. Long text is cut | No |
| `links_to` | Lists the notes that link to a note with `[[wiki links]]`, with the line of each link | No |
| `handed_notes` | Lists your AI tasks: the To do list of the `AI tasks` note, oldest first, each with what you asked and the note in full | No |
| `replace_in_note` | Changes part of a note: replaces `old_text`, which must appear exactly once. Needs edit permission | Yes |
| `append_to_note` | Adds text at the end of a note. Needs edit permission | Yes |
| `create_note` | Makes a new note. Refuses if a note is already at that path. Needs edit permission | Yes |
| `move_note` | Moves or renames a note, file or subfolder inside the same memory. Needs edit permission | Yes |
| `make_folder` | Makes a subfolder. Needs edit permission | Yes |
| `trash_note` | Puts a note, file or subfolder in the app's trash, where you can put it back for 7 days. Needs edit permission | Yes |
| `finish_handed_note` | Ticks an AI task off with a one or two sentence note of what was done. You see it in the app. Needs edit permission | Yes |

Ten tools only read. Seven can change things. None of them can delete anything for good, unlock a memory, change a setting, or touch a password.

## How unlocking reaches you

No tool unlocks anything. If no memory is unlocked, the tools answer with a message that says so and tells the AI to ask you to unlock it in the app. They never ask for a password. You unlock with your password or Touch ID, in the app.

## Naming a note

Edits take a note by `path` (like `Projects/plan.md`, which stays valid after edits) or by an `id` from a search or from `handed_notes`. When several memories are unlocked, say which with `folder`.

## Private notes

Most tools that read or write a note take a `private` option (all except `status`, `recent_changes`, `handed_notes` and `finish_handed_note`). It must be `true` only when you asked, in the chat, for something in a folder you keep private. Hidden files like `.env` count as private. Without `private=true` the tools refuse.

## When a tool says no

| Message | What it means |
|---|---|
| This AI app isn't connected | The key is not in **Settings › AI apps**. Connect the app |
| This AI app may only read | The app was not given **Allow edits** |
| No memory this app may use is unlocked | Everything is locked, hidden from AI, or not given to this app |
| That folder isn't known. Search again | The id is for a memory the app may not reach, or an old id |
| The folder is locked now | You locked it. Unlock it in the app |
| Several folders are open: say which one with folder | Add `folder=<name>` |
| Is in a folder the person keeps private from AI | Private for AI. Ask in the chat, then the AI calls again with `private=true` |
| old_text must appear exactly once in the note | The text is missing or repeated. Read the note again, copy it exactly |
| A message that something already exists at that path | `create_note` never overwrites |
| That PDF can't be read | It is a scan, or has its own password |

## Limits

- `search_notes` returns 1 to 20 results (default 8).
- `recent_changes` returns 1 to 50 (default 15).
- `list_notes` shows up to 500 paths. Use `inside` to look in one subfolder.
- `read_file_text` cuts text at 60,000 characters, reads the first 200 pages of a PDF, and reads only notes, text, CSV, Word and PDF files.
- A note can be up to about 2 MB. Bigger text files are not searched.
- The last 50 AI changes can be undone, and only while the memory stays unlocked.

## Asking first

The tools do not ask you per call. You decide ahead of time in **Settings › AI apps**: which memories an app may reach, and whether it may edit. Signing in an app that supports MCP sign-in needs you to press **Allow** in the app. Every call is listed in **Activity**, and every change has **Undo**. You can mark a folder **Private for AI** so the AI has to ask you in the chat first.

## What next

See [examples.md](examples.md) for things to ask, and [safety.md](safety.md) for what to turn on first.
