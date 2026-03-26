<div align="center">
  <img src="nanobot_logo.png" alt="nanobot" width="420">
  <h1>nanobot</h1>
  <p>Lightweight personal AI assistant framework (Python 3.11+)</p>
  <p>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </p>
</div>

`nanobot` is a compact agent framework with:
- CLI chat mode
- gateway mode for chat channels
- built-in tools (shell/web/MCP)
- memory, cron tasks, and heartbeat services

## What is actual in this repo

This README reflects the current codebase (including merged PR changes) and intentionally removes outdated/marketing-heavy sections.

### Implemented channels
- **Telegram**
- **Email (IMAP + SMTP)**

### Implemented command groups
- `nanobot onboard`
- `nanobot agent`
- `nanobot gateway`
- `nanobot status`
- `nanobot channels status`
- `nanobot provider login`

### Implemented provider configuration
- custom (OpenAI-compatible endpoint)

## Installation

### From source (recommended for development)

```bash
git clone https://github.com/modeco46/nanobot
cd nanobot
pip install -e .
```

### One-line installer script

For quick setup, use the automated installer script from this repository:

- `install_nanobot.sh`: https://github.com/modeco46/nanobot/blob/main/install_nanobot.sh

## Quick start

### 1) Initialize config and workspace

```bash
nanobot onboard
```

This creates `~/.nanobot/config.json` and workspace defaults.

### 2) Configure model + provider key

Minimal example using OpenRouter:

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.nanobot/workspace",
      "model": "",
      "provider": "custom",
      "maxTokens": 8192,
      "temperature": 0.1,
      "maxToolIterations": 40,
      "memoryWindow": 50,
      "reasoningEffort": null
    }
  },
  "channels": {
    "sendProgress": true,
    "sendToolHints": false,
    "whatsapp": {
      "enabled": false,
      "bridgeUrl": "ws://localhost:3001",
      "bridgeToken": "",
      "allowFrom": []
    },
    "telegram": {
      "enabled": true,
      "token": "",
      "allowFrom": [],
      "proxy": null,
      "replyToMessage": false
    }
  },
  "providers": {
    "custom": {
      "apiKey": "",
      "apiBase": "",
      "extraHeaders": null
    }
  },
  "gateway": {
    "host": "0.0.0.0",
    "port": 18790,
    "heartbeat": {
      "enabled": true,
      "intervalS": 1800
    }
  },
  "tools": {
    "web": {
      "proxy": null,
      "search": {
        "engine": "tavily",
        "apiKey": "",
        "maxResults": 10
      }
    },
    "exec": {
      "timeout": 60,
      "pathAppend": ""
    },
    "restrictToWorkspace": false,
    "mcpServers": {}
  }
}
```

### 3) Run in CLI mode

```bash
nanobot agent
```

One-shot message mode:

```bash
nanobot agent -m "Hello"
```

## Channel mode (gateway)

Run gateway:

```bash
nanobot gateway
```

### Email config example

```json
{
  "channels": {
    "email": {
      "enabled": true,
      "consentGranted": true,
      "imapHost": "imap.example.com",
      "imapUsername": "bot@example.com",
      "imapPassword": "***",
      "smtpHost": "smtp.example.com",
      "smtpUsername": "bot@example.com",
      "smtpPassword": "***",
      "fromAddress": "bot@example.com",
      "allowFrom": ["owner@example.com"]
    }
  }
}
```

> `allowFrom` cannot be an empty list for enabled channels.

## 🌐 Agent Social Network

🦞 nanobot is capable of linking to the agent social network (agent community). **Just send one message and your nanobot joins automatically!**

| Platform | How to Join (send this message to your bot) |
|----------|-------------|
| [**Moltbook**](https://www.moltbook.com/) | `Read https://moltbook.com/skill.md and follow the instructions to join Moltbook` |
| [**ClawdChat**](https://clawdchat.ai/) | `Read https://clawdchat.ai/skill.md and follow the instructions to join ClawdChat` |

## Runtime model switching

You can change the active model without restarting the bot by sending `/model` commands directly in the chat.

| Command | Effect |
|---|---|
| `/model` | Show current model, source, and available models |
| `/model <provider/model>` | Switch model for this chat/session only |
| `/model reset` | Clear session override (falls back to global or config default) |
| `/model global <provider/model>` | Switch model for **all** chats and groups |
| `/model global reset` | Remove global override (falls back to config default) |


**Priority:** session override → global override → config default (`model` in `config.json`)

The global override is stored in `{workspace}/global_model` as plain text and survives restarts.

To pre-populate the list shown by `/model`, create a `models` file next to `config.json`:

```
google/gemini-3-flash-preview
x-ai/grok-4.1-fast
openai/gpt-5-mini
```

## Bot commands

- /new — Start a new conversation
- /model — Show or change model for this chat
- /stop — Stop the current task
- /help — Show available commands
 
## Tools and capabilities

- **Shell execution tool** with timeout/path controls
- **Web search tool** (Tavily API)
- **MCP servers** via `stdio`, `sse`, or `streamableHttp`
- **Cron service** for scheduled jobs
- **Heartbeat service** for periodic activity
- **Workspace template sync** on startup/onboard

## Useful commands

```bash
nanobot --version
nanobot status
nanobot channels status
```

## Project structure

- `nanobot/cli/commands.py` — CLI entrypoints
- `nanobot/config/schema.py` — config models
- `nanobot/providers/registry.py` — provider registry and matching rules
- `nanobot/channels/` — channel implementations
- `nanobot/agent/` — core agent loop, memory, commands
- `tests/` — test suite

## License

MIT
