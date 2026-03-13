"""
Enhanced drone swarm model
Integrates terrain system, complex environment and advanced AI decision-making
"""

import random
import datetime
import os
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from simulation.enhanced_drone_agent import EnhancedDroneAgent, SimpleSurvivorAgent, SimpleChargingStationAgent
from simulation.terrain_system import TerrainGenerator, TerrainAnalyzer, TerrainType, ObstacleType, WeatherCondition

class EnhancedDroneSwarmModel(Model):
    """Enhanced drone swarm model with complex terrain and advanced AI support"""
    
    def __init__(self, width=20, height=20, n_drones=3, n_survivors=5, n_charging_stations=2, 
                 terrain_seed=None, weather_enabled=True, obstacles_enabled=True):
        super().__init__()
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, True)
        self.custom_agents = []
        self.running = True
        self.step_count = 0
        
        # Survivor assignment coordination
        self.survivor_assignments = {}  # {survivor_id: drone_id}
        self.drone_targets = {}  # {drone_id: survivor_id}
        
        # Terrain system
        self.terrain = TerrainGenerator.generate_realistic_terrain(
            width, height, seed=terrain_seed
        )
        self.weather_enabled = weather_enabled
        self.obstacles_enabled = obstacles_enabled
        
        # Logging system
        self.mission_log = []
        self.reasoning_log = []
        self.terrain_analysis_log = []
        
        # Performance statistics
        self.total_rescues = 0
        self.total_failed_attempts = 0
        self.total_distance_traveled = 0.0
        self.weather_delays = 0
        self.terrain_obstacles_encountered = 0
        
        # Create agents
        self._create_charging_stations(n_charging_stations)
        self._create_drones(n_drones)
        self._create_survivors(n_survivors)
        
        # Data collector
        self.datacollector = DataCollector(
            model_reporters={
                "Active_Drones": self._count_active_drones,
                "Survivors_Found": self._count_rescued_survivors,
                "Average_Battery": self._calculate_average_battery,
                "Weather_Delays": lambda m: m.weather_delays,
                "Terrain_Obstacles": lambda m: m.terrain_obstacles_encountered,
                "Total_Distance": lambda m: sum([d.total_distance_traveled for d in m.custom_agents 
                                                if isinstance(d, EnhancedDroneAgent)]),
                "Rescue_Success_Rate": self._calculate_rescue_success_rate
            }
        )
        
        # Record initial terrain analysis
        self._log_terrain_analysis()
    
    def _create_charging_stations(self, n_stations):
        """Create charging stations"""
        for i in range(n_stations):
            station = SimpleChargingStationAgent(f"station_{i}", self)
            self.custom_agents.append(station)
            
            # Place charging stations on flat terrain
            placed = False
            attempts = 0
            while not placed and attempts < 50:
                x = random.randrange(self.width)
                y = random.randrange(self.height)
                
                terrain_cell = self.terrain[y][x]
                # Select suitable terrain
                if (terrain_cell.terrain_type in [TerrainType.FLAT, TerrainType.URBAN] and
                    terrain_cell.obstacle is None):
                    
                    self.grid.place_agent(station, (x, y))
                    self.log_event(f"Charging station {station.unique_id} deployed on {terrain_cell.terrain_type.value} terrain at ({x}, {y})")
                    placed = True
                
                attempts += 1
            
            if not placed:
                # Force placement if no suitable location found
                x, y = (1, 1) if i == 0 else (self.width - 2, self.height - 2)
                self.grid.place_agent(station, (x, y))
                self.log_event(f"Charging station {station.unique_id} force deployed at ({x}, {y})")
    
    def _create_drones(self, n_drones):
        """Create drones"""
        for i in range(n_drones):
            drone = EnhancedDroneAgent(f"drone_{i}", self)
            self.custom_agents.append(drone)
            
            # Deploy drones near charging stations
            charging_stations = [a for a in self.custom_agents if isinstance(a, SimpleChargingStationAgent)]
            if charging_stations:
                station = charging_stations[0]  # Use first charging station
                station_x, station_y = station.pos
                
                # Find suitable position in 3x3 area around charging station
                # Try to place each drone in a different position
                placed = False
                attempts = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2)]
                
                # Offset attempts based on drone index to spread them out
                attempts = attempts[i:] + attempts[:i]
                
                for dx, dy in attempts:
                    x = max(0, min(self.width - 1, station_x + dx))
                    y = max(0, min(self.height - 1, station_y + dy))
                    
                    # Check if position is already occupied by another drone
                    cell_contents = self.grid.get_cell_list_contents((x, y))
                    has_drone = any(isinstance(agent, EnhancedDroneAgent) for agent in cell_contents)
                    
                    if not has_drone:
                        terrain_cell = self.terrain[y][x]
                        if terrain_cell.get_movement_cost() != float('inf'):
                            self.grid.place_agent(drone, (x, y))
                            terrain_info = f"{terrain_cell.terrain_type.value}"
                            if terrain_cell.weather != WeatherCondition.CLEAR:
                                terrain_info += f",{terrain_cell.weather.value}"
                            self.log_event(f"Drone {drone.unique_id} deployed on {terrain_info} at ({x}, {y})")
                            placed = True
                            break
                
                if not placed:
                    # Fall back to charging station position
                    self.grid.place_agent(drone, station.pos)
                    self.log_event(f"Drone {drone.unique_id} deployed at charging station position {station.pos}")
    
    def _create_survivors(self, n_survivors):
        """Create survivors"""
        for i in range(n_survivors):
            survivor = SimpleSurvivorAgent(f"survivor_{i}", self)
            self.custom_agents.append(survivor)
            
            # Randomly place survivors, but avoid unreachable locations
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                x = random.randrange(self.width)
                y = random.randrange(self.height)
                
                terrain_cell = self.terrain[y][x]
                # Avoid placing on impassable terrain
                if (terrain_cell.get_movement_cost() != float('inf') and
                    terrain_cell.obstacle != ObstacleType.BUILDING):
                    
                    # Check if there's already a charging station
                    cell_contents = self.grid.get_cell_list_contents([(x, y)])
                    if not any(isinstance(agent, SimpleChargingStationAgent) for agent in cell_contents):
                        self.grid.place_agent(survivor, (x, y))
                        terrain_info = f"{terrain_cell.terrain_type.value}"
                        if terrain_cell.obstacle:
                            terrain_info += f", near {terrain_cell.obstacle.value}"
                        self.log_event(f"Survivor signal {survivor.unique_id} detected at {terrain_info} ({x}, {y})")
                        placed = True
                
                attempts += 1
            
            if not placed:
                # Force placement at safe location
                x = random.randrange(self.width)
                y = random.randrange(self.height)
                self.grid.place_agent(survivor, (x, y))
                self.log_event(f"Survivor signal {survivor.unique_id} force placed at ({x}, {y})")
    
    def add_drone_manually(self, x, y, battery=100):
        """User manually adds drone"""
        # Check if position is suitable
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None, "Position out of bounds"
        
        terrain_cell = self.terrain[y][x]
        if terrain_cell.get_movement_cost() == float('inf'):
            return None, f"Cannot deploy drone on {terrain_cell.terrain_type.value} terrain"
        
        if terrain_cell.obstacle == ObstacleType.BUILDING:
            return None, "Building blocking, cannot deploy"
        
        # Create drone
        drone_count = len([a for a in self.custom_agents if isinstance(a, EnhancedDroneAgent)])
        drone_id = f"user_drone_{drone_count}"
        new_drone = EnhancedDroneAgent(drone_id, self)
        new_drone.battery = battery
        
        self.custom_agents.append(new_drone)
        self.grid.place_agent(new_drone, (x, y))
        
        # Record detailed information
        terrain_info = f"{terrain_cell.terrain_type.value} (altitude {terrain_cell.height:.0f}m)"
        if terrain_cell.weather != WeatherCondition.CLEAR:
            terrain_info += f", {terrain_cell.weather.value}"
        if terrain_cell.obstacle:
            terrain_info += f", near {terrain_cell.obstacle.value}"
        
        action = f"User added drone {drone_id} at {terrain_info} ({x},{y}), battery {battery}%"
        self.log_event(action)
        
        return new_drone, f"Successfully deployed at {terrain_info}"
    
    def add_survivor_manually(self, x, y):
        """User manually adds survivor"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None, "Position out of bounds"
        
        terrain_cell = self.terrain[y][x]
        
        # Create survivor
        survivor_count = len([a for a in self.custom_agents if isinstance(a, SimpleSurvivorAgent)])
        survivor_id = f"user_survivor_{survivor_count}"
        new_survivor = SimpleSurvivorAgent(survivor_id, self)
        
        self.custom_agents.append(new_survivor)
        self.grid.place_agent(new_survivor, (x, y))
        
        # Record detailed information
        terrain_info = f"{terrain_cell.terrain_type.value}"
        if terrain_cell.weather != WeatherCondition.CLEAR:
            terrain_info += f", {terrain_cell.weather.value} weather"
        
        action = f"User added survivor signal {survivor_id} at {terrain_info} ({x},{y})"
        self.log_event(action)
        
        return new_survivor, f"Signal activated at {terrain_info}"
    
    def add_charging_station_manually(self, x, y):
        """User manually adds charging station"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None, "Position out of bounds"
        
        # Check if position is already occupied by another charging station
        existing_agents = self.grid.get_cell_list_contents([(x, y)])
        for agent in existing_agents:
            if isinstance(agent, SimpleChargingStationAgent):
                return None, "Charging station already exists at this position"
        
        terrain_cell = self.terrain[y][x]
        
        # Check terrain suitability (allow more terrain types than automatic placement)
        if terrain_cell.obstacle == ObstacleType.BUILDING:
            return None, "Cannot place charging station on building"
        
        # Create charging station
        station_count = len([a for a in self.custom_agents if isinstance(a, SimpleChargingStationAgent)])
        station_id = f"user_station_{station_count}"
        new_station = SimpleChargingStationAgent(station_id, self)
        
        self.custom_agents.append(new_station)
        self.grid.place_agent(new_station, (x, y))
        
        # Record detailed information
        terrain_info = f"{terrain_cell.terrain_type.value}"
        if terrain_cell.weather != WeatherCondition.CLEAR:
            terrain_info += f", {terrain_cell.weather.value} weather"
        if terrain_cell.obstacle:
            terrain_info += f", near {terrain_cell.obstacle.value}"
        
        action = f"User deployed charging station {station_id} at {terrain_info} ({x},{y})"
        self.log_event(action)
        
        return new_station, f"Charging station deployed at {terrain_info}"
    
    def assign_survivor_to_drone(self, drone_id, survivor_id):
        """Assign a survivor to a drone for coordination"""
        # Clear any previous assignment for this drone
        if drone_id in self.drone_targets:
            old_survivor_id = self.drone_targets[drone_id]
            if old_survivor_id in self.survivor_assignments:
                del self.survivor_assignments[old_survivor_id]
        
        # Make new assignment
        self.survivor_assignments[survivor_id] = drone_id
        self.drone_targets[drone_id] = survivor_id
        
    def release_survivor_assignment(self, drone_id):
        """Release a drone's survivor assignment"""
        if drone_id in self.drone_targets:
            survivor_id = self.drone_targets[drone_id]
            if survivor_id in self.survivor_assignments:
                del self.survivor_assignments[survivor_id]
            del self.drone_targets[drone_id]
    
    def get_available_survivors(self, requesting_drone_id):
        """Get survivors that are not assigned to other drones"""
        all_survivors = [agent for agent in self.custom_agents 
                        if hasattr(agent, 'found') and not agent.found]
        
        available_survivors = []
        for survivor in all_survivors:
            survivor_id = survivor.unique_id
            # Include if not assigned, or assigned to the requesting drone
            if (survivor_id not in self.survivor_assignments or 
                self.survivor_assignments[survivor_id] == requesting_drone_id):
                available_survivors.append(survivor)
        
        return available_survivors
    
    def is_survivor_assigned(self, survivor_id, drone_id):
        """Check if a survivor is assigned to a specific drone"""
        return (survivor_id in self.survivor_assignments and 
                self.survivor_assignments[survivor_id] == drone_id)
    
    def get_terrain_info(self, x, y):
        """Get terrain information at specified location"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        
        terrain_cell = self.terrain[y][x]
        
        info = {
            "terrain_type": terrain_cell.terrain_type.value,
            "height": terrain_cell.height,
            "weather": terrain_cell.weather.value,
            "obstacle": terrain_cell.obstacle.value if terrain_cell.obstacle else None,
            "movement_cost": terrain_cell.get_movement_cost(),
            "scan_efficiency": terrain_cell.get_scan_efficiency(),
            "communication_quality": terrain_cell.get_communication_quality(),
            "visibility": terrain_cell.visibility,
            "wind_speed": terrain_cell.wind_speed
        }
        
        return info
    
    def get_ai_analysis(self):
        """Get enhanced AI analysis"""
        drones = [a for a in self.custom_agents if isinstance(a, EnhancedDroneAgent)]
        survivors = [a for a in self.custom_agents if isinstance(a, SimpleSurvivorAgent)]
        
        analysis = {
            "total_drones": len(drones),
            "active_drones": len([d for d in drones if d.status not in ['charging', 'crashed']]),
            "total_survivors": len(survivors),
            "rescued": len([s for s in survivors if s.found]),
            "avg_battery": sum([d.battery for d in drones]) / len(drones) if drones else 0,
            "status_distribution": {},
            "terrain_challenges": self.terrain_obstacles_encountered,
            "weather_delays": self.weather_delays,
            "total_distance": sum([d.total_distance_traveled for d in drones]),
            "rescue_success_rate": self._calculate_rescue_success_rate(),
            "ai_decisions": [],
            "terrain_analysis": self._get_current_terrain_analysis()
        }
        
        # Count drone status distribution
        for drone in drones:
            status = drone.status
            analysis["status_distribution"][status] = analysis["status_distribution"].get(status, 0) + 1
        
        # Get recent AI decisions
        for drone in drones:
            if drone.decision_history:
                latest_decision = drone.decision_history[-1]
                analysis["ai_decisions"].append({
                    "drone": drone.unique_id,
                    "thought": latest_decision["thought"],
                    "decision": latest_decision["decision"],
                    "terrain": latest_decision["terrain_info"]
                })
        
        return analysis
    
    def _get_current_terrain_analysis(self):
        """Get current terrain analysis"""
        terrain_stats = {
            "terrain_distribution": {},
            "obstacle_count": 0,
            "weather_conditions": {},
            "avg_altitude": 0.0
        }
        
        total_height = 0.0
        cell_count = 0
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.terrain[y][x]
                cell_count += 1
                
                # Terrain distribution
                terrain_type = cell.terrain_type.value
                terrain_stats["terrain_distribution"][terrain_type] = terrain_stats["terrain_distribution"].get(terrain_type, 0) + 1
                
                # Obstacle statistics
                if cell.obstacle:
                    terrain_stats["obstacle_count"] += 1
                
                # Weather conditions
                weather = cell.weather.value
                terrain_stats["weather_conditions"][weather] = terrain_stats["weather_conditions"].get(weather, 0) + 1
                
                # Height statistics
                total_height += cell.height
        
        if cell_count > 0:
            terrain_stats["avg_altitude"] = total_height / cell_count
        
        return terrain_stats
    
    def step(self):
        """Execute one simulation step"""
        self.step_count += 1
        self.datacollector.collect(self)
        
        # Update weather conditions (every 10 steps)
        if self.step_count % 10 == 0 and self.weather_enabled:
            self._update_weather_conditions()
        
        # Execute all agent steps
        for agent in self.custom_agents:
            if hasattr(agent, 'step'):
                agent.step()
        
        # Update performance statistics
        self._update_performance_stats()
        
        # Record important events
        if self.step_count % 20 == 0:
            self._log_periodic_status()
    
    def _update_weather_conditions(self):
        """Update weather conditions"""
        # Randomly change weather in some areas
        weather_change_probability = 0.1
        
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < weather_change_probability:
                    cell = self.terrain[y][x]
                    old_weather = cell.weather
                    
                    # Weather transition logic
                    if cell.weather == WeatherCondition.CLEAR:
                        new_weather = random.choice([WeatherCondition.WIND, WeatherCondition.RAIN])
                    elif cell.weather == WeatherCondition.STORM:
                        new_weather = random.choice([WeatherCondition.RAIN, WeatherCondition.WIND])
                    else:
                        new_weather = random.choice([WeatherCondition.CLEAR, WeatherCondition.FOG])
                    
                    cell.weather = new_weather
                    
                    if old_weather != new_weather:
                        self.log_event(f"Weather change: ({x},{y}) {old_weather.value} → {new_weather.value}")
    
    def _update_performance_stats(self):
        """Update performance statistics"""
        drones = [a for a in self.custom_agents if isinstance(a, EnhancedDroneAgent)]
        
        # Count rescue situations
        self.total_rescues = sum([d.successful_rescues for d in drones])
        self.total_failed_attempts = sum([d.failed_attempts for d in drones])
        
        # Count weather delays
        weather_affected_drones = len([d for d in drones if d.status == 'weather_hold'])
        if weather_affected_drones > 0:
            self.weather_delays += 1
    
    def _log_periodic_status(self):
        """Record periodic status"""
        active_drones = self._count_active_drones()
        rescued_survivors = self._count_rescued_survivors()
        avg_battery = self._calculate_average_battery()
        
        status_msg = (f"Step {self.step_count}: {active_drones} drones active, "
                     f"{rescued_survivors} survivors rescued, average battery {avg_battery:.1f}%")
        
        if self.weather_delays > 0:
            status_msg += f", {self.weather_delays} weather delays"
        
        if self.terrain_obstacles_encountered > 0:
            status_msg += f", {self.terrain_obstacles_encountered} terrain obstacles"
        
        self.log_event(status_msg)
    
    def _log_terrain_analysis(self):
        """Record terrain analysis"""
        analysis = self._get_current_terrain_analysis()
        
        terrain_summary = []
        for terrain_type, count in analysis["terrain_distribution"].items():
            percentage = (count / (self.width * self.height)) * 100
            terrain_summary.append(f"{terrain_type}({percentage:.1f}%)")
        
        log_msg = (f"Terrain analysis: {', '.join(terrain_summary)}, "
                  f"{analysis['obstacle_count']} obstacles, "
                  f"average altitude {analysis['avg_altitude']:.0f}m")
        
        self.log_event(log_msg)
        self.terrain_analysis_log.append(analysis)
    
    # Data collector methods
    def _count_active_drones(self):
        return len([a for a in self.custom_agents 
                   if isinstance(a, EnhancedDroneAgent) and a.status not in ['charging', 'crashed']])
    
    def _count_rescued_survivors(self):
        return len([a for a in self.custom_agents 
                   if isinstance(a, SimpleSurvivorAgent) and a.found])
    
    def _calculate_average_battery(self):
        drones = [a for a in self.custom_agents if isinstance(a, EnhancedDroneAgent)]
        if drones:
            return sum([d.battery for d in drones]) / len(drones)
        return 0.0
    
    def _calculate_rescue_success_rate(self):
        total_attempts = self.total_rescues + self.total_failed_attempts
        if total_attempts > 0:
            return (self.total_rescues / total_attempts) * 100
        return 0.0
    
    def log_event(self, message):
        """Record event log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.mission_log.append(log_entry)
        
        # Write to file
        os.makedirs("logs", exist_ok=True)
        with open("logs/mission.log", "a", encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def log_reasoning(self, drone_id, thought, decision, action, observation):
        """Record AI reasoning process"""
        reasoning_entry = {
            "drone_id": drone_id,
            "thought": thought,
            "decision": decision,
            "action": action,
            "observation": observation,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "step": self.step_count
        }
        self.reasoning_log.append(reasoning_entry)
        
        # Limit log length
        if len(self.reasoning_log) > 100:
            self.reasoning_log = self.reasoning_log[-100:]