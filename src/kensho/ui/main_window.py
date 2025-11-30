from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFrame, QStackedWidget)
from PySide6.QtCore import Qt, QSize
from .dashboard import DashboardView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kenshō")
        self.resize(1000, 700)
        
        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo
        logo = QLabel("Kenshō")
        logo.setObjectName("Logo")
        logo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo)
        
        # Navigation
        self.nav_dashboard = self._create_nav_button("Dashboard")
        self.nav_history = self._create_nav_button("History")
        self.nav_settings = self._create_nav_button("Settings")
        
        sidebar_layout.addWidget(self.nav_dashboard)
        sidebar_layout.addWidget(self.nav_history)
        sidebar_layout.addWidget(self.nav_settings)
        sidebar_layout.addStretch()
        
        # Content Area
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("ContentArea")
        
        # Views
        self.dashboard_view = DashboardView()
        
        self.history_view = QLabel("History View")
        self.history_view.setAlignment(Qt.AlignCenter)
        
        self.settings_view = QLabel("Settings View")
        self.settings_view.setAlignment(Qt.AlignCenter)
        
        self.content_area.addWidget(self.dashboard_view)
        self.content_area.addWidget(self.history_view)
        self.content_area.addWidget(self.settings_view)
        
        # Add to Main Layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)
        
        # Kensho Button (Bottom of Sidebar)
        self.btn_kensho = QPushButton("Enter Kenshō")
        self.btn_kensho.setCursor(Qt.PointingHandCursor)
        self.btn_kensho.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        self.btn_kensho.clicked.connect(self.enter_widget_mode)
        sidebar_layout.addWidget(self.btn_kensho)
        
        # Connect Signals
        self.nav_dashboard.clicked.connect(lambda: self.switch_view(0))
        self.nav_history.clicked.connect(lambda: self.switch_view(1))
        self.nav_settings.clicked.connect(lambda: self.switch_view(2))
        
        # Default View
        self.nav_dashboard.setChecked(True)
        self.switch_view(0)
        
        # Widget Mode Window
        self.widget_window = None

    def _create_nav_button(self, text):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setProperty("class", "NavButton") # For stylesheet
        return btn

    def switch_view(self, index):
        self.content_area.setCurrentIndex(index)

    def enter_widget_mode(self):
        from .widget_mode import WidgetMode
        
        # Get clocks from dashboard
        clocks = self.dashboard_view.clocks
        if not clocks: return
        
        self.hide()
        self.widget_window = WidgetMode(clocks)
        self.widget_window.restore_requested.connect(self.exit_widget_mode)
        self.widget_window.show()

    def exit_widget_mode(self):
        if self.widget_window:
            self.widget_window.close()
            self.widget_window = None
        self.show()
        self.raise_()
        self.activateWindow()
