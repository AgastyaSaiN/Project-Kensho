from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PySide6.QtCore import Qt, Signal, QPoint, QTimer
from PySide6.QtGui import QColor
from typing import List
from ..core.models import ClockUnit
from .components.concentric_rings import ConcentricRings

class NotificationWindow(QWidget):
    def __init__(self, message: str, color: QColor, parent_pos: QPoint, parent_width: int, on_restart):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container for styling
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(20, 20, 20, 0.95);
                border: 1px solid {color.name()};
                border-radius: 8px;
            }}
            QLabel {{
                color: {color.name()};
                font-size: 14px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            QPushButton {{
                background-color: {color.name()};
                color: black;
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: white;
            }}
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(10)
        
        # Message
        self.label = QLabel(message)
        self.label.setWordWrap(True)
        container_layout.addWidget(self.label)
        
        # Restart Button (Symbol)
        self.btn_restart = QPushButton("↻")
        self.btn_restart.setCursor(Qt.PointingHandCursor)
        self.btn_restart.setToolTip("Restart Timer")
        
        # Callback wrapper
        def handle_click():
            on_restart()
            self.close()
            
        self.btn_restart.clicked.connect(handle_click)
        container_layout.addWidget(self.btn_restart, 0, Qt.AlignRight)
        
        layout.addWidget(container)
        
        # Position: Top-Right relative to parent widget
        self.move(parent_pos.x() + parent_width + 15, parent_pos.y())

from ..core.sound import SoundManager
from ..core.history import HistoryManager

class WidgetMode(QWidget):
    restore_requested = Signal()
    
    def __init__(self, clocks: List[ClockUnit], sound_preference: str = "System Exclamation"):
        super().__init__()
        self.sound_preference = sound_preference
        self.history_manager = HistoryManager()
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
        
        # Connect Clocks
        for i, clock in enumerate(clocks):
            # Use closure to capture index/clock
            clock.finished.connect(lambda c=clock, idx=i: self.show_notification(c, idx))
        
        # Initial position update
        self.update_button_positions()
        
        # Drag Logic
        self._drag_pos = QPoint()
        self._active_notifications = []

    def show_notification(self, clock, index):
        # Play Sound
        SoundManager.play_sound(self.sound_preference)
        
        # Log History
        self.history_manager.log_session(clock.label, clock._interval_minutes)
        
        # Get color from rings component
        colors = self.rings.colors
        color = colors[index % len(colors)]
        
        # Define restart callback
        def restart_clock():
            clock.reset()
            clock.start()

        # Spawn detached window
        notif = NotificationWindow(
            clock.completion_message, 
            color, 
            self.pos(), 
            self.width(),
            restart_clock
        )
        notif.show()
        
        # Keep reference to prevent GC
        self._active_notifications.append(notif)

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
