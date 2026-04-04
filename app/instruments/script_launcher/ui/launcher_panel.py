"""Script Launcher panel — browse directories, select and run scripts.

Also provides ROSPHERE matrix cutting (via cmat + pexpect) and Autosort operations.
"""

import os
import re
import shutil
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit,
    QFileDialog, QMessageBox, QLineEdit, QSplitter, QComboBox,
)
from PyQt6.QtCore import QProcess, Qt, QThread, pyqtSignal
from app.config import load_settings, save_settings


# ── ROSPHERE ring-pair mapping ──
# Detectors 0-4: Fw, 5-9: Fw70deg, 10-14: 90deg, 15-19: Bw70deg, 20-24: Bw
# Ring pair code XY: X = ring of det A, Y = ring of det B
# Ring numbering: 1=Fw, 2=Fw70deg, 3=90deg, 4=Bw70deg, 5=Bw
_RING_LABELS = {1: "Fw", 2: "Fw70deg", 3: "90deg", 4: "Bw70deg", 5: "Bw"}

# Ordered: Fw+Bw first, then Fw70deg/Bw70deg cross, then pure 70deg, then 90deg
_RING_COMBOS = [
    # Group 1: Fw ↔ Bw
    ("Fw_Fw", 11), ("Fw_Bw", 15), ("Bw_Fw", 51), ("Bw_Bw", 55),
    # Group 2: Fw/Bw crossed with 70deg
    ("Fw_Fw70deg", 12), ("Fw_Bw70deg", 14),
    ("Fw70deg_Fw", 21), ("Fw70deg_Bw", 25),
    ("Bw70deg_Fw", 41), ("Bw70deg_Bw", 45),
    ("Bw_Fw70deg", 52), ("Bw_Bw70deg", 54),
    # Group 3: Fw70deg ↔ Bw70deg
    ("Fw70deg_Fw70deg", 22), ("Fw70deg_Bw70deg", 24),
    ("Bw70deg_Fw70deg", 42), ("Bw70deg_Bw70deg", 44),
    # Group 4: 90deg combinations
    ("Fw_90deg", 13), ("90deg_Fw", 31),
    ("Bw_90deg", 53), ("90deg_Bw", 35),
    ("Fw70deg_90deg", 23), ("90deg_Fw70deg", 32),
    ("Bw70deg_90deg", 43), ("90deg_Bw70deg", 34),
    ("90deg_90deg", 33),
]


class _CmatWorker(QThread):
    """Background thread that drives cmat interactively via pexpect.

    Loops over every subdirectory whose name starts with a digit (e.g. 13um,
    11_um, 45um).  In each one it looks for a matrix file matching
    ``Ge_Ge_pair_<dirname>.cmat`` or ``Ge_Ge_pairs_<dirname>.cmat``,
    opens it in cmat, runs the m2d extraction for the chosen ring-pair code,
    and writes the result next to the source matrix.
    """

    output = pyqtSignal(str)
    finished_signal = pyqtSignal(int, int)  # (success_count, fail_count)

    _DIR_RE = re.compile(r"^\d+")  # directory name must start with a digit

    def __init__(self, wd: str, label: str, code: int, parent=None):
        super().__init__(parent)
        self._wd = wd
        self._label = label
        self._code = code
        self._stopped = False

    def stop(self):
        self._stopped = True

    # ── helpers ──

    @staticmethod
    def _find_matrix(directory: Path) -> Path | None:
        """Return the Ge_Ge_pair(s)_<name>.cmat file, or None."""
        name = directory.name
        for pattern in (f"Ge_Ge_pair_{name}.cmat", f"Ge_Ge_pairs_{name}.cmat"):
            p = directory / pattern
            if p.exists():
                return p
        return None

    def _drive_cmat(self, cwd: Path, matrix_name: str, out_name: str):
        """Spawn cmat in *cwd*, open *matrix_name*, extract to *out_name*."""
        import pexpect

        code_str = str(self._code)
        child = pexpect.spawn(self._cmat_bin, args=[], timeout=120,
                              encoding="utf-8", cwd=str(cwd))
        try:
            child.expect("CMAT>")
            child.sendline(f"o {matrix_name}")
            child.expect("CMAT>")
            child.sendline("m2d")
            child.expect("Which indexes do you want to project")
            child.sendline("1 2")
            child.expect("Gates from file")
            child.sendline("N")
            child.expect("Low, High, Sign")
            child.sendline(f"{code_str} {code_str}")
            child.expect("Low, High, Sign")
            child.sendline("")
            child.expect("OK")
            child.sendline("Y")
            child.expect("Want to symmetrize the extracted matrix")
            child.sendline("N")
            child.expect("File_name of the extracted matrix")
            child.sendline(out_name)
            child.expect("CMAT>")
            child.sendline("q")
            child.expect(pexpect.EOF)
        finally:
            child.close()

    # ── main loop ──

    def run(self):
        # Resolve cmat binary — may not be on PATH inside the venv
        self._cmat_bin = shutil.which("cmat")
        if not self._cmat_bin:
            # Common GASPware install location
            candidate = Path.home() / "bin" / "GASPware" / "bin" / "cmat"
            if candidate.exists():
                self._cmat_bin = str(candidate)
        if not self._cmat_bin:
            self.output.emit(
                "ERROR: 'cmat' not found on PATH and not in "
                "~/bin/GASPware/bin/.\n"
            )
            self.finished_signal.emit(0, 0)
            return

        ok, fail = 0, 0
        wd = Path(self._wd)

        dirs = sorted(
            d for d in wd.iterdir()
            if d.is_dir() and self._DIR_RE.match(d.name)
        )

        if not dirs:
            self.output.emit("No subdirectories starting with a digit found.\n")
            self.finished_signal.emit(0, 0)
            return

        self.output.emit(f"Found {len(dirs)} directories to process.\n\n")

        for d in dirs:
            if self._stopped:
                self.output.emit("Stopped by user.\n")
                break

            mat = self._find_matrix(d)
            if mat is None:
                self.output.emit(
                    f"  Skipping {d.name}/ — no Ge_Ge_pair(s)_{d.name}.cmat\n"
                )
                continue

            out_name = f"{self._label}_{d.name}.cmat"
            self.output.emit(f"  {d.name}/  {mat.name} → {out_name} ... ")

            try:
                self._drive_cmat(d, mat.name, out_name)
                ok += 1
                self.output.emit("OK\n")
            except Exception as exc:
                fail += 1
                self.output.emit(f"FAILED ({exc})\n")

        self.finished_signal.emit(ok, fail)


class LauncherPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = None
        self._settings = load_settings()
        self._init_ui()
        self._refresh_dir_list()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        title = QLabel("Script Launcher")
        title.setProperty("heading", True)
        layout.addWidget(title)

        subtitle = QLabel(
            "Run experiment shell scripts (gsort, cmat, Autosort, etc.) "
            "from configured directories"
        )
        subtitle.setProperty("subheading", True)
        layout.addWidget(subtitle)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: directories + scripts ──
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Directory management
        dir_group = QGroupBox("Script Directories")
        dir_layout = QVBoxLayout(dir_group)

        self.dir_list = QListWidget()
        self.dir_list.currentRowChanged.connect(self._on_dir_selected)
        dir_layout.addWidget(self.dir_list)

        dir_btn_row = QHBoxLayout()
        add_dir_btn = QPushButton("Add Directory")
        add_dir_btn.setProperty("secondary", True)
        add_dir_btn.clicked.connect(self._add_directory)
        dir_btn_row.addWidget(add_dir_btn)

        remove_dir_btn = QPushButton("Remove")
        remove_dir_btn.setProperty("secondary", True)
        remove_dir_btn.clicked.connect(self._remove_directory)
        dir_btn_row.addWidget(remove_dir_btn)
        dir_btn_row.addStretch()
        dir_layout.addLayout(dir_btn_row)
        left_layout.addWidget(dir_group)

        # Scripts in selected directory
        script_group = QGroupBox("Scripts in Directory")
        script_layout = QVBoxLayout(script_group)

        self.script_list = QListWidget()
        self.script_list.itemDoubleClicked.connect(self._run_selected_script)
        script_layout.addWidget(self.script_list)
        left_layout.addWidget(script_group)

        splitter.addWidget(left)

        # ── Right: working dir + output ──
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Working directory override
        wd_group = QGroupBox("Working Directory (script runs here)")
        wd_layout = QHBoxLayout(wd_group)
        self.wd_edit = QLineEdit()
        self.wd_edit.setPlaceholderText("defaults to the script's directory")
        wd_layout.addWidget(self.wd_edit)
        wd_browse = QPushButton("Browse")
        wd_browse.setProperty("secondary", True)
        wd_browse.clicked.connect(self._browse_wd)
        wd_layout.addWidget(wd_browse)
        right_layout.addWidget(wd_group)

        # ── Matrix operations ──
        matrix_group = QGroupBox("ROSPHERE Matrix Operations")
        matrix_layout = QVBoxLayout(matrix_group)

        cut_row = QHBoxLayout()
        cut_row.addWidget(QLabel("Angle combination:"))
        self.ring_combo = QComboBox()
        for label, code in _RING_COMBOS:
            self.ring_combo.addItem(f"{label}  ({code})", code)
        self.ring_combo.setFixedWidth(220)
        cut_row.addWidget(self.ring_combo)

        cut_btn = QPushButton("Cut Matrices")
        cut_btn.clicked.connect(self._cut_matrices)
        cut_row.addWidget(cut_btn)
        cut_row.addStretch()
        matrix_layout.addLayout(cut_row)

        autosort_row = QHBoxLayout()
        autosort_btn = QPushButton("Run Autosort (all subdirs)")
        autosort_btn.setProperty("secondary", True)
        autosort_btn.clicked.connect(self._run_autosort)
        autosort_row.addWidget(autosort_btn)
        autosort_row.addStretch()
        matrix_layout.addLayout(autosort_row)

        right_layout.addWidget(matrix_group)

        # Run / Stop buttons
        btn_row = QHBoxLayout()
        run_btn = QPushButton("Run Script")
        run_btn.clicked.connect(self._run_selected_script)
        btn_row.addWidget(run_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setProperty("secondary", True)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_script)
        btn_row.addWidget(self.stop_btn)

        self.clear_btn = QPushButton("Clear Output")
        self.clear_btn.setProperty("secondary", True)
        self.clear_btn.clicked.connect(lambda: self.output_text.clear())
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()
        right_layout.addLayout(btn_row)

        # Terminal output
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(
            "QTextEdit {"
            "  background-color: #16161e;"
            "  color: #9ece6a;"
            "  font-family: 'Cascadia Mono', 'Fira Mono', monospace;"
            "  font-size: 12px;"
            "  border: 1px solid #292e42;"
            "  border-radius: 4px;"
            "  padding: 8px;"
            "}"
        )
        output_layout.addWidget(self.output_text)
        right_layout.addWidget(output_group, stretch=1)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter, stretch=1)

    # ── Directory management ──

    def _refresh_dir_list(self):
        self.dir_list.clear()
        for d in self._settings.get("script_directories", []):
            self.dir_list.addItem(d)

    def _add_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Select Script Directory")
        if not path:
            return
        dirs = self._settings.setdefault("script_directories", [])
        if path not in dirs:
            dirs.append(path)
            save_settings(self._settings)
            self._refresh_dir_list()

    def _remove_directory(self):
        row = self.dir_list.currentRow()
        if row < 0:
            return
        dirs = self._settings.get("script_directories", [])
        if 0 <= row < len(dirs):
            dirs.pop(row)
            save_settings(self._settings)
            self._refresh_dir_list()
            self.script_list.clear()

    def _on_dir_selected(self, row):
        """List scripts (.sh, .bash, .expect, executable files) in selected dir."""
        self.script_list.clear()
        dirs = self._settings.get("script_directories", [])
        if row < 0 or row >= len(dirs):
            return

        dir_path = Path(dirs[row])
        if not dir_path.exists():
            return

        # Also set working directory hint
        self.wd_edit.setPlaceholderText(str(dir_path))

        script_exts = {'.sh', '.bash', '.expect', '.tcl', '.py'}
        for entry in sorted(dir_path.iterdir()):
            if entry.is_file():
                if entry.suffix in script_exts or os.access(entry, os.X_OK):
                    item = QListWidgetItem(entry.name)
                    item.setData(Qt.ItemDataRole.UserRole, str(entry))
                    self.script_list.addItem(item)

    # ── Script execution ──

    def _run_selected_script(self):
        item = self.script_list.currentItem()
        if not item:
            QMessageBox.information(self, "Info", "Select a script to run.")
            return

        script_path = item.data(Qt.ItemDataRole.UserRole)
        if not script_path:
            return

        # Determine working directory
        wd = self.wd_edit.text().strip()
        if not wd:
            wd = str(Path(script_path).parent)

        self.output_text.clear()
        self._append_output(f"── Running: {script_path}\n── Working dir: {wd}\n{'─' * 50}\n")

        self._process = QProcess(self)
        self._process.setWorkingDirectory(wd)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)

        # Detect interpreter from shebang or extension
        ext = Path(script_path).suffix
        if ext in ('.expect', '.tcl'):
            self._process.start("expect", [script_path])
        elif ext == '.py':
            self._process.start("python3", [script_path])
        else:
            self._process.start("bash", [script_path])

        self.stop_btn.setEnabled(True)

    def _stop_script(self):
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            self._append_output("\n── Process terminated by user ──\n")
        if hasattr(self, "_cmat_worker") and self._cmat_worker.isRunning():
            self._cmat_worker.stop()
        self.stop_btn.setEnabled(False)

    def _on_stdout(self):
        data = self._process.readAllStandardOutput().data().decode(errors='replace')
        self._append_output(data)

    def _on_stderr(self):
        data = self._process.readAllStandardError().data().decode(errors='replace')
        self._append_output(data)

    def _on_finished(self, exit_code, exit_status):
        self._append_output(f"\n{'─' * 50}\n── Finished (exit code: {exit_code}) ──\n")
        self.stop_btn.setEnabled(False)

    def _append_output(self, text):
        self.output_text.moveCursor(self.output_text.textCursor().MoveOperation.End)
        self.output_text.insertPlainText(text)
        self.output_text.ensureCursorVisible()

    def _browse_wd(self):
        path = QFileDialog.getExistingDirectory(self, "Select Working Directory")
        if path:
            self.wd_edit.setText(path)

    # ── Matrix cutting ──

    def _get_working_dir(self) -> str | None:
        """Return the effective working directory, prompting if empty."""
        wd = self.wd_edit.text().strip()
        if not wd:
            wd = QFileDialog.getExistingDirectory(
                self, "Select matrices directory to work in"
            )
            if not wd:
                return None
            self.wd_edit.setText(wd)
        return wd

    def _cut_matrices(self):
        """Cut matrices for the selected ring pair using pexpect to drive cmat."""
        wd = self._get_working_dir()
        if not wd:
            return

        idx = self.ring_combo.currentIndex()
        label, code = _RING_COMBOS[idx]

        self.output_text.clear()
        self._append_output(
            f"── Cutting matrices: {label} (ring pair {code})\n"
            f"── Working dir: {wd}\n"
            f"{'─' * 50}\n"
        )

        self._cmat_worker = _CmatWorker(wd, label, code, parent=self)
        self._cmat_worker.output.connect(self._append_output)
        self._cmat_worker.finished_signal.connect(self._on_cmat_finished)
        self._cmat_worker.start()
        self.stop_btn.setEnabled(True)

    def _on_cmat_finished(self, ok: int, fail: int):
        self._append_output(
            f"{'─' * 50}\n"
            f"── Done: {ok} succeeded, {fail} failed ──\n"
        )
        self.stop_btn.setEnabled(False)

    # ── Autosort ──

    def _run_autosort(self):
        """Loop over all subdirectories and run ./Autosort in each."""
        wd = self._get_working_dir()
        if not wd:
            return

        # Check that subdirectories with Autosort exist
        wd_path = Path(wd)
        subdirs = sorted(
            d for d in wd_path.iterdir()
            if d.is_dir() and d.name != "TT" and (d / "Autosort").exists()
        )

        if not subdirs:
            QMessageBox.warning(
                self, "No Autosort found",
                f"No subdirectories with an 'Autosort' executable found in:\n{wd}",
            )
            return

        # Build a bash script that loops over subdirs
        script_lines = ["#!/bin/bash", "set -e"]
        for d in subdirs:
            script_lines.append(f'cd "{d}"')
            script_lines.append("./Autosort")
            script_lines.append(f'cd "{wd}"')
            script_lines.append(f'echo "Done: {d.name}"')
        script = "\n".join(script_lines) + "\n"

        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix="_autosort.sh",
            prefix="gna_", delete=False
        )
        tmp.write(script)
        tmp.close()
        os.chmod(tmp.name, 0o755)

        self.output_text.clear()
        self._append_output(
            f"── Running Autosort in {len(subdirs)} subdirectories\n"
            f"── Working dir: {wd}\n"
            f"{'─' * 50}\n"
        )

        self._process = QProcess(self)
        self._process.setWorkingDirectory(wd)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)
        self._process.start("bash", [tmp.name])
        self.stop_btn.setEnabled(True)
