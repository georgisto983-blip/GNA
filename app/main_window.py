"""GNA main application window — sidebar navigation + instrument panels."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QStackedWidget, QListWidgetItem, QLabel, QFrame, QComboBox,
    QApplication,
)
from PyQt6.QtCore import Qt, QSize
from app.instruments import discover_instruments
from app.theme import THEMES, apply_theme, active_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GNA — Georgi's Nuclear Assistant  v2.0")
        self.setMinimumSize(1100, 750)
        self.resize(1280, 850)

        self.instruments = discover_instruments()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(
            "#sidebar { background-color: #16161e; border-right: 1px solid #292e42; }"
        )
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # App header
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 20, 12)
        title = QLabel("GNA")
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #7aa2f7; background: transparent;"
        )
        subtitle = QLabel("Georgi's Nuclear Assistant")
        subtitle.setStyleSheet(
            "font-size: 11px; color: #565f89; background: transparent;"
        )
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        sidebar_layout.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #292e42; background-color: #292e42; max-height: 1px;")
        sidebar_layout.addWidget(sep)

        # Instrument list
        self.sidebar_list = QListWidget()
        self.sidebar_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        sidebar_layout.addWidget(self.sidebar_list)
        sidebar_layout.addStretch()

        # ── Theme switcher ──
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #292e42; background-color: #292e42; max-height: 1px;")
        sidebar_layout.addWidget(sep2)

        theme_widget = QWidget()
        theme_layout = QVBoxLayout(theme_widget)
        theme_layout.setContentsMargins(16, 8, 16, 4)
        theme_layout.setSpacing(4)
        theme_lbl = QLabel("Theme")
        theme_lbl.setStyleSheet("color: #565f89; font-size: 10px; background: transparent;")
        theme_layout.addWidget(theme_lbl)
        self.theme_combo = QComboBox()
        for name in THEMES:
            self.theme_combo.addItem(name)
        self.theme_combo.setCurrentText(active_theme())
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        sidebar_layout.addWidget(theme_widget)

        version = QLabel("v2.0")
        version.setStyleSheet(
            "color: #3b4261; padding: 12px 20px; font-size: 11px; background: transparent;"
        )
        sidebar_layout.addWidget(version)
        main_layout.addWidget(sidebar)

        # ── Content area ──
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # Register instruments
        for inst in self.instruments:
            item = QListWidgetItem(f"  {inst.icon_text()}   {inst.name()}")
            item.setToolTip(inst.description())
            item.setSizeHint(QSize(220, 52))
            self.sidebar_list.addItem(item)
            self.content_stack.addWidget(inst.create_panel())

        self.sidebar_list.currentRowChanged.connect(self._on_instrument_changed)
        if self.instruments:
            self.sidebar_list.setCurrentRow(0)

    def _on_instrument_changed(self, index):
        if 0 <= index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)

    def _on_theme_changed(self, name: str):
        app = QApplication.instance()
        if app:
            apply_theme(name, app)
