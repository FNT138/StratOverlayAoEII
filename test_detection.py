"""
Debug script to test state detection - ASCII only for Windows
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.game_detector import StateReader, GameState
from PyQt6.QtCore import QCoreApplication
import traceback


def test_state_reader():
    """Test the state reader with dummy calibration"""
    print("=" * 60)
    print("Testing State Reader")
    print("=" * 60)
    
    # Create Qt application (needed for signals)
    app = QCoreApplication(sys.argv)
    
    # Create state reader
    print("\n1. Creating StateReader...")
    try:
        reader = StateReader(fps=5)
        print("[OK] StateReader created successfully")
    except Exception as e:
        print(f"[ERROR] Error creating StateReader: {e}")
        traceback.print_exc()
        return
    
    # Setup signal handlers
    print("\n2. Connecting signals...")
    def on_state_updated(state: GameState):
        print(f"   State updated: {state}")
    
    def on_error(error_msg: str):
        print(f"   ERROR: {error_msg}")
    
    reader.state_updated.connect(on_state_updated)
    reader.detection_error.connect(on_error)
    print("[OK] Signals connected")
    
    # Load dummy calibration
    print("\n3. Loading dummy calibration...")
    dummy_calibration = {
        'villager_count': (100, 20, 50, 30),
        'population': (200, 20, 60, 30),
        'food': (300, 20, 60, 25),
        'wood': (380, 20, 60, 25),
        'gold': (460, 20, 60, 25),
        'stone': (540, 20, 60, 25)
    }
    reader.load_calibration(dummy_calibration)
    print("[OK] Calibration loaded")
    print(f"   is_calibrated = {reader.is_calibrated}")
    
    # Start detection
    print("\n4. Starting detection...")
    try:
        reader.start()
        print("[OK] Detection started")
        print(f"   is_running = {reader.is_running}")
    except Exception as e:
        print(f"[ERROR] Error starting detection: {e}")
        traceback.print_exc()
        return
    
    # Let it run for a few seconds
    print("\n5. Running for 5 seconds...")
    print("   (Watch for state updates above)")
    
    import time
    start_time = time.time()
    try:
        while time.time() - start_time < 5:
            app.processEvents()  # Process Qt events
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n   Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Error during run: {e}")
        traceback.print_exc()
    
    # Stop detection
    print("\n6. Stopping detection...")
    try:
        reader.stop()
        print("[OK] Detection stopped")
    except Exception as e:
        print(f"[ERROR] Error stopping detection: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_state_reader()
