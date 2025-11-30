from PySide6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QGridLayout, 
                               QPushButton, QFrame)
from PySide6.QtCore import Qt
from ..core.models import ClockUnit
from .components.clock_card import ClockCard

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        # Container for Grid
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)
        
        # Add Button (Floating or Bottom?)
        # For now, let's put it at the bottom
        self.btn_add = QPushButton("+ Add Clock")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setFixedHeight(50)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                border: 2px dashed #444;
                border-radius: 10px;
                color: #888;
                font-size: 16px;
            }
            QPushButton:hover {
                border-color: #8b5cf6;
                color: #8b5cf6;
                background-color: #333;
            }
        """)
        self.btn_add.clicked.connect(self.add_clock)
        layout.addWidget(self.btn_add)
        
        # State
        self.clocks = []
        
        # Add initial clock
        self.add_clock()

    def add_clock(self):
        idx = len(self.clocks) + 1
        clock = ClockUnit(f"C{idx}", f"Session {idx}", 25)
        card = ClockCard(clock)
        
        # Grid Logic (2 columns?)
        row = (idx - 1) // 2
        col = (idx - 1) % 2
        
        self.grid_layout.addWidget(card, row, col)
        self.clocks.append(clock)
