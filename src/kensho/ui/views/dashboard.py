import customtkinter as ctk
from typing import Dict, Any, List
from ...models import ClockUnit
from ..components.modern_clock_card import ModernClockCard

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_state: Dict[str, Any], on_save_state: Any):
        super().__init__(master, fg_color="transparent")
        self.app_state = app_state
        self.on_save_state = on_save_state
        self.clock_cards: List[ModernClockCard] = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self._load_clocks()

    def _load_clocks(self):
        saved_clocks = self.app_state.get("clocks", [])
        if not saved_clocks:
            # Default clock if none exist
            default_clock = ClockUnit(identifier="C1", label="Focus Session", interval_minutes=25)
            self._add_clock_card(default_clock)
        else:
            for payload in saved_clocks:
                clock = ClockUnit.from_dict(payload)
                self._add_clock_card(clock)

        # Add "New Clock" button at the end
        self._add_new_button()

    def _add_clock_card(self, clock: ClockUnit):
        card = ModernClockCard(self, clock, on_update=self._on_clock_update)
        self.clock_cards.append(card)
        self._layout_cards()

    def _add_new_button(self):
        self.add_btn = ctk.CTkButton(
            self, 
            text="+ Add Clock", 
            command=self._handle_add_clock,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            text_color=("gray10", "gray90"),
            height=50
        )
        # Layout happens in _layout_cards

    def _layout_cards(self):
        # Single column layout for compactness
        for idx, card in enumerate(self.clock_cards):
            card.grid(row=idx, column=0, padx=5, pady=5, sticky="nsew")
        
        # Place add button after last card
        if hasattr(self, 'add_btn'):
            idx = len(self.clock_cards)
            self.add_btn.grid(row=idx, column=0, padx=5, pady=5, sticky="nsew")

    def _handle_add_clock(self):
        if len(self.clock_cards) >= 6:
            return # Limit to 6 for now
        
        new_idx = len(self.clock_cards) + 1
        clock = ClockUnit(identifier=f"C{new_idx}", label="New Session", interval_minutes=15)
        self._add_clock_card(clock)
        self._save()

    def _on_clock_update(self):
        self._save()

    def _save(self):
        self.app_state["clocks"] = [c.clock.serialize() for c in self.clock_cards]
        self.on_save_state(self.app_state)
