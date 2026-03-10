"""
增强UI的主要方法实现
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
from simulation.enhanced_model import EnhancedDroneSwarmModel
from simulation.enhanced_drone_agent import EnhancedDroneAgent, SimpleSurvivorAgent, SimpleChargingStationAgent
from simulation.terrain_system import TerrainType, ObstacleType, WeatherCondition
from ui.enhanced_ui_components import get_terrain_color, get_obstacle_symbol, get_weather_symbol

class EnhancedUIMethodsMixin:
    """增强UI方法的混入类"""
    
    def create_model(self):
        """创建增强模拟模型"""
        self.model = EnhancedDroneSwarmModel(
            width=20, height=20,
            n_drones=3, n_survivors=5,
            n_charging_stations=2,
            terrain_seed=42
        )
        self.log_message("✅ 增强模拟系统初始化完成")
        self.log_message(f"🗺️ 复杂地形生成: 包含山脉、水域、森林等多种地形")
        self.log_message(f"🌦️ 动态天气系统: 支持晴天、雨天、大风、雾天、暴雨")
        self.log_message(f"🚧 障碍物系统: 建筑、树木、信号塔等影响导航")
    
    def regenerate_terrain(self):
        """重新生成地形"""
        if messagebox.askyesno("重新生成地形", "这将重置所有智能体并生成新地形，确定继续吗？"):
            seed = self.terrain_seed_var.get()
            self.model = EnhancedDroneSwarmModel(
                width=20, height=20,
                n_drones=3, n_survivors=5,
                n_charging_stations=2,
                terrain_seed=seed
            )
            self.log_message(f"🗺️ 使用种子{seed}重新生成地形")
            self.update_reasoning_displays()
    
    def toggle_terrain_display(self):
        """切换地形显示"""
        self.show_terrain = self.terrain_var.get()
        self.log_message(f"🎨 地形显示: {'开启' if self.show_terrain else '关闭'}")
    
    def toggle_height_display(self):
        """切换高度显示"""
        self.show_height = self.height_var.get()
        self.log_message(f"📏 高度显示: {'开启' if self.show_height else '关闭'}")
    
    def toggle_weather_display(self):
        """切换天气显示"""
        self.show_weather = self.weather_var.get()
        self.log_message(f"🌤️ 天气显示: {'开启' if self.show_weather else '关闭'}")
    
    def on_canvas_click(self, event):
        """处理画布点击事件"""
        x = int(event.x // self.cell_size)
        y = int(event.y // self.cell_size)
        
        if 0 <= x < 20 and 0 <= y < 20:
            self.x_var.set(x)
            self.y_var.set(y)
            self.selected_pos = (x, y)
            
            # 显示详细地形信息
            self.show_terrain_info(x, y)
    
    def on_canvas_hover(self, event):
        """处理鼠标悬停事件"""
        x = int(event.x // self.cell_size)
        y = int(event.y // self.cell_size)
        
        if 0 <= x < 20 and 0 <= y < 20 and self.model:
            terrain_info = self.model.get_terrain_info(x, y)
            if terrain_info:
                info_text = (f"({x},{y}) {terrain_info['terrain_type']} "
                           f"海拔{terrain_info['height']:.0f}m "
                           f"{terrain_info['weather']}")
                if terrain_info['obstacle']:
                    info_text += f" {terrain_info['obstacle']}"
                
                self.terrain_info_label.config(text=f"地形信息: {info_text}")
    
    def show_terrain_info(self, x, y):
        """显示详细地形信息"""
        if not self.model:
            return
        
        terrain_info = self.model.get_terrain_info(x, y)
        if terrain_info:
            info_msg = f"""位置 ({x}, {y}) 详细信息:
            
🗺️ 地形类型: {terrain_info['terrain_type']}
📏 海拔高度: {terrain_info['height']:.1f} 米
🌤️ 天气条件: {terrain_info['weather']}
🚧 障碍物: {terrain_info['obstacle'] or '无'}
⚡ 移动成本: {terrain_info['movement_cost']:.2f}
🔍 扫描效率: {terrain_info['scan_efficiency']:.2f}
📡 通信质量: {terrain_info['communication_quality']:.2f}
👁️ 可见度: {terrain_info['visibility']:.2f}
💨 风速: {terrain_info['wind_speed']:.1f} m/s"""
            
            messagebox.showinfo("地形详情", info_msg)
    
    def add_drone(self):
        """添加无人机"""
        if not self.model:
            return
        
        x, y = self.x_var.get(), self.y_var.get()
        battery = self.battery_var.get()
        
        drone, message = self.model.add_drone_manually(x, y, battery)
        
        if drone:
            self.log_message(f"🚁 {message}")
            messagebox.showinfo("添加成功", f"无人机{drone.unique_id}已添加\n{message}")
            self.update_reasoning_displays()
        else:
            self.log_message(f"❌ 添加失败: {message}")
            messagebox.showwarning("添加失败", message)
    
    def add_survivor(self):
        """添加幸存者"""
        if not self.model:
            return
        
        x, y = self.x_var.get(), self.y_var.get()
        
        survivor, message = self.model.add_survivor_manually(x, y)
        
        if survivor:
            self.log_message(f"🆘 {message}")
            messagebox.showinfo("添加成功", f"幸存者{survivor.unique_id}已添加\n{message}")
        else:
            self.log_message(f"❌ 添加失败: {message}")
            messagebox.showwarning("添加失败", message)
    
    def step_simulation(self):
        """执行一步模拟"""
        if self.model:
            self.model.step()
            self.log_message(f"▶️ 执行第{self.model.step_count}步模拟")
            self.update_reasoning_displays()
    
    def toggle_auto_run(self):
        """切换自动运行"""
        self.auto_run = self.auto_var.get()
        if self.auto_run:
            self.log_message("🔄 启动自动运行模式")
            self.auto_run_thread()
        else:
            self.log_message("⏸️ 停止自动运行模式")
    
    def auto_run_thread(self):
        """自动运行线程"""
        def run():
            while self.auto_run and self.model:
                self.model.step()
                self.update_reasoning_displays()
                time.sleep(2)  # 2秒间隔，便于观察AI推理
        
        import threading
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def reset_simulation(self):
        """重置模拟"""
        if messagebox.askyesno("确认重置", "确定要重置模拟吗？这将清除所有当前数据。"):
            self.auto_var.set(False)
            self.auto_run = False
            self.create_model()
            self.update_reasoning_displays()
            self.log_message("🔄 模拟已重置")
    
    def draw_grid(self):
        """绘制增强网格"""
        self.canvas.delete("all")
        
        if not self.model:
            return
        
        # 绘制地形背景
        for y in range(20):
            for x in range(20):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = (x + 1) * self.cell_size
                y2 = (y + 1) * self.cell_size
                
                terrain_cell = self.model.terrain[y][x]
                
                # 获取地形颜色
                if self.show_terrain:
                    color = get_terrain_color(
                        terrain_cell.terrain_type,
                        terrain_cell.height if self.show_height else 0,
                        terrain_cell.weather if self.show_weather else None,
                        terrain_cell.obstacle
                    )
                else:
                    color = "#F0F0F0"  # 默认浅灰色
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="lightgray")
                
                # 显示高度信息
                if self.show_height and terrain_cell.height > 100:
                    height_text = f"{int(terrain_cell.height)}"
                    self.canvas.create_text((x1+x2)/2, y1+8, text=height_text, 
                                          font=('Arial', 6), fill="black")
                
                # 显示障碍物
                if terrain_cell.obstacle:
                    obstacle_symbol = get_obstacle_symbol(terrain_cell.obstacle)
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2-5, text=obstacle_symbol, 
                                          font=('Arial', 12))
                
                # 显示天气
                if self.show_weather and terrain_cell.weather != WeatherCondition.CLEAR:
                    weather_symbol = get_weather_symbol(terrain_cell.weather)
                    self.canvas.create_text(x2-8, y1+8, text=weather_symbol, 
                                          font=('Arial', 10))
        
        # 绘制智能体
        for agent in self.model.custom_agents:
            if agent.pos:
                self.draw_agent(agent)
        
        # 高亮选中位置
        x, y = self.x_var.get(), self.y_var.get()
        x1 = x * self.cell_size
        y1 = y * self.cell_size
        x2 = (x + 1) * self.cell_size
        y2 = (y + 1) * self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=3, fill="", stipple="gray25")
    
    def draw_agent(self, agent):
        """绘制智能体"""
        x, y = agent.pos
        x1 = x * self.cell_size + 3
        y1 = y * self.cell_size + 3
        x2 = (x + 1) * self.cell_size - 3
        y2 = (y + 1) * self.cell_size - 3
        
        if isinstance(agent, EnhancedDroneAgent):
            # 增强无人机可视化
            if agent.battery > 60:
                color = "green"
            elif agent.battery > 30:
                color = "orange"
            else:
                color = "red"
            
            # 状态边框
            outline_colors = {
                "idle": "black",
                "scanning": "blue",
                "rescue_mission": "purple",
                "charging": "cyan",
                "emergency_return": "red",
                "weather_hold": "gray",
                "area_scan": "lightblue"
            }
            outline = outline_colors.get(agent.status, "black")
            
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline=outline, width=2)
            
            # 显示无人机ID
            drone_id = agent.unique_id.split('_')[-1]
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=drone_id, 
                                  fill="white", font=('Arial', 8, 'bold'))
            
            # 显示路径规划
            if hasattr(agent, 'planned_path') and agent.planned_path:
                self.draw_planned_path(agent.planned_path, agent.current_path_index)
        
        elif isinstance(agent, SimpleSurvivorAgent):
            color = "gray" if agent.found else "red"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            text = "✓" if agent.found else "S"
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=text, 
                                  fill="white", font=('Arial', 8, 'bold'))
        
        elif isinstance(agent, SimpleChargingStationAgent):
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="cyan", outline="black", width=2)
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="⚡", font=('Arial', 12))
    
    def draw_planned_path(self, path, current_index):
        """绘制规划路径"""
        if len(path) < 2:
            return
        
        for i in range(current_index, len(path) - 1):
            y1, x1 = path[i]
            y2, x2 = path[i + 1]
            
            # 转换为画布坐标
            canvas_x1 = x1 * self.cell_size + self.cell_size // 2
            canvas_y1 = y1 * self.cell_size + self.cell_size // 2
            canvas_x2 = x2 * self.cell_size + self.cell_size // 2
            canvas_y2 = y2 * self.cell_size + self.cell_size // 2
            
            # 绘制路径线
            color = "yellow" if i == current_index else "orange"
            self.canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                                  fill=color, width=2, dash=(3, 3))
    
    def update_reasoning_displays(self):
        """更新AI推理显示"""
        if not self.model:
            return
        
        drones = [a for a in self.model.custom_agents if isinstance(a, EnhancedDroneAgent)]
        
        # 清除旧的标签页
        for tab_id in self.reasoning_notebook.tabs():
            self.reasoning_notebook.forget(tab_id)
        
        self.reasoning_displays = {}
        
        # 为每个无人机创建推理显示
        for drone in drones:
            frame = ttk.Frame(self.reasoning_notebook)
            self.reasoning_notebook.add(frame, text=f"🚁 {drone.unique_id}")
            
            # 创建滚动文本区域
            text_widget = tk.Text(frame, height=15, width=60, font=('Courier', 8), wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.reasoning_displays[drone.unique_id] = text_widget
            
            # 显示推理历史
            self.update_drone_reasoning_display(drone)
    
    def update_drone_reasoning_display(self, drone):
        """更新单个无人机的推理显示"""
        if drone.unique_id not in self.reasoning_displays:
            return
        
        text_widget = self.reasoning_displays[drone.unique_id]
        text_widget.delete(1.0, tk.END)
        
        # 显示当前状态
        current_terrain = drone.get_current_terrain()
        terrain_info = "未知地形"
        if current_terrain:
            terrain_info = f"{current_terrain.terrain_type.value}(海拔{current_terrain.height:.0f}m)"
            if current_terrain.weather != WeatherCondition.CLEAR:
                terrain_info += f",{current_terrain.weather.value}"
        
        status_text = f"""🚁 无人机 {drone.unique_id} 当前状态:
📍 位置: {drone.pos}
🔋 电量: {drone.battery}%
📊 状态: {drone.status}
🗺️ 地形: {terrain_info}
🎯 目标: {drone.target or '无'}
📏 总飞行距离: {drone.total_distance_traveled:.1f}
🆘 成功救援: {drone.successful_rescues}
❌ 失败尝试: {drone.failed_attempts}

🧠 AI推理历史:
{'='*50}
"""
        
        text_widget.insert(tk.END, status_text)
        
        # 显示推理历史
        for i, decision in enumerate(drone.decision_history[-5:]):  # 显示最近5次决策
            reasoning_text = f"""
第 {len(drone.decision_history) - 4 + i} 次决策 [{decision.get('timestamp', 'N/A')}]:
💭 AI思考: {decision['thought']}
🎯 决策: {decision['decision']}
⚡ 行动: {decision['action']}
👁️ 观察: {decision['observation']}
🗺️ 地形环境: {decision['terrain_info']}

🔍 详细推理步骤:"""
            
            text_widget.insert(tk.END, reasoning_text)
            
            for j, step in enumerate(decision.get('reasoning_steps', [])):
                text_widget.insert(tk.END, f"\n   {j+1}. {step}")
            
            text_widget.insert(tk.END, f"\n{'-'*50}\n")
        
        # 滚动到底部
        text_widget.see(tk.END)