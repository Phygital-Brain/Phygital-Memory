# Connect your AI app

For when you want an AI app to use your memories. You leave with the app connected and one question answered from your notes.

## Before you start

1. Install Phygital Memory and make a memory: [setup-computer.md](setup-computer.md).
2. Keep the app open. The door only exists while the app runs.
3. For an Encrypted memory, unlock it in the app. A locked memory cannot be searched.

Every AI app gets its **own key**. In the app, go to **Settings › AI apps › Connect an AI app**, pick the app, choose which memories it may reach, and decide whether it may edit. The key is shown **once**, together with the exact setup to paste. The app stores only a fingerprint, so you cannot see it again. Make a new one if you lose it.

The door's address is always:

```
http://127.0.0.1:8790/mcp
```

> [!TIP]
> Start with **Allow edits** off. You can turn it on later in the same place.

If your memory is **Open**, any AI app that can read files can also open the folder directly. You do not need the door for reading. The door adds search, edits with Undo, and AI tasks.

## Claude Code

The quickest way: in **Settings › AI apps**, press **Add to Claude Code**. The app adds the door and the key for you.

By hand, run this in Terminal, with your key in place of `YOUR_KEY`:

```bash
claude mcp add --scope user --transport http phygital-memory http://127.0.0.1:8790/mcp --header "Authorization: Bearer YOUR_KEY"
```

You should see `phygital-memory` when you run:

```bash
claude mcp list
```

Check it works: start `claude` and ask *"Run status from Phygital Memory."* It should list your memories.

## Claude Desktop

1. In **Settings › AI apps › Connect an AI app**, choose **Claude Desktop** and press **Download**.
2. The app saves `Phygital Memory.mcpb` in your Downloads folder and copies your key to the clipboard.
3. Double-click the file. Claude Desktop asks for the key and the address. Paste the key. Leave the address as it is.
4. Open a new chat and ask *"Run status from Phygital Memory."*

## Cursor

Add this to `~/.cursor/mcp.json`, with your key in place of `YOUR_KEY`:

```json
{
  "mcpServers": {
    "phygital-memory": {
      "url": "http://127.0.0.1:8790/mcp",
      "headers": { "Authorization": "Bearer YOUR_KEY" }
    }
  }
}
```

Restart Cursor, then ask its agent *"Run status from Phygital Memory."*

## Codex

Add this to `~/.codex/config.toml`, with your key in place of `YOUR_KEY`:

```toml
[mcp_servers.phygital_memory]
url = "http://127.0.0.1:8790/mcp"
http_headers = { Authorization = "Bearer YOUR_KEY" }
```

Restart Codex, then ask *"Run status from Phygital Memory."*

## Other MCP apps

Pick **Other AI app** in **Settings › AI apps**. In your app, add an MCP server of type streamable HTTP with this address and header:

```
http://127.0.0.1:8790/mcp
Authorization: Bearer YOUR_KEY
```

Apps that support MCP sign-in can add the address without a key. The app then shows an **Allow** window and you press **Allow**. This is not tested with the Claude app, which refuses sign-in pages that are not on `https`, so use a key there.

## Claude website and phone app

Not supported yet. The door lives on your Mac at `127.0.0.1`, which a website or phone cannot reach. If your memory is **Open** and sits in a cloud folder or a private GitHub backup that your phone AI app can read, that app can read the files without the door.

## ChatGPT, VS Code, Gemini CLI, OpenClaw, Hermes Agent, Goose

Not tested. If the app can use an MCP server over streamable HTTP with a header, the "Other MCP apps" steps are the ones to try. We say "not tested" because we have not run them.

## If it does not connect

See [troubleshooting.md](troubleshooting.md#connecting-your-ai-app).

## What next

Try the prompts in [examples.md](examples.md).
