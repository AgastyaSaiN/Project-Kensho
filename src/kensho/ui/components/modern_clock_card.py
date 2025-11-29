import customtkinter as ctk
from ...models import ClockUnit, SECONDS_PER_MINUTE
from typing import Callable
from .circular_timer import CircularTimer

class ModernClockCard(ctk.CTkFrame):
    def __init__(self, master, clock: ClockUnit, on_update: Callable[[], None]):
        super().__init__(master, corner_radius=15, fg_color="#1a1a1a") # Darker card bg
        self.clock = clock
        self.on_update = on_update
        
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.label_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Session",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            border_width=0,
            justify="center",
            height=24,
            text_color="#e0e0e0"
        )
        self.label_entry.insert(0, clock.label)
        self.label_entry.bind("<FocusOut>", self._update_label)
        self.label_entry.bind("<Return>", self._update_label)
        self.label_entry.grid(row=0, column=0, padx=5, pady=(8, 2), sticky="ew")

        # Circular Timer
        self.timer_canvas = CircularTimer(
            self, 
            width=140, 
            height=140, 
            stroke_width=8,
            initial_value=clock.progress_ratio(),
            on_change=self._on_drag_timer,
            bg="#1a1a1a" # Match card bg
        )
        self.timer_canvas.grid(row=1, column=0, pady=5)

        # Time Display (Overlay or below? Below for now)
        self.time_label = ctk.CTkLabel(
            self, 
            text=self._get_time_text(),
            font=ctk.CTkFont(size=20, family="monospace", weight="bold"),
            text_color="#ffffff"
        )
        # Place time inside the circle?
        # Let's try placing it below first for simplicity, or we can use place() to center it.
        # Using place relative to the canvas parent frame
        self.time_label.place(relx=0.5, rely=0.45, anchor="center")

        # Controls
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=2, column=0, pady=(10, 15))

        self.btn_toggle = ctk.CTkButton(
            self.controls_frame,
            text="Start" if not clock.paused and clock.elapsed_seconds == 0 else "Pause",
            width=60,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#2cc985", # Teal
            hover_color="#25a06a",
            command=self._toggle_timer
        )
        self.btn_toggle.pack(side="left", padx=3)

        self.btn_reset = ctk.CTkButton(
            self.controls_frame,
            text="Reset",
            width=60,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            border_width=1,
            border_color="#555555",
            command=self._reset_timer
        )
        self.btn_reset.pack(side="left", padx=3)
        
        self._update_ui_state()

    def _update_label(self, event=None):
        self.clock.label = self.label_entry.get()
        self.on_update()
        self.focus()

    def _toggle_timer(self):
        self.clock.toggle_pause()
        self._update_ui_state()
        self.on_update()

    def _reset_timer(self):
        self.clock.reset()
        self.timer_canvas.set_value(0.0)
        self._update_ui_state()
        self.on_update()

    def _on_drag_timer(self, value: float):
        # When dragging, we are setting the ELAPSED time or the INTERVAL?
        # Usually dragging a timer sets the DURATION (Interval).
        # But here we are visualizing progress.
        # Let's say dragging sets the progress (elapsed).
        
        # Actually, for a "timer", dragging usually sets the target time if it's a countdown.
        # But our model is "elapsed / interval".
        # Let's map drag to "Elapsed Time" for now to allow scrubbing.
        
        total_seconds = self.clock.interval_minutes * SECONDS_PER_MINUTE
        self.clock.elapsed_seconds = total_seconds * value
        self.clock.due = self.clock.elapsed_seconds >= total_seconds
        
        self.time_label.configure(text=self._get_time_text())
        # Don't trigger save on every drag event to avoid IO spam, 
        # but we should probably trigger it on release. 
        # For now, just update local state.

    def _get_time_text(self) -> str:
        remaining = self.clock.remaining_seconds()
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_state(self):
        """Called by parent loop to refresh UI based on model state"""
        self.timer_canvas.set_value(self.clock.progress_ratio())
        self.time_label.configure(text=self._get_time_text())
        self._update_ui_state()

    def _update_ui_state(self):
        # Update button text
        if self.clock.paused:
             self.btn_toggle.configure(text="Resume")
        elif self.clock.elapsed_seconds == 0:
             self.btn_toggle.configure(text="Start")
        else:
             self.btn_toggle.configure(text="Pause")
             
        # Update colors based on state
        if self.clock.due:
            self.timer_canvas.fg_color = "#ef4444" # Red
        else:
            self.timer_canvas.fg_color = "#2cc985" # Teal

