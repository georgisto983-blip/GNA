"""GNA application theme manager — multiple colour schemes with runtime switching."""

from string import Template
from typing import Any


# ──────────────────────────────────────────────────────────────────
# QSS template  (uses $key substitution via string.Template)
# ──────────────────────────────────────────────────────────────────
_QSS_TEMPLATE = Template("""
/* ── Global ── */
QMainWindow, QWidget {
    background-color: $bg;
    color: $text;
    font-family: 'Segoe UI', 'Ubuntu', 'Cantarell', sans-serif;
    font-size: 13px;
}

/* ── Sidebar list ── */
QListWidget {
    background-color: $bg_dark;
    border: none;
    border-right: 1px solid $surface2;
    padding: 8px 0;
    outline: none;
}
QListWidget::item {
    padding: 14px 16px;
    border: none;
    color: $text_dim;
    font-size: 14px;
    font-weight: bold;
}
QListWidget::item:selected {
    background-color: $bg;
    color: $primary;
    border-left: 3px solid $primary;
}
QListWidget::item:hover:!selected {
    background-color: $surface;
    color: $text_bright;
}

/* ── Buttons ── */
QPushButton {
    background-color: $primary;
    color: $btn_text;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 13px;
    min-width: 80px;
}
QPushButton:hover {
    background-color: $primary_hover;
}
QPushButton:pressed {
    background-color: $primary_dim;
}
QPushButton[secondary="true"] {
    background-color: $surface2;
    color: $text;
}
QPushButton[secondary="true"]:hover {
    background-color: $surface3;
}

/* ── Line edits ── */
QLineEdit {
    background-color: $surface2;
    color: $text;
    border: 1px solid $border;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
    selection-background-color: $primary;
}
QLineEdit:focus {
    border-color: $primary;
}
QLineEdit:disabled {
    color: $text_dim;
    background-color: $surface;
}

/* ── Group boxes ── */
QGroupBox {
    background-color: $surface;
    border: 1px solid $surface2;
    border-radius: 8px;
    margin-top: 16px;
    padding: 16px;
    padding-top: 28px;
    font-weight: bold;
    color: $text_bright;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 10px;
    color: $accent;
}

/* ── Labels ── */
QLabel {
    color: $text;
    background: transparent;
}
QLabel[heading="true"] {
    font-size: 20px;
    font-weight: bold;
    color: $text;
    padding-bottom: 2px;
}
QLabel[subheading="true"] {
    font-size: 13px;
    color: $text_dim;
    padding-bottom: 8px;
}
QLabel[result="true"] {
    font-size: 17px;
    font-weight: bold;
    color: $success;
    padding: 12px;
    background-color: $surface;
    border: 1px solid $surface2;
    border-radius: 6px;
}

/* ── Table ── */
QTableWidget {
    background-color: $surface;
    color: $text;
    gridline-color: $surface2;
    border: 1px solid $surface2;
    border-radius: 4px;
    selection-background-color: $surface2;
}
QTableWidget::item {
    padding: 4px 8px;
}
QTableWidget::item:selected {
    background-color: $surface2;
}
QHeaderView::section {
    background-color: $surface2;
    color: $text_bright;
    padding: 8px;
    border: none;
    border-right: 1px solid $border;
    border-bottom: 1px solid $border;
    font-weight: bold;
    font-size: 12px;
}

/* ── Tabs ── */
QTabWidget::pane {
    border: 1px solid $surface2;
    background-color: $bg;
    border-radius: 0 0 4px 4px;
    top: -1px;
}
QTabBar::tab {
    background-color: $bg_dark;
    color: $text_dim;
    padding: 10px 24px;
    border: 1px solid $surface2;
    border-bottom: none;
    margin-right: 2px;
    border-radius: 4px 4px 0 0;
    font-weight: bold;
}
QTabBar::tab:selected {
    background-color: $bg;
    color: $primary;
    border-bottom: 2px solid $primary;
}
QTabBar::tab:hover:!selected {
    color: $text_bright;
    background-color: $surface;
}

/* ── Scroll bars ── */
QScrollBar:vertical {
    background-color: $bg;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: $surface2;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: $border;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background-color: $bg;
    height: 8px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background-color: $surface2;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ── Combo box ── */
QComboBox {
    background-color: $surface2;
    color: $text;
    border: 1px solid $border;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 12px;
}
QComboBox:hover { border-color: $primary; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: $surface;
    color: $text;
    selection-background-color: $surface2;
    border: 1px solid $border;
}

/* ── Splitter ── */
QSplitter::handle {
    background-color: $surface2;
    width: 2px;
    height: 2px;
}

/* ── Message boxes & tooltips ── */
QMessageBox {
    background-color: $surface;
    color: $text;
}
QMessageBox QLabel {
    color: $text;
}
QMessageBox QPushButton {
    min-width: 80px;
}
QToolTip {
    background-color: $surface2;
    color: $text;
    border: 1px solid $border;
    padding: 6px;
    border-radius: 4px;
}
""")


def _build_qss(c: dict) -> str:
    """Build QSS string from a colour palette dict."""
    return _QSS_TEMPLATE.safe_substitute(c)


# ──────────────────────────────────────────────────────────────────
# Colour palettes
# ──────────────────────────────────────────────────────────────────

COLORS = {
    'bg': '#1a1b26',
    'bg_dark': '#16161e',
    'surface': '#1e1e2e',
    'surface2': '#292e42',
    'surface3': '#33384d',
    'border': '#3b4261',
    'text': '#c0caf5',
    'text_dim': '#565f89',
    'text_bright': '#a9b1d6',
    'primary': '#7aa2f7',
    'primary_hover': '#89b4fa',
    'primary_dim': '#6690e0',
    'btn_text': '#1a1b26',
    'accent': '#bb9af7',
    'success': '#9ece6a',
    'error': '#f7768e',
    'warning': '#e0af68',
}


STYLESHEET = _build_qss(COLORS)  # backward-compat alias

# ──────────────────────────────────────────────────────────────────
# Plot styles per theme
# ──────────────────────────────────────────────────────────────────

_NORD_COLORS = {
    'bg': '#2e3440',
    'bg_dark': '#242831',
    'surface': '#3b4252',
    'surface2': '#434c5e',
    'surface3': '#4f5a6e',
    'border': '#4c566a',
    'text': '#eceff4',
    'text_dim': '#d8dee9',
    'text_bright': '#e5e9f0',
    'primary': '#88c0d0',
    'primary_hover': '#81a1c1',
    'primary_dim': '#6b97b0',
    'btn_text': '#2e3440',
    'accent': '#b48ead',
    'success': '#a3be8c',
    'error': '#bf616a',
    'warning': '#ebcb8b',
}

_MONOKAI_COLORS = {
    'bg': '#272822',
    'bg_dark': '#1e1f1c',
    'surface': '#2d2e27',
    'surface2': '#3e3d32',
    'surface3': '#4a4940',
    'border': '#49483e',
    'text': '#f8f8f2',
    'text_dim': '#75715e',
    'text_bright': '#cfcfc2',
    'primary': '#66d9e8',
    'primary_hover': '#a1efe4',
    'primary_dim': '#3ec5d4',
    'btn_text': '#272822',
    'accent': '#ae81ff',
    'success': '#a6e22e',
    'error': '#f92672',
    'warning': '#fd971f',
}

_SCIENTIFIC_LIGHT_COLORS = {
    'bg': '#f5f5f5',
    'bg_dark': '#ebebeb',
    'surface': '#ffffff',
    'surface2': '#e8e8e8',
    'surface3': '#d8d8d8',
    'border': '#c0c0c0',
    'text': '#212121',
    'text_dim': '#757575',
    'text_bright': '#424242',
    'primary': '#1565c0',
    'primary_hover': '#1976d2',
    'primary_dim': '#0d47a1',
    'btn_text': '#ffffff',
    'accent': '#6a1b9a',
    'success': '#2e7d32',
    'error': '#c62828',
    'warning': '#e65100',
}

_MINIMAL_DARK_COLORS = {
    'bg': '#141414',
    'bg_dark': '#0d0d0d',
    'surface': '#1c1c1c',
    'surface2': '#242424',
    'surface3': '#2e2e2e',
    'border': '#383838',
    'text': '#e8e8e8',
    'text_dim': '#888888',
    'text_bright': '#c0c0c0',
    'primary': '#4a9eff',
    'primary_hover': '#6ab3ff',
    'primary_dim': '#3080e0',
    'btn_text': '#ffffff',
    'accent': '#a06fff',
    'success': '#5abf5a',
    'error': '#e05050',
    'warning': '#d4a040',
}


_PLOT_STYLES = {
    'Tokyo Night': {
        'figure.facecolor': '#1e1e2e',
        'axes.facecolor': '#1a1b26',
        'axes.edgecolor': '#3b4261',
        'axes.labelcolor': '#c0caf5',
        'axes.titlecolor': '#c0caf5',
        'xtick.color': '#565f89',
        'ytick.color': '#565f89',
        'text.color': '#c0caf5',
        'grid.color': '#292e42',
        'grid.alpha': 0.6,
        'font.size': 11,
        'legend.facecolor': '#1e1e2e',
        'legend.edgecolor': '#3b4261',
        'legend.labelcolor': '#c0caf5',
    },
    'Nord': {
        'figure.facecolor': '#3b4252',
        'axes.facecolor': '#2e3440',
        'axes.edgecolor': '#4c566a',
        'axes.labelcolor': '#eceff4',
        'axes.titlecolor': '#88c0d0',
        'xtick.color': '#d8dee9',
        'ytick.color': '#d8dee9',
        'text.color': '#eceff4',
        'grid.color': '#434c5e',
        'grid.alpha': 0.5,
        'font.size': 11,
        'legend.facecolor': '#3b4252',
        'legend.edgecolor': '#4c566a',
        'legend.labelcolor': '#eceff4',
    },
    'Monokai': {
        'figure.facecolor': '#2d2e27',
        'axes.facecolor': '#272822',
        'axes.edgecolor': '#49483e',
        'axes.labelcolor': '#f8f8f2',
        'axes.titlecolor': '#66d9e8',
        'xtick.color': '#75715e',
        'ytick.color': '#75715e',
        'text.color': '#f8f8f2',
        'grid.color': '#3e3d32',
        'grid.alpha': 0.5,
        'font.size': 11,
        'legend.facecolor': '#2d2e27',
        'legend.edgecolor': '#49483e',
        'legend.labelcolor': '#f8f8f2',
    },
    'Scientific Light': {
        'figure.facecolor': '#ffffff',
        'axes.facecolor': '#f5f5f5',
        'axes.edgecolor': '#c0c0c0',
        'axes.labelcolor': '#212121',
        'axes.titlecolor': '#1565c0',
        'xtick.color': '#424242',
        'ytick.color': '#424242',
        'text.color': '#212121',
        'grid.color': '#e0e0e0',
        'grid.alpha': 0.8,
        'font.size': 11,
        'legend.facecolor': '#ffffff',
        'legend.edgecolor': '#c0c0c0',
        'legend.labelcolor': '#212121',
    },
    'Minimal Dark': {
        'figure.facecolor': '#1c1c1c',
        'axes.facecolor': '#141414',
        'axes.edgecolor': '#383838',
        'axes.labelcolor': '#e8e8e8',
        'axes.titlecolor': '#4a9eff',
        'xtick.color': '#888888',
        'ytick.color': '#888888',
        'text.color': '#e8e8e8',
        'grid.color': '#242424',
        'grid.alpha': 0.5,
        'font.size': 11,
        'legend.facecolor': '#1c1c1c',
        'legend.edgecolor': '#383838',
        'legend.labelcolor': '#e8e8e8',
    },
}

_PALETTES = {
    'Tokyo Night': COLORS,
    'Nord': _NORD_COLORS,
    'Monokai': _MONOKAI_COLORS,
    'Scientific Light': _SCIENTIFIC_LIGHT_COLORS,
    'Minimal Dark': _MINIMAL_DARK_COLORS,
}

THEMES = {name: {
    'qss': _build_qss(_PALETTES[name]),
    'plot': _PLOT_STYLES[name],
} for name in _PALETTES}

# ──────────────────────────────────────────────────────────────────
# Active theme state (mutable — updated in-place by apply_theme)
# ──────────────────────────────────────────────────────────────────

PLOT_STYLE: dict = dict(_PLOT_STYLES['Tokyo Night'])
_active_theme: str = 'Tokyo Night'


def apply_theme(name: str, app) -> None:
    """Switch the active theme at runtime.

    Updates both the Qt stylesheet and the matplotlib PLOT_STYLE dict.
    All panels that redraw their figures will automatically pick up
    the new style on the next render.
    """
    global _active_theme
    if name not in THEMES:
        return
    theme = THEMES[name]
    app.setStyleSheet(theme['qss'])
    PLOT_STYLE.clear()
    PLOT_STYLE.update(theme['plot'])
    _active_theme = name
    import matplotlib
    matplotlib.rcParams.update(PLOT_STYLE)


def active_theme() -> str:
    return _active_theme


# ── Backward-compat aliases for old imports ──────────────────────
NORD_COLORS = _NORD_COLORS
NORD_PLOT_STYLE = _PLOT_STYLES['Nord']
MONOKAI_COLORS = _MONOKAI_COLORS
MONOKAI_PLOT_STYLE = _PLOT_STYLES['Monokai']
SCIENTIFIC_LIGHT_COLORS = _SCIENTIFIC_LIGHT_COLORS
SCIENTIFIC_LIGHT_PLOT_STYLE = _PLOT_STYLES['Scientific Light']
