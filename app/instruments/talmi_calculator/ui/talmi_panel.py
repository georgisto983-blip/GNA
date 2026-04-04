"""Talmi Calculator panel — B(E2) transition probability calculator."""

import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QHeaderView, QTabWidget,
)
from PyQt6.QtCore import Qt

from app.instruments.talmi_calculator import calculator
from app.result_window import ResultWindow


class TalmiPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._matrix = None
        self._init_ui()
        self._load_default_weights()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        title = QLabel("Talmi Calculator — B(E2) Transition Probabilities")
        title.setProperty("heading", True)
        layout.addWidget(title)

        subtitle = QLabel(
            "Talmi Empirical Shell Model procedure for the g₉/₂ shell "
            "(j = 9/2 multiplet)"
        )
        subtitle.setProperty("subheading", True)
        layout.addWidget(subtitle)

        tabs = QTabWidget()
        tabs.addTab(self._create_manual_tab(), "Manual Input")
        tabs.addTab(self._create_json_tab(), "Load from JSON")
        layout.addWidget(tabs, stretch=1)

    # ── Manual input tab ──

    def _create_manual_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)

        # Nuclei info
        nuclei_group = QGroupBox("Nuclei Information (optional)")
        nuclei_layout = QHBoxLayout(nuclei_group)
        nuclei_layout.addWidget(QLabel("Source nucleus:"))
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("e.g. 104Cd")
        self.source_edit.setFixedWidth(100)
        nuclei_layout.addWidget(self.source_edit)
        nuclei_layout.addWidget(QLabel("Target nucleus:"))
        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderText("e.g. 103Ag")
        self.target_edit.setFixedWidth(100)
        nuclei_layout.addWidget(self.target_edit)
        nuclei_layout.addStretch()
        layout.addWidget(nuclei_group)

        # Input vector(s)
        vec_group = QGroupBox("Input Vectors (4 values each — empirical B(E2) data)")
        vec_layout = QVBoxLayout(vec_group)

        self.dataset_table = QTableWidget(1, 5)
        self.dataset_table.setHorizontalHeaderLabels([
            "Method Name", "v₁", "v₂", "v₃", "v₄"
        ])
        self.dataset_table.setMinimumWidth(700)
        self.dataset_table.setMinimumHeight(100)
        hh = self.dataset_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, 5):
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
        self.dataset_table.setColumnWidth(1, 110)
        self.dataset_table.setColumnWidth(2, 110)
        self.dataset_table.setColumnWidth(3, 110)
        self.dataset_table.setColumnWidth(4, 110)
        self.dataset_table.setItem(0, 0, QTableWidgetItem("Experimental"))
        vec_layout.addWidget(self.dataset_table)

        ds_btn_row = QHBoxLayout()
        for text, slot in [
            ("Add Dataset", self._add_dataset_row),
            ("Remove Dataset", self._remove_dataset_row),
        ]:
            btn = QPushButton(text)
            btn.setProperty("secondary", True)
            btn.clicked.connect(slot)
            ds_btn_row.addWidget(btn)
        ds_btn_row.addStretch()
        vec_layout.addLayout(ds_btn_row)
        layout.addWidget(vec_group)

        # Weights file
        wt_group = QGroupBox("Weighting Factors Matrix")
        wt_layout = QHBoxLayout(wt_group)
        self.weights_path_label = QLabel("(using default)")
        self.weights_path_label.setStyleSheet("color: #565f89;")
        wt_layout.addWidget(self.weights_path_label)
        wt_browse_btn = QPushButton("Load Custom")
        wt_browse_btn.setProperty("secondary", True)
        wt_browse_btn.clicked.connect(self._load_custom_weights)
        wt_layout.addWidget(wt_browse_btn)
        wt_layout.addStretch()
        layout.addWidget(wt_group)

        # Calculate
        calc_btn = QPushButton("Calculate B(E2)")
        calc_btn.setFixedHeight(42)
        calc_btn.clicked.connect(self._calculate_manual)
        layout.addWidget(calc_btn)

        # Results table
        self._create_results_area(layout)
        return w

    # ── JSON tab ──

    def _create_json_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)

        file_group = QGroupBox("Input JSON File")
        file_layout = QHBoxLayout(file_group)
        self.json_path_edit = QLineEdit()
        self.json_path_edit.setPlaceholderText("path to input_data.json")
        file_layout.addWidget(self.json_path_edit)
        browse_btn = QPushButton("Browse")
        browse_btn.setProperty("secondary", True)
        browse_btn.clicked.connect(self._browse_json)
        file_layout.addWidget(browse_btn)
        layout.addWidget(file_group)

        calc_btn = QPushButton("Load && Calculate")
        calc_btn.setFixedHeight(42)
        calc_btn.clicked.connect(self._calculate_json)
        layout.addWidget(calc_btn)

        # Re-use the same results table reference
        self._create_results_area_json(layout)
        return w

    # ── Shared results table ──

    def _create_results_area(self, layout):
        res_group = QGroupBox("B(E2) Results [W.u.]")
        res_layout = QVBoxLayout(res_group)

        self.result_table = QTableWidget(0, 0)
        self.result_table.setMinimumHeight(250)
        self.result_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        res_layout.addWidget(self.result_table)

        save_btn = QPushButton("Save Results")
        save_btn.setProperty("secondary", True)
        save_btn.clicked.connect(lambda: self._save_results(self.result_table))
        res_layout.addWidget(save_btn)

        layout.addWidget(res_group, stretch=1)

    def _create_results_area_json(self, layout):
        res_group = QGroupBox("B(E2) Results [W.u.]")
        res_layout = QVBoxLayout(res_group)

        self.result_table_json = QTableWidget(0, 0)
        self.result_table_json.setMinimumHeight(250)
        self.result_table_json.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        res_layout.addWidget(self.result_table_json)

        save_btn = QPushButton("Save Results")
        save_btn.setProperty("secondary", True)
        save_btn.clicked.connect(lambda: self._save_results(self.result_table_json))
        res_layout.addWidget(save_btn)

        layout.addWidget(res_group, stretch=1)

    # ── Actions ──

    def _load_default_weights(self):
        try:
            self._matrix = calculator.load_weighting_matrix()
            self.weights_path_label.setText("(default matrix loaded)")
        except FileNotFoundError as e:
            self.weights_path_label.setText(str(e))

    def _load_custom_weights(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Weighting Factors", "", "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            self._matrix = calculator.load_weighting_matrix(path)
            self.weights_path_label.setText(f"Loaded: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load weights:\n{e}")

    def _add_dataset_row(self):
        r = self.dataset_table.rowCount()
        self.dataset_table.insertRow(r)
        self.dataset_table.setItem(r, 0, QTableWidgetItem(f"Method_{r+1}"))

    def _remove_dataset_row(self):
        if self.dataset_table.rowCount() > 1:
            self.dataset_table.removeRow(self.dataset_table.rowCount() - 1)

    def _calculate_manual(self):
        if self._matrix is None:
            QMessageBox.warning(
                self, "Error", "Weighting factor matrix not loaded."
            )
            return

        try:
            all_results = {}
            for row in range(self.dataset_table.rowCount()):
                method_item = self.dataset_table.item(row, 0)
                method = method_item.text() if method_item else f"Dataset_{row+1}"

                vec = []
                for col in range(1, 5):
                    item = self.dataset_table.item(row, col)
                    if item and item.text().strip():
                        vec.append(float(item.text()))
                    else:
                        vec.append(0.0)

                be2_values = calculator.compute_be2(vec, self._matrix)
                all_results[method] = be2_values

            self._populate_result_table(
                self.result_table, all_results,
                self.source_edit.text(), self.target_edit.text()
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Calculation failed:\n{e}")

    def _calculate_json(self):
        path = self.json_path_edit.text().strip()
        if not path:
            QMessageBox.information(self, "Info", "Select a JSON file first.")
            return

        try:
            if self._matrix is None:
                self._matrix = calculator.load_weighting_matrix()

            source, target, datasets = calculator.parse_input_json(path)

            all_results = {}
            for ds in datasets:
                vec = [float(x) for x in ds["vector"]]
                be2_values = calculator.compute_be2(vec, self._matrix)
                all_results[ds["method"]] = be2_values

            self._populate_result_table(
                self.result_table_json, all_results, source, target
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed:\n{e}")

    def _populate_result_table(self, table, all_results, source, target):
        """Fill a QTableWidget with B(E2) results and open result window."""
        methods = list(all_results.keys())
        labels = calculator.TRANSITION_LABELS

        headers = ["Jᵢ", "Jᶠ"] + [f"B(E2) {m} [W.u.]" for m in methods]
        table.setColumnCount(len(headers))
        table.setRowCount(len(labels))
        table.setHorizontalHeaderLabels(headers)

        rows_data = []
        for i, (ji, jf) in enumerate(labels):
            table.setItem(i, 0, self._centered_item(ji))
            table.setItem(i, 1, self._centered_item(jf))
            row = [ji, jf]
            for j, method in enumerate(methods):
                val = all_results[method][i]
                text = "n/a" if (val is None or val != val) else f"{val:.2f}"
                table.setItem(i, j + 2, self._centered_item(text))
                row.append(text)
            rows_data.append(row)

        # Open result in separate window
        subtitle = ""
        if source and target:
            subtitle = f"{source} → {target}"

        win = ResultWindow("Talmi Calculator — B(E2) Results", parent=self)
        win.set_subtitle(subtitle)
        win.set_table(headers, rows_data, numeric_cols=list(range(2, len(headers))))
        win.show()
        # Keep reference so window is not garbage-collected
        self._result_window = win

    @staticmethod
    def _centered_item(text):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def _browse_json(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Input JSON", "", "JSON Files (*.json)"
        )
        if path:
            self.json_path_edit.setText(path)

    def _save_results(self, table):
        if table.rowCount() == 0:
            QMessageBox.information(self, "Info", "No results to save.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "talmi_results.pdf",
            "PDF Files (*.pdf);;Text Files (*.txt);;CSV Files (*.csv)",
        )
        if not path:
            return

        headers = []
        for c in range(table.columnCount()):
            headers.append(table.horizontalHeaderItem(c).text())

        rows = []
        for r in range(table.rowCount()):
            row_data = []
            for c in range(table.columnCount()):
                item = table.item(r, c)
                row_data.append(item.text() if item else "")
            rows.append(row_data)

        if path.endswith(".pdf"):
            from app.pdf_export import save_table_pdf
            # Ji/Jf columns are narrow; result columns fill remaining space
            n_result_cols = len(headers) - 2
            page_w = 190.0  # A4 usable width in mm (210 - margins)
            ji_jf_w = 20.0
            result_w = (page_w - 2 * ji_jf_w) / max(n_result_cols, 1)
            col_widths = [ji_jf_w, ji_jf_w] + [result_w] * n_result_cols
            subtitle = ""
            src = self.source_edit.text().strip()
            tgt = self.target_edit.text().strip()
            if src and tgt:
                subtitle = f"{src} → {tgt}"
            save_table_pdf(
                path, "Talmi Calculator — B(E2) Results", headers, rows,
                subtitle=subtitle, col_widths=col_widths,
            )
        else:
            sep = "," if path.endswith(".csv") else "\t"
            with open(path, "w") as f:
                f.write(sep.join(headers) + "\n")
                for row_data in rows:
                    f.write(sep.join(row_data) + "\n")

        QMessageBox.information(self, "Saved", f"Results saved to:\n{path}")
