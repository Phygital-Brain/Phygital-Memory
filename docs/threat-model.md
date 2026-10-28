# Threat model

For anyone deciding where to use Phygital Memory. It says what the app protects against and what it cannot, so you can decide what to put in it.

## What it protects

| Situation | What happens |
|---|---|
| Someone gets your Encrypted memory folder (a stolen drive, a cloud account, a GitHub backup) | They see Cryptomator format 8 encrypted files. File names are encrypted too. They need your password or recovery key |
| An AI app wants your password | No tool takes one, and the AI's instructions say never to ask. You unlock only in the app |
| An AI app wants more than you allowed | Which memories it may reach, and read only versus edit, are checked in code on every call. An invalid or unknown app gets nothing |
| An AI app makes a bad change | The old text is kept. **Undo** puts it back while the note is untouched since. Trashed notes stay 7 days. Notes keep up to 50 versions |
| An AI app wants a folder you marked **Private for AI** | Search shows a locked line only. The tools refuse to open it unless the call says you asked in the chat |
| The file with AI app keys is read by another program | It holds fingerprints (SHA-256) of keys, not keys |
| A web page tries to use the app's local door | The program listens on `127.0.0.1` only, checks the host name and origin, and its own screens need a token only the window has |
| A program on your computer tries to unlock, or to make AI keys | The app's `/api` needs the window's token. On a Mac, Touch ID and Keychain use go through a helper that only answers this app's own program |
| Someone guesses your memory password | After 5 wrong tries, unlocking pauses for a minute. The vault uses scrypt, as Cryptomator does |
| A shared folder or file reveals the rest of the memory | A shared part goes into its own small locked memory with its own key, so the rest is out of reach, not only hidden |
| Someone is let into a share without you knowing | Nothing is sent before you press **Let in**, and each sharing change is signed with your own key |
| A GitHub backup becomes public | Before each push the app asks GitHub again. If the repo turned public, it stops |

## What it can't protect

| Situation | Why, and what to do |
|---|---|
| Any program running as you on your computer, while a memory is unlocked | An unlocked memory lives in the app's memory, and the same user can in principle reach it. Keep malware off your computer. Lock a memory when you are done |
| The Finder view (Mac only for now) | While it is shown, any program of your user account can read the files, AI tools with a shell included. It closes when you lock. Show it only when you need it |
| An Open memory | It is a plain folder. Any program or AI app that can open it can read it, with no key. Use Encrypted for anything private |
| What you let the AI read | It goes to the company that runs your AI app. Use read only, **Private for AI**, or hidden for sensitive things |
| Instructions hidden in your notes | A known limit of AI models (prompt injection). The tools label note text as data, but the AI may still be fooled. See [safety.md](safety.md) |
| **Private for AI** | It is a rule the tools enforce, not encryption. A program reading an Open memory's folder is not stopped |
| A forged approvals list | The sealed list catches later edits to the file. A program that runs as you and can read the seal key from the system's secret store could forge lines. Signed Phygital Key receipts are the planned upgrade |
| Someone you removed from a share | Their app deletes its copy, but a copy they already opened stays with them. Changing the memory's key to shut them out of later changes is not built yet |
| A shared memory when one of the two computers is off | Changes do not travel. They wait until both are online with the app open. This is not a safety limit, only a limit on sync |
| A lost password and recovery key | Nobody can open the memory, including us |
| Weak passwords | Use a long one. Eight characters is the minimum the setup page accepts |
| Problems in Cryptomator's format, Syncthing, rclone, git or your cloud | Report those to them |
| A computer that is not yours | Do not unlock memories on it |

## On your own server

[Phygital Memory Server](server.md) puts the page and the AI door on the internet, so the protection changes:

- **The passphrase is the lock.** Anyone with it can open the page. Ten wrong tries close the door for 15 minutes. The login is a cookie that only the server's own page can use.
- **Other sites can't act for you.** Changes are accepted only from the server's own address, and only with the login.
- **Whoever controls the server can read open memories.** An Encrypted memory is readable on the server from the moment you unlock it until you lock it or the server restarts. Use a server you trust.
- **Secrets sit in one file on the server's disk**, readable only by the server, not in a keychain. Keep the server's disk private.

## Not audited yet

Nobody outside the project has audited the code. It is not certified and we do not claim it is secure. The tests in `core/tests/` check the rules in [AGENTS.md](../AGENTS.md), but tests are not an audit. A security review of the whole app is planned. The Windows and Linux builds use new code in some places (the secret store, the pickers, the file manager) and need the same review. Windows is not fully tested yet.

## What next

Read [safety.md](safety.md) for what to do, and [SECURITY.md](../SECURITY.md) to report a problem.
