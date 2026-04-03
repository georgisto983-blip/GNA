"""Angular-momentum coupling (J-Coupling) instrument."""

from PyQt6.QtWidgets import QWidget
from app.instruments.base_instrument import BaseInstrument
from app.instruments.nuclear_utils.ui.j_coupling_panel import JCouplingPanel


class JCouplingInstrument(BaseInstrument):
    def name(self) -> str:
        return "J-Coupling"

    def description(self) -> str:
        return "Enumerate allowed spin states from coupling J1 ⊗ J2 → J_total"

    def icon_text(self) -> str:
        return "\U0001F300"  # 🌀

    def create_panel(self, parent: QWidget = None) -> QWidget:
        return JCouplingPanel(parent)


def create_instrument():
    return JCouplingInstrument()
