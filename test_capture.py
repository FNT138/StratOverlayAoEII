"""
Quick test script for screen capture
Run this to verify screen capture works
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.game_detector import ScreenCapture
import cv2


def main():
    print("Screen Capture Test")
    print("=" * 50)
    
    with ScreenCapture(fps_limit=5) as capture:
        # Get screen size
        width, height = capture.get_screen_size()
        print(f"Screen size: {width}x{height}")
        
        # Capture top bar
        print("\nCapturing top bar of screen...")
        top_bar = capture.capture_top_bar(height=150)
        print(f"Captured image shape: {top_bar.shape}")
        
        # Save it
        output_path = "test_capture.png"
        cv2.imwrite(output_path, top_bar)
        print(f"\nSaved screenshot to: {output_path}")
        print("Check the image to see if it captured correctly!")
        
        print("\n" + "=" * 50)
        print("Test completed successfully!")


if __name__ == "__main__":
    main()
