from __future__ import annotations

from typing import Iterable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from flexta.database import settings_db

class StartupWidget(QWidget):
    create_project_requested = Signal()
    open_project_requested = Signal()
    template_selected = Signal(str)
    recent_project_requested = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None, show_open_button: bool = True) -> None:
        super().__init__(parent)
        self._show_open_button = show_open_button
        self._recent_placeholder = QListWidgetItem("No recent projects")
        self._build_ui()
        self.refresh_recent_projects()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        title = QLabel("Welcome to Flexta")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setStyleSheet("font-size: 28px; font-weight: 600;")
        layout.addWidget(title)

        actions_layout = QHBoxLayout()
        self.create_button = QPushButton("Create Project")
        self.create_button.clicked.connect(self.create_project_requested)
        self.create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        actions_layout.addWidget(self.create_button)

        if self._show_open_button:
            self.open_button = QPushButton("Open Project")
            self.open_button.clicked.connect(self.open_project_requested)
            self.open_button.setCursor(Qt.CursorShape.PointingHandCursor)
            actions_layout.addWidget(self.open_button)

        actions_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(actions_layout)

        template_group = QGroupBox("Template")
        template_layout = QHBoxLayout(template_group)
        template_layout.setContentsMargins(16, 12, 16, 12)
        template_label = QLabel("Choose a template:")
        self.template_picker = QComboBox()
        self.template_picker.addItems(["Blank", "Web App", "CLI Tool", "Library"])
        self.template_picker.currentTextChanged.connect(self.template_selected)
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_picker, 1)
        layout.addWidget(template_group)

        recent_group = QGroupBox("Recent Projects")
        recent_layout = QVBoxLayout(recent_group)
        recent_layout.setContentsMargins(16, 12, 16, 12)
        self.recent_list = QListWidget()
        self.recent_list.itemActivated.connect(self._handle_recent_activation)
        self.recent_list.addItem(self._recent_placeholder)
        self._recent_placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
        recent_layout.addWidget(self.recent_list)
        layout.addWidget(recent_group, 1)

    def set_templates(self, templates: Iterable[str]) -> None:
        self.template_picker.clear()
        self.template_picker.addItems(list(templates))
        if self.template_picker.count() > 0:
            self.template_selected.emit(self.template_picker.currentText())

    def set_recent_projects(self, projects: Iterable[str]) -> None:
        self.recent_list.clear()
        project_list = list(projects)
        if not project_list:
            self.recent_list.addItem(self._recent_placeholder)
            self._recent_placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            return

        for project in project_list:
            item = QListWidgetItem(project)
            item.setToolTip(project)
            self.recent_list.addItem(item)

    def refresh_recent_projects(self) -> None:
        self.set_recent_projects(settings_db.get_recent_projects())

    def record_recent_project(self, project_path: str) -> None:
        settings_db.add_recent_project(project_path)
        self.refresh_recent_projects()

    def _handle_recent_activation(self, item: QListWidgetItem) -> None:
        if item.flags() == Qt.ItemFlag.NoItemFlags:
            return
        self.record_recent_project(item.text())
        self.recent_project_requested.emit(item.text())
