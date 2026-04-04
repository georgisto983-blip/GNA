"""Silhouette overlay — paints faint animal shapes + floating symbols.

Usage:
    overlay = SilhouetteOverlay(parent_widget)
    overlay.set_animal('Cat')  # or None to disable
    overlay.raise_()           # ensure on top of siblings
"""

import random
from pathlib import Path

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QWidget


class SilhouetteOverlay(QWidget):
    """Transparent overlay that renders animal watermarks + floating symbols."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self._renderer: QSvgRenderer | None = None
        self._symbols: list[str] = []
        self._animal: str | None = None
        self._opacity = 0.06          # silhouette opacity
        self._symbol_opacity = 0.10   # floating symbol opacity
        self._seed = 42               # deterministic scatter

        # Cache scatter positions (recalculated on resize)
        self._silhouette_rects: list[QRectF] = []
        self._symbol_positions: list[tuple[QPointF, str, int]] = []

    # ── Public API ──

    def set_animal(self, name: str | None):
        """Switch to *name* animal theme, or None to disable."""
        if name == self._animal:
            return
        self._animal = name
        if name is None:
            self._renderer = None
            self._symbols = []
            self.hide()
            return

        from app.animal_themes import ANIMAL_THEMES
        data = ANIMAL_THEMES.get(name)
        if data is None:
            self._renderer = None
            self._symbols = []
            self.hide()
            return

        svg_path = data['svg']
        if Path(svg_path).exists():
            self._renderer = QSvgRenderer(svg_path)
        else:
            self._renderer = None

        self._symbols = data.get('symbols', [])
        self._recalc_positions()
        self.show()
        self.update()

    # ── Layout ──

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._recalc_positions()

    def _recalc_positions(self):
        """Pre-compute deterministic scatter positions for current size."""
        w, h = self.width(), self.height()
        if w < 10 or h < 10:
            return

        rng = random.Random(self._seed)

        # Place 2-4 silhouettes depending on available area
        self._silhouette_rects = []
        if self._renderer:
            sil_size = min(w, h) * 0.35
            sil_size = max(sil_size, 60)
            count = max(2, min(4, (w * h) // 200_000))
            for _ in range(count):
                x = rng.uniform(0.05 * w, 0.85 * w - sil_size * 0.5)
                y = rng.uniform(0.05 * h, 0.85 * h - sil_size * 0.5)
                self._silhouette_rects.append(
                    QRectF(x, y, sil_size, sil_size)
                )

        # Scatter 8-16 small symbols across the area
        self._symbol_positions = []
        if self._symbols:
            sym_count = max(8, min(16, (w * h) // 60_000))
            for _ in range(sym_count):
                x = rng.uniform(0.02 * w, 0.95 * w)
                y = rng.uniform(0.04 * h, 0.95 * h)
                sym = rng.choice(self._symbols)
                size = rng.randint(14, 26)
                self._symbol_positions.append((QPointF(x, y), sym, size))

    # ── Painting ──

    def paintEvent(self, event):
        if self._animal is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw silhouettes
        if self._renderer:
            painter.setOpacity(self._opacity)
            for rect in self._silhouette_rects:
                self._renderer.render(painter, rect)

        # Draw floating symbols
        if self._symbol_positions:
            painter.setOpacity(self._symbol_opacity)
            for pos, sym, size in self._symbol_positions:
                font = QFont()
                font.setPixelSize(size)
                painter.setFont(font)
                painter.drawText(pos, sym)

        painter.end()
