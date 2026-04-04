"""Reusable result window — displays tables and/or plots in a separate pop-out window.

Used by all instruments to show results outside the main panel. Supports:
  - Table view with sortable columns
  - Plot view (gnuplot-generated PNG displayed as QPixmap)
  - PDF export for both tables and plots
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QTabWidget, QWidget, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from app.pdf_export import save_table_pdf, save_plot_pdf


class ResultWindow(QDialog):
    """Pop-out window for displaying calculation results.

    Can show a table, a plot image, or both (in tabs).
    """

    def __init__(self, title: str = "Results", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(700, 500)
        self.resize(900, 650)

        self._title = title
        self._subtitle = ""
        self._table: QTableWidget | None = None
        self._plot_path: str | None = None
        self._orig_headers: list[str] = []
        self._orig_rows: list[list[str]] = []

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(10)

        # Title label
        self._title_label = QLabel(title)
        self._title_label.setProperty("heading", True)
        self._layout.addWidget(self._title_label)

        self._subtitle_label = QLabel("")
        self._subtitle_label.setProperty("subheading", True)
        self._subtitle_label.setVisible(False)
        self._layout.addWidget(self._subtitle_label)

        # Content area (will be populated by set_table / set_plot)
        self._content_area = QVBoxLayout()
        self._layout.addLayout(self._content_area, stretch=1)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._save_btn = QPushButton("Save as PDF…")
        self._save_btn.setFixedHeight(36)
        self._save_btn.clicked.connect(self._save_pdf)
        btn_row.addWidget(self._save_btn)
        self._layout.addLayout(btn_row)

    def set_subtitle(self, text: str) -> None:
        self._subtitle = text
        self._subtitle_label.setText(text)
        self._subtitle_label.setVisible(bool(text))

    def set_table(
        self,
        headers: list[str],
        rows: list[list[str]],
        *,
        numeric_cols: list[int] | None = None,
    ) -> None:
        """Populate the window with a data table.

        Parameters
        ----------
        headers : list[str]
            Column header labels.
        rows : list[list[str]]
            Table data.
        numeric_cols : list[int] or None
            Column indices that should be right-aligned and sorted numerically.
        """
        self._clear_content()
        if numeric_cols is None:
            numeric_cols = []

        # Store original data for PDF export (preserves insertion order)
        self._orig_headers = list(headers)
        self._orig_rows = [list(r) for r in rows]

        table = QTableWidget(len(rows), len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                if c in numeric_cols:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                    try:
                        item.setData(Qt.ItemDataRole.UserRole, float(cell))
                    except ValueError:
                        pass
                else:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
                    )
                table.setItem(r, c, item)

        hdr = table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSortingEnabled(True)

        self._table = table
        self._content_area.addWidget(table)

    def set_plot(self, image_path: str) -> None:
        """Display a gnuplot-generated PNG in the window."""
        self._clear_content()
        self._plot_path = image_path

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        img_label = QLabel()
        pixmap = QPixmap(image_path)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(img_label)

        self._content_area.addWidget(scroll)

    def set_table_and_plot(
        self,
        headers: list[str],
        rows: list[list[str]],
        image_path: str,
        *,
        numeric_cols: list[int] | None = None,
    ) -> None:
        """Show both table and plot in tabs."""
        self._clear_content()
        if numeric_cols is None:
            numeric_cols = []

        # Store original data for PDF export (preserves insertion order)
        self._orig_headers = list(headers)
        self._orig_rows = [list(r) for r in rows]

        tabs = QTabWidget()

        # Table tab
        table_widget = QWidget()
        tl = QVBoxLayout(table_widget)
        tl.setContentsMargins(0, 8, 0, 0)

        table = QTableWidget(len(rows), len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                if c in numeric_cols:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                    try:
                        item.setData(Qt.ItemDataRole.UserRole, float(cell))
                    except ValueError:
                        pass
                else:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
                    )
                table.setItem(r, c, item)

        hdr = table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSortingEnabled(True)

        self._table = table
        tl.addWidget(table)
        tabs.addTab(table_widget, "Table")

        # Plot tab
        plot_widget = QWidget()
        pl = QVBoxLayout(plot_widget)
        pl.setContentsMargins(0, 8, 0, 0)
        self._plot_path = image_path
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        img_label = QLabel()
        pixmap = QPixmap(image_path)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(img_label)
        pl.addWidget(scroll)
        tabs.addTab(plot_widget, "Plot")

        self._content_area.addWidget(tabs)

    def _clear_content(self):
        while self._content_area.count():
            item = self._content_area.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._table = None
        self._plot_path = None
        self._orig_headers = []
        self._orig_rows = []

    def _save_pdf(self):
        default_name = self._title.replace(" ", "_").lower() + ".pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save as PDF", default_name, "PDF Files (*.pdf)"
        )
        if not path:
            return

        if self._table and self._plot_path:
            # Save both: table first, then plot on second page
            self._save_combined_pdf(path)
        elif self._table:
            self._save_table_only(path)
        elif self._plot_path:
            save_plot_pdf(path, self._plot_path, self._title, subtitle=self._subtitle)

    def _save_table_only(self, path: str):
        save_table_pdf(
            path, self._title, self._orig_headers, self._orig_rows,
            subtitle=self._subtitle,
        )

    def _save_combined_pdf(self, path: str):
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Page 1: table
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, self._title, new_x="LMARGIN", new_y="NEXT", align="C")
        if self._subtitle:
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(
                0, 6, self._subtitle, new_x="LMARGIN", new_y="NEXT", align="C"
            )
        pdf.ln(6)

        n_cols = len(self._orig_headers)
        page_w = pdf.w - pdf.l_margin - pdf.r_margin
        col_w = [page_w / n_cols] * n_cols

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(220, 220, 220)
        for hdr_text in self._orig_headers:
            pdf.cell(col_w[0], 8, hdr_text, border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 9)
        for row in self._orig_rows:
            for i, cell in enumerate(row):
                w = col_w[i] if i < len(col_w) else col_w[-1]
                pdf.cell(w, 7, str(cell), border=1, align="C")
            pdf.ln()

        # Page 2: plot
        pdf.add_page("L")
        img_w = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.image(self._plot_path, x=pdf.l_margin, w=img_w)

        pdf.output(path)
