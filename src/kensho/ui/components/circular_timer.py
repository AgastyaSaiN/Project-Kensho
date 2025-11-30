import customtkinter as ctk
import math
from typing import Callable, Optional

class CircularTimer(ctk.CTkCanvas):
    def __init__(
        self, 
        master, 
        width: int = 200, 
        height: int = 200, 
        stroke_width: int = 10,
        initial_value: float = 0.0, # 0.0 to 1.0
        on_change: Optional[Callable[[float], None]] = None,
        **kwargs
    ):
        super().__init__(master, width=width, height=height, highlightthickness=0, **kwargs)
        
        self.stroke_width = stroke_width
        self.on_change = on_change
        self._value = initial_value
        self._is_dragging = False
        self._pulsing = False
        self._current_stroke_width = stroke_width
        
        # Colors (can be made configurable)
        self.bg_color = "#2b2b2b" # Track color
        self.fg_color = "#2cc985" # Active color (Teal)
        self.handle_color = "#ffffff"
        
        # Geometry
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = (min(width, height) - stroke_width * 3) // 2
        
        # Bindings
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        
        self._draw()

    def set_value(self, value: float):
        """Set progress from 0.0 to 1.0"""
        if self._is_dragging:
            return # Don't overwrite while user is interacting
        self._value = max(0.0, min(1.0, value))
        self._draw()

    def get_value(self) -> float:
        return self._value

    def _draw(self):
        self.delete("all")
        
        # Background Ring
        self.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            width=self.stroke_width,
            outline=self.bg_color
        )
        
        # Progress Arc
        # Tkinter arc starts at 3 o'clock (0 degrees) and goes counter-clockwise
        # We want to start at 12 o'clock (90 degrees) and go clockwise (negative extent)
        start_angle = 90
        extent = -360 * self._value
        
        if self._value > 0:
            self.create_arc(
                self.center_x - self.radius,
                self.center_y - self.radius,
                self.center_x + self.radius,
                self.center_y + self.radius,
                start=start_angle,
                extent=extent,
                style="arc",
                width=self.stroke_width,
                outline=self.fg_color
            )
            
        # Handle (Knob)
        # Calculate position
        angle_rad = math.radians(start_angle + extent)
        handle_x = self.center_x + self.radius * math.cos(angle_rad)
        handle_y = self.center_y - self.radius * math.sin(angle_rad) # Y is inverted in screen coords
        
        r_handle = self.stroke_width
        self.create_oval(
            handle_x - r_handle,
            handle_y - r_handle,
            handle_x + r_handle,
            handle_y + r_handle,
            fill=self.handle_color,
            outline=""
        )

    def _on_click(self, event):
        self._update_from_event(event)
        self._is_dragging = True

    def _on_drag(self, event):
        self._update_from_event(event)

    def _on_release(self, event):
        self._is_dragging = False

    def _update_from_event(self, event):
        # Calculate angle from center to mouse
        dx = event.x - self.center_x
        dy = self.center_y - event.y # Invert Y to match Cartesian
        
        # Atan2 returns -pi to pi. 0 is 3 o'clock.
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # Convert to 0-360 starting at 12 o'clock clockwise
        # 12 o'clock is 90 degrees in Cartesian
        # We want 12=0.0, 3=0.25, 6=0.5, 9=0.75
        
        # Cartesian: 90=12, 0=3, -90=6, 180/-180=9
        # Map:
        # 90 -> 0
        # 0 -> 90
        # -90 -> 180
        # 180 -> 270
        
        mapped_angle = (90 - angle_deg) % 360
        value = mapped_angle / 360.0
        
        self._value = value
        self._draw()
        
        if self.on_change:
            self.on_change(value)

    def start_pulse(self):
        if not self._pulsing:
            self._pulsing = True
            self._pulse_start_time = 0
            self._animate_pulse()

    def stop_pulse(self):
        self._pulsing = False
        # Reset stroke width
        self._draw()

    def _animate_pulse(self):
        if not self._pulsing:
            return
            
        # Simple sine wave breathing
        import time
        import math
        
        t = time.time() * 2 # Speed
        # Oscillate stroke width between base and base+4
        base_width = self.stroke_width
        extra = (math.sin(t) + 1) * 2 # 0 to 4
        
        current_width = base_width + extra
        
        # Redraw only the arc with new width? 
        # Full redraw is safer for now to keep handles aligned, 
        # though slightly more expensive.
        
        # We can optimize by just updating the arc coords/width if we saved the item ID.
        # But _draw() is fast enough for this simple shape.
        
        # We need to pass the dynamic width to _draw, or set a temporary property.
        self._current_stroke_width = current_width
        self._draw(pulse_width=current_width)
        
        self.after(50, self._animate_pulse)

    def _draw(self, pulse_width=None):
        self.delete("all")
        
        width_to_use = pulse_width if pulse_width is not None else self.stroke_width
        
        # Background Ring
        self.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            width=self.stroke_width, # Background stays constant? Or pulses too? Let's keep bg constant.
            outline=self.bg_color
        )
        
        # Progress Arc
        start_angle = 90
        extent = -360 * self._value
        
        if self._value > 0:
            self.create_arc(
                self.center_x - self.radius,
                self.center_y - self.radius,
                self.center_x + self.radius,
                self.center_y + self.radius,
                start=start_angle,
                extent=extent,
                style="arc",
                width=width_to_use,
                outline=self.fg_color
            )
            
        # Handle (Knob)
        angle_rad = math.radians(start_angle + extent)
        handle_x = self.center_x + self.radius * math.cos(angle_rad)
        handle_y = self.center_y - self.radius * math.sin(angle_rad)
        
        r_handle = width_to_use # Handle grows with pulse
        self.create_oval(
            handle_x - r_handle/2, # Adjust radius
            handle_y - r_handle/2,
            handle_x + r_handle/2,
            handle_y + r_handle/2,
            fill=self.handle_color,
            outline=""
        )
