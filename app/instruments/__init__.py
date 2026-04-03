"""Instrument auto-discovery — scans subdirectories for plugins."""

import importlib
from pathlib import Path


def discover_instruments():
    """Find and instantiate all instrument plugins.

    Each subdirectory of app/instruments/ that contains an instrument.py
    module with a ``create_instrument()`` function is loaded automatically.
    To add a new instrument, create a new folder with that module — no other
    files need to be modified.
    """
    instruments = []
    instruments_dir = Path(__file__).parent

    for item in sorted(instruments_dir.iterdir()):
        if item.is_dir() and not item.name.startswith("_"):
            try:
                module = importlib.import_module(
                    f"app.instruments.{item.name}.instrument"
                )
                if hasattr(module, "create_instrument"):
                    instruments.append(module.create_instrument())
            except (ImportError, AttributeError) as e:
                print(f"[GNA] Could not load instrument '{item.name}': {e}")

    return instruments
