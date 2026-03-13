"""
Simplified Drone Swarm Model for Mesa 3.x
Compatible with the new Mesa API
"""

import random
from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import datetime
import os

class SimpleDroneAgent(Agent):
    """Simplified drone agent for Mesa 3.x"""
    
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
        self.battery = 100
        self.status = "idle"  # idle, scanning, moving, charging, returning_home
        self.target = None
        self.home_base = None  # Main return point for all drones
        
    def step(self):
        """Simple drone behavior with home base return capability"""
        # Decrease battery
        self.battery = max(0, self.battery - 1)
        
        # Check if drone should return home (emergency recall or mission complete)
        if hasattr(self.model, 'emergency_recall') and self.model.emergency_recall:
            self.status = "returning_home"
            if self.home_base and self.pos != self.home_base:
                self.move_towards(self.home_base)
                return
            elif self.pos == self.home_base:
                self.status = "at_home_base"
                return
        
        # Simple AI logic
        if self.battery <= 20:
            self.status = "charging"
            # Find charging station
            stations = [agent for agent in self.model.custom_agents 
                       if isinstance(agent, SimpleChargingStationAgent)]
            if stations:
                station = stations[0]
                if self.pos == station.pos:
                    self.battery = min(100, self.battery + 10)
                    # If fully charged and no emergency, return to normal operations
                    if self.battery >= 80 and not (hasattr(self.model, 'emergency_recall') and self.model.emergency_recall):
                        self.status = "idle"
                else:
                    self.move_towards(station.pos)
        else:
            # Look for survivors
            survivors = [agent for agent in self.model.custom_agents 
                        if isinstance(agent, SimpleSurvivorAgent) and not agent.found]
            if survivors:
                survivor = survivors[0]
                distance = self.get_distance(survivor.pos)
                if distance <= 1:
                    survivor.found = True
                    self.status = "rescuing"
                    self.model.log_event(f"Drone {self.unique_id} rescued survivor at {survivor.pos}")
                    # After rescue, check if should return home
                    if hasattr(self.model, 'return_home_after_mission') and self.model.return_home_after_mission:
                        self.status = "returning_home"
                else:
                    self.status = "moving"
                    self.move_towards(survivor.pos)
            else:
                # No survivors found - check if should return home or continue patrol
                if hasattr(self.model, 'return_home_when_idle') and self.model.return_home_when_idle:
                    if self.home_base and self.pos != self.home_base:
                        self.status = "returning_home"
                        self.move_towards(self.home_base)
                    else:
                        self.status = "at_home_base"
                else:
                    self.status = "scanning"
                    self.random_move()
    
    def move_towards(self, target_pos):
        """Move one step towards target"""
        if not target_pos:
            return
        
        x, y = self.pos
        target_x, target_y = target_pos
        
        dx = 0 if target_x == x else (1 if target_x > x else -1)
        dy = 0 if target_y == y else (1 if target_y > y else -1)
        
        new_x = max(0, min(self.model.grid.width - 1, x + dx))
        new_y = max(0, min(self.model.grid.height - 1, y + dy))
        
        self.model.grid.move_agent(self, (new_x, new_y))
    
    def random_move(self):
        """Move randomly"""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        if possible_steps:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)
    
    def get_distance(self, pos):
        """Calculate distance to position"""
        return abs(self.pos[0] - pos[0]) + abs(self.pos[1] - pos[1])

class SimpleSurvivorAgent(Agent):
    """Simplified survivor agent"""
    
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
        self.found = False
    
    def step(self):
        pass

class SimpleHomeBaseAgent(Agent):
    """Main home base where all drones return"""
    
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
        self.drones_at_base = []
        self.total_missions_completed = 0
    
    def step(self):
        """Monitor drones at base"""
        # Count drones currently at base
        drones_here = [agent for agent in self.model.grid.get_cell_list_contents([self.pos])
                      if isinstance(agent, SimpleDroneAgent)]
        self.drones_at_base = [drone.unique_id for drone in drones_here]

class SimpleChargingStationAgent(Agent):
    """Simplified charging station"""
    
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
    
    def step(self):
        pass

class SimpleDroneSwarmModel(Model):
    """Simplified model compatible with Mesa 3.x with home base functionality"""
    
    def __init__(self, width=20, height=20, n_drones=3, n_survivors=5, n_charging_stations=2, home_base_pos=(10, 10)):
        super().__init__()
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, True)
        self.custom_agents = []  # Use custom_agents instead of agents
        self.running = True
        self.step_count = 0
        self.mission_log = []
        
        # Home base configuration
        self.home_base_pos = home_base_pos
        self.emergency_recall = False
        self.return_home_after_mission = False
        self.return_home_when_idle = False
        
        # Create home base
        home_base = SimpleHomeBaseAgent("home_base", self)
        self.custom_agents.append(home_base)
        self.grid.place_agent(home_base, home_base_pos)
        self.log_event(f"🏠 Home Base established at {home_base_pos}")
        
        # Create charging stations
        for i in range(n_charging_stations):
            station = SimpleChargingStationAgent(f"station_{i}", self)
            self.custom_agents.append(station)
            x, y = (1, 1) if i == 0 else (width - 2, height - 2)
            self.grid.place_agent(station, (x, y))
            self.log_event(f"⚡ Charging station deployed at ({x}, {y})")
        
        # Create drones
        for i in range(n_drones):
            drone = SimpleDroneAgent(f"drone_{i}", self)
            drone.home_base = home_base_pos  # Set home base for each drone
            self.custom_agents.append(drone)
            # Start drones at home base
            x, y = home_base_pos
            self.grid.place_agent(drone, (x, y))
            self.log_event(f"🚁 Drone {drone.unique_id} deployed from home base at ({x}, {y})")
        
        # Create survivors
        for i in range(n_survivors):
            survivor = SimpleSurvivorAgent(f"survivor_{i}", self)
            self.custom_agents.append(survivor)
            x, y = random.randrange(width), random.randrange(height)
            # Avoid placing on charging stations or home base
            while len([a for a in self.grid.get_cell_list_contents([(x, y)]) 
                      if isinstance(a, (SimpleChargingStationAgent, SimpleHomeBaseAgent))]) > 0:
                x, y = random.randrange(width), random.randrange(height)
            self.grid.place_agent(survivor, (x, y))
            self.log_event(f"🆘 Survivor signal detected at ({x}, {y})")
        
        # Data collector
        self.datacollector = DataCollector(
            model_reporters={
                "Active_Drones": lambda m: len([a for a in m.custom_agents 
                                              if isinstance(a, SimpleDroneAgent) and a.status not in ["charging", "at_home_base"]]),
                "Drones_At_Home": lambda m: len([a for a in m.custom_agents 
                                               if isinstance(a, SimpleDroneAgent) and a.status == "at_home_base"]),
                "Survivors_Found": lambda m: len([a for a in m.custom_agents 
                                                if isinstance(a, SimpleSurvivorAgent) and a.found]),
                "Average_Battery": lambda m: sum([a.battery for a in m.custom_agents 
                                                if isinstance(a, SimpleDroneAgent)]) / len([a for a in m.custom_agents 
                                                if isinstance(a, SimpleDroneAgent)]) if len([a for a in m.custom_agents 
                                                if isinstance(a, SimpleDroneAgent)]) > 0 else 0
            }
        )
    
    def log_event(self, message):
        """Log mission events"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.mission_log.append(log_entry)
        
        # Write to file with UTF-8 encoding
        os.makedirs("logs", exist_ok=True)
        with open("logs/mission.log", "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def step(self):
        """Advance model by one step"""
        self.step_count += 1
        self.datacollector.collect(self)
        
        # Step all agents
        for agent in self.custom_agents:
            agent.step()
        
        # Log progress
        if self.step_count % 10 == 0:
            active_drones = len([a for a in self.custom_agents 
                               if isinstance(a, SimpleDroneAgent) and a.status != "charging"])
            self.log_event(f"Step {self.step_count}: {active_drones} drones active")
    
    def get_drone_status(self):
        """Get status of all drones"""
        drones = [a for a in self.custom_agents if isinstance(a, SimpleDroneAgent)]
        return [{
            "id": drone.unique_id,
            "battery": drone.battery,
            "status": drone.status,
            "position": drone.pos,
            "home_base": drone.home_base
        } for drone in drones]
    
    def recall_all_drones(self):
        """Emergency recall - all drones return to home base immediately"""
        self.emergency_recall = True
        self.log_event("🚨 EMERGENCY RECALL: All drones ordered to return to home base")
        
    def cancel_recall(self):
        """Cancel emergency recall"""
        self.emergency_recall = False
        self.log_event("✅ Emergency recall cancelled - drones resume normal operations")
    
    def set_return_home_after_mission(self, enabled=True):
        """Set whether drones should return home after completing missions"""
        self.return_home_after_mission = enabled
        status = "enabled" if enabled else "disabled"
        self.log_event(f"📋 Return home after mission: {status}")
    
    def set_return_home_when_idle(self, enabled=True):
        """Set whether drones should return home when idle (no survivors to rescue)"""
        self.return_home_when_idle = enabled
        status = "enabled" if enabled else "disabled"
        self.log_event(f"🏠 Return home when idle: {status}")
    
    def get_home_base_status(self):
        """Get status of home base and drones there"""
        home_base = next((a for a in self.custom_agents if isinstance(a, SimpleHomeBaseAgent)), None)
        if not home_base:
            return None
            
        drones_at_home = [a for a in self.custom_agents 
                         if isinstance(a, SimpleDroneAgent) and a.pos == self.home_base_pos]
        
        return {
            "position": self.home_base_pos,
            "drones_at_base": len(drones_at_home),
            "drone_ids": [drone.unique_id for drone in drones_at_home],
            "emergency_recall_active": self.emergency_recall,
            "return_home_after_mission": self.return_home_after_mission,
            "return_home_when_idle": self.return_home_when_idle
        }