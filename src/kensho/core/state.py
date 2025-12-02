import json
import os
from pathlib import Path
from typing import List, Dict, Any
from .models import ClockUnit

class AppState:
    def __init__(self):
        self.app_dir = Path.home() / ".kensho"
        self.state_file = self.app_dir / "state.json"
        self._ensure_dir()

    def _ensure_dir(self):
        if not self.app_dir.exists():
            self.app_dir.mkdir(parents=True)

    def load_state(self) -> List[Dict[str, Any]]:
        """Loads clock data from JSON file."""
        if not self.state_file.exists():
            return []
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                return data.get("clocks", [])
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading state: {e}")
            return []

    def save_state(self, clocks: List[ClockUnit]):
        """Saves clock data to JSON file."""
        data = {
            "clocks": [clock.to_dict() for clock in clocks]
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving state: {e}")

    def get_state_path(self) -> str:
        return str(self.state_file)
