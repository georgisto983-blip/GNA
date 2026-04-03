"""Nuclear Utilities main panel — sub-tabs for each tool."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from app.instruments.nuclear_utils.ui.beam_yield_panel import BeamYieldPanel
from app.instruments.nuclear_utils.ui.j_coupling_panel import JCouplingPanel
from app.instruments.nuclear_utils.ui.kinematics_panel import KinematicsPanel
from app.instruments.nuclear_utils.ui.pace4_panel import Pace4Panel


class NuclearUtilsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        title = QLabel("Nuclear Utilities — Toolbox")
        title.setProperty("heading", True)
        layout.addWidget(title)

        subtitle = QLabel(
            "Common nuclear physics calculations: yield estimates, "
            "kinematics, angular momentum coupling, PACE4 cross sections"
        )
        subtitle.setProperty("subheading", True)
        layout.addWidget(subtitle)

        tabs = QTabWidget()
        tabs.addTab(BeamYieldPanel(), "Beam Yield")
        tabs.addTab(KinematicsPanel(), "Kinematics")
        tabs.addTab(JCouplingPanel(), "J-Coupling")
        tabs.addTab(Pace4Panel(), "PACE4 Plot")
        layout.addWidget(tabs, stretch=1)
