"""PACE4 evaporation cross-section instrument."""

from PyQt6.QtWidgets import QWidget
from app.instruments.base_instrument import BaseInstrument
from app.instruments.nuclear_utils.ui.pace4_panel import Pace4Panel


class Pace4Instrument(BaseInstrument):
    def name(self) -> str:
        return "PACE4"

    def description(self) -> str:
        return (
            "Parse PACE4 Monte Carlo evaporation output: residue table "
            "and cross-section vs beam energy plot"
        )

    def icon_text(self) -> str:
        return "\U0001F4CA"  # 📊

    def create_panel(self, parent: QWidget = None) -> QWidget:
        return Pace4Panel(parent)


def create_instrument():
    return Pace4Instrument()
