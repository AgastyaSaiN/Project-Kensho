from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QProgressBar, QWidget)
from PySide6.QtCore import Qt
from ...core.models import ClockUnit

class ClockCard(QFrame):
    def __init__(self, clock: ClockUnit, parent=None):
        super().__init__(parent)
        self.clock = clock
        self.setObjectName("ClockCard")
        self.setFixedSize(300, 180)
        
        # Styles
        self.setStyleSheet("""
            QFrame#ClockCard {
                background-color: #2b2b2b;
                border-radius: 15px;
                border: 1px solid #333;
            }
            QLabel#TimeLabel {
                font-size: 32px;
                font-weight: bold;
                color: #e0e0e0;
            }
            QLabel#TitleLabel {
                font-size: 16px;
                color: #a0a0a0;
            }
            QProgressBar {
                border: none;
                background-color: #333;
                height: 6px;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #3b8ed0;
                border-radius: 3px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self.title_label = QLabel(clock.label)
        self.title_label.setObjectName("TitleLabel")
        layout.addWidget(self.title_label)
        
        # Time Display
        self.time_label = QLabel(clock.time_text)
        self.time_label.setObjectName("TimeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(int(clock.progress * 1000))
        layout.addWidget(self.progress_bar)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.btn_toggle = QPushButton("Start")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.clock.toggle)
        
        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.clicked.connect(self._on_edit)
        
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self.clock.reset)
        
        controls_layout.addWidget(self.btn_toggle)
        controls_layout.addWidget(self.btn_edit)
        controls_layout.addWidget(self.btn_reset)
        layout.addLayout(controls_layout)
        
        # Connect Signals
        self.clock.ticked.connect(self._on_tick)
        self.clock.paused_changed.connect(self._on_paused_changed)
        self.clock.finished.connect(self._on_finished)
        
        # Initial State
        self._on_paused_changed(True)

    def _on_edit(self):
        from PySide6.QtWidgets import QInputDialog
        minutes, ok = QInputDialog.getInt(
            self, "Edit Timer", "Duration (minutes):", 
            value=self.clock._interval_minutes, minValue=1, maxValue=180
        )
        if ok:
            self.clock.update_interval(minutes)

    def _on_tick(self, progress):
        self.time_label.setText(self.clock.time_text)
        self.progress_bar.setValue(int(progress * 1000))

    def _on_paused_changed(self, paused):
        self.btn_toggle.setText("Start" if paused else "Pause")
        # Update style for active state?
        if not paused:
            self.setStyleSheet(self.styleSheet().replace("#333;", "#3b8ed0;")) # Hacky highlight
        else:
            self.setStyleSheet(self.styleSheet().replace("#3b8ed0;", "#333;"))

    def _on_finished(self):
        self.btn_toggle.setText("Start")
        # Maybe play sound?
