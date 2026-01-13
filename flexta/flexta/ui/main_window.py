from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow

from .widgets.startup_widget import StartupWidget


class MainWindow(QMainWindow):
    create_project_requested = Signal()
    open_project_requested = Signal()
    template_selected = Signal(str)
    recent_project_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Flexta")

        self.startup_widget = StartupWidget(self)
        self.setCentralWidget(self.startup_widget)

        self.startup_widget.create_project_requested.connect(self.create_project_requested)
        self.startup_widget.open_project_requested.connect(self.open_project_requested)
        self.startup_widget.template_selected.connect(self.template_selected)
        self.startup_widget.recent_project_requested.connect(self.recent_project_requested)
