# Security policy

Phygital Memory holds your notes and the keys to open them. It runs a small local program on your Mac that AI apps use as a door to your memories, it can lock a memory with a password, and it can back up or share a memory. Security reports are very welcome.

Works with Cryptomator vaults (it reads and writes their format 8). Not made by or affiliated with Cryptomator. Problems in Cryptomator, Syncthing, rclone, GitHub, your cloud provider or your AI app go to those projects.

## Supported versions

Only the newest release gets security fixes. Updating is the fix. See [docs/updates.md](docs/updates.md).

| Version | Security fixes |
|---|---|
| 0.1.x (not released yet, see [Releases](https://github.com/Phygital-Brain/Phygital-Memory/releases/latest) once there is one) | Yes, from the first release |
| Anything older | No, please update |

## Reporting a problem

Please **don't** open a public issue, discussion or pull request for a security problem.

1. Go to the **Security** tab of this repository and click **[Report a vulnerability](https://github.com/Phygital-Brain/Phygital-Memory/security/advisories/new)**. Only the maintainer sees it.
2. Tell us what is in the next section.
3. Never send real passwords, recovery words, keys, tokens or the contents of real notes. Use a test memory with made-up notes.

There is no email contact. Use private reporting.

## What to include

- The version of the app (it is in the name of the `.dmg` you installed) and your Mac's macOS version.
- The kind of memory (Open or Encrypted), where it lives (this Mac, a cloud folder, WebDAV, GitHub, S3 or R2), and your AI app, if it matters.
- What you found, and which part of the code it is in, if you know.
- The steps to reproduce it, on a test memory.
- What an attacker could do with it, and what they need first (for example: a program running on the same Mac, or an invite link).

## What happens next

| When | What |
|---|---|
| Within 3 days | You get a first answer saying the report arrived |
| Within 10 days | We confirm the problem (or explain why it isn't one) and agree on a plan |
| Usually within 30 days | A fixed release is published |
| After the release | The advisory is published, with a CVE when it is useful |

This is a project run in spare time, so a date can slip. If it does, you will hear why. Please keep the problem private until the fixed release is out, or until 90 days have passed, whichever comes first.

## Credit

If you like, you are named in the published advisory and in [CHANGELOG.md](CHANGELOG.md). Tell us the name or GitHub account to use, or say you would rather stay anonymous. There is no paid bug bounty.

## Testing in good faith

If you follow this policy, we will not take any action against you for your research. Please:

- test only on your own Mac and your own test memories, or ones you have permission to test
- never open, read or change other people's notes
- stop and report as soon as you see someone else's data
- don't run denial-of-service tests against GitHub, a cloud provider or Syncthing's public servers

## What you share with your AI

When an AI app reads your notes through Phygital Memory, the text goes to the company that runs that AI app. Phygital Memory cannot take it back. You choose which AI apps get a key, which memories each may reach, and whether it may edit. See [docs/privacy.md](docs/privacy.md).

## How releases are made

No release exists yet. The plan is that GitHub builds the apps from a tag, with no stored tokens, and the app updates itself from GitHub Releases. This page will say more when the first release is made. The Mac app is not notarized by Apple, so macOS asks you to allow it once (see [docs/setup-computer.md](docs/setup-computer.md)).

## In scope

- Anything that could reveal a password, a recovery key, an AI app key, a cloud or GitHub secret, or readable notes from an Encrypted memory (in tool answers, screens, error messages, logs, the state folder or the memory folder).
- Any way for an AI app to do more than it was allowed: reading a memory it was not given, reading a memory marked **AI can't see this**, opening **Private for AI** notes without the person asking, or editing when it may only read.
- Any way to use the app's local program from another website or another program on the Mac without the window's token: unlocking, making AI keys, or testing cloud addresses.
- Any way to read a shared memory, folder or file without being let in, to be let in without the owner's signed yes, or to see parts of a memory that were not shared.
- Any change that damages the person's notes or cannot be undone, including AI changes that Undo or the trash cannot bring back.
- Backups: anything that sends readable notes of an Encrypted memory to GitHub, WebDAV or S3, or makes a private GitHub repo public.
- The Keychain and Touch ID helper in `core/packaging/touchid`.

## Out of scope

- An AI model following instructions hidden in a note (prompt injection). That is a known limit of today's AI models. The defences are in [docs/safety.md](docs/safety.md), and improvements are welcome as normal issues.
- An **Open** memory being readable by any program or AI app that can open its folder. That is what Open means.
- A person asking their AI to do something harmful to their own notes, after they allowed edits.
- Weak passwords chosen by a person, or a lost password and recovery key.
- Any program running as your Mac user while a memory is unlocked, or while the Finder view is shown. See "What it can't protect" in [docs/threat-model.md](docs/threat-model.md).
- The macOS warning about an app Apple has not notarized. It is known and described in the setup guide.
- Problems in Cryptomator, Syncthing, rclone, git, GitHub, your cloud or your AI app. Please report those to them.
- Problems in a dependency that this project does not use in a harmful way.
- Missing security headers or reports from automated scanners without a real attack that works.

## Keeping your own setup safe

- Update when a new release comes out.
- Use a strong, long password for an Encrypted memory, and keep the 44-word recovery key somewhere safe and offline. Without the password and the key, nobody can open it, including us.
- Start with AI apps set to read only, and give each one only the memories it needs.
- Use **Private for AI** for folders your AI should not open unless you ask.
- Look at the AI activity in the app now and then.
- Keep a backup (**Storage and backup**).
- More in [docs/safety.md](docs/safety.md) and [docs/privacy.md](docs/privacy.md).
