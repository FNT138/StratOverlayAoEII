"""
Screen capture module for efficient game state detection
Uses mss for fast screenshot capture
"""
import mss
import numpy as np
from typing import Optional, Tuple
import time


class ScreenCapture:
    """Handles screen capture for game state detection"""
    
    def __init__(self, fps_limit: int = 5):
        """
        Initialize screen capture
        
        Args:
            fps_limit: Maximum captures per second (default 5 for performance)
        """
        self.mss = mss.mss()
        self.fps_limit = fps_limit
        self.min_frame_time = 1.0 / fps_limit
        self.last_capture_time = 0
        
        # Cache for game window position
        self.game_window_region: Optional[dict] = None
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        Capture a specific screen region
        
        Args:
            x: Left coordinate
            y: Top coordinate  
            width: Width of region
            height: Height of region
            
        Returns:
            numpy array with BGR image data
        """
        # FPS limiting
        current_time = time.time()
        time_since_last = current_time - self.last_capture_time
        if time_since_last < self.min_frame_time:
            time.sleep(self.min_frame_time - time_since_last)
        
        # Capture region
        monitor = {
            "left": x,
            "top": y,
            "width": width,
            "height": height
        }
        
        screenshot = self.mss.grab(monitor)
        
        # Convert to numpy array (RGB)
        img = np.array(screenshot)
        
        # Convert RGBA to RGB (remove alpha channel if present)
        if img.shape[2] == 4:
            img = img[:, :, :3]
        
        # Convert RGB to BGR for OpenCV compatibility
        img = img[:, :, ::-1].copy()
        
        self.last_capture_time = time.time()
        
        return img
    
    def capture_full_screen(self) -> np.ndarray:
        """
        Capture the full primary screen
        
        Returns:
            numpy array with BGR image data
        """
        monitor = self.mss.monitors[1]  # Primary monitor
        return self.capture_region(
            monitor["left"],
            monitor["top"],
            monitor["width"],
            monitor["height"]
        )
    
    def capture_top_bar(self, height: int = 150) -> np.ndarray:
        """
        Capture just the top bar of the screen (where UI is in AOE II)
        
        Args:
            height: Height of the top bar to capture (default 150px)
            
        Returns:
            numpy array with BGR image data
        """
        monitor = self.mss.monitors[1]
        return self.capture_region(
            monitor["left"],
            monitor["top"],
            monitor["width"],
            height
        )
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get the primary screen size
        
        Returns:
            Tuple of (width, height)
        """
        monitor = self.mss.monitors[1]
        return (monitor["width"], monitor["height"])
    
    def set_fps_limit(self, fps: int):
        """Update the FPS limit"""
        self.fps_limit = fps
        self.min_frame_time = 1.0 / fps
    
    def close(self):
        """Clean up resources"""
        self.mss.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
