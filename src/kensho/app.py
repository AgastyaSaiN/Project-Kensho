"""Main application bootstrap for Kenshō."""

from __future__ import annotations

import tkinter as tk
from typing import Dict, List, Optional, Any

from .models import ClockUnit, SECONDS_PER_MINUTE
from .notifications import notify_clock_due
from .storage import load_app_state, save_app_state
from .ui.main_window import MainWindow

TICK_INTERVAL_MS = 250

class KenshoApp:
    """Application controller."""

    def __init__(self) -> None:
        self.state: Dict[str, Any] = load_app_state()
        
        # Initialize Main Window
        self.window = MainWindow(self.state, self._save_state)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self._ticker_job: Optional[str] = None
        self._start_ticker()

    def _save_state(self, new_state: Dict[str, Any]):
        self.state = new_state
        save_app_state(self.state)

    def on_close(self) -> None:
        """Persist window state and destroy the root window."""
        self._save_state(self.state)
        self.window.destroy()

    def run(self) -> None:
        """Start the main loop."""
        self.window.mainloop()

    # --- Timer loop -------------------------------------------------------

    def _start_ticker(self) -> None:
        self._ticker_job = self.window.after(TICK_INTERVAL_MS, self._on_tick)

    def _on_tick(self) -> None:
        delta_seconds = TICK_INTERVAL_MS / 1000.0
        
        # Access clocks from the dashboard view if available
        if hasattr(self.window, 'dashboard_view'):
            cards = self.window.dashboard_view.clock_cards
            for card in cards:
                clock = card.clock
                clock.ensure_today()
                
                if not clock.due:
                    completed = clock.tick(delta_seconds)
                    if completed:
                        clock.paused = True
                        notify_clock_due(clock.label, clock.sound_id)
                
                # Update UI component
                card.update_state()

        self._ticker_job = self.window.after(TICK_INTERVAL_MS, self._on_tick)

def main() -> None:
    app = KenshoApp()
    app.run()

if __name__ == "__main__":
    main()
