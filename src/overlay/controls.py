"""
Control panel widget
"""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QLabel, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
from typing import List

from ..build_order import BuildOrderLoader


class ControlsWidget(QWidget):
    """Control panel for selecting build orders and managing the overlay"""
    
    build_order_selected = pyqtSignal(str)  # Emits filepath when build order is selected
    next_step_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_orders_dir = ""
        self.init_ui()
    
    def init_ui(self):
        """Initialize controls UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.setLayout(layout)
        
        # Build order selector
        selector_layout = QHBoxLayout()
        
        selector_label = QLabel("Build Order:")
        selector_label.setFont(QFont("Segoe UI", 9))
        selector_label.setStyleSheet("color: #ffffff;")
        
        self.build_order_combo = QComboBox()
        self.build_order_combo.setFont(QFont("Segoe UI", 9))
        self.build_order_combo.currentTextChanged.connect(self.on_build_order_changed)
        self.build_order_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(60, 60, 70, 0.9);
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox:hover {
                border-color: #2196f3;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(50, 50, 60, 0.95);
                color: #ffffff;
                selection-background-color: #2196f3;
            }
        """)
        
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.build_order_combo, stretch=1)
        
        layout.addLayout(selector_layout)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        # Next step button (for testing/manual progression)
        self.next_step_btn = QPushButton("Next Step →")
        self.next_step_btn.setFont(QFont("Segoe UI", 9))
        self.next_step_btn.clicked.connect(self.next_step_clicked.emit)
        self.next_step_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(76, 175, 80, 0.8);
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 1.0);
            }
            QPushButton:pressed {
                background-color: rgba(56, 142, 60, 1.0);
            }
        """)
        
        # Reload button
        self.reload_btn = QPushButton("🔄")
        self.reload_btn.setFixedWidth(40)
        self.reload_btn.clicked.connect(self.reload_build_orders)
        self.reload_btn.setToolTip("Reload build orders")
        self.reload_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 70, 0.8);
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 90, 1.0);
            }
        """)
        
        buttons_layout.addWidget(self.next_step_btn, stretch=1)
        buttons_layout.addWidget(self.reload_btn)
        
        layout.addLayout(buttons_layout)
        
        # Info label
        self.info_label = QLabel("Press F8 to toggle overlay")
        self.info_label.setFont(QFont("Segoe UI", 8))
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: #888;")
        
        layout.addWidget(self.info_label)
        
        # Background style
        self.setStyleSheet("""
            ControlsWidget {
                background-color: rgba(30, 30, 40, 0.95);
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
    
    def set_build_orders_directory(self, directory: str):
        """Set the directory to load build orders from"""
        self.build_orders_dir = directory
        self.reload_build_orders()
    
    def reload_build_orders(self):
        """Reload available build orders from directory"""
        self.build_order_combo.clear()
        
        if not self.build_orders_dir:
            return
        
        build_orders = BuildOrderLoader.get_available_build_orders(self.build_orders_dir)
        
        for filepath in build_orders:
            # Get just the filename without extension for display
            name = Path(filepath).stem.replace('_', ' ').title()
            self.build_order_combo.addItem(name, filepath)
        
        if build_orders:
            self.info_label.setText(f"{len(build_orders)} build order(s) loaded")
        else:
            self.info_label.setText("No build orders found")
    
    def on_build_order_changed(self, text: str):
        """Handle build order selection change"""
        filepath = self.build_order_combo.currentData()
        if filepath:
            self.build_order_selected.emit(filepath)
