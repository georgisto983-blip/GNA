"""GNA — Georgi's Nuclear Assistant v2.0

Desktop application for nuclear physics calculations and experiment support.
"""

import sys
import matplotlib
matplotlib.use("QtAgg")  # must be set before any other matplotlib imports

from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow
from app.theme import THEMES, active_theme, apply_theme


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GNA")

    # Apply the saved theme (or default)
    apply_theme(active_theme(), app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()