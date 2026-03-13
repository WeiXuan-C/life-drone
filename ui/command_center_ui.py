"""
Command Center UI for Home Base Operations
Interactive interface for managing drone home base functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Optional

from command_center import get_command_center
from simulation.simple_model import SimpleDroneSwarmModel


class CommandCenterUI:
    """GUI for Command Center with Home Base Management"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏢 Drone Command Center - Home Base Operations")
        self.root.geometry("800x600")
        
        self.command_center = get_command_center()
        self.model: Optional[SimpleDroneSwarmModel] = None
        self.simulation_running = False
        
        self.setup_ui()
        self.update_status()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🏢 Drone Command Center", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Home Base Status Frame
        home_frame = ttk.LabelFrame(main_frame, text="🏠 Home Base Status", padding="10")
        home_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Home base position
        ttk.Label(home_frame, text="Home Base Position:").grid(row=0, column=0, sticky=tk.W)
        self.home_pos_label = ttk.Label(home_frame, text="(10, 10)", font=("Arial", 10, "bold"))
        self.home_pos_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Drones at home
        ttk.Label(home_frame, text="Drones at Home:").grid(row=1, column=0, sticky=tk.W)
        self.drones_home_label = ttk.Label(home_frame, text="0", font=("Arial", 10, "bold"))
        self.drones_home_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Emergency recall status
        ttk.Label(home_frame, text="Emergency Recall:").grid(row=2, column=0, sticky=tk.W)
        self.recall_status_label = ttk.Label(home_frame, text="Inactive", font=("Arial", 10, "bold"))
        self.recall_status_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Control Buttons Frame
        control_frame = ttk.LabelFrame(main_frame, text="🎮 Home Base Controls", padding="10")
        control_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Emergency recall button
        self.recall_button = ttk.Button(control_frame, text="🚨 Emergency Recall All", 
                                       command=self.emergency_recall)
        self.recall_button.grid(row=0, column=0, padx=(0, 10))
        
        # Cancel recall button
        self.cancel_recall_button = ttk.Button(control_frame, text="✅ Cancel Recall", 
                                              command=self.cancel_recall, state="disabled")
        self.cancel_recall_button.grid(row=0, column=1, padx=(0, 10))
        
        # Simulation Controls Frame
        sim_frame = ttk.LabelFrame(main_frame, text="🚁 Simulation Controls", padding="10")
        sim_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Start simulation button
        self.start_sim_button = ttk.Button(sim_frame, text="▶️ Start Simulation", 
                                          command=self.start_simulation)
        self.start_sim_button.grid(row=0, column=0, padx=(0, 10))
        
        # Stop simulation button
        self.stop_sim_button = ttk.Button(sim_frame, text="⏹️ Stop Simulation", 
                                         command=self.stop_simulation, state="disabled")
        self.stop_sim_button.grid(row=0, column=1, padx=(0, 10))
        
        # Home base options
        options_frame = ttk.Frame(sim_frame)
        options_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        self.return_after_mission = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Return home after missions", 
                       variable=self.return_after_mission,
                       command=self.update_return_settings).grid(row=0, column=0, sticky=tk.W)
        
        self.return_when_idle = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Return home when idle", 
                       variable=self.return_when_idle,
                       command=self.update_return_settings).grid(row=1, column=0, sticky=tk.W)
        
        # Status Display Frame
        status_frame = ttk.LabelFrame(main_frame, text="📊 System Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Status text area
        self.status_text = tk.Text(status_frame, height=15, width=70)
        scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
    
    def emergency_recall(self):
        """Trigger emergency recall"""
        if self.model:
            self.model.recall_all_drones()
        self.command_center.emergency_recall_all()
        
        self.recall_button.config(state="disabled")
        self.cancel_recall_button.config(state="normal")
        
        self.log_message("🚨 EMERGENCY RECALL ACTIVATED - All drones returning to home base")
    
    def cancel_recall(self):
        """Cancel emergency recall"""
        if self.model:
            self.model.cancel_recall()
        self.command_center.cancel_emergency_recall()
        
        self.recall_button.config(state="normal")
        self.cancel_recall_button.config(state="disabled")
        
        self.log_message("✅ Emergency recall cancelled - Normal operations resumed")
    
    def start_simulation(self):
        """Start the drone simulation"""
        try:
            self.model = SimpleDroneSwarmModel(
                width=20, height=20, 
                n_drones=5, n_survivors=8, 
                n_charging_stations=2,
                home_base_pos=self.command_center.home_base_position
            )
            
            self.simulation_running = True
            self.start_sim_button.config(state="disabled")
            self.stop_sim_button.config(state="normal")
            
            # Start simulation thread
            self.sim_thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.sim_thread.start()
            
            self.log_message("▶️ Simulation started with home base functionality")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start simulation: {str(e)}")
    
    def stop_simulation(self):
        """Stop the drone simulation"""
        self.simulation_running = False
        self.start_sim_button.config(state="normal")
        self.stop_sim_button.config(state="disabled")
        
        self.log_message("⏹️ Simulation stopped")
    
    def run_simulation(self):
        """Run the simulation loop"""
        step_count = 0
        while self.simulation_running and self.model:
            try:
                self.model.step()
                step_count += 1
                
                if step_count % 10 == 0:
                    self.root.after(0, self.update_simulation_status)
                
                time.sleep(0.5)  # Slow down for visualization
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Simulation error: {str(e)}"))
                break
    
    def update_return_settings(self):
        """Update return home settings"""
        if self.model:
            self.model.set_return_home_after_mission(self.return_after_mission.get())
            self.model.set_return_home_when_idle(self.return_when_idle.get())
    
    def update_simulation_status(self):
        """Update simulation status display"""
        if not self.model:
            return
            
        # Get drone status
        drone_status = self.model.get_drone_status()
        home_status = self.model.get_home_base_status()
        
        status_msg = f"📊 Simulation Status (Step {self.model.step_count}):\n"
        status_msg += f"   🏠 Drones at home base: {home_status['drones_at_base']}\n"
        status_msg += f"   🚁 Active drones: {len([d for d in drone_status if d['status'] not in ['at_home_base', 'charging']])}\n"
        status_msg += f"   🆘 Survivors found: {len([a for a in self.model.custom_agents if hasattr(a, 'found') and a.found])}\n"
        
        if home_status['emergency_recall_active']:
            status_msg += "   🚨 EMERGENCY RECALL ACTIVE\n"
        
        self.log_message(status_msg)
    
    def update_status(self):
        """Update status display"""
        try:
            # Update home base status
            home_status = self.command_center.get_home_base_status()
            
            self.home_pos_label.config(text=str(home_status['position']))
            self.drones_home_label.config(text=str(home_status['drones_at_base']))
            
            if home_status['emergency_recall_active']:
                self.recall_status_label.config(text="🚨 ACTIVE", foreground="red")
                self.recall_button.config(state="disabled")
                self.cancel_recall_button.config(state="normal")
            else:
                self.recall_status_label.config(text="✅ Inactive", foreground="green")
                self.recall_button.config(state="normal")
                self.cancel_recall_button.config(state="disabled")
            
        except Exception as e:
            self.log_message(f"❌ Status update error: {str(e)}")
        
        # Schedule next update
        self.root.after(2000, self.update_status)
    
    def log_message(self, message):
        """Add message to status log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, log_entry)
        self.status_text.see(tk.END)
    
    def run(self):
        """Start the UI"""
        self.log_message("🏢 Command Center UI initialized")
        self.log_message("🏠 Home base ready for drone operations")
        self.root.mainloop()


if __name__ == "__main__":
    app = CommandCenterUI()
    app.run()