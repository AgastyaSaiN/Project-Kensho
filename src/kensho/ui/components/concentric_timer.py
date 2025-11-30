import customtkinter as ctk
import math
import time
from typing import List, Optional, Callable
from ...models import ClockUnit

class ConcentricTimer(ctk.CTkCanvas):
    def __init__(
        self, 
        master, 
        clocks: List[ClockUnit],
        width: int = 200, 
        height: int = 200, 
        stroke_width: int = 8,
        gap: int = 5,
        on_click: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, width=width, height=height, highlightthickness=0, **kwargs)
        
        self.clocks = clocks
        self.stroke_width = stroke_width
        self.gap = gap
        self.on_click = on_click
        
        self.center_x = width // 2
        self.center_y = height // 2
        self.max_radius = (min(width, height) - stroke_width) // 2
        
        # Colors for different layers
        self.colors = ["#2cc985", "#3b8ed0", "#8b5cf6", "#f59e0b", "#ef4444", "#ec4899"]
        self.bg_color = "#2b2b2b"
        
        self._pulsing = False
        self._pulse_start_time = 0
        
        if self.on_click:
            self.bind("<Button-1>", lambda e: self.on_click())
        
        self._draw()
        self._start_animation()

    def update_state(self):
        """Called externally to refresh the view"""
        self._draw()

    def _start_animation(self):
        self._animate()

    def _animate(self):
        # We need continuous animation for pulsing
        self._draw()
        self.after(50, self._animate)

    def _draw(self):
        self.delete("all")
        
        # Pulse calculation
        t = time.time() * 2
        pulse_extra = (math.sin(t) + 1) * 1.5 # 0 to 3
        
        for i, clock in enumerate(self.clocks):
            # Outer to Inner
            radius = self.max_radius - (i * (self.stroke_width + self.gap))
            if radius <= 0:
                break
                
            color = self.colors[i % len(self.colors)]
            
            # Determine if this specific clock is active/pulsing
            is_active = not clock.paused and clock.elapsed_seconds > 0 and not clock.due
            
            current_width = self.stroke_width
            if is_active:
                current_width += pulse_extra
                
            # Background Ring
            self.create_oval(
                self.center_x - radius,
                self.center_y - radius,
                self.center_x + radius,
                self.center_y + radius,
                width=self.stroke_width, # Keep bg constant width
                outline=self.bg_color
            )
            
            # Progress Arc
            start_angle = 90
            extent = -360 * clock.progress_ratio()
            
            if clock.progress_ratio() > 0:
                self.create_arc(
                    self.center_x - radius,
                    self.center_y - radius,
                    self.center_x + radius,
                    self.center_y + radius,
                    start=start_angle,
                    extent=extent,
                    style="arc",
                    width=current_width,
                    outline=color if not clock.due else "#ef4444"
                )
