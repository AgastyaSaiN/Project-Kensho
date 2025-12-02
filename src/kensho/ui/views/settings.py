from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, 
                               QPushButton, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt
from ...core.sound import SoundManager

class SettingsView(QWidget):
    def __init__(self, current_sound="System Exclamation", parent=None):
        super().__init__(parent)
        self.current_sound = current_sound
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Sound Section
        sound_frame = QFrame()
        sound_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        sound_layout = QVBoxLayout(sound_frame)
        
        lbl_sound = QLabel("Notification Sound")
        lbl_sound.setStyleSheet("font-size: 16px; font-weight: bold; color: #ddd;")
        sound_layout.addWidget(lbl_sound)
        
        # Controls Row
        controls_layout = QHBoxLayout()
        
        self.combo_sound = QComboBox()
        self.combo_sound.addItems(SoundManager.get_available_sounds())
        self.combo_sound.setCurrentText(self.current_sound)
        self.combo_sound.setStyleSheet("""
            QComboBox {
                background-color: #333;
                color: white;
                padding: 8px;
                border: 1px solid #555;
                border-radius: 5px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.combo_sound.currentTextChanged.connect(self._on_sound_changed)
        controls_layout.addWidget(self.combo_sound)
        
        self.btn_test = QPushButton("Test Sound")
        self.btn_test.setCursor(Qt.PointingHandCursor)
        self.btn_test.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        self.btn_test.clicked.connect(self._test_sound)
        controls_layout.addWidget(self.btn_test)
        
        controls_layout.addStretch()
        sound_layout.addLayout(controls_layout)
        
        layout.addWidget(sound_frame)
        layout.addStretch()

    def _on_sound_changed(self, text):
        self.current_sound = text

    def _test_sound(self):
        SoundManager.play_sound(self.current_sound)
