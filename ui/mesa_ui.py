"""
Mesa UI for Autonomous Drone Swarm Command System
Interactive simulation dashboard for disaster rescue operations
"""

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from simulation.model import DroneSwarmModel
from ui.visualization import (
    grid, battery_chart, activity_chart, mission_log, 
    reasoning_panel, drone_status, model_params
)

def launch_server():
    """Launch the Mesa visualization server"""
    
    # Create the server with all visualization elements
    server = ModularServer(
        DroneSwarmModel,
        [
            grid,                # Main simulation grid (top-left)
            drone_status,        # Drone status table (top-right)
            reasoning_panel,     # AI reasoning display (middle-right)
            mission_log,         # Mission log (bottom-right)
            battery_chart,       # Battery monitoring chart (bottom-left)
            activity_chart       # Activity monitoring chart (bottom-left)
        ],
        "Autonomous Drone Swarm Command System",
        model_params
    )
    
    # Configure server
    server.port = 8521
    server.launch()

if __name__ == "__main__":
    print("🚁 Starting Autonomous Drone Swarm Command System...")
    print("📊 Dashboard will open at: http://localhost:8521")
    print("🎮 Use the controls to:")
    print("   • Adjust number of drones and survivors")
    print("   • Start/Stop simulation")
    print("   • Monitor AI decision making")
    print("   • View mission logs")
    print("\n🔧 Integration ready for:")
    print("   • FastMCP server integration")
    print("   • LangGraph workflow orchestration") 
    print("   • Ollama/Qwen2 AI reasoning")
    print("\n🚀 Launching server...")
    
    launch_server()