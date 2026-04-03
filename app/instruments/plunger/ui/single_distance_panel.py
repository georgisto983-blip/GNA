"""Single-distance RDDS half-life calculation panel."""

import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QFileDialog, QMessageBox,
)
from app.widgets import ValueUncertaintyInput, format_halflife
from app.instruments.plunger import calculator


class SingleDistancePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._result_text = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 12, 8, 12)

        # ── Input fields ──
        input_group = QGroupBox("Input Data")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)

        self.distance_input = ValueUncertaintyInput("Plunger distance:", "\u00b5m")
        self.beta_input = ValueUncertaintyInput("\u03b2  (v/c):")
        self.shifted_input = ValueUncertaintyInput("Shifted peak area (I\u209b):")
        self.unshifted_input = ValueUncertaintyInput("Unshifted peak area (I\u1d64):")

        for w in (self.distance_input, self.beta_input,
                  self.shifted_input, self.unshifted_input):
            input_layout.addWidget(w)

        btn_row = QHBoxLayout()
        load_btn = QPushButton("Load JSON")
        load_btn.setProperty("secondary", True)
        load_btn.clicked.connect(self._load_json)
        btn_row.addWidget(load_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setProperty("secondary", True)
        clear_btn.clicked.connect(self._clear)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        input_layout.addLayout(btn_row)

        layout.addWidget(input_group)

        # ── Calculate button ──
        calc_btn = QPushButton("Calculate Half-Life")
        calc_btn.setFixedHeight(42)
        calc_btn.clicked.connect(self._calculate)
        layout.addWidget(calc_btn)

        # ── Result ──
        result_group = QGroupBox("Result")
        result_layout = QVBoxLayout(result_group)

        self.result_label = QLabel("Enter data and click Calculate")
        self.result_label.setProperty("result", True)
        result_layout.addWidget(self.result_label)

        save_btn = QPushButton("Save Result")
        save_btn.setProperty("secondary", True)
        save_btn.clicked.connect(self._save_result)
        result_layout.addWidget(save_btn)

        layout.addWidget(result_group)
        layout.addStretch()

    # ── Actions ──

    def _calculate(self):
        try:
            distance = self.distance_input.get_value()
            beta = self.beta_input.get_value()
            area_s = self.shifted_input.get_value()
            area_u = self.unshifted_input.get_value()

            t_half = calculator.halflife_single(distance, beta, area_s, area_u)
            self._result_text = format_halflife(t_half)
            self.result_label.setText(self._result_text)

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(
                self, "Calculation Error", f"An error occurred:\n{e}"
            )

    def _load_json(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Input Data", "", "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            with open(path) as f:
                data = json.load(f)
            self._populate_field(self.distance_input, data.get("plunger_distance"))
            self._populate_field(self.beta_input, data.get("beta"))
            self._populate_field(self.shifted_input, data.get("area_shifted"))
            self._populate_field(self.unshifted_input, data.get("area_unshifted"))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load file:\n{e}")

    @staticmethod
    def _populate_field(widget, raw):
        """Parse old format ('value uncertainty' string) or [val, unc] list."""
        if raw is None:
            return
        if isinstance(raw, str):
            parts = raw.split()
            widget.set_value(parts[0], parts[1] if len(parts) > 1 else None)
        elif isinstance(raw, list):
            widget.set_value(raw[0], raw[1] if len(raw) > 1 else None)
        else:
            widget.set_value(raw)

    def _clear(self):
        for w in (self.distance_input, self.beta_input,
                  self.shifted_input, self.unshifted_input):
            w.clear()
        self.result_label.setText("Enter data and click Calculate")
        self._result_text = ""

    def _save_result(self):
        if not self._result_text:
            QMessageBox.information(self, "Info", "No result to save yet.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Result", "rdds_single_result.txt", "Text Files (*.txt)"
        )
        if not path:
            return
        with open(path, "w") as f:
            f.write("GNA \u2014 RDDS Half-Life (Single Distance)\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Plunger distance:  {self.distance_input.get_text()} \u00b5m\n")
            f.write(f"Beta (v/c):        {self.beta_input.get_text()}\n")
            f.write(f"Shifted area:      {self.shifted_input.get_text()}\n")
            f.write(f"Unshifted area:    {self.unshifted_input.get_text()}\n\n")
            f.write("=" * 50 + "\n")
            f.write(f"{self._result_text}\n")
        QMessageBox.information(self, "Saved", f"Result saved to:\n{path}")
