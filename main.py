"""
Agentic AI Disaster Rescue Drone System
Main entry point - Launch Redesigned UI
"""

import sys
import os

def main():
    """Launch the redesigned UI"""
    try:
        from ui.redesigned_ui import main as redesigned_main
        redesigned_main()
    except ImportError as e:
        print(f"❌ Error loading Redesigned UI: {e}")
        print("💡 Please ensure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ UI Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()