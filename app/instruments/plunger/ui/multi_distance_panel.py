"""Multiple-distance RDDS half-life calculation panel with linear fit plot."""

import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QHeaderView,
)
from uncertainties import ufloat, UFloat

from app.widgets import format_halflife
from app.instruments.plunger import calculator
from app.instruments.plunger.plotter import create_canvas, plot_rdds_fit


class MultiDistancePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._result_text = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 12, 8, 12)

        # ── Beta input ──
        beta_group = QGroupBox("Beam Parameters")
        beta_layout = QHBoxLayout(beta_group)
        beta_layout.addWidget(QLabel("\u03b2 (v/c):"))

        self.beta_value = QLineEdit()
        self.beta_value.setPlaceholderText("value")
        self.beta_value.setFixedWidth(130)
        beta_layout.addWidget(self.beta_value)

        beta_layout.addWidget(QLabel("\u00b1"))

        self.beta_unc = QLineEdit()
        self.beta_unc.setPlaceholderText("uncertainty")
        self.beta_unc.setFixedWidth(130)
        beta_layout.addWidget(self.beta_unc)
        beta_layout.addStretch()
        layout.addWidget(beta_group)

        # ── Measurement table ──
        table_group = QGroupBox("Distance Measurements")
        table_layout = QVBoxLayout(table_group)

        self.table = QTableWidget(3, 6)
        self.table.setHorizontalHeaderLabels([
            "d (\u00b5m)", "\u03c3_d",
            "I_shifted", "\u03c3_shifted",
            "I_unshifted", "\u03c3_unshifted",
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setMinimumHeight(180)
        table_layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        for text, slot in [
            ("Add Row", self._add_row),
            ("Remove Row", self._remove_row),
            ("Load JSON", self._load_json),
            ("Clear", self._clear_table),
        ]:
            btn = QPushButton(text)
            btn.setProperty("secondary", True)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        table_layout.addLayout(btn_row)
        layout.addWidget(table_group, stretch=1)

        # ── Calculate button ──
        calc_btn = QPushButton("Calculate && Fit")
        calc_btn.setFixedHeight(42)
        calc_btn.clicked.connect(self._calculate)
        layout.addWidget(calc_btn)

        # ── Results area (plot + text) ──
        results_layout = QHBoxLayout()

        self.figure, self.canvas = create_canvas()
        results_layout.addWidget(self.canvas, stretch=2)

        result_panel = QVBoxLayout()
        self.result_label = QLabel("Result will appear here")
        self.result_label.setProperty("result", True)
        self.result_label.setWordWrap(True)
        result_panel.addWidget(self.result_label)

        save_btn = QPushButton("Save Result")
        save_btn.setProperty("secondary", True)
        save_btn.clicked.connect(self._save_result)
        result_panel.addWidget(save_btn)
        result_panel.addStretch()
        results_layout.addLayout(result_panel, stretch=1)

        layout.addLayout(results_layout, stretch=2)

    # ── Table helpers ──

    def _add_row(self):
        self.table.insertRow(self.table.rowCount())

    def _remove_row(self):
        if self.table.rowCount() > 1:
            self.table.removeRow(self.table.rowCount() - 1)

    def _clear_table(self):
        self.table.setRowCount(3)
        for r in range(3):
            for c in range(6):
                self.table.setItem(r, c, QTableWidgetItem(""))
        self.beta_value.clear()
        self.beta_unc.clear()
        self.result_label.setText("Result will appear here")
        self._result_text = ""

    def _cell_float(self, row, col):
        """Read a float from a table cell; return 0.0 if empty."""
        item = self.table.item(row, col)
        if item and item.text().strip():
            return float(item.text())
        return 0.0

    # ── Calculation ──

    def _calculate(self):
        try:
            beta_val = float(self.beta_value.text())
            beta_unc_text = self.beta_unc.text().strip()
            beta_unc = float(beta_unc_text) if beta_unc_text else 0.0
            beta = ufloat(beta_val, beta_unc)

            distances = []
            areas_shifted = []
            areas_unshifted = []

            for row in range(self.table.rowCount()):
                d_val = self._cell_float(row, 0)
                if d_val == 0:
                    continue  # skip empty rows
                d_err = self._cell_float(row, 1)
                s_val = self._cell_float(row, 2)
                s_err = self._cell_float(row, 3)
                u_val = self._cell_float(row, 4)
                u_err = self._cell_float(row, 5)

                distances.append(ufloat(d_val, d_err))
                areas_shifted.append(ufloat(s_val, s_err))
                areas_unshifted.append(ufloat(u_val, u_err))

            if len(distances) < 2:
                QMessageBox.warning(
                    self, "Insufficient Data",
                    "At least 2 data points are required for a linear fit.",
                )
                return

            t_half, odr_out, x, x_err, y, y_err = calculator.halflife_multi(
                distances, areas_shifted, areas_unshifted, beta
            )

            self._result_text = format_halflife(t_half)
            self.result_label.setText(self._result_text)

            # Format label for the plot annotation
            t_ps = t_half * 1e12
            if isinstance(t_ps, UFloat):
                t_label = f"= {t_ps:.2u} ps".replace("+/-", " \u00b1 ")
            else:
                t_label = f"= {t_ps:.2f} ps"

            plot_rdds_fit(self.figure, x, x_err, y, y_err, odr_out, t_label)
            self.canvas.draw()

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(
                self, "Calculation Error", f"An error occurred:\n{e}"
            )

    # ── JSON loading ──

    def _load_json(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Input Data", "", "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            with open(path) as f:
                data = json.load(f)

            # Beta
            beta_raw = data.get("beta", [])
            if isinstance(beta_raw, list) and len(beta_raw) >= 1:
                self.beta_value.setText(str(beta_raw[0]))
                if len(beta_raw) > 1:
                    self.beta_unc.setText(str(beta_raw[1]))

            # Measurements
            dists = data.get("plunger_distance", [])
            shifted = data.get("area_shifted", [])
            unshifted = data.get("area_unshifted", [])

            n = len(dists)
            self.table.setRowCount(n)

            for i in range(n):
                row_vals = []
                for arr in (dists, shifted, unshifted):
                    if isinstance(arr[i], list):
                        row_vals.append(str(arr[i][0]))
                        row_vals.append(str(arr[i][1]) if len(arr[i]) > 1 else "")
                    else:
                        row_vals.append(str(arr[i]))
                        row_vals.append("")
                for c, val in enumerate(row_vals):
                    self.table.setItem(i, c, QTableWidgetItem(val))

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load file:\n{e}")

    # ── Save ──

    def _save_result(self):
        if not self._result_text:
            QMessageBox.information(self, "Info", "No result to save yet.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Result", "rdds_multi_result.txt", "Text Files (*.txt)"
        )
        if not path:
            return

        # Text report
        with open(path, "w") as f:
            f.write("GNA \u2014 RDDS Half-Life (Multiple Distances)\n")
            f.write("=" * 55 + "\n\n")
            f.write(
                f"Beta (v/c):  {self.beta_value.text()} "
                f"\u00b1 {self.beta_unc.text()}\n\n"
            )
            headers = [
                "d(\u00b5m)", "\u03c3_d", "I_s", "\u03c3_s", "I_u", "\u03c3_u"
            ]
            f.write("\t".join(headers) + "\n")
            for r in range(self.table.rowCount()):
                row = []
                for c in range(6):
                    item = self.table.item(r, c)
                    row.append(item.text() if item else "")
                f.write("\t".join(row) + "\n")
            f.write("\n" + "=" * 55 + "\n")
            f.write(f"{self._result_text}\n")

        # Plot image
        plot_path = path.rsplit(".", 1)[0] + "_plot.png"
        self.figure.savefig(
            plot_path, dpi=150, bbox_inches="tight",
            facecolor=self.figure.get_facecolor(),
        )

        QMessageBox.information(
            self, "Saved",
            f"Result saved to:\n{path}\n\nPlot saved to:\n{plot_path}",
        )
