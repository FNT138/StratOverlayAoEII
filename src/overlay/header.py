"""
Header widget for the overlay
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class HeaderWidget(QWidget):
    """Header bar with title and controls"""
    
    close_clicked = pyqtSignal()
    minimize_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize header UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(layout)
        
        # Title label
        self.title_label = QLabel("AoE II Strategy Overlay")
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #ffffff;")
        
        # Minimize button (collapse/expand)
        self.minimize_btn = QPushButton("─")
        self.minimize_btn.setFixedSize(25, 25)
        self.minimize_btn.clicked.connect(self.minimize_clicked.emit)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 193, 7, 0.8);
                border: none;
                border-radius: 12px;
                color: #000;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 193, 7, 1.0);
            }
        """)
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.clicked.connect(self.close_clicked.emit)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(244, 67, 54, 0.8);
                border: none;
                border-radius: 12px;
                color: #fff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(244, 67, 54, 1.0);
            }
        """)
        
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.close_btn)
        
        # Background style
        self.setStyleSheet("""
            HeaderWidget {
                background-color: rgba(30, 30, 40, 0.95);
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
    
    def update_title(self, title: str):
        """Update the title text"""
        self.title_label.setText(title)
