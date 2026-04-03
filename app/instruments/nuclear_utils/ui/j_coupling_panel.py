"""J-coupling enumerator — angular momentum coupling for nucleons in a shell."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTextEdit, QGridLayout,
)
from app.instruments.nuclear_utils import calculator


class JCouplingPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # ── Nucleus input ──
        nucleus_group = QGroupBox("Nucleus")
        n_grid = QGridLayout(nucleus_group)
        n_grid.setSpacing(10)

        n_grid.addWidget(QLabel("Z (protons):"), 0, 0)
        self.z_edit = QLineEdit("47")
        self.z_edit.setFixedWidth(80)
        n_grid.addWidget(self.z_edit, 0, 1)

        n_grid.addWidget(QLabel("N (neutrons):"), 0, 2)
        self.n_edit = QLineEdit("60")
        self.n_edit.setFixedWidth(80)
        n_grid.addWidget(self.n_edit, 0, 3)

        n_grid.addWidget(QLabel("Nucleus name:"), 0, 4)
        self.name_edit = QLineEdit("107Ag")
        self.name_edit.setFixedWidth(80)
        n_grid.addWidget(self.name_edit, 0, 5)

        layout.addWidget(nucleus_group)

        # ── Shell info button ──
        info_btn = QPushButton("Analyze Shell Occupancy")
        info_btn.clicked.connect(self._analyze_shell)
        layout.addWidget(info_btn)

        self.shell_info = QTextEdit()
        self.shell_info.setReadOnly(True)
        self.shell_info.setMaximumHeight(160)
        self.shell_info.setStyleSheet(
            "QTextEdit {"
            "  background-color: #1e1e2e;"
            "  color: #c0caf5;"
            "  font-family: 'Cascadia Mono', 'Fira Mono', monospace;"
            "  font-size: 12px;"
            "  border: 1px solid #292e42;"
            "  border-radius: 4px;"
            "  padding: 8px;"
            "}"
        )
        layout.addWidget(self.shell_info)

        # ── Manual J-coupling ──
        coupling_group = QGroupBox("Enumerate J-values for Particles/Holes in an Orbital")
        c_layout = QHBoxLayout(coupling_group)

        c_layout.addWidget(QLabel("j (orbital):"))
        self.j_edit = QLineEdit("9/2")
        self.j_edit.setFixedWidth(60)
        c_layout.addWidget(self.j_edit)

        c_layout.addWidget(QLabel("n (particles/holes):"))
        self.n_particles_edit = QLineEdit("3")
        self.n_particles_edit.setFixedWidth(60)
        c_layout.addWidget(self.n_particles_edit)

        calc_btn = QPushButton("Enumerate J")
        calc_btn.clicked.connect(self._enumerate_j)
        c_layout.addWidget(calc_btn)
        c_layout.addStretch()
        layout.addWidget(coupling_group)

        # ── Results ──
        result_group = QGroupBox("Allowed J Values")
        result_layout = QVBoxLayout(result_group)
        self.result_label = QLabel("")
        self.result_label.setProperty("result", True)
        self.result_label.setWordWrap(True)
        result_layout.addWidget(self.result_label)
        layout.addWidget(result_group)

        layout.addStretch()

    def _analyze_shell(self):
        try:
            Z = int(self.z_edit.text())
            N = int(self.n_edit.text())
            name = self.name_edit.text().strip() or f"Z={Z}, N={N}"

            info = calculator.shell_model_occupancy(Z, N)

            lines = [f"Shell model analysis for {name}  (Z={Z}, N={N})\n"]
            for nucleon, label in [("protons", "Protons"), ("neutrons", "Neutrons")]:
                data = info[nucleon]
                lines.append(f"  {label}: {data['count']}  "
                             f"(shell {data['lower_closure']}–{data['upper_closure']})")
                lines.append(f"    Particles above closure: {data['particles_above_closure']}")
                lines.append(f"    Holes below closure:     {data['holes_below_closure']}")

                if data["filled_orbitals"]:
                    lines.append("    Orbital occupancy:")
                    for orb in data["filled_orbitals"]:
                        bar = "█" * orb["occupancy"] + "░" * (orb["capacity"] - orb["occupancy"])
                        lines.append(
                            f"      {orb['orbital']:>8s} (j={orb['j']:>4s}): "
                            f"{bar}  {orb['occupancy']}/{orb['capacity']}"
                        )

                active = data.get("active_orbital")
                if active:
                    holes = active["capacity"] - active["occupancy"]
                    lines.append(
                        f"    → Active orbital: {active['orbital']} "
                        f"({active['occupancy']} particles, {holes} holes)"
                    )
                    # Auto-fill the J-coupling inputs
                    self.j_edit.setText(active["j"])
                    self.n_particles_edit.setText(str(active["occupancy"]))
                lines.append("")

            self.shell_info.setPlainText("\n".join(lines))

        except ValueError:
            QMessageBox.warning(self, "Error", "Z and N must be integers.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _enumerate_j(self):
        try:
            j_str = self.j_edit.text().strip()
            n = int(self.n_particles_edit.text())

            J_values = calculator.enumerate_J_values(j_str, n)

            J_strs = [str(J) for J in J_values]
            text = (
                f"n = {n} particles in j = {j_str} orbital:\n\n"
                f"Allowed J values:  {', '.join(J_strs)}\n\n"
                f"Total distinct J states: {len(J_values)}"
            )
            self.result_label.setText(text)

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
