"""Constants reference panel — nuclear & fundamental physics constants with unit conversion."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
)
from PyQt6.QtCore import Qt

# ──────────────────────────────────────────────────────────────────
# Unit systems
# ──────────────────────────────────────────────────────────────────

_UNIT_SYSTEMS = [
    "SI (base units)",
    "SI (practical multiples)",
    "eV system (eV, fm, c)",
    "keV system",
    "MeV system",
]

# ──────────────────────────────────────────────────────────────────
# Constants data
#
# Each entry: (name, symbol, values_per_unit_system, note)
# values_per_unit_system is a list of (value_str, unit_str) tuples
# matching the order of _UNIT_SYSTEMS.
# ──────────────────────────────────────────────────────────────────

_CONSTANTS = [
    # ── Fundamental ──
    (
        "Speed of light", "c",
        [
            ("299 792 458", "m/s"),
            ("299 792 458", "m/s"),
            ("1", "c  (natural)"),
            ("1", "c"),
            ("1", "c"),
        ],
        "Exact (SI definition)",
    ),
    (
        "Planck constant", "h",
        [
            ("6.62607 × 10⁻³⁴", "J·s"),
            ("6.62607 × 10⁻³⁴", "J·s"),
            ("4.13567 × 10⁻¹⁵", "eV·s"),
            ("4.13567 × 10⁻¹²", "keV·s"),
            ("4.13567 × 10⁻¹⁵", "MeV·s"),
        ],
        "CODATA 2018",
    ),
    (
        "Reduced Planck constant", "ℏ",
        [
            ("1.05457 × 10⁻³⁴", "J·s"),
            ("1.05457 × 10⁻³⁴", "J·s"),
            ("6.58212 × 10⁻¹⁶", "eV·s"),
            ("6.58212 × 10⁻¹³", "keV·s"),
            ("6.58212 × 10⁻²²", "MeV·s"),
        ],
        "CODATA 2018",
    ),
    (
        "ℏc product", "ℏc",
        [
            ("3.16153 × 10⁻²⁶", "J·m"),
            ("3.16153 × 10⁻²⁶", "J·m"),
            ("197.327", "eV·nm = MeV·fm"),
            ("197.327 × 10³", "keV·fm"),
            ("197.327", "MeV·fm"),
        ],
        "Useful for converting wavelengths ↔ energies",
    ),
    (
        "Elementary charge", "e",
        [
            ("1.60218 × 10⁻¹⁹", "C"),
            ("1.60218 × 10⁻¹⁹", "C"),
            ("1", "e"),
            ("1", "e"),
            ("1", "e"),
        ],
        "Exact (SI 2019 redefinition)",
    ),
    (
        "Boltzmann constant", "k_B",
        [
            ("1.38065 × 10⁻²³", "J/K"),
            ("1.38065 × 10⁻²³", "J/K"),
            ("8.61733 × 10⁻⁵", "eV/K"),
            ("8.61733 × 10⁻⁸", "keV/K"),
            ("8.61733 × 10⁻¹¹", "MeV/K"),
        ],
        "CODATA 2018",
    ),
    (
        "Fine structure constant", "α",
        [
            ("7.29735 × 10⁻³", "dimensionless"),
            ("1 / 137.036", "dimensionless"),
            ("1 / 137.036", "dimensionless"),
            ("1 / 137.036", "dimensionless"),
            ("1 / 137.036", "dimensionless"),
        ],
        "α = e²/(4πε₀ℏc)",
    ),
    (
        "Avogadro constant", "Nₐ",
        [
            ("6.02214 × 10²³", "mol⁻¹"),
            ("6.02214 × 10²³", "mol⁻¹"),
            ("6.02214 × 10²³", "mol⁻¹"),
            ("6.02214 × 10²³", "mol⁻¹"),
            ("6.02214 × 10²³", "mol⁻¹"),
        ],
        "Exact (SI 2019 redefinition)",
    ),
    # ── Nuclear masses & radii ──
    (
        "Atomic mass unit", "u (AMU)",
        [
            ("1.66054 × 10⁻²⁷", "kg"),
            ("1.66054 × 10⁻²⁷", "kg"),
            ("931.494 × 10⁶", "eV/c²"),
            ("931 494", "keV/c²"),
            ("931.494", "MeV/c²"),
        ],
        "1 u = m(¹²C) / 12",
    ),
    (
        "Proton mass", "mₚ",
        [
            ("1.67262 × 10⁻²⁷", "kg"),
            ("1.67262 × 10⁻²⁷", "kg"),
            ("938.272 × 10⁶", "eV/c²"),
            ("938 272", "keV/c²"),
            ("938.272", "MeV/c²"),
        ],
        "CODATA 2018",
    ),
    (
        "Neutron mass", "mₙ",
        [
            ("1.67493 × 10⁻²⁷", "kg"),
            ("1.67493 × 10⁻²⁷", "kg"),
            ("939.565 × 10⁶", "eV/c²"),
            ("939 565", "keV/c²"),
            ("939.565", "MeV/c²"),
        ],
        "CODATA 2018",
    ),
    (
        "Electron mass", "mₑ",
        [
            ("9.10938 × 10⁻³¹", "kg"),
            ("9.10938 × 10⁻³¹", "kg"),
            ("0.51100 × 10⁶", "eV/c²"),
            ("511.0", "keV/c²"),
            ("0.51100", "MeV/c²"),
        ],
        "CODATA 2018",
    ),
    (
        "Nuclear matter radius", "r₀ (matter)",
        [
            ("1.2 × 10⁻¹⁵", "m"),
            ("1.2", "fm"),
            ("1.2", "fm"),
            ("1.2", "fm"),
            ("1.2", "fm"),
        ],
        "R = r₀ · A^(1/3). PDG / AME",
    ),
    (
        "Coulomb barrier radius", "r₀ (Coulomb)",
        [
            ("1.35 × 10⁻¹⁵", "m"),
            ("1.35", "fm"),
            ("1.35", "fm"),
            ("1.35", "fm"),
            ("1.35", "fm"),
        ],
        "V_C = Z₁Z₂e²/(4πε₀·r₀·(A₁^⅓+A₂^⅓)). Bass 1980",
    ),
    (
        "Classical proton radius", "rₚ",
        [
            ("0.8414 × 10⁻¹⁵", "m"),
            ("0.8414", "fm"),
            ("0.8414", "fm"),
            ("0.8414", "fm"),
            ("0.8414", "fm"),
        ],
        "Charge radius from electron scattering (PRad 2019)",
    ),
    # ── Nuclear energy scales ──
    (
        "Neutron separation energy (typical)", "Sₙ",
        [
            ("~1.3 × 10⁻¹²", "J"),
            ("~1.3 × 10⁻¹²", "J"),
            ("~8 × 10⁶", "eV"),
            ("~8 000", "keV"),
            ("~8", "MeV"),
        ],
        "Typical for stable nuclei near β-stability",
    ),
    (
        "Pion mass (π±)", "m_π±",
        [
            ("2.48801 × 10⁻²⁸", "kg"),
            ("2.48801 × 10⁻²⁸", "kg"),
            ("139.570 × 10⁶", "eV/c²"),
            ("139 570", "keV/c²"),
            ("139.570", "MeV/c²"),
        ],
        "Sets nuclear force range: r ~ ℏ/(m_π c) ≈ 1.4 fm",
    ),
    # ── Electromagnetic ──
    (
        "Coulomb constant", "kₑ = 1/(4πε₀)",
        [
            ("8.98755 × 10⁹", "N·m²/C²"),
            ("8.98755 × 10⁹", "N·m²/C²"),
            ("1.43996", "eV·nm / e²"),
            ("1.43996 × 10³", "keV·fm / e²"),
            ("1.43996", "MeV·fm / e²"),
        ],
        "Coulomb barrier, electromagnetic transition rates",
    ),
    (
        "Nuclear magneton", "μₙ",
        [
            ("5.05078 × 10⁻²⁷", "J/T"),
            ("5.05078 × 10⁻²⁷", "J/T"),
            ("3.15245 × 10⁻⁸", "eV/T"),
            ("3.15245 × 10⁻⁵", "keV/T"),
            ("3.15245 × 10⁻⁸", "MeV/T"),
        ],
        "μₙ = eℏ/(2mₚ). Magnetic moments in nuclear structure",
    ),
    (
        "Bohr magneton", "μ_B",
        [
            ("9.27401 × 10⁻²⁴", "J/T"),
            ("9.27401 × 10⁻²⁴", "J/T"),
            ("5.78838 × 10⁻⁵", "eV/T"),
            ("5.78838 × 10⁻²", "keV/T"),
            ("5.78838 × 10⁻⁵", "MeV/T"),
        ],
        "Atomic magnetic moments",
    ),
    # ── Transition rates ──
    (
        "Weisskopf single-particle estimate B(E1)", "B_W(E1)",
        [
            ("—", "—"),
            ("6.446 × 10⁻⁴ · A^(2/3)", "e²·fm²"),
            ("6.446 × 10⁻⁴ · A^(2/3)", "e²·fm²"),
            ("6.446 × 10⁻⁴ · A^(2/3)", "e²·fm²"),
            ("6.446 × 10⁻⁴ · A^(2/3)", "e²·fm²"),
        ],
        "B_W(Eλ) = (1/(4π)) · (3/(λ+3))² · R^(2λ) e²",
    ),
    (
        "Weisskopf single-particle estimate B(E2)", "B_W(E2)",
        [
            ("—", "—"),
            ("5.940 × 10⁻⁶ · A^(4/3)", "e²·fm⁴"),
            ("5.940 × 10⁻⁶ · A^(4/3)", "e²·fm⁴"),
            ("5.940 × 10⁻⁶ · A^(4/3)", "e²·fm⁴"),
            ("5.940 × 10⁻⁶ · A^(4/3)", "e²·fm⁴"),
        ],
        "B_W(E2; A) — depends on mass number A",
    ),
    (
        "Weisskopf single-particle estimate B(M1)", "B_W(M1)",
        [
            ("—", "—"),
            ("1.790", "μₙ²"),
            ("1.790", "μₙ²"),
            ("1.790", "μₙ²"),
            ("1.790", "μₙ²"),
        ],
        "B_W(M1) = 10/(4π) (3/4)² μₙ²",
    ),
    # ── Useful conversion factors ──
    (
        "1 barn", "b",
        [
            ("1 × 10⁻²⁸", "m²"),
            ("100", "fm²"),
            ("100", "fm²"),
            ("100", "fm²"),
            ("100", "fm²"),
        ],
        "Cross-section unit. 1 mb = 10⁻³ b",
    ),
    (
        "ℏ / ln(2)", "—",
        [
            ("1.51926 × 10⁻³⁴", "J·s"),
            ("1.51926 × 10⁻³⁴", "J·s"),
            ("9.49122 × 10⁻¹⁶", "eV·s"),
            ("9.49122 × 10⁻¹³", "keV·s"),
            ("9.49122 × 10⁻²²", "MeV·s"),
        ],
        "Γ (width) = ℏ·ln(2) / T₁/₂. Width ↔ half-life conversion",
    ),
    (
        "1 ps in distance (v = c)", "c · 1 ps",
        [
            ("2.99792 × 10⁻⁴", "m"),
            ("0.29979", "mm = 299.792 µm"),
            ("0.29979", "mm"),
            ("0.29979", "mm"),
            ("0.29979", "mm"),
        ],
        "Light travel distance in 1 ps — sets RDDS distance scale",
    ),
]


class ConstantsPanel(QWidget):
    """Interactive physics constants reference with unit-system selector."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        header = QLabel("Constants — Nuclear & Fundamental Physics")
        header.setProperty("heading", True)
        layout.addWidget(header)

        sub = QLabel(
            "Quick reference for constants commonly used in nuclear structure, "
            "γ-ray spectroscopy, and reaction calculations. "
            "Select a unit system to convert all values."
        )
        sub.setProperty("subheading", True)
        sub.setWordWrap(True)
        layout.addWidget(sub)

        # Unit selector
        unit_row = QHBoxLayout()
        unit_row.addWidget(QLabel("Unit system:"))
        self._unit_combo = QComboBox()
        for name in _UNIT_SYSTEMS:
            self._unit_combo.addItem(name)
        self._unit_combo.setCurrentIndex(4)  # MeV system default
        self._unit_combo.currentIndexChanged.connect(self._refresh_table)
        unit_row.addWidget(self._unit_combo)
        unit_row.addStretch()
        layout.addLayout(unit_row)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(
            ["Constant", "Symbol", "Value", "Unit", "Note"]
        )
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self._table, stretch=1)

        self._refresh_table(self._unit_combo.currentIndex())

    def _refresh_table(self, unit_idx: int):
        self._table.setRowCount(len(_CONSTANTS))
        for row, (name, symbol, unit_vals, note) in enumerate(_CONSTANTS):
            val_str, unit_str = unit_vals[unit_idx]
            self._table.setItem(row, 0, self._item(name))
            self._table.setItem(row, 1, self._item(symbol, center=True))
            self._table.setItem(
                row, 2, self._item(val_str, Qt.AlignmentFlag.AlignRight)
            )
            self._table.setItem(row, 3, self._item(unit_str, center=True))
            self._table.setItem(row, 4, self._item(note))

    @staticmethod
    def _item(
        text: str,
        align=Qt.AlignmentFlag.AlignLeft,
        center: bool = False,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        a = Qt.AlignmentFlag.AlignCenter if center else align
        item.setTextAlignment(a | Qt.AlignmentFlag.AlignVCenter)
        return item
