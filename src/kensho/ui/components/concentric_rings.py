from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QPen, QColor, QConicalGradient, QBrush
from typing import List
from ...core.models import ClockUnit
import math

class ConcentricRings(QWidget):
    def __init__(self, clocks: List[ClockUnit], parent=None):
        super().__init__(parent)
        self.clocks = clocks
        self.setMinimumSize(50, 50)
        
        # Pulse Property
        self._pulse_factor = 0.0
        
        # Animation
        self.anim = QPropertyAnimation(self, b"pulse_factor")
        self.anim.setDuration(2000) # 2 seconds per breath
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setLoopCount(-1) # Infinite
        self.anim.setEasingCurve(QEasingCurve.InOutSine)
        self.anim.start()
        
        # Update Timer (for progress)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16) # 60 FPS
        
        # Colors
        self.colors = [
            QColor("#2cc985"), # Teal
            QColor("#3b8ed0"), # Blue
            QColor("#8b5cf6"), # Purple
            QColor("#f59e0b"), # Amber
            QColor("#ef4444"), # Red
            QColor("#ec4899")  # Pink
        ]
        self.bg_color = QColor("#2b2b2b")

    def get_pulse_factor(self):
        return self._pulse_factor

    def set_pulse_factor(self, value):
        self._pulse_factor = value
        self.update()

    pulse_factor = Property(float, get_pulse_factor, set_pulse_factor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        min_dim = min(width, height)
        stroke_width = 8
        gap = 5
        max_radius = (min_dim - stroke_width) / 2
        
        for i, clock in enumerate(self.clocks):
            radius = max_radius - (i * (stroke_width + gap))
            if radius <= 0: break
            
            color = self.colors[i % len(self.colors)]
            
            # Draw Background Ring
            pen = QPen(self.bg_color)
            pen.setWidth(stroke_width)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawEllipse(
                center_x - radius, 
                center_y - radius, 
                radius * 2, 
                radius * 2
            )
            
            # Draw Progress Arc
            progress = clock.progress
            if progress > 0:
                pen.setColor(color)
                
                # Pulse Effect (Thicken line if active)
                if not clock._paused and not clock._due:
                    # Use animated property
                    # Oscillate between 0 and 3px extra width
                    # pulse_factor goes 0->1. We want 0->1->0? 
                    # Or InOutSine handles the ease, but we need to map 0-1 to width.
                    # Let's say we want it to breathe in and out.
                    # If anim is 0->1, we can map it directly.
                    # But for breathing we usually want 0->1->0.
                    # Let's use sin of the factor? Or just configure animation to reverse?
                    # For now, let's map 0..1 to a sine wave shape here or just use it directly.
                    # If we use KeyValueAt in animation it's better.
                    # But simple approach:
                    pulse = self._pulse_factor * 3.0
                    if self.anim.direction() == QPropertyAnimation.Forward:
                         # We need it to go back down.
                         # Actually, let's just use sin(factor * pi)
                         pulse = math.sin(self._pulse_factor * math.pi) * 3.0
                    
                    pen.setWidthF(stroke_width + pulse)
                else:
                    pen.setWidth(stroke_width)

                painter.setPen(pen)
                
                # Qt draws arcs in 1/16th of a degree
                # 0 is 3 o'clock. We want 12 o'clock (90 deg)
                start_angle = 90 * 16
                span_angle = -360 * progress * 16
                
                rect = QRectF(
                    center_x - radius, 
                    center_y - radius, 
                    radius * 2, 
                    radius * 2
                )
                painter.drawArc(rect, start_angle, span_angle)
