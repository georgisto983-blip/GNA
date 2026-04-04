"""Talmi Calculator instrument — Empirical Shell Model B(E2) transition probabilities."""

from PyQt6.QtWidgets import QWidget
from app.instruments.base_instrument import BaseInstrument
from app.instruments.talmi_calculator.ui.talmi_panel import TalmiPanel


class TalmiCalculatorInstrument(BaseInstrument):
    def name(self) -> str:
        return "Talmi Calculator"

    def description(self) -> str:
        return (
            "Calculate B(E2) transition probabilities using the "
            "Talmi Empirical Shell Model procedure (j = 9/2 shell)"
        )

    def icon_text(self) -> str:
        return "\U0001f4ca"  # bar chart emoji

    def create_panel(self, parent: QWidget = None) -> QWidget:
        return TalmiPanel(parent)


def create_instrument():
    return TalmiCalculatorInstrument()
