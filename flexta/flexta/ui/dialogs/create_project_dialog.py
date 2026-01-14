from __future__ import annotations

from pathlib import Path
import shutil
from typing import Iterable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from flexta.database import settings_db
from flexta.utils.validation import does_folder_exist, is_empty_name, is_invalid_path


class CreateProjectDialog(QDialog):
    project_created = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create Project")
        self.setModal(True)
        self._templates_dir = Path(__file__).resolve().parents[2] / "resources" / "templates"
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Project name")
        form_layout.addRow("Name", self.name_input)

        directory_layout = QHBoxLayout()
        self.directory_input = QLineEdit()
        self.directory_input.setPlaceholderText("Project directory")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse_directory)
        directory_layout.addWidget(self.directory_input, 1)
        directory_layout.addWidget(browse_button)
        form_layout.addRow("Directory", directory_layout)

        self.template_picker = QComboBox()
        templates = list(self._load_templates())
        if templates:
            self.template_picker.addItems(templates)
        else:
            self.template_picker.addItem("default")
        form_layout.addRow("Template", self.template_picker)

        layout.addLayout(form_layout)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #c62828;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.error_label)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.create_button = QPushButton("Create")
        self.create_button.setDefault(True)
        self.create_button.clicked.connect(self._handle_create)
        button_box.addButton(self.create_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _browse_directory(self) -> None:
        start_dir = settings_db.get_last_used_folder()
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Project Directory",
            start_dir or "",
        )
        if directory:
            self.directory_input.setText(directory)
            settings_db.set_last_used_folder(directory)

    def _load_templates(self) -> Iterable[str]:
        if not self._templates_dir.exists():
            return []
        template_names: set[str] = set()
        for template_file in self._templates_dir.iterdir():
            if template_file.is_file() and template_file.suffix:
                template_names.add(template_file.stem.split(".")[0])
        return sorted(template_names)

    def _handle_create(self) -> None:
        name = self.name_input.text().strip()
        directory = self.directory_input.text().strip()
        if is_empty_name(name):
            self._set_error("Project name cannot be empty.")
            return
        if is_invalid_path(directory):
            self._set_error("Project directory is invalid.")
            return

        project_path = Path(directory).expanduser() / name
        if does_folder_exist(project_path):
            self._set_error("Project folder already exists.")
            return

        project_path.mkdir(parents=True, exist_ok=False)
        self._seed_project(project_path, self.template_picker.currentText())
        self.project_created.emit(str(project_path))
        settings_db.add_recent_project(str(project_path))
        settings_db.set_last_used_folder(str(project_path.parent))
        self.accept()

    def _seed_project(self, project_path: Path, template_name: str) -> None:
        if not self._templates_dir.exists():
            return
        template_files = list(self._templates_dir.glob(f"{template_name}.*"))
        if not template_files:
            template_files = list(self._templates_dir.glob("*.*"))
        for template_file in template_files:
            if template_file.is_file():
                destination = project_path / template_file.name
                shutil.copy2(template_file, destination)

    def _set_error(self, message: str) -> None:
        self.error_label.setText(message)
