# Find your threat model

For when you make a new memory and have to pick **Open** or **Encrypted**. You can't switch later, so this page helps you pick once. You leave knowing which one fits you, and why.

A threat model is a short answer to two questions: **what do you want to keep safe, and from whom?** This page uses the simple grid from [Techlore](https://techlore.tech) (their Techlore Dispatch guide to threat modeling), adapted for notes, and then turns your answers into Open or Encrypted.

> [!TIP]
> Not sure? Pick **Open**. It fits most people, and it's the one the app marks **Recommended**.

## The two kinds, in one line each

- **Open:** a normal folder of Markdown files. Anyone and anything that can open the folder can read it: you, your AI apps, your cloud app, and a person at your unlocked computer.
- **Encrypted:** the files are scrambled with your password (the Cryptomator format). Your cloud, a backup or a stolen disk only see scrambled files. You and your AI apps read it only through the Phygital Memory app, while it's unlocked.

## Step 1: fill in the grid

Draw this grid on paper, or just think it through. For each box, give a score from **1** (I don't worry about this) to **3** (this matters a lot), and one line on what you want to protect.

| | **People** (family, coworkers, a thief, an ex) | **Companies** (your cloud, AI providers, advertisers) | **Leaks and loss** (a lost or stolen laptop, a hacked account, a data breach) |
|---|---|---|---|
| **Security:** nobody changes or destroys my notes | | | |
| **Privacy:** nobody reads my notes | | | |
| **Anonymity:** nobody knows the notes are mine | | | |

The three rows mean different things:

- **Security** is about your notes staying whole: not lost, deleted or changed.
- **Privacy** is about who can read what you wrote.
- **Anonymity** is about who knows it's you.

## Step 2: read your grid

**Security row.** Both kinds keep version history, a 7-day trash and backups, and every AI change can be undone. Security alone doesn't decide the kind. Turn on a backup either way.

**Privacy row.** This row decides the kind.

- **Mostly 1s:** Open. Your notes are no more private than your other files, and that's fine for you.
- **A 3 under People:** think about who uses your computer, and where your laptop goes. Encrypted locks when you lock it or quit the app. An Open memory is readable by anyone at your unlocked computer.
- **A 3 under Companies:** Encrypted, if your notes sit in a cloud folder (iCloud Drive, Dropbox, Google Drive, a GitHub backup). The cloud then only stores scrambled files.
- **A 3 under Leaks and loss:** Encrypted, and lock it when you leave your computer or travel with it. A lost laptop or a leaked cloud account then shows only scrambled files. See [threat-model.md](threat-model.md) for what the app does and doesn't protect.

**Anonymity row.** Neither kind hides who you are, and Phygital Memory isn't made to. Your cloud account, your GitHub account and your AI app all know it's you.

> [!IMPORTANT]
> **What you show an AI app, its company sees.** When your AI reads a note to answer you, that text goes to the AI's company (Anthropic, OpenAI and others), whatever the kind. Encrypted protects the files where they're kept. It doesn't stop your AI from sending what it reads. To keep a note from AI, mark it **Private for AI**, or hide the whole memory from AI.

## Step 3: one sentence

Write one sentence that sums up your grid, like the people below. Check every choice against it later: which cloud, which AI app, which backup.

## People and what they picked

**Maya, illustrator, notes on clients and ideas.** "I want my AI to find my client briefs fast, on my laptop and my phone." Privacy from people: 1. From companies: 1. She keeps the memory in iCloud Drive so her phone sees it. **Open.**

**Tom, student.** "Class notes and reading lists. If someone saw them, nothing would happen." Every box is a 1 or a 2. **Open**, with a GitHub backup so nothing gets lost.

**Ana, freelance developer, notes in Dropbox.** "Work notes are fine to show, but my journal isn't." Two memories: an **Open** one for work, and an **Encrypted** one for the journal. You can have as many memories as you like, each of its own kind.

**Leo, therapist.** "Session notes about clients must never be readable by my cloud or by anyone who gets my laptop." Privacy from people: 3. From companies: 3. **Encrypted.** He keeps those notes out of AI too: the memory is marked **AI can't see this**.

**Sara, journalist.** "The people I interview trust me with their names. Those notes must stay safe if my laptop is lost or my cloud account leaks." Privacy from people: 3. Leaks and loss: 3. **Encrypted**, locked when she travels, and the interview notes marked **Private for AI**.

**Ken, small business owner.** "Prices, plans and supplier deals. A competitor seeing them would hurt." Privacy from companies: 2, from people: 2. He works mostly with his AI on one computer. **Encrypted** if the memory goes to a shared cloud; **Open** if it stays on his own computer only. He picked Encrypted to be safe.

## What you give up with Encrypted

- **No phone, yet.** An Encrypted memory opens only in the app, and there's no phone app.
- **The app must be open and unlocked** for AI apps to reach it. An Open memory works with the app closed, when the AI app starts Phygital Memory itself (see [connect your AI](connect-your-ai.md#two-ways-in)).
- **The password matters.** Keep the 44-word recovery key safe. Without the password or the recovery key, nobody can open the notes.
- **Other apps can't read the folder** directly. They go through Phygital Memory.

## What you give up with Open

- **Anyone with the folder can read it:** your cloud, a person at your unlocked computer, any program you run.
- **Backups and cloud copies are readable files** too.

## What next

Make your memory: [setup-computer.md](setup-computer.md). Then [connect your AI](connect-your-ai.md). For the details of what the app protects, read [threat-model.md](threat-model.md) and [safety.md](safety.md).
