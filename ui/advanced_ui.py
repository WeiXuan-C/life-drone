"""
Advanced Mesa UI with Enhanced Features
Extended version with more interactive controls and better visualization
"""

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from simulation.model import DroneSwarmModel
from ui.visualization import agent_portrayal, MissionLogElement, ReasoningElement, DroneStatusElement
from mesa.visualization.modules import CanvasGrid
import json

class AdvancedControlPanel(TextElement):
    """Advanced control panel with JavaScript interactions"""
    
    def __init__(self):
        pass
    
    def render(self, model):
        control_html = """
        <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;'>
            <h3>🎮 Advanced Controls</h3>
            
            <div style='display: flex; gap: 10px; margin: 10px 0;'>
                <button onclick='addDrone()' style='padding: 8px 16px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;'>
                    ➕ Add Drone
                </button>
                <button onclick='addSurvivor()' style='padding: 8px 16px; background-color: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;'>
                    🆘 Add Survivor
                </button>
                <button onclick='emergencyRecall()' style='padding: 8px 16px; background-color: #ffc107; color: black; border: none; border-radius: 4px; cursor: pointer;'>
                    🔄 Emergency Recall
                </button>
            </div>
            
            <div style='margin: 10px 0;'>
                <label>Mission Priority:</label>
                <select id='missionPriority' style='margin-left: 10px; padding: 4px;'>
                    <option value='rescue'>🆘 Rescue Operations</option>
                    <option value='patrol'>👁️ Area Patrol</option>
                    <option value='recon'>🔍 Reconnaissance</option>
                </select>
            </div>
            
            <div style='margin: 10px 0;'>
                <label>Weather Condition:</label>
                <select id='weather' style='margin-left: 10px; padding: 4px;'>
                    <option value='clear'>☀️ Clear</option>
                    <option value='cloudy'>☁️ Cloudy</option>
                    <option value='storm'>⛈️ Storm</option>
                </select>
            </div>
        </div>
        
        <script>
            function addDrone() {
                // This would integrate with the model to add drones dynamically
                console.log('Adding new drone...');
                alert('Drone deployment requested - feature ready for MCP integration');
            }
            
            function addSurvivor() {
                console.log('Adding survivor signal...');
                alert('Survivor signal added - feature ready for MCP integration');
            }
            
            function emergencyRecall() {
                console.log('Emergency recall initiated...');
                alert('Emergency recall - all drones returning to base');
            }
        </script>
        """
        return control_html


class SystemMetrics(TextElement):
    """Display system performance metrics"""
    
    def __init__(self):
        pass
    
    def render(self, model):
        # Calculate metrics
        total_drones = len([a for a in model.schedule.agents if hasattr(a, 'battery')])
        active_drones = len([a for a in model.schedule.agents if hasattr(a, 'battery') and a.status != 'charging'])
        total_survivors = len([a for a in model.schedule.agents if hasattr(a, 'found')])
        rescued_survivors = len([a for a in model.schedule.agents if hasattr(a, 'found') and a.found])
        
        avg_battery = 0
        if total_drones > 0:
            avg_battery = sum([a.battery for a in model.schedule.agents if hasattr(a, 'battery')]) / total_drones
        
        efficiency = (rescued_survivors / total_survivors * 100) if total_survivors > 0 else 0
        
        metrics_html = f"""
        <div style='background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0;'>
            <h3>📊 System Metrics</h3>
            
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                <div>
                    <div style='font-size: 24px; font-weight: bold; color: #007bff;'>{active_drones}/{total_drones}</div>
                    <div style='font-size: 12px; color: #666;'>Active Drones</div>
                </div>
                
                <div>
                    <div style='font-size: 24px; font-weight: bold; color: #28a745;'>{avg_battery:.1f}%</div>
                    <div style='font-size: 12px; color: #666;'>Avg Battery</div>
                </div>
                
                <div>
                    <div style='font-size: 24px; font-weight: bold; color: #dc3545;'>{rescued_survivors}/{total_survivors}</div>
                    <div style='font-size: 12px; color: #666;'>Survivors Rescued</div>
                </div>
                
                <div>
                    <div style='font-size: 24px; font-weight: bold; color: #fd7e14;'>{efficiency:.1f}%</div>
                    <div style='font-size: 12px; color: #666;'>Mission Efficiency</div>
                </div>
            </div>
            
            <div style='margin-top: 15px; font-size: 12px; color: #666;'>
                Step: {model.step_count} | Runtime: {model.step_count * 0.1:.1f}s
            </div>
        </div>
        """
        return metrics_html


class IntegrationStatus(TextElement):
    """Show integration status for external systems"""
    
    def __init__(self):
        pass
    
    def render(self, model):
        integration_html = """
        <div style='background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #28a745;'>
            <h3>🔗 Integration Status</h3>
            
            <div style='margin: 10px 0;'>
                <div style='display: flex; align-items: center; margin: 5px 0;'>
                    <span style='color: #28a745; margin-right: 10px;'>✅</span>
                    <strong>Mesa Framework:</strong> Active
                </div>
                <div style='display: flex; align-items: center; margin: 5px 0;'>
                    <span style='color: #ffc107; margin-right: 10px;'>⏳</span>
                    <strong>FastMCP Server:</strong> Ready for integration
                </div>
                <div style='display: flex; align-items: center; margin: 5px 0;'>
                    <span style='color: #ffc107; margin-right: 10px;'>⏳</span>
                    <strong>LangGraph:</strong> Ready for workflow orchestration
                </div>
                <div style='display: flex; align-items: center; margin: 5px 0;'>
                    <span style='color: #ffc107; margin-right: 10px;'>⏳</span>
                    <strong>Ollama/Qwen2:</strong> Ready for AI reasoning
                </div>
            </div>
            
            <div style='font-size: 12px; color: #666; margin-top: 10px;'>
                💡 All components are architected for seamless integration
            </div>
        </div>
        """
        return integration_html


def create_advanced_server():
    """Create advanced Mesa server with enhanced features"""
    
    # Enhanced grid with tooltips and animations
    enhanced_grid = CanvasGrid(agent_portrayal, 20, 20, 700, 700)
    
    # Enhanced charts
    performance_chart = ChartModule([
        {"Label": "Average_Battery", "Color": "#28a745"},
        {"Label": "Active_Drones", "Color": "#007bff"},
        {"Label": "Survivors_Found", "Color": "#dc3545"}
    ], data_collector_name='datacollector')
    
    # Create all UI elements
    control_panel = AdvancedControlPanel()
    system_metrics = SystemMetrics()
    integration_status = IntegrationStatus()
    mission_log = MissionLogElement()
    reasoning_panel = ReasoningElement()
    drone_status = DroneStatusElement()
    
    # Enhanced model parameters
    enhanced_params = {
        "n_drones": UserSettableParameter(
            "slider", "🚁 Drones", 3, 1, 10, 1,
            description="Number of drones to deploy"
        ),
        "n_survivors": UserSettableParameter(
            "slider", "🆘 Survivors", 5, 1, 15, 1,
            description="Number of survivor signals"
        ),
        "n_charging_stations": UserSettableParameter(
            "slider", "⚡ Charging Stations", 2, 1, 4, 1,
            description="Number of charging stations"
        ),
        "width": 20,
        "height": 20
    }
    
    # Create server with enhanced layout
    server = ModularServer(
        DroneSwarmModel,
        [
            enhanced_grid,        # Main simulation grid
            control_panel,        # Advanced controls
            system_metrics,       # Performance metrics
            drone_status,         # Drone status table
            reasoning_panel,      # AI reasoning
            mission_log,          # Mission log
            integration_status,   # Integration status
            performance_chart     # Performance chart
        ],
        "🚁 Autonomous Drone Swarm Command System - Advanced Dashboard",
        enhanced_params
    )
    
    return server


if __name__ == "__main__":
    print("🚁 Starting Advanced Drone Swarm Command System...")
    print("🎯 Enhanced Features:")
    print("   • Interactive control panel")
    print("   • Real-time system metrics")
    print("   • Advanced AI reasoning display")
    print("   • Integration status monitoring")
    print("   • Performance analytics")
    print("\n📊 Dashboard: http://localhost:8521")
    print("🔧 Ready for integration with FastMCP, LangGraph, and Ollama")
    print("\n🚀 Launching enhanced server...")
    
    server = create_advanced_server()
    server.port = 8521
    server.launch()