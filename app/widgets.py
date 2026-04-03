"""Shared UI widgets used across GNA instruments."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import Qt
from uncertainties import ufloat, UFloat


class ValueUncertaintyInput(QWidget):
    """Paired input fields for a physical quantity: value +/- uncertainty."""

    def __init__(self, label, unit="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._label = QLabel(label)
        self._label.setFixedWidth(180)
        layout.addWidget(self._label)

        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("value")
        self.value_edit.setFixedWidth(130)
        layout.addWidget(self.value_edit)

        pm = QLabel("±")
        pm.setFixedWidth(16)
        pm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(pm)

        self.unc_edit = QLineEdit()
        self.unc_edit.setPlaceholderText("uncertainty")
        self.unc_edit.setFixedWidth(130)
        layout.addWidget(self.unc_edit)

        if unit:
            unit_label = QLabel(unit)
            unit_label.setFixedWidth(40)
            layout.addWidget(unit_label)

        layout.addStretch()

    def get_value(self):
        """Return float (no uncertainty given) or ufloat (with uncertainty)."""
        val = float(self.value_edit.text())
        unc_text = self.unc_edit.text().strip()
        if unc_text:
            return ufloat(val, float(unc_text))
        return val

    def set_value(self, value, uncertainty=None):
        """Populate fields programmatically."""
        self.value_edit.setText(str(value))
        if uncertainty is not None:
            self.unc_edit.setText(str(uncertainty))
        else:
            self.unc_edit.clear()

    def clear(self):
        self.value_edit.clear()
        self.unc_edit.clear()

    def get_text(self):
        """Human-readable summary of the current value."""
        val = self.value_edit.text()
        unc = self.unc_edit.text().strip()
        return f"{val} ± {unc}" if unc else val


def format_halflife(t_half_s):
    """Format a half-life (in seconds) as a display string in picoseconds."""
    t_ps = t_half_s * 1e12
    if isinstance(t_ps, UFloat):
        return "T₁/₂ = " + f"{t_ps:.2u}".replace("+/-", " ± ") + " ps"
    return f"T₁/₂ = {t_ps:.2f} ps"
