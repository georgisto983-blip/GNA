"""Accelerator panel — tabbed container for Kinematics and Beam Yield."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel
from app.instruments.nuclear_utils.ui.kinematics_panel import KinematicsPanel
from app.instruments.nuclear_utils.ui.beam_yield_panel import BeamYieldPanel


class AcceleratorPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        title = QLabel("Accelerator — Beam & Kinematics")
        title.setProperty("heading", True)
        layout.addWidget(title)

        subtitle = QLabel(
            "Beam kinematics, Coulomb barrier, recoil velocities, "
            "and beam-on-target yield estimates"
        )
        subtitle.setProperty("subheading", True)
        layout.addWidget(subtitle)

        self._tabs = QTabWidget()
        self._kin_panel = KinematicsPanel()
        self._yield_panel = BeamYieldPanel()
        self._tabs.addTab(self._kin_panel, "Kinematics")
        self._tabs.addTab(self._yield_panel, "Beam Yield")
        layout.addWidget(self._tabs, stretch=1)

    def restore_params(self, params: dict):
        """Forward to the correct sub-panel based on param keys."""
        if "E_beam" in params:
            self._tabs.setCurrentIndex(0)
            self._kin_panel.restore_params(params)
        elif "beam_current" in params:
            self._tabs.setCurrentIndex(1)
            self._yield_panel.restore_params(params)
