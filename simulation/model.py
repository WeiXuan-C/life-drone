"""
Drone Swarm Simulation Model
Mesa-based model for autonomous drone rescue simulation
"""

import random
from mesa import Model
from mesa.time import Schedule
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from simulation.drone_agent import DroneAgent, SurvivorAgent, ChargingStationAgent
import datetime
import os

class DroneSwarmModel(Model):
    """A model with drones, survivors, and charging stations."""
    
    def __init__(self, width=20, height=20, n_drones=3, n_survivors=5, n_charging_stations=2):
        super().__init__()
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, True)
        self.schedule = Schedule(self)
        self.running = True
        self.step_count = 0
        
        # Mission log
        self.mission_log = []
        self.reasoning_log = []
        
        # Create charging stations first
        for i in range(n_charging_stations):
            station = ChargingStationAgent(f"station_{i}", self)
            self.schedule.add(station)
            # Place stations at corners
            if i == 0:
                x, y = 1, 1
            else:
                x, y = self.width - 2, self.height - 2
            self.grid.place_agent(station, (x, y))
            self.log_mission(f"Charging station deployed at ({x}, {y})")
        
        # Create drones
        for i in range(n_drones):
            drone = DroneAgent(f"drone_{i}", self)
            self.schedule.add(drone)
            # Place drones near charging stations initially
            x = random.randrange(3)
            y = random.randrange(3)
            self.grid.place_agent(drone, (x, y))
            self.log_mission(f"Drone {drone.unique_id} deployed at ({x}, {y})")
        
        # Create survivors
        for i in range(n_survivors):
            survivor = SurvivorAgent(f"survivor_{i}", self)
            self.schedule.add(survivor)
            # Place survivors randomly
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            # Ensure not on charging station
            while len([agent for agent in self.grid.get_cell_list_contents([(x, y)]) 
                      if isinstance(agent, ChargingStationAgent)]) > 0:
                x = random.randrange(self.width)
                y = random.randrange(self.height)
            self.grid.place_agent(survivor, (x, y))
            self.log_mission(f"Survivor signal detected at ({x}, {y})")
        
        # Data collector for charts
        self.datacollector = DataCollector(
            model_reporters={
                "Active_Drones": lambda m: len([a for a in m.schedule.agents 
                                              if isinstance(a, DroneAgent) and a.status != "charging"]),
                "Survivors_Found": lambda m: len([a for a in m.schedule.agents 
                                                if isinstance(a, SurvivorAgent) and a.found]),
                "Average_Battery": lambda m: sum([a.battery for a in m.schedule.agents 
                                                if isinstance(a, DroneAgent)]) / len([a for a in m.schedule.agents 
                                                if isinstance(a, DroneAgent)]) if len([a for a in m.schedule.agents 
                                                if isinstance(a, DroneAgent)]) > 0 else 0
            }
        )
    
    def log_mission(self, message):
        """Log mission events with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.mission_log.append(log_entry)
        
        # Also write to file
        os.makedirs("logs", exist_ok=True)
        with open("logs/mission.log", "a") as f:
            f.write(log_entry + "\n")
    
    def log_reasoning(self, drone_id, thought, decision, action, observation):
        """Log AI reasoning process"""
        reasoning_entry = {
            "drone_id": drone_id,
            "thought": thought,
            "decision": decision,
            "action": action,
            "observation": observation,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        }
        self.reasoning_log.append(reasoning_entry)
    
    def add_drone(self, x=None, y=None):
        """Dynamically add a new drone"""
        drone_count = len([a for a in self.schedule.agents if isinstance(a, DroneAgent)])
        drone = DroneAgent(f"drone_{drone_count}", self)
        self.schedule.add(drone)
        
        if x is None or y is None:
            x = random.randrange(self.width)
            y = random.randrange(self.height)
        
        self.grid.place_agent(drone, (x, y))
        self.log_mission(f"New drone {drone.unique_id} deployed at ({x}, {y})")
        return drone
    
    def add_survivor(self, x=None, y=None):
        """Dynamically add a survivor signal"""
        survivor_count = len([a for a in self.schedule.agents if isinstance(a, SurvivorAgent)])
        survivor = SurvivorAgent(f"survivor_{survivor_count}", self)
        self.schedule.add(survivor)
        
        if x is None or y is None:
            x = random.randrange(self.width)
            y = random.randrange(self.height)
        
        self.grid.place_agent(survivor, (x, y))
        self.log_mission(f"New survivor signal detected at ({x}, {y})")
        return survivor
    
    def get_drone_status(self):
        """Get status of all drones for UI display"""
        drones = [agent for agent in self.schedule.agents if isinstance(agent, DroneAgent)]
        status_list = []
        for drone in drones:
            status_list.append({
                "id": drone.unique_id,
                "battery": drone.battery,
                "status": drone.status,
                "position": drone.pos,
                "target": getattr(drone, 'target', None)
            })
        return status_list
    
    def step(self):
        """Advance the model by one step."""
        self.step_count += 1
        self.datacollector.collect(self)
        self.schedule.step()
        
        # Log step completion
        if self.step_count % 10 == 0:  # Log every 10 steps
            active_drones = len([a for a in self.schedule.agents 
                               if isinstance(a, DroneAgent) and a.status != "charging"])
            self.log_mission(f"Step {self.step_count}: {active_drones} drones active")