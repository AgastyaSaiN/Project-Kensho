import json
import os
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any

class HistoryManager:
    def __init__(self):
        self.app_dir = Path.home() / ".kensho"
        self.history_file = self.app_dir / "history.json"
        self._ensure_dir()

    def _ensure_dir(self):
        if not self.app_dir.exists():
            self.app_dir.mkdir(parents=True)

    def log_session(self, clock_name: str, duration_minutes: float):
        """Logs a completed session."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "clock_name": clock_name,
            "duration_minutes": duration_minutes
        }
        
        history = self._load_history()
        history.append(record)
        self._save_history(history)

    def get_today_sessions(self) -> List[Dict[str, Any]]:
        """Returns sessions for the current date."""
        history = self._load_history()
        today_str = date.today().isoformat()
        return [r for r in history if r.get("date") == today_str]

    def get_total_time_today(self) -> float:
        """Returns total minutes focused today."""
        sessions = self.get_today_sessions()
        return sum(s.get("duration_minutes", 0) for s in sessions)

    def _load_history(self) -> List[Dict[str, Any]]:
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_history(self, history: List[Dict[str, Any]]):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=4)
        except IOError as e:
            print(f"Error saving history: {e}")

    def clear_history(self):
        """Clears all history data."""
        if self.history_file.exists():
            try:
                self.history_file.unlink()
            except IOError as e:
                print(f"Error clearing history: {e}")
