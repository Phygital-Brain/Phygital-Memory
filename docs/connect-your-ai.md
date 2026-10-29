# Connect your AI app

For when you want an AI app to use your memories. You leave with the app connected and one question answered from your notes.

## Before you start

1. Install Phygital Memory and make a memory: [setup-computer.md](setup-computer.md).
2. For an Encrypted memory, open the app and unlock it. A locked memory cannot be searched.

Every AI app gets its **own key**. In the app, go to **AI › Connect an AI app** (also in **Settings › AI apps**), pick the app, choose which memories it may reach, and decide whether it may edit. The key is shown **once**, together with the exact setup to paste. The app stores only a fingerprint, so you cannot see it again. Make a new one if you lose it.

## Two ways in

| | How the AI app reaches your notes | With the app closed |
|---|---|---|
| **The AI app starts Phygital Memory itself** (Claude Code, Claude Desktop, Cursor, Codex, others that start an MCP server) | It runs the app's engine in the background, only while it needs it | Open memories work. Encrypted memories need the app open and unlocked |
| **The door** (any app that speaks MCP over HTTP) | `http://127.0.0.1:8790/mcp` | Nothing works |

The setup the app shows you uses the first way when it can. With the app open, the first way goes through the app, so Encrypted memories, Undo and the activity list work as usual. With the app closed, it reaches your **Open** memories by itself: search, read and, with **Allow edits**, write. Those changes don't show in the app's activity list and have no **Undo** there, but every note's version history keeps the old text. No backups run until you open the app again.

The engine's place on a Mac is `/Applications/Phygital Memory.app/Contents/Resources/server/phygital-memory-server`. On Windows and Linux the app shows the exact path. The Linux AppImage moves each time it runs, so it always uses the door: install the `.deb` or `.rpm` for the first way.

> [!TIP]
> Start with **Allow edits** off. You can turn it on later in the same place.

If your memory is **Open**, any AI app that can read files can also open the folder directly. You do not need the door for reading. The door adds search, edits with Undo, and AI tasks.

## Claude Code

The quickest way: in **AI › Connect an AI app**, pick **Claude Code** and press **Add to Claude Code for me**. The app adds itself and the key for you.

By hand on a Mac, run this in a terminal, with your key in place of `YOUR_KEY`:

```bash
claude mcp add phygital-memory --scope user -e PHYGITAL_MEMORY_KEY=YOUR_KEY -- "/Applications/Phygital Memory.app/Contents/Resources/server/phygital-memory-server" mcp
```

Or through the door, which needs the app open:

```bash
claude mcp add --scope user --transport http phygital-memory http://127.0.0.1:8790/mcp --header "Authorization: Bearer YOUR_KEY"
```

You should see `phygital-memory` when you run:

```bash
claude mcp list
```

Check it works: start `claude` and ask *"Run status from Phygital Memory."* It should list your memories.

## Claude Desktop

1. In **AI › Connect an AI app**, choose **Claude Desktop** and press **Download**.
2. The app saves `Phygital Memory.mcpb` in your Downloads folder and shows your key. Press **Copy**. (During the first setup of a memory, the key is copied for you.)
3. Double-click the file. Claude Desktop asks for the key and the address. Paste the key. Leave the address as it is.
4. Open a new chat and ask *"Run status from Phygital Memory."*

Every step, the Mac-only limit and fixes: [Claude Desktop extension](claude-desktop-extension.md).

## Cursor

Add this to `~/.cursor/mcp.json`, with your key in place of `YOUR_KEY`:

```json
{
  "mcpServers": {
    "phygital-memory": {
      "command": "/Applications/Phygital Memory.app/Contents/Resources/server/phygital-memory-server",
      "args": ["mcp"],
      "env": { "PHYGITAL_MEMORY_KEY": "YOUR_KEY" }
    }
  }
}
```

Restart Cursor, then ask its agent *"Run status from Phygital Memory."*

## Codex

Add this to `~/.codex/config.toml`, with your key in place of `YOUR_KEY`:

```toml
[mcp_servers.phygital_memory]
command = '/Applications/Phygital Memory.app/Contents/Resources/server/phygital-memory-server'
args = ["mcp"]
env = { PHYGITAL_MEMORY_KEY = "YOUR_KEY" }
```

Restart Codex, then ask *"Run status from Phygital Memory."*

## Other MCP apps

Pick **Other AI app** in **AI › Connect an AI app**. If your app can start an MCP server itself (stdio), give it the engine's place with `mcp` after it, and the setting `PHYGITAL_MEMORY_KEY` with your key. Otherwise add an MCP server of type streamable HTTP with this address and header:

```
http://127.0.0.1:8790/mcp
Authorization: Bearer YOUR_KEY
```

Apps that support MCP sign-in can add the address without a key. The app then shows an **Allow** window and you press **Allow**. Agents that only accept `https` sign-in pages connect with a key instead.

## AI agents on the web and phones

They can't reach your computer directly. Pick a way in: [Use it from your phone](phone.md).

## ChatGPT, VS Code, Gemini CLI, OpenClaw, Hermes Agent, Goose

If the agent can use an MCP server over streamable HTTP with a header, follow the steps in [Other MCP apps](#other-mcp-apps).

## If it does not connect

See [troubleshooting.md](troubleshooting.md#connecting-your-ai-app).

## What next

Try the prompts in [examples.md](examples.md).
