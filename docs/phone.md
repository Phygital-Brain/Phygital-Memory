# Use it from your phone

For when you want your AI agent on your phone, or on the web, to use your memories. There is no Phygital Memory phone app, but there are several ways in. You leave knowing which one fits you.

AI agents on the web and in phone apps run on their company's computers, not on your phone. They can't reach the app on your computer by themselves. Each way below gives them a path.

| Way | Your computer must be on | Encrypted memories | Opens anything to the internet |
|---|---|---|---|
| [1. Remote control of an agent on your computer](#1-remote-control-of-an-agent-on-your-computer) | Yes | Yes, while unlocked | No |
| [2. Your cloud](#2-your-cloud) | No | No | No (your cloud already has the files) |
| [3. Your own server](#3-your-own-server) | No | Yes | Yes, your server, behind your passphrase |
| [4. A tunnel to your computer](#4-a-tunnel-to-your-computer) | Yes | Yes, while unlocked | Yes, your computer's door, behind a key |

> [!TIP]
> Start with 1 or 2. They open nothing new to the internet.

## 1. Remote control of an agent on your computer

Some AI agents let you continue a session on your computer from your phone. The agent keeps running on your computer and uses Phygital Memory there, through the same local connection as always. Your phone only sends your messages and shows the answers.

- Connect the agent on your computer first: [connect your AI](connect-your-ai.md).
- Turn on its remote control, the way that agent's own docs describe.
- Open memories work with the app closed. Encrypted memories need the app open and unlocked.

## 2. Your cloud

An **Open** memory is a normal folder. Keep it in a cloud your phone and your AI agents can already read: iCloud Drive, Dropbox, Google Drive, OneDrive, a WebDAV or Nextcloud folder, or a private GitHub backup (in **Storage and backup**). Many AI agents can connect to these clouds and read the notes from there.

- Nothing to set up in Phygital Memory beyond where the memory lives.
- The agent reads the files directly, so there is no search across notes, no **Undo** and no AI tasks from Phygital Memory.
- An **Encrypted** memory's cloud copy is scrambled, so this way works for Open memories only. See [find your threat model](find-your-threat-model.md).

## 3. Your own server

Run the same app on a server you own. It gets its own https address, so web and phone agents connect to it as a custom connector, and you approve each one with your passphrase. It works when your computer is off, and keeps in step with your computer. See [server.md](server.md).

## 4. A tunnel to your computer

A tunnel gives the app's door on your computer a public https address, so web and phone agents can reach it while your computer is on. Tools that do this include Cloudflare Tunnel, ngrok and Tailscale Funnel.

> [!WARNING]
> Not tested yet. A tunnel opens your computer's door, and the app's own page, to the internet. Every AI agent still needs its own key, and the page needs your password, but use it only if you understand the risk. Turn the tunnel off when you don't need it.

The door only answers to the names `127.0.0.1` and `localhost`, so the tunnel has to send that name on. With Cloudflare's quick tunnel:

```bash
cloudflared tunnel --url http://127.0.0.1:8790 --http-host-header localhost:8790
```

Then, in **AI › Connect an AI app**, make a key for the agent. In the agent, add a custom connector with the tunnel's address and `/mcp` at the end, and the header `Authorization: Bearer YOUR_KEY`. Agents that only offer sign-in, with no header, don't work this way yet: the sign-in page expects the local address.

## What next

Not sure which memories should leave your computer at all? Read [find your threat model](find-your-threat-model.md).
