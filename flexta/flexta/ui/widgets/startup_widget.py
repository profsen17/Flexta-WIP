from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from flexta.utils.file_utils import create_project


class StartupWidget(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=24)
        self.project_name_var = tk.StringVar()
        self.location_var = tk.StringVar(value="~/flexta-projects")
        self.status_var = tk.StringVar()

        self._build()

    def _build(self) -> None:
        title = ttk.Label(self, text="Start a new project", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w")

        subtitle = ttk.Label(
            self,
            text="Create a simple HTML/CSS/JS project to get started with Flexta.",
            foreground="#6b7280",
        )
        subtitle.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 16))

        name_label = ttk.Label(self, text="Project name")
        name_label.grid(row=2, column=0, sticky="w")
        name_entry = ttk.Entry(self, textvariable=self.project_name_var, width=40)
        name_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 12))

        location_label = ttk.Label(self, text="Location")
        location_label.grid(row=4, column=0, sticky="w")
        location_entry = ttk.Entry(self, textvariable=self.location_var, width=40)
        location_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(4, 12))

        create_button = ttk.Button(self, text="Create project", command=self._handle_create)
        create_button.grid(row=6, column=0, sticky="w")

        status_label = ttk.Label(self, textvariable=self.status_var, foreground="#ef4444")
        status_label.grid(row=7, column=0, columnspan=2, sticky="w", pady=(12, 0))

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        name_entry.focus()

    def _handle_create(self) -> None:
        self.status_var.set("")
        try:
            result = create_project(
                project_name=self.project_name_var.get(),
                base_path=self.location_var.get(),
            )
        except ValueError as exc:
            self.status_var.set(str(exc))
            return

        self.status_var.set(f"Project created at: {result.path}")
