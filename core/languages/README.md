# Languages

Phygital Memory is written in English and ready in 40 more languages. Rules for making and checking one: [TRANSLATING.md](TRANSLATING.md). For users: [docs/languages.md](../../docs/languages.md).

## Ready languages

| Language | Its own name | Code | Status | Matched to macOS words |
|---|---|---|---|---|
| English | English | `en` | source | not applicable |
| Arabic | العربية | `ar` | machine | yes |
| Bengali | বাংলা | `bn` | machine | no |
| Czech | Čeština | `cs` | machine | yes |
| Danish | Dansk | `da` | machine | yes |
| German | Deutsch | `de` | machine | yes |
| Greek | Ελληνικά | `el` | machine | yes |
| Spanish | Español | `es` | machine | yes |
| Persian | فارسی | `fa` | machine | no |
| Finnish | Suomi | `fi` | machine | yes |
| Filipino | Filipino | `fil` | machine | no |
| French | Français | `fr` | machine | yes |
| Gujarati | ગુજરાતી | `gu` | machine | no |
| Hebrew | עברית | `he` | machine | yes |
| Hindi | हिन्दी | `hi` | machine | yes |
| Hungarian | Magyar | `hu` | machine | yes |
| Indonesian | Bahasa Indonesia | `id` | machine | yes |
| Italian | Italiano | `it` | machine | yes |
| Japanese | 日本語 | `ja` | machine | yes |
| Korean | 한국어 | `ko` | machine | yes |
| Marathi | मराठी | `mr` | machine | no |
| Malay | Bahasa Melayu | `ms` | machine | yes |
| Norwegian Bokmål | Norsk (bokmål) | `nb` | machine | yes |
| Dutch | Nederlands | `nl` | machine | yes |
| Punjabi | ਪੰਜਾਬੀ | `pa` | machine | no |
| Polish | Polski | `pl` | machine | yes |
| Portuguese (Brazil) | Português (Brasil) | `pt-BR` | machine | yes |
| Portuguese (Portugal) | Português (Portugal) | `pt-PT` | machine | yes |
| Romanian | Română | `ro` | machine | yes |
| Russian | Русский | `ru` | machine | yes |
| Swedish | Svenska | `sv` | machine | yes |
| Swahili | Kiswahili | `sw` | machine | no |
| Tamil | தமிழ் | `ta` | machine | no |
| Telugu | తెలుగు | `te` | machine | no |
| Thai | ไทย | `th` | machine | yes |
| Turkish | Türkçe | `tr` | machine | yes |
| Ukrainian | Українська | `uk` | machine | yes |
| Urdu | اردو | `ur` | machine | no |
| Vietnamese | Tiếng Việt | `vi` | machine | yes |
| Chinese (Simplified) | 简体中文 | `zh-CN` | machine | yes |
| Chinese (Traditional) | 繁體中文 | `zh-TW` | machine | yes |

**Status:**

- `machine`: made by AI and checked by a script (every text present, placeholders intact). No person has read it.
- `reviewed-by-ai`: a second agent read it as a native speaker and translated a sample back to English.
- `reviewed`: a native speaker read it.

Never mark `reviewed` without a native speaker. Today every language is `machine`. No language is `reviewed-by-ai` or `reviewed` yet, and native speakers are the most useful help we can get.

**Matched to macOS words:** for the 30 languages macOS itself has, words for things macOS names (Finder, Trash, Settings, Keychain and similar) were compared with Apple's own translations on a Mac, and used where the meaning matches. The other languages have no macOS version to match.

**Right to left:** Arabic (`ar`), Persian (`fa`), Hebrew (`he`) and Urdu (`ur`) set the page direction to right to left. A native reader has not checked that the layout looks right.

All 40 translated files had every one of the 934 texts in `en.json` when last checked on 2026-10-28.

## Add or fix one

Read [TRANSLATING.md](TRANSLATING.md), then, from the `core` folder:

```bash
python3 scripts/i18n.py extract
python3 scripts/i18n.py check
python3 scripts/i18n.py translate th
```

`extract` refreshes `languages/en.json` from the code. `check` lists what each language is missing or has wrong. `translate` fills what is missing with Claude and needs `ANTHROPIC_API_KEY` in your environment (it is never stored). Add `--dry` to only count.
