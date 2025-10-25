"""Persistence helpers for Kenshō."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

# Directory paths
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
APP_STATE_FILE = DATA_DIR / "app_state.json"


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
