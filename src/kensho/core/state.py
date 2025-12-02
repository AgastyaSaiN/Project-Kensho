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

    def load_state(self) -> Dict[str, Any]:
        """Loads app state from JSON file."""
        if not self.state_file.exists():
            return {"clocks": [], "sound": "System Exclamation"}
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                # Ensure defaults
                if "sound" not in data:
                    data["sound"] = "System Exclamation"
                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading state: {e}")
            return {"clocks": [], "sound": "System Exclamation"}

    def save_state(self, clocks: List[ClockUnit], sound_preference: str):
        """Saves app state to JSON file."""
        data = {
            "clocks": [clock.to_dict() for clock in clocks],
            "sound": sound_preference
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving state: {e}")

    def get_state_path(self) -> str:
        return str(self.state_file)
