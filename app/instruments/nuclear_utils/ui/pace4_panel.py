"""PACE4 results panel — multi-file cross-section analysis with gnuplot.

Workflow:
  1. Load multiple PACE4 HTML output files (one per beam energy)
  2. Parse each for residue cross-sections
  3. Rank nuclei by total σ (sum across energies)
  4. User selects channels via checklist
  5. Plot σ(E) with gnuplot in publication style
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QAbstractItemView, QFileDialog, QGroupBox,
    QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QListWidgetItem, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from app.instruments.nuclear_utils.pace4_parser import parse_pace4_html
from app.result_window import ResultWindow
from app import gnuplot


class Pace4Panel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._files: dict[str, dict] = {}
        self._plot_data: dict[str, dict[float, float]] = {}
        self._ranked_labels: list[str] = []
        self._last_plot_path: str | None = None
        self._init_ui()

    # ─────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────

    def _init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(10)

        # ── File management ──
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

        # ── Tabs ──
        self._tabs = QTabWidget()
        outer.addWidget(self._tabs, stretch=1)

        # ── Tab 1: Residue Table ──
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

        table_btn_row = QHBoxLayout()
        table_btn_row.addStretch()
        show_table_btn = QPushButton("Show Table in Window")
        show_table_btn.setProperty("secondary", True)
        show_table_btn.clicked.connect(self._show_table_window)
        table_btn_row.addWidget(show_table_btn)
        table_layout.addLayout(table_btn_row)

        self._tabs.addTab(table_widget, "Residue Table")

        # ── Tab 2: CS vs Energy (gnuplot) ──
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        plot_layout.setContentsMargins(0, 4, 0, 0)
        plot_layout.setSpacing(6)

        channel_group = QGroupBox("Residue Channels (ranked by total σ)")
        ch_layout = QVBoxLayout(channel_group)

        ch_btn_row = QHBoxLayout()
        for lbl, slot in [("All", self._select_all), ("None", self._select_none)]:
            b = QPushButton(lbl)
            b.setProperty("secondary", True)
            b.setFixedWidth(60)
            b.clicked.connect(slot)
            ch_btn_row.addWidget(b)
        ch_btn_row.addStretch()

        plot_btn = QPushButton("Plot with gnuplot")
        plot_btn.clicked.connect(self._do_gnuplot)
        ch_btn_row.addWidget(plot_btn)
        ch_layout.addLayout(ch_btn_row)

        self._channel_list = QListWidget()
        self._channel_list.setFixedHeight(120)
        self._channel_list.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        ch_layout.addWidget(self._channel_list)
        plot_layout.addWidget(channel_group)

        self._plot_scroll = QScrollArea()
        self._plot_scroll.setWidgetResizable(True)
        self._plot_label = QLabel("Load files and click 'Plot with gnuplot'")
        self._plot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._plot_scroll.setWidget(self._plot_label)
        plot_layout.addWidget(self._plot_scroll, stretch=1)

        save_row = QHBoxLayout()
        save_row.addStretch()
        for text, slot in [
            ("Save Plot…", self._save_plot),
            ("Show in Window", self._show_plot_window),
        ]:
            btn = QPushButton(text)
            btn.setProperty("secondary", True)
            btn.clicked.connect(slot)
            save_row.addWidget(btn)
        plot_layout.addLayout(save_row)

        self._tabs.addTab(plot_widget, "CS vs Energy")

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
                    raise ValueError("No residue data found")
                self._files[path] = result
                new_paths.append(path)

                energy = result["energy_MeV"]
                name = Path(path).name
                self.file_list.addItem(f"E={energy:.0f} MeV  —  {name}")

                for res in result["residues"]:
                    lbl = res["label"]
                    self._plot_data.setdefault(lbl, {})[energy] = res["xsec_mb"]

            except Exception as exc:
                errors.append(f"{Path(path).name}: {exc}")

        if errors:
            QMessageBox.warning(self, "Parse errors", "\n".join(errors))

        self._file_selector.blockSignals(True)
        for path in new_paths:
            self._file_selector.addItem(Path(path).name, path)
        self._file_selector.blockSignals(False)

        if new_paths:
            self._file_selector.setCurrentIndex(self._file_selector.count() - 1)
            self._on_file_selected(self._file_selector.currentIndex())

        self._rank_channels()
        self._refresh_channel_list()

    def _remove_selected(self):
        selected = self.file_list.selectedItems()
        if not selected:
            return
        selected_rows = sorted(
            {self.file_list.row(item) for item in selected}, reverse=True
        )
        paths = list(self._files.keys())
        for row in selected_rows:
            if row < len(paths):
                del self._files[paths[row]]
                self.file_list.takeItem(row)

        self._rebuild_plot_data()

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

    def _clear_files(self):
        self._files.clear()
        self._plot_data.clear()
        self._ranked_labels.clear()
        self.file_list.clear()
        self._file_selector.clear()
        self._channel_list.clear()
        self._reaction_label.setText("Load a PACE4 output file to view residues")
        self._residue_table.setRowCount(0)
        self._plot_label.setPixmap(QPixmap())
        self._plot_label.setText("Load files and click 'Plot with gnuplot'")
        self._last_plot_path = None

    def _rebuild_plot_data(self):
        self._plot_data.clear()
        for result in self._files.values():
            energy = result["energy_MeV"]
            for res in result["residues"]:
                self._plot_data.setdefault(res["label"], {})[energy] = res["xsec_mb"]
        self._rank_channels()

    # ─────────────────────────────────────────
    # Ranking
    # ─────────────────────────────────────────

    def _rank_channels(self):
        totals = {lbl: sum(pts.values()) for lbl, pts in self._plot_data.items()}
        self._ranked_labels = sorted(totals, key=totals.get, reverse=True)

    def _refresh_channel_list(self):
        current_sel = {
            self._channel_list.item(i).text()
            for i in range(self._channel_list.count())
            if self._channel_list.item(i).isSelected()
        }
        self._channel_list.blockSignals(True)
        self._channel_list.clear()

        for label in self._ranked_labels:
            total = sum(self._plot_data[label].values())
            item = QListWidgetItem(label)
            item.setToolTip(f"Total σ = {total:.1f} mb")
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
    # Residue Table
    # ─────────────────────────────────────────

    def _on_file_selected(self, index: int):
        if index < 0 or index >= self._file_selector.count():
            return
        path = self._file_selector.itemData(index)
        if path not in self._files:
            return
        self._populate_table(self._files[path])

    def _populate_table(self, result: dict):
        residues = result["residues"]
        energy = result["energy_MeV"]

        proj = result.get("projectile", "")
        targ = result.get("target", "")
        comp = result.get("compound", "")
        rx = f"{proj} + {targ}" if proj and targ else "PACE4"
        self._reaction_label.setText(
            f"{rx}  →  {comp}  |  E = {energy:.0f} MeV  |  {len(residues)} residues"
        )

        self._residue_table.setSortingEnabled(False)
        self._residue_table.setRowCount(len(residues))

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
        item.setData(Qt.ItemDataRole.UserRole, val)
        return item

    # ─────────────────────────────────────────
    # Gnuplot plotting
    # ─────────────────────────────────────────

    def _get_selected_channels(self) -> dict[str, dict[float, float]]:
        selected = {}
        for i in range(self._channel_list.count()):
            item = self._channel_list.item(i)
            if item.isSelected():
                label = item.text()
                if label in self._plot_data:
                    selected[label] = self._plot_data[label]
        return selected

    def _get_reaction_label(self) -> str:
        for result in self._files.values():
            proj = result.get("projectile", "")
            targ = result.get("target", "")
            if proj and targ:
                return (
                    f"^{{{_mass_num(proj)}}}{_symbol(proj)} + "
                    f"^{{{_mass_num(targ)}}}{_symbol(targ)}"
                )
        return "PACE4 Reaction Cross Sections"

    def _do_gnuplot(self):
        channels = self._get_selected_channels()
        if not channels:
            QMessageBox.information(self, "Info", "Select at least one channel.")
            return
        try:
            reaction = self._get_reaction_label()
            path, pixmap = gnuplot.plot_pace4(channels, reaction)
            self._last_plot_path = path
            self._plot_label.setPixmap(pixmap)
            self._plot_label.setText("")
        except Exception as e:
            QMessageBox.critical(self, "Gnuplot Error", str(e))

    def _save_plot(self):
        if not self._last_plot_path:
            QMessageBox.information(self, "Info", "No plot to save.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Plot", "pace4_plot.pdf",
            "PDF (*.pdf);;PNG (*.png);;SVG (*.svg)"
        )
        if not path:
            return
        if path.endswith(".pdf"):
            from app.pdf_export import save_plot_pdf
            reaction = self._get_reaction_label().replace("^{", "").replace("}", "")
            save_plot_pdf(path, self._last_plot_path, f"PACE4 — {reaction}")
        else:
            channels = self._get_selected_channels()
            if channels:
                gnuplot.plot_pace4(channels, self._get_reaction_label(), output=path)
        QMessageBox.information(self, "Saved", f"Plot saved to:\n{path}")

    # ─────────────────────────────────────────
    # Result windows
    # ─────────────────────────────────────────

    def _show_table_window(self):
        if self._residue_table.rowCount() == 0:
            QMessageBox.information(self, "Info", "No table data to show.")
            return

        headers = [
            self._residue_table.horizontalHeaderItem(c).text()
            for c in range(self._residue_table.columnCount())
        ]
        rows = []
        for r in range(self._residue_table.rowCount()):
            rows.append([
                (self._residue_table.item(r, c).text()
                 if self._residue_table.item(r, c) else "")
                for c in range(self._residue_table.columnCount())
            ])

        win = ResultWindow("PACE4 — Residue Table", parent=self)
        win.set_subtitle(self._reaction_label.text())
        win.set_table(headers, rows, numeric_cols=[2, 3, 4, 5, 6])
        win.show()
        self._result_window_table = win

    def _show_plot_window(self):
        if not self._last_plot_path:
            QMessageBox.information(self, "Info", "No plot to show.")
            return
        win = ResultWindow("PACE4 — Cross Sections vs Energy", parent=self)
        win.set_plot(self._last_plot_path)
        win.show()
        self._result_window_plot = win


def _mass_num(nuclide: str) -> str:
    i = 0
    while i < len(nuclide) and nuclide[i].isdigit():
        i += 1
    return nuclide[:i] if i > 0 else ""


def _symbol(nuclide: str) -> str:
    i = 0
    while i < len(nuclide) and nuclide[i].isdigit():
        i += 1
    return nuclide[i:]
