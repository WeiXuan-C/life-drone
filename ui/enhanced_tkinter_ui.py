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

# MANDATORY: Import RescueAgent for LangGraph workflow
from agent.rescue_agent import get_rescue_agent, RescueAgent

class EnhancedDroneUI(EnhancedUIMethodsMixin):
    """Enhanced drone control interface with terrain and complex AI analysis support"""
    
    def __init__(self):
        print("🚁 Initializing Enhanced Terrain UI...")
        
        self.root = tk.Tk()
        self.root.title("🚁 Enhanced Autonomous Drone Swarm Command System - Complete Terrain Edition")
        self.root.geometry("1800x1200")
        
        # MANDATORY: Initialize RescueAgent with LangGraph workflow
        print("🤖 Initializing RescueAgent with mandatory LangGraph workflow...")
        self.rescue_agent = get_rescue_agent()
        print("✅ RescueAgent initialized - All operations will use LangGraph")
        
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
        
        print("🎨 UI styling configured")
        
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
        
        print("📊 Creating UI components...")
        # Create UI
        self.create_widgets()
        print("✅ UI components created")
        
        print("🗺️ Initializing terrain model...")
        self.create_model()
        print("✅ Enhanced terrain model initialized")
        
        # Initialize AI Reasoning display
        if hasattr(self, 'update_reasoning_displays'):
            self.update_reasoning_displays()
            print("🧠 AI reasoning displays initialized")
        
        print("🔄 Starting real-time update loop...")
        # Start update loop
        self.update_display()
        
        print("🎮 Enhanced Terrain UI ready - Console logging active!")
    
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
        
        # Tab 4: JSON Responses
        json_tab = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(json_tab, text="🤖 Ollama JSON")
        self.create_json_panel(json_tab)
        
        # Tab 5: Mission Log
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
    
    def create_json_panel(self, parent):
        """Create JSON response display panel"""
        json_frame = ttk.LabelFrame(parent, text="🤖 Ollama Qwen2 JSON Responses", padding=10)
        json_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(json_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="🔄 Refresh", 
                  command=self.refresh_json_display).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="🗑️ Clear", 
                  command=self.clear_json_display).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="💾 Save JSON", 
                  command=self.save_json_to_file).pack(side=tk.LEFT)
        
        # JSON display area with syntax highlighting
        json_display_frame = ttk.Frame(json_frame)
        json_display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget with scrollbars
        self.json_text = tk.Text(json_display_frame, wrap=tk.WORD, font=('Consolas', 10),
                                bg='#1e1e1e', fg='#d4d4d4', insertbackground='white')
        
        json_scrollbar_v = ttk.Scrollbar(json_display_frame, orient=tk.VERTICAL, command=self.json_text.yview)
        json_scrollbar_h = ttk.Scrollbar(json_display_frame, orient=tk.HORIZONTAL, command=self.json_text.xview)
        
        self.json_text.config(yscrollcommand=json_scrollbar_v.set, xscrollcommand=json_scrollbar_h.set)
        
        # Pack scrollbars and text widget
        json_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        json_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.json_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure syntax highlighting tags
        self.json_text.tag_configure("key", foreground="#9cdcfe")      # Light blue for keys
        self.json_text.tag_configure("string", foreground="#ce9178")   # Orange for strings
        self.json_text.tag_configure("number", foreground="#b5cea8")   # Light green for numbers
        self.json_text.tag_configure("boolean", foreground="#569cd6")  # Blue for booleans
        self.json_text.tag_configure("null", foreground="#569cd6")     # Blue for null
        self.json_text.tag_configure("bracket", foreground="#ffd700")  # Gold for brackets
        
        # Initialize with welcome message
        self.json_responses = []
        self.display_json_welcome()

    def display_json_welcome(self):
        """Display welcome message in JSON panel"""
        welcome_text = """🤖 Ollama Qwen2 JSON Response Viewer
═══════════════════════════════════════════════════════════════

This panel shows the actual JSON responses generated by Ollama Qwen2 
for drone action planning.

📋 What you'll see here:
• Raw JSON responses from Ollama Qwen2
• Structured action plans with drone assignments
• Parameters for each drone action
• Priority levels and execution order

🚀 To see JSON responses:
1. Click any mission button (Start Mission, Search Area, etc.)
2. The system will query Ollama Qwen2 for action planning
3. JSON responses will appear here in real-time

💡 JSON Structure:
{
  "actions": [
    {
      "action": "move_to",
      "drone_id": "drone_A", 
      "parameters": {"x": 10, "y": 15},
      "priority": 1
    },
    {
      "action": "thermal_scan",
      "drone_id": "drone_A",
      "parameters": {},
      "priority": 2
    }
  ]
}

Ready to capture JSON responses...
"""
        self.json_text.delete(1.0, tk.END)
        self.json_text.insert(tk.END, welcome_text)

    def add_json_response(self, json_data, mission_type="Unknown"):
        """Add a new JSON response to the display"""
        import json
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Store the response
        self.json_responses.append({
            "timestamp": timestamp,
            "mission_type": mission_type,
            "json_data": json_data
        })
        
        # Format and display
        self.json_text.insert(tk.END, f"\n\n{'='*60}\n")
        self.json_text.insert(tk.END, f"🕒 {timestamp} | 🎯 {mission_type}\n")
        self.json_text.insert(tk.END, f"{'='*60}\n")
        
        try:
            if isinstance(json_data, str):
                parsed_json = json.loads(json_data)
            else:
                parsed_json = json_data
                
            formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)
            self.json_text.insert(tk.END, formatted_json)
            
            # Apply syntax highlighting
            self.highlight_json_syntax()
            
            # Auto-scroll to bottom
            self.json_text.see(tk.END)
            
        except json.JSONDecodeError:
            self.json_text.insert(tk.END, f"❌ Invalid JSON: {json_data}")

    def highlight_json_syntax(self):
        """Apply basic syntax highlighting to JSON text"""
        content = self.json_text.get(1.0, tk.END)
        lines = content.split('\n')
        
        # Simple highlighting - this is basic but functional
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            if '"action":' in line or '"drone_id":' in line or '"parameters":' in line:
                # Highlight keys
                start_idx = line.find('"')
                if start_idx != -1:
                    end_idx = line.find(':', start_idx)
                    if end_idx != -1:
                        self.json_text.tag_add("key", f"{i+1}.{start_idx}", f"{i+1}.{end_idx}")

    def refresh_json_display(self):
        """Refresh the JSON display"""
        self.json_text.delete(1.0, tk.END)
        self.display_json_welcome()
        
        # Re-display all stored responses
        for response in self.json_responses:
            self.add_json_response(response["json_data"], response["mission_type"])

    def clear_json_display(self):
        """Clear all JSON responses"""
        self.json_responses.clear()
        self.json_text.delete(1.0, tk.END)
        self.display_json_welcome()

    def save_json_to_file(self):
        """Save JSON responses to file"""
        if not self.json_responses:
            messagebox.showinfo("No Data", "No JSON responses to save.")
            return
            
        from tkinter import filedialog
        import json
        from datetime import datetime
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save JSON Responses"
        )
        
        if filename:
            try:
                save_data = {
                    "export_timestamp": datetime.now().isoformat(),
                    "total_responses": len(self.json_responses),
                    "responses": self.json_responses
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                    
                messagebox.showinfo("Success", f"JSON responses saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

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
        def create_json_panel(self, parent):
            """Create JSON response display panel"""
            json_frame = ttk.LabelFrame(parent, text="🤖 Ollama Qwen2 JSON Responses", padding=10)
            json_frame.pack(fill=tk.BOTH, expand=True)

            # Control buttons
            control_frame = ttk.Frame(json_frame)
            control_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Button(control_frame, text="🔄 Refresh",
                      command=self.refresh_json_display).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(control_frame, text="🗑️ Clear",
                      command=self.clear_json_display).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(control_frame, text="💾 Save JSON",
                      command=self.save_json_to_file).pack(side=tk.LEFT)

            # JSON display area
            json_display_frame = ttk.Frame(json_frame)
            json_display_frame.pack(fill=tk.BOTH, expand=True)

            # Create text widget with scrollbars
            self.json_text = tk.Text(json_display_frame, wrap=tk.WORD, font=('Consolas', 10),
                                    bg='#1e1e1e', fg='#d4d4d4', insertbackground='white')

            json_scrollbar_v = ttk.Scrollbar(json_display_frame, orient=tk.VERTICAL, command=self.json_text.yview)
            json_scrollbar_h = ttk.Scrollbar(json_display_frame, orient=tk.HORIZONTAL, command=self.json_text.xview)

            self.json_text.config(yscrollcommand=json_scrollbar_v.set, xscrollcommand=json_scrollbar_h.set)

            # Pack scrollbars and text widget
            json_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
            json_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
            self.json_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Initialize with welcome message
            self.json_responses = []
            self.display_json_welcome()

        def display_json_welcome(self):
            """Display welcome message in JSON panel"""
            welcome_text = """🤖 Ollama Qwen2 JSON Response Viewer
    ═══════════════════════════════════════════════════════════════

    This panel shows the actual JSON responses generated by Ollama Qwen2
    for drone action planning.

    📋 What you'll see here:
    • Raw JSON responses from Ollama Qwen2
    • Structured action plans with drone assignments
    • Parameters for each drone action
    • Priority levels and execution order

    🚀 To see JSON responses:
    1. Click any mission button (Start Mission, Search Area, etc.)
    2. The system will query Ollama Qwen2 for action planning
    3. JSON responses will appear here in real-time

    💡 JSON Structure:
    {
      "actions": [
        {
          "action": "move_to",
          "drone_id": "drone_A",
          "parameters": {"x": 10, "y": 15},
          "priority": 1
        },
        {
          "action": "thermal_scan",
          "drone_id": "drone_A",
          "parameters": {},
          "priority": 2
        }
      ]
    }

    Ready to capture JSON responses...
    """
            self.json_text.delete(1.0, tk.END)
            self.json_text.insert(tk.END, welcome_text)

        def add_json_response(self, json_data, mission_type="Unknown"):
            """Add a new JSON response to the display"""
            import json
            from datetime import datetime

            timestamp = datetime.now().strftime("%H:%M:%S")

            # Store the response
            self.json_responses.append({
                "timestamp": timestamp,
                "mission_type": mission_type,
                "json_data": json_data
            })

            # Format and display
            self.json_text.insert(tk.END, f"\n\n{'='*60}\n")
            self.json_text.insert(tk.END, f"🕒 {timestamp} | 🎯 {mission_type}\n")
            self.json_text.insert(tk.END, f"{'='*60}\n")

            try:
                if isinstance(json_data, str):
                    parsed_json = json.loads(json_data)
                else:
                    parsed_json = json_data

                formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                self.json_text.insert(tk.END, formatted_json)

                # Auto-scroll to bottom
                self.json_text.see(tk.END)

            except json.JSONDecodeError:
                self.json_text.insert(tk.END, f"❌ Invalid JSON: {json_data}")

        def refresh_json_display(self):
            """Refresh the JSON display"""
            self.json_text.delete(1.0, tk.END)
            self.display_json_welcome()

            # Re-display all stored responses
            for response in self.json_responses:
                self.add_json_response(response["json_data"], response["mission_type"])

        def clear_json_display(self):
            """Clear all JSON responses"""
            self.json_responses.clear()
            self.json_text.delete(1.0, tk.END)
            self.display_json_welcome()

        def save_json_to_file(self):
            """Save JSON responses to file"""
            if not self.json_responses:
                messagebox.showinfo("No Data", "No JSON responses to save.")
                return

            from tkinter import filedialog
            import json
            from datetime import datetime

            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save JSON Responses"
            )

            if filename:
                try:
                    save_data = {
                        "export_timestamp": datetime.now().isoformat(),
                        "total_responses": len(self.json_responses),
                        "responses": self.json_responses
                    }

                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(save_data, f, indent=2, ensure_ascii=False)

                    messagebox.showinfo("Success", f"JSON responses saved to {filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}")

    
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
        """Add log message to both UI and console"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Add to UI log
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        
        # Also print to console for complete logging
        print(f"🖥️  UI LOG: {log_entry}")
        
        # Limit log length
        lines = self.log_text.get(1.0, tk.END).split('\n')
        if len(lines) > 100:
            self.log_text.delete(1.0, f"{len(lines)-100}.0")
    
    def process_ui_action(self, action_type: str, **kwargs):
        """
        Process UI action through RescueAgent → Ollama → LangGraph → MCP
        MANDATORY: All UI actions must go through this flow
        """
        
        # Create request for RescueAgent
        request = {
            "type": action_type,
            "timestamp": time.time(),
            "source": "enhanced_tkinter_ui",
            **kwargs
        }
        
        # Enhanced console logging
        print(f"🔄 CONSOLE: Processing {action_type} action through AI workflow")
        print(f"📋 CONSOLE: Request details: {request}")
        
        self.log_message(f"🔄 Processing {action_type} through RescueAgent → LangGraph")
        
        try:
            # MANDATORY: Route through RescueAgent (which uses LangGraph)
            print(f"🤖 CONSOLE: Sending request to RescueAgent...")
            result = self.rescue_agent.process_ui_request(request)
            
            if result.get("success"):
                print(f"✅ CONSOLE: {action_type} completed successfully")
                print(f"📊 CONSOLE: Mission results: {result.get('survivors_found', [])} survivors found")
                
                self.log_message(f"✅ {action_type} completed successfully")
                self.log_message(f"📊 Survivors found: {len(result.get('survivors_found', []))}")
                
                # Update UI with results
                self._update_ui_with_results(result)
                
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"❌ CONSOLE: {action_type} failed: {error_msg}")
                self.log_message(f"❌ {action_type} failed: {error_msg}")
                messagebox.showerror("Operation Failed", f"Failed to execute {action_type}:\n{error_msg}")
        
        except Exception as e:
            error_msg = f"UI processing error: {str(e)}"
            print(f"❌ CONSOLE: {error_msg}")
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("System Error", error_msg)
    
    def _update_ui_with_results(self, result: dict):
        """Update UI components with LangGraph workflow results"""
        
        # Update status displays
        if hasattr(self, 'metrics_labels'):
            survivors_found = len(result.get('survivors_found', []))
            self.metrics_labels.get("Rescue Progress", tk.Label()).config(
                text=f"{survivors_found}/? survivors"
            )
        
        # Log execution steps
        for step in result.get('execution_steps', []):
            self.log_message(f"🔄 {step}")
    
    def on_start_mission_click(self):
        """Handle start mission button click - routes through LangGraph"""
        self.process_ui_action(
            "start_mission",
            mission_goal="Execute comprehensive search and rescue mission",
            priority="high"
        )
    
    def on_search_area_click(self):
        """Handle search area button click - routes through LangGraph"""
        self.process_ui_action(
            "search_area",
            area={"x": self.selected_pos[0], "y": self.selected_pos[1]},
            search_radius=5
        )
    
    def on_emergency_response_click(self):
        """Handle emergency response button click - routes through LangGraph"""
        self.process_ui_action(
            "emergency_response",
            details="Emergency situation detected",
            location={"x": self.selected_pos[0], "y": self.selected_pos[1]}
        )
    
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
    """Main function with comprehensive console logging"""
    print("🚁 Starting Enhanced Terrain UI with Complete Console Logging")
    print("=" * 70)
    
    print("🗺️ Complex Terrain Features:")
    print("   • Multiple terrain types: Flat, Hills, Mountains, Water, Forest, Desert")
    print("   • Altitude differences: 0-2000m elevation affecting movement and communication")
    print("   • Dynamic weather: Clear, Rain, Wind, Fog, Storm conditions")
    print("   • Obstacle system: Buildings, Trees, Towers, Debris")
    
    print("\n🧠 AI Enhancement Features:")
    print("   • Multi-step reasoning: Environment → Threat → Resource → Planning → Path → Decision")
    print("   • Complex path planning: A* algorithm with terrain cost analysis")
    print("   • Dynamic adaptation: Real-time response to weather and terrain changes")
    print("   • Complete reasoning visualization: Full AI thinking process display")
    
    print("\n🔄 LangGraph Workflow Integration:")
    print("   • Mandatory AI workflow: UI → RescueAgent → Ollama → LangGraph → MCP")
    print("   • Real-time mission coordination and drone fleet management")
    print("   • Intelligent task planning and resource allocation")
    
    print("\n📊 Console Logging Features:")
    print("   • Real-time UI event logging to console")
    print("   • Mission progress tracking and status updates")
    print("   • AI reasoning process output")
    print("   • Drone coordination and rescue operation logs")
    
    print("\n🎮 Starting Complete Terrain UI Demo...")
    print("=" * 70)
    
    try:
        app = EnhancedDroneUI()
        print("✅ Enhanced Terrain UI initialized successfully")
        print("🖥️  UI Window opened - Check both UI and console for complete logging")
        print("📝 All UI actions will be logged to console in real-time")
        app.run()
    except Exception as e:
        print(f"❌ Error starting Enhanced Terrain UI: {e}")
        print("💡 Please check system requirements and dependencies")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()