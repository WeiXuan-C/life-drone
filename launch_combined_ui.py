#!/usr/bin/env python3
"""
Combined UI Launcher - Opens both Terrain UI and JSON Viewer together
"""

import sys
import os
import threading
import time
from multiprocessing import Process

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def launch_terrain_ui():
    """Launch the terrain UI in a separate process"""
    try:
        from ui.enhanced_tkinter_ui import main as enhanced_main
        print("🗺️ Launching Enhanced Terrain UI...")
        enhanced_main()
    except ImportError as e:
        print(f"❌ Error loading Enhanced Terrain UI: {e}")
        print("💡 Trying alternative terrain UI...")
        try:
            from ui.enhanced_ui_with_json import main as alt_main
            alt_main()
        except Exception as e2:
            print(f"❌ Alternative UI also failed: {e2}")
    except Exception as e:
        print(f"❌ Terrain UI Error: {e}")

def launch_json_viewer():
    """Launch the JSON viewer in a separate process"""
    try:
        from simple_json_ui import main as json_main
        print("🤖 Launching JSON Response Viewer...")
        time.sleep(1)  # Small delay to let terrain UI start first
        json_main()
    except Exception as e:
        print(f"❌ JSON Viewer Error: {e}")

def main():
    """Main launcher function"""
    print("🚁 Agentic AI Disaster Rescue Drone System")
    print("=" * 55)
    print("🏢 Central Command Center - Main Control Hub")
    print("🤖 AI-Powered Drone Coordination for Emergency Response")
    print("🔄 MANDATORY: All operations use LangGraph workflow")
    
    print("\nSystem Features:")
    print("   • Central Command Center for all drone operations")
    print("   • MANDATORY LangGraph workflow for all AI operations")
    print("   • Advanced AI reasoning with Ollama Qwen2")
    print("   • Complex terrain system (mountains, water, forests)")
    print("   • Dynamic weather and environmental conditions")
    print("   • Multi-step AI decision process visualization")
    print("   • A* pathfinding with terrain cost analysis")
    print("   • Real-time mission memory and logging")
    print("   • MCP server integration for tool coordination")
    print("   • JSON Response Viewer for Ollama Qwen2 outputs")
    
    print("\n" + "=" * 55)
    print("🎮 Launch Combined UI Demo")
    print("   • Enhanced terrain visualization with mountains, water, forests")
    print("   • Real-time JSON response viewer for Ollama Qwen2")
    print("   • AI-powered drone coordination with LangGraph workflow")
    print("   • Complete rescue mission simulation")
    print("   • Side-by-side terrain and JSON analysis")
    
    choice = input("\nPress Enter to launch the Combined UI Demo (Terrain + JSON), or 'q' to quit: ").strip().lower()
    
    if choice == 'q':
        print("\n👋 Goodbye!")
        sys.exit(0)
    else:
        print("\n🎮 Launching Combined UI Demo...")
        print("🔄 Flow: UI → RescueAgent → Ollama → LangGraph → MCP")
        print("📋 Opening both Terrain UI and JSON Viewer...")
        
        try:
            # Launch both UIs using multiprocessing for true parallel execution
            terrain_process = Process(target=launch_terrain_ui, name="TerrainUI")
            json_process = Process(target=launch_json_viewer, name="JSONViewer")
            
            print("🗺️ Starting Terrain UI process...")
            terrain_process.start()
            
            print("🤖 Starting JSON Viewer process...")
            json_process.start()
            
            print("✅ Both UIs launched successfully!")
            print("\n📋 Usage Instructions:")
            print("   1. Use the Terrain UI to control drone missions")
            print("   2. Use the JSON Viewer to see Ollama Qwen2 responses")
            print("   3. Actions in Terrain UI will generate JSON in the viewer")
            print("   4. Close both windows when done")
            
            # Wait for both processes to complete
            terrain_process.join()
            json_process.join()
            
            print("\n✅ Combined UI Demo completed!")
            
        except Exception as e:
            print(f"❌ Error launching combined UI: {e}")
            print("💡 Trying fallback single UI...")
            
            # Fallback to single UI
            try:
                launch_json_viewer()
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
                print("💡 Please check system requirements")

if __name__ == "__main__":
    main()