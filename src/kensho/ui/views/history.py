from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, 
                               QFrame, QHBoxLayout)
from PySide6.QtCore import Qt, QTimer
from datetime import datetime
from ..core.history import HistoryManager

class HistoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_manager = HistoryManager()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)
        
        # Header
        title = QLabel("History")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Stats Card
        self.stats_card = QFrame()
        self.stats_card.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                color: white;
            }
        """)
        stats_layout = QVBoxLayout(self.stats_card)
        
        lbl_today = QLabel("Today's Focus")
        lbl_today.setStyleSheet("font-size: 14px; color: #888;")
        stats_layout.addWidget(lbl_today)
        
        self.lbl_total_time = QLabel("0h 0m")
        self.lbl_total_time.setStyleSheet("font-size: 36px; font-weight: bold; color: #8b5cf6;")
        stats_layout.addWidget(self.lbl_total_time)
        
        layout.addWidget(self.stats_card)
        
        # Sessions List Header
        lbl_sessions = QLabel("Completed Sessions")
        lbl_sessions.setStyleSheet("font-size: 18px; font-weight: bold; color: #ddd; margin-top: 20px;")
        layout.addWidget(lbl_sessions)
        
        # Scroll Area for List
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(10)
        self.list_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.list_container)
        layout.addWidget(scroll)
        
        # Auto-refresh when shown
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(5000) # Refresh every 5s
        
        self.refresh_data()

    def showEvent(self, event):
        self.refresh_data()
        super().showEvent(event)

    def refresh_data(self):
        # Update Total Time
        total_minutes = self.history_manager.get_total_time_today()
        h = int(total_minutes // 60)
        m = int(total_minutes % 60)
        self.lbl_total_time.setText(f"{h}h {m}m")
        
        # Update List
        # Clear existing
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        sessions = self.history_manager.get_today_sessions()
        # Sort by timestamp desc
        sessions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        if not sessions:
            lbl_empty = QLabel("No sessions yet today.")
            lbl_empty.setStyleSheet("color: #666; font-style: italic;")
            self.list_layout.addWidget(lbl_empty)
        else:
            for s in sessions:
                self._add_session_row(s)

    def _add_session_row(self, session):
        row = QFrame()
        row.setStyleSheet("""
            QFrame {
                background-color: #333;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel {
                color: #ddd;
                background: transparent;
            }
        """)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 5, 10, 5)
        
        # Time
        ts = datetime.fromisoformat(session['timestamp'])
        time_str = ts.strftime("%H:%M")
        lbl_time = QLabel(time_str)
        lbl_time.setFixedWidth(60)
        lbl_time.setStyleSheet("color: #888;")
        row_layout.addWidget(lbl_time)
        
        # Name
        lbl_name = QLabel(session['clock_name'])
        lbl_name.setStyleSheet("font-weight: bold;")
        row_layout.addWidget(lbl_name)
        
        # Duration
        dur = int(session['duration_minutes'])
        lbl_dur = QLabel(f"{dur} min")
        lbl_dur.setAlignment(Qt.AlignRight)
        lbl_dur.setStyleSheet("color: #8b5cf6;")
        row_layout.addWidget(lbl_dur)
        
        self.list_layout.addWidget(row)
