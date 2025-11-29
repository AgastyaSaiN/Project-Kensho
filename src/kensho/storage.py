"""Persistence helpers for Kenshō."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

APP_NAME = "Kensho"
APP_STATE_FILENAME = "app_state.json"


def _default_data_dir() -> Path:
    """Determine a writable directory for persisted data."""
    override = os.getenv("KENSHO_DATA_DIR")
    if override:
        return Path(override).expanduser()

    if sys.platform.startswith("win"):
        base = os.getenv("APPDATA") or os.getenv("LOCALAPPDATA")
        if base:
            return Path(base) / APP_NAME

    home = Path.home()
    return home / f".{APP_NAME.lower()}"


DATA_DIR = _default_data_dir()
APP_STATE_FILE = DATA_DIR / APP_STATE_FILENAME


def ensure_data_dir() -> None:
    """Make sure the data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_app_state() -> Dict[str, Any]:
    """Read persisted application state from disk."""
    ensure_data_dir()
    if not APP_STATE_FILE.exists():
        return {}

    try:
        with APP_STATE_FILE.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        # If the file is corrupted or unreadable we return a clean state
        return {}


def save_app_state(state: Dict[str, Any]) -> None:
    """Persist application state atomically."""
    ensure_data_dir()
    tmp_path = APP_STATE_FILE.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)
    tmp_path.replace(APP_STATE_FILE)


__all__ = [
    "APP_STATE_FILE",
    "DATA_DIR",
    "ensure_data_dir",
    "load_app_state",
    "save_app_state",
]
