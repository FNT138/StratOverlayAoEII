"""
Game state display widget - shows current game state in real-time
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Optional

from ..game_detector import GameState


class GameStateWidget(QFrame):
    """Widget to display current game state"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_state: Optional[GameState] = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)
        self.setLayout(layout)
        
        # Title
        title = QLabel("📊 Game State")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #4CAF50;")
        layout.addWidget(title)
        
        # Population row
        pop_layout = QHBoxLayout()
        self.vill_label = QLabel("👤 Vills: --")
        self.vill_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.pop_label = QLabel("Pop: --/--")
        self.pop_label.setFont(QFont("Segoe UI", 9))
        pop_layout.addWidget(self.vill_label)
        pop_layout.addStretch()
        pop_layout.addWidget(self.pop_label)
        layout.addLayout(pop_layout)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #555;")
        layout.addWidget(line)
        
        # Resources Grid (Label | Amount | Income | Vills)
        self.res_labels = {}
        
        for res, icon, color in [
            ('food', '🌾', '#FF9800'), 
            ('wood', '🪵', '#795548'),
            ('gold', '🪙', '#FFC107'),
            ('stone', '🪨', '#9E9E9E')
        ]:
            row = QHBoxLayout()
            row.setSpacing(5)
            
            # Icon & Name
            lbl_name = QLabel(f"{icon}")
            lbl_name.setFixedWidth(20)
            
            # Amount & Income
            lbl_data = QLabel("-- (+0/m)")
            lbl_data.setFont(QFont("Segoe UI", 9))
            lbl_data.setStyleSheet(f"color: {color};")
            
            # Villagers count
            lbl_vills = QLabel("0 👤")
            lbl_vills.setFont(QFont("Segoe UI", 9))
            lbl_vills.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_vills.setFixedWidth(40)
            
            row.addWidget(lbl_name)
            row.addWidget(lbl_data, stretch=1)
            row.addWidget(lbl_vills)
            layout.addLayout(row)
            
            self.res_labels[res] = {'data': lbl_data, 'vills': lbl_vills}
        
        # Age
        layout.addSpacing(5)
        self.age_label = QLabel("🏛️ Age: Dark Age")
        self.age_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self.age_label)
        
        # Status
        self.status_label = QLabel("⚪ Not detecting")
        self.status_label.setFont(QFont("Segoe UI", 8))
        self.status_label.setStyleSheet("color: #888;")
        layout.addWidget(self.status_label)
        
        # Styling
        self.setStyleSheet("""
            GameStateWidget {
                background-color: rgba(30, 30, 40, 0.95);
                border: 1px solid #555;
                border-radius: 5px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def update_state(self, state: GameState):
        """Update display with new game state"""
        self.current_state = state
        
        if not state.is_valid:
            self.status_label.setText("⚠️ Invalid state")
            self.status_label.setStyleSheet("color: #FF9800;")
            return
        
        # Update header
        self.vill_label.setText(f"👤 Vills: {state.villager_count}")
        self.pop_label.setText(f"Pop: {state.population}/{state.max_population}")
        self.age_label.setText(f"🏛️ Age: {state.age} Age")
        
        # Update resources
        income = state.get_income_per_minute()
        
        # Food
        self.res_labels['food']['data'].setText(f"{state.food} (+{int(income['food'])}/m)")
        self.res_labels['food']['vills'].setText(f"{state.food_villagers} 👤")
        
        # Wood
        self.res_labels['wood']['data'].setText(f"{state.wood} (+{int(income['wood'])}/m)")
        self.res_labels['wood']['vills'].setText(f"{state.wood_villagers} 👤")
        
        # Gold
        self.res_labels['gold']['data'].setText(f"{state.gold} (+{int(income['gold'])}/m)")
        self.res_labels['gold']['vills'].setText(f"{state.gold_villagers} 👤")
        
        # Stone
        self.res_labels['stone']['data'].setText(f"{state.stone} (+{int(income['stone'])}/m)")
        self.res_labels['stone']['vills'].setText(f"{state.stone_villagers} 👤")
        
        self.status_label.setText("🟢 Detecting")
        self.status_label.setStyleSheet("color: #4CAF50;")
    
    def set_detecting_status(self, is_detecting: bool):
        """Update the detection status indicator"""
        if is_detecting:
            self.status_label.setText("🟢 Detecting")
            self.status_label.setStyleSheet("color: #4CAF50;")
        else:
            self.status_label.setText("⚪ Not detecting")
            self.status_label.setStyleSheet("color: #888;")
    
    def show_error(self, error_msg: str):
        """Show an error message"""
        self.status_label.setText(f"❌ Error: {error_msg[:30]}")
        self.status_label.setStyleSheet("color: #F44336;")
