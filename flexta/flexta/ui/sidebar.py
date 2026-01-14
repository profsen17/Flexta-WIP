from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from .dialogs.create_project_dialog import CreateProjectDialog


class Sidebar(QWidget):
    create_project_opened = Signal(CreateProjectDialog)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._create_project_dialog: Optional[CreateProjectDialog] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.create_project_button = QPushButton("Create Project")
        self.create_project_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.create_project_button.clicked.connect(self._open_create_project_dialog)
        layout.addWidget(self.create_project_button)
        layout.addStretch(1)

    def _open_create_project_dialog(self) -> None:
        dialog = CreateProjectDialog(self.window())
        dialog.open()
        self._create_project_dialog = dialog
        self.create_project_opened.emit(dialog)

    def current_dialog(self) -> Optional[CreateProjectDialog]:
        return self._create_project_dialog
