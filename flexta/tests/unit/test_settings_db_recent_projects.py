from __future__ import annotations

import time
from pathlib import Path

from flexta.database import settings_db


def _isolate_settings_db(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "settings.db"
    monkeypatch.setattr(settings_db, "_get_db_path", lambda: db_path)


def test_add_recent_project_persists_and_orders(tmp_path: Path, monkeypatch) -> None:
    _isolate_settings_db(tmp_path, monkeypatch)

    settings_db.add_recent_project("/tmp/project-alpha")
    time.sleep(1)
    settings_db.add_recent_project("/tmp/project-bravo")

    recent = settings_db.get_recent_projects()
    assert recent[0] == "/tmp/project-bravo"
    assert recent[1] == "/tmp/project-alpha"


def test_set_recent_projects_overwrites_previous(tmp_path: Path, monkeypatch) -> None:
    _isolate_settings_db(tmp_path, monkeypatch)

    settings_db.add_recent_project("/tmp/project-old")
    settings_db.set_recent_projects(["/tmp/project-new", "/tmp/project-next"])

    recent = settings_db.get_recent_projects()
    assert set(recent) == {"/tmp/project-new", "/tmp/project-next"}
