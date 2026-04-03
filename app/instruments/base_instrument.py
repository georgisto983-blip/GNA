"""Abstract base class that every GNA instrument must implement."""

from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget


class BaseInstrument(ABC):
    """Base class for all GNA instrument plugins.

    To create a new instrument:
      1. Create a subdirectory under app/instruments/<name>/
      2. Add instrument.py with a class inheriting from BaseInstrument
      3. Define a module-level ``create_instrument()`` that returns an instance
    """

    @abstractmethod
    def name(self) -> str:
        """Display name shown in the sidebar."""
        ...

    @abstractmethod
    def description(self) -> str:
        """Short description (shown as tooltip)."""
        ...

    @abstractmethod
    def icon_text(self) -> str:
        """Emoji or short text used as a sidebar icon."""
        ...

    @abstractmethod
    def create_panel(self, parent: QWidget = None) -> QWidget:
        """Create and return the main UI panel for this instrument."""
        ...
