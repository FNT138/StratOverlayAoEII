"""
Main overlay window using PyQt6
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QKeySequence, QShortcut
from typing import Optional

from ..build_order import BuildOrder
from ..game_detector import StateReader, GameState


class OverlayWindow(QMainWindow):
    """Transparent overlay window that stays on top of the game"""
    
    def __init__(self):
        super().__init__()
        
        self.build_order: Optional[BuildOrder] = None
        self.dragging = False
        self.drag_position = QPoint()
        
        # Initialize state reader
        self.state_reader = StateReader(fps=5)
        
        self.init_ui()
        self.setup_hotkeys()
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("AoE II Strategy Overlay")
        
        # Window flags for transparent overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Make window transparent and allow click-through for game area
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set initial size and position
        self.setGeometry(50, 50, 400, 600)
        
        # Create central widget with layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # Import and add components here
        # We'll create these in separate files
        from .header import HeaderWidget
        from .build_order_display import BuildOrderDisplay
        from .game_state_display import GameStateWidget
        from .controls import ControlsWidget
        
        self.header = HeaderWidget(self)
        self.game_state_widget = GameStateWidget(self)
        self.build_order_display = BuildOrderDisplay(self)
        self.controls = ControlsWidget(self)
        
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.game_state_widget)
        main_layout.addWidget(self.build_order_display, stretch=1)
        main_layout.addWidget(self.controls)
    
    def connect_signals(self):
        """Connect signals between components"""
        # State reader signals
        self.state_reader.state_updated.connect(self.on_state_updated)
        self.state_reader.detection_error.connect(self.on_detection_error)
        
        # Control signals
        self.controls.start_detection_clicked.connect(self.start_detection)
        self.controls.stop_detection_clicked.connect(self.stop_detection)
    
    def start_detection(self):
        """Start game state detection"""
        print("Starting game state detection...")
        # La calibración se carga automáticamente desde config/calibration.json
        # en el constructor de StateReader
        self.state_reader.start()
        self.game_state_widget.set_detecting_status(True)
    
    def stop_detection(self):
        """Stop game state detection"""
        print("Stopping game state detection...")
        self.state_reader.stop()
        self.game_state_widget.set_detecting_status(False)
    
    def on_state_updated(self, state: GameState):
        """Handle state update from state reader"""
        self.game_state_widget.update_state(state)
        # TODO: Auto-advance build order based on state
    
    def on_detection_error(self, error_msg: str):
        """Handle detection error"""
        print(f"Detection error: {error_msg}")
        self.game_state_widget.show_error(error_msg)
    
    def setup_hotkeys(self):
        """Setup global hotkeys"""
        # F8 to toggle visibility
        self.toggle_shortcut = QShortcut(QKeySequence("F8"), self)
        self.toggle_shortcut.activated.connect(self.toggle_visibility)
    
    def toggle_visibility(self):
        """Toggle overlay visibility"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
    
    def set_build_order(self, build_order: BuildOrder):
        """Load a build order into the overlay"""
        self.build_order = build_order
        self.build_order_display.set_build_order(build_order)
        self.header.update_title(build_order.name)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
