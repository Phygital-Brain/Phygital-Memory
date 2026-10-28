# Translating Phygital Memory

How a language is made. Read this before you translate or review.

## What you make

For a language with code `{code}` (for example `pt-BR`):

| File | What |
|---|---|
| `core/languages/{code}.json` | Every text the app shows. The key is the English text, the value is your translation |
| `core/languages/languages.json` | The list of languages: `["{code}", "the language's own name"]`. Add one line for a new language |

English (`en.json`) is the source. Never edit it by hand: it is made from the screens (every `t("text")` in `frontend/src/`) and the error messages the engine sends to them. Change English in the code first, then run the three commands, from the `core` folder:

```bash
python3 scripts/i18n.py extract
```

Refreshes `languages/en.json` from the code and prints how many texts there are.

```bash
python3 scripts/i18n.py translate
```

Fills what is missing in every language, or only one with `translate pt-BR`. It uses Claude and needs `ANTHROPIC_API_KEY` in your environment (it is never stored). Add `--dry` to only count, `--model` to pick another model. It keeps only answers with the same `{0}` parts as English.

```bash
python3 scripts/i18n.py check
```

You should see `N/N done` for each language, with nothing missing and no wrong `{0}` parts. It fails when a placeholder is lost or added. "No longer used" means a text was removed from English; it does no harm.

A text that is missing shows in English, so a half-done file still works.

## Two special kinds of text

- **Texts with `@@`.** The same English word can mean two things. `Open@@kind` is the kind of memory (an adjective), while `Open` is the button (a verb). The part after `@@` is a hint for you and never shows. Translate only the meaning: the value in `{code}.json` has no `@@`.
- **Mac words and computer words.** Many texts say "this Mac" or "Finder". Each has a twin in `frontend/src/shell/pc-words.js` that says "this computer" or "your file manager". The app shows the computer wording on every system, the Mac too, except texts about Finder, the Keychain, Touch ID and the security chip, which keep the Mac words on a Mac. Both twins are in `en.json`: translate both, each in its own words. When you add a screen text that names the Mac or Finder, add its twin to `pc-words.js` and run `extract` again.

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
- Feature names get a natural local name, the same one every time. The key words and how to treat each one are in [GLOSSARY.md](GLOSSARY.md).
- Right-to-left languages (Arabic, Persian, Hebrew, Urdu) are translated the same way. The page direction is set by the code. Tell us if the layout looks wrong.

## Review

A second person (or agent) who did not translate it reads everything as a native speaker would, fixes anything stiff, odd or wrong, and translates a sample back to English to catch changes in meaning. Set the status in [README.md](README.md) to `reviewed-by-ai` when that is done, and `reviewed` only after a native speaker has read it. Never call a machine translation reviewed.

## Add a language with an AI agent

Give an AI coding agent this request, in a copy of the repository:

> *"Add Catalan: add `["ca", "Català"]` to core/languages/languages.json, run `python3 scripts/i18n.py translate ca` from core, then run `python3 scripts/i18n.py check` until Catalan passes. Follow core/languages/TRANSLATING.md."*

Catalan is not in the list yet. Pick any language that is not.

## Fix a translation

1. Open `core/languages/{code}.json`.
2. Find the English text (the key) and change the value.
3. Keep every `{0}` and `{1}` exactly as in English.
4. Run `python3 scripts/i18n.py check` from `core`.
5. Open a pull request, or an issue with the old and new wording.
