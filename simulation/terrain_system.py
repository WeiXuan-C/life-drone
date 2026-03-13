"""
Terrain system module
Contains various terrain types, heights, obstacles, and movement cost calculations
"""

import random
import math
import numpy as np
from enum import Enum
from typing import Tuple, List, Dict, Optional

class TerrainType(Enum):
    """Terrain type enumeration"""
    FLAT = "Flat"           # Basic movement cost
    HILL = "Hill"           # Medium movement cost
    MOUNTAIN = "Mountain"   # High movement cost, may be impassable
    WATER = "Water"         # Drones can fly over, but risky
    FOREST = "Forest"       # Medium cost, affects scanning
    DESERT = "Desert"       # High power consumption
    SWAMP = "Swamp"         # High movement cost, affects communication
    URBAN = "Urban"         # Complex terrain with buildings
    CLIFF = "Cliff"         # Extremely high movement cost
    VALLEY = "Valley"       # Lowland, may have airflow effects

class ObstacleType(Enum):
    """Obstacle type"""
    BUILDING = "Building"   # Impassable
    TREE = "Tree"           # Affects flight altitude
    TOWER = "Tower"         # Affects communication, but may provide signal boost
    DEBRIS = "Debris"       # Post-disaster obstacles
    VEHICLE = "Vehicle"     # Potentially mobile obstacles
    BRIDGE = "Bridge"       # Special passage
    TUNNEL = "Tunnel"       # Underground passage

class WeatherCondition(Enum):
    """Weather conditions"""
    CLEAR = "Clear"         # Normal conditions
    RAIN = "Rain"           # Affects electronics and visibility
    WIND = "Wind"           # Affects flight stability and power consumption
    FOG = "Fog"             # Severely affects scanning and navigation
    STORM = "Storm"         # Dangerous conditions, may require emergency landing

class TerrainCell:
    """Terrain cell"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.terrain_type = TerrainType.FLAT
        self.height = 0.0  # Altitude (meters)
        self.obstacle = None  # Obstacle type
        self.weather = WeatherCondition.CLEAR
        self.visibility = 1.0  # Visibility (0-1)
        self.signal_strength = 1.0  # Signal strength (0-1)
        self.wind_speed = 0.0  # Wind speed (m/s)
        self.wind_direction = 0.0  # Wind direction (degrees)
        
    def get_movement_cost(self, drone_type: str = "standard") -> float:
        """Calculate movement cost"""
        base_cost = {
            TerrainType.FLAT: 1.0,
            TerrainType.HILL: 1.5,
            TerrainType.MOUNTAIN: 3.0,
            TerrainType.WATER: 1.2,  # Drones can fly over but risky
            TerrainType.FOREST: 1.8,
            TerrainType.DESERT: 2.0,
            TerrainType.SWAMP: 2.5,
            TerrainType.URBAN: 1.6,
            TerrainType.CLIFF: 4.0,
            TerrainType.VALLEY: 1.3
        }
        
        cost = base_cost.get(self.terrain_type, 1.0)
        
        # Height impact
        height_factor = 1.0 + (self.height / 1000.0) * 0.5  # 50% increase per 1000m
        cost *= height_factor
        
        # Weather impact
        weather_multiplier = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.RAIN: 1.3,
            WeatherCondition.WIND: 1.2,
            WeatherCondition.FOG: 1.8,
            WeatherCondition.STORM: 3.0
        }
        cost *= weather_multiplier.get(self.weather, 1.0)
        
        # Obstacle impact
        if self.obstacle:
            obstacle_cost = {
                ObstacleType.BUILDING: float('inf'),  # Impassable
                ObstacleType.TREE: 1.4,
                ObstacleType.TOWER: 1.2,
                ObstacleType.DEBRIS: 2.0,
                ObstacleType.VEHICLE: 1.5,
                ObstacleType.BRIDGE: 0.8,  # Bridges are actually easier to pass
                ObstacleType.TUNNEL: 0.9
            }
            obstacle_multiplier = obstacle_cost.get(self.obstacle, 1.0)
            if obstacle_multiplier == float('inf'):
                return float('inf')  # Impassable
            cost *= obstacle_multiplier
        
        return cost
    
    def get_scan_efficiency(self) -> float:
        """Get scan efficiency"""
        base_efficiency = 1.0
        
        # Terrain impact on scanning
        terrain_efficiency = {
            TerrainType.FLAT: 1.0,
            TerrainType.HILL: 0.9,
            TerrainType.MOUNTAIN: 0.6,
            TerrainType.WATER: 0.8,
            TerrainType.FOREST: 0.4,  # Forest severely affects scanning
            TerrainType.DESERT: 1.1,  # Desert has open visibility
            TerrainType.SWAMP: 0.7,
            TerrainType.URBAN: 0.5,   # Urban buildings block view
            TerrainType.CLIFF: 0.8,
            TerrainType.VALLEY: 0.9
        }
        
        efficiency = terrain_efficiency.get(self.terrain_type, 1.0)
        
        # Visibility impact
        efficiency *= self.visibility
        
        # Weather impact
        weather_efficiency = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.RAIN: 0.7,
            WeatherCondition.WIND: 0.9,
            WeatherCondition.FOG: 0.3,
            WeatherCondition.STORM: 0.2
        }
        efficiency *= weather_efficiency.get(self.weather, 1.0)
        
        return max(0.1, efficiency)  # Minimum 10% efficiency
    
    def get_communication_quality(self) -> float:
        """Get communication quality"""
        base_quality = self.signal_strength
        
        # Terrain impact on communication
        terrain_comm = {
            TerrainType.FLAT: 1.0,
            TerrainType.HILL: 0.9,
            TerrainType.MOUNTAIN: 0.4,  # Mountains severely affect signal
            TerrainType.WATER: 0.8,
            TerrainType.FOREST: 0.6,
            TerrainType.DESERT: 1.1,
            TerrainType.SWAMP: 0.5,
            TerrainType.URBAN: 0.7,     # Urban has signal interference
            TerrainType.CLIFF: 0.3,
            TerrainType.VALLEY: 0.6     # Valley has poor signal
        }
        
        quality = base_quality * terrain_comm.get(self.terrain_type, 1.0)
        
        # Obstacle impact
        if self.obstacle == ObstacleType.TOWER:
            quality *= 1.5  # Tower enhances communication
        elif self.obstacle == ObstacleType.BUILDING:
            quality *= 0.3  # Building blocks signal
        
        return max(0.1, min(1.0, quality))

class TerrainGenerator:
    """Terrain generator"""
    
    @staticmethod
    def generate_realistic_terrain(width: int, height: int, seed: Optional[int] = None) -> List[List[TerrainCell]]:
        """Generate realistic terrain"""
        if seed:
            random.seed(seed)
            np.random.seed(seed)
        
        terrain = [[TerrainCell(x, y) for x in range(width)] for y in range(height)]
        
        # Generate height map (simplified Perlin noise)
        TerrainGenerator._generate_height_map(terrain, width, height)
        
        # Assign terrain types based on height
        TerrainGenerator._assign_terrain_types(terrain, width, height)
        
        # Add obstacles
        TerrainGenerator._add_obstacles(terrain, width, height)
        
        # Set weather conditions
        TerrainGenerator._set_weather_conditions(terrain, width, height)
        
        # Calculate visibility and signal strength
        TerrainGenerator._calculate_environmental_factors(terrain, width, height)
        
        return terrain
    
    @staticmethod
    def _generate_height_map(terrain: List[List[TerrainCell]], width: int, height: int):
        """Generate height map"""
        # Create several height center points
        peaks = []
        num_peaks = random.randint(2, 5)
        
        for _ in range(num_peaks):
            peak_x = random.randint(0, width - 1)
            peak_y = random.randint(0, height - 1)
            peak_height = random.uniform(500, 2000)  # 500-2000 meters
            peaks.append((peak_x, peak_y, peak_height))
        
        # Calculate height for each point
        for y in range(height):
            for x in range(width):
                total_height = 0
                total_weight = 0
                
                for peak_x, peak_y, peak_height in peaks:
                    distance = math.sqrt((x - peak_x)**2 + (y - peak_y)**2)
                    # Use Gaussian distribution to calculate influence
                    weight = math.exp(-(distance**2) / (2 * (width/4)**2))
                    total_height += peak_height * weight
                    total_weight += weight
                
                if total_weight > 0:
                    terrain[y][x].height = total_height / total_weight
                else:
                    terrain[y][x].height = 0
                
                # Add some random noise
                terrain[y][x].height += random.uniform(-50, 50)
                terrain[y][x].height = max(0, terrain[y][x].height)
    
    @staticmethod
    def _assign_terrain_types(terrain: List[List[TerrainCell]], width: int, height: int):
        """Assign terrain types based on height"""
        # Calculate height statistics
        all_heights = [terrain[y][x].height for y in range(height) for x in range(width)]
        min_height = min(all_heights)
        max_height = max(all_heights)
        height_range = max_height - min_height
        
        for y in range(height):
            for x in range(width):
                cell = terrain[y][x]
                relative_height = (cell.height - min_height) / height_range if height_range > 0 else 0
                
                # Assign terrain based on relative height
                if relative_height < 0.1:
                    # Lowland
                    terrain_options = [TerrainType.WATER, TerrainType.SWAMP, TerrainType.VALLEY]
                    cell.terrain_type = random.choice(terrain_options)
                elif relative_height < 0.3:
                    # Flatland
                    terrain_options = [TerrainType.FLAT, TerrainType.FOREST, TerrainType.URBAN]
                    weights = [0.5, 0.3, 0.2]
                    cell.terrain_type = random.choices(terrain_options, weights=weights)[0]
                elif relative_height < 0.6:
                    # Hills
                    terrain_options = [TerrainType.HILL, TerrainType.FOREST, TerrainType.DESERT]
                    weights = [0.6, 0.3, 0.1]
                    cell.terrain_type = random.choices(terrain_options, weights=weights)[0]
                elif relative_height < 0.8:
                    # Mountains
                    terrain_options = [TerrainType.MOUNTAIN, TerrainType.CLIFF]
                    weights = [0.8, 0.2]
                    cell.terrain_type = random.choices(terrain_options, weights=weights)[0]
                else:
                    # High mountains
                    cell.terrain_type = TerrainType.MOUNTAIN
    
    @staticmethod
    def _add_obstacles(terrain: List[List[TerrainCell]], width: int, height: int):
        """Add obstacles"""
        obstacle_density = 0.15  # 15% of cells have obstacles
        num_obstacles = int(width * height * obstacle_density)
        
        for _ in range(num_obstacles):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            cell = terrain[y][x]
            
            # Select appropriate obstacles based on terrain type
            if cell.terrain_type == TerrainType.URBAN:
                obstacles = [ObstacleType.BUILDING, ObstacleType.TOWER, ObstacleType.VEHICLE]
                weights = [0.6, 0.1, 0.3]
            elif cell.terrain_type == TerrainType.FOREST:
                obstacles = [ObstacleType.TREE]
                weights = [1.0]
            elif cell.terrain_type in [TerrainType.MOUNTAIN, TerrainType.CLIFF]:
                obstacles = [ObstacleType.DEBRIS]
                weights = [1.0]
            elif cell.terrain_type == TerrainType.WATER:
                obstacles = [ObstacleType.BRIDGE]
                weights = [1.0]
            else:
                obstacles = [ObstacleType.DEBRIS, ObstacleType.TREE, ObstacleType.VEHICLE]
                weights = [0.5, 0.3, 0.2]
            
            if obstacles:
                cell.obstacle = random.choices(obstacles, weights=weights)[0]
    
    @staticmethod
    def _set_weather_conditions(terrain: List[List[TerrainCell]], width: int, height: int):
        """Set weather conditions"""
        # Create weather zones
        weather_zones = random.randint(1, 3)
        
        for _ in range(weather_zones):
            center_x = random.randint(0, width - 1)
            center_y = random.randint(0, height - 1)
            radius = random.randint(3, 8)
            weather = random.choice(list(WeatherCondition))
            
            for y in range(max(0, center_y - radius), min(height, center_y + radius + 1)):
                for x in range(max(0, center_x - radius), min(width, center_x + radius + 1)):
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance <= radius:
                        terrain[y][x].weather = weather
    
    @staticmethod
    def _calculate_environmental_factors(terrain: List[List[TerrainCell]], width: int, height: int):
        """Calculate environmental factors"""
        for y in range(height):
            for x in range(width):
                cell = terrain[y][x]
                
                # Calculate visibility
                base_visibility = 1.0
                if cell.weather == WeatherCondition.FOG:
                    base_visibility = 0.3
                elif cell.weather == WeatherCondition.RAIN:
                    base_visibility = 0.7
                elif cell.weather == WeatherCondition.STORM:
                    base_visibility = 0.2
                
                cell.visibility = base_visibility
                
                # Calculate signal strength
                base_signal = 0.8
                if cell.terrain_type in [TerrainType.MOUNTAIN, TerrainType.CLIFF]:
                    base_signal = 0.4
                elif cell.terrain_type == TerrainType.VALLEY:
                    base_signal = 0.6
                elif cell.terrain_type == TerrainType.URBAN:
                    base_signal = 0.9
                
                cell.signal_strength = base_signal
                
                # Set wind speed and direction
                if cell.weather == WeatherCondition.WIND:
                    cell.wind_speed = random.uniform(10, 25)
                elif cell.weather == WeatherCondition.STORM:
                    cell.wind_speed = random.uniform(25, 50)
                else:
                    cell.wind_speed = random.uniform(0, 10)
                
                cell.wind_direction = random.uniform(0, 360)

class PathfindingSystem:
    """Pathfinding system"""
    
    @staticmethod
    def calculate_real_distance(terrain: List[List[TerrainCell]], 
                              start: Tuple[int, int], 
                              end: Tuple[int, int]) -> float:
        """Calculate real distance cost considering terrain"""
        if start == end:
            return 0.0
        
        # Use A* algorithm to calculate optimal path
        path = PathfindingSystem.a_star_pathfinding(terrain, start, end)
        
        if not path:
            return float('inf')  # Unreachable
        
        total_cost = 0.0
        for i in range(len(path) - 1):
            current = path[i]
            next_pos = path[i + 1]
            
            # Get movement cost of current cell
            y, x = current
            if 0 <= y < len(terrain) and 0 <= x < len(terrain[0]):
                cell = terrain[y][x]
                move_cost = cell.get_movement_cost()
                
                # Calculate base distance (Euclidean distance)
                base_distance = math.sqrt((next_pos[0] - current[0])**2 + (next_pos[1] - current[1])**2)
                
                # Apply terrain cost
                total_cost += base_distance * move_cost
        
        return total_cost
    
    @staticmethod
    def a_star_pathfinding(terrain: List[List[TerrainCell]], 
                          start: Tuple[int, int], 
                          end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """A* pathfinding algorithm"""
        from heapq import heappush, heappop
        
        height = len(terrain)
        width = len(terrain[0]) if height > 0 else 0
        
        # Check if start and end are valid
        if (not (0 <= start[0] < height and 0 <= start[1] < width) or
            not (0 <= end[0] < height and 0 <= end[1] < width)):
            return []
        
        # Check if end is reachable
        end_cell = terrain[end[0]][end[1]]
        if end_cell.get_movement_cost() == float('inf'):
            return []
        
        # A* algorithm implementation
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: PathfindingSystem._heuristic(start, end)}
        
        while open_set:
            current = heappop(open_set)[1]
            
            if current == end:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            # Check neighbors
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dy == 0 and dx == 0:
                        continue
                    
                    neighbor = (current[0] + dy, current[1] + dx)
                    
                    # Check boundaries
                    if not (0 <= neighbor[0] < height and 0 <= neighbor[1] < width):
                        continue
                    
                    # Check if passable
                    neighbor_cell = terrain[neighbor[0]][neighbor[1]]
                    move_cost = neighbor_cell.get_movement_cost()
                    
                    if move_cost == float('inf'):
                        continue
                    
                    # Calculate movement cost
                    base_distance = math.sqrt(dy**2 + dx**2)
                    tentative_g_score = g_score[current] + base_distance * move_cost
                    
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + PathfindingSystem._heuristic(neighbor, end)
                        heappush(open_set, (f_score[neighbor], neighbor))
        
        return []  # No path found
    
    @staticmethod
    def _heuristic(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Heuristic function (Manhattan distance)"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

class TerrainAnalyzer:
    """Terrain analyzer"""
    
    @staticmethod
    def analyze_area(terrain: List[List[TerrainCell]], 
                    center: Tuple[int, int], 
                    radius: int) -> Dict:
        """Analyze terrain features of specified area"""
        height = len(terrain)
        width = len(terrain[0]) if height > 0 else 0
        
        analysis = {
            "terrain_distribution": {},
            "obstacle_count": 0,
            "average_height": 0.0,
            "weather_conditions": {},
            "movement_difficulty": 0.0,
            "scan_efficiency": 0.0,
            "communication_quality": 0.0
        }
        
        cells_analyzed = 0
        total_height = 0.0
        total_movement_cost = 0.0
        total_scan_efficiency = 0.0
        total_comm_quality = 0.0
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                y = center[0] + dy
                x = center[1] + dx
                
                if 0 <= y < height and 0 <= x < width:
                    cell = terrain[y][x]
                    cells_analyzed += 1
                    
                    # Terrain distribution
                    terrain_type = cell.terrain_type.value
                    analysis["terrain_distribution"][terrain_type] = \
                        analysis["terrain_distribution"].get(terrain_type, 0) + 1
                    
                    # Obstacle statistics
                    if cell.obstacle:
                        analysis["obstacle_count"] += 1
                    
                    # Height statistics
                    total_height += cell.height
                    
                    # Weather conditions
                    weather = cell.weather.value
                    analysis["weather_conditions"][weather] = \
                        analysis["weather_conditions"].get(weather, 0) + 1
                    
                    # Performance metrics
                    total_movement_cost += cell.get_movement_cost()
                    total_scan_efficiency += cell.get_scan_efficiency()
                    total_comm_quality += cell.get_communication_quality()
        
        if cells_analyzed > 0:
            analysis["average_height"] = total_height / cells_analyzed
            analysis["movement_difficulty"] = total_movement_cost / cells_analyzed
            analysis["scan_efficiency"] = total_scan_efficiency / cells_analyzed
            analysis["communication_quality"] = total_comm_quality / cells_analyzed
        
        return analysis