from __future__ import annotations

from pathlib import Path

from flexta.utils import validation


def test_is_empty_name_handles_blank_and_whitespace() -> None:
    assert validation.is_empty_name("")
    assert validation.is_empty_name("   ")
    assert not validation.is_empty_name("Project")


def test_is_invalid_path_rejects_missing_or_null_bytes() -> None:
    assert validation.is_invalid_path(None)
    assert validation.is_invalid_path("")
    assert validation.is_invalid_path(" \t")
    assert validation.is_invalid_path("bad\x00path")
    assert not validation.is_invalid_path("valid/path")


def test_does_folder_exist_checks_path(tmp_path: Path) -> None:
    existing = tmp_path / "existing"
    existing.mkdir()

    assert validation.does_folder_exist(existing)
    assert not validation.does_folder_exist(tmp_path / "missing")
    assert not validation.does_folder_exist("bad\x00path")
