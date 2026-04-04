"""Recent-files tracker — persists a short history of loaded files."""

import json
from pathlib import Path
from typing import Optional

_MAX_ENTRIES = 20
_RECENT_PATH = Path(__file__).resolve().parent.parent / "config" / "recent_files.json"


def _load() -> list[dict]:
    if _RECENT_PATH.exists():
        try:
            data = json.loads(_RECENT_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save(entries: list[dict]) -> None:
    _RECENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _RECENT_PATH.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def add(path: str, tool: str) -> None:
    """Record that *path* was opened by *tool*."""
    entries = _load()
    # Remove duplicate
    entries = [e for e in entries if e.get("path") != path]
    entries.insert(0, {"path": path, "tool": tool})
    entries = entries[:_MAX_ENTRIES]
    _save(entries)


def get_all() -> list[dict]:
    """Return recent entries, newest first.  Each: {path, tool}."""
    return [e for e in _load() if Path(e.get("path", "")).exists()]


def clear() -> None:
    _save([])
