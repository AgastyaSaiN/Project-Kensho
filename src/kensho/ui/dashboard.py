from PySide6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QGridLayout, 
                               QPushButton, QFrame, QMessageBox)
from PySide6.QtCore import Qt
from ..core.models import ClockUnit
from .components.clock_card import ClockCard

class DashboardView(QWidget):
    def __init__(self, clocks=None, parent=None):
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
        self.clocks = clocks if clocks is not None else []
        
        # Initial Render
        self.refresh_grid()

    def refresh_grid(self):
        # Clear existing items
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Rebuild Grid
        for i, clock in enumerate(self.clocks):
            card = ClockCard(clock)
            card.delete_requested.connect(self.remove_clock)
            
            row = i // 2
            col = i % 2
            self.grid_layout.addWidget(card, row, col)

    def add_clock(self, checked=False):
        idx = len(self.clocks) + 1
        new_clock = ClockUnit(f"C{idx}", f"Session {idx}", 25)
        self.clocks.append(new_clock)
        self.refresh_grid()

    def remove_clock(self, clock):
        reply = QMessageBox.question(
            self, 
            "Delete Clock", 
            f"Are you sure you want to delete '{clock.label}'?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if clock in self.clocks:
                self.clocks.remove(clock)
                self.refresh_grid()
