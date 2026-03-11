from pathlib import Path

from nanobot.config.loader import get_config_path, set_config_path
from nanobot.config.models import load_models_allowlist


def test_load_models_allowlist_returns_three_values_for_missing_file(tmp_path: Path):
    original = get_config_path()
    cfg = tmp_path / "config.json"
    cfg.write_text("{}", encoding="utf-8")
    set_config_path(cfg)
    try:
        result = load_models_allowlist()
        assert len(result) == 3
        models, source, error = result
        assert models == []
        assert source is None
        assert error is None
    finally:
        set_config_path(original)


def test_load_models_allowlist_returns_error_for_invalid_json(tmp_path: Path):
    original = get_config_path()
    cfg = tmp_path / "config.json"
    cfg.write_text("{}", encoding="utf-8")
    (tmp_path / "models.json").write_text("{bad json", encoding="utf-8")
    set_config_path(cfg)
    try:
        models, source, error = load_models_allowlist()
        assert models == []
        assert source == tmp_path / "models.json"
        assert error is not None
    finally:
        set_config_path(original)
 codex/implement-dynamic-model-switching-in-bot-8zkqjx

 codex/implement-dynamic-model-switching-in-bot-ki1ptz
 main


def test_load_models_allowlist_skips_directory_candidate(tmp_path: Path):
    original = get_config_path()
    cfg = tmp_path / "config.json"
    cfg.write_text("{}", encoding="utf-8")
    (tmp_path / "models").mkdir()
    (tmp_path / "models.txt").write_text("openai/gpt-4o-mini\n", encoding="utf-8")
    set_config_path(cfg)
    try:
        models, source, error = load_models_allowlist()
        assert models == ["openai/gpt-4o-mini"]
        assert source == tmp_path / "models.txt"
        assert error is None
    finally:
        set_config_path(original)
 codex/implement-dynamic-model-switching-in-bot-8zkqjx


 main
 main
