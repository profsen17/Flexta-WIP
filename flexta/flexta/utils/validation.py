from __future__ import annotations

from pathlib import Path
from typing import Union


PathLike = Union[str, Path]


def is_empty_name(name: str) -> bool:
    return not name or not name.strip()


def is_invalid_path(path_value: PathLike) -> bool:
    if path_value is None:
        return True
    path_text = str(path_value).strip()
    if not path_text:
        return True
    if "\x00" in path_text:
        return True
    try:
        Path(path_text).expanduser()
    except (TypeError, ValueError, OSError):
        return True
    return False


def does_folder_exist(path_value: PathLike) -> bool:
    try:
        return Path(path_value).expanduser().exists()
    except (TypeError, ValueError, OSError):
        return False
