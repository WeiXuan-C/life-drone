"""
Enhanced UI main method implementation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
import time
from simulation.enhanced_model import EnhancedDroneSwarmModel
from simulation.enhanced_drone_agent import EnhancedDroneAgent, SimpleSurvivorAgent, SimpleChargingStationAgent
from simulation.terrain_system import TerrainType, ObstacleType, WeatherCondition
from ui.enhanced_ui_components import get_terrain_color, get_obstacle_symbol, get_weather_symbol

class EnhancedUIMethodsMixin:
    """Enhanced UI methods mixin class"""
    
    def create_model(self):
        """Create enhanced simulation model"""
        self.model = EnhancedDroneSwarmModel(
            width=20, height=20,
            n_drones=3, n_survivors=5,
            n_charging_stations=2,
            terrain_seed=42
        )
        self.log_message("✅ Enhanced simulation system initialized")
        self.log_message(f"🗺️ Complex terrain generation: Includes mountains, water, forests, and various terrain types")
        self.log_message(f"🌦️ Dynamic weather system: Supports clear, rain, wind, fog, storm")
        self.log_message(f"🚧 Obstacle system: Buildings, trees, towers, etc. affect navigation")
    
    def regenerate_terrain(self):
        """Regenerate terrain"""
        if messagebox.askyesno("Regenerate Terrain", "This will reset all agents and generate new terrain. Continue?"):
            seed = self.terrain_seed_var.get()
            self.model = EnhancedDroneSwarmModel(
                width=20, height=20,
                n_drones=3, n_survivors=5,
                n_charging_stations=2,
                terrain_seed=seed
            )
            self.log_message(f"🗺️ Regenerated terrain using seed {seed}")
            self.update_reasoning_displays()
    
    def toggle_terrain_display(self):
        """Toggle terrain display"""
        self.show_terrain = self.terrain_var.get()
        self.log_message(f"🎨 Terrain display: {'Enabled' if self.show_terrain else 'Disabled'}")
    
    def toggle_height_display(self):
        """Toggle height display"""
        self.show_height = self.height_var.get()
        self.log_message(f"📏 Height display: {'Enabled' if self.show_height else 'Disabled'}")
    
    def toggle_weather_display(self):
        """Toggle weather display"""
        self.show_weather = self.weather_var.get()
        self.log_message(f"🌤️ Weather display: {'Enabled' if self.show_weather else 'Disabled'}")
    
    def on_canvas_click(self, event):
        """Handle canvas click event"""
        # Account for zoom and scroll
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        cell_size_zoomed = self.cell_size * self.zoom_level
        x = int(canvas_x // cell_size_zoomed)
        y = int(canvas_y // cell_size_zoomed)
        
        if 0 <= x < 20 and 0 <= y < 20:
            self.x_var.set(x)
            self.y_var.set(y)
            self.selected_pos = (x, y)
            
            # Show detailed terrain info
            self.show_terrain_info(x, y)
    
    def on_canvas_hover(self, event):
        """Handle mouse hover event"""
        # Account for zoom and scroll
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        cell_size_zoomed = self.cell_size * self.zoom_level
        x = int(canvas_x // cell_size_zoomed)
        y = int(canvas_y // cell_size_zoomed)
        
        if 0 <= x < 20 and 0 <= y < 20 and self.model:
            terrain_info = self.model.get_terrain_info(x, y)
            if terrain_info:
                info_text = (f"({x},{y}) {terrain_info['terrain_type']} "
                           f"Altitude {terrain_info['height']:.0f}m "
                           f"{terrain_info['weather']}")
                if terrain_info['obstacle']:
                    info_text += f" {terrain_info['obstacle']}"
                
                self.terrain_info_label.config(text=f"Terrain Info: {info_text}")
    
    def show_terrain_info(self, x, y):
        """Show detailed terrain info"""
        if not self.model:
            return
        
        terrain_info = self.model.get_terrain_info(x, y)
        if terrain_info:
            info_msg = f"""Position ({x}, {y}) Details:
            
🗺️ Terrain Type: {terrain_info['terrain_type']}
📏 Altitude: {terrain_info['height']:.1f} meters
🌤️ Weather Condition: {terrain_info['weather']}
🚧 Obstacle: {terrain_info['obstacle'] or 'None'}
⚡ Movement Cost: {terrain_info['movement_cost']:.2f}
🔍 Scan Efficiency: {terrain_info['scan_efficiency']:.2f}
📡 Communication Quality: {terrain_info['communication_quality']:.2f}
👁️ Visibility: {terrain_info['visibility']:.2f}
💨 Wind Speed: {terrain_info['wind_speed']:.1f} m/s"""
            
            messagebox.showinfo("Terrain Details", info_msg)
    
    def add_drone(self):
        """Add drone"""
        if not self.model:
            return
        
        x, y = self.x_var.get(), self.y_var.get()
        battery = self.battery_var.get()
        
        drone, message = self.model.add_drone_manually(x, y, battery)
        
        if drone:
            self.log_message(f"🚁 {message}")
            messagebox.showinfo("Add Successful", f"Drone {drone.unique_id} added\n{message}")
            self.update_reasoning_displays()
        else:
            self.log_message(f"❌ Add failed: {message}")
            messagebox.showwarning("Add Failed", message)
    
    def add_survivor(self):
        """Add survivor"""
        if not self.model:
            return
        
        x, y = self.x_var.get(), self.y_var.get()
        
        survivor, message = self.model.add_survivor_manually(x, y)
        
        if survivor:
            self.log_message(f"🆘 {message}")
            messagebox.showinfo("Add Successful", f"Survivor {survivor.unique_id} added\n{message}")
        else:
            self.log_message(f"❌ Add failed: {message}")
            messagebox.showwarning("Add Failed", message)
    
    def add_charging_station(self):
        """Add charging station"""
        if not self.model:
            return
        
        x, y = self.x_var.get(), self.y_var.get()
        
        station, message = self.model.add_charging_station_manually(x, y)
        
        if station:
            self.log_message(f"⚡ {message}")
            messagebox.showinfo("Add Successful", f"Charging station {station.unique_id} added\n{message}")
        else:
            self.log_message(f"❌ Add failed: {message}")
            messagebox.showwarning("Add Failed", message)
    
    def step_simulation(self):
        """Execute one simulation step"""
        if self.model:
            self.model.step()
            self.log_message(f"▶️ Executed step {self.model.step_count}")
            self.update_reasoning_displays()
    
    def toggle_auto_run(self):
        """Toggle auto run"""
        self.auto_run = self.auto_var.get()
        if self.auto_run:
            self.log_message("🔄 Auto run mode started")
            self.auto_run_thread()
        else:
            self.log_message("⏸️ Auto run mode stopped")
    
    def auto_run_thread(self):
        """Auto run thread"""
        def run():
            while self.auto_run and self.model:
                self.model.step()
                self.update_reasoning_displays()
                time.sleep(2)  # 2 second interval for observing AI reasoning
        
        import threading
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def reset_simulation(self):
        """Reset simulation"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the simulation? This will clear all current data."):
            self.auto_var.set(False)
            self.auto_run = False
            self.create_model()
            self.update_reasoning_displays()
            self.log_message("🔄 Simulation reset")
    
    def draw_grid(self):
        """Draw enhanced grid"""
        self.canvas.delete("all")
        
        if not self.model:
            return
        
        # Calculate zoomed cell size
        cell_size_zoomed = self.cell_size * self.zoom_level
        
        # Draw terrain background
        for y in range(20):
            for x in range(20):
                x1 = x * cell_size_zoomed
                y1 = y * cell_size_zoomed
                x2 = (x + 1) * cell_size_zoomed
                y2 = (y + 1) * cell_size_zoomed
                
                terrain_cell = self.model.terrain[y][x]
                
                # Get terrain color
                if self.show_terrain:
                    color = get_terrain_color(
                        terrain_cell.terrain_type,
                        terrain_cell.height if self.show_height else 0,
                        terrain_cell.weather if self.show_weather else None,
                        terrain_cell.obstacle
                    )
                else:
                    color = "#F0F0F0"  # Default light gray
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="lightgray")
                
                # Show height info (scale font with zoom)
                if self.show_height and terrain_cell.height > 100:
                    height_text = f"{int(terrain_cell.height)}"
                    font_size = max(7, int(9 * self.zoom_level))
                    self.canvas.create_text((x1+x2)/2, y1+8*self.zoom_level, text=height_text, 
                                          font=('Arial', font_size), fill="black")
                
                # Show obstacles (scale font with zoom)
                if terrain_cell.obstacle:
                    obstacle_symbol = get_obstacle_symbol(terrain_cell.obstacle)
                    font_size = max(10, int(16 * self.zoom_level))
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2-5*self.zoom_level, text=obstacle_symbol, 
                                          font=('Arial', font_size))
                
                # Show weather (scale font with zoom)
                if self.show_weather and terrain_cell.weather != WeatherCondition.CLEAR:
                    weather_symbol = get_weather_symbol(terrain_cell.weather)
                    font_size = max(10, int(14 * self.zoom_level))
                    self.canvas.create_text(x2-8*self.zoom_level, y1+8*self.zoom_level, text=weather_symbol, 
                                          font=('Arial', font_size))
        
        # Draw agents
        for agent in self.model.custom_agents:
            if agent.pos:
                self.draw_agent(agent)
        
        # Highlight selected position (account for zoom)
        x, y = self.x_var.get(), self.y_var.get()
        x1 = x * cell_size_zoomed
        y1 = y * cell_size_zoomed
        x2 = (x + 1) * cell_size_zoomed
        y2 = (y + 1) * cell_size_zoomed
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=max(2, int(3*self.zoom_level)), fill="", stipple="gray25")
    
    def draw_agent(self, agent):
        """Draw agent"""
        cell_size_zoomed = self.cell_size * self.zoom_level
        x, y = agent.pos
        padding = 3 * self.zoom_level
        x1 = x * cell_size_zoomed + padding
        y1 = y * cell_size_zoomed + padding
        x2 = (x + 1) * cell_size_zoomed - padding
        y2 = (y + 1) * cell_size_zoomed - padding
        
        if isinstance(agent, EnhancedDroneAgent):
            # Enhanced drone visualization
            if agent.battery > 60:
                color = "green"
            elif agent.battery > 30:
                color = "orange"
            else:
                color = "red"
            
            # Status border
            outline_colors = {
                "idle": "black",
                "scanning": "blue",
                "rescue_mission": "purple",
                "charging": "cyan",
                "emergency_return": "red",
                "weather_hold": "gray",
                "area_scan": "lightblue"
            }
            outline = outline_colors.get(agent.status, "black")
            
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline=outline, width=max(1, int(2*self.zoom_level)))
            
            # Show drone ID (scale font with zoom)
            drone_id = agent.unique_id.split('_')[-1]
            font_size = max(8, int(12 * self.zoom_level))
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=drone_id, 
                                  fill="white", font=('Arial', font_size, 'bold'))
            
            # Show path planning
            if hasattr(agent, 'planned_path') and agent.planned_path:
                self.draw_planned_path(agent.planned_path, agent.current_path_index)
        
        elif isinstance(agent, SimpleSurvivorAgent):
            color = "gray" if agent.found else "red"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            text = "✓" if agent.found else "S"
            font_size = max(8, int(12 * self.zoom_level))
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=text, 
                                  fill="white", font=('Arial', font_size, 'bold'))
        
        elif isinstance(agent, SimpleChargingStationAgent):
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="cyan", outline="black", width=max(1, int(2*self.zoom_level)))
            font_size = max(10, int(16 * self.zoom_level))
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="⚡", font=('Arial', font_size))
    
    def draw_planned_path(self, path, current_index):
        """Draw planned path"""
        if len(path) < 2:
            return
        
        cell_size_zoomed = self.cell_size * self.zoom_level
        
        for i in range(current_index, len(path) - 1):
            y1, x1 = path[i]
            y2, x2 = path[i + 1]
            
            # Convert to canvas coordinates (account for zoom)
            canvas_x1 = x1 * cell_size_zoomed + cell_size_zoomed // 2
            canvas_y1 = y1 * cell_size_zoomed + cell_size_zoomed // 2
            canvas_x2 = x2 * cell_size_zoomed + cell_size_zoomed // 2
            canvas_y2 = y2 * cell_size_zoomed + cell_size_zoomed // 2
            
            # Draw path line (scale width with zoom)
            color = "yellow" if i == current_index else "orange"
            line_width = max(1, int(2 * self.zoom_level))
            self.canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                                  fill=color, width=line_width, dash=(3, 3))
    
    def update_reasoning_displays(self):
        """Update AI reasoning display"""
        if not self.model:
            return
        
        drones = [a for a in self.model.custom_agents if isinstance(a, EnhancedDroneAgent)]
        
        # Clear old tabs
        for tab_id in self.reasoning_notebook.tabs():
            self.reasoning_notebook.forget(tab_id)
        
        self.reasoning_displays = {}
        
        # Create reasoning display for each drone
        for drone in drones:
            frame = ttk.Frame(self.reasoning_notebook, padding=5)
            self.reasoning_notebook.add(frame, text=f"🚁 {drone.unique_id}")
            
            # Create frame for text widget and scrollbar
            text_frame = ttk.Frame(frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create scrolled text area with scrollbar
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(text_frame, height=12, font=('Courier', 10), wrap=tk.WORD,
                                yscrollcommand=scrollbar.set)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=text_widget.yview)
            
            self.reasoning_displays[drone.unique_id] = text_widget
            
            # Show reasoning history
            self.update_drone_reasoning_display(drone)
    
    def update_drone_reasoning_display(self, drone):
        """Update single drone reasoning display"""
        if drone.unique_id not in self.reasoning_displays:
            return
        
        text_widget = self.reasoning_displays[drone.unique_id]
        text_widget.delete(1.0, tk.END)
        
        # Show current status
        current_terrain = drone.get_current_terrain()
        terrain_info = "Unknown terrain"
        if current_terrain:
            terrain_info = f"{current_terrain.terrain_type.value}(Altitude {current_terrain.height:.0f}m)"
            if current_terrain.weather != WeatherCondition.CLEAR:
                terrain_info += f",{current_terrain.weather.value}"
        
        status_text = f"""🚁 Drone {drone.unique_id} Current Status:
📍 Position: {drone.pos}
🔋 Battery: {drone.battery}%
📊 Status: {drone.status}
🗺️ Terrain: {terrain_info}
🎯 Target: {drone.target or 'None'}
📏 Total Distance: {drone.total_distance_traveled:.1f}
🆘 Successful Rescues: {drone.successful_rescues}
❌ Failed Attempts: {drone.failed_attempts}

🧠 AI Reasoning History:
{'='*50}
"""
        
        text_widget.insert(tk.END, status_text)
        
        # Show reasoning history
        for i, decision in enumerate(drone.decision_history[-5:]):  # Show last 5 decisions
            reasoning_text = f"""
Decision {len(drone.decision_history) - 4 + i} [{decision.get('timestamp', 'N/A')}]:
💭 AI Thought: {decision['thought']}
🎯 Decision: {decision['decision']}
⚡ Action: {decision['action']}
👁️ Observation: {decision['observation']}
🗺️ Terrain Environment: {decision['terrain_info']}

🔍 Detailed Reasoning Steps:"""
            
            text_widget.insert(tk.END, reasoning_text)
            
            for j, step in enumerate(decision.get('reasoning_steps', [])):
                text_widget.insert(tk.END, f"\n   {j+1}. {step}")
            
            text_widget.insert(tk.END, f"\n{'-'*50}\n")
        
        # Scroll to bottom
        text_widget.see(tk.END)