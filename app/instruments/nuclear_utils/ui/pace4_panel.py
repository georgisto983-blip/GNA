"""PACE4 results panel — residue table + cross-section vs energy plot.

Supports any PACE4 HTML output file (with or without extension).
Primary view: sortable residue table (rank, nuclide, Z, N, A, σ, %).
Secondary view: σ vs E plot when multiple files are loaded.
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QAbstractItemView, QFileDialog, QGroupBox,
    QSplitter, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from app.theme import PLOT_STYLE
from app.instruments.nuclear_utils.pace4_parser import parse_pace4_html


_MARKERS = ["x", "+", "s", "^", "D", "o", "v", "P", "*", "h"]
_COLORS = [
    "#7aa2f7", "#9ece6a", "#e0af68", "#f7768e", "#bb9af7",
    "#73daca", "#ff9e64", "#b4f9f8", "#7dcfff", "#c3e88d",
]


class Pace4Panel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # per-file parsed results: path → result dict
        self._files: dict[str, dict] = {}   # path → parse result
        # aggregated for CS-vs-E plot: label → {energy: xsec}
        self._plot_data: dict[str, dict[float, float]] = {}
        self._init_ui()

    # ─────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────

    def _init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(10)

        # ── File management row ──
        file_group = QGroupBox("PACE4 Output Files")
        fg_layout = QVBoxLayout(file_group)

        btn_row = QHBoxLayout()
        for label, slot in [
            ("Add File(s)", self._add_files),
            ("Remove Selected", self._remove_selected),
            ("Clear All", self._clear_files),
        ]:
            btn = QPushButton(label)
            btn.setProperty("secondary", True)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        btn_row.addStretch()

        # File selector for table view
        self._file_selector = QComboBox()
        self._file_selector.setMinimumWidth(200)
        self._file_selector.setToolTip("Select file to display in table")
        self._file_selector.currentIndexChanged.connect(self._on_file_selected)
        btn_row.addWidget(QLabel("View:"))
        btn_row.addWidget(self._file_selector)
        fg_layout.addLayout(btn_row)

        self.file_list = QListWidget()
        self.file_list.setFixedHeight(75)
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setStyleSheet("font-size:11px;")
        fg_layout.addWidget(self.file_list)
        outer.addWidget(file_group)

        # ── Tabs: Residue Table | CS vs Energy ──
        self._tabs = QTabWidget()
        outer.addWidget(self._tabs, stretch=1)

        # ── Tab 1: Residue Table ──────────────────
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 8, 0, 0)
        table_layout.setSpacing(6)

        self._reaction_label = QLabel("Load a PACE4 output file to view residues")
        self._reaction_label.setProperty("subheading", True)
        table_layout.addWidget(self._reaction_label)

        self._residue_table = QTableWidget()
        self._residue_table.setColumnCount(7)
        self._residue_table.setHorizontalHeaderLabels(
            ["#", "Residue", "Z", "N", "A", "σ (mb)", "Yield (%)"]
        )
        self._residue_table.setAlternatingRowColors(True)
        self._residue_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._residue_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._residue_table.setSortingEnabled(True)
        hdr = self._residue_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in range(2, 7):
            hdr.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self._residue_table.setColumnWidth(0, 40)
        table_layout.addWidget(self._residue_table, stretch=1)

        self._tabs.addTab(table_widget, "Residue Table")

        # ── Tab 2: CS vs Energy Plot ──────────────
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setSpacing(4)

        # Residue channel selector
        channel_row = QHBoxLayout()
        channel_row.addWidget(QLabel("Channels:"))
        self._channel_list = QListWidget()
        self._channel_list.setFixedHeight(90)
        self._channel_list.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        self._channel_list.itemSelectionChanged.connect(self._redraw_plot)

        for lbl, slot in [("All", self._select_all), ("None", self._select_none)]:
            b = QPushButton(lbl)
            b.setProperty("secondary", True)
            b.setFixedWidth(60)
            b.clicked.connect(slot)
            channel_row.addWidget(b)
        channel_row.addStretch()
        plot_layout.addLayout(channel_row)
        plot_layout.addWidget(self._channel_list)

        with plt.style.context(PLOT_STYLE):
            self._fig, self._ax = plt.subplots(figsize=(7, 5))
        self._canvas = FigureCanvasQTAgg(self._fig)
        toolbar = NavigationToolbar2QT(self._canvas, plot_widget)
        plot_layout.addWidget(toolbar)
        plot_layout.addWidget(self._canvas, stretch=1)

        save_btn = QPushButton("Save Plot…")
        save_btn.setProperty("secondary", True)
        save_btn.clicked.connect(self._save_plot)
        plot_layout.addWidget(save_btn)

        self._tabs.addTab(plot_widget, "CS vs Energy")

        self._draw_empty_plot()

    # ─────────────────────────────────────────
    # File handling
    # ─────────────────────────────────────────

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PACE4 Output Files",
            str(Path.home()),
            "All Files (*);;HTML Files (*.html *.htm)",
        )
        if not paths:
            return

        errors = []
        new_paths = []
        for path in sorted(paths):
            if path in self._files:
                continue
            try:
                result = parse_pace4_html(path)
                if not result["residues"]:
                    raise ValueError("No residue data found — check file format")
                self._files[path] = result
                new_paths.append(path)

                energy = result["energy_MeV"]
                name = Path(path).name
                self.file_list.addItem(f"E={energy:.0f} MeV  —  {name}")

                # Accumulate for CS-vs-E plot
                for res in result["residues"]:
                    lbl = res["label"]
                    self._plot_data.setdefault(lbl, {})[energy] = res["xsec_mb"]

            except Exception as exc:
                errors.append(f"{Path(path).name}: {exc}")

        if errors:
            QMessageBox.warning(self, "Parse errors", "\n".join(errors))

        # Update file selector combo
        self._file_selector.blockSignals(True)
        for path in new_paths:
            name = Path(path).name
            self._file_selector.addItem(name, path)
        self._file_selector.blockSignals(False)

        if new_paths:
            self._file_selector.setCurrentIndex(self._file_selector.count() - 1)
            self._on_file_selected(self._file_selector.currentIndex())

        self._refresh_channel_list()
        self._redraw_plot()

    def _remove_selected(self):
        selected = self.file_list.selectedItems()
        if not selected:
            return
        # Rebuild from scratch (simplest approach)
        selected_rows = sorted(
            {self.file_list.row(item) for item in selected}, reverse=True
        )
        paths = list(self._files.keys())
        for row in selected_rows:
            if row < len(paths):
                path = paths[row]
                del self._files[path]
                self.file_list.takeItem(row)

        # Rebuild plot data
        self._rebuild_plot_data()

        # Rebuild file selector
        self._file_selector.blockSignals(True)
        self._file_selector.clear()
        for path in self._files:
            self._file_selector.addItem(Path(path).name, path)
        self._file_selector.blockSignals(False)

        if self._files:
            self._on_file_selected(0)
        else:
            self._reaction_label.setText("Load a PACE4 output file to view residues")
            self._residue_table.setRowCount(0)

        self._refresh_channel_list()
        self._redraw_plot()

    def _clear_files(self):
        self._files.clear()
        self._plot_data.clear()
        self.file_list.clear()
        self._file_selector.clear()
        self._channel_list.clear()
        self._reaction_label.setText("Load a PACE4 output file to view residues")
        self._residue_table.setRowCount(0)
        self._draw_empty_plot()

    def _rebuild_plot_data(self):
        self._plot_data.clear()
        for result in self._files.values():
            energy = result["energy_MeV"]
            for res in result["residues"]:
                lbl = res["label"]
                self._plot_data.setdefault(lbl, {})[energy] = res["xsec_mb"]

    # ─────────────────────────────────────────
    # Residue Table
    # ─────────────────────────────────────────

    def _on_file_selected(self, index: int):
        if index < 0 or index >= self._file_selector.count():
            return
        path = self._file_selector.itemData(index)
        if path not in self._files:
            return
        result = self._files[path]
        self._populate_table(result)

    def _populate_table(self, result: dict):
        residues = result["residues"]
        energy = result["energy_MeV"]

        # Build label
        proj = result.get("projectile", "")
        targ = result.get("target", "")
        comp = result.get("compound", "")
        if proj and targ:
            rx = f"{proj} + {targ}"
        else:
            rx = "PACE4"
        self._reaction_label.setText(
            f"{rx}  →  {comp}  |  E = {energy:.0f} MeV  |  {len(residues)} residues"
        )

        self._residue_table.setSortingEnabled(False)
        self._residue_table.setRowCount(len(residues))

        # Sort residues by cross-section descending for display
        sorted_res = sorted(residues, key=lambda r: r["xsec_mb"], reverse=True)
        total_xsec = sum(r["xsec_mb"] for r in sorted_res)

        for row, res in enumerate(sorted_res):
            frac = (res["xsec_mb"] / total_xsec * 100) if total_xsec > 0 else 0.0

            items = [
                self._mkitem(str(row + 1), Qt.AlignmentFlag.AlignCenter),
                self._mkitem(res["label"], Qt.AlignmentFlag.AlignCenter),
                self._mkitem(str(res["Z"]), Qt.AlignmentFlag.AlignCenter),
                self._mkitem(str(res["N"]), Qt.AlignmentFlag.AlignCenter),
                self._mkitem(str(res["A"]), Qt.AlignmentFlag.AlignCenter),
                self._mkitem_float(res["xsec_mb"]),
                self._mkitem_float(frac, fmt=".1f"),
            ]
            for col, item in enumerate(items):
                self._residue_table.setItem(row, col, item)

        self._residue_table.setSortingEnabled(True)
        self._residue_table.resizeRowsToContents()

    @staticmethod
    def _mkitem(text: str, align=Qt.AlignmentFlag.AlignLeft) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
        return item

    @staticmethod
    def _mkitem_float(val: float, fmt: str = ".2f") -> QTableWidgetItem:
        item = QTableWidgetItem(f"{val:{fmt}}")
        item.setTextAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        item.setData(Qt.ItemDataRole.UserRole, val)  # for numeric sort
        return item

    # ─────────────────────────────────────────
    # Channel selector (CS vs E tab)
    # ─────────────────────────────────────────

    def _refresh_channel_list(self):
        current_sel = {
            self._channel_list.item(i).text()
            for i in range(self._channel_list.count())
            if self._channel_list.item(i).isSelected()
        }
        self._channel_list.blockSignals(True)
        self._channel_list.clear()
        sorted_labels = sorted(
            self._plot_data,
            key=lambda lbl: max(self._plot_data[lbl].values()),
            reverse=True,
        )
        for label in sorted_labels:
            from PyQt6.QtWidgets import QListWidgetItem
            item = QListWidgetItem(label)
            self._channel_list.addItem(item)
            if label in current_sel or (
                not current_sel and self._channel_list.count() <= 8
            ):
                item.setSelected(True)
        self._channel_list.blockSignals(False)

    def _select_all(self):
        self._channel_list.selectAll()

    def _select_none(self):
        self._channel_list.clearSelection()

    # ─────────────────────────────────────────
    # Plotting
    # ─────────────────────────────────────────

    def _draw_empty_plot(self):
        with plt.style.context(PLOT_STYLE):
            self._ax.cla()
            self._ax.set_xlabel("E (MeV)")
            self._ax.set_ylabel("σ (mb)")
            self._ax.set_yscale("log")
            self._ax.set_title("PACE4 Reaction Cross Sections")
            self._ax.text(
                0.5, 0.5,
                "Load multiple PACE4 files (one per energy)\nto plot cross sections vs beam energy",
                transform=self._ax.transAxes,
                ha="center", va="center",
                color=PLOT_STYLE.get("text.color", "#c0caf5"),
                fontsize=11, alpha=0.6,
            )
            self._ax.grid(True, which="both", alpha=0.3)
        self._canvas.draw()

    def _redraw_plot(self):
        if not self._plot_data:
            self._draw_empty_plot()
            return

        selected = [
            self._channel_list.item(i).text()
            for i in range(self._channel_list.count())
            if self._channel_list.item(i).isSelected()
        ]
        if not selected:
            self._draw_empty_plot()
            return

        with plt.style.context(PLOT_STYLE):
            self._ax.cla()
            for idx, label in enumerate(selected):
                pts = self._plot_data[label]
                energies = sorted(pts.keys())
                xsecs = [pts[e] for e in energies]
                color = _COLORS[idx % len(_COLORS)]
                marker = _MARKERS[idx % len(_MARKERS)]
                if len(energies) > 1:
                    self._ax.semilogy(
                        energies, xsecs,
                        marker=marker, color=color,
                        linewidth=1.4, markersize=7,
                        label=label,
                    )
                else:
                    self._ax.semilogy(
                        energies, xsecs,
                        marker=marker, color=color,
                        linestyle="none", markersize=9,
                        label=label,
                    )

            self._ax.set_title("PACE4 — Evaporation Residue Cross Sections")
            self._ax.set_xlabel("$E_{\\mathrm{beam}}$ (MeV)")
            self._ax.set_ylabel("$\\sigma$ (mb)")
            self._ax.set_yscale("log")
            self._ax.grid(True, which="both", alpha=0.3)
            self._ax.legend(
                loc="best", fontsize=9, framealpha=0.7,
                ncol=2 if len(selected) > 8 else 1,
            )
            self._fig.tight_layout()

        self._canvas.draw()

    def _save_plot(self):
        if not self._plot_data:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Plot", "pace4_plot.png",
            "PNG (*.png);;PDF (*.pdf);;SVG (*.svg)"
        )
        if path:
            self._fig.savefig(path, dpi=150, bbox_inches="tight")
