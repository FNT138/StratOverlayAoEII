"""
Build order display widget
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, 
                             QLabel, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Optional

from ..build_order import BuildOrder, BuildOrderStep


class BuildOrderStepWidget(QFrame):
    """Widget for displaying a single build order step"""
    
    def __init__(self, step: BuildOrderStep, is_current: bool = False, parent=None):
        super().__init__(parent)
        self.step = step
        self.is_current = is_current
        self.init_ui()
    
    def init_ui(self):
        """Initialize step UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        self.setLayout(layout)
        
        # Villager count indicator
        vill_label = QLabel(f"{self.step.villager_count}")
        vill_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        vill_label.setFixedWidth(30)
        vill_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Checkmark or bullet
        if self.step.completed:
            check_label = QLabel("✓")
            check_label.setStyleSheet("color: #4caf50; font-size: 16px;")
        else:
            check_label = QLabel("●")
            check_label.setStyleSheet("color: #888;")
        check_label.setFixedWidth(20)
        
        # Description
        desc_label = QLabel(self.step.description)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setWordWrap(True)
        
        layout.addWidget(check_label)
        layout.addWidget(vill_label)
        layout.addWidget(desc_label, stretch=1)
        
        # Styling
        if self.is_current:
            bg_color = "rgba(33, 150, 243, 0.3)"
            border_color = "#2196f3"
            text_color = "#ffffff"
        elif self.step.completed:
            bg_color = "rgba(76, 175, 80, 0.2)"
            border_color = "#4caf50"
            text_color = "#cccccc"
        elif self.step.important:
            bg_color = "rgba(255, 152, 0, 0.2)"
            border_color = "#ff9800"
            text_color = "#ffffff"
        else:
            bg_color = "rgba(50, 50, 60, 0.8)"
            border_color = "#555"
            text_color = "#ffffff"
        
        self.setStyleSheet(f"""
            BuildOrderStepWidget {{
                background-color: {bg_color};
                border-left: 3px solid {border_color};
                border-radius: 5px;
                margin: 2px 5px;
            }}
            QLabel {{
                color: {text_color};
            }}
        """)


class BuildOrderDisplay(QWidget):
    """Main widget for displaying the build order steps"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_order: Optional[BuildOrder] = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize display UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        # Build order info header
        self.info_label = QLabel("No build order loaded")
        self.info_label.setFont(QFont("Segoe UI", 9))
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: rgba(40, 40, 50, 0.9);
                color: #aaa;
                padding: 8px;
            }
        """)
        layout.addWidget(self.info_label)
        
        # Scroll area for steps
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: rgba(25, 25, 35, 0.95);
            }
            QScrollBar:vertical {
                background-color: rgba(30, 30, 40, 0.8);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(100, 100, 120, 0.8);
                border-radius: 5px;
            }
        """)
        
        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout()
        self.steps_layout.setContentsMargins(5, 5, 5, 5)
        self.steps_layout.setSpacing(3)
        self.steps_container.setLayout(self.steps_layout)
        
        scroll_area.setWidget(self.steps_container)
        layout.addWidget(scroll_area)
    
    def set_build_order(self, build_order: BuildOrder):
        """Load and display a build order"""
        self.build_order = build_order
        self.update_display()
    
    def update_display(self):
        """Refresh the display with current build order state"""
        # Clear existing steps
        while self.steps_layout.count():
            item = self.steps_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.build_order:
            return
        
        # Update info label
        info_text = (f"📋 {self.build_order.strategy or 'Strategy'} | "
                    f"🏛️ {self.build_order.civilization.title()} | "
                    f"🎯 {self.build_order.target_age} Age")
        self.info_label.setText(info_text)
        
        # Add step widgets
        current_idx = self.build_order.current_step_index
        
        for i, step in enumerate(self.build_order.steps):
            is_current = (i == current_idx)
            step_widget = BuildOrderStepWidget(step, is_current)
            self.steps_layout.addWidget(step_widget)
        
        # Add spacer at the end
        self.steps_layout.addStretch()
    
    def advance_step(self):
        """Move to next step and refresh display"""
        if self.build_order:
            self.build_order.advance_step()
            self.update_display()
