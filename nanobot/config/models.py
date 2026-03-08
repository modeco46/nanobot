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


def load_models_allowlist() -> tuple[list[str], Path | None]:
    """Load allowed models from models/models.txt/models.json near config.

    Supported formats:
    - models / models.txt: one model per line, '#' comments allowed
    - models.json: ["provider/model", ...] or {"models": [...]} 
    """
    for path in get_models_candidates():
        if not path.exists():
            continue

        if path.suffix == ".json":
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = data.get("models", [])
            if not isinstance(data, list):
                return [], path
            models = [str(m).strip() for m in data if str(m).strip()]
            return list(dict.fromkeys(models)), path

        with open(path, encoding="utf-8") as f:
            lines = []
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                lines.append(stripped)
            return list(dict.fromkeys(lines)), path

    return [], None
