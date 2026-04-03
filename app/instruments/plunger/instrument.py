"""Plunger instrument plugin — RDDS half-life calculator."""

from PyQt6.QtWidgets import QWidget
from app.instruments.base_instrument import BaseInstrument
from app.instruments.plunger.ui.plunger_panel import PlungerPanel


class PlungerInstrument(BaseInstrument):
    def name(self) -> str:
        return "Plunger (RDDS)"

    def description(self) -> str:
        return (
            "Calculate nuclear excited-state half-lives using the "
            "Recoil Distance Doppler Shift method"
        )

    def icon_text(self) -> str:
        return "\U0001f52c"  # microscope emoji

    def create_panel(self, parent: QWidget = None) -> QWidget:
        return PlungerPanel(parent)


def create_instrument():
    return PlungerInstrument()
