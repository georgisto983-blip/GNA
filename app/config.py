"""Application settings — load/save from config/settings.json."""

import json
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "script_directories": [],
    "last_input_dir": "",
    "last_save_dir": "",
}


def load_settings():
    """Load settings from disk, falling back to defaults."""
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE) as f:
            saved = json.load(f)
        settings = DEFAULT_SETTINGS.copy()
        settings.update(saved)
        return settings
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Persist settings to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
