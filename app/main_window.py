"""GNA main application window — sidebar navigation + instrument panels."""

import re
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QStackedWidget, QListWidgetItem, QLabel, QFrame, QComboBox,
    QApplication, QScrollArea, QPushButton, QTextBrowser,
)
from PyQt6.QtCore import Qt, QSize
from app.instruments import discover_instruments
from app.theme import THEMES, THEME_FAMILIES, apply_theme, active_theme
from app.animal_themes import ANIMAL_THEMES, ANIMAL_FAMILIES
from app.constants_panel import ConstantsPanel
from app.theme_overlay import SilhouetteOverlay

# Desired sidebar order — instruments not in this list appear at the end
_SIDEBAR_ORDER = [
    "Plunger (RDDS)",
    "J-Coupling",
    "Talmi Calculator",
    "PACE4",
    "Script Launcher",
    "Accelerator",
]


class _WelcomeWidget(QWidget):
    """Branded welcome screen shown when no instrument is selected."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Center everything
        layout.addStretch(2)

        logo = QLabel("GNA")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(
            "font-size: 72px; font-weight: 900; letter-spacing: 8px;"
        )
        logo.setProperty("heading", True)
        layout.addWidget(logo)

        full_name = QLabel("GEORGI'S NUCLEAR ASSISTANT")
        full_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        full_name.setProperty("subheading", True)
        full_name.setStyleSheet(
            "font-size: 14px; letter-spacing: 4px; padding-bottom: 16px;"
        )
        layout.addWidget(full_name)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedWidth(60)
        divider.setStyleSheet("max-height: 2px;")
        div_container = QWidget()
        div_layout = QHBoxLayout(div_container)
        div_layout.setContentsMargins(0, 0, 0, 0)
        div_layout.addStretch()
        div_layout.addWidget(divider)
        div_layout.addStretch()
        layout.addWidget(div_container)

        desc = QLabel(
            "Nuclear physics analysis suite for RDDS lifetime measurements,\n"
            "kinematics, shell model calculations, and experiment support."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 13px; padding: 16px 40px;")
        desc.setProperty("subheading", True)
        layout.addWidget(desc)

        # Tool chips
        chip_container = QWidget()
        chip_layout = QHBoxLayout(chip_container)
        chip_layout.setContentsMargins(0, 8, 0, 0)
        chip_layout.setSpacing(12)
        chip_layout.addStretch()
        for name in _SIDEBAR_ORDER:
            chip = QLabel(name)
            chip.setStyleSheet(
                "font-size: 11px; font-weight: bold; padding: 5px 12px;"
                "border: 1px solid palette(mid);"
            )
            chip_layout.addWidget(chip)
        chip_layout.addStretch()
        layout.addWidget(chip_container)

        # Recent files
        self._recent_label = QLabel("RECENT FILES")
        self._recent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._recent_label.setStyleSheet(
            "font-size: 10px; letter-spacing: 2px; padding-top: 16px;"
        )
        self._recent_label.setProperty("subheading", True)
        layout.addWidget(self._recent_label)

        self._recent_list = QListWidget()
        self._recent_list.setMaximumWidth(500)
        self._recent_list.setMaximumHeight(140)
        self._recent_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._recent_list.setStyleSheet("font-size: 12px;")
        # Center the list
        recent_container = QWidget()
        rc_layout = QHBoxLayout(recent_container)
        rc_layout.setContentsMargins(0, 0, 0, 0)
        rc_layout.addStretch()
        rc_layout.addWidget(self._recent_list)
        rc_layout.addStretch()
        layout.addWidget(recent_container)

        layout.addStretch(3)

        ver = QLabel("v2.0")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet("font-size: 11px; padding-bottom: 16px;")
        ver.setProperty("subheading", True)
        layout.addWidget(ver)

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_recent()

    def _refresh_recent(self):
        from app.recent_files import get_all
        entries = get_all()
        self._recent_list.clear()
        if not entries:
            self._recent_label.hide()
            self._recent_list.hide()
            return
        self._recent_label.show()
        self._recent_list.show()
        for entry in entries[:8]:
            p = Path(entry["path"])
            item = QListWidgetItem(f"{entry['tool']}  —  {p.name}")
            item.setToolTip(str(p))
            item.setSizeHint(QSize(480, 26))
            self._recent_list.addItem(item)


class _HelpWidget(QWidget):
    """In-app Markdown-rendered README viewer."""

    # Map of sidebar tool names → README anchor fragments
    _TOOL_ANCHORS = {
        "Plunger (RDDS)": "1-plunger-rdds",
        "J-Coupling": "2-j-coupling",
        "Talmi Calculator": "3-talmi-calculator",
        "PACE4": "4-pace4",
        "Script Launcher": "5-script-launcher",
        "Accelerator": "6-accelerator",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        header = QLabel("Help — Documentation")
        header.setProperty("heading", True)
        layout.addWidget(header)

        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)
        layout.addWidget(self._browser, stretch=1)

        self._load_readme()

    def _load_readme(self):
        readme_path = Path(__file__).resolve().parent.parent / "README.md"
        if readme_path.exists():
            md = readme_path.read_text(encoding="utf-8")
            html = self._markdown_to_html(md)
            self._browser.setHtml(html)
        else:
            self._browser.setPlainText("README.md not found.")

    @staticmethod
    def _markdown_to_html(md: str) -> str:
        """Minimal Markdown → HTML conversion (no external deps)."""
        lines = md.split("\n")
        html_lines: list[str] = []
        in_code = False
        in_table = False
        in_list = False

        for line in lines:
            # Fenced code blocks
            if line.strip().startswith("```"):
                if in_code:
                    html_lines.append("</pre>")
                    in_code = False
                else:
                    html_lines.append(
                        "<pre style='background:#1a1a2e; color:#ccc; "
                        "padding:10px; font-size:12px; overflow-x:auto;'>"
                    )
                    in_code = True
                continue
            if in_code:
                html_lines.append(
                    line.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                continue

            stripped = line.strip()

            # Close table if we left it
            if in_table and not stripped.startswith("|"):
                html_lines.append("</table>")
                in_table = False

            # Close list if we left it
            if in_list and not stripped.startswith("- ") and not stripped.startswith("* "):
                html_lines.append("</ul>")
                in_list = False

            # Horizontal rule
            if stripped in ("---", "***", "___"):
                html_lines.append("<hr/>")
                continue

            # Headings
            if stripped.startswith("#"):
                level = len(stripped) - len(stripped.lstrip("#"))
                level = min(level, 6)
                text = stripped[level:].strip()
                # Generate anchor
                anchor = re.sub(r"[^\w\s-]", "", text.lower())
                anchor = re.sub(r"\s+", "-", anchor).strip("-")
                html_lines.append(
                    f"<h{level} id='{anchor}'>{_inline_format(text)}</h{level}>"
                )
                continue

            # Table rows
            if stripped.startswith("|"):
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                # Skip separator rows
                if all(set(c) <= set("-: ") for c in cells):
                    continue
                if not in_table:
                    html_lines.append(
                        "<table style='border-collapse:collapse; width:100%;'>"
                    )
                    in_table = True
                tag = "td"
                row = "".join(
                    f"<{tag} style='border:1px solid #444; padding:4px 8px;'>"
                    f"{_inline_format(c)}</{tag}>"
                    for c in cells
                )
                html_lines.append(f"<tr>{row}</tr>")
                continue

            # Unordered list
            if stripped.startswith("- ") or stripped.startswith("* "):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                html_lines.append(
                    f"<li>{_inline_format(stripped[2:])}</li>"
                )
                continue

            # Blockquote
            if stripped.startswith("> "):
                html_lines.append(
                    f"<blockquote style='border-left:3px solid #b060ff; "
                    f"padding-left:12px; margin:8px 0; color:#aaa;'>"
                    f"{_inline_format(stripped[2:])}</blockquote>"
                )
                continue

            # Blank line
            if not stripped:
                html_lines.append("<br/>")
                continue

            # Normal paragraph
            html_lines.append(f"<p>{_inline_format(stripped)}</p>")

        if in_table:
            html_lines.append("</table>")
        if in_list:
            html_lines.append("</ul>")

        return (
            "<html><body style='font-family: sans-serif; font-size: 13px; "
            "line-height: 1.5;'>"
            + "\n".join(html_lines)
            + "</body></html>"
        )

    def scroll_to_tool(self, tool_name: str):
        """Scroll the browser to the section for a given tool."""
        anchor = self._TOOL_ANCHORS.get(tool_name)
        if anchor:
            self._browser.scrollToAnchor(anchor)


class _HistoryWidget(QWidget):
    """Action-history panel — lists past calculations with one-click replay."""

    def __init__(self, main_window: "MainWindow", parent=None):
        super().__init__(parent)
        self._mw = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        header = QLabel("History — Recent Actions")
        header.setProperty("heading", True)
        layout.addWidget(header)

        sub = QLabel(
            "Click any entry to switch to that tool and restore its parameters."
        )
        sub.setProperty("subheading", True)
        sub.setWordWrap(True)
        layout.addWidget(sub)

        self._list = QListWidget()
        self._list.setAlternatingRowColors(True)
        self._list.itemDoubleClicked.connect(self._on_replay)
        layout.addWidget(self._list, stretch=1)

        btn_row = QHBoxLayout()
        replay_btn = QPushButton("Replay selected")
        replay_btn.clicked.connect(
            lambda: self._on_replay(self._list.currentItem())
        )
        clear_btn = QPushButton("Clear history")
        clear_btn.setProperty("secondary", True)
        clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(replay_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def refresh(self):
        from app.action_history import get_all
        import time as _time
        self._entries = get_all()
        self._list.clear()
        for entry in self._entries:
            ts = _time.strftime(
                "%Y-%m-%d %H:%M", _time.localtime(entry.get("timestamp", 0))
            )
            text = f"[{ts}]  {entry['tool']}  —  {entry['description']}"
            item = QListWidgetItem(text)
            item.setSizeHint(QSize(600, 30))
            self._list.addItem(item)

    def _on_replay(self, item):
        if item is None:
            return
        row = self._list.row(item)
        if row < 0 or row >= len(self._entries):
            return
        entry = self._entries[row]
        tool_name = entry.get("tool", "")
        params = entry.get("params", {})
        # Find the instrument in the sidebar and switch to it
        for i in range(self._mw.sidebar_list.count()):
            sidebar_item = self._mw.sidebar_list.item(i)
            if sidebar_item and sidebar_item.text().strip() == tool_name:
                self._mw.sidebar_list.setCurrentRow(i)
                # Try to restore parameters on the panel
                stack_idx = i + 1  # welcome is index 0
                scroll = self._mw.content_stack.widget(stack_idx)
                if scroll and hasattr(scroll, 'widget'):
                    panel = scroll.widget()
                    if hasattr(panel, 'restore_params'):
                        panel.restore_params(params)
                break

    def _on_clear(self):
        from app.action_history import clear
        clear()
        self.refresh()


def _inline_format(text: str) -> str:
    """Apply inline Markdown formatting: bold, italic, code, links."""
    # Code spans
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<a href='\2'>\1</a>", text)
    return text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GNA — Georgi's Nuclear Assistant  v2.0")
        self.setMinimumSize(1100, 750)
        self.resize(1280, 850)

        all_instruments = discover_instruments()
        # Sort by desired order
        order_map = {n: i for i, n in enumerate(_SIDEBAR_ORDER)}
        self.instruments = sorted(
            all_instruments,
            key=lambda inst: order_map.get(inst.name(), 999),
        )

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        sidebar = QWidget()
        sidebar.setFixedWidth(210)
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # App header (clickable → welcome)
        header = QWidget()
        header.setCursor(Qt.CursorShape.PointingHandCursor)
        header.mousePressEvent = lambda _: self._show_welcome()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 16, 16, 10)
        title = QLabel("GNA")
        title.setStyleSheet(
            "font-size: 26px; font-weight: 900; letter-spacing: 2px;"
        )
        title.setProperty("heading", True)
        subtitle = QLabel("Georgi's Nuclear Assistant")
        subtitle.setStyleSheet("font-size: 10px;")
        subtitle.setProperty("subheading", True)
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        sidebar_layout.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sidebar_layout.addWidget(sep)

        # Instrument list
        self.sidebar_list = QListWidget()
        self.sidebar_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        sidebar_layout.addWidget(self.sidebar_list)
        sidebar_layout.addStretch()

        # ── Theme switcher (color + animal combos + dark/light buttons) ──
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFixedHeight(1)
        sidebar_layout.addWidget(sep2)

        theme_widget = QWidget()
        theme_layout = QVBoxLayout(theme_widget)
        theme_layout.setContentsMargins(12, 6, 12, 4)
        theme_layout.setSpacing(3)

        # Color themes
        clbl = QLabel("COLOR THEMES")
        clbl.setStyleSheet("font-size: 9px; letter-spacing: 1px;")
        clbl.setProperty("subheading", True)
        theme_layout.addWidget(clbl)
        self._color_combo = QComboBox()
        for fam in THEME_FAMILIES:
            self._color_combo.addItem(fam)
        theme_layout.addWidget(self._color_combo)

        # Animal themes
        albl = QLabel("ANIMAL THEMES")
        albl.setStyleSheet("font-size: 9px; letter-spacing: 1px; padding-top: 4px;")
        albl.setProperty("subheading", True)
        theme_layout.addWidget(albl)
        self._animal_combo = QComboBox()
        self._animal_combo.addItem("—")  # "none" sentinel
        for fam in ANIMAL_FAMILIES:
            self._animal_combo.addItem(fam)
        theme_layout.addWidget(self._animal_combo)

        # Dark / Light toggle row
        variant_row = QHBoxLayout()
        variant_row.setSpacing(4)
        self._dark_btn = QPushButton("Dark")
        self._light_btn = QPushButton("Light")
        for btn in (self._dark_btn, self._light_btn):
            btn.setProperty("secondary", True)
            btn.setFixedHeight(26)
            btn.setStyleSheet(
                "font-size: 11px; font-weight: bold; padding: 2px 8px;"
                "text-align: center;"
            )
        self._dark_btn.clicked.connect(lambda: self._apply_variant(dark=True))
        self._light_btn.clicked.connect(lambda: self._apply_variant(dark=False))
        variant_row.addWidget(self._dark_btn)
        variant_row.addWidget(self._light_btn)
        theme_layout.addLayout(variant_row)
        sidebar_layout.addWidget(theme_widget)

        # Cross-link combos: selecting a color theme resets animal to "—" and vice-versa
        self._color_combo.currentTextChanged.connect(self._on_color_combo_changed)
        self._animal_combo.currentTextChanged.connect(self._on_animal_combo_changed)

        version = QLabel("v2.0")
        version.setStyleSheet("padding: 8px 16px; font-size: 10px;")
        version.setProperty("subheading", True)
        sidebar_layout.addWidget(version)

        # Constants button
        const_btn = QPushButton("  Constants")
        const_btn.setProperty("secondary", True)
        const_btn.setStyleSheet("text-align: left; padding: 8px 16px;")
        const_btn.setFixedHeight(36)
        const_btn.clicked.connect(self._show_constants)
        sidebar_layout.addWidget(const_btn)

        # History button
        history_btn = QPushButton("  History")
        history_btn.setProperty("secondary", True)
        history_btn.setStyleSheet("text-align: left; padding: 8px 16px;")
        history_btn.setFixedHeight(36)
        history_btn.clicked.connect(self._show_history)
        sidebar_layout.addWidget(history_btn)

        # Help button
        help_btn = QPushButton("  Help")
        help_btn.setProperty("secondary", True)
        help_btn.setStyleSheet("text-align: left; padding: 8px 16px;")
        help_btn.setFixedHeight(36)
        help_btn.clicked.connect(self._show_help)
        sidebar_layout.addWidget(help_btn)

        main_layout.addWidget(sidebar)

        # ── Content area ──
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # Index 0 = welcome page
        self._welcome = _WelcomeWidget()
        self.content_stack.addWidget(self._welcome)

        # Register instruments (starting at index 1)
        for inst in self.instruments:
            item = QListWidgetItem(f"  {inst.name()}")
            item.setToolTip(inst.description())
            item.setSizeHint(QSize(190, 42))
            self.sidebar_list.addItem(item)
            panel = inst.create_panel()
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setWidget(panel)
            self.content_stack.addWidget(scroll)

        # Constants page
        self._constants = ConstantsPanel()
        self._constants_index = self.content_stack.count()
        self.content_stack.addWidget(self._constants)

        # History page
        self._history_widget = _HistoryWidget(self)
        self._history_index = self.content_stack.count()
        self.content_stack.addWidget(self._history_widget)

        # Help page = last index in the stack
        self._help = _HelpWidget()
        self._help_index = self.content_stack.count()
        self.content_stack.addWidget(self._help)

        self.sidebar_list.currentRowChanged.connect(self._on_instrument_changed)
        # Start with no instrument selected — show welcome
        self.content_stack.setCurrentIndex(0)

        # Silhouette overlay (covers content area; mouse-transparent)
        self._overlay = SilhouetteOverlay(self.content_stack)
        self._overlay.resize(self.content_stack.size())
        self._overlay.raise_()

        # Track variant state and sync selector to saved theme
        self._is_dark = not active_theme().endswith(" Light")
        self._sync_theme_selector(active_theme())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_overlay'):
            self._overlay.resize(self.content_stack.size())

    # ── Theme helpers ──

    def _on_color_combo_changed(self, text):
        """User picked a colour family — reset animal combo and apply."""
        self._animal_combo.blockSignals(True)
        self._animal_combo.setCurrentIndex(0)  # "—"
        self._animal_combo.blockSignals(False)
        self._apply_variant(dark=self._is_dark)

    def _on_animal_combo_changed(self, text):
        """User picked an animal family — apply it."""
        if text == "—":
            # Switched back to no-animal — apply the colour theme
            self._apply_variant(dark=self._is_dark)
            return
        self._apply_variant(dark=self._is_dark)

    def _sync_theme_selector(self, theme_name: str):
        """Set the family combo + dark/light state to match *theme_name*."""
        if theme_name.endswith(" Light"):
            family = theme_name[: -len(" Light")]
            self._is_dark = False
        else:
            family = theme_name
            self._is_dark = True

        # Block both combos while syncing
        self._color_combo.blockSignals(True)
        self._animal_combo.blockSignals(True)

        # Is it an animal theme?
        if family in ANIMAL_FAMILIES:
            self._animal_combo.setCurrentText(family)
            self._color_combo.setCurrentIndex(0)
            self._overlay.set_animal(family)
        else:
            idx = self._color_combo.findText(family)
            if idx >= 0:
                self._color_combo.setCurrentIndex(idx)
            self._animal_combo.setCurrentIndex(0)  # "—"
            self._overlay.set_animal(None)

        self._color_combo.blockSignals(False)
        self._animal_combo.blockSignals(False)
        self._update_variant_buttons()

    def _apply_variant(self, dark: bool):
        """Apply the current family + dark/light variant."""
        self._is_dark = dark
        # Prefer animal combo if set, else colour combo
        animal = self._animal_combo.currentText()
        if animal and animal != "—":
            family = animal
            self._overlay.set_animal(animal)
        else:
            family = self._color_combo.currentText()
            self._overlay.set_animal(None)
        name = family if dark else f"{family} Light"
        if name in THEMES:
            app = QApplication.instance()
            if app:
                apply_theme(name, app)
        self._update_variant_buttons()

    def _update_variant_buttons(self):
        """Highlight the active variant button."""
        for btn, active in ((self._dark_btn, self._is_dark),
                            (self._light_btn, not self._is_dark)):
            if active:
                btn.setProperty("secondary", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            else:
                btn.setProperty("secondary", True)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    # ── Navigation ──

    def _on_instrument_changed(self, index):
        # index in sidebar maps to content_stack index + 1 (welcome is at 0)
        stack_index = index + 1
        if 0 < stack_index < self.content_stack.count():
            self.content_stack.setCurrentIndex(stack_index)

    def _show_welcome(self):
        """Return to the welcome screen."""
        self.sidebar_list.clearSelection()
        self.content_stack.setCurrentIndex(0)

    def _show_constants(self):
        """Open the Constants reference panel."""
        self.sidebar_list.clearSelection()
        self.content_stack.setCurrentIndex(self._constants_index)

    def _show_history(self):
        """Open the action-history panel."""
        self.sidebar_list.clearSelection()
        self._history_widget.refresh()
        self.content_stack.setCurrentIndex(self._history_index)

    def _show_help(self):
        """Open the Help page, optionally scrolled to the current tool."""
        self.sidebar_list.clearSelection()
        self.content_stack.setCurrentIndex(self._help_index)
        # Context-sensitive: scroll to current tool's section if one was active
        for i in range(self.sidebar_list.count()):
            item = self.sidebar_list.item(i)
            if item and item.isSelected():
                self._help.scroll_to_tool(item.text().strip())
                break
