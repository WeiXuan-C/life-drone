"""
Demo Script for Autonomous Drone Swarm Command System
Shows the system in action with a simple simulation
"""

import sys
import os
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.simple_model import SimpleDroneSwarmModel, SimpleDroneAgent, SimpleSurvivorAgent, SimpleChargingStationAgent

def print_grid(model):
    """Print a visual representation of the grid"""
    print("🗺️  Simulation Grid:")
    print("   " + "".join([f"{i:2d}" for i in range(min(model.width, 20))]))  # Limit display width
    
    for y in range(min(model.height, 20)):  # Limit display height
        row = f"{y:2d} "
        for x in range(min(model.width, 20)):
            cell_contents = model.grid.get_cell_list_contents([(x, y)])
            
            if not cell_contents:
                row += " ."
            else:
                # Priority: Charging Station > Drone > Survivor
                if any(isinstance(agent, SimpleChargingStationAgent) for agent in cell_contents):
                    row += " ⚡"
                elif any(isinstance(agent, SimpleDroneAgent) for agent in cell_contents):
                    drone = next(agent for agent in cell_contents if isinstance(agent, SimpleDroneAgent))
                    if drone.battery > 60:
                        row += " 🟢"  # Green drone (healthy)
                    elif drone.battery > 30:
                        row += " 🟡"  # Yellow drone (medium)
                    else:
                        row += " 🔴"  # Red drone (low battery)
                elif any(isinstance(agent, SimpleSurvivorAgent) for agent in cell_contents):
                    survivor = next(agent for agent in cell_contents if isinstance(agent, SimpleSurvivorAgent))
                    if survivor.found:
                        row += " ✅"  # Rescued survivor
                    else:
                        row += " 🆘"  # Survivor needs rescue
                else:
                    row += " ?"
        print(row)

def print_status(model):
    """Print system status"""
    drones = [a for a in model.custom_agents if isinstance(a, SimpleDroneAgent)]
    survivors = [a for a in model.custom_agents if isinstance(a, SimpleSurvivorAgent)]
    
    print(f"\n📊 System Status (Step {model.step_count}):")
    
    # Drone status
    print("🚁 Drones:")
    for drone in drones:
        battery_icon = "🟢" if drone.battery > 60 else "🟡" if drone.battery > 30 else "🔴"
        print(f"   {drone.unique_id}: {battery_icon} {drone.battery}% | {drone.status} | pos {drone.pos}")
    
    # Mission stats
    rescued = len([s for s in survivors if s.found])
    total_survivors = len(survivors)
    active_drones = len([d for d in drones if d.status != 'charging'])
    
    print(f"\n📈 Mission Progress:")
    print(f"   Active Drones: {active_drones}/{len(drones)}")
    print(f"   Survivors Rescued: {rescued}/{total_survivors}")
    if total_survivors > 0:
        print(f"   Success Rate: {rescued/total_survivors*100:.1f}%")

def run_demo():
    """Run the demonstration"""
    print("🚁 Autonomous Drone Swarm Command System - DEMO")
    print("=" * 60)
    print("This demo shows AI-driven drones rescuing survivors in a disaster zone.")
    print("🟢 = Healthy Drone | 🟡 = Medium Battery | 🔴 = Low Battery")
    print("🆘 = Survivor | ✅ = Rescued | ⚡ = Charging Station")
    print("=" * 60)
    
    # Create model
    print("🏗️  Setting up simulation...")
    model = SimpleDroneSwarmModel(
        width=15, height=15, 
        n_drones=3, n_survivors=6, 
        n_charging_stations=2
    )
    
    print("✅ Simulation ready!")
    print(f"   Grid: {model.width}x{model.height}")
    print(f"   Drones: {len([a for a in model.custom_agents if isinstance(a, SimpleDroneAgent)])}")
    print(f"   Survivors: {len([a for a in model.custom_agents if isinstance(a, SimpleSurvivorAgent)])}")
    print(f"   Charging Stations: {len([a for a in model.custom_agents if isinstance(a, SimpleChargingStationAgent)])}")
    
    input("\nPress ENTER to start the simulation...")
    
    # Run simulation
    try:
        for step in range(50):  # Run for 50 steps
            # Clear screen (works on most terminals)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print(f"🚁 Drone Swarm Simulation - Step {step + 1}/50")
            print("=" * 60)
            
            # Step the model
            model.step()
            
            # Display grid and status
            print_grid(model)
            print_status(model)
            
            # Show recent mission log
            if model.mission_log:
                print(f"\n📝 Latest Event: {model.mission_log[-1]}")
            
            # Check if all survivors are rescued
            survivors = [a for a in model.custom_agents if isinstance(a, SimpleSurvivorAgent)]
            rescued = len([s for s in survivors if s.found])
            
            if rescued == len(survivors):
                print("\n🎉 MISSION COMPLETE! All survivors rescued!")
                break
            
            # Wait before next step
            time.sleep(2)  # 2 seconds between steps
    
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL MISSION REPORT")
    print("=" * 60)
    
    drones = [a for a in model.custom_agents if isinstance(a, SimpleDroneAgent)]
    survivors = [a for a in model.custom_agents if isinstance(a, SimpleSurvivorAgent)]
    rescued = len([s for s in survivors if s.found])
    
    print(f"Mission Duration: {model.step_count} steps")
    print(f"Survivors Rescued: {rescued}/{len(survivors)} ({rescued/len(survivors)*100:.1f}%)")
    print(f"Mission Log Entries: {len(model.mission_log)}")
    
    # Show final drone status
    print(f"\n🚁 Final Drone Status:")
    for drone in drones:
        print(f"   {drone.unique_id}: {drone.battery}% battery, {drone.status}")
    
    print(f"\n🎯 System Features Demonstrated:")
    print("   ✅ AI-driven autonomous drone behavior")
    print("   ✅ Battery management and charging")
    print("   ✅ Survivor detection and rescue")
    print("   ✅ Real-time mission logging")
    print("   ✅ Grid-based spatial simulation")
    
    print(f"\n🔧 Ready for Integration:")
    print("   • FastMCP server for external control")
    print("   • LangGraph for complex workflows")
    print("   • Ollama/Qwen2 for advanced AI reasoning")
    print("   • Mesa visualization for web UI")
    
    print("\n🚀 To run the full system:")
    print("   python main.py")
    print("   python ui/console_ui.py")

if __name__ == "__main__":
    run_demo()