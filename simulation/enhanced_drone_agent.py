"""
增强的无人机智能体
支持复杂地形导航、路径规划和高级AI决策
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
    """增强的无人机智能体，具备复杂地形导航能力"""
    
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
        
        # 基础属性
        self.battery = 100
        self.max_battery = 100
        self.status = "idle"
        self.target = None
        self.planned_path = []
        self.current_path_index = 0
        
        # 增强属性
        self.flight_altitude = 50  # 飞行高度（米）
        self.max_altitude = 200
        self.scan_radius = 2
        self.communication_range = 5
        
        # AI决策相关
        self.decision_history = []
        self.reasoning_steps = []
        self.risk_tolerance = 0.7  # 风险容忍度 (0-1)
        self.energy_efficiency_priority = 0.8  # 能效优先级
        self.mission_priority = 0.9  # 任务优先级
        
        # 性能统计
        self.total_distance_traveled = 0.0
        self.successful_rescues = 0
        self.failed_attempts = 0
        self.terrain_analysis_cache = {}
        
        # 传感器和设备状态
        self.gps_accuracy = 1.0
        self.camera_quality = 1.0
        self.communication_quality = 1.0
        
    def step(self):
        """执行一步AI决策和行动"""
        if self.battery <= 0:
            self.status = "crashed"
            self.log_reasoning("电量耗尽", "无人机坠毁", "emergency_landing", "系统关闭")
            return
        
        # 获取当前位置的地形信息
        current_terrain = self.get_current_terrain()
        
        # 执行多步AI推理
        self.perform_ai_reasoning(current_terrain)
        
        # 执行决策
        self.execute_decision()
        
        # 更新状态
        self.update_status(current_terrain)
    
    def perform_ai_reasoning(self, current_terrain: TerrainCell):
        """执行多步AI推理过程"""
        self.reasoning_steps = []
        
        # 第一步：环境感知和分析
        env_analysis = self.analyze_environment(current_terrain)
        self.reasoning_steps.append(f"环境分析: {env_analysis}")
        
        # 第二步：威胁评估
        threat_assessment = self.assess_threats(current_terrain)
        self.reasoning_steps.append(f"威胁评估: {threat_assessment}")
        
        # 第三步：资源状态评估
        resource_status = self.evaluate_resources()
        self.reasoning_steps.append(f"资源状态: {resource_status}")
        
        # 第四步：任务优先级分析
        mission_analysis = self.analyze_mission_priorities()
        self.reasoning_steps.append(f"任务分析: {mission_analysis}")
        
        # 第五步：路径规划和风险评估
        path_analysis = self.plan_optimal_path()
        self.reasoning_steps.append(f"路径规划: {path_analysis}")
        
        # 第六步：最终决策
        final_decision = self.make_final_decision()
        self.reasoning_steps.append(f"最终决策: {final_decision}")
        
        # 记录完整的推理过程
        self.log_reasoning(
            thought=f"多步推理完成，共{len(self.reasoning_steps)}个步骤",
            decision=final_decision,
            action=self.status,
            observation="推理过程已记录"
        )
    
    def analyze_environment(self, current_terrain: TerrainCell) -> str:
        """分析当前环境"""
        analysis_parts = []
        
        # 地形分析
        terrain_info = f"地形:{current_terrain.terrain_type.value}"
        if current_terrain.height > 1000:
            terrain_info += f",高海拔({current_terrain.height:.0f}m)"
        analysis_parts.append(terrain_info)
        
        # 天气分析
        weather_info = f"天气:{current_terrain.weather.value}"
        if current_terrain.weather != WeatherCondition.CLEAR:
            weather_info += f",可见度{current_terrain.visibility:.1f}"
        analysis_parts.append(weather_info)
        
        # 障碍物分析
        if current_terrain.obstacle:
            analysis_parts.append(f"障碍物:{current_terrain.obstacle.value}")
        
        # 通信质量
        comm_quality = current_terrain.get_communication_quality()
        if comm_quality < 0.5:
            analysis_parts.append(f"通信受限({comm_quality:.1f})")
        
        return ", ".join(analysis_parts)
    
    def assess_threats(self, current_terrain: TerrainCell) -> str:
        """评估威胁和风险"""
        threats = []
        risk_level = 0.0
        
        # 天气威胁
        if current_terrain.weather == WeatherCondition.STORM:
            threats.append("暴风雨威胁")
            risk_level += 0.8
        elif current_terrain.weather == WeatherCondition.WIND:
            threats.append("强风影响")
            risk_level += 0.4
        elif current_terrain.weather == WeatherCondition.FOG:
            threats.append("能见度极低")
            risk_level += 0.6
        
        # 地形威胁
        if current_terrain.terrain_type in [TerrainType.MOUNTAIN, TerrainType.CLIFF]:
            threats.append("复杂地形")
            risk_level += 0.5
        
        # 电量威胁
        if self.battery < 30:
            threats.append("电量不足")
            risk_level += 0.7
        elif self.battery < 50:
            threats.append("电量偏低")
            risk_level += 0.3
        
        # 障碍物威胁
        if current_terrain.obstacle == ObstacleType.BUILDING:
            threats.append("建筑物阻挡")
            risk_level += 0.6
        
        risk_description = "低风险"
        if risk_level > 0.7:
            risk_description = "高风险"
        elif risk_level > 0.4:
            risk_description = "中等风险"
        
        if threats:
            return f"{risk_description}: {', '.join(threats)}"
        else:
            return "环境安全"
    
    def evaluate_resources(self) -> str:
        """评估资源状态"""
        resources = []
        
        # 电量状态
        if self.battery > 80:
            resources.append("电量充足")
        elif self.battery > 50:
            resources.append("电量良好")
        elif self.battery > 30:
            resources.append("电量偏低")
        else:
            resources.append("电量危险")
        
        # 设备状态
        if self.camera_quality < 0.7:
            resources.append("摄像头受损")
        if self.gps_accuracy < 0.8:
            resources.append("GPS信号弱")
        if self.communication_quality < 0.6:
            resources.append("通信受限")
        
        # 飞行能力
        current_terrain = self.get_current_terrain()
        if current_terrain and current_terrain.height > self.max_altitude:
            resources.append("高度受限")
        
        return ", ".join(resources) if resources else "所有系统正常"
    
    def analyze_mission_priorities(self) -> str:
        """分析任务优先级"""
        priorities = []
        
        # 紧急情况优先级
        if self.battery <= 20:
            priorities.append("紧急充电(优先级:最高)")
            return ", ".join(priorities)
        
        # 寻找幸存者
        survivors = self.find_nearby_survivors()
        if survivors:
            closest_survivor = min(survivors, key=lambda s: self.calculate_terrain_distance(s.pos))
            distance = self.calculate_terrain_distance(closest_survivor.pos)
            priorities.append(f"救援幸存者@{closest_survivor.pos}(距离:{distance:.1f})")
        
        # 区域扫描
        if not survivors:
            priorities.append("区域扫描搜索")
        
        # 充电站维护
        if self.battery < 60:
            charging_stations = self.find_charging_stations()
            if charging_stations:
                closest_station = min(charging_stations, key=lambda s: self.calculate_terrain_distance(s.pos))
                distance = self.calculate_terrain_distance(closest_station.pos)
                priorities.append(f"前往充电站@{closest_station.pos}(距离:{distance:.1f})")
        
        return ", ".join(priorities) if priorities else "无紧急任务"
    
    def plan_optimal_path(self) -> str:
        """规划最优路径"""
        if not self.target:
            return "无目标，无需路径规划"
        
        # 使用地形系统计算最优路径
        terrain = self.model.terrain
        start = self.pos
        end = self.target
        
        # 计算多条可能路径
        direct_distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        terrain_distance = PathfindingSystem.calculate_real_distance(terrain, start, end)
        
        # 路径复杂度分析
        if terrain_distance == float('inf'):
            return f"目标不可达，需要重新选择目标"
        
        complexity_ratio = terrain_distance / direct_distance if direct_distance > 0 else 1.0
        
        if complexity_ratio > 3.0:
            return f"路径极其复杂(复杂度:{complexity_ratio:.1f}),建议绕行"
        elif complexity_ratio > 2.0:
            return f"路径复杂(复杂度:{complexity_ratio:.1f}),需谨慎导航"
        elif complexity_ratio > 1.5:
            return f"路径中等难度(复杂度:{complexity_ratio:.1f})"
        else:
            return f"路径相对简单(复杂度:{complexity_ratio:.1f})"
    
    def make_final_decision(self) -> str:
        """做出最终决策"""
        current_terrain = self.get_current_terrain()
        
        # 紧急情况处理
        if self.battery <= 15:
            self.status = "emergency_return"
            self.target = self.find_nearest_charging_station()
            return "电量极低，紧急返回充电站"
        
        # 恶劣天气处理
        if current_terrain and current_terrain.weather == WeatherCondition.STORM:
            if self.battery > 50:
                self.status = "weather_hold"
                return "暴风雨天气，原地等待"
            else:
                self.status = "emergency_return"
                self.target = self.find_nearest_charging_station()
                return "暴风雨+低电量，紧急返回"
        
        # 正常任务决策
        if self.status == "charging":
            if self.battery >= 80:
                self.status = "idle"
                return "充电完成，准备执行任务"
            else:
                return "继续充电中"
        
        # 寻找救援目标
        survivors = self.find_nearby_survivors()
        if survivors:
            closest_survivor = min(survivors, key=lambda s: self.calculate_terrain_distance(s.pos))
            distance = self.calculate_terrain_distance(closest_survivor.pos)
            
            # 评估是否有足够电量完成救援
            estimated_cost = distance * 2 + 20  # 往返+救援操作
            if self.battery > estimated_cost:
                self.target = closest_survivor.pos
                self.status = "rescue_mission"
                return f"执行救援任务，目标距离{distance:.1f}"
            else:
                self.status = "charging"
                self.target = self.find_nearest_charging_station()
                return "电量不足以完成救援，先充电"
        
        # 区域扫描
        self.status = "area_scan"
        return "执行区域扫描任务"
    
    def execute_decision(self):
        """执行决策"""
        if self.status == "charging":
            self.handle_charging()
        elif self.status in ["rescue_mission", "emergency_return"]:
            self.handle_movement()
        elif self.status == "area_scan":
            self.handle_area_scan()
        elif self.status == "weather_hold":
            self.handle_weather_hold()
    
    def handle_movement(self):
        """处理移动"""
        if not self.target:
            return
        
        # 如果没有规划路径或路径已完成，重新规划
        if not self.planned_path or self.current_path_index >= len(self.planned_path):
            terrain = self.model.terrain
            self.planned_path = PathfindingSystem.a_star_pathfinding(terrain, self.pos, self.target)
            self.current_path_index = 0
        
        # 沿着规划路径移动
        if self.planned_path and self.current_path_index < len(self.planned_path):
            next_pos = self.planned_path[self.current_path_index]
            
            # 检查下一个位置的地形
            if self.can_move_to(next_pos):
                old_pos = self.pos
                self.model.grid.move_agent(self, next_pos)
                
                # 计算移动成本
                terrain_cell = self.get_terrain_at(next_pos)
                move_cost = terrain_cell.get_movement_cost() if terrain_cell else 2.0
                self.battery -= move_cost
                
                # 更新统计
                distance = math.sqrt((next_pos[0] - old_pos[0])**2 + (next_pos[1] - old_pos[1])**2)
                self.total_distance_traveled += distance
                
                self.current_path_index += 1
                
                # 检查是否到达目标
                if next_pos == self.target:
                    self.handle_target_reached()
            else:
                # 路径被阻挡，重新规划
                self.planned_path = []
                self.current_path_index = 0
    
    def handle_charging(self):
        """处理充电"""
        # 检查是否在充电站
        charging_stations = [agent for agent in self.model.grid.get_cell_list_contents([self.pos])
                           if hasattr(agent, 'unique_id') and 'station' in str(agent.unique_id)]
        
        if charging_stations:
            charge_rate = 10
            # 地形可能影响充电效率
            current_terrain = self.get_current_terrain()
            if current_terrain and current_terrain.weather == WeatherCondition.STORM:
                charge_rate = 5  # 恶劣天气影响充电
            
            self.battery = min(self.max_battery, self.battery + charge_rate)
        else:
            # 不在充电站，需要移动到充电站
            self.target = self.find_nearest_charging_station()
            if self.target:
                self.handle_movement()
    
    def handle_area_scan(self):
        """处理区域扫描"""
        current_terrain = self.get_current_terrain()
        scan_efficiency = current_terrain.get_scan_efficiency() if current_terrain else 0.5
        
        # 扫描周围区域寻找幸存者
        scan_cost = 1.0 / scan_efficiency  # 效率越低，成本越高
        self.battery -= scan_cost
        
        # 在扫描范围内寻找幸存者
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
            # 发现幸存者，切换到救援模式
            closest_survivor = min(found_survivors, key=lambda s: self.calculate_terrain_distance(s.pos))
            self.target = closest_survivor.pos
            self.status = "rescue_mission"
        else:
            # 随机移动继续搜索
            self.random_move()
    
    def handle_weather_hold(self):
        """处理恶劣天气等待"""
        # 在恶劣天气中等待，消耗少量电量维持系统
        self.battery -= 0.5
        
        # 检查天气是否好转
        current_terrain = self.get_current_terrain()
        if current_terrain and current_terrain.weather != WeatherCondition.STORM:
            self.status = "idle"
    
    def handle_target_reached(self):
        """处理到达目标"""
        if self.status == "rescue_mission":
            # 尝试救援幸存者
            survivors_here = [agent for agent in self.model.grid.get_cell_list_contents([self.pos])
                            if hasattr(agent, 'found') and not agent.found]
            
            for survivor in survivors_here:
                current_terrain = self.get_current_terrain()
                rescue_efficiency = current_terrain.get_scan_efficiency() if current_terrain else 0.8
                
                if random.random() < rescue_efficiency:
                    survivor.found = True
                    survivor.rescued_by = self.unique_id
                    self.successful_rescues += 1
                    self.model.log_event(f"无人机{self.unique_id}成功救援幸存者{survivor.unique_id}")
                else:
                    self.failed_attempts += 1
                    self.model.log_event(f"无人机{self.unique_id}救援失败，环境条件不佳")
        
        # 清除目标和路径
        self.target = None
        self.planned_path = []
        self.current_path_index = 0
        self.status = "idle"
    
    def update_status(self, current_terrain: TerrainCell):
        """更新状态"""
        # 更新设备状态基于环境条件
        if current_terrain:
            # 天气影响设备
            if current_terrain.weather == WeatherCondition.STORM:
                self.camera_quality *= 0.95
                self.gps_accuracy *= 0.98
            elif current_terrain.weather == WeatherCondition.RAIN:
                self.camera_quality *= 0.99
            
            # 通信质量
            self.communication_quality = current_terrain.get_communication_quality()
            
            # 地形影响
            if current_terrain.terrain_type == TerrainType.MOUNTAIN:
                self.gps_accuracy *= 0.99
    
    # 辅助方法
    def get_current_terrain(self) -> Optional[TerrainCell]:
        """获取当前位置的地形"""
        if hasattr(self.model, 'terrain') and self.pos:
            y, x = self.pos
            if 0 <= y < len(self.model.terrain) and 0 <= x < len(self.model.terrain[0]):
                return self.model.terrain[y][x]
        return None
    
    def get_terrain_at(self, pos: Tuple[int, int]) -> Optional[TerrainCell]:
        """获取指定位置的地形"""
        if hasattr(self.model, 'terrain'):
            y, x = pos
            if 0 <= y < len(self.model.terrain) and 0 <= x < len(self.model.terrain[0]):
                return self.model.terrain[y][x]
        return None
    
    def can_move_to(self, pos: Tuple[int, int]) -> bool:
        """检查是否可以移动到指定位置"""
        terrain_cell = self.get_terrain_at(pos)
        if not terrain_cell:
            return False
        
        move_cost = terrain_cell.get_movement_cost()
        return move_cost != float('inf') and self.battery > move_cost
    
    def calculate_terrain_distance(self, target_pos: Tuple[int, int]) -> float:
        """计算考虑地形的距离"""
        if hasattr(self.model, 'terrain'):
            return PathfindingSystem.calculate_real_distance(self.model.terrain, self.pos, target_pos)
        else:
            # 回退到欧几里得距离
            return math.sqrt((target_pos[0] - self.pos[0])**2 + (target_pos[1] - self.pos[1])**2)
    
    def find_nearby_survivors(self):
        """寻找附近的幸存者"""
        survivors = [agent for agent in self.model.custom_agents 
                    if hasattr(agent, 'found') and not agent.found]
        
        # 按地形距离排序
        survivors.sort(key=lambda s: self.calculate_terrain_distance(s.pos))
        return survivors[:5]  # 返回最近的5个
    
    def find_charging_stations(self):
        """寻找充电站"""
        stations = [agent for agent in self.model.custom_agents 
                   if hasattr(agent, 'unique_id') and 'station' in str(agent.unique_id)]
        return stations
    
    def find_nearest_charging_station(self):
        """寻找最近的充电站"""
        stations = self.find_charging_stations()
        if stations:
            nearest = min(stations, key=lambda s: self.calculate_terrain_distance(s.pos))
            return nearest.pos
        return None
    
    def random_move(self):
        """随机移动"""
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
            
            # 计算移动成本
            terrain_cell = self.get_terrain_at(new_pos)
            move_cost = terrain_cell.get_movement_cost() if terrain_cell else 2.0
            self.battery -= move_cost
    
    def log_reasoning(self, thought: str, decision: str, action: str, observation: str):
        """记录推理过程"""
        reasoning_entry = {
            "drone_id": self.unique_id,
            "thought": thought,
            "decision": decision,
            "action": action,
            "observation": observation,
            "reasoning_steps": self.reasoning_steps.copy(),
            "battery": self.battery,
            "position": self.pos,
            "terrain_info": self.analyze_environment(self.get_current_terrain()) if self.get_current_terrain() else "未知地形"
        }
        
        if hasattr(self.model, 'log_reasoning'):
            self.model.log_reasoning(
                self.unique_id, thought, decision, action, 
                f"{observation} | 地形: {reasoning_entry['terrain_info']}"
            )
        
        self.decision_history.append(reasoning_entry)
        
        # 限制历史记录长度
        if len(self.decision_history) > 20:
            self.decision_history = self.decision_history[-20:]

# 保持原有的简单智能体以兼容现有代码
class SimpleSurvivorAgent(Agent):
    """简单幸存者智能体"""
    
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
        self.found = False
        self.rescued_by = None
        self.signal_strength = random.randint(1, 10)
    
    def step(self):
        pass

class SimpleChargingStationAgent(Agent):
    """简单充电站智能体"""
    
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
        self.capacity = 2
        self.charging_rate = 10
    
    def step(self):
        pass