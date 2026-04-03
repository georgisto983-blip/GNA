"""Script Launcher panel — browse directories, select and run scripts."""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit,
    QFileDialog, QMessageBox, QLineEdit, QSplitter,
)
from PyQt6.QtCore import QProcess, Qt
from app.config import load_settings, save_settings


class LauncherPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = None
        self._settings = load_settings()
        self._init_ui()
        self._refresh_dir_list()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
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
