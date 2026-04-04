"""Beam-on-target yield calculator panel."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QMessageBox, QGridLayout,
)
from app.instruments.nuclear_utils import calculator


class BeamYieldPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # ── Inputs ──
        input_group = QGroupBox("Beam & Target Parameters")
        grid = QGridLayout(input_group)
        grid.setSpacing(10)

        fields = [
            ("Beam current:", "pnA", "beam_current", "2"),
            ("Cross-section:", "mb", "cross_section", "70"),
            ("Target thickness:", "mg/cm²", "target_thickness", "1.3"),
            ("Target A:", "", "target_A", "100"),
            ("Detector efficiency:", "(0–1)", "det_eff", "0.01"),
            ("Excitation ratio:", "(0–1)", "exc_ratio", "0.08"),
            ("Sorter efficiency:", "(0–1)", "sort_eff", "0.05"),
        ]

        self._inputs = {}
        for row, (label, unit, key, default) in enumerate(fields):
            grid.addWidget(QLabel(label), row, 0)
            edit = QLineEdit(default)
            edit.setFixedWidth(130)
            self._inputs[key] = edit
            grid.addWidget(edit, row, 1)
            grid.addWidget(QLabel(unit), row, 2)

        layout.addWidget(input_group)

        # Calculate button
        calc_btn = QPushButton("Calculate Yield")
        calc_btn.setFixedHeight(42)
        calc_btn.clicked.connect(self._calculate)
        layout.addWidget(calc_btn)

        # ── Results ──
        result_group = QGroupBox("Expected Yield")
        result_layout = QVBoxLayout(result_group)
        self.result_label = QLabel("Enter parameters and click Calculate")
        self.result_label.setProperty("result", True)
        self.result_label.setWordWrap(True)
        result_layout.addWidget(self.result_label)
        layout.addWidget(result_group)

        layout.addStretch()

    def _calculate(self):
        try:
            result = calculator.beam_yield(
                beam_current_pnA=float(self._inputs["beam_current"].text()),
                cross_section_mb=float(self._inputs["cross_section"].text()),
                target_thickness_mg_cm2=float(self._inputs["target_thickness"].text()),
                target_A=float(self._inputs["target_A"].text()),
                detector_efficiency=float(self._inputs["det_eff"].text()),
                excitation_ratio=float(self._inputs["exc_ratio"].text()),
                sorter_efficiency=float(self._inputs["sort_eff"].text()),
            )

            text = (
                f"Y = {result['per_second']:.4f} counts/s\n"
                f"Y = {result['per_hour']:.1f} counts/hour\n"
                f"Y = {result['per_shift_8h']:.0f} counts / 8h shift"
            )
            self.result_label.setText(text)

            from app.action_history import record
            params = {k: v.text() for k, v in self._inputs.items()}
            record("Accelerator", f"Beam yield: {result['per_hour']:.1f} counts/hr", params)

        except ValueError:
            QMessageBox.warning(self, "Input Error", "All fields must be valid numbers.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def restore_params(self, params: dict):
        for key, val in params.items():
            if key in self._inputs:
                self._inputs[key].setText(str(val))
