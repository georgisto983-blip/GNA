"""GNA — Georgi's Nuclear Assistant v2.0

Desktop application for nuclear physics calculations and experiment support.
"""

import sys
import matplotlib
matplotlib.use("QtAgg")  # must be set before any other matplotlib imports

from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow
from app.theme import STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GNA")
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()