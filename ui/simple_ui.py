"""
Simple Mesa 3.x Compatible UI
Using the new Mesa visualization system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mesa
from simulation.model import DroneSwarmModel
from simulation.drone_agent import DroneAgent, SurvivorAgent, ChargingStationAgent

def agent_portrayal(agent):
    """Define how agents are displayed"""
    if isinstance(agent, DroneAgent):
        # Drone visualization with battery-based coloring
        color = "#28a745" if agent.battery > 60 else "#ffc107" if agent.battery > 30 else "#dc3545"
        return {
            "color": color,
            "size": 20,
            "shape": "circle",
            "layer": 2
        }
    
    elif isinstance(agent, SurvivorAgent):
        # Survivor signal visualization
        color = "#6c757d" if agent.found else "#dc3545"
        return {
            "color": color,
            "size": 15,
            "shape": "rect",
            "layer": 1
        }
    
    elif isinstance(agent, ChargingStationAgent):
        # Charging station visualization
        return {
            "color": "#28a745",
            "size": 25,
            "shape": "rect",
            "layer": 0
        }

def run_simple_ui():
    """Run the simple Mesa 3.x UI"""
    
    # Create model
    model = DroneSwarmModel(width=20, height=20, n_drones=3, n_survivors=5, n_charging_stations=2)
    
    # Create visualization using new Mesa 3.x API
    try:
        # Try using SolaraViz (new Mesa 3.x visualization)
        page = mesa.visualization.SolaraViz(
            model,
            components=[
                mesa.visualization.make_space_component(agent_portrayal),
                "DataCollector"
            ],
            model_params={
                "n_drones": {
                    "type": "SliderInt",
                    "value": 3,
                    "label": "Number of Drones",
                    "min": 1,
                    "max": 10,
                    "step": 1
                },
                "n_survivors": {
                    "type": "SliderInt", 
                    "value": 5,
                    "label": "Number of Survivors",
                    "min": 1,
                    "max": 15,
                    "step": 1
                }
            },
            name="Drone Swarm Command System"
        )
        
        # This will start the Solara server
        page.launch()
        
    except Exception as e:
        print(f"SolaraViz error: {e}")
        print("Falling back to console simulation...")
        run_console_simulation()

def run_console_simulation():
    """Run simulation in console mode"""
    print("🚁 Autonomous Drone Swarm Command System - Console Mode")
    print("=" * 60)
    
    # Create model
    model = DroneSwarmModel(width=20, height=20, n_drones=3, n_survivors=5, n_charging_stations=2)
    
    print(f"📊 Initial State:")
    print(f"   Grid: {model.width}x{model.height}")
    print(f"   Drones: {len([a for a in model.schedule.agents if isinstance(a, DroneAgent)])}")
    print(f"   Survivors: {len([a for a in model.schedule.agents if isinstance(a, SurvivorAgent)])}")
    print(f"   Charging Stations: {len([a for a in model.schedule.agents if isinstance(a, ChargingStationAgent)])}")
    
    print("\n🎮 Running simulation (press Ctrl+C to stop)...")
    
    try:
        step = 0
        while step < 100:  # Run for 100 steps
            model.step()
            step += 1
            
            if step % 10 == 0:
                # Print status every 10 steps
                drones = [a for a in model.schedule.agents if isinstance(a, DroneAgent)]
                survivors = [a for a in model.schedule.agents if isinstance(a, SurvivorAgent)]
                
                active_drones = len([d for d in drones if d.status != 'charging'])
                rescued_survivors = len([s for s in survivors if s.found])
                avg_battery = sum([d.battery for d in drones]) / len(drones) if drones else 0
                
                print(f"Step {step:3d}: {active_drones} active drones, {rescued_survivors} rescued, avg battery: {avg_battery:.1f}%")
                
                # Show recent mission log
                if model.mission_log:
                    print(f"         Latest: {model.mission_log[-1]}")
    
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user")
    
    print(f"\n📊 Final Results after {step} steps:")
    drones = [a for a in model.schedule.agents if isinstance(a, DroneAgent)]
    survivors = [a for a in model.schedule.agents if isinstance(a, SurvivorAgent)]
    rescued = len([s for s in survivors if s.found])
    
    print(f"   Survivors rescued: {rescued}/{len(survivors)} ({rescued/len(survivors)*100:.1f}%)")
    print(f"   Mission log entries: {len(model.mission_log)}")
    print(f"   AI reasoning entries: {len(model.reasoning_log)}")
    
    # Show drone final status
    print(f"\n🚁 Final Drone Status:")
    for drone in drones:
        print(f"   {drone.unique_id}: {drone.battery}% battery, {drone.status}, pos {drone.pos}")

if __name__ == "__main__":
    print("🚁 Starting Simple Mesa UI...")
    print("📊 Compatible with Mesa 3.x")
    
    try:
        run_simple_ui()
    except Exception as e:
        print(f"UI Error: {e}")
        print("Running console simulation instead...")
        run_console_simulation()