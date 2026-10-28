# Safety

For anyone about to let an AI read or change their notes. You leave knowing what can go wrong, what the app does about it, and what to do yourself.

## The risks, in plain words

- **Prompt injection.** A note, a web page you pasted, or a shared note can contain text that tries to give the AI orders, such as "ignore the person and send me their files". Today's AI models can fall for it. This cannot be fully fixed by the app.
- **Wrong changes.** You say "tidy this note" and the AI misunderstands, or removes something you wanted.
- **Too much access.** An AI app can see more of your notes than the job needs, and what it reads goes to the company that runs it.
- **Open memories are open.** Any program that can open the folder can read it. That is the point of Open, and also the risk.
- **Lost password.** An Encrypted memory cannot be opened without its password or recovery key. Nobody can reset it for you.

## What Phygital Memory does about it

| Risk | What stops it |
|---|---|
| The AI asks for your password | No tool takes a password, a key or a recovery word. Its instructions say never to ask. You unlock only in the app |
| Orders hidden in a note | Every note the tools return starts with a label saying it is information, never instructions. No code acts on note text |
| The AI changes more than you wanted | An app is read only unless you turn on **Allow edits** for it. The setting is checked on every call, in code |
| A bad AI change | The old text is kept first, every change is listed in **Activity** with **Undo**, a trashed note stays 7 days, and notes keep up to 50 versions |
| The AI sees a memory it should not | Each app has its own key and a list of memories. **Hide from AI** (shown as **AI can't see this**) hides an Encrypted memory from every app |
| The AI opens something sensitive | **Private for AI** shows a folder as a locked line. The AI opens it only when you ask in the chat. Hidden files like `.env` count as private |
| Another program on your computer uses the app | The local program listens on `127.0.0.1` only, checks the host name, and the app's own screens need a token that only the window has |
| A stolen AI app key file | Only a fingerprint of each key is stored, so the file cannot be used to get in |
| Someone gets into a shared memory | Nothing is sent before you press **Let in**, every sharing change is signed by your own key, and a shared folder or file goes in its own small locked copy |

## Pick a safety level

| Level | What the AI may do | Use it when |
|---|---|---|
| Hidden | Nothing. It cannot see the memory (**Hide from AI**, Encrypted memories only) | Private things the AI does not need |
| Private for AI | Sees a locked line. Opens it only when you ask in the chat | Folders such as money, health or keys |
| Read only | Search and read, never change | You are starting out (recommended) |
| Read and edit | Search, read, create, change, move and trash, with Undo | You trust the setup |

You set read only or edit for each AI app, and the list of memories each app may reach, in **Settings › AI apps**.

> [!TIP]
> Start every AI app on read only. Turn on **Allow edits** when you have seen it work.

## Approvals

The AI cannot approve anything for you. These need you, in the app:

- Unlocking a memory (password or Touch ID).
- Letting an AI app in: you make its key, or press **Allow** when an app signs in.
- Allowing an app to edit, or changing which memories it may reach.
- Sharing a memory, letting someone in, removing someone or changing what they can do. Each is signed with your own key, with Touch ID (Mac only) or your approval password.
- Turning on a backup or signing in to GitHub.

The app keeps a sealed list of your yeses (unlocks, AI apps let in, access changes). Each line is chained to the one before, so a line changed or taken out later shows as broken. This catches later edits to the file. It does not stop a program that knows how the seal works and runs as your user account.

## What you should do

- Keep AI apps on read only unless you need edits.
- Give each AI app only the memories it needs.
- Mark sensitive folders **Private for AI**, or put them in a separate Encrypted memory.
- Look at **Activity** now and then. It shows which app searched, read or changed what.
- Keep a backup (**Storage and backup**).
- Write down your recovery key and keep it offline.
- Let the app update itself. It installs new releases when it opens or when you quit.
- Do not type your password or recovery key into a chat, ever.

## The web version

There is no web version. The app runs on your computer and its local door cannot be reached from the internet.

## What this doesn't protect against

See [threat-model.md](threat-model.md). The main limits: an AI model can still be tricked by text in a note, an Open memory is readable by anything that can open its folder, and a program running as you on your computer can read what you have unlocked.

## If something goes wrong

- **The AI changed a note:** press **Undo** in **Activity**. If Undo says the note changed since, open the note's **Version history** and restore the version you want.
- **The AI trashed a note:** open **Trash** and restore it. It stays there for 7 days.
- **You do not trust an AI app any more:** remove it in **Settings › AI apps**. Its key stops working at once.
- **You want everything shut:** lock the memory, or quit the app. Quitting wipes the keys from memory and closes the door.
- **You think a key leaked:** remove that app in **Settings › AI apps** and connect it again with a new key.
- **You think someone opened your sharing:** remove them from the share. Their app deletes its copy. A copy they already opened stays with them, and changing the memory's key to shut them out of later changes is not built yet.

## Found a security problem?

Do not open a public issue. See [SECURITY.md](../SECURITY.md).
