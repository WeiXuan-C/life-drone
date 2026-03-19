#!/usr/bin/env python3
"""
Simple JSON Response Viewer for Ollama Qwen2
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from langchain_ollama import ChatOllama
    from langchain_core.messages import HumanMessage
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️ Ollama not available, using mock responses")


class SimpleJSONViewer:
    """Simple JSON Response Viewer for Ollama Qwen2"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Ollama Qwen2 JSON Response Viewer")
        self.root.geometry("1200x800")
        
        self.json_responses = []
        
        # Initialize Ollama connection first
        if OLLAMA_AVAILABLE:
            try:
                self.llm = ChatOllama(
                    model="qwen2",
                    base_url="http://localhost:11434",
                    temperature=0.1
                )
                self.ollama_status = "✅ Connected"
            except:
                self.ollama_status = "❌ Connection Failed"
                self.llm = None
        else:
            self.ollama_status = "❌ Not Available"
            self.llm = None
        
        # Now create widgets
        self.create_widgets()
    
    def create_widgets(self):
        """Create UI widgets"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 Ollama Qwen2 JSON Response Viewer", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text=f"Ollama Status: {self.ollama_status}")
        self.status_label.pack(side=tk.LEFT)
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="🎮 Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Mission buttons
        mission_frame = ttk.Frame(control_frame)
        mission_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(mission_frame, text="🚀 Start Mission", 
                  command=self.start_mission).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(mission_frame, text="🔍 Search Area", 
                  command=self.search_area).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(mission_frame, text="🚨 Emergency Response", 
                  command=self.emergency_response).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(mission_frame, text="🧪 Test JSON", 
                  command=self.test_json).pack(side=tk.LEFT)
        
        # JSON control buttons
        json_control_frame = ttk.Frame(control_frame)
        json_control_frame.pack(fill=tk.X)
        
        ttk.Button(json_control_frame, text="🔄 Refresh", 
                  command=self.refresh_display).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(json_control_frame, text="🗑️ Clear", 
                  command=self.clear_display).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(json_control_frame, text="💾 Save JSON", 
                  command=self.save_json).pack(side=tk.LEFT)
        
        # JSON display frame
        json_frame = ttk.LabelFrame(main_frame, text="📋 JSON Responses from Ollama Qwen2", padding=10)
        json_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget with scrollbars
        text_frame = ttk.Frame(json_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.json_text = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 11),
                                bg='#1e1e1e', fg='#d4d4d4', insertbackground='white')
        
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.json_text.yview)
        h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.json_text.xview)
        
        self.json_text.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and text widget
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.json_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure syntax highlighting
        self.json_text.tag_configure("key", foreground="#9cdcfe")
        self.json_text.tag_configure("string", foreground="#ce9178")
        self.json_text.tag_configure("number", foreground="#b5cea8")
        self.json_text.tag_configure("bracket", foreground="#ffd700")
        
        # Initial welcome message
        self.display_welcome()
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = """🤖 Ollama Qwen2 JSON Response Viewer
═══════════════════════════════════════════════════════════════

Status: """ + self.ollama_status + """

This viewer shows the actual JSON responses generated by Ollama Qwen2 
for drone action planning in the LifeDrone system.

📋 What you'll see:
• Raw JSON responses from Ollama Qwen2
• Structured action plans with drone assignments  
• Parameters for each drone action
• Priority levels and execution order

🚀 How to use:
1. Click any mission button above
2. The system queries Ollama Qwen2 for action planning
3. JSON responses appear here in real-time

💡 Example JSON Structure:
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
        """Add a JSON response to the display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Store response
        self.json_responses.append({
            "timestamp": timestamp,
            "mission_type": mission_type,
            "json_data": json_data
        })
        
        # Display response
        self.json_text.insert(tk.END, f"\n\n{'='*70}\n")
        self.json_text.insert(tk.END, f"🕒 {timestamp} | 🎯 {mission_type}\n")
        self.json_text.insert(tk.END, f"{'='*70}\n")
        
        try:
            if isinstance(json_data, str):
                parsed_json = json.loads(json_data)
            else:
                parsed_json = json_data
                
            formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)
            self.json_text.insert(tk.END, formatted_json)
            
            # Show summary
            actions = parsed_json.get("actions", [])
            self.json_text.insert(tk.END, f"\n\n📊 Summary: {len(actions)} actions planned")
            
            # Count action types
            action_counts = {}
            for action in actions:
                action_type = action.get("action", "unknown")
                action_counts[action_type] = action_counts.get(action_type, 0) + 1
            
            for action_type, count in action_counts.items():
                self.json_text.insert(tk.END, f"\n   • {action_type}: {count}")
            
        except json.JSONDecodeError:
            self.json_text.insert(tk.END, f"❌ Invalid JSON: {json_data}")
        
        # Auto-scroll to bottom
        self.json_text.see(tk.END)
    
    def query_ollama(self, mission_type, prompt):
        """Query Ollama for JSON response"""
        if not self.llm:
            # Mock response if Ollama not available
            mock_response = {
                "actions": [
                    {
                        "action": "move_to",
                        "drone_id": "drone_A",
                        "parameters": {"x": 5, "y": 8},
                        "priority": 1
                    },
                    {
                        "action": "thermal_scan",
                        "drone_id": "drone_A", 
                        "parameters": {},
                        "priority": 2
                    },
                    {
                        "action": "move_to",
                        "drone_id": "drone_B",
                        "parameters": {"x": 12, "y": 15},
                        "priority": 1
                    },
                    {
                        "action": "thermal_scan",
                        "drone_id": "drone_B",
                        "parameters": {},
                        "priority": 2
                    }
                ]
            }
            self.add_json_response(mock_response, f"{mission_type} (Mock)")
            return
        
        try:
            # Show loading
            self.json_text.insert(tk.END, f"\n\n🔄 Querying Ollama Qwen2 for {mission_type}...\n")
            self.json_text.see(tk.END)
            self.root.update()
            
            # Query Ollama
            response = self.llm.invoke([HumanMessage(content=prompt)])
            self.add_json_response(response.content, mission_type)
            
        except Exception as e:
            error_msg = f"❌ Error querying Ollama: {str(e)}"
            self.json_text.insert(tk.END, f"\n{error_msg}\n")
            self.json_text.see(tk.END)
    
    def start_mission(self):
        """Start mission scenario"""
        prompt = '''
        Based on the following information, develop a rescue plan:
        
        Mission Objective: Search and rescue survivors in disaster area
        Available Drones: ['drone_A', 'drone_B', 'drone_C', 'drone_D', 'drone_E']
        Drone Status: {
            'drone_A': {'battery_level': 85, 'position': [0, 0], 'status': 'idle'},
            'drone_B': {'battery_level': 92, 'position': [5, 10], 'status': 'idle'},
            'drone_C': {'battery_level': 15, 'position': [10, 10], 'status': 'idle'},
            'drone_D': {'battery_level': 78, 'position': [15, 5], 'status': 'idle'},
            'drone_E': {'battery_level': 88, 'position': [20, 15], 'status': 'idle'}
        }
        
        Reply in JSON format:
        {"actions": [
            {"action": "move_to", "drone_id": "drone_A", "parameters": {"x": 5, "y": 8}, "priority": 1}, 
            {"action": "thermal_scan", "drone_id": "drone_A", "parameters": {}, "priority": 2}
        ]}
        
        Important: Only use actions: move_to, thermal_scan, rescue_survivor, return_to_base
        '''
        self.query_ollama("Start Mission", prompt)
    
    def search_area(self):
        """Search area scenario"""
        prompt = '''
        Based on the following information, develop a search plan:
        
        Mission Objective: Search specific area at coordinates (10, 10) with radius 8
        Available Drones: ['drone_A', 'drone_B', 'drone_C']
        Drone Status: {
            'drone_A': {'battery_level': 95, 'position': [2, 3], 'status': 'idle'},
            'drone_B': {'battery_level': 87, 'position': [8, 12], 'status': 'idle'},
            'drone_C': {'battery_level': 91, 'position': [15, 8], 'status': 'idle'}
        }
        
        Reply in JSON format:
        {"actions": [
            {"action": "move_to", "drone_id": "drone_A", "parameters": {"x": 8, "y": 8}, "priority": 1},
            {"action": "thermal_scan", "drone_id": "drone_A", "parameters": {}, "priority": 2}
        ]}
        
        Focus on systematic area coverage. Only use: move_to, thermal_scan, rescue_survivor, return_to_base
        '''
        self.query_ollama("Search Area", prompt)
    
    def emergency_response(self):
        """Emergency response scenario"""
        prompt = '''
        Based on the following information, develop an emergency response plan:
        
        Mission Objective: Emergency response - Multiple survivors detected in disaster zone
        Available Drones: ['drone_A', 'drone_B', 'drone_C', 'drone_D']
        Drone Status: {
            'drone_A': {'battery_level': 95, 'position': [2, 3], 'status': 'idle'},
            'drone_B': {'battery_level': 18, 'position': [8, 12], 'status': 'idle'},
            'drone_C': {'battery_level': 87, 'position': [15, 8], 'status': 'idle'},
            'drone_D': {'battery_level': 12, 'position': [20, 20], 'status': 'idle'}
        }
        
        Known Survivor Locations: [(7, 9), (14, 16), (3, 12)]
        
        Reply in JSON format:
        {"actions": [
            {"action": "return_to_base", "drone_id": "drone_B", "parameters": {}, "priority": 1},
            {"action": "move_to", "drone_id": "drone_A", "parameters": {"x": 7, "y": 9}, "priority": 2},
            {"action": "rescue_survivor", "drone_id": "drone_A", "parameters": {"x": 7, "y": 9}, "priority": 3}
        ]}
        
        Prioritize: 1) Low battery drones return to base, 2) Rescue known survivors
        Only use: move_to, thermal_scan, rescue_survivor, return_to_base
        '''
        self.query_ollama("Emergency Response", prompt)
    
    def test_json(self):
        """Test with sample JSON"""
        sample_json = {
            "actions": [
                {
                    "action": "move_to",
                    "drone_id": "drone_A",
                    "parameters": {"x": 5, "y": 8},
                    "priority": 1
                },
                {
                    "action": "thermal_scan",
                    "drone_id": "drone_A",
                    "parameters": {},
                    "priority": 2
                },
                {
                    "action": "move_to",
                    "drone_id": "drone_B",
                    "parameters": {"x": 12, "y": 15},
                    "priority": 1
                },
                {
                    "action": "thermal_scan",
                    "drone_id": "drone_B",
                    "parameters": {},
                    "priority": 2
                },
                {
                    "action": "rescue_survivor",
                    "drone_id": "drone_A",
                    "parameters": {"x": 6, "y": 9},
                    "priority": 3
                }
            ]
        }
        self.add_json_response(sample_json, "Test Sample")
    
    def refresh_display(self):
        """Refresh the display"""
        self.json_text.delete(1.0, tk.END)
        self.display_welcome()
        
        for response in self.json_responses:
            self.add_json_response(response["json_data"], response["mission_type"])
    
    def clear_display(self):
        """Clear all responses"""
        self.json_responses.clear()
        self.json_text.delete(1.0, tk.END)
        self.display_welcome()
    
    def save_json(self):
        """Save JSON responses to file"""
        if not self.json_responses:
            messagebox.showinfo("No Data", "No JSON responses to save.")
            return
        
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
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main function"""
    try:
        app = SimpleJSONViewer()
        app.run()
    except Exception as e:
        print(f"❌ Error starting JSON viewer: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()