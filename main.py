"""
Main entry point for AoE II Strategy Overlay
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from src.overlay import OverlayWindow
from src.build_order import BuildOrderLoader


def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("AoE II Strategy Overlay")
    app.setOrganizationName("StratOverlay")
    
    # Create main window
    window = OverlayWindow()
    
    # Set build orders directory
    build_orders_dir = Path(__file__).parent / "build_orders"
    build_orders_dir.mkdir(exist_ok=True)
    
    window.controls.set_build_orders_directory(str(build_orders_dir))
    
    # Define callback functions
    def on_build_order_selected(filepath: str):
        """Load selected build order"""
        try:
            build_order = BuildOrderLoader.load_from_file(filepath)
            window.set_build_order(build_order)
            print(f"Loaded build order: {build_order.name}")
        except Exception as e:
            print(f"Error loading build order: {e}")
    
    # Connect signals
    window.controls.build_order_selected.connect(on_build_order_selected)
    window.controls.next_step_clicked.connect(lambda: window.build_order_display.advance_step())
    window.header.close_clicked.connect(app.quit)
    window.header.minimize_clicked.connect(window.showMinimized)
    
    # Show window
    window.show()
    
    print("=" * 50)
    print("   AoE II Strategy Overlay - MVP v0.1")
    print("=" * 50)
    print("\nControls:")
    print("  F8          -> Toggle overlay visibility")
    print("  Drag header -> Move overlay")
    print("  Next Step   -> Manually advance build order")
    print("\nOverlay is now running. Minimize this window.")
    print("Press Ctrl+C here or click X on overlay to exit.\n")
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
