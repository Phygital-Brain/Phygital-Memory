# Translating Phygital Memory

How a language is made. Read this before you translate or review.

## What you make

For a language with code `{code}` (for example `pt-BR`):

| File | What |
|---|---|
| `core/languages/{code}.json` | Every text the app shows. The key is the English text, the value is your translation |
| `core/languages/languages.json` | The list of languages: `["{code}", "the language's own name"]`. Add one line for a new language |

English (`en.json`) is the source and is made by `python3 scripts/i18n.py extract` from the screens and the messages the engine sends to them. Change English first, then run `translate` to add the new texts to every language. A text that is missing shows in English, so a half-done file still works.

Then check it, from the `core` folder:

```bash
python3 scripts/i18n.py check
```

You should see `N/N done` for your language, with nothing missing and no wrong `{0}` parts.

## What stays English

- The words the AI tools use. AI apps read English best. The AI explains in your language.
- Note, folder and file names. People wrote them.
- Placeholders like `{0}` and `{1}`. Copy them exactly, and keep them in the sentence. A translation with a lost or added placeholder is skipped by the script and English shows.
- Keyboard keys such as ⌘ and ⇧.
- The names Phygital Memory, Phygital Key, Phygital Brain, GitHub, iCloud, Finder, Touch ID and Claude.
- Paths, commands, setting names and file names, in the docs. Docs stay English: tell readers to ask their AI to explain a page in their language.

## Writing

- Natural, everyday speech. Read each sentence aloud. If a native speaker would not say it that way, rewrite it. Adapt, do not translate word for word.
- About an 8th-grade reading level. Plain and clear, never childish.
- One register for the whole language, the one popular consumer apps in that language use (informal "du", "você", "tu"). Use the same word every time for the same thing.
- Where macOS has the language, use the words macOS itself uses for things it names (Finder, Trash, Settings, Keychain). Compare with Apple's own translations on a Mac and use them where the meaning matches.
- Where English says "they" about a person, repeat the name or rephrase. No guessed pronouns.
- Keep every fact, rule, number and step. Do not add or remove rules.
- Never use em dashes, three dots or the ellipsis character. Use periods, commas, colons or brackets.
- Memory kinds are called Open and Encrypted. Keep each name the same everywhere in your language.
- Feature names get a natural local name. If you want, note the choices and the reason in a `GLOSSARY.md` for your language (not required yet).
- Right-to-left languages (Arabic, Persian, Hebrew, Urdu) are translated the same way. The page direction is set by the code. Tell us if the layout looks wrong.

## Review

A second person (or agent) who did not translate it reads everything as a native speaker would, fixes anything stiff, odd or wrong, and translates a sample back to English to catch changes in meaning. Set the status in [README.md](README.md) to `reviewed-by-ai` when that is done, and `reviewed` only after a native speaker has read it. Never call a machine translation reviewed.

## Add a language with an AI agent

Give an AI coding agent this request, in a copy of the repository:

> *"Add Thai: add `["th", "ไทย"]` to core/languages/languages.json, run `python3 scripts/i18n.py translate th` from core, then run `python3 scripts/i18n.py check` until Thai passes. Follow core/languages/TRANSLATING.md."*

Thai already exists. Use a language that is not in the list.

## Fix a translation

1. Open `core/languages/{code}.json`.
2. Find the English text (the key) and change the value.
3. Keep every `{0}` and `{1}` exactly as in English.
4. Run `python3 scripts/i18n.py check` from `core`.
5. Open a pull request, or an issue with the old and new wording.
