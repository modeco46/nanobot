"""Model allowlist loading from files near the active config."""

from __future__ import annotations

import json
from pathlib import Path

from nanobot.config.loader import get_config_path


def get_models_candidates() -> list[Path]:
    """Return candidate model-list files in config directory."""
    base = get_config_path().parent
    return [
        base / "models",
        base / "models.txt",
        base / "models.json",
    ]


def load_models_allowlist() -> tuple[list[str], Path | None, str | None]:
    """Load allowed models from models/models.txt/models.json near config.

    Supported formats:
    - models / models.txt: one model per line, '#' comments allowed
    - models.json: ["provider/model", ...] or {"models": [...]}.

    Returns:
        (models, source_path, error_message)
    """
    for path in get_models_candidates():
 codex/implement-dynamic-model-switching-in-bot-8zkqjx
        if not path.exists() or not path.is_file():

 codex/implement-dynamic-model-switching-in-bot-ki1ptz
        if not path.exists() or not path.is_file():

        if not path.exists():
 main
 main
            continue

        try:
            if path.suffix == ".json":
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    data = data.get("models", [])
                if not isinstance(data, list):
                    return [], path, "Invalid models.json format: expected array or {'models': [...]}"
                models = [str(m).strip() for m in data if str(m).strip()]
                return list(dict.fromkeys(models)), path, None

            with open(path, encoding="utf-8") as f:
                lines = []
                for line in f:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    lines.append(stripped)
                return list(dict.fromkeys(lines)), path, None
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            return [], path, f"Failed to read model list: {exc}"

    return [], None, None
