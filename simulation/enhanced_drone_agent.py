"""
Enhanced drone agent
Supports complex terrain navigation, path planning and advanced AI decision-making
"""

import random
import math
from mesa import Agent
from typing import Tuple, List, Dict, Optional
from simulation.terrain_system import (
    TerrainCell, TerrainType, ObstacleType, WeatherCondition,
    PathfindingSystem, TerrainAnalyzer
)

class EnhancedDroneAgent(Agent):
    """Enhanced drone agent with complex terrain navigation capability"""
    
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
        
        # Basic attributes
        self.battery = 100
        self.max_battery = 100
        self.status = "idle"
        self.target = None
        self.planned_path = []
        self.current_path_index = 0
        
        # Enhanced attributes
        self.flight_altitude = 50  # Flight altitude (meters)
        self.max_altitude = 200
        self.scan_radius = 2
        self.communication_range = 5
        
        # AI decision-making related
        self.decision_history = []
        self.reasoning_steps = []
        self.risk_tolerance = 0.7  # Risk tolerance (0-1)
        self.energy_efficiency_priority = 0.8  # Energy efficiency priority
        self.mission_priority = 0.9  # Mission priority
        
        # Performance statistics
        self.total_distance_traveled = 0.0
        self.successful_rescues = 0
        self.failed_attempts = 0
        self.terrain_analysis_cache = {}
        
        # Sensor and device status
        self.gps_accuracy = 1.0
        self.camera_quality = 1.0
        self.communication_quality = 1.0
        
    def step(self):
        """Execute one step of AI decision-making and action"""
        if self.battery <= 0:
            self.status = "crashed"
            self.log_reasoning("Battery depleted", "Drone crashed", "emergency_landing", "System shutdown")
            return
        
        # Get current terrain information
        current_terrain = self.get_current_terrain()
        
        # Execute multi-step AI reasoning
        self.perform_ai_reasoning(current_terrain)
        
        # Execute decision
        self.execute_decision()
        
        # Update status
        self.update_status(current_terrain)
    
    def perform_ai_reasoning(self, current_terrain: TerrainCell):
        """Execute multi-step AI reasoning process"""
        self.reasoning_steps = []
        
        # Step 1: Environment perception and analysis
        env_analysis = self.analyze_environment(current_terrain)
        self.reasoning_steps.append(f"Environment Analysis: {env_analysis}")
        
        # Step 2: Threat assessment
        threat_assessment = self.assess_threats(current_terrain)
        self.reasoning_steps.append(f"Threat Assessment: {threat_assessment}")
        
        # Step 3: Resource status evaluation
        resource_status = self.evaluate_resources()
        self.reasoning_steps.append(f"Resource Status: {resource_status}")
        
        # Step 4: Mission priority analysis
        mission_analysis = self.analyze_mission_priorities()
        self.reasoning_steps.append(f"Mission Analysis: {mission_analysis}")
        
        # Step 5: Path planning and risk assessment
        path_analysis = self.plan_optimal_path()
        self.reasoning_steps.append(f"Path Planning: {path_analysis}")
        
        # Step 6: Final decision
        final_decision = self.make_final_decision()
        self.reasoning_steps.append(f"Final Decision: {final_decision}")
        
        # Record complete reasoning process
        self.log_reasoning(
            thought=f"Multi-step reasoning completed, {len(self.reasoning_steps)} steps total",
            decision=final_decision,
            action=self.status,
            observation="Reasoning process recorded"
        )
    
    def analyze_environment(self, current_terrain: TerrainCell) -> str:
        """Analyze current environment"""
        analysis_parts = []
        
        # Terrain analysis
        terrain_info = f"Terrain:{current_terrain.terrain_type.value}"
        if current_terrain.height > 1000:
            terrain_info += f",High altitude({current_terrain.height:.0f}m)"
        analysis_parts.append(terrain_info)
        
        # Weather analysis
        weather_info = f"Weather:{current_terrain.weather.value}"
        if current_terrain.weather != WeatherCondition.CLEAR:
            weather_info += f",Visibility {current_terrain.visibility:.1f}"
        analysis_parts.append(weather_info)
        
        # Obstacle analysis
        if current_terrain.obstacle:
            analysis_parts.append(f"Obstacle:{current_terrain.obstacle.value}")
        
        # Communication quality
        comm_quality = current_terrain.get_communication_quality()
        if comm_quality < 0.5:
            analysis_parts.append(f"Limited communication({comm_quality:.1f})")
        
        return ", ".join(analysis_parts)
    
    def assess_threats(self, current_terrain: TerrainCell) -> str:
        """Assess threats and risks"""
        threats = []
        risk_level = 0.0
        
        # Weather threats
        if current_terrain.weather == WeatherCondition.STORM:
            threats.append("Storm threat")
            risk_level += 0.8
        elif current_terrain.weather == WeatherCondition.WIND:
            threats.append("Strong wind impact")
            risk_level += 0.4
        elif current_terrain.weather == WeatherCondition.FOG:
            threats.append("Extremely low visibility")
            risk_level += 0.6
        
        # Terrain threats
        if current_terrain.terrain_type in [TerrainType.MOUNTAIN, TerrainType.CLIFF]:
            threats.append("Complex terrain")
            risk_level += 0.5
        
        # Battery threats
        if self.battery < 30:
            threats.append("Insufficient battery")
            risk_level += 0.7
        elif self.battery < 50:
            threats.append("Low battery")
            risk_level += 0.3
        
        # Obstacle threats
        if current_terrain.obstacle == ObstacleType.BUILDING:
            threats.append("Building obstruction")
            risk_level += 0.6
        
        risk_description = "Low risk"
        if risk_level > 0.7:
            risk_description = "High risk"
        elif risk_level > 0.4:
            risk_description = "Medium risk"
        
        if threats:
            return f"{risk_description}: {', '.join(threats)}"
        else:
            return "Environment safe"
    
    def evaluate_resources(self) -> str:
        """Evaluate resource status"""
        resources = []
        
        # Battery status
        if self.battery > 80:
            resources.append("Battery sufficient")
        elif self.battery > 50:
            resources.append("Battery good")
        elif self.battery > 30:
            resources.append("Battery low")
        else:
            resources.append("Battery critical")
        
        # Equipment status
        if self.camera_quality < 0.7:
            resources.append("Camera damaged")
        if self.gps_accuracy < 0.8:
            resources.append("Weak GPS signal")
        if self.communication_quality < 0.6:
            resources.append("Limited communication")
        
        # Flight capability
        current_terrain = self.get_current_terrain()
        if current_terrain and current_terrain.height > self.max_altitude:
            resources.append("Altitude limited")
        
        return ", ".join(resources) if resources else "All systems normal"
    
    def analyze_mission_priorities(self) -> str:
        """Analyze mission priorities"""
        priorities = []
        
        # Emergency priority
        if self.battery <= 20:
            priorities.append("Emergency charging(Priority:Highest)")
            return ", ".join(priorities)
        
        # Find survivors
        survivors = self.find_nearby_survivors()
        if survivors:
            closest_survivor = min(survivors, key=lambda s: self.calculate_terrain_distance(s.pos))
            distance = self.calculate_terrain_distance(closest_survivor.pos)
            
            # Check if already assigned to this drone
            if self.model.is_survivor_assigned(closest_survivor.unique_id, self.unique_id):
                priorities.append(f"Continue rescue {closest_survivor.unique_id}@{closest_survivor.pos}(Distance:{distance:.1f})")
            else:
                priorities.append(f"Rescue survivor@{closest_survivor.pos}(Distance:{distance:.1f})")
        
        # Area scanning
        if not survivors:
            priorities.append("Area scan search")
        
        # Charging station maintenance
        if self.battery < 60:
            charging_stations = self.find_charging_stations()
            if charging_stations:
                closest_station = min(charging_stations, key=lambda s: self.calculate_terrain_distance(s.pos))
                distance = self.calculate_terrain_distance(closest_station.pos)
                priorities.append(f"Go to charging station@{closest_station.pos}(Distance:{distance:.1f})")
        
        return ", ".join(priorities) if priorities else "No urgent tasks"
    
    def plan_optimal_path(self) -> str:
        """Plan optimal path"""
        if not self.target:
            return "No target, no path planning needed"
        
        # Use terrain system to calculate optimal path
        terrain = self.model.terrain
        start = self.pos
        end = self.target
        
        # Calculate multiple possible paths
        direct_distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        terrain_distance = PathfindingSystem.calculate_real_distance(terrain, start, end)
        
        # Path complexity analysis
        if terrain_distance == float('inf'):
            return f"Target unreachable, need to reselect target"
        
        complexity_ratio = terrain_distance / direct_distance if direct_distance > 0 else 1.0
        
        if complexity_ratio > 3.0:
            return f"Path extremely complex(Complexity:{complexity_ratio:.1f}), recommend detour"
        elif complexity_ratio > 2.0:
            return f"Path complex(Complexity:{complexity_ratio:.1f}), navigate carefully"
        elif complexity_ratio > 1.5:
            return f"Path medium difficulty(Complexity:{complexity_ratio:.1f})"
        else:
            return f"Path relatively simple(Complexity:{complexity_ratio:.1f})"
    
    def make_final_decision(self) -> str:
        """Make final decision"""
        current_terrain = self.get_current_terrain()
        
        # Emergency handling
        if self.battery <= 15:
            # Release any survivor assignment when going to emergency mode
            self.model.release_survivor_assignment(self.unique_id)
            self.status = "emergency_return"
            self.target = self.find_nearest_charging_station()
            return "Battery extremely low, emergency return to charging station"
        
        # Severe weather handling
        if current_terrain and current_terrain.weather == WeatherCondition.STORM:
            if self.battery > 50:
                self.status = "weather_hold"
                return "Storm weather, holding position"
            else:
                # Release any survivor assignment when going to emergency mode
                self.model.release_survivor_assignment(self.unique_id)
                self.status = "emergency_return"
                self.target = self.find_nearest_charging_station()
                return "Storm + low battery, emergency return"
        
        # Normal mission decision
        if self.status == "charging":
            if self.battery >= 80:
                self.status = "idle"
                return "Charging complete, ready for mission"
            else:
                return "Continuing to charge"
        
        # Find rescue targets
        survivors = self.find_nearby_survivors()
        if survivors:
            closest_survivor = min(survivors, key=lambda s: self.calculate_terrain_distance(s.pos))
            distance = self.calculate_terrain_distance(closest_survivor.pos)
            
            # Evaluate if there's enough battery to complete rescue
            estimated_cost = distance * 2 + 20  # Round trip + rescue operation
            if self.battery > estimated_cost:
                # Assign this survivor to this drone to prevent conflicts
                self.model.assign_survivor_to_drone(self.unique_id, closest_survivor.unique_id)
                self.target = closest_survivor.pos
                self.status = "rescue_mission"
                return f"Execute rescue mission to {closest_survivor.unique_id}, target distance {distance:.1f}"
            else:
                # Release any survivor assignment when switching to charging
                self.model.release_survivor_assignment(self.unique_id)
                self.status = "charging"
                self.target = self.find_nearest_charging_station()
                return "Insufficient battery to complete rescue, charging first"
        
        # Area scanning
        self.status = "area_scan"
        return "Execute area scan mission"
    
    def execute_decision(self):
        """Execute decision"""
        if self.status == "charging":
            self.handle_charging()
        elif self.status in ["rescue_mission", "emergency_return"]:
            self.handle_movement()
        elif self.status == "area_scan":
            self.handle_area_scan()
        elif self.status == "weather_hold":
            self.handle_weather_hold()
    
    def handle_movement(self):
        """Handle movement"""
        if not self.target:
            return
        
        # If no planned path or path completed, replan
        if not self.planned_path or self.current_path_index >= len(self.planned_path):
            terrain = self.model.terrain
            self.planned_path = PathfindingSystem.a_star_pathfinding(terrain, self.pos, self.target)
            self.current_path_index = 0
        
        # Move along planned path
        if self.planned_path and self.current_path_index < len(self.planned_path):
            next_pos = self.planned_path[self.current_path_index]
            
            # Check terrain at next position
            if self.can_move_to(next_pos):
                old_pos = self.pos
                self.model.grid.move_agent(self, next_pos)
                
                # Calculate movement cost
                terrain_cell = self.get_terrain_at(next_pos)
                move_cost = terrain_cell.get_movement_cost() if terrain_cell else 2.0
                self.battery -= move_cost
                
                # Update statistics
                distance = math.sqrt((next_pos[0] - old_pos[0])**2 + (next_pos[1] - old_pos[1])**2)
                self.total_distance_traveled += distance
                
                self.current_path_index += 1
                
                # Check if target reached
                if next_pos == self.target:
                    self.handle_target_reached()
            else:
                # Path blocked, replan
                self.planned_path = []
                self.current_path_index = 0
    
    def handle_charging(self):
        """Handle charging"""
        # Check if at charging station
        charging_stations = [agent for agent in self.model.grid.get_cell_list_contents([self.pos])
                           if hasattr(agent, 'unique_id') and 'station' in str(agent.unique_id)]
        
        if charging_stations:
            charge_rate = 10
            # Terrain may affect charging efficiency
            current_terrain = self.get_current_terrain()
            if current_terrain and current_terrain.weather == WeatherCondition.STORM:
                charge_rate = 5  # Severe weather affects charging
            
            self.battery = min(self.max_battery, self.battery + charge_rate)
        else:
            # Not at charging station, need to move to charging station
            self.target = self.find_nearest_charging_station()
            if self.target:
                self.handle_movement()
    
    def handle_area_scan(self):
        """Handle area scanning"""
        current_terrain = self.get_current_terrain()
        scan_efficiency = current_terrain.get_scan_efficiency() if current_terrain else 0.5
        
        # Scan surrounding area for survivors
        scan_cost = 1.0 / scan_efficiency  # Lower efficiency, higher cost
        self.battery -= scan_cost
        
        # Find survivors within scan range
        found_survivors = []
        for dx in range(-self.scan_radius, self.scan_radius + 1):
            for dy in range(-self.scan_radius, self.scan_radius + 1):
                scan_pos = (self.pos[0] + dx, self.pos[1] + dy)
                if (0 <= scan_pos[0] < self.model.height and 
                    0 <= scan_pos[1] < self.model.width):
                    
                    cell_contents = self.model.grid.get_cell_list_contents([scan_pos])
                    for agent in cell_contents:
                        if (hasattr(agent, 'found') and not agent.found and 
                            random.random() < scan_efficiency):
                            found_survivors.append(agent)
        
        if found_survivors:
            # Found survivors, switch to rescue mode
            closest_survivor = min(found_survivors, key=lambda s: self.calculate_terrain_distance(s.pos))
            self.target = closest_survivor.pos
            self.status = "rescue_mission"
        else:
            # Random move to continue search
            self.random_move()
    
    def handle_weather_hold(self):
        """Handle severe weather waiting"""
        # Wait in severe weather, consume small amount of battery to maintain systems
        self.battery -= 0.5
        
        # Check if weather has improved
        current_terrain = self.get_current_terrain()
        if current_terrain and current_terrain.weather != WeatherCondition.STORM:
            self.status = "idle"
    
    def handle_target_reached(self):
        """Handle target reached"""
        if self.status == "rescue_mission":
            # Release survivor assignment since we're at the target
            self.model.release_survivor_assignment(self.unique_id)
            
            # Attempt to rescue survivors
            survivors_here = [agent for agent in self.model.grid.get_cell_list_contents([self.pos])
                            if hasattr(agent, 'found') and not agent.found]
            
            for survivor in survivors_here:
                current_terrain = self.get_current_terrain()
                rescue_efficiency = current_terrain.get_scan_efficiency() if current_terrain else 0.8
                
                if random.random() < rescue_efficiency:
                    survivor.found = True
                    survivor.rescued_by = self.unique_id
                    self.successful_rescues += 1
                    self.model.log_event(f"Drone {self.unique_id} successfully rescued survivor {survivor.unique_id}")
                else:
                    self.failed_attempts += 1
                    self.model.log_event(f"Drone {self.unique_id} rescue failed, poor environmental conditions")
        
        # Clear target and path
        self.target = None
        self.planned_path = []
        self.current_path_index = 0
        self.status = "idle"
    
    def update_status(self, current_terrain: TerrainCell):
        """Update status"""
        # Update equipment status based on environmental conditions
        if current_terrain:
            # Weather affects equipment
            if current_terrain.weather == WeatherCondition.STORM:
                self.camera_quality *= 0.95
                self.gps_accuracy *= 0.98
            elif current_terrain.weather == WeatherCondition.RAIN:
                self.camera_quality *= 0.99
            
            # Communication quality
            self.communication_quality = current_terrain.get_communication_quality()
            
            # Terrain effects
            if current_terrain.terrain_type == TerrainType.MOUNTAIN:
                self.gps_accuracy *= 0.99
    
    # Helper methods
    def get_current_terrain(self) -> Optional[TerrainCell]:
        """Get terrain at current position"""
        if hasattr(self.model, 'terrain') and self.pos:
            y, x = self.pos
            if 0 <= y < len(self.model.terrain) and 0 <= x < len(self.model.terrain[0]):
                return self.model.terrain[y][x]
        return None
    
    def get_terrain_at(self, pos: Tuple[int, int]) -> Optional[TerrainCell]:
        """Get terrain at specified position"""
        if hasattr(self.model, 'terrain'):
            y, x = pos
            if 0 <= y < len(self.model.terrain) and 0 <= x < len(self.model.terrain[0]):
                return self.model.terrain[y][x]
        return None
    
    def can_move_to(self, pos: Tuple[int, int]) -> bool:
        """Check if can move to specified position"""
        terrain_cell = self.get_terrain_at(pos)
        if not terrain_cell:
            return False
        
        move_cost = terrain_cell.get_movement_cost()
        return move_cost != float('inf') and self.battery > move_cost
    
    def calculate_terrain_distance(self, target_pos: Tuple[int, int]) -> float:
        """Calculate distance considering terrain"""
        if hasattr(self.model, 'terrain'):
            return PathfindingSystem.calculate_real_distance(self.model.terrain, self.pos, target_pos)
        else:
            # Fallback to Euclidean distance
            return math.sqrt((target_pos[0] - self.pos[0])**2 + (target_pos[1] - self.pos[1])**2)
    
    def find_nearby_survivors(self):
        """Find nearby survivors that are not assigned to other drones"""
        # Get available survivors (not assigned to other drones)
        survivors = self.model.get_available_survivors(self.unique_id)
        
        # Sort by terrain distance
        survivors.sort(key=lambda s: self.calculate_terrain_distance(s.pos))
        return survivors[:5]  # Return closest 5
    
    def find_charging_stations(self):
        """Find charging stations"""
        stations = [agent for agent in self.model.custom_agents 
                   if hasattr(agent, 'unique_id') and 'station' in str(agent.unique_id)]
        return stations
    
    def find_nearest_charging_station(self):
        """Find nearest charging station"""
        stations = self.find_charging_stations()
        if stations:
            nearest = min(stations, key=lambda s: self.calculate_terrain_distance(s.pos))
            return nearest.pos
        return None
    
    def random_move(self):
        """Random move"""
        possible_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_pos = (self.pos[0] + dy, self.pos[1] + dx)
                if (0 <= new_pos[0] < self.model.height and 
                    0 <= new_pos[1] < self.model.width and
                    self.can_move_to(new_pos)):
                    possible_moves.append(new_pos)
        
        if possible_moves:
            new_pos = random.choice(possible_moves)
            old_pos = self.pos
            self.model.grid.move_agent(self, new_pos)
            
            # Calculate movement cost
            terrain_cell = self.get_terrain_at(new_pos)
            move_cost = terrain_cell.get_movement_cost() if terrain_cell else 2.0
            self.battery -= move_cost
    
    def log_reasoning(self, thought: str, decision: str, action: str, observation: str):
        """Log reasoning process"""
        reasoning_entry = {
            "drone_id": self.unique_id,
            "thought": thought,
            "decision": decision,
            "action": action,
            "observation": observation,
            "reasoning_steps": self.reasoning_steps.copy(),
            "battery": self.battery,
            "position": self.pos,
            "terrain_info": self.analyze_environment(self.get_current_terrain()) if self.get_current_terrain() else "Unknown terrain"
        }
        
        if hasattr(self.model, 'log_reasoning'):
            self.model.log_reasoning(
                self.unique_id, thought, decision, action, 
                f"{observation} | Terrain: {reasoning_entry['terrain_info']}"
            )
        
        self.decision_history.append(reasoning_entry)
        
        # Limit history length
        if len(self.decision_history) > 20:
            self.decision_history = self.decision_history[-20:]

# Keep original simple agents for compatibility with existing code
class SimpleSurvivorAgent(Agent):
    """Simple survivor agent"""
    
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
        self.found = False
        self.rescued_by = None
        self.signal_strength = random.randint(1, 10)
    
    def step(self):
        pass

class SimpleChargingStationAgent(Agent):
    """Simple charging station agent"""
    
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
        self.capacity = 2
        self.charging_rate = 10
    
    def step(self):
        pass