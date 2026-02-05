"""
Test stop/restart detection cycle
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.game_detector import StateReader, GameState
from PyQt6.QtCore import QCoreApplication
import time


def test_stop_restart():
    """Test stopping and restarting detection"""
    print("=" * 60)
    print("Testing Stop/Restart Detection Cycle")
    print("=" * 60)
    
    app = QCoreApplication(sys.argv)
    
    reader = StateReader(fps=5)
    
    def on_state_updated(state: GameState):
        print(f"   State: {state}")
    
    def on_error(error_msg: str):
        print(f"   ERROR: {error_msg}")
    
    reader.state_updated.connect(on_state_updated)
    reader.detection_error.connect(on_error)
    
    # Load calibration
    dummy_calibration = {
        'villager_count': (100, 20, 50, 30),
        'population': (200, 20, 60, 30),
        'food': (300, 20, 60, 25),
        'wood': (380, 20, 60, 25),
        'gold': (460, 20, 60, 25),
        'stone': (540, 20, 60, 25)
    }
    reader.load_calibration(dummy_calibration)
    
    # Cycle 1
    print("\n[Cycle 1] Starting detection...")
    reader.start()
    start_time = time.time()
    while time.time() - start_time < 2:
        app.processEvents()
        time.sleep(0.1)
    
    print("[Cycle 1] Stopping detection...")
    reader.stop()
    time.sleep(0.5)
    
    # Cycle 2
    print("\n[Cycle 2] Starting detection again...")
    reader.start()
    start_time = time.time()
    while time.time() - start_time < 2:
        app.processEvents()
        time.sleep(0.1)
    
    print("[Cycle 2] Stopping detection...")
    reader.stop()
    time.sleep(0.5)
    
    # Cycle 3
    print("\n[Cycle 3] Starting detection third time...")
    reader.start()
    start_time = time.time()
    while time.time() - start_time < 2:
        app.processEvents()
        time.sleep(0.1)
    
    print("[Cycle 3] Stopping detection...")
    reader.stop()
    
    print("\n" + "=" * 60)
    print("Test completed! If no errors, bug is fixed.")
    print("=" * 60)


if __name__ == "__main__":
    test_stop_restart()
