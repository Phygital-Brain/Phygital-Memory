# Languages

For when you want the app in another language, or want to fix a translation. You leave knowing which language you see and how to change it.

The screens of the app come in **41 languages**, and an AI agent can add more with one command. The AI tools and these docs stay in English: your AI app talks to you in your own language and explains for you.

## Which language you see

The app follows your Mac. If there is no file for your Mac's language, you see English. To pick one yourself, open **Settings › General › Language** and choose it, or choose it on the lock screen. Only the app's own words change. Your note, folder and file names stay as you wrote them. Reopen the app after you change it so the new language shows everywhere.

| Language | Code | | Language | Code |
|---|---|---|---|---|
| English | `en` | | Japanese | `ja` |
| Spanish | `es` | | Chinese (Simplified) | `zh-CN` |
| Portuguese (Brazil) | `pt-BR` | | Hindi | `hi` |
| French | `fr` | | Arabic | `ar` |
| German | `de` | | Russian | `ru` |

These are ten of the 41. The full list, with the status of each one, is in [core/languages/README.md](../core/languages/README.md).

The translations were made with AI and checked by a script, and matched to macOS's own words for the 30 languages macOS has. Native speakers have not read them. If something reads oddly, please [fix it](#fix-a-translation).

## What stays in English

- What the AI tools tell your AI app. The AI answers you in your language.
- Your own names: note, folder, file and memory names.
- The names Phygital Memory, Phygital Key, Phygital Brain, GitHub, iCloud, Finder, Touch ID and Claude.
- Commands, file names and these docs. To read a docs page in your language, ask your AI app: *"Explain this page in Polish."*

## Add a language with your AI agent

Give an AI coding agent this request, in a copy of the repository:

> *"Add Catalan: add `["ca", "Català"]` to core/languages/languages.json, run `python3 scripts/i18n.py translate ca` from core, then run `python3 scripts/i18n.py check` until Catalan passes. Follow core/languages/TRANSLATING.md."*

1. `translate ca` fills a new `ca.json` with a translation of every English text. It needs `ANTHROPIC_API_KEY` set in your environment. The key is never stored.
2. Each `{0}` placeholder stays exactly as in English. A translation that loses one is skipped.
3. `check` makes sure nothing is missing or broken.
4. Build the app again (`bash rebuild.sh --install`). People whose Mac or app is set to Catalan now see it.

Missing texts show in English, so a half-done file still works.

## Fix a translation

Open `core/languages/<code>.json`, change the value of the line that reads wrong, keep every `{0}` as it is, and run `python3 scripts/i18n.py check` from `core`. Then open a pull request, or an issue with the old and new wording. The steps are in [core/languages/TRANSLATING.md](../core/languages/TRANSLATING.md#fix-a-translation).

## Right to left

Arabic, Persian, Hebrew and Urdu set the page direction to right to left. A native reader has not checked the layout yet.

## Settings

| Setting | Default | What it does |
|---|---|---|
| **Settings › General › Language** | System | Shows the app in one language |

## What next

Back to [the guides](README.md).
