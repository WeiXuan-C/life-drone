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
        self.status = "idle"  # idle, scanning, moving, charging
        self.target = None
        
    def step(self):
        """Simple drone behavior"""
        # Decrease battery
        self.battery = max(0, self.battery - 1)
        
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
                else:
                    self.status = "moving"
                    self.move_towards(survivor.pos)
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

class SimpleChargingStationAgent(Agent):
    """Simplified charging station"""
    
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
    
    def step(self):
        pass

class SimpleDroneSwarmModel(Model):
    """Simplified model compatible with Mesa 3.x"""
    
    def __init__(self, width=20, height=20, n_drones=3, n_survivors=5, n_charging_stations=2):
        super().__init__()
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, True)
        self.custom_agents = []  # Use custom_agents instead of agents
        self.running = True
        self.step_count = 0
        self.mission_log = []
        
        # Create charging stations
        for i in range(n_charging_stations):
            station = SimpleChargingStationAgent(f"station_{i}", self)
            self.custom_agents.append(station)
            x, y = (1, 1) if i == 0 else (width - 2, height - 2)
            self.grid.place_agent(station, (x, y))
            self.log_event(f"Charging station deployed at ({x}, {y})")
        
        # Create drones
        for i in range(n_drones):
            drone = SimpleDroneAgent(f"drone_{i}", self)
            self.custom_agents.append(drone)
            x, y = random.randrange(3), random.randrange(3)
            self.grid.place_agent(drone, (x, y))
            self.log_event(f"Drone {drone.unique_id} deployed at ({x}, {y})")
        
        # Create survivors
        for i in range(n_survivors):
            survivor = SimpleSurvivorAgent(f"survivor_{i}", self)
            self.custom_agents.append(survivor)
            x, y = random.randrange(width), random.randrange(height)
            # Avoid placing on charging stations
            while len([a for a in self.grid.get_cell_list_contents([(x, y)]) 
                      if isinstance(a, SimpleChargingStationAgent)]) > 0:
                x, y = random.randrange(width), random.randrange(height)
            self.grid.place_agent(survivor, (x, y))
            self.log_event(f"Survivor signal detected at ({x}, {y})")
        
        # Data collector
        self.datacollector = DataCollector(
            model_reporters={
                "Active_Drones": lambda m: len([a for a in m.custom_agents 
                                              if isinstance(a, SimpleDroneAgent) and a.status != "charging"]),
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
        
        # Write to file
        os.makedirs("logs", exist_ok=True)
        with open("logs/mission.log", "a") as f:
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
            "position": drone.pos
        } for drone in drones]