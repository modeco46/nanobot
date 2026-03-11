import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def test_agent_loop_is_valid_python_source() -> None:
    """Regression guard: reject accidental merge-artifact corruption in loop.py."""
    src = _read("nanobot/agent/loop.py")
    ast.parse(src)


def test_no_git_conflict_markers_in_critical_files() -> None:
    critical_files = [
        "nanobot/agent/loop.py",
        "nanobot/config/models.py",
        "tests/test_model_switch.py",
        "tests/test_models_allowlist.py",
    ]
    for rel in critical_files:
        src = _read(rel)
        assert "<<<<<<<" not in src
        assert "=======" not in src
        assert ">>>>>>>" not in src
