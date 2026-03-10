"""
地形系统模块
包含各种地形类型、高度、障碍物和移动成本计算
"""

import random
import math
import numpy as np
from enum import Enum
from typing import Tuple, List, Dict, Optional

class TerrainType(Enum):
    """地形类型枚举"""
    FLAT = "平地"           # 基础移动成本
    HILL = "丘陵"           # 中等移动成本
    MOUNTAIN = "山脉"       # 高移动成本，可能不可通行
    WATER = "水域"          # 无人机可飞越，但有风险
    FOREST = "森林"         # 中等成本，影响扫描
    DESERT = "沙漠"         # 高电量消耗
    SWAMP = "沼泽"          # 高移动成本，影响通信
    URBAN = "城市"          # 复杂地形，有建筑物
    CLIFF = "悬崖"          # 极高移动成本
    VALLEY = "山谷"         # 低地，可能有气流影响

class ObstacleType(Enum):
    """障碍物类型"""
    BUILDING = "建筑物"     # 不可通行
    TREE = "大树"           # 影响飞行高度
    TOWER = "信号塔"        # 影响通信，但可能提供信号增强
    DEBRIS = "废墟"         # 灾后障碍物
    VEHICLE = "车辆"        # 可能移动的障碍
    BRIDGE = "桥梁"         # 特殊通道
    TUNNEL = "隧道"         # 地下通道

class WeatherCondition(Enum):
    """天气条件"""
    CLEAR = "晴朗"          # 正常条件
    RAIN = "雨天"           # 影响电子设备和能见度
    WIND = "大风"           # 影响飞行稳定性和电量消耗
    FOG = "雾天"            # 严重影响扫描和导航
    STORM = "暴风雨"        # 危险条件，可能需要紧急降落

class TerrainCell:
    """地形单元格"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.terrain_type = TerrainType.FLAT
        self.height = 0.0  # 海拔高度（米）
        self.obstacle = None  # 障碍物类型
        self.weather = WeatherCondition.CLEAR
        self.visibility = 1.0  # 可见度 (0-1)
        self.signal_strength = 1.0  # 信号强度 (0-1)
        self.wind_speed = 0.0  # 风速 (m/s)
        self.wind_direction = 0.0  # 风向 (度)
        
    def get_movement_cost(self, drone_type: str = "standard") -> float:
        """计算移动成本"""
        base_cost = {
            TerrainType.FLAT: 1.0,
            TerrainType.HILL: 1.5,
            TerrainType.MOUNTAIN: 3.0,
            TerrainType.WATER: 1.2,  # 无人机可飞越但有风险
            TerrainType.FOREST: 1.8,
            TerrainType.DESERT: 2.0,
            TerrainType.SWAMP: 2.5,
            TerrainType.URBAN: 1.6,
            TerrainType.CLIFF: 4.0,
            TerrainType.VALLEY: 1.3
        }
        
        cost = base_cost.get(self.terrain_type, 1.0)
        
        # 高度影响
        height_factor = 1.0 + (self.height / 1000.0) * 0.5  # 每1000米增加50%成本
        cost *= height_factor
        
        # 天气影响
        weather_multiplier = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.RAIN: 1.3,
            WeatherCondition.WIND: 1.2,
            WeatherCondition.FOG: 1.8,
            WeatherCondition.STORM: 3.0
        }
        cost *= weather_multiplier.get(self.weather, 1.0)
        
        # 障碍物影响
        if self.obstacle:
            obstacle_cost = {
                ObstacleType.BUILDING: float('inf'),  # 不可通行
                ObstacleType.TREE: 1.4,
                ObstacleType.TOWER: 1.2,
                ObstacleType.DEBRIS: 2.0,
                ObstacleType.VEHICLE: 1.5,
                ObstacleType.BRIDGE: 0.8,  # 桥梁实际上更容易通行
                ObstacleType.TUNNEL: 0.9
            }
            obstacle_multiplier = obstacle_cost.get(self.obstacle, 1.0)
            if obstacle_multiplier == float('inf'):
                return float('inf')  # 不可通行
            cost *= obstacle_multiplier
        
        return cost
    
    def get_scan_efficiency(self) -> float:
        """获取扫描效率"""
        base_efficiency = 1.0
        
        # 地形影响扫描
        terrain_efficiency = {
            TerrainType.FLAT: 1.0,
            TerrainType.HILL: 0.9,
            TerrainType.MOUNTAIN: 0.6,
            TerrainType.WATER: 0.8,
            TerrainType.FOREST: 0.4,  # 森林严重影响扫描
            TerrainType.DESERT: 1.1,  # 沙漠视野开阔
            TerrainType.SWAMP: 0.7,
            TerrainType.URBAN: 0.5,   # 城市建筑物遮挡
            TerrainType.CLIFF: 0.8,
            TerrainType.VALLEY: 0.9
        }
        
        efficiency = terrain_efficiency.get(self.terrain_type, 1.0)
        
        # 可见度影响
        efficiency *= self.visibility
        
        # 天气影响
        weather_efficiency = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.RAIN: 0.7,
            WeatherCondition.WIND: 0.9,
            WeatherCondition.FOG: 0.3,
            WeatherCondition.STORM: 0.2
        }
        efficiency *= weather_efficiency.get(self.weather, 1.0)
        
        return max(0.1, efficiency)  # 最低10%效率
    
    def get_communication_quality(self) -> float:
        """获取通信质量"""
        base_quality = self.signal_strength
        
        # 地形影响通信
        terrain_comm = {
            TerrainType.FLAT: 1.0,
            TerrainType.HILL: 0.9,
            TerrainType.MOUNTAIN: 0.4,  # 山脉严重影响信号
            TerrainType.WATER: 0.8,
            TerrainType.FOREST: 0.6,
            TerrainType.DESERT: 1.1,
            TerrainType.SWAMP: 0.5,
            TerrainType.URBAN: 0.7,     # 城市有信号干扰
            TerrainType.CLIFF: 0.3,
            TerrainType.VALLEY: 0.6     # 山谷信号差
        }
        
        quality = base_quality * terrain_comm.get(self.terrain_type, 1.0)
        
        # 障碍物影响
        if self.obstacle == ObstacleType.TOWER:
            quality *= 1.5  # 信号塔增强通信
        elif self.obstacle == ObstacleType.BUILDING:
            quality *= 0.3  # 建筑物阻挡信号
        
        return max(0.1, min(1.0, quality))

class TerrainGenerator:
    """地形生成器"""
    
    @staticmethod
    def generate_realistic_terrain(width: int, height: int, seed: Optional[int] = None) -> List[List[TerrainCell]]:
        """生成真实的地形"""
        if seed:
            random.seed(seed)
            np.random.seed(seed)
        
        terrain = [[TerrainCell(x, y) for x in range(width)] for y in range(height)]
        
        # 生成高度图（使用柏林噪声的简化版本）
        TerrainGenerator._generate_height_map(terrain, width, height)
        
        # 根据高度分配地形类型
        TerrainGenerator._assign_terrain_types(terrain, width, height)
        
        # 添加障碍物
        TerrainGenerator._add_obstacles(terrain, width, height)
        
        # 设置天气条件
        TerrainGenerator._set_weather_conditions(terrain, width, height)
        
        # 计算可见度和信号强度
        TerrainGenerator._calculate_environmental_factors(terrain, width, height)
        
        return terrain
    
    @staticmethod
    def _generate_height_map(terrain: List[List[TerrainCell]], width: int, height: int):
        """生成高度图"""
        # 创建几个高度中心点
        peaks = []
        num_peaks = random.randint(2, 5)
        
        for _ in range(num_peaks):
            peak_x = random.randint(0, width - 1)
            peak_y = random.randint(0, height - 1)
            peak_height = random.uniform(500, 2000)  # 500-2000米
            peaks.append((peak_x, peak_y, peak_height))
        
        # 为每个点计算高度
        for y in range(height):
            for x in range(width):
                total_height = 0
                total_weight = 0
                
                for peak_x, peak_y, peak_height in peaks:
                    distance = math.sqrt((x - peak_x)**2 + (y - peak_y)**2)
                    # 使用高斯分布计算影响
                    weight = math.exp(-(distance**2) / (2 * (width/4)**2))
                    total_height += peak_height * weight
                    total_weight += weight
                
                if total_weight > 0:
                    terrain[y][x].height = total_height / total_weight
                else:
                    terrain[y][x].height = 0
                
                # 添加一些随机噪声
                terrain[y][x].height += random.uniform(-50, 50)
                terrain[y][x].height = max(0, terrain[y][x].height)
    
    @staticmethod
    def _assign_terrain_types(terrain: List[List[TerrainCell]], width: int, height: int):
        """根据高度分配地形类型"""
        # 计算高度统计
        all_heights = [terrain[y][x].height for y in range(height) for x in range(width)]
        min_height = min(all_heights)
        max_height = max(all_heights)
        height_range = max_height - min_height
        
        for y in range(height):
            for x in range(width):
                cell = terrain[y][x]
                relative_height = (cell.height - min_height) / height_range if height_range > 0 else 0
                
                # 根据相对高度分配地形
                if relative_height < 0.1:
                    # 低地
                    terrain_options = [TerrainType.WATER, TerrainType.SWAMP, TerrainType.VALLEY]
                    cell.terrain_type = random.choice(terrain_options)
                elif relative_height < 0.3:
                    # 平地
                    terrain_options = [TerrainType.FLAT, TerrainType.FOREST, TerrainType.URBAN]
                    weights = [0.5, 0.3, 0.2]
                    cell.terrain_type = random.choices(terrain_options, weights=weights)[0]
                elif relative_height < 0.6:
                    # 丘陵
                    terrain_options = [TerrainType.HILL, TerrainType.FOREST, TerrainType.DESERT]
                    weights = [0.6, 0.3, 0.1]
                    cell.terrain_type = random.choices(terrain_options, weights=weights)[0]
                elif relative_height < 0.8:
                    # 山地
                    terrain_options = [TerrainType.MOUNTAIN, TerrainType.CLIFF]
                    weights = [0.8, 0.2]
                    cell.terrain_type = random.choices(terrain_options, weights=weights)[0]
                else:
                    # 高山
                    cell.terrain_type = TerrainType.MOUNTAIN
    
    @staticmethod
    def _add_obstacles(terrain: List[List[TerrainCell]], width: int, height: int):
        """添加障碍物"""
        obstacle_density = 0.15  # 15%的格子有障碍物
        num_obstacles = int(width * height * obstacle_density)
        
        for _ in range(num_obstacles):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            cell = terrain[y][x]
            
            # 根据地形类型选择合适的障碍物
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
        """设置天气条件"""
        # 创建天气区域
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
        """计算环境因素"""
        for y in range(height):
            for x in range(width):
                cell = terrain[y][x]
                
                # 计算可见度
                base_visibility = 1.0
                if cell.weather == WeatherCondition.FOG:
                    base_visibility = 0.3
                elif cell.weather == WeatherCondition.RAIN:
                    base_visibility = 0.7
                elif cell.weather == WeatherCondition.STORM:
                    base_visibility = 0.2
                
                cell.visibility = base_visibility
                
                # 计算信号强度
                base_signal = 0.8
                if cell.terrain_type in [TerrainType.MOUNTAIN, TerrainType.CLIFF]:
                    base_signal = 0.4
                elif cell.terrain_type == TerrainType.VALLEY:
                    base_signal = 0.6
                elif cell.terrain_type == TerrainType.URBAN:
                    base_signal = 0.9
                
                cell.signal_strength = base_signal
                
                # 设置风速和风向
                if cell.weather == WeatherCondition.WIND:
                    cell.wind_speed = random.uniform(10, 25)
                elif cell.weather == WeatherCondition.STORM:
                    cell.wind_speed = random.uniform(25, 50)
                else:
                    cell.wind_speed = random.uniform(0, 10)
                
                cell.wind_direction = random.uniform(0, 360)

class PathfindingSystem:
    """路径规划系统"""
    
    @staticmethod
    def calculate_real_distance(terrain: List[List[TerrainCell]], 
                              start: Tuple[int, int], 
                              end: Tuple[int, int]) -> float:
        """计算考虑地形的真实距离成本"""
        if start == end:
            return 0.0
        
        # 使用A*算法计算最优路径
        path = PathfindingSystem.a_star_pathfinding(terrain, start, end)
        
        if not path:
            return float('inf')  # 无法到达
        
        total_cost = 0.0
        for i in range(len(path) - 1):
            current = path[i]
            next_pos = path[i + 1]
            
            # 获取当前格子的移动成本
            y, x = current
            if 0 <= y < len(terrain) and 0 <= x < len(terrain[0]):
                cell = terrain[y][x]
                move_cost = cell.get_movement_cost()
                
                # 计算基础距离（欧几里得距离）
                base_distance = math.sqrt((next_pos[0] - current[0])**2 + (next_pos[1] - current[1])**2)
                
                # 应用地形成本
                total_cost += base_distance * move_cost
        
        return total_cost
    
    @staticmethod
    def a_star_pathfinding(terrain: List[List[TerrainCell]], 
                          start: Tuple[int, int], 
                          end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """A*路径规划算法"""
        from heapq import heappush, heappop
        
        height = len(terrain)
        width = len(terrain[0]) if height > 0 else 0
        
        # 检查起点和终点是否有效
        if (not (0 <= start[0] < height and 0 <= start[1] < width) or
            not (0 <= end[0] < height and 0 <= end[1] < width)):
            return []
        
        # 检查终点是否可达
        end_cell = terrain[end[0]][end[1]]
        if end_cell.get_movement_cost() == float('inf'):
            return []
        
        # A*算法实现
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: PathfindingSystem._heuristic(start, end)}
        
        while open_set:
            current = heappop(open_set)[1]
            
            if current == end:
                # 重构路径
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            # 检查邻居
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dy == 0 and dx == 0:
                        continue
                    
                    neighbor = (current[0] + dy, current[1] + dx)
                    
                    # 检查边界
                    if not (0 <= neighbor[0] < height and 0 <= neighbor[1] < width):
                        continue
                    
                    # 检查是否可通行
                    neighbor_cell = terrain[neighbor[0]][neighbor[1]]
                    move_cost = neighbor_cell.get_movement_cost()
                    
                    if move_cost == float('inf'):
                        continue
                    
                    # 计算移动成本
                    base_distance = math.sqrt(dy**2 + dx**2)
                    tentative_g_score = g_score[current] + base_distance * move_cost
                    
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + PathfindingSystem._heuristic(neighbor, end)
                        heappush(open_set, (f_score[neighbor], neighbor))
        
        return []  # 无法找到路径
    
    @staticmethod
    def _heuristic(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """启发式函数（曼哈顿距离）"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

class TerrainAnalyzer:
    """地形分析器"""
    
    @staticmethod
    def analyze_area(terrain: List[List[TerrainCell]], 
                    center: Tuple[int, int], 
                    radius: int) -> Dict:
        """分析指定区域的地形特征"""
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
                    
                    # 地形分布
                    terrain_type = cell.terrain_type.value
                    analysis["terrain_distribution"][terrain_type] = \
                        analysis["terrain_distribution"].get(terrain_type, 0) + 1
                    
                    # 障碍物统计
                    if cell.obstacle:
                        analysis["obstacle_count"] += 1
                    
                    # 高度统计
                    total_height += cell.height
                    
                    # 天气条件
                    weather = cell.weather.value
                    analysis["weather_conditions"][weather] = \
                        analysis["weather_conditions"].get(weather, 0) + 1
                    
                    # 性能指标
                    total_movement_cost += cell.get_movement_cost()
                    total_scan_efficiency += cell.get_scan_efficiency()
                    total_comm_quality += cell.get_communication_quality()
        
        if cells_analyzed > 0:
            analysis["average_height"] = total_height / cells_analyzed
            analysis["movement_difficulty"] = total_movement_cost / cells_analyzed
            analysis["scan_efficiency"] = total_scan_efficiency / cells_analyzed
            analysis["communication_quality"] = total_comm_quality / cells_analyzed
        
        return analysis