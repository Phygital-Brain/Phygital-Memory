# Contributing

Thanks for wanting to help. Phygital Memory is a desktop app for Mac, Windows and Linux that keeps your notes as a memory your AI can use. License: AGPL-3.0-only. Bug reports, fixes, translations and clearer docs are all welcome. Small, focused changes are the easiest to review.

## Reporting a problem

Click **New issue** on GitHub and pick a form:

| Form | Use it when |
|---|---|
| **Something doesn't work** | You hit a bug or an error message |
| **Question** | You want to know how to do something |
| **Idea or feature** | You want something new or different |
| **Report a security problem, privately** | Someone could misuse the app or reach private notes. Only the maintainer sees it. See [SECURITY.md](SECURITY.md) |

Each form asks for what is needed to help you, such as which kind of memory you use and which AI app.

**Leave out passwords, recovery words, keys, tokens and the contents of your notes before posting.** Issues are public. For security problems, don't open an issue: follow [SECURITY.md](SECURITY.md).

## Changing the code

1. Read [AGENTS.md](AGENTS.md). It explains the code and the rules that must never break.
2. Install the tools: `uv`, `npm`, Rust with `cargo tauri`, `syncthing` and `rclone`. On a Mac, Homebrew has them.
3. Make your change, with a test script in `core/tests/` when it changes behaviour. Tests use test data only. Never use real notes or a real secret in a test.
4. Run the tests that touch what you changed:

   ```bash
   sh core/tests/run.sh test_open.py
   ```

   You should see PASS or FAIL for each check. Some tests need a test memory first (`sh core/tests/run.sh make_test_vault.py --fresh`).
5. If people will notice the change, update the matching page in `docs/` and add a line to [CHANGELOG.md](CHANGELOG.md).
6. Open a pull request saying what changed and why.

## Special tests

Tests that talk to WebDAV, S3, GitHub or Syncthing use offline stand-ins, set by `PHYGITAL_MEMORY_OFFLINE` and related variables, so they never touch your real accounts. Tests that need Touch ID use `core/tests/fake-touchid.sh`. A real Finder drag, a real Touch ID unlock and real cloud accounts are checked by hand, not by the test scripts.

## Rules

- **Never weaken the safety rules** in [AGENTS.md](AGENTS.md). A change that touches one needs a very good reason, a test, and a clear note in the pull request.
- No tool may ever take a password, a key or a recovery word.
- Nothing may talk to the internet until the person presses the button that needs it. A new outside call must be listed in [docs/privacy.md](docs/privacy.md).
- Don't add new runtime dependencies without a strong reason.
- Don't change the Touch ID and Keychain helper without talking to the maintainer first.
- Keep third-party GitHub Actions pinned to a commit.

## Releases (maintainers)

1. Set the new version in `core/pyproject.toml`, `app/src-tauri/tauri.conf.json`, `app/src-tauri/Cargo.toml`, `CITATION.cff` and the version in `server.py`. Move the notes in [CHANGELOG.md](CHANGELOG.md) under that version, with the date.
2. Run the tests.
3. Push to `main`, then tag it `vX.Y.Z` and push the tag. GitHub builds the Mac, Windows and Linux apps (`.github/workflows/release.yml`) and puts them, with `latest.json` for the updater, in one draft release. You can also start it by hand: `gh workflow run release.yml`, or `gh workflow run release.yml -f only=<runner>` for one system.
4. Check the draft, add the changelog notes, and publish it by hand. The apps already installed find it the next time they open.

The same tag also builds the server image (`.github/workflows/server-image.yml`) and puts it on the Packages page as `ghcr.io/phygital-brain/phygital-memory`, with the version and `latest`.

On GitHub, a push to `main` runs only the Linux engine tests. The full test matrix runs when started by hand: `gh workflow run tests.yml -f full=true`. On a Mac, `bash rebuild.sh` still makes the `.dmg` locally.

## Writing docs

The docs are for people who have never used a terminal.

- Short sentences (8 to 20 words), everyday words, "you". Explain any technical word the first time.
- Headings in sentence case, phrased the way a reader would ask ("If something goes wrong").
- One command per code block, and show what the reader should see when it works.
- Button and page names in **bold**, exactly as on screen. Example questions for the AI in *italics*. Commands, settings and file names in `code`.
- No em dashes and no three dots. Use colons, commas or brackets.
- Never write that something was tested unless it was. Say "not supported" with the reason.
- Where it matters: "Works with Cryptomator vaults. Not made by or affiliated with Cryptomator."

## Translations

The screens are in 41 languages. English is the source. Add or fix a language by following [core/languages/TRANSLATING.md](core/languages/TRANSLATING.md). The list and status of every language is in [core/languages/README.md](core/languages/README.md). A native speaker reading a language is one of the most useful things you can do.

## Credit and license

AGPL-3.0-only. Before you send a contribution, read "Other licenses, and contributions" in [NOTICE](NOTICE): sending one means you agree to it. Please open an issue before a big change. Add yourself to [CONTRIBUTORS.md](CONTRIBUTORS.md) if you like.

## This repository

| Folder or file | What it is |
|---|---|
| [`core/phygital_memory/`](core/phygital_memory) | The engine (Python): memories, encryption, search, sharing, backups, the AI door. |
| [`core/phygital_memory/vault/`](core/phygital_memory/vault) | How a memory is stored: `plain.py` for Open memories, the rest for Encrypted ones. |
| [`core/frontend/`](core/frontend) | The app's screens (JavaScript). They build into `core/phygital_memory/web/`. |
| [`core/languages/`](core/languages) | Every screen text in 41 languages. `en.json` is the source. |
| [`core/tests/`](core/tests) | Every test, the sample notes they use, and `run.sh` to run one. |
| [`core/packaging/`](core/packaging) | Turns the engine into one program, plus the Touch ID and Keychain helper (Mac only). |
| [`core/scripts/`](core/scripts) | Small tools, such as `i18n.py` for the screen texts. |
| [`app/`](app) | The window around it all (Tauri, Rust): starts the engine, draws the menu bar, asks before closing. |
| [`server/`](server) | Phygital Memory Server: the Docker image and Compose files ([guide](docs/server.md)). |
| [`render.yaml`](render.yaml) | The Deploy to Render button's settings for the server (Render looks for it here). |
| [`brand/`](brand) | Logo, colours, icons and the brand guide. |
| [`rebuild.sh`](rebuild.sh) | Builds the Mac app and makes the `.dmg`. |

To build the Mac app yourself you need `uv`, `npm`, Rust with `cargo tauri`, `syncthing` and `rclone`. Then run:

```bash
bash rebuild.sh --install
```

You should see a `.dmg` in `release/`, and the app replaced in Applications and reopened. The first build takes longer, because it fetches the build tools. The Windows and Linux apps are built on GitHub. To run one test:

```bash
sh core/tests/run.sh test_open.py
```

You should see PASS or FAIL for each check. More for developers in [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
