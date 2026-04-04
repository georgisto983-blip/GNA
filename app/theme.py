"""GNA application theme manager — colour schemes (dark + light families) with runtime switching."""

import json
from pathlib import Path
from string import Template
from typing import Any

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "settings.json"


def _load_saved_theme() -> str | None:
    """Read the last-used theme name from settings.json."""
    try:
        data = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
        return data.get("theme")
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def _save_theme(name: str) -> None:
    """Write the current theme name to settings.json."""
    try:
        data = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    data["theme"] = name
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ──────────────────────────────────────────────────────────────────
# QSS template  (uses $key substitution via string.Template)
# Sharp corners (0 px radius), modern professional look
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
    border-right: 1px solid $border;
    padding: 4px 0;
    outline: none;
}
QListWidget::item {
    padding: 11px 16px;
    border: none;
    color: $text_dim;
    font-size: 13px;
    font-weight: bold;
    border-left: 3px solid transparent;
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
    border-radius: 0px;
    padding: 8px 22px;
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
    background-color: transparent;
    color: $text_bright;
    border: 1px solid $border;
}
QPushButton[secondary="true"]:hover {
    background-color: $surface2;
    color: $text;
}

/* ── Line edits ── */
QLineEdit {
    background-color: $surface2;
    color: $text;
    border: 1px solid $border;
    border-radius: 0px;
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
    border: 1px solid $border;
    border-radius: 0px;
    margin-top: 14px;
    padding: 14px;
    padding-top: 26px;
    font-weight: bold;
    color: $text_bright;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 3px 10px;
    color: $accent;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Labels ── */
QLabel {
    color: $text;
    background: transparent;
}
QLabel[heading="true"] {
    font-size: 18px;
    font-weight: bold;
    color: $text;
    padding-bottom: 2px;
}
QLabel[subheading="true"] {
    font-size: 12px;
    color: $text_dim;
    padding-bottom: 6px;
}
QLabel[result="true"] {
    font-size: 16px;
    font-weight: bold;
    color: $success;
    padding: 10px 14px;
    background-color: $surface;
    border: 1px solid $border;
    border-radius: 0px;
}

/* ── Table ── */
QTableWidget {
    background-color: $surface;
    color: $text;
    gridline-color: $border;
    border: 1px solid $border;
    border-radius: 0px;
    selection-background-color: $surface2;
}
QTableWidget::item {
    padding: 6px 8px;
}
QTableWidget::item:selected {
    background-color: $surface2;
}
QHeaderView::section {
    background-color: $surface2;
    color: $text_bright;
    padding: 7px 8px;
    border: none;
    border-right: 1px solid $border;
    border-bottom: 1px solid $border;
    font-weight: bold;
    font-size: 12px;
}

/* ── Tabs ── */
QTabWidget::pane {
    border: 1px solid $border;
    background-color: $bg;
    border-radius: 0px;
    top: -1px;
}
QTabBar::tab {
    background-color: $bg_dark;
    color: $text_dim;
    padding: 9px 22px;
    border: 1px solid $border;
    border-bottom: none;
    margin-right: 1px;
    border-radius: 0px;
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
    width: 7px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: $surface2;
    border-radius: 0px;
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
    height: 7px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background-color: $surface2;
    border-radius: 0px;
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
    border-radius: 0px;
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
    background-color: $border;
    width: 1px;
    height: 1px;
}

/* ── Spin boxes ── */
QSpinBox, QDoubleSpinBox {
    background-color: $surface2;
    color: $text;
    border: 1px solid $border;
    border-radius: 0px;
    padding: 4px 8px;
    font-size: 13px;
}

/* ── Text edits ── */
QTextEdit, QPlainTextEdit {
    background-color: $surface;
    color: $text;
    border: 1px solid $border;
    border-radius: 0px;
    selection-background-color: $primary;
}

/* ── Check boxes ── */
QCheckBox {
    spacing: 6px;
    color: $text;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid $border;
    background-color: $surface2;
    border-radius: 0px;
}
QCheckBox::indicator:checked {
    background-color: $primary;
    border-color: $primary;
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
    border-radius: 0px;
}

/* ── Sidebar container ── */
QWidget#sidebar {
    background-color: $bg_dark;
    border-right: 1px solid $border;
}
""")


def _build_qss(c: dict) -> str:
    """Build QSS string from a colour palette dict."""
    return _QSS_TEMPLATE.safe_substitute(c)


# ──────────────────────────────────────────────────────────────────
# Colour palettes — 9 families × 2 variants (dark + light)
# ──────────────────────────────────────────────────────────────────

# A1 — Neon Prism (DEFAULT)
_NEON_PRISM_COLORS = {
    'bg': '#141028',
    'bg_dark': '#0e0b1e',
    'surface': '#1e1a3a',
    'surface2': '#28244c',
    'surface3': '#34305e',
    'border': '#3e3870',
    'text': '#e8e8ff',
    'text_dim': '#6060a0',
    'text_bright': '#b0b0d8',
    'primary': '#b060ff',
    'primary_hover': '#c480ff',
    'primary_dim': '#9040e0',
    'btn_text': '#08080e',
    'accent': '#4090ff',
    'success': '#40e890',
    'error': '#ff4070',
    'warning': '#ffb840',
}

# A2 — Neon Prism Light
_NEON_PRISM_LIGHT_COLORS = {
    'bg': '#dcd4f2',
    'bg_dark': '#d0c8e6',
    'surface': '#e8e0fa',
    'surface2': '#cec6e0',
    'surface3': '#c0b8d2',
    'border': '#aca0c4',
    'text': '#2a2040',
    'text_dim': '#9088b0',
    'text_bright': '#504068',
    'primary': '#8040d0',
    'primary_hover': '#9458e0',
    'primary_dim': '#6c30b8',
    'btn_text': '#ffffff',
    'accent': '#3070e0',
    'success': '#1a9a50',
    'error': '#d03050',
    'warning': '#c08020',
}

# B1 — Ultraviolet
_ULTRAVIOLET_COLORS = {
    'bg': '#0c1030',
    'bg_dark': '#080c24',
    'surface': '#141842',
    'surface2': '#1e2252',
    'surface3': '#282c60',
    'border': '#30366c',
    'text': '#e0e0ff',
    'text_dim': '#5050a0',
    'text_bright': '#a0a0d0',
    'primary': '#6080ff',
    'primary_hover': '#80a0ff',
    'primary_dim': '#4060e0',
    'btn_text': '#060610',
    'accent': '#c060ff',
    'success': '#30e870',
    'error': '#ff4060',
    'warning': '#ffc040',
}

# B2 — Ultraviolet Light
_ULTRAVIOLET_LIGHT_COLORS = {
    'bg': '#d2d6ee',
    'bg_dark': '#c6cadf',
    'surface': '#dde0f5',
    'surface2': '#c4c8de',
    'surface3': '#b8bcd2',
    'border': '#a4a8c0',
    'text': '#1a2040',
    'text_dim': '#8890b0',
    'text_bright': '#3a4060',
    'primary': '#4060d0',
    'primary_hover': '#5070e0',
    'primary_dim': '#3050b8',
    'btn_text': '#ffffff',
    'accent': '#9050d0',
    'success': '#18884a',
    'error': '#c03040',
    'warning': '#b07818',
}

# C1 — Plasma Burst
_PLASMA_BURST_COLORS = {
    'bg': '#17102a',
    'bg_dark': '#0f0a1e',
    'surface': '#21183a',
    'surface2': '#2d2048',
    'surface3': '#392858',
    'border': '#46326c',
    'text': '#f0e8ff',
    'text_dim': '#705088',
    'text_bright': '#c0a8d8',
    'primary': '#e040c0',
    'primary_hover': '#f060d0',
    'primary_dim': '#c030a0',
    'btn_text': '#08040a',
    'accent': '#5090ff',
    'success': '#40e880',
    'error': '#ff3060',
    'warning': '#ffb030',
}

# C2 — Plasma Burst Light
_PLASMA_BURST_LIGHT_COLORS = {
    'bg': '#e0cedd',
    'bg_dark': '#d4c2d1',
    'surface': '#ecdce9',
    'surface2': '#cfbdcc',
    'surface3': '#c2aebe',
    'border': '#ae98ab',
    'text': '#2a1828',
    'text_dim': '#a088a0',
    'text_bright': '#503850',
    'primary': '#b02890',
    'primary_hover': '#c438a0',
    'primary_dim': '#981878',
    'btn_text': '#ffffff',
    'accent': '#3878d0',
    'success': '#1a8848',
    'error': '#c02840',
    'warning': '#b87018',
}

# D1 — Celestial
_CELESTIAL_COLORS = {
    'bg': '#10102e',
    'bg_dark': '#0a0a22',
    'surface': '#18183c',
    'surface2': '#22224c',
    'surface3': '#2c2c5a',
    'border': '#363668',
    'text': '#e4e4ff',
    'text_dim': '#5858a0',
    'text_bright': '#a8a8d4',
    'primary': '#a080ff',
    'primary_hover': '#b898ff',
    'primary_dim': '#8060e0',
    'btn_text': '#080810',
    'accent': '#5098ff',
    'success': '#44e888',
    'error': '#ff4070',
    'warning': '#ffc040',
}

# D2 — Celestial Light
_CELESTIAL_LIGHT_COLORS = {
    'bg': '#dad4f2',
    'bg_dark': '#cec8e6',
    'surface': '#e5dff8',
    'surface2': '#cac4e0',
    'surface3': '#bcb6d2',
    'border': '#a8a2c4',
    'text': '#201838',
    'text_dim': '#9090b0',
    'text_bright': '#403858',
    'primary': '#6850b8',
    'primary_hover': '#7860c8',
    'primary_dim': '#5840a0',
    'btn_text': '#ffffff',
    'accent': '#3880d0',
    'success': '#1a904c',
    'error': '#b82840',
    'warning': '#a87018',
}

# ── E: Teal ──

_TEAL_COLORS = {
    'bg': '#0a1e22',
    'bg_dark': '#06161a',
    'surface': '#122c32',
    'surface2': '#1c3a42',
    'surface3': '#264a52',
    'border': '#305a64',
    'text': '#e0f4f8',
    'text_dim': '#508890',
    'text_bright': '#90c8d0',
    'primary': '#30c8c8',
    'primary_hover': '#50e0e0',
    'primary_dim': '#20a8a8',
    'btn_text': '#06161a',
    'accent': '#60a0ff',
    'success': '#40e890',
    'error': '#ff5060',
    'warning': '#ffb840',
}

_TEAL_LIGHT_COLORS = {
    'bg': '#c8e4e4',
    'bg_dark': '#bcd8d8',
    'surface': '#d6f0f0',
    'surface2': '#b4d0d0',
    'surface3': '#a4c2c2',
    'border': '#88aaaa',
    'text': '#0e2828',
    'text_dim': '#608888',
    'text_bright': '#2a5050',
    'primary': '#188888',
    'primary_hover': '#209898',
    'primary_dim': '#107070',
    'btn_text': '#ffffff',
    'accent': '#3070c0',
    'success': '#18884a',
    'error': '#c03040',
    'warning': '#b07818',
}

# ── F: Emerald ──

_EMERALD_COLORS = {
    'bg': '#0a200e',
    'bg_dark': '#061808',
    'surface': '#142c18',
    'surface2': '#1e3c22',
    'surface3': '#284c2e',
    'border': '#325c38',
    'text': '#e0ffe8',
    'text_dim': '#508860',
    'text_bright': '#90d0a0',
    'primary': '#30d060',
    'primary_hover': '#48e878',
    'primary_dim': '#20b048',
    'btn_text': '#061808',
    'accent': '#60b0ff',
    'success': '#40e880',
    'error': '#ff5060',
    'warning': '#ffb840',
}

_EMERALD_LIGHT_COLORS = {
    'bg': '#cce4d0',
    'bg_dark': '#c0d8c4',
    'surface': '#daf2de',
    'surface2': '#b8d0bc',
    'surface3': '#a8c2ac',
    'border': '#8caa90',
    'text': '#102818',
    'text_dim': '#608868',
    'text_bright': '#2a5032',
    'primary': '#18882e',
    'primary_hover': '#20983a',
    'primary_dim': '#107020',
    'btn_text': '#ffffff',
    'accent': '#3870c0',
    'success': '#18884a',
    'error': '#c03040',
    'warning': '#b07818',
}

# ── G: Golden ──

_GOLDEN_COLORS = {
    'bg': '#1e1808',
    'bg_dark': '#161204',
    'surface': '#2a2210',
    'surface2': '#382e18',
    'surface3': '#463a22',
    'border': '#56482c',
    'text': '#fff4e0',
    'text_dim': '#a09060',
    'text_bright': '#d0c090',
    'primary': '#e0b020',
    'primary_hover': '#f0c838',
    'primary_dim': '#c89810',
    'btn_text': '#161204',
    'accent': '#60a0ff',
    'success': '#40e880',
    'error': '#ff5060',
    'warning': '#ffb840',
}

_GOLDEN_LIGHT_COLORS = {
    'bg': '#e8dcc0',
    'bg_dark': '#dcd0b4',
    'surface': '#f4e8d0',
    'surface2': '#d4c8ac',
    'surface3': '#c8bc9c',
    'border': '#b0a480',
    'text': '#282010',
    'text_dim': '#908060',
    'text_bright': '#504828',
    'primary': '#b08810',
    'primary_hover': '#c09818',
    'primary_dim': '#987008',
    'btn_text': '#ffffff',
    'accent': '#5080c0',
    'success': '#18884a',
    'error': '#c03040',
    'warning': '#b07818',
}

# ── H: Amber ──

_AMBER_COLORS = {
    'bg': '#221408',
    'bg_dark': '#1a0e04',
    'surface': '#2e1e10',
    'surface2': '#3c2a1a',
    'surface3': '#4a3624',
    'border': '#5a4430',
    'text': '#fff0e0',
    'text_dim': '#a08060',
    'text_bright': '#d0b890',
    'primary': '#e08830',
    'primary_hover': '#f0a048',
    'primary_dim': '#c87020',
    'btn_text': '#1a0e04',
    'accent': '#60a0ff',
    'success': '#40e880',
    'error': '#ff5060',
    'warning': '#ffb840',
}

_AMBER_LIGHT_COLORS = {
    'bg': '#e8d4c0',
    'bg_dark': '#dcc8b4',
    'surface': '#f4e0d0',
    'surface2': '#d4c0ac',
    'surface3': '#c8b49c',
    'border': '#b09c80',
    'text': '#281808',
    'text_dim': '#907860',
    'text_bright': '#504028',
    'primary': '#b06818',
    'primary_hover': '#c07820',
    'primary_dim': '#985010',
    'btn_text': '#ffffff',
    'accent': '#5080c0',
    'success': '#18884a',
    'error': '#c03040',
    'warning': '#b07818',
}

# ── I: Scarlet ──

_SCARLET_COLORS = {
    'bg': '#220c0c',
    'bg_dark': '#1a0606',
    'surface': '#2e1414',
    'surface2': '#3c2020',
    'surface3': '#4c2c2c',
    'border': '#5c3838',
    'text': '#ffe8e8',
    'text_dim': '#a06060',
    'text_bright': '#d0a0a0',
    'primary': '#e03838',
    'primary_hover': '#f05050',
    'primary_dim': '#c82828',
    'btn_text': '#1a0606',
    'accent': '#60a0ff',
    'success': '#40e880',
    'error': '#ff5060',
    'warning': '#ffb840',
}

_SCARLET_LIGHT_COLORS = {
    'bg': '#e8cccc',
    'bg_dark': '#dcc0c0',
    'surface': '#f4dada',
    'surface2': '#d4b8b8',
    'surface3': '#c8aaaa',
    'border': '#b09090',
    'text': '#281010',
    'text_dim': '#906060',
    'text_bright': '#503030',
    'primary': '#b02828',
    'primary_hover': '#c03030',
    'primary_dim': '#981818',
    'btn_text': '#ffffff',
    'accent': '#5080c0',
    'success': '#18884a',
    'error': '#c03040',
    'warning': '#b07818',
}

# ── J: Silver ──

_SILVER_COLORS = {
    'bg': '#1a1c20',
    'bg_dark': '#141618',
    'surface': '#24262c',
    'surface2': '#30343a',
    'surface3': '#3c4048',
    'border': '#4a4e58',
    'text': '#e8eaee',
    'text_dim': '#7880a8',
    'text_bright': '#b0b4c0',
    'primary': '#a0a8c0',
    'primary_hover': '#b8c0d4',
    'primary_dim': '#8890a8',
    'btn_text': '#141618',
    'accent': '#7090d0',
    'success': '#40c878',
    'error': '#e04858',
    'warning': '#d0a040',
}

_SILVER_LIGHT_COLORS = {
    'bg': '#d8dae0',
    'bg_dark': '#ccced4',
    'surface': '#e4e6ea',
    'surface2': '#c8cad0',
    'surface3': '#bcc0c8',
    'border': '#a0a4b0',
    'text': '#1a1c22',
    'text_dim': '#787c88',
    'text_bright': '#3a3e48',
    'primary': '#5c6478',
    'primary_hover': '#6c7488',
    'primary_dim': '#4c5468',
    'btn_text': '#ffffff',
    'accent': '#4870b0',
    'success': '#188848',
    'error': '#b83040',
    'warning': '#a07818',
}

# ── K: Olive Raw Umber ──

_OLIVE_UMBER_COLORS = {
    'bg': '#181a0e',
    'bg_dark': '#121408',
    'surface': '#222618',
    'surface2': '#2e3220',
    'surface3': '#3a3e2a',
    'border': '#484c34',
    'text': '#eaf0d8',
    'text_dim': '#7a8060',
    'text_bright': '#b0b890',
    'primary': '#8a9040',
    'primary_hover': '#9ca850',
    'primary_dim': '#747a30',
    'btn_text': '#121408',
    'accent': '#c09040',
    'success': '#60c060',
    'error': '#d04840',
    'warning': '#d0a030',
}

_OLIVE_UMBER_LIGHT_COLORS = {
    'bg': '#dcdcc4',
    'bg_dark': '#d0d0b8',
    'surface': '#e8e8d0',
    'surface2': '#ccceb4',
    'surface3': '#c0c2a8',
    'border': '#a8aa8c',
    'text': '#1a1c10',
    'text_dim': '#7a7c60',
    'text_bright': '#44462a',
    'primary': '#686c28',
    'primary_hover': '#787c34',
    'primary_dim': '#585c1c',
    'btn_text': '#ffffff',
    'accent': '#987020',
    'success': '#308838',
    'error': '#b03030',
    'warning': '#987018',
}


# ──────────────────────────────────────────────────────────────────
# Plot styles per theme
# ──────────────────────────────────────────────────────────────────

def _make_plot_style(c: dict) -> dict:
    """Generate a matplotlib plot style dict from a palette."""
    return {
        'figure.facecolor': c['surface'],
        'axes.facecolor': c['bg'],
        'axes.edgecolor': c['border'],
        'axes.labelcolor': c['text'],
        'axes.titlecolor': c['text'],
        'xtick.color': c['text_dim'],
        'ytick.color': c['text_dim'],
        'text.color': c['text'],
        'grid.color': c['surface2'],
        'grid.alpha': 0.6,
        'font.size': 11,
        'legend.facecolor': c['surface'],
        'legend.edgecolor': c['border'],
        'legend.labelcolor': c['text'],
    }


_PALETTES = {
    'Neon Prism': _NEON_PRISM_COLORS,
    'Neon Prism Light': _NEON_PRISM_LIGHT_COLORS,
    'Ultraviolet': _ULTRAVIOLET_COLORS,
    'Ultraviolet Light': _ULTRAVIOLET_LIGHT_COLORS,
    'Plasma Burst': _PLASMA_BURST_COLORS,
    'Plasma Burst Light': _PLASMA_BURST_LIGHT_COLORS,
    'Celestial': _CELESTIAL_COLORS,
    'Celestial Light': _CELESTIAL_LIGHT_COLORS,
    'Teal': _TEAL_COLORS,
    'Teal Light': _TEAL_LIGHT_COLORS,
    'Emerald': _EMERALD_COLORS,
    'Emerald Light': _EMERALD_LIGHT_COLORS,
    'Golden': _GOLDEN_COLORS,
    'Golden Light': _GOLDEN_LIGHT_COLORS,
    'Amber': _AMBER_COLORS,
    'Amber Light': _AMBER_LIGHT_COLORS,
    'Scarlet': _SCARLET_COLORS,
    'Scarlet Light': _SCARLET_LIGHT_COLORS,
    'Silver': _SILVER_COLORS,
    'Silver Light': _SILVER_LIGHT_COLORS,
    'Olive Raw Umber': _OLIVE_UMBER_COLORS,
    'Olive Raw Umber Light': _OLIVE_UMBER_LIGHT_COLORS,
}

# ── Theme families (for the UI two-step selector) ──
THEME_FAMILIES = [
    'Neon Prism', 'Ultraviolet', 'Plasma Burst', 'Celestial',
    'Teal', 'Emerald', 'Golden', 'Amber', 'Scarlet',
    'Silver', 'Olive Raw Umber',
]

_PLOT_STYLES = {name: _make_plot_style(pal) for name, pal in _PALETTES.items()}

THEMES = {name: {
    'qss': _build_qss(_PALETTES[name]),
    'plot': _PLOT_STYLES[name],
} for name in _PALETTES}

# ── Register animal theme palettes ──
from app.animal_themes import ANIMAL_THEMES as _ANIMAL_THEMES

for _aname, _adata in _ANIMAL_THEMES.items():
    for _variant, _suffix in [('dark', ''), ('light', ' Light')]:
        _full = f"{_aname}{_suffix}"
        _pal = _adata[_variant]
        _PALETTES[_full] = _pal
        _PLOT_STYLES[_full] = _make_plot_style(_pal)
        THEMES[_full] = {'qss': _build_qss(_pal), 'plot': _PLOT_STYLES[_full]}

# Default palette (resolves saved theme or falls back to Neon Prism)
_saved = _load_saved_theme()
COLORS = _PALETTES.get(_saved, _NEON_PRISM_COLORS)
STYLESHEET = _build_qss(COLORS)  # backward-compat alias

# ──────────────────────────────────────────────────────────────────
# Active theme state (mutable — updated in-place by apply_theme)
# ──────────────────────────────────────────────────────────────────

PLOT_STYLE: dict = dict(_PLOT_STYLES['Neon Prism'])
_active_theme: str = _load_saved_theme() or 'Neon Prism'
if _active_theme not in THEMES:
    _active_theme = 'Neon Prism'
# Pre-load saved theme's plot style
PLOT_STYLE.clear()
PLOT_STYLE.update(_PLOT_STYLES.get(_active_theme, _PLOT_STYLES['Neon Prism']))


def apply_theme(name: str, app) -> None:
    """Switch the active theme at runtime and persist the choice."""
    global _active_theme
    if name not in THEMES:
        return
    theme = THEMES[name]
    app.setStyleSheet(theme['qss'])
    PLOT_STYLE.clear()
    PLOT_STYLE.update(theme['plot'])
    _active_theme = name
    _save_theme(name)
    import matplotlib
    matplotlib.rcParams.update(PLOT_STYLE)


def active_theme() -> str:
    return _active_theme


def get_palette(name: str = None) -> dict:
    """Return the colour palette dict for a theme (default: active theme)."""
    if name is None:
        name = _active_theme
    return _PALETTES.get(name, _NEON_PRISM_COLORS)
