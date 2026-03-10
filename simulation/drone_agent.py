"""
Drone Swarm Agents
Mesa agents for drone rescue simulation
"""

import random
import math
from mesa import Agent

class DroneAgent(Agent):
    """A drone agent with battery, status, and AI decision making."""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.battery = 100
        self.max_battery = 100
        self.status = "idle"  # idle, scanning, moving, charging, rescuing
        self.target = None
        self.scan_radius = 2
        self.move_cost = 2
        self.scan_cost = 1
        self.survivors_found = 0
        
    def get_battery_status(self):
        """Get battery status color indicator"""
        if self.battery > 60:
            return "healthy"
        elif self.battery > 30:
            return "medium"
        else:
            return "low"
    
    def find_nearest_charging_station(self):
        """Find the nearest charging station"""
        stations = [agent for agent in self.model.schedule.agents 
                   if isinstance(agent, ChargingStationAgent)]
        if not stations:
            return None
        
        min_distance = float('inf')
        nearest_station = None
        
        for station in stations:
            distance = math.sqrt((self.pos[0] - station.pos[0])**2 + 
                               (self.pos[1] - station.pos[1])**2)
            if distance < min_distance:
                min_distance = distance
                nearest_station = station
        
        return nearest_station
    
    def find_nearest_survivor(self):
        """Find the nearest unrescued survivor"""
        survivors = [agent for agent in self.model.schedule.agents 
                    if isinstance(agent, SurvivorAgent) and not agent.found]
        if not survivors:
            return None
        
        min_distance = float('inf')
        nearest_survivor = None
        
        for survivor in survivors:
            distance = math.sqrt((self.pos[0] - survivor.pos[0])**2 + 
                               (self.pos[1] - survivor.pos[1])**2)
            if distance < min_distance:
                min_distance = distance
                nearest_survivor = survivor
        
        return nearest_survivor
    
    def move_towards(self, target_pos):
        """Move one step towards target position"""
        if not target_pos or target_pos == self.pos:
            return False
        
        x, y = self.pos
        target_x, target_y = target_pos
        
        # Calculate direction
        dx = 0 if target_x == x else (1 if target_x > x else -1)
        dy = 0 if target_y == y else (1 if target_y > y else -1)
        
        new_x = max(0, min(self.model.width - 1, x + dx))
        new_y = max(0, min(self.model.height - 1, y + dy))
        
        self.model.grid.move_agent(self, (new_x, new_y))
        self.battery -= self.move_cost
        return True
    
    def scan_area(self):
        """Scan surrounding area for survivors"""
        self.battery -= self.scan_cost
        found_survivors = []
        
        # Check cells within scan radius
        for dx in range(-self.scan_radius, self.scan_radius + 1):
            for dy in range(-self.scan_radius, self.scan_radius + 1):
                x = self.pos[0] + dx
                y = self.pos[1] + dy
                
                if 0 <= x < self.model.width and 0 <= y < self.model.height:
                    cell_contents = self.model.grid.get_cell_list_contents([(x, y)])
                    for agent in cell_contents:
                        if isinstance(agent, SurvivorAgent) and not agent.found:
                            agent.found = True
                            agent.rescued_by = self.unique_id
                            found_survivors.append(agent)
                            self.survivors_found += 1
        
        return found_survivors
    
    def make_decision(self):
        """AI decision making process"""
        # Battery critical - must charge
        if self.battery <= 20:
            thought = f"Battery critical at {self.battery}%"
            decision = "Return to charging station immediately"
            station = self.find_nearest_charging_station()
            if station:
                action = f"move_to_station({station.pos})"
                self.target = station.pos
                self.status = "charging"
            else:
                action = "no_charging_station_available"
                self.status = "idle"
            
            observation = f"Battery: {self.battery}%, Status: {self.status}"
            self.model.log_reasoning(self.unique_id, thought, decision, action, observation)
            return
        
        # At charging station - charge if needed
        if self.status == "charging":
            stations = [agent for agent in self.model.grid.get_cell_list_contents([self.pos])
                       if isinstance(agent, ChargingStationAgent)]
            if stations and self.battery < self.max_battery:
                self.battery = min(self.max_battery, self.battery + 10)
                thought = f"At charging station, battery at {self.battery}%"
                decision = "Continue charging"
                action = "charge()"
                observation = f"Battery increased to {self.battery}%"
                self.model.log_reasoning(self.unique_id, thought, decision, action, observation)
                
                if self.battery >= 80:
                    self.status = "idle"
                    self.target = None
                return
        
        # Look for survivors to rescue
        if self.status in ["idle", "scanning"]:
            survivor = self.find_nearest_survivor()
            if survivor:
                distance = math.sqrt((self.pos[0] - survivor.pos[0])**2 + 
                                   (self.pos[1] - survivor.pos[1])**2)
                
                if distance <= self.scan_radius:
                    # Close enough to scan
                    thought = f"Survivor detected within scan range at {survivor.pos}"
                    decision = "Scan area for survivors"
                    action = f"scan_area(radius={self.scan_radius})"
                    found = self.scan_area()
                    observation = f"Found {len(found)} survivors"
                    self.status = "scanning"
                    self.model.log_reasoning(self.unique_id, thought, decision, action, observation)
                else:
                    # Move towards survivor
                    thought = f"Survivor detected at {survivor.pos}, distance: {distance:.1f}"
                    decision = "Move towards survivor location"
                    action = f"move_to({survivor.pos})"
                    self.target = survivor.pos
                    self.status = "moving"
                    observation = f"Moving from {self.pos} towards {survivor.pos}"
                    self.model.log_reasoning(self.unique_id, thought, decision, action, observation)
            else:
                # No survivors found, patrol randomly
                if not self.target or self.target == self.pos:
                    x = random.randrange(self.model.width)
                    y = random.randrange(self.model.height)
                    self.target = (x, y)
                
                thought = "No survivors detected in area"
                decision = "Continue patrol pattern"
                action = f"patrol_to({self.target})"
                self.status = "scanning"
                observation = f"Patrolling to {self.target}"
                self.model.log_reasoning(self.unique_id, thought, decision, action, observation)
    
    def step(self):
        """Execute one step of drone behavior"""
        if self.battery <= 0:
            self.status = "dead"
            return
        
        # Make AI decision
        self.make_decision()
        
        # Execute movement if needed
        if self.target and self.status in ["moving", "charging"]:
            moved = self.move_towards(self.target)
            if not moved or self.pos == self.target:
                self.target = None
                if self.status == "moving":
                    self.status = "scanning"


class SurvivorAgent(Agent):
    """A survivor agent that needs to be rescued."""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.found = False
        self.rescued_by = None
        self.signal_strength = random.randint(1, 10)
    
    def step(self):
        """Survivors don't move, just emit signals"""
        pass


class ChargingStationAgent(Agent):
    """A charging station for drones."""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.capacity = 2  # Can charge 2 drones simultaneously
        self.charging_rate = 10  # Battery points per step
    
    def step(self):
        """Charging stations are stationary"""
        pass