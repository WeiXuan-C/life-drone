"""
增强的无人机群模型
集成地形系统、复杂环境和高级AI决策
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
    """增强的无人机群模型，支持复杂地形和高级AI"""
    
    def __init__(self, width=20, height=20, n_drones=3, n_survivors=5, n_charging_stations=2, 
                 terrain_seed=None, weather_enabled=True, obstacles_enabled=True):
        super().__init__()
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, True)
        self.custom_agents = []
        self.running = True
        self.step_count = 0
        
        # 地形系统
        self.terrain = TerrainGenerator.generate_realistic_terrain(
            width, height, seed=terrain_seed
        )
        self.weather_enabled = weather_enabled
        self.obstacles_enabled = obstacles_enabled
        
        # 日志系统
        self.mission_log = []
        self.reasoning_log = []
        self.terrain_analysis_log = []
        
        # 性能统计
        self.total_rescues = 0
        self.total_failed_attempts = 0
        self.total_distance_traveled = 0.0
        self.weather_delays = 0
        self.terrain_obstacles_encountered = 0
        
        # 创建智能体
        self._create_charging_stations(n_charging_stations)
        self._create_drones(n_drones)
        self._create_survivors(n_survivors)
        
        # 数据收集器
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
        
        # 记录初始地形分析
        self._log_terrain_analysis()
    
    def _create_charging_stations(self, n_stations):
        """创建充电站"""
        for i in range(n_stations):
            station = SimpleChargingStationAgent(f"station_{i}", self)
            self.custom_agents.append(station)
            
            # 在平坦地形放置充电站
            placed = False
            attempts = 0
            while not placed and attempts < 50:
                x = random.randrange(self.width)
                y = random.randrange(self.height)
                
                terrain_cell = self.terrain[y][x]
                # 选择适合的地形
                if (terrain_cell.terrain_type in [TerrainType.FLAT, TerrainType.URBAN] and
                    terrain_cell.obstacle is None):
                    
                    self.grid.place_agent(station, (x, y))
                    self.log_event(f"充电站{station.unique_id}部署在{terrain_cell.terrain_type.value}地形({x}, {y})")
                    placed = True
                
                attempts += 1
            
            if not placed:
                # 如果找不到合适位置，强制放置
                x, y = (1, 1) if i == 0 else (self.width - 2, self.height - 2)
                self.grid.place_agent(station, (x, y))
                self.log_event(f"充电站{station.unique_id}强制部署在({x}, {y})")
    
    def _create_drones(self, n_drones):
        """创建无人机"""
        for i in range(n_drones):
            drone = EnhancedDroneAgent(f"drone_{i}", self)
            self.custom_agents.append(drone)
            
            # 在充电站附近部署无人机
            charging_stations = [a for a in self.custom_agents if isinstance(a, SimpleChargingStationAgent)]
            if charging_stations:
                station = charging_stations[0]  # 使用第一个充电站
                station_x, station_y = station.pos
                
                # 在充电站周围3x3区域寻找合适位置
                placed = False
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        x = max(0, min(self.width - 1, station_x + dx))
                        y = max(0, min(self.height - 1, station_y + dy))
                        
                        terrain_cell = self.terrain[y][x]
                        if terrain_cell.get_movement_cost() != float('inf'):
                            self.grid.place_agent(drone, (x, y))
                            terrain_info = f"{terrain_cell.terrain_type.value}"
                            if terrain_cell.weather != WeatherCondition.CLEAR:
                                terrain_info += f",{terrain_cell.weather.value}"
                            self.log_event(f"无人机{drone.unique_id}部署在{terrain_info}({x}, {y})")
                            placed = True
                            break
                    if placed:
                        break
                
                if not placed:
                    # 回退到充电站位置
                    self.grid.place_agent(drone, station.pos)
                    self.log_event(f"无人机{drone.unique_id}部署在充电站位置{station.pos}")
    
    def _create_survivors(self, n_survivors):
        """创建幸存者"""
        for i in range(n_survivors):
            survivor = SimpleSurvivorAgent(f"survivor_{i}", self)
            self.custom_agents.append(survivor)
            
            # 随机放置幸存者，但避免不可达位置
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                x = random.randrange(self.width)
                y = random.randrange(self.height)
                
                terrain_cell = self.terrain[y][x]
                # 避免放在不可通行的地形
                if (terrain_cell.get_movement_cost() != float('inf') and
                    terrain_cell.obstacle != ObstacleType.BUILDING):
                    
                    # 检查是否已有充电站
                    cell_contents = self.grid.get_cell_list_contents([(x, y)])
                    if not any(isinstance(agent, SimpleChargingStationAgent) for agent in cell_contents):
                        self.grid.place_agent(survivor, (x, y))
                        terrain_info = f"{terrain_cell.terrain_type.value}"
                        if terrain_cell.obstacle:
                            terrain_info += f",{terrain_cell.obstacle.value}附近"
                        self.log_event(f"幸存者信号{survivor.unique_id}检测到在{terrain_info}({x}, {y})")
                        placed = True
                
                attempts += 1
            
            if not placed:
                # 强制放置在安全位置
                x = random.randrange(self.width)
                y = random.randrange(self.height)
                self.grid.place_agent(survivor, (x, y))
                self.log_event(f"幸存者信号{survivor.unique_id}强制放置在({x}, {y})")
    
    def add_drone_manually(self, x, y, battery=100):
        """用户手动添加无人机"""
        # 检查位置是否合适
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None, "位置超出边界"
        
        terrain_cell = self.terrain[y][x]
        if terrain_cell.get_movement_cost() == float('inf'):
            return None, f"无法在{terrain_cell.terrain_type.value}地形部署无人机"
        
        if terrain_cell.obstacle == ObstacleType.BUILDING:
            return None, "建筑物阻挡，无法部署"
        
        # 创建无人机
        drone_count = len([a for a in self.custom_agents if isinstance(a, EnhancedDroneAgent)])
        drone_id = f"user_drone_{drone_count}"
        new_drone = EnhancedDroneAgent(drone_id, self)
        new_drone.battery = battery
        
        self.custom_agents.append(new_drone)
        self.grid.place_agent(new_drone, (x, y))
        
        # 记录详细信息
        terrain_info = f"{terrain_cell.terrain_type.value}(高度{terrain_cell.height:.0f}m)"
        if terrain_cell.weather != WeatherCondition.CLEAR:
            terrain_info += f",{terrain_cell.weather.value}"
        if terrain_cell.obstacle:
            terrain_info += f",{terrain_cell.obstacle.value}附近"
        
        action = f"用户在{terrain_info}({x},{y})添加无人机{drone_id}，电量{battery}%"
        self.log_event(action)
        
        return new_drone, f"成功部署在{terrain_info}"
    
    def add_survivor_manually(self, x, y):
        """用户手动添加幸存者"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None, "位置超出边界"
        
        terrain_cell = self.terrain[y][x]
        
        # 创建幸存者
        survivor_count = len([a for a in self.custom_agents if isinstance(a, SimpleSurvivorAgent)])
        survivor_id = f"user_survivor_{survivor_count}"
        new_survivor = SimpleSurvivorAgent(survivor_id, self)
        
        self.custom_agents.append(new_survivor)
        self.grid.place_agent(new_survivor, (x, y))
        
        # 记录详细信息
        terrain_info = f"{terrain_cell.terrain_type.value}"
        if terrain_cell.weather != WeatherCondition.CLEAR:
            terrain_info += f",{terrain_cell.weather.value}天气"
        
        action = f"用户在{terrain_info}({x},{y})添加幸存者信号{survivor_id}"
        self.log_event(action)
        
        return new_survivor, f"信号已在{terrain_info}激活"
    
    def get_terrain_info(self, x, y):
        """获取指定位置的地形信息"""
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
        """获取增强的AI分析"""
        drones = [a for a in self.custom_agents if isinstance(a, EnhancedDroneAgent)]
        survivors = [a for a in self.custom_agents if isinstance(a, SimpleSurvivorAgent)]
        
        analysis = {
            "总无人机数": len(drones),
            "活跃无人机": len([d for d in drones if d.status not in ['charging', 'crashed']]),
            "总幸存者": len(survivors),
            "已救援": len([s for s in survivors if s.found]),
            "平均电量": sum([d.battery for d in drones]) / len(drones) if drones else 0,
            "状态分布": {},
            "地形挑战": self.terrain_obstacles_encountered,
            "天气延误": self.weather_delays,
            "总飞行距离": sum([d.total_distance_traveled for d in drones]),
            "救援成功率": self._calculate_rescue_success_rate(),
            "AI决策": [],
            "地形分析": self._get_current_terrain_analysis()
        }
        
        # 统计无人机状态分布
        for drone in drones:
            status = drone.status
            analysis["状态分布"][status] = analysis["状态分布"].get(status, 0) + 1
        
        # 获取最近的AI决策
        for drone in drones:
            if drone.decision_history:
                latest_decision = drone.decision_history[-1]
                analysis["AI决策"].append({
                    "无人机": drone.unique_id,
                    "思考": latest_decision["thought"],
                    "决策": latest_decision["decision"],
                    "地形": latest_decision["terrain_info"]
                })
        
        return analysis
    
    def _get_current_terrain_analysis(self):
        """获取当前地形分析"""
        terrain_stats = {
            "地形分布": {},
            "障碍物数量": 0,
            "天气条件": {},
            "平均高度": 0.0
        }
        
        total_height = 0.0
        cell_count = 0
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.terrain[y][x]
                cell_count += 1
                
                # 地形分布
                terrain_type = cell.terrain_type.value
                terrain_stats["地形分布"][terrain_type] = terrain_stats["地形分布"].get(terrain_type, 0) + 1
                
                # 障碍物统计
                if cell.obstacle:
                    terrain_stats["障碍物数量"] += 1
                
                # 天气条件
                weather = cell.weather.value
                terrain_stats["天气条件"][weather] = terrain_stats["天气条件"].get(weather, 0) + 1
                
                # 高度统计
                total_height += cell.height
        
        if cell_count > 0:
            terrain_stats["平均高度"] = total_height / cell_count
        
        return terrain_stats
    
    def step(self):
        """执行一步模拟"""
        self.step_count += 1
        self.datacollector.collect(self)
        
        # 更新天气条件（每10步）
        if self.step_count % 10 == 0 and self.weather_enabled:
            self._update_weather_conditions()
        
        # 执行所有智能体的步骤
        for agent in self.custom_agents:
            if hasattr(agent, 'step'):
                agent.step()
        
        # 统计性能指标
        self._update_performance_stats()
        
        # 记录重要事件
        if self.step_count % 20 == 0:
            self._log_periodic_status()
    
    def _update_weather_conditions(self):
        """更新天气条件"""
        # 随机改变部分区域的天气
        weather_change_probability = 0.1
        
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < weather_change_probability:
                    cell = self.terrain[y][x]
                    old_weather = cell.weather
                    
                    # 天气转换逻辑
                    if cell.weather == WeatherCondition.CLEAR:
                        new_weather = random.choice([WeatherCondition.WIND, WeatherCondition.RAIN])
                    elif cell.weather == WeatherCondition.STORM:
                        new_weather = random.choice([WeatherCondition.RAIN, WeatherCondition.WIND])
                    else:
                        new_weather = random.choice([WeatherCondition.CLEAR, WeatherCondition.FOG])
                    
                    cell.weather = new_weather
                    
                    if old_weather != new_weather:
                        self.log_event(f"天气变化: ({x},{y}) {old_weather.value} → {new_weather.value}")
    
    def _update_performance_stats(self):
        """更新性能统计"""
        drones = [a for a in self.custom_agents if isinstance(a, EnhancedDroneAgent)]
        
        # 统计救援情况
        self.total_rescues = sum([d.successful_rescues for d in drones])
        self.total_failed_attempts = sum([d.failed_attempts for d in drones])
        
        # 统计天气延误
        weather_affected_drones = len([d for d in drones if d.status == 'weather_hold'])
        if weather_affected_drones > 0:
            self.weather_delays += 1
    
    def _log_periodic_status(self):
        """记录周期性状态"""
        active_drones = self._count_active_drones()
        rescued_survivors = self._count_rescued_survivors()
        avg_battery = self._calculate_average_battery()
        
        status_msg = (f"步骤{self.step_count}: {active_drones}架无人机活跃, "
                     f"{rescued_survivors}名幸存者获救, 平均电量{avg_battery:.1f}%")
        
        if self.weather_delays > 0:
            status_msg += f", {self.weather_delays}次天气延误"
        
        if self.terrain_obstacles_encountered > 0:
            status_msg += f", {self.terrain_obstacles_encountered}次地形障碍"
        
        self.log_event(status_msg)
    
    def _log_terrain_analysis(self):
        """记录地形分析"""
        analysis = self._get_current_terrain_analysis()
        
        terrain_summary = []
        for terrain_type, count in analysis["地形分布"].items():
            percentage = (count / (self.width * self.height)) * 100
            terrain_summary.append(f"{terrain_type}({percentage:.1f}%)")
        
        log_msg = (f"地形分析: {', '.join(terrain_summary)}, "
                  f"障碍物{analysis['障碍物数量']}个, "
                  f"平均海拔{analysis['平均高度']:.0f}m")
        
        self.log_event(log_msg)
        self.terrain_analysis_log.append(analysis)
    
    # 数据收集器方法
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
        """记录事件日志"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.mission_log.append(log_entry)
        
        # 写入文件
        os.makedirs("logs", exist_ok=True)
        with open("logs/mission.log", "a", encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def log_reasoning(self, drone_id, thought, decision, action, observation):
        """记录AI推理过程"""
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
        
        # 限制日志长度
        if len(self.reasoning_log) > 100:
            self.reasoning_log = self.reasoning_log[-100:]