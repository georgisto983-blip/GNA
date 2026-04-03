"""Plunger instrument main panel — tabs for single and multiple distances."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from app.instruments.plunger.ui.single_distance_panel import SingleDistancePanel
from app.instruments.plunger.ui.multi_distance_panel import MultiDistancePanel


class PlungerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        title = QLabel("Plunger — RDDS Half-Life Calculator")
        title.setProperty("heading", True)
        layout.addWidget(title)

        subtitle = QLabel(
            "Calculate nuclear excited-state half-lives using the "
            "Recoil Distance Doppler Shift method"
        )
        subtitle.setProperty("subheading", True)
        layout.addWidget(subtitle)

        tabs = QTabWidget()
        tabs.addTab(SingleDistancePanel(), "Single Distance")
        tabs.addTab(MultiDistancePanel(), "Multiple Distances")
        layout.addWidget(tabs)
