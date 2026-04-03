"""Script Launcher instrument — run experiment shell scripts from GNA."""

from PyQt6.QtWidgets import QWidget
from app.instruments.base_instrument import BaseInstrument
from app.instruments.script_launcher.ui.launcher_panel import LauncherPanel


class ScriptLauncherInstrument(BaseInstrument):
    def name(self) -> str:
        return "Script Launcher"

    def description(self) -> str:
        return (
            "Run experiment shell scripts (gsort, cmat, etc.) "
            "from configured directories with live output"
        )

    def icon_text(self) -> str:
        return "\U0001f5a5"  # desktop computer emoji

    def create_panel(self, parent: QWidget = None) -> QWidget:
        return LauncherPanel(parent)


def create_instrument():
    return ScriptLauncherInstrument()
