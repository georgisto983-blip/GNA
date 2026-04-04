"""Action-history tracker — persists recent user actions for quick replay.

Each action records the tool name, a description, the panel field values
needed to reproduce the action, and a timestamp.
"""

import json
import time
from pathlib import Path
from typing import Any

_MAX_ENTRIES = 50
_HISTORY_PATH = Path(__file__).resolve().parent.parent / "config" / "action_history.json"


def _load() -> list[dict]:
    if _HISTORY_PATH.exists():
        try:
            data = json.loads(_HISTORY_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save(entries: list[dict]) -> None:
    _HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    _HISTORY_PATH.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def record(tool: str, description: str, params: dict[str, Any] | None = None) -> None:
    """Record an action.

    *tool*        — sidebar instrument name (e.g. "Plunger (RDDS)")
    *description* — short human-readable description of what was calculated
    *params*      — dict of field name → value, enough to reproduce the action
    """
    entries = _load()
    entry = {
        "tool": tool,
        "description": description,
        "params": params or {},
        "timestamp": time.time(),
    }
    entries.insert(0, entry)
    entries = entries[:_MAX_ENTRIES]
    _save(entries)


def get_all() -> list[dict]:
    """Return history entries, newest first."""
    return _load()


def clear() -> None:
    _save([])
