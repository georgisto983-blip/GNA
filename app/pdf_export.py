"""PDF export utility — save tables and plots as PDF documents.

Uses fpdf2 for lightweight, pure-Python PDF generation.
"""

from pathlib import Path
from fpdf import FPDF


def save_table_pdf(
    path: str,
    title: str,
    headers: list[str],
    rows: list[list[str]],
    *,
    subtitle: str = "",
    col_widths: list[float] | None = None,
) -> None:
    """Save a data table to a PDF file.

    Parameters
    ----------
    path : str
        Output PDF file path.
    title : str
        Document title (shown at top).
    headers : list[str]
        Column header labels.
    rows : list[list[str]]
        Table data (each inner list = one row).
    subtitle : str
        Optional subtitle below the title.
    col_widths : list[float] or None
        Column widths in mm. If None, columns are auto-sized equally.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")

    if subtitle:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, subtitle, new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.ln(6)

    # Calculate column widths
    n_cols = len(headers)
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    if col_widths is None:
        col_widths = [page_width / n_cols] * n_cols

    # Header row
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(220, 220, 220)
    for i, hdr in enumerate(headers):
        pdf.cell(col_widths[i], 8, hdr, border=1, fill=True, align="C")
    pdf.ln()

    # Data rows
    pdf.set_font("Helvetica", "", 9)
    for row in rows:
        for i, cell in enumerate(row):
            w = col_widths[i] if i < len(col_widths) else col_widths[-1]
            pdf.cell(w, 7, str(cell), border=1, align="C")
        pdf.ln()

    pdf.output(path)


def save_plot_pdf(
    path: str,
    image_path: str,
    title: str = "",
    *,
    subtitle: str = "",
) -> None:
    """Save a plot image (PNG) into a PDF with optional title.

    Parameters
    ----------
    path : str
        Output PDF path.
    image_path : str
        Path to the PNG plot image.
    title : str
        Optional title above the plot.
    subtitle : str
        Optional subtitle.
    """
    pdf = FPDF()
    pdf.add_page("L")  # landscape for plots

    if title:
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")

    if subtitle:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, subtitle, new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.ln(4)

    # Fit image to page width
    img_w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.image(image_path, x=pdf.l_margin, w=img_w)

    pdf.output(path)
