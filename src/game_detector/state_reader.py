"""
State reader - main interface for reading game state
"""
from typing import Optional, Callable
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal

from .game_state import GameState
from .screen_capture import ScreenCapture
from .template_matcher import TemplateMatcher


class StateReader(QObject):
    """
    Main class for reading game state from screen captures
    Runs in a separate thread to avoid blocking the UI
    """
    
    # Signals for Qt integration
    state_updated = pyqtSignal(GameState)
    detection_error = pyqtSignal(str)
    
    def __init__(self, fps: int = 5):
        """
        Initialize state reader
        
        Args:
            fps: How many times per second to update state
        """
        super().__init__()
        
        self.capture = ScreenCapture(fps_limit=fps)
        self.matcher = TemplateMatcher(confidence_threshold=0.7)
        
        self.current_state = GameState()
        self.is_running = False
        self.update_thread: Optional[threading.Thread] = None
        
        # Calibration data (UI positions)
        self.calibration = {
            'villager_count': None,  # (x, y, width, height)
            'population': None,
            'food': None,
            'wood': None,
            'gold': None,
            'stone': None
        }
        
        self.is_calibrated = False
    
    def load_calibration(self, calibration_data: dict):
        """
        Load calibration data for UI positions
        
        Args:
            calibration_data: Dictionary with UI element positions
        """
        self.calibration = calibration_data
        self.is_calibrated = True
    
    def start(self):
        """Start the state reading loop in a background thread"""
        if self.is_running:
            return
        
        if not self.is_calibrated:
            self.detection_error.emit("Not calibrated! Please run calibration first.")
            return
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def stop(self):
        """Stop the state reading loop"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=2.0)
        
        # Reset screen capture to allow restart in new thread
        if self.capture.mss is not None:
            try:
                self.capture.mss.close()
            except:
                pass  # Ignore errors during cleanup
            self.capture.mss = None
    
    def _update_loop(self):
        """Main loop that runs in background thread"""
        while self.is_running:
            try:
                self._update_state()
                time.sleep(0.2)  # 5 Hz update rate
            except Exception as e:
                self.detection_error.emit(f"Error reading state: {str(e)}")
                time.sleep(1.0)  # Back off on error
    
    def _update_state(self):
        """
        Update the game state from screen capture
        This is where the actual detection happens
        """
        # Capture the UI area (top of screen)
        screenshot = self.capture.capture_top_bar(height=150)
        
        # Create new state
        new_state = GameState()
        
        # TODO: Implement actual detection
        # For now, just marking state as updated
        
        # Example of what we'll implement:
        # - Extract regions based on calibration
        # - Use template matching to find numbers
        # - Parse numbers and populate state
        
        # Placeholder: detect some dummy values for testing
        new_state.is_valid = True
        new_state.villager_count = 0  # Will implement detection
        new_state.food = 0
        new_state.wood = 0
        new_state.gold = 0
        new_state.stone = 0
        new_state.update_timestamp()
        
        # Update current state
        self.current_state = new_state
        
        # Emit signal for UI updates
        self.state_updated.emit(new_state)
    
    def get_current_state(self) -> GameState:
        """Get the most recent game state"""
        return self.current_state
    
    def manual_capture(self) -> GameState:
        """
        Manually capture and return current state
        Useful for testing without starting the loop
        """
        self._update_state()
        return self.current_state
