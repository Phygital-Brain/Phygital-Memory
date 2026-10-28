# Run it on your own server

Phygital Memory Server is the same app on a server you own, without the window. It is open all the time, so the AI apps on your phone can reach your memories even when your computer is off.

You get two things at your address, say `https://memory.example.com`:

- **The page.** The same screens as the desktop app, in your browser, behind a passphrase. You make and unlock memories, write notes, connect AI apps and set up backups there.
- **The AI door** at `https://memory.example.com/mcp`. Claude, ChatGPT and any other AI app that speaks MCP connect to it, on your computer or your phone.

## What it can reach

Only the memories on the server. Nothing on your computer.

- The same 17 tools as the desktop app ([the list](tools.md)). Search goes through Engram, like on your computer.
- Every AI app starts **read only**. You choose which memories it sees, and turn on **Allow edits** for each one.
- **Encrypted memories** open only after you unlock them on the page. They stay open in the server's memory until you lock them or the server restarts. Their passwords are never written down.

Things that need a computer are not on the server: Touch ID, Finder, and choosing files with your computer's own file chooser (backup files, import and export). Do those in the desktop app.

## Before you start

- A server with Docker (any Linux server, a home server, or a host like Coolify).
- A domain or subdomain pointing at it, like `memory.example.com`. The page and the AI door need HTTPS.
- A long passphrase, 12 characters or more, that you use nowhere else.

## Set it up with Docker Compose

1. Copy the [`server`](../server) folder from this repository to your server.
2. Copy `.env.example` to `.env` and fill in `DOMAIN` and `PASSPHRASE`.
3. Start it:

```bash
docker compose up -d
```

Caddy gets the HTTPS certificate on its own. Open `https://your-domain` and type your passphrase.

## Other ways

- **Coolify:** make a new resource from Docker Compose and paste [`server/compose.yaml`](../server/compose.yaml). Set `DOMAIN` and `PASSPHRASE`. If Coolify already does HTTPS for you, remove the `caddy` part and point your domain at port 8790.
- **Render:** New, Blueprint, this repository, Blueprint path `server/render.yaml`. After the first deploy, set `PHYGITAL_MEMORY_URL` to the address Render gives you.
- **Railway or any host that runs images:** use the image `ghcr.io/phygital-brain/phygital-memory:latest`, a disk at `/data`, port 8790, and the settings below.

On Render and Railway there is no WebDAV drive (they don't allow it), and syncing with your computer goes through relays, which is slower.

## Settings

| Setting | What it is |
|---|---|
| `PHYGITAL_MEMORY_URL` | The address people open, like `https://memory.example.com`. Required |
| `PHYGITAL_MEMORY_PASSPHRASE` | What you type to open the page. 12 characters or more. Required |
| `PHYGITAL_MEMORY_DATA` | Where memories and settings live. `/data` in the image: keep it on a disk that survives restarts |
| `PHYGITAL_MEMORY_SYNC_PORT` | The port for syncing with your computers. `22000` in the image |

Keep the passphrase in your host's secret settings or in `.env`, never in a file you share.

## Connect your AI apps

On the page, open **Settings**, **AI apps**.

- **Claude (website, desktop and phone) and ChatGPT:** add a custom connector with your server's address and `/mcp` at the end. The AI app opens your server's page. Sign in with your passphrase and press **Allow**.
- **Other AI apps:** make a key in **AI apps** and paste the address and key into the AI app's setup.

More in [Connect your AI app](connect-your-ai.md).

## Keep it in step with your computer

There are two ways, and you can use both:

- **Link my computer.** In the desktop app, open **Link my computer** and make a link. On the server's page, paste it and press Link. The memories you pick then sync straight between your computer and the server, still encrypted. The server is always on, so your computer catches up whenever the app is open.
- **The same storage.** The desktop app and the server both open the same WebDAV or Nextcloud folder. On the server this needs the four WebDAV lines in `compose.yaml`.

If the same note changes in both places at once, both copies are kept, and **Version history** lets you go back.

## Updates

Every release also builds a new server image. The page tells you when a newer version is out. To update:

```bash
docker compose pull && docker compose up -d
```

On Coolify, Render and Railway, press Redeploy. Your memories and settings stay on the `/data` disk. After an update, unlock your Encrypted memories again.

## Safety

- The page and the AI door are on the internet, so the passphrase is the lock. Make it long. Ten wrong tries close the door for 15 minutes.
- A login lasts 30 days, or until the server restarts. **Sign out** is at the bottom of the side bar.
- Secrets the desktop app keeps in your computer's keychain (cloud passwords, the GitHub key, your sharing key) are kept on the server in one file that only the server can read.
- Anyone who controls the server can see unlocked memories while they are open. Use a server you trust. More in [Threat model](threat-model.md).
