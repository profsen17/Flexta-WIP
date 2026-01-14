from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar, QWidget

from .dialogs.create_project_dialog import CreateProjectDialog


class AppToolBar(QToolBar):
    create_project_opened = Signal(CreateProjectDialog)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("main-toolbar")
        self._create_project_dialog: Optional[CreateProjectDialog] = None
        self._build_actions()

    def _build_actions(self) -> None:
        self.create_project_action = QAction("Create Project", self)
        self.create_project_action.triggered.connect(self._open_create_project_dialog)
        self.addAction(self.create_project_action)

    def _open_create_project_dialog(self) -> None:
        dialog = CreateProjectDialog(self.window())
        dialog.open()
        self._create_project_dialog = dialog
        self.create_project_opened.emit(dialog)

    def current_dialog(self) -> Optional[CreateProjectDialog]:
        return self._create_project_dialog
