from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from flexta.ui.widgets import StartupWidget


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Flexta")
        self.geometry("720x480")
        self.minsize(640, 420)

        self._configure_style()
        self._build()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

    def _build(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

        startup = StartupWidget(container)
        startup.pack(fill="both", expand=True)
