"""
Enhanced Tkinter Interactive UI
Supports terrain visualization, complex AI decision analysis, and detailed environment information
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import math
from simulation.enhanced_model import EnhancedDroneSwarmModel
from simulation.enhanced_drone_agent import EnhancedDroneAgent, SimpleSurvivorAgent, SimpleChargingStationAgent
from simulation.terrain_system import TerrainType, ObstacleType, WeatherCondition
from ui.enhanced_ui_components import (
    create_legend, create_control_panel, create_enhanced_analysis_panel,
    create_ai_reasoning_panel, create_terrain_analysis_panel
)
from ui.enhanced_ui_methods import EnhancedUIMethodsMixin

class EnhancedDroneUI(EnhancedUIMethodsMixin):
    """Enhanced drone control interface with terrain and complex AI analysis support"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚁 Enhanced Autonomous Drone Swarm Command System - Complex Terrain Edition")
        self.root.geometry("1800x1200")
        
        # Configure default font size
        self.root.option_add('*Font', 'Arial 12')
        self.root.option_add('*Label.Font', 'Arial 12')
        self.root.option_add('*Button.Font', 'Arial 12')
        self.root.option_add('*Checkbutton.Font', 'Arial 12')
        
        # Configure ttk styles
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12))
        style.configure('TButton', font=('Arial', 12), padding=(10, 5))
        style.configure('TCheckbutton', font=('Arial', 12))
        style.configure('TLabelFrame.Label', font=('Arial', 14, 'bold'))
        style.configure('Heading', font=('Arial', 12, 'bold'))
        
        # Model and state
        self.model = None
        self.auto_run = False
        self.selected_pos = (10, 10)
        self.canvas_size = 800  # Enlarged canvas
        self.cell_size = 40     # Enlarged grid cell
        self.zoom_level = 1.0   # Zoom level (0.5 to 2.0)
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        self.show_terrain = True
        self.show_height = False
        self.show_weather = False
        
        # Pan/scroll offset
        self.offset_x = 0
        self.offset_y = 0
        
        # Create UI
        self.create_widgets()
        self.create_model()
        
        # Initialize AI Reasoning display
        if hasattr(self, 'update_reasoning_displays'):
            self.update_reasoning_displays()
        
        # Start update loop
        self.update_display()
    
    def create_widgets(self):
        """Create UI components"""
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side: Grid visualization
        left_frame = ttk.LabelFrame(main_frame, text="🗺️ Complex Terrain Disaster Area Simulation", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Visualization options
        viz_frame = ttk.Frame(left_frame)
        viz_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.terrain_var = tk.BooleanVar(value=True)
        self.height_var = tk.BooleanVar(value=False)
        self.weather_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(viz_frame, text="Show Terrain", variable=self.terrain_var,
                       command=self.toggle_terrain_display).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(viz_frame, text="Show Height", variable=self.height_var,
                       command=self.toggle_height_display).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(viz_frame, text="Show Weather", variable=self.weather_var,
                       command=self.toggle_weather_display).pack(side=tk.LEFT)
        
        # Zoom controls
        zoom_frame = ttk.Frame(left_frame)
        zoom_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(zoom_frame, text="Zoom:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(zoom_frame, text="➖ Zoom Out", command=self.zoom_out, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="🔍 Reset", command=self.zoom_reset, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="➕ Zoom In", command=self.zoom_in, width=12).pack(side=tk.LEFT, padx=2)
        
        self.zoom_label = ttk.Label(zoom_frame, text="100%")
        self.zoom_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Grid canvas with scrollbars
        canvas_frame = ttk.Frame(left_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_size, height=self.canvas_size, 
                               bg='white', relief=tk.SUNKEN, borderwidth=2,
                               xscrollcommand=h_scrollbar.set,
                               yscrollcommand=v_scrollbar.set)
        
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_hover)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows/Mac
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux scroll down
        
        # Terrain info display
        self.terrain_info_label = ttk.Label(left_frame, text="Terrain Info: Click grid to view details", 
                                           font=('Arial', 12))
        self.terrain_info_label.pack(pady=5)
        
        # Legend
        create_legend(left_frame)
        
        # Right side: Control and analysis panels
        right_frame = ttk.Frame(main_frame, width=600)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Control panel at top
        create_control_panel(right_frame, self)
        
        # Create main notebook for all analysis tabs
        self.main_notebook = ttk.Notebook(right_frame)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Tab 1: AI Analysis & Status
        analysis_tab = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(analysis_tab, text="📊 Analysis & Status")
        create_enhanced_analysis_panel(analysis_tab, self)
        self.create_status_table(analysis_tab)
        
        # Tab 2: AI Reasoning
        reasoning_tab = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(reasoning_tab, text="🤔 AI Reasoning")
        create_ai_reasoning_panel(reasoning_tab, self)
        
        # Tab 3: Terrain Analysis
        terrain_tab = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(terrain_tab, text="🗺️ Terrain")
        create_terrain_analysis_panel(terrain_tab, self)
        
        # Tab 4: Mission Log
        log_tab = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(log_tab, text="📝 Mission Log")
        self.create_log_panel(log_tab)
    
    def create_status_table(self, parent):
        """Create status table"""
        table_frame = ttk.LabelFrame(parent, text="🚁 Drone Detailed Status", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create table
        columns = ("ID", "Battery", "Status", "Position", "Terrain", "Target")
        self.status_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        # Set column headers and widths
        column_widths = {"ID": 100, "Battery": 80, "Status": 100, "Position": 80, "Terrain": 120, "Target": 80}
        for col in columns:
            self.status_tree.heading(col, text=col)
            self.status_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.status_tree.yview)
        self.status_tree.configure(yscrollcommand=scrollbar.set)
        
        self.status_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_log_panel(self, parent):
        """Create log panel"""
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, font=('Courier', 10), wrap=tk.WORD,
                               yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
    
    def update_analysis(self):
        """Update AI analysis"""
        if not self.model:
            return
        
        analysis = self.model.get_ai_analysis()
        
        # Update metrics
        self.metrics_labels["Active Drones"].config(text=f"{analysis['active_drones']}/{analysis['total_drones']}")
        self.metrics_labels["Rescue Progress"].config(text=f"{analysis['rescued']}/{analysis['total_survivors']}")
        self.metrics_labels["Avg Battery"].config(text=f"{analysis['avg_battery']:.1f}%")
        self.metrics_labels["Terrain Challenges"].config(text=str(analysis['terrain_challenges']))
        self.metrics_labels["Weather Delays"].config(text=str(analysis['weather_delays']))
        self.metrics_labels["Rescue Success Rate"].config(text=f"{analysis['rescue_success_rate']:.1f}%")
        
        # Update terrain analysis
        terrain_analysis = analysis['terrain_analysis']
        terrain_text = f"Terrain Distribution: "
        for terrain, count in terrain_analysis['terrain_distribution'].items():
            percentage = (count / 400) * 100  # 20x20 = 400 cells
            terrain_text += f"{terrain}({percentage:.1f}%) "
        
        terrain_text += f"\nObstacles: {terrain_analysis['obstacle_count']} units"
        terrain_text += f"\nAvg Altitude: {terrain_analysis['avg_altitude']:.0f}m"
        
        weather_text = "Weather Distribution: "
        for weather, count in terrain_analysis['weather_conditions'].items():
            percentage = (count / 400) * 100
            weather_text += f"{weather}({percentage:.1f}%) "
        
        terrain_text += f"\n{weather_text}"
        
        self.terrain_stats_text.delete(1.0, tk.END)
        self.terrain_stats_text.insert(1.0, terrain_text)
    
    def update_status_table(self):
        """Update status table"""
        if not self.model:
            return
        
        # Clear table
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)
        
        # Add drone data
        drones = [a for a in self.model.custom_agents if isinstance(a, EnhancedDroneAgent)]
        
        for drone in drones:
            battery_icon = "🟢" if drone.battery > 60 else "🟡" if drone.battery > 30 else "🔴"
            
            # Get terrain info
            terrain_info = "Unknown"
            if drone.pos:
                terrain_cell = drone.get_current_terrain()
                if terrain_cell:
                    terrain_info = f"{terrain_cell.terrain_type.value}"
                    if terrain_cell.height > 500:
                        terrain_info += f"({terrain_cell.height:.0f}m)"
            
            position = f"({drone.pos[0]}, {drone.pos[1]})" if drone.pos else "Unknown"
            target = f"({drone.target[0]}, {drone.target[1]})" if drone.target else "None"
            
            self.status_tree.insert("", tk.END, values=(
                drone.unique_id,
                f"{battery_icon} {drone.battery}%",
                drone.status,
                position,
                terrain_info,
                target
            ))
    
    def log_message(self, message):
        """Add log message"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Limit log length
        lines = self.log_text.get(1.0, tk.END).split('\n')
        if len(lines) > 100:
            self.log_text.delete(1.0, f"{len(lines)-100}.0")
    
    def zoom_in(self):
        """Zoom in"""
        if self.zoom_level < self.max_zoom:
            self.zoom_level = min(self.max_zoom, self.zoom_level + 0.25)
            self.update_zoom()
            self.log_message(f"🔍 Zoomed in to {int(self.zoom_level * 100)}%")
    
    def zoom_out(self):
        """Zoom out"""
        if self.zoom_level > self.min_zoom:
            self.zoom_level = max(self.min_zoom, self.zoom_level - 0.25)
            self.update_zoom()
            self.log_message(f"🔍 Zoomed out to {int(self.zoom_level * 100)}%")
    
    def zoom_reset(self):
        """Reset zoom to 100%"""
        self.zoom_level = 1.0
        self.update_zoom()
        self.log_message("🔍 Zoom reset to 100%")
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel zoom"""
        # Windows/Mac
        if event.num == 4 or event.delta > 0:
            self.zoom_in()
        elif event.num == 5 or event.delta < 0:
            self.zoom_out()
    
    def update_zoom(self):
        """Update zoom level and redraw"""
        # Update zoom label
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        
        # Update canvas scroll region
        zoomed_size = int(20 * self.cell_size * self.zoom_level)
        self.canvas.config(scrollregion=(0, 0, zoomed_size, zoomed_size))
        
        # Redraw grid
        self.draw_grid()
    
    def update_display(self):
        """Update display"""
        self.draw_grid()
        self.update_analysis()
        self.update_status_table()
        
        # Periodic update
        self.root.after(1000, self.update_display)
    
    def run(self):
        """Run UI"""
        self.root.mainloop()

def main():
    """Main function"""
    print("🚁 Starting Enhanced Tkinter Interactive UI...")
    print("🗺️ Complex Terrain Features:")
    print("   • Multiple terrain types: Flat, Hills, Mountains, Water, Forest, Desert, etc.")
    print("   • Altitude differences: 0-2000m elevation, affecting movement cost and communication")
    print("   • Dynamic weather: Clear, Rain, Wind, Fog, Storm")
    print("   • Obstacle system: Buildings, Trees, Towers, Debris, etc.")
    print("🧠 AI Enhancement Features:")
    print("   • Multi-step reasoning: Environment perception → Threat assessment → Resource analysis → Mission planning → Path optimization → Decision execution")
    print("   • Complex path planning: A* algorithm considering terrain cost, non-linear distance")
    print("   • Dynamic adaptation: Real-time response to weather changes and terrain challenges")
    print("   • Detailed reasoning records: Complete AI thinking process visualization")
    
    app = EnhancedDroneUI()
    app.run()

if __name__ == "__main__":
    main()