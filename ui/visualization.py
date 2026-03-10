"""
Mesa Visualization Components
Custom visualization elements for drone swarm simulation
"""

from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from simulation.drone_agent import DroneAgent, SurvivorAgent, ChargingStationAgent

class MissionLogElement(TextElement):
    """Display mission log in the UI"""
    
    def __init__(self):
        pass
    
    def render(self, model):
        # Get last 10 log entries
        recent_logs = model.mission_log[-10:] if len(model.mission_log) > 10 else model.mission_log
        log_html = "<h3>Mission Log</h3>"
        log_html += "<div style='height: 200px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; font-family: monospace; font-size: 12px;'>"
        
        for log_entry in recent_logs:
            log_html += f"<div>{log_entry}</div>"
        
        log_html += "</div>"
        return log_html


class ReasoningElement(TextElement):
    """Display AI reasoning process"""
    
    def __init__(self):
        pass
    
    def render(self, model):
        reasoning_html = "<h3>AI Reasoning Panel</h3>"
        reasoning_html += "<div style='height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; font-size: 12px;'>"
        
        # Get last 5 reasoning entries
        recent_reasoning = model.reasoning_log[-5:] if len(model.reasoning_log) > 5 else model.reasoning_log
        
        for entry in recent_reasoning:
            reasoning_html += f"""
            <div style='margin-bottom: 15px; padding: 10px; border-left: 3px solid #007bff; background-color: #f8f9fa;'>
                <strong>Drone {entry['drone_id']}</strong> [{entry['timestamp']}]<br>
                <strong>AI Thought:</strong> {entry['thought']}<br>
                <strong>Decision:</strong> {entry['decision']}<br>
                <strong>Tool Call:</strong> <code>{entry['action']}</code><br>
                <strong>Observation:</strong> {entry['observation']}
            </div>
            """
        
        if not recent_reasoning:
            reasoning_html += "<div style='color: #666; font-style: italic;'>No reasoning data available yet...</div>"
        
        reasoning_html += "</div>"
        return reasoning_html


class DroneStatusElement(TextElement):
    """Display drone status table"""
    
    def __init__(self):
        pass
    
    def render(self, model):
        drone_status = model.get_drone_status()
        
        status_html = "<h3>Drone Status Panel</h3>"
        status_html += """
        <table style='width: 100%; border-collapse: collapse; font-size: 12px;'>
            <thead>
                <tr style='background-color: #f8f9fa;'>
                    <th style='border: 1px solid #ddd; padding: 8px;'>Drone ID</th>
                    <th style='border: 1px solid #ddd; padding: 8px;'>Battery</th>
                    <th style='border: 1px solid #ddd; padding: 8px;'>Status</th>
                    <th style='border: 1px solid #ddd; padding: 8px;'>Position</th>
                    <th style='border: 1px solid #ddd; padding: 8px;'>Target</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for drone in drone_status:
            # Battery color coding
            battery_color = "#28a745" if drone['battery'] > 60 else "#ffc107" if drone['battery'] > 30 else "#dc3545"
            
            # Status color coding
            status_colors = {
                "idle": "#6c757d",
                "scanning": "#007bff", 
                "moving": "#17a2b8",
                "charging": "#28a745",
                "rescuing": "#fd7e14"
            }
            status_color = status_colors.get(drone['status'], "#6c757d")
            
            target_str = f"({drone['target'][0]}, {drone['target'][1]})" if drone['target'] else "None"
            
            status_html += f"""
            <tr>
                <td style='border: 1px solid #ddd; padding: 8px;'>{drone['id']}</td>
                <td style='border: 1px solid #ddd; padding: 8px; color: {battery_color}; font-weight: bold;'>{drone['battery']}%</td>
                <td style='border: 1px solid #ddd; padding: 8px; color: {status_color}; font-weight: bold;'>{drone['status']}</td>
                <td style='border: 1px solid #ddd; padding: 8px;'>({drone['position'][0]}, {drone['position'][1]})</td>
                <td style='border: 1px solid #ddd; padding: 8px;'>{target_str}</td>
            </tr>
            """
        
        status_html += """
            </tbody>
        </table>
        """
        
        return status_html


def agent_portrayal(agent):
    """Define how agents are displayed on the grid"""
    
    if isinstance(agent, DroneAgent):
        # Drone visualization with battery-based coloring
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "r": 0.8,
            "Layer": 2,
            "text": agent.unique_id.split('_')[1],  # Show drone number
            "text_color": "white"
        }
        
        # Color based on battery level
        if agent.battery > 60:
            portrayal["Color"] = "#28a745"  # Green - healthy
        elif agent.battery > 30:
            portrayal["Color"] = "#ffc107"  # Yellow - medium
        else:
            portrayal["Color"] = "#dc3545"  # Red - low battery
        
        # Add status indicator
        if agent.status == "charging":
            portrayal["stroke_color"] = "#17a2b8"
            portrayal["stroke_width"] = 3
        elif agent.status == "scanning":
            portrayal["stroke_color"] = "#007bff"
            portrayal["stroke_width"] = 2
        
        return portrayal
    
    elif isinstance(agent, SurvivorAgent):
        # Survivor signal visualization
        portrayal = {
            "Shape": "rect",
            "w": 0.6,
            "h": 0.6,
            "Filled": "true",
            "Layer": 1,
            "text": "S",
            "text_color": "white"
        }
        
        if agent.found:
            portrayal["Color"] = "#6c757d"  # Gray - rescued
            portrayal["text"] = "✓"
        else:
            portrayal["Color"] = "#dc3545"  # Red - needs rescue
        
        return portrayal
    
    elif isinstance(agent, ChargingStationAgent):
        # Charging station visualization
        portrayal = {
            "Shape": "rect",
            "w": 0.9,
            "h": 0.9,
            "Filled": "true",
            "Color": "#28a745",  # Green
            "Layer": 0,
            "text": "⚡",
            "text_color": "white"
        }
        
        return portrayal
    
    return {}


# Grid visualization
grid = CanvasGrid(agent_portrayal, 20, 20, 600, 600)

# Charts for monitoring
battery_chart = ChartModule([
    {"Label": "Average_Battery", "Color": "#28a745"}
], data_collector_name='datacollector')

activity_chart = ChartModule([
    {"Label": "Active_Drones", "Color": "#007bff"},
    {"Label": "Survivors_Found", "Color": "#dc3545"}
], data_collector_name='datacollector')

# Text elements
mission_log = MissionLogElement()
reasoning_panel = ReasoningElement()
drone_status = DroneStatusElement()

# User parameters for dynamic control
model_params = {
    "n_drones": UserSettableParameter(
        "slider", "Number of Drones", 3, 1, 10, 1,
        description="Choose how many drones to deploy"
    ),
    "n_survivors": UserSettableParameter(
        "slider", "Number of Survivors", 5, 1, 15, 1,
        description="Choose how many survivor signals to generate"
    ),
    "n_charging_stations": UserSettableParameter(
        "slider", "Charging Stations", 2, 1, 4, 1,
        description="Choose number of charging stations"
    ),
    "width": 20,
    "height": 20
}