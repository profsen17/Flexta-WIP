from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Iterable, Optional


_DB_FILENAME = "settings.db"
_SETTINGS_DIRNAME = ".flexta"


def _get_db_path() -> Path:
    settings_dir = Path.home() / _SETTINGS_DIRNAME
    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir / _DB_FILENAME


def _get_schema_path() -> Path:
    return Path(__file__).resolve().with_name("schema.sql")


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(_get_db_path())
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db() -> None:
    schema_path = _get_schema_path()
    schema = schema_path.read_text(encoding="utf-8")
    with _connect() as connection:
        connection.executescript(schema)


def add_recent_project(path: str) -> None:
    initialize_db()
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO recent_projects (path, last_opened)
            VALUES (?, CURRENT_TIMESTAMP)
            ON CONFLICT(path) DO UPDATE SET last_opened = CURRENT_TIMESTAMP
            """,
            (path,),
        )


def get_recent_projects(limit: int = 10) -> list[str]:
    initialize_db()
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT path
            FROM recent_projects
            ORDER BY last_opened DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [row["path"] for row in rows]


def set_last_used_folder(folder: str) -> None:
    initialize_db()
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO settings (key, value)
            VALUES ('last_used_folder', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (folder,),
        )


def get_last_used_folder() -> Optional[str]:
    initialize_db()
    with _connect() as connection:
        row = connection.execute(
            "SELECT value FROM settings WHERE key = 'last_used_folder'"
        ).fetchone()
    if row is None:
        return None
    return row["value"]


def set_recent_projects(projects: Iterable[str]) -> None:
    initialize_db()
    with _connect() as connection:
        connection.execute("DELETE FROM recent_projects")
        connection.executemany(
            """
            INSERT INTO recent_projects (path, last_opened)
            VALUES (?, CURRENT_TIMESTAMP)
            ON CONFLICT(path) DO UPDATE SET last_opened = CURRENT_TIMESTAMP
            """,
            [(project,) for project in projects],
        )
