"""
Console-based UI for Drone Swarm System
Works with any Mesa version - no web dependencies
"""

import sys
import os
import time
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.simple_model import SimpleDroneSwarmModel, SimpleDroneAgent, SimpleSurvivorAgent, SimpleChargingStationAgent

class ConsoleUI:
    """Console-based user interface"""
    
    def __init__(self):
        self.model = None
        self.running = False
        self.auto_step = False
        
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_grid(self):
        """Print the simulation grid"""
        print("🗺️  Simulation Grid:")
        print("   " + "".join([f"{i:2d}" for i in range(self.model.width)]))
        
        for y in range(self.model.height):
            row = f"{y:2d} "
            for x in range(self.model.width):
                cell_contents = self.model.grid.get_cell_list_contents([(x, y)])
                
                if not cell_contents:
                    row += " ."
                else:
                    # Priority: Charging Station > Drone > Survivor
                    if any(isinstance(agent, SimpleChargingStationAgent) for agent in cell_contents):
                        row += " ⚡"
                    elif any(isinstance(agent, SimpleDroneAgent) for agent in cell_contents):
                        drone = next(agent for agent in cell_contents if isinstance(agent, SimpleDroneAgent))
                        if drone.battery > 60:
                            row += " 🟢"  # Green drone (healthy)
                        elif drone.battery > 30:
                            row += " 🟡"  # Yellow drone (medium)
                        else:
                            row += " 🔴"  # Red drone (low battery)
                    elif any(isinstance(agent, SimpleSurvivorAgent) for agent in cell_contents):
                        survivor = next(agent for agent in cell_contents if isinstance(agent, SimpleSurvivorAgent))
                        if survivor.found:
                            row += " ✅"  # Rescued survivor
                        else:
                            row += " 🆘"  # Survivor needs rescue
                    else:
                        row += " ?"
            print(row)
    
    def print_status(self):
        """Print system status"""
        drones = [a for a in self.model.custom_agents if isinstance(a, SimpleDroneAgent)]
        survivors = [a for a in self.model.custom_agents if isinstance(a, SimpleSurvivorAgent)]
        
        print(f"\n📊 System Status (Step {self.model.step_count}):")
        print("=" * 50)
        
        # Drone status table
        print("🚁 Drone Status:")
        print("ID       | Battery | Status   | Position")
        print("-" * 40)
        for drone in drones:
            battery_indicator = "🟢" if drone.battery > 60 else "🟡" if drone.battery > 30 else "🔴"
            print(f"{drone.unique_id:8} | {battery_indicator} {drone.battery:3d}% | {drone.status:8} | {drone.pos}")
        
        # Mission statistics
        rescued = len([s for s in survivors if s.found])
        total_survivors = len(survivors)
        active_drones = len([d for d in drones if d.status != 'charging'])
        avg_battery = sum([d.battery for d in drones]) / len(drones) if drones else 0
        
        print(f"\n📈 Mission Statistics:")
        print(f"   Active Drones: {active_drones}/{len(drones)}")
        print(f"   Survivors Rescued: {rescued}/{total_survivors} ({rescued/total_survivors*100:.1f}%)")
        print(f"   Average Battery: {avg_battery:.1f}%")
        
        # Recent mission log
        print(f"\n📝 Recent Mission Log:")
        recent_logs = self.model.mission_log[-5:] if len(self.model.mission_log) > 5 else self.model.mission_log
        for log_entry in recent_logs:
            print(f"   {log_entry}")
    
    def print_legend(self):
        """Print legend for symbols"""
        print("\n🔤 Legend:")
        print("   🟢 Healthy Drone (>60% battery)")
        print("   🟡 Medium Drone (30-60% battery)")
        print("   🔴 Low Battery Drone (<30% battery)")
        print("   🆘 Survivor (needs rescue)")
        print("   ✅ Rescued Survivor")
        print("   ⚡ Charging Station")
        print("   .  Empty Cell")
    
    def print_controls(self):
        """Print available controls"""
        print("\n🎮 Controls:")
        print("   [ENTER] - Single Step")
        print("   [a] - Auto Step (toggle)")
        print("   [r] - Reset Simulation")
        print("   [s] - Show Statistics")
        print("   [l] - Show Legend")
        print("   [q] - Quit")
    
    def create_model(self):
        """Create a new model"""
        print("🚁 Creating new drone swarm simulation...")
        
        # Get parameters from user
        try:
            width = int(input("Grid width (default 20): ") or "20")
            height = int(input("Grid height (default 20): ") or "20")
            n_drones = int(input("Number of drones (default 3): ") or "3")
            n_survivors = int(input("Number of survivors (default 5): ") or "5")
            n_stations = int(input("Number of charging stations (default 2): ") or "2")
        except ValueError:
            print("Using default values...")
            width, height, n_drones, n_survivors, n_stations = 20, 20, 3, 5, 2
        
        self.model = SimpleDroneSwarmModel(
            width=width, height=height, 
            n_drones=n_drones, n_survivors=n_survivors, 
            n_charging_stations=n_stations
        )
        
        print(f"✅ Model created: {width}x{height} grid, {n_drones} drones, {n_survivors} survivors")
    
    def auto_step_loop(self):
        """Auto-stepping loop in separate thread"""
        while self.auto_step and self.running:
            if self.model:
                self.model.step()
                self.update_display()
            time.sleep(1)  # 1 second between steps
    
    def update_display(self):
        """Update the display"""
        self.clear_screen()
        print("🚁 Autonomous Drone Swarm Command System - Console UI")
        print("=" * 60)
        
        if self.model:
            self.print_grid()
            self.print_status()
        
        if self.auto_step:
            print("\n🔄 Auto-stepping enabled (press 'a' to disable)")
        
        self.print_controls()
    
    def run(self):
        """Main UI loop"""
        print("🚁 Autonomous Drone Swarm Command System")
        print("=" * 60)
        print("Welcome to the Console UI!")
        
        # Create initial model
        self.create_model()
        self.running = True
        
        # Start auto-step thread
        auto_thread = threading.Thread(target=self.auto_step_loop, daemon=True)
        auto_thread.start()
        
        try:
            while self.running:
                self.update_display()
                
                # Get user input
                user_input = input("\nCommand: ").strip().lower()
                
                if user_input == 'q':
                    self.running = False
                    break
                elif user_input == '':
                    # Single step
                    if self.model:
                        self.model.step()
                elif user_input == 'a':
                    # Toggle auto step
                    self.auto_step = not self.auto_step
                    if self.auto_step:
                        print("🔄 Auto-stepping enabled")
                    else:
                        print("⏸️  Auto-stepping disabled")
                    time.sleep(1)
                elif user_input == 'r':
                    # Reset simulation
                    self.auto_step = False
                    self.create_model()
                elif user_input == 's':
                    # Show detailed statistics
                    self.clear_screen()
                    self.print_status()
                    input("\nPress ENTER to continue...")
                elif user_input == 'l':
                    # Show legend
                    self.clear_screen()
                    self.print_legend()
                    input("\nPress ENTER to continue...")
                else:
                    print("❌ Unknown command. Press ENTER for help.")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        
        finally:
            self.running = False
            self.auto_step = False
            print("👋 Goodbye!")

def main():
    """Main entry point"""
    ui = ConsoleUI()
    ui.run()

if __name__ == "__main__":
    main()