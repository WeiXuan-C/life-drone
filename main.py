"""
Autonomous Drone Swarm Command System
Main entry point for the disaster rescue simulation
"""

import sys
import os

def main():
    """Main entry point with options for different UI modes"""
    
    print("🚁 Autonomous Drone Swarm Command System")
    print("=" * 50)
    print("Choose your interface:")
    print("1. Console UI (interactive terminal interface)")
    print("2. Basic Tkinter UI (simple desktop GUI)")
    print("3. Enhanced Terrain UI (complex terrain + advanced AI)")
    print("4. Mesa 3.x Web UI (experimental web interface)")
    print("5. Demo Mode (automated demonstration)")
    print("6. Run simulation without UI (headless)")
    print("7. Exit")
    
    choice = input("\nEnter your choice (1-7): ").strip()
    
    if choice == "1":
        print("\n🚀 Launching Console UI...")
        from ui.console_ui import main as console_main
        console_main()
        
    elif choice == "2":
        print("\n🚀 Launching Basic Tkinter UI...")
        try:
            from ui.tkinter_interactive_ui import main as tkinter_main
            tkinter_main()
        except ImportError as e:
            print(f"❌ Error: {e}")
            print("💡 Tkinter should be included with Python by default")
        
    elif choice == "3":
        print("\n🚀 Launching Enhanced Terrain UI...")
        print("🗺️ Features:")
        print("   • Complex terrain system (mountains, water, forests)")
        print("   • Dynamic weather conditions")
        print("   • Advanced AI multi-step reasoning")
        print("   • A* pathfinding with terrain costs")
        print("   • Detailed decision process visualization")
        try:
            from ui.enhanced_tkinter_ui import main as enhanced_main
            enhanced_main()
        except ImportError as e:
            print(f"❌ Error: {e}")
            print("💡 Make sure all terrain system files are present")
        
    elif choice == "4":
        print("\n🚀 Launching Mesa 3.x Web UI...")
        print("🌐 This will open a web browser interface")
        try:
            from ui.mesa3_interactive_ui import create_interactive_ui
            ui = create_interactive_ui()
            if ui:
                print("📱 Access at: http://localhost:8521")
                ui.launch(port=8521)
            else:
                print("❌ Failed to create web UI")
                print("💡 Try: pip install solara mesa>=3.0.0")
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("💡 Install dependencies: pip install solara mesa>=3.0.0")
        
    elif choice == "5":
        print("\n🚀 Launching Demo Mode...")
        from demo import run_demo
        run_demo()
        
    elif choice == "6":
        print("\n🤖 Running headless simulation...")
        from simulation.simple_model import SimpleDroneSwarmModel, SimpleDroneAgent, SimpleSurvivorAgent
        
        # Create and run model
        model = SimpleDroneSwarmModel(n_drones=5, n_survivors=8, n_charging_stations=2)
        
        print("Running 100 simulation steps...")
        for i in range(100):
            model.step()
            if i % 20 == 0:
                active_drones = len([a for a in model.custom_agents 
                                   if isinstance(a, SimpleDroneAgent) and a.status != 'charging'])
                rescued = len([a for a in model.custom_agents 
                             if isinstance(a, SimpleSurvivorAgent) and a.found])
                print(f"Step {i}: {active_drones} active drones, {rescued} survivors rescued")
        
        print("✅ Simulation completed!")
        
    elif choice == "7":
        print("👋 Goodbye!")
        sys.exit(0)
        
    else:
        print("❌ Invalid choice. Please try again.")
        main()

if __name__ == "__main__":
    main()