"""Beam Yield calculator instrument."""

from PyQt6.QtWidgets import QWidget
from app.instruments.base_instrument import BaseInstrument
from app.instruments.nuclear_utils.ui.beam_yield_panel import BeamYieldPanel


class BeamYieldInstrument(BaseInstrument):
    def name(self) -> str:
        return "Beam Yield"

    def description(self) -> str:
        return "Estimate beam-on-target yield from cross section, thickness and beam intensity"

    def icon_text(self) -> str:
        return "\u26A1"  # ⚡

    def create_panel(self, parent: QWidget = None) -> QWidget:
        return BeamYieldPanel(parent)


def create_instrument():
    return BeamYieldInstrument()
