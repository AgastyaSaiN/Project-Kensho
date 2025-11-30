from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, QPoint
from typing import List
from ..core.models import ClockUnit
from .components.concentric_rings import ConcentricRings

class WidgetMode(QWidget):
    restore_requested = Signal()
    
    def __init__(self, clocks: List[ClockUnit]):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(220, 220)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Concentric Rings
        self.rings = ConcentricRings(clocks)
        self.layout.addWidget(self.rings)
        
        # Resize Controls (Top Right)
        self.btn_plus = QPushButton("+", self)
        self.btn_plus.setCursor(Qt.PointingHandCursor)
        self.btn_plus.resize(24, 24)
        self.btn_plus.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.btn_plus.clicked.connect(lambda: self.scale_window(20))
        
        self.btn_minus = QPushButton("-", self)
        self.btn_minus.setCursor(Qt.PointingHandCursor)
        self.btn_minus.resize(24, 24)
        self.btn_minus.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.btn_minus.clicked.connect(lambda: self.scale_window(-20))
        
        # Initial position update
        self.update_button_positions()
        
        # Drag Logic
        self._drag_pos = QPoint()

    def resizeEvent(self, event):
        self.update_button_positions()
        super().resizeEvent(event)

    def update_button_positions(self):
        # Top right corner, with some padding
        m = 10
        s = 24
        self.btn_plus.move(self.width() - s - m, m)
        self.btn_minus.move(self.width() - (s * 2) - m - 5, m)

    def scale_window(self, delta):
        new_size = max(80, min(600, self.width() + delta))
        self.resize(new_size, new_size)

        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self._is_dragging = False
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self._is_dragging = True
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self._is_dragging:
                # Only restore if it was a click, not a drag
                self.restore_requested.emit()
            self._is_dragging = False
            event.accept()
            
    # Optional: Right click menu to pause/reset?
