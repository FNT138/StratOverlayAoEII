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
        self.vill_label = QLabel("👤 Villagers: --")
        self.vill_label.setFont(QFont("Segoe UI", 9))
        self.pop_label = QLabel("Pop: --/--")
        self.pop_label.setFont(QFont("Segoe UI", 9))
        pop_layout.addWidget(self.vill_label)
        pop_layout.addStretch()
        pop_layout.addWidget(self.pop_label)
        layout.addLayout(pop_layout)
        
        # Resources
        self.food_label = QLabel("🌾 Food: --")
        self.food_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self.food_label)
        
        self.wood_label = QLabel("🪵 Wood: --")
        self.wood_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self.wood_label)
        
        self.gold_label = QLabel("🪙 Gold: --")
        self.gold_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self.gold_label)
        
        self.stone_label = QLabel("🪨 Stone: --")
        self.stone_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self.stone_label)
        
        # Age
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
                background-color: rgba(40, 40, 50, 0.9);
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
        
        # Update all labels
        self.vill_label.setText(f"👤 Villagers: {state.villager_count}")
        self.pop_label.setText(f"Pop: {state.population}/{state.max_population}")
        self.food_label.setText(f"🌾 Food: {state.food}")
        self.wood_label.setText(f"🪵 Wood: {state.wood}")
        self.gold_label.setText(f"🪙 Gold: {state.gold}")
        self.stone_label.setText(f"🪨 Stone: {state.stone}")
        self.age_label.setText(f"🏛️ Age: {state.age} Age")
        
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
