from __future__ import annotations

import os

from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication

from flexta.ui.main_window import MainWindow
from flexta.ui.sidebar import Sidebar
from flexta.ui.toolbar import AppToolBar
from flexta.ui.widgets.startup_widget import StartupWidget


def _get_app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_welcome_view_first_and_dialog_opens() -> None:
    app = _get_app()

    window = MainWindow()
    toolbar = AppToolBar(window)
    sidebar = Sidebar(window)

    window.addToolBar(toolbar)
    sidebar.setParent(window)
    window.show()
    app.processEvents()

    assert isinstance(window.centralWidget(), StartupWidget)

    toolbar_spy = QSignalSpy(toolbar.create_project_opened)
    toolbar.create_project_action.trigger()
    app.processEvents()
    assert len(toolbar_spy) == 1
    toolbar_dialog = toolbar.current_dialog()
    assert toolbar_dialog is not None
    assert toolbar_dialog.isVisible()
    toolbar_dialog.close()

    sidebar_spy = QSignalSpy(sidebar.create_project_opened)
    sidebar.create_project_button.click()
    app.processEvents()
    assert len(sidebar_spy) == 1
    sidebar_dialog = sidebar.current_dialog()
    assert sidebar_dialog is not None
    assert sidebar_dialog.isVisible()
    sidebar_dialog.close()

    window.close()
