"""
Agentic AI Disaster Rescue Drone System
Main entry point with Central Command Center coordination
"""

import sys
import os
from command_center import CentralCommandCenter, get_command_center

def main():
    """Main entry point for the Agentic AI system with Central Command"""
    
    print("🚁 Agentic AI Disaster Rescue Drone System")
    print("=" * 55)
    print("🏢 Central Command Center - Main Control Hub")
    print("🤖 AI-Powered Drone Coordination for Emergency Response")
    print("\nSystem Features:")
    print("   • Central Command Center for all drone operations")
    print("   • Advanced AI reasoning with Ollama Qwen2")
    print("   • Complex terrain system (mountains, water, forests)")
    print("   • Dynamic weather and environmental conditions")
    print("   • Multi-step AI decision process visualization")
    print("   • A* pathfinding with terrain cost analysis")
    print("   • Real-time mission memory and logging")
    print("   • MCP server integration for tool coordination")
    
    print("\n" + "=" * 55)
    print("Choose your mode:")
    print("1. 🎮 Launch Enhanced Terrain UI")
    print("2. 🚀 Run LangGraph Workflow Demo")
    print("3. 🧪 Run AI Demo")
    print("4. 📊 Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🎮 Launching Enhanced Terrain UI...")
        try:
            launch_enhanced_ui()
        except Exception as e:
            print(f"❌ Error: {e}")
            run_basic_demo()
        
    elif choice == "2":
        print("\n🚀 Launching LangGraph Workflow Demo...")
        try:
            import subprocess
            subprocess.run([sys.executable, "demo_langgraph.py"])
        except Exception as e:
            print(f"❌ Error: {e}")
            run_basic_demo()
        
    elif choice == "3":
        print("\n🧪 Running AI Demo...")
        try:
            import subprocess
            subprocess.run([sys.executable, "demo_agentic_ai.py"])
        except Exception as e:
            print(f"❌ Error: {e}")
            run_basic_demo()
        
    elif choice == "4":
        print("\n👋 Goodbye!")
        sys.exit(0)
        
    else:
        print("❌ Invalid choice. Please select 1-4.")
        main()



def launch_command_center_dashboard():
    """Launch the Central Command Center dashboard interface"""
    print("\n🏢 Central Command Center Dashboard")
    print("=" * 50)
    
    # Initialize the command center
    cc = get_command_center()
    
    # Display main dashboard
    while True:
        print("\n📊 COMMAND CENTER DASHBOARD")
        print("-" * 30)
        
        # Show system status
        status = cc.get_system_status()
        print(f"🏢 Command Status: {status['command_center_status'].upper()}")
        print(f"⏱️  System Uptime: {status['system_uptime']}")
        print(f"🚁 Drones: {status['active_drones']}/{status['total_drones']} active")
        print(f"📋 Active Missions: {status['active_missions']}")
        print(f"📡 Pending Orders: {status['pending_orders']}")
        print(f"🆘 Survivors Located: {status['survivor_count']}")
        print(f"✅ Completed Rescues: {status['total_rescues']}")
        
        print("\n🎮 COMMAND OPTIONS:")
        print("1. 📋 Create New Mission")
        print("2. 🚁 Register New Drone")
        print("3. 🆘 Report Survivor Location")
        print("4. 📡 Issue Direct Command")
        print("5. 📊 View Detailed Status")
        print("6. 🚨 Emergency Recall All")
        print("7. 🎮 Launch Simulation UI")
        print("8. 🔙 Return to Main Menu")
        
        choice = input("\nEnter command (1-8): ").strip()
        
        if choice == "1":
            create_mission_interactive(cc)
        elif choice == "2":
            register_drone_interactive(cc)
        elif choice == "3":
            report_survivor_interactive(cc)
        elif choice == "4":
            issue_command_interactive(cc)
        elif choice == "5":
            show_detailed_status(cc)
        elif choice == "6":
            cc.emergency_recall_all()
            input("Press any key to continue...")
        elif choice == "7":
            launch_enhanced_ui()
            break
        elif choice == "8":
            break
        else:
            print("❌ Invalid choice. Please select 1-8.")


def launch_home_base_ui():
    """Launch the Home Base Control Center UI"""
    try:
        import ui.command_center_ui
        app = ui.command_center_ui.CommandCenterUI()
        app.run()
    except ImportError as e:
        print(f"❌ Error loading Home Base UI: {e}")
        print("💡 Running home base demo instead...")
        run_home_base_demo()
    except Exception as e:
        print(f"❌ UI Error: {e}")
        print("💡 Falling back to demo mode...")
        run_home_base_demo()


def run_home_base_demo():
    """Run the home base demonstration"""
    try:
        import subprocess
        result = subprocess.run([sys.executable, "demo_home_base.py"], 
                              capture_output=False, text=True)
        if result.returncode != 0:
            print("💡 Running basic demo...")
            run_basic_demo()
    except Exception as e:
        print(f"❌ Home base demo error: {e}")
        print("💡 Running basic simulation...")
        run_basic_demo()
    
    print("\nPress any key to return to main menu...")
    try:
        input()
    except:
        pass
    main()


def launch_enhanced_ui():
    """Launch the enhanced terrain UI"""
    try:
        from ui.enhanced_tkinter_ui import main as enhanced_main
        enhanced_main()
    except ImportError as e:
        print(f"❌ Error loading Enhanced UI: {e}")
        print("💡 Running basic demo instead...")
        run_basic_demo()
    except Exception as e:
        print(f"❌ UI Error: {e}")
        print("💡 Falling back to demo mode...")
        run_basic_demo()


def create_mission_interactive(cc: CentralCommandCenter):
    """Interactive mission creation"""
    print("\n📋 CREATE NEW MISSION")
    print("-" * 20)
    
    name = input("Mission name: ").strip()
    if not name:
        print("❌ Mission name required")
        return
    
    description = input("Mission description (optional): ").strip()
    
    print("Priority levels: 1=Critical, 2=High, 3=Normal, 4=Low")
    priority_input = input("Priority (1-4, default 3): ").strip()
    
    from command_center import CommandPriority
    priority_map = {
        "1": CommandPriority.CRITICAL,
        "2": CommandPriority.HIGH,
        "3": CommandPriority.NORMAL,
        "4": CommandPriority.LOW
    }
    priority = priority_map.get(priority_input, CommandPriority.NORMAL)
    
    # Get target locations
    targets = []
    print("Enter target locations (x,y coordinates). Press enter with empty input to finish:")
    while True:
        coord_input = input(f"Target {len(targets)+1} (x,y): ").strip()
        if not coord_input:
            break
        try:
            x, y = map(int, coord_input.split(','))
            targets.append((x, y))
            print(f"✅ Added target at ({x}, {y})")
        except ValueError:
            print("❌ Invalid format. Use: x,y (e.g., 10,15)")
    
    if targets:
        mission_id = cc.create_mission(name, targets, priority, description)
        
        start = input("Start mission immediately? (y/n): ").strip().lower()
        if start == 'y':
            cc.start_mission(mission_id)
        
        print(f"✅ Mission '{name}' created with ID: {mission_id}")
    else:
        print("❌ No targets specified. Mission cancelled.")


def register_drone_interactive(cc: CentralCommandCenter):
    """Interactive drone registration"""
    print("\n🚁 REGISTER NEW DRONE")
    print("-" * 20)
    
    drone_id = input("Drone ID: ").strip()
    if not drone_id:
        print("❌ Drone ID required")
        return
    
    try:
        x = int(input("Initial X position: "))
        y = int(input("Initial Y position: "))
        battery = float(input("Battery level (0-100): "))
        
        from mcp_server.drone_tools import DroneInfo, DroneStatus
        drone_info = DroneInfo(drone_id, (x, y), DroneStatus.IDLE, battery)
        
        if cc.register_drone(drone_info):
            print(f"✅ Drone {drone_id} registered successfully")
        else:
            print(f"❌ Failed to register drone {drone_id}")
            
    except ValueError:
        print("❌ Invalid input format")


def report_survivor_interactive(cc: CentralCommandCenter):
    """Interactive survivor reporting"""
    print("\n🆘 REPORT SURVIVOR LOCATION")
    print("-" * 25)
    
    try:
        x = int(input("Survivor X position: "))
        y = int(input("Survivor Y position: "))
        
        from mcp_server.drone_tools import SurvivorInfo
        survivor_id = f"survivor_{int(time.time())}"
        survivor_info = SurvivorInfo(survivor_id, (x, y), False)
        
        cc.add_survivor_location(survivor_info)
        print(f"✅ Survivor reported at ({x}, {y})")
        
    except ValueError:
        print("❌ Invalid position format")


def issue_command_interactive(cc: CentralCommandCenter):
    """Interactive command issuing"""
    print("\n📡 ISSUE DIRECT COMMAND")
    print("-" * 20)
    
    drone_id = input("Target drone ID: ").strip()
    if not drone_id:
        print("❌ Drone ID required")
        return
    
    print("Available commands: move, rescue, charge, patrol, return")
    command = input("Command type: ").strip().lower()
    
    target_pos = None
    if command in ["move", "rescue"]:
        try:
            x = int(input("Target X position: "))
            y = int(input("Target Y position: "))
            target_pos = (x, y)
        except ValueError:
            print("❌ Invalid position format")
            return
    
    from command_center import CommandPriority
    order_id = cc.issue_command(drone_id, command, target_pos, CommandPriority.NORMAL)
    print(f"✅ Command issued with order ID: {order_id}")


def show_detailed_status(cc: CentralCommandCenter):
    """Show detailed system status"""
    print("\n📊 DETAILED SYSTEM STATUS")
    print("=" * 30)
    
    status = cc.get_system_status()
    
    print(f"\n🏢 Command Center Status: {status['command_center_status'].upper()}")
    print(f"⏱️  System Uptime: {status['system_uptime']}")
    print(f"🚁 Total Drones: {status['total_drones']}")
    print(f"🟢 Active Drones: {status['active_drones']}")
    print(f"📋 Active Missions: {status['active_missions']}")
    print(f"📡 Pending Orders: {status['pending_orders']}")
    print(f"✅ Completed Missions: {status['completed_missions']}")
    print(f"🆘 Total Rescues: {status['total_rescues']}")
    print(f"👥 Survivors Located: {status['survivor_count']}")
    
    print(f"\n🗺️  Drone Positions:")
    for drone_id, pos in status['drone_positions'].items():
        print(f"   {drone_id}: {pos}")
    
    # Show active missions
    print(f"\n📋 Active Missions:")
    for mission_id, mission in cc.active_missions.items():
        print(f"   {mission_id}: {mission.name} ({mission.status.value})")
        print(f"      Progress: {mission.completion_percentage:.1f}%")
        print(f"      Drones: {', '.join(mission.assigned_drones)}")
    
    input("\nPress any key to continue...")


import time


def run_basic_demo():
    """Run a basic simulation demo when advanced UIs are unavailable"""
    print("\n🤖 Running Basic Agentic AI Demo...")
    
    try:
        from simulation.simple_model import SimpleDroneSwarmModel
        from agent.memory import MissionMemory
        
        # Initialize components
        memory = MissionMemory()
        memory.clear_memory()
        memory.add_event("Basic demo started")
        
        model = SimpleDroneSwarmModel(n_drones=3, n_survivors=5, n_charging_stations=2)
        
        print("🚁 Simulation initialized:")
        print(f"   • Drones: {len([a for a in model.custom_agents if hasattr(a, 'battery')])}")
        print(f"   • Survivors: {len([a for a in model.custom_agents if hasattr(a, 'found')])}")
        
        # Run simulation steps
        print("\n🎮 Running simulation...")
        for step in range(20):
            model.step()
            
            if step % 5 == 0:
                active_drones = len([a for a in model.custom_agents 
                                   if hasattr(a, 'battery') and a.battery > 20])
                rescued = len([a for a in model.custom_agents 
                             if hasattr(a, 'found') and a.found])
                
                print(f"   Step {step:2d}: {active_drones} active drones, {rescued} rescued")
                memory.add_event(f"Step {step}: {active_drones} drones active, {rescued} rescued")
        
        print("\n✅ Demo completed successfully!")
        print("📝 Mission log created in logs/mission.log")
        
        print("\nPress any key to return to main menu...")
        try:
            input()
        except:
            pass
        main()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Please check system requirements and dependencies")


if __name__ == "__main__":
    main()