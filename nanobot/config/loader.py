"""Configuration loading utilities."""

import json
from pathlib import Path

from nanobot.config.schema import Config


# Global variable to store current config path (for multi-instance support)
_current_config_path: Path | None = None


def get_onboard_default_config_data() -> dict:
    """Return the default config content used by `nanobot onboard`."""
    return {
        "agents": {
            "defaults": {
                "workspace": "~/.nanobot/workspace",
                "model": "",
                "provider": "custom",
                "maxTokens": 8192,
                "temperature": 0.1,
                "maxToolIterations": 40,
                "memoryWindow": 50,
                "reasoningEffort": None,
            }
        },
        "channels": {
            "sendProgress": True,
            "sendToolHints": False,
            "whatsapp": {
                "enabled": False,
                "bridgeUrl": "ws://localhost:3001",
                "bridgeToken": "",
                "allowFrom": [],
            },
            "telegram": {
                "enabled": True,
                "token": "",
                "allowFrom": [],
                "proxy": None,
                "replyToMessage": False,
            },
        },
        "providers": {
            "custom": {
                "apiKey": "",
                "apiBase": "",
                "extraHeaders": None,
            }
        },
        "gateway": {
            "host": "0.0.0.0",
            "port": 18790,
            "heartbeat": {
                "enabled": True,
                "intervalS": 3600,
            },
        },
        "tools": {
            "web": {
                "proxy": None,
                "search": {
                    "engine": "tavily",
                    "apiKey": "",
                    "maxResults": 10,
                },
            },
            "exec": {
                "timeout": 60,
                "pathAppend": "",
            },
            "restrictToWorkspace": False,
            "mcpServers": {},
        },
    }


def set_config_path(path: Path) -> None:
    """Set the current config path (used to derive data directory)."""
    global _current_config_path
    _current_config_path = path


def get_config_path() -> Path:
    """Get the configuration file path."""
    if _current_config_path:
        return _current_config_path
    return Path.home() / ".nanobot" / "config.json"


def load_config(config_path: Path | None = None) -> Config:
    """
    Load configuration from file or create default.

    Args:
        config_path: Optional path to config file. Uses default if not provided.

    Returns:
        Loaded configuration object.
    """
    path = config_path or get_config_path()

    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            data = _migrate_config(data)
            return Config.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to load config from {path}: {e}")
            print("Using default configuration.")

    return Config()


def save_config(config: Config, config_path: Path | None = None) -> None:
    """
    Save configuration to file.

    Args:
        config: Configuration to save.
        config_path: Optional path to save to. Uses default if not provided.
    """
    path = config_path or get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    data = config.model_dump(by_alias=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_onboard_default_config(config_path: Path | None = None) -> None:
    """Save the onboarding default config template."""
    path = config_path or get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(get_onboard_default_config_data(), f, indent=2, ensure_ascii=False)


def _migrate_config(data: dict) -> dict:
    """Migrate old config formats to current."""
    # Move tools.exec.restrictToWorkspace → tools.restrictToWorkspace
    tools = data.get("tools", {})
    exec_cfg = tools.get("exec", {})
    if "restrictToWorkspace" in exec_cfg and "restrictToWorkspace" not in tools:
        tools["restrictToWorkspace"] = exec_cfg.pop("restrictToWorkspace")
    return data
