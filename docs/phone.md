# Use it from your phone

Your AI agent on the phone or the web can use your memories. Pick one of four ways.

| Way | Computer must be on | Encrypted memories |
|---|---|---|
| [Remote control](#remote-control) | Yes | Yes |
| [Your cloud](#your-cloud) | No | No |
| [Your own server](#your-own-server) | No | Yes |
| [A tunnel](#a-tunnel) | Yes | Yes |

> [!TIP]
> Start with remote control or your cloud. Neither opens anything to the internet.

## Remote control

Some agents let you control a session on your computer from your phone. The agent runs on your computer and uses your memories there.

1. Connect the agent on your computer: [connect your AI](connect-your-ai.md).
2. Turn on the agent's remote control. Its own docs show how.
3. Talk to it from your phone.

Encrypted memories must be unlocked in the app.

## Your cloud

An Open memory is a normal folder. Keep it in a cloud your agent can read.

1. In **Storage and backup**, put the memory in iCloud Drive, Dropbox, Google Drive or OneDrive, or back it up to GitHub.
2. Connect that cloud to your agent.
3. Ask your agent about your notes.

The agent reads the files directly, so it works without the app. Search, Undo and AI tasks need the app.

## Your own server

Run Phygital Memory on a server you own. It has its own web address and works when your computer is off.

1. Set up the server: [server.md](server.md).
2. Link it to your computer: **Link a computer › To my server**.
3. In your agent, add a custom connector with your server's address and `/mcp` at the end.
4. Sign in with your passphrase and press **Allow**.

## A tunnel

A tunnel gives your computer a web address while it's on.

1. Install [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) (`cloudflared`).
2. Run:

   ```bash
   cloudflared tunnel --url http://127.0.0.1:8790 --http-host-header localhost:8790
   ```

3. Copy the `https://` address it prints.
4. In **AI › Connect an AI app**, make a key for your agent.
5. In your agent, add a custom connector with that address plus `/mcp`, and the header `Authorization: Bearer YOUR_KEY`.

Every agent needs its own key, and the app's page needs your password. Stop the tunnel when you're done: press **Ctrl+C**.

## What next

Not sure which memories should leave your computer? Read [find your threat model](find-your-threat-model.md).
