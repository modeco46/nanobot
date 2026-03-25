<div align="center">
  <img src="nanobot_logo.png" alt="nanobot" width="420">
  <h1>nanobot</h1>
  <p>Lightweight personal AI assistant framework (Python 3.11+)</p>
  <p>
    <a href="https://pypi.org/project/nanobot-ai/"><img src="https://img.shields.io/pypi/v/nanobot-ai" alt="PyPI"></a>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </p>
</div>

`nanobot` is a compact agent framework with:
- CLI chat mode
- gateway mode for chat channels
- built-in tools (shell/web/MCP)
- memory, cron tasks, and heartbeat services

> Current package version in this repo: **0.1.4.post4**.

## What is актуально in this repo

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
- azure_openai
- anthropic
- openai
- openrouter
- deepseek
- groq
- zhipu
- dashscope
- vllm
- gemini
- moonshot
- minimax
- aihubmix
- siliconflow
- volcengine
- openai_codex (OAuth)
- github_copilot (OAuth)

## Installation

### From source (recommended for development)

```bash
git clone https://github.com/HKUDS/nanobot.git
cd nanobot
pip install -e .
```

### From PyPI

```bash
pip install nanobot-ai
```

### With uv

```bash
uv tool install nanobot-ai
```

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
      "model": "anthropic/claude-opus-4-5",
      "provider": "openrouter"
    }
  },
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
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

### Telegram config example

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
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

🐈 nanobot is capable of linking to the agent social network (agent community). **Just send one message and your nanobot joins automatically!**

| Platform | How to Join (send this message to your bot) |
|----------|-------------|
| [**Moltbook**](https://www.moltbook.com/) | `Read https://moltbook.com/skill.md and follow the instructions to join Moltbook` |
| [**ClawdChat**](https://clawdchat.ai/) | `Read https://clawdchat.ai/skill.md and follow the instructions to join ClawdChat` |

## Tools and capabilities

- **Shell execution tool** with timeout/path controls
- **Web search tool** (Brave API)
- **MCP servers** via `stdio`, `sse`, or `streamableHttp`
- **Cron service** for scheduled jobs
- **Heartbeat service** for periodic activity
- **Workspace template sync** on startup/onboard

## Useful commands

```bash
nanobot --version
nanobot status
nanobot channels status
nanobot provider login openai-codex
nanobot provider login github-copilot
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
