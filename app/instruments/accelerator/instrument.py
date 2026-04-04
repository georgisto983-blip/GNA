"""Accelerator instrument — combines Kinematics and Beam Yield into tabbed panel."""

from PyQt6.QtWidgets import QWidget
from app.instruments.base_instrument import BaseInstrument
from app.instruments.accelerator.ui.accelerator_panel import AcceleratorPanel


class AcceleratorInstrument(BaseInstrument):
    def name(self) -> str:
        return "Accelerator"

    def description(self) -> str:
        return "Beam kinematics, Coulomb barrier, and beam-on-target yield estimates"

    def icon_text(self) -> str:
        return ""

    def create_panel(self, parent: QWidget = None) -> QWidget:
        return AcceleratorPanel(parent)


def create_instrument():
    return AcceleratorInstrument()
