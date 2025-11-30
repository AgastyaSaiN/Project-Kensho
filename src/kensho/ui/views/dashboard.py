import customtkinter as ctk
from typing import Dict, Any, List, Callable
from ...models import ClockUnit
from ..components.modern_clock_card import ModernClockCard

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_state: Dict[str, Any], on_save_state: Any, on_focus_mode: Callable[[], None]):
        super().__init__(master, fg_color="transparent")
        self.app_state = app_state
        self.on_save_state = on_save_state
        self.on_focus_mode = on_focus_mode
        self.clock_cards: List[ModernClockCard] = []
        self.is_compact = False
        
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
        # Container for actions
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=999, column=0, pady=20, sticky="ew")
        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid_columnconfigure(1, weight=1)

        self.add_btn = ctk.CTkButton(
            self.actions_frame, 
            text="+ Add Clock", 
            command=self._handle_add_clock,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            text_color=("gray10", "gray90"),
            height=40
        )
        self.add_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.kensho_btn = ctk.CTkButton(
            self.actions_frame,
            text="Enter Kenshō",
            command=self.on_focus_mode,
            fg_color="#8b5cf6", # Purple accent
            hover_color="#7c3aed",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.kensho_btn.grid(row=0, column=1, padx=5, sticky="ew")

        self._layout_cards()

    def _layout_cards(self):
        # Single column layout for compactness
        for idx, card in enumerate(self.clock_cards):
            card.grid(row=idx, column=0, padx=5, pady=5, sticky="nsew")
            
            # In compact mode, only show the first card? 
            # Or just let them scroll. Scrolling is fine.
            if self.is_compact and idx > 0:
                card.grid_remove()
            else:
                card.grid()
        
        # Place actions frame after last card
        if hasattr(self, 'actions_frame'):
            if self.is_compact:
                self.actions_frame.grid_remove()
            else:
                idx = len(self.clock_cards)
                self.actions_frame.grid(row=idx, column=0, padx=5, pady=10, sticky="ew")

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

    def set_compact(self, compact: bool):
        self.is_compact = compact
        
        if compact:
            # Hide all cards
            for card in self.clock_cards:
                card.grid_remove()
            if hasattr(self, 'add_btn'):
                self.add_btn.grid_remove()
                
            # Show Concentric Timer
            if not hasattr(self, 'concentric_timer'):
                from ..components.concentric_timer import ConcentricTimer
                # Extract ClockUnit objects
                clocks = [c.clock for c in self.clock_cards]
                self.concentric_timer = ConcentricTimer(
                    self, 
                    clocks=clocks,
                    width=200,
                    height=200,
                    bg="#2b2b2b", # Canvas doesn't support 'transparent', use dark bg
                    on_click=self.on_focus_mode # Click to toggle back
                )
            else:
                # Update clocks list in case it changed
                self.concentric_timer.clocks = [c.clock for c in self.clock_cards]
                # Ensure callback is set
                self.concentric_timer.on_click = self.on_focus_mode
                
            self.concentric_timer.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            
        else:
            # Hide Concentric Timer
            if hasattr(self, 'concentric_timer'):
                self.concentric_timer.grid_remove()
                
            # Show cards
            self._layout_cards()
