"""Kinematics panel — beam velocity, Coulomb barrier, recoil velocity."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QMessageBox, QGridLayout,
)
from app.instruments.nuclear_utils import calculator


class KinematicsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # ── Beam parameters ──
        beam_group = QGroupBox("Beam & Reaction")
        grid = QGridLayout(beam_group)
        grid.setSpacing(10)

        fields = [
            ("Beam energy:", "MeV", "E_beam", "59"),
            ("Beam A:", "", "A_beam", "13"),
            ("Beam Z:", "", "Z_beam", "6"),
            ("Target A:", "", "A_target", "100"),
            ("Target Z:", "", "Z_target", "42"),
        ]
        self._inputs = {}
        for row, (label, unit, key, default) in enumerate(fields):
            grid.addWidget(QLabel(label), row, 0)
            edit = QLineEdit(default)
            edit.setFixedWidth(130)
            self._inputs[key] = edit
            grid.addWidget(edit, row, 1)
            if unit:
                grid.addWidget(QLabel(unit), row, 2)

        layout.addWidget(beam_group)

        calc_btn = QPushButton("Calculate Kinematics")
        calc_btn.setFixedHeight(42)
        calc_btn.clicked.connect(self._calculate)
        layout.addWidget(calc_btn)

        # ── Results ──
        result_group = QGroupBox("Results")
        result_layout = QVBoxLayout(result_group)
        self.result_label = QLabel("Enter data and click Calculate")
        self.result_label.setProperty("result", True)
        self.result_label.setWordWrap(True)
        result_layout.addWidget(self.result_label)
        layout.addWidget(result_group)

        layout.addStretch()

    def _calculate(self):
        try:
            E = float(self._inputs["E_beam"].text())
            A_b = float(self._inputs["A_beam"].text())
            Z_b = float(self._inputs["Z_beam"].text())
            A_t = float(self._inputs["A_target"].text())
            Z_t = float(self._inputs["Z_target"].text())

            # Beam velocity
            beta_beam, v_beam = calculator.beam_beta_and_velocity(E, A_b)

            # Coulomb barrier
            V_C = calculator.coulomb_barrier_MeV(Z_b, A_b, Z_t, A_t)

            # Compound nucleus recoil
            beta_recoil, v_recoil = calculator.recoil_velocity_two_body(E, A_b, A_t)

            # Nuclear radii
            R_beam = calculator.nuclear_radius_fm(A_b)
            R_target = calculator.nuclear_radius_fm(A_t)

            text = (
                f"Beam velocity:  β = {beta_beam:.5f}  "
                f"({beta_beam*100:.3f}% c)  |  v = {v_beam:.0f} m/s\n"
                f"Coulomb barrier:  V_C = {V_C:.2f} MeV  "
                f"(E/V_C = {E/V_C:.2f})\n"
                f"CN recoil:  β_CN = {beta_recoil:.6f}  "
                f"({beta_recoil*100:.4f}% c)  |  v = {v_recoil:.0f} m/s\n"
                f"Nuclear radii:  R_beam = {R_beam:.3f} fm  |  "
                f"R_target = {R_target:.3f} fm"
            )
            self.result_label.setText(text)

            from app.action_history import record
            params = {k: v.text() for k, v in self._inputs.items()}
            record(
                "Accelerator",
                f"Kinematics: E={E} MeV, A_b={A_b}, Z_b={Z_b}, A_t={A_t}, Z_t={Z_t}",
                params,
            )

        except ValueError:
            QMessageBox.warning(self, "Input Error", "All fields must be valid numbers.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def restore_params(self, params: dict):
        for key, val in params.items():
            if key in self._inputs:
                self._inputs[key].setText(str(val))
