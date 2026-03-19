#!/usr/bin/env python3
"""
Enhanced Tkinter UI with JSON Response Viewer
Shows Ollama Qwen2 JSON responses in real-time
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.rescue_agent import get_rescue_agent
from ui.enhanced_ui_components import *
from ui.enhanced_ui_methods import *
from simulation.enhanced_model import EnhancedDroneSwarmModel


class EnhancedDroneUIWithJSON:
    """Enhanced Drone UI with JSON Response Viewer"""
    
    def __init__(self):
        """Initialize Enhanced Drone UI with JSON viewer"""
        
        # Initialize Tkinter
        self.root = tk.Tk()
        self.root.title("🚁 LifeDrone Command Center - Enhanced with JSON Viewer")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize models and agents
        self.drone_model = EnhancedDroneSwarmModel()
        self.rescue_agent = get_rescue_agent()
        
        # UI state
        self.canvas_size = 600
        self.cell_size = 20
        self.zoom_factor = 1.0
        self.selected_cell = None
        
        # JSON tracking
        self.json_responses = []
        
        # Create UI
        self.create_widgets()
        self.update_display()
        
        print("✅ Enhanced Drone UI with JSON Viewer initialized")
    
    def create_widgets(self):
        """Create UI components with JSON tab"""
        
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
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        
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
        
        # Tab 4: JSON Responses - NEW!
        json_tab = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(json_tab, text="🤖 Ollama JSON")
        self.create_json_panel(json_tab)
        
        # Tab 5: Mission Log
        log_tab = ttk.Frame(self.main_notebook, padding=5)
        self.main_notebook.add(log_tab, text="📝 Mission Log")
        self.create_log_panel(log_tab)
    
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
                  command=self.save_json_to_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="🧪 Test JSON", 
                  command=self.test_json_generation).pack(side=tk.LEFT)
        
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

🧪 Click "Test JSON" to see a sample response from Ollama Qwen2!

Ready to capture JSON responses...
"""
        self.json_text.delete(1.0, tk.END)
        self.json_text.insert(tk.END, welcome_text)
    
    def add_json_response(self, json_data, mission_type="Unknown"):
        """Add a new JSON response to the display"""
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
    
    def test_json_generation(self):
        """Test JSON generation by calling Ollama directly"""
        from langchain_ollama import ChatOllama
        from langchain_core.messages import HumanMessage
        
        try:
            # Show loading message
            self.json_text.insert(tk.END, f"\n\n🔄 Testing Ollama Qwen2 JSON generation...\n")
            self.json_text.see(tk.END)
            self.root.update()
            
            # Initialize Ollama LLM
            llm = ChatOllama(
                model="qwen2",
                base_url="http://localhost:11434",
                temperature=0.1
            )
            
            # Create test prompt
            test_prompt = """
            Based on the following information, develop a rescue plan:
            
            Mission Objective: Test JSON generation for UI display
            Available Drones: ['drone_A', 'drone_B', 'drone_C']
            Drone Status: {
                'drone_A': {'battery_level': 85, 'position': [0, 0], 'status': 'idle'},
                'drone_B': {'battery_level': 92, 'position': [5, 10], 'status': 'idle'},
                'drone_C': {'battery_level': 15, 'position': [10, 10], 'status': 'idle'}
            }
            
            Reply in JSON format:
            {"actions": [
                {"action": "move_to", "drone_id": "drone_A", "parameters": {"x": 5, "y": 8}, "priority": 1}, 
                {"action": "thermal_scan", "drone_id": "drone_A", "parameters": {}, "priority": 2}
            ]}
            """
            
            # Get response from Ollama
            response = llm.invoke([HumanMessage(content=test_prompt)])
            
            # Display the response
            self.add_json_response(response.content, "Test Generation")
            
        except Exception as e:
            error_msg = f"❌ Error testing Ollama: {str(e)}"
            self.json_text.insert(tk.END, f"\n{error_msg}\n")
            self.json_text.see(tk.END)
            messagebox.showerror("Test Error", error_msg)
    
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
    
    def create_status_table(self, parent):
        """Create status table"""
        table_frame = ttk.LabelFrame(parent, text="🚁 Drone Detailed Status", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create table
        columns = ("ID", "Battery", "Status", "Position", "Terrain", "Target")
        self.status_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        # Set column headers and widths
        for col in columns:
            self.status_tree.heading(col, text=col)
            self.status_tree.column(col, width=80, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.status_tree.yview)
        self.status_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack table and scrollbar
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
    
    def process_ui_action(self, action_type: str, **kwargs):
        """Process UI action and capture JSON responses"""
        
        # Create request for RescueAgent
        request = {
            "type": action_type,
            "timestamp": time.time(),
            "source": "enhanced_tkinter_ui_with_json",
            **kwargs
        }
        
        print(f"🔄 Processing {action_type} action through AI workflow")
        self.log_message(f"🔄 Processing {action_type} through RescueAgent → LangGraph")
        
        try:
            # Route through RescueAgent (which uses LangGraph)
            result = self.rescue_agent.process_ui_request(request)
            
            # Try to capture JSON from the workflow
            if hasattr(self.rescue_agent, 'langgraph_workflow'):
                # Access the last LLM response if available
                try:
                    # This is a hook to capture JSON - we'll modify the workflow to expose this
                    if hasattr(self.rescue_agent.langgraph_workflow, 'last_json_response'):
                        json_response = self.rescue_agent.langgraph_workflow.last_json_response
                        self.add_json_response(json_response, action_type)
                except:
                    pass
            
            if result.get("success"):
                print(f"✅ {action_type} completed successfully")
                self.log_message(f"✅ {action_type} completed successfully")
                self.log_message(f"📊 Survivors found: {len(result.get('survivors_found', []))}")
                
                # Update UI with results
                self._update_ui_with_results(result)
                
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"❌ {action_type} failed: {error_msg}")
                self.log_message(f"❌ {action_type} failed: {error_msg}")
                messagebox.showerror("Operation Failed", f"Failed to execute {action_type}:\\n{error_msg}")
        
        except Exception as e:
            error_msg = f"UI processing error: {str(e)}"
            print(f"❌ {error_msg}")
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("System Error", error_msg)
    
    def _update_ui_with_results(self, result: dict):
        """Update UI with mission results"""
        # Update status table and display
        self.update_status_table()
        self.update_display()
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\\n"
        
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
    
    def update_status_table(self):
        """Update drone status table"""
        # Clear existing items
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)
        
        # Get drone status from model
        drone_status = self.drone_model.get_all_drone_status()
        
        for drone_id, status in drone_status.items():
            position = f"({status.get('x', 0)}, {status.get('y', 0)})"
            terrain = status.get('terrain', 'Unknown')
            
            self.status_tree.insert("", tk.END, values=(
                drone_id,
                f"{status.get('battery', 0)}%",
                status.get('status', 'Unknown'),
                position,
                terrain,
                status.get('target', 'None')
            ))
    
    def update_display(self):
        """Update the main display"""
        self.canvas.delete("all")
        
        # Draw grid and terrain
        grid_size = self.drone_model.grid_size
        cell_size = int(self.cell_size * self.zoom_factor)
        
        for x in range(grid_size[0]):
            for y in range(grid_size[1]):
                x1, y1 = x * cell_size, y * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                
                # Get terrain info
                terrain_info = self.drone_model.get_terrain_info(x, y)
                color = self.get_terrain_color(terrain_info)
                
                # Draw cell
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
        
        # Draw drones
        drone_status = self.drone_model.get_all_drone_status()
        for drone_id, status in drone_status.items():
            x, y = status.get('x', 0), status.get('y', 0)
            cx = x * cell_size + cell_size // 2
            cy = y * cell_size + cell_size // 2
            
            # Draw drone
            self.canvas.create_oval(cx-8, cy-8, cx+8, cy+8, fill="blue", outline="white", width=2)
            self.canvas.create_text(cx, cy-15, text=drone_id, font=('Arial', 8, 'bold'), fill="black")
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def get_terrain_color(self, terrain_info):
        """Get color for terrain type"""
        terrain_colors = {
            'Mountain': '#8B4513',
            'Hill': '#DEB887',
            'Forest': '#228B22',
            'Water': '#4169E1',
            'Desert': '#F4A460',
            'Urban': '#696969',
            'Flat': '#90EE90',
            'Swamp': '#556B2F',
            'Valley': '#9ACD32',
            'Cliff': '#A0522D'
        }
        return terrain_colors.get(terrain_info.get('terrain', 'Flat'), '#90EE90')
    
    # Event handlers
    def on_canvas_click(self, event):
        """Handle canvas click"""
        pass
    
    def on_canvas_hover(self, event):
        """Handle canvas hover"""
        pass
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming"""
        pass
    
    def zoom_in(self):
        """Zoom in"""
        self.zoom_factor = min(self.zoom_factor * 1.2, 3.0)
        self.update_zoom()
    
    def zoom_out(self):
        """Zoom out"""
        self.zoom_factor = max(self.zoom_factor / 1.2, 0.5)
        self.update_zoom()
    
    def zoom_reset(self):
        """Reset zoom"""
        self.zoom_factor = 1.0
        self.update_zoom()
    
    def update_zoom(self):
        """Update zoom display"""
        self.zoom_label.config(text=f"{int(self.zoom_factor * 100)}%")
        self.update_display()
    
    def toggle_terrain_display(self):
        """Toggle terrain display"""
        self.update_display()
    
    def toggle_height_display(self):
        """Toggle height display"""
        self.update_display()
    
    def toggle_weather_display(self):
        """Toggle weather display"""
        self.update_display()
    
    # Mission control methods
    def on_start_mission_click(self):
        """Handle start mission button"""
        self.process_ui_action("start_mission", mission_goal="Search and rescue survivors in disaster area")
    
    def on_search_area_click(self):
        """Handle search area button"""
        self.process_ui_action("search_area", area={"x": 10, "y": 10}, search_radius=8, priority="high")
    
    def on_emergency_response_click(self):
        """Handle emergency response button"""
        self.process_ui_action("emergency_response", details="Multiple survivors detected in disaster zone", priority="critical")
    
    def run(self):
        """Run the UI"""
        self.root.mainloop()


def main():
    """Main function"""
    try:
        app = EnhancedDroneUIWithJSON()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start Enhanced UI with JSON: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()