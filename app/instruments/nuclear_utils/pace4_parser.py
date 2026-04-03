"""PACE4 HTML parser — extracts beam energy and residual nucleus cross sections
from LISE++ PACE4 output files.
"""

import re
from html.parser import HTMLParser
from pathlib import Path


# Proton-number → element-symbol lookup (Z=1..118)
_ELEMENTS = [
    "", "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",
    "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds",
    "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
]


def _z_to_symbol(z: int) -> str:
    if 1 <= z <= len(_ELEMENTS) - 1:
        return _ELEMENTS[z]
    return "??"


# ─────────────────────────────────────────────────────────
# HTML table extractor
# ─────────────────────────────────────────────────────────

class _TableParser(HTMLParser):
    """Minimal state-machine parser that collects all HTML table contents."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[str]]] = []
        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._current_cell: str | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._current_table = []
        elif tag == "tr" and self._current_table is not None:
            self._current_row = []
        elif tag in ("td", "th") and self._current_row is not None:
            self._current_cell = ""

    def handle_data(self, data):
        if self._current_cell is not None:
            self._current_cell += data

    def handle_endtag(self, tag):
        if tag == "table":
            if self._current_table is not None:
                self.tables.append(self._current_table)
            self._current_table = None
            self._current_row = None
            self._current_cell = None
        elif tag == "tr":
            if self._current_row is not None and self._current_table is not None:
                self.tables[-1].append(self._current_row) if self.tables else None
                if self._current_table is not None:
                    self._current_table.append(self._current_row)
                self._current_row = None
        elif tag in ("td", "th"):
            if self._current_row is not None and self._current_cell is not None:
                self._current_row.append(self._current_cell.strip())
                self._current_cell = None


# ─────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────

def parse_pace4_html(path: str | Path) -> dict:
    """Parse a LISE++ PACE4 HTML output file.

    Returns
    -------
    dict with keys:
        "energy_MeV"  : float — lab-frame beam energy
        "projectile"  : str   — e.g. "48Ca"
        "target"      : str   — e.g. "124Sn"
        "compound"    : str   — e.g. "172Yb"
        "residues"    : list of dicts, each with keys
                          "Z", "N", "A", "symbol", "label",
                          "events", "percent", "xsec_mb"
    """
    path = Path(path)
    content = path.read_text(encoding="utf-8", errors="replace")

    result = {
        "energy_MeV": _extract_energy(content),
        "projectile": "",
        "target": "",
        "compound": "",
        "residues": [],
    }

    tp = _TableParser()
    tp.feed(content)

    # First table: projectile / target / compound nucleus info
    _parse_header_table(tp.tables, result)

    # The "Yields of residual nuclei" table: look for table with x-section header
    result["residues"] = _parse_yields_table(tp.tables)

    return result


# ─────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────

def _extract_energy(content: str) -> float:
    """Extract beam energy from PACE4 HTML content."""
    # Pattern: "E = </em>300<em> MeV" or "E = 300 MeV"
    m = re.search(r"E\s*=\s*</em>\s*(\d+\.?\d*)\s*<em>\s*MeV", content)
    if m:
        return float(m.group(1))
    # Fallback: bare "E = 300 MeV"
    m = re.search(r"E\s*=\s*(\d+\.?\d*)\s*MeV", content)
    if m:
        return float(m.group(1))
    return 0.0


def _parse_header_table(tables: list, result: dict):
    """Extract projectile / target / compound from the first Z-N-A table."""
    for table in tables[:3]:
        if not table:
            continue
        header = table[0]
        if len(header) >= 4 and any("Z" in c for c in header) and any("A" in c for c in header):
            for row in table[1:]:
                if len(row) < 4:
                    continue
                label = row[0].lower()
                try:
                    z = int(row[1])
                    a = int(row[3])
                    sym = _z_to_symbol(z)
                    nuclide = f"{a}{sym}"
                except (ValueError, IndexError):
                    continue
                if "project" in label:
                    result["projectile"] = nuclide
                elif "target" in label:
                    result["target"] = nuclide
                elif "compound" in label:
                    result["compound"] = nuclide
            return


def _parse_yields_table(tables: list) -> list[dict]:
    """Find and parse the 'Yields of residual nuclei' table.

    The LISE++ PACE4 HTML table has header (6 cols due to colspan=2 on A):
        Z | N | A | events | percent | x-section(mb)

    But data rows have 7 columns because the colspan=2 "A" becomes two cells:
        Z | N | A(number) | Symbol | events | percent | x-section(mb)
    """
    for table in tables:
        if not table:
            continue
        header = table[0]
        header_str = " ".join(header).lower()
        if "x-section" not in header_str and "percent" not in header_str:
            continue

        # Verify column 0 is Z and column 1 is N
        if not (header[0].strip() == "Z" and header[1].strip() == "N"):
            continue

        residues = []
        for row in table[1:]:
            if len(row) < 5:
                continue
            try:
                z = int(row[0])
                n = int(row[1])
            except ValueError:
                continue

            # If 7 columns: Z N A symbol events percent xsec
            # If 6 columns: Z N A events percent xsec (no separate symbol)
            if len(row) >= 7 and row[3].strip().isalpha() and len(row[3].strip()) <= 3:
                try:
                    a = int(row[2])
                    symbol = row[3].strip()
                    xsec = float(row[6].replace(",", "."))
                except (ValueError, IndexError):
                    continue
            else:
                try:
                    a = int(row[2])
                    xsec = float(row[-1].replace(",", "."))
                except (ValueError, IndexError):
                    continue
                symbol = ""

            label = f"{a}{symbol}" if symbol else str(a)
            residues.append({
                "Z": z, "N": n, "A": a,
                "symbol": symbol, "label": label,
                "xsec_mb": xsec,
            })

        if residues:
            return residues

    return []
