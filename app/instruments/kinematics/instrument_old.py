"""Kinematics calculator instrument."""

from PyQt6.QtWidgets import QWidget
from app.instruments.base_instrument import BaseInstrument
from app.instruments.nuclear_utils.ui.kinematics_panel import KinematicsPanel


class KinematicsInstrument(BaseInstrument):
    def name(self) -> str:
        return "Kinematics"

    def description(self) -> str:
        return "Two-body kinematics: lab ↔ CM angles, recoil energies, Q-value"

    def icon_text(self) -> str:
        return "\U0001F535"  # 🔵

    def create_panel(self, parent: QWidget = None) -> QWidget:
        return KinematicsPanel(parent)


def create_instrument():
    return KinematicsInstrument()
