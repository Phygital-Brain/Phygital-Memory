# Phygital Memory

Your notes as a memory your AI can use. Each memory is one of two kinds:

- **Open**: a normal folder of notes. Any AI app can read it, and a cloud folder puts it on your phone too.
- **Encrypted**: locked with your password. AI apps reach it only through this app, and only the ones you allow.

The app adds search, version history, a trash, AI tasks, sharing (Mac to Mac, no account), and backups to GitHub,
WebDAV or S3. It speaks 41 languages.

> [!NOTE]
> This repo is private while the app gets ready to ship. The Mac version works today. Windows and Linux are being
> ported from the same code (see [Roadmap](#roadmap)).

## What's in this repo

| Folder or file | What it is |
|---|---|
| [`core/phygital_memory/`](core/phygital_memory) | The engine (Python): memories, encryption, search, sharing, backups, the AI door (MCP). |
| [`core/phygital_memory/vault/`](core/phygital_memory/vault) | How a memory is stored: `plain.py` for Open memories, the rest for Encrypted ones (Cryptomator format 8). |
| [`core/frontend/`](core/frontend) | The app's screens (JavaScript). They build into `core/phygital_memory/web/`. |
| [`core/languages/`](core/languages) | Every screen text in 41 languages. `en.json` is the source. |
| [`core/tests/`](core/tests) | Every test, the sample notes they use, and `run.sh` to run one. |
| [`core/packaging/`](core/packaging) | Turns the engine into one program, plus the Touch ID and Keychain helper. |
| [`core/scripts/`](core/scripts) | Small tools: `i18n.py` extracts, checks and translates the screen texts. |
| [`app/`](app) | The window around it all (Tauri, Rust): starts the engine, draws the menu bar, asks before closing. |
| [`brand/`](brand) | Logo, colours, icons and the brand guide. |
| [`rebuild.sh`](rebuild.sh) | Builds everything and makes the `.dmg`. With `--install` it also replaces the app in Applications and reopens it. |

Not in the repo, on purpose: `.signing/` (this Mac's private signing key) and `release/` (built apps, which go to
GitHub Releases).

## Build

Needs `uv`, `npm`, Rust with `cargo tauri`, `syncthing` and `rclone` (Homebrew on a Mac).

```bash
bash rebuild.sh --install
```

The first build takes longer: it fetches the build tools (`core/.venv`, `core/frontend/node_modules`,
`app/src-tauri/target`).

## Test

Each test is a small script that prints PASS or FAIL for each check. Run one from anywhere:

```bash
sh core/tests/run.sh test_open.py
```

Tests that talk to a running app need a test memory first: `sh core/tests/run.sh make_test_vault.py --fresh`.

## Languages

The screens go through `t("...")`; the English text is the key. To add or check a language:

```bash
cd core && python3 scripts/i18n.py extract && python3 scripts/i18n.py check
```

Translations were made with AI, checked for completeness and placeholders, and matched to macOS's own words where
macOS has the language. Native speakers haven't reviewed them yet.

## Roadmap

1. One repo, organised and labelled (this).
2. The Mac-only pieces get Windows and Linux versions: Touch ID, the Keychain, folder pickers, Show in Finder.
3. GitHub builds the Mac, Windows and Linux apps from one tag, with auto-update from the latest Release.
4. Tests on GitHub's Windows and Linux machines, and in virtual machines.

## License

AGPL-3.0-only. See [LICENSE](LICENSE) and [NOTICE](NOTICE). Copyright 2026 Phygital-Brain and Phygital Memory contributors.
