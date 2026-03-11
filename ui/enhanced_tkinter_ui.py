"""
增强的Tkinter交互式UI
支持地形可视化、复杂AI决策分析和详细环境信息
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import math
from simulation.enhanced_model import EnhancedDroneSwarmModel
from simulation.enhanced_drone_agent import EnhancedDroneAgent, SimpleSurvivorAgent, SimpleChargingStationAgent
from simulation.terrain_system import TerrainType, ObstacleType, WeatherCondition
from ui.enhanced_ui_components import (
    create_legend, create_control_panel, create_enhanced_analysis_panel,
    create_ai_reasoning_panel, create_terrain_analysis_panel
)
from ui.enhanced_ui_methods import EnhancedUIMethodsMixin

class EnhancedDroneUI(EnhancedUIMethodsMixin):
    """增强的无人机控制界面，支持地形和复杂AI分析"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚁 增强型自主无人机群指挥系统 - 复杂地形版")
        self.root.geometry("1800x1200")
        
        # 配置默认字体大小
        self.root.option_add('*Font', 'Arial 12')
        self.root.option_add('*Label.Font', 'Arial 12')
        self.root.option_add('*Button.Font', 'Arial 12')
        self.root.option_add('*Checkbutton.Font', 'Arial 12')
        
        # 配置ttk样式
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12))
        style.configure('TButton', font=('Arial', 12), padding=(10, 5))
        style.configure('TCheckbutton', font=('Arial', 12))
        style.configure('TLabelFrame.Label', font=('Arial', 14, 'bold'))
        style.configure('Heading', font=('Arial', 12, 'bold'))
        
        # 模型和状态
        self.model = None
        self.auto_run = False
        self.selected_pos = (10, 10)
        self.canvas_size = 800  # 增大画布
        self.cell_size = 40     # 增大网格单元
        self.show_terrain = True
        self.show_height = False
        self.show_weather = False
        
        # 创建UI
        self.create_widgets()
        self.create_model()
        
        # 启动更新循环
        self.update_display()
    
    def create_widgets(self):
        """创建UI组件"""
        
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：网格可视化
        left_frame = ttk.LabelFrame(main_frame, text="🗺️ 复杂地形灾区模拟", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 可视化选项
        viz_frame = ttk.Frame(left_frame)
        viz_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.terrain_var = tk.BooleanVar(value=True)
        self.height_var = tk.BooleanVar(value=False)
        self.weather_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(viz_frame, text="显示地形", variable=self.terrain_var,
                       command=self.toggle_terrain_display).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(viz_frame, text="显示高度", variable=self.height_var,
                       command=self.toggle_height_display).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(viz_frame, text="显示天气", variable=self.weather_var,
                       command=self.toggle_weather_display).pack(side=tk.LEFT)
        
        # 网格画布
        self.canvas = tk.Canvas(left_frame, width=self.canvas_size, height=self.canvas_size, 
                               bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_hover)
        
        # 地形信息显示
        self.terrain_info_label = ttk.Label(left_frame, text="地形信息: 点击网格查看详情", 
                                           font=('Arial', 12))
        self.terrain_info_label.pack(pady=5)
        
        # 图例
        create_legend(left_frame)
        
        # 右侧：控制和分析面板
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        # 创建各个面板
        create_control_panel(right_frame, self)
        create_enhanced_analysis_panel(right_frame, self)
        create_ai_reasoning_panel(right_frame, self)
        create_terrain_analysis_panel(right_frame, self)
        self.create_status_table(right_frame)
        self.create_log_panel(right_frame)
    
    def create_status_table(self, parent):
        """创建状态表格"""
        table_frame = ttk.LabelFrame(parent, text="🚁 无人机详细状态", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建表格
        columns = ("ID", "电量", "状态", "位置", "地形", "目标")
        self.status_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        
        # 设置列标题和宽度
        column_widths = {"ID": 100, "电量": 80, "状态": 100, "位置": 80, "地形": 120, "目标": 80}
        for col in columns:
            self.status_tree.heading(col, text=col)
            self.status_tree.column(col, width=column_widths.get(col, 100))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.status_tree.yview)
        self.status_tree.configure(yscrollcommand=scrollbar.set)
        
        self.status_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_log_panel(self, parent):
        """创建日志面板"""
        log_frame = ttk.LabelFrame(parent, text="📝 任务日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, width=50, 
                                                 font=('Courier', 11), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def update_analysis(self):
        """更新AI分析"""
        if not self.model:
            return
        
        analysis = self.model.get_ai_analysis()
        
        # 更新指标
        self.metrics_labels["活跃无人机"].config(text=f"{analysis['活跃无人机']}/{analysis['总无人机数']}")
        self.metrics_labels["救援进度"].config(text=f"{analysis['已救援']}/{analysis['总幸存者']}")
        self.metrics_labels["平均电量"].config(text=f"{analysis['平均电量']:.1f}%")
        self.metrics_labels["地形挑战"].config(text=str(analysis['地形挑战']))
        self.metrics_labels["天气延误"].config(text=str(analysis['天气延误']))
        self.metrics_labels["救援成功率"].config(text=f"{analysis['救援成功率']:.1f}%")
        
        # 更新地形分析
        terrain_analysis = analysis['地形分析']
        terrain_text = f"地形分布: "
        for terrain, count in terrain_analysis['地形分布'].items():
            percentage = (count / 400) * 100  # 20x20 = 400 cells
            terrain_text += f"{terrain}({percentage:.1f}%) "
        
        terrain_text += f"\n障碍物: {terrain_analysis['障碍物数量']}个"
        terrain_text += f"\n平均海拔: {terrain_analysis['平均高度']:.0f}m"
        
        weather_text = "天气分布: "
        for weather, count in terrain_analysis['天气条件'].items():
            percentage = (count / 400) * 100
            weather_text += f"{weather}({percentage:.1f}%) "
        
        terrain_text += f"\n{weather_text}"
        
        self.terrain_stats_text.delete(1.0, tk.END)
        self.terrain_stats_text.insert(1.0, terrain_text)
    
    def update_status_table(self):
        """更新状态表格"""
        if not self.model:
            return
        
        # 清空表格
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)
        
        # 添加无人机数据
        drones = [a for a in self.model.custom_agents if isinstance(a, EnhancedDroneAgent)]
        
        for drone in drones:
            battery_icon = "🟢" if drone.battery > 60 else "🟡" if drone.battery > 30 else "🔴"
            
            # 获取地形信息
            terrain_info = "未知"
            if drone.pos:
                terrain_cell = drone.get_current_terrain()
                if terrain_cell:
                    terrain_info = f"{terrain_cell.terrain_type.value}"
                    if terrain_cell.height > 500:
                        terrain_info += f"({terrain_cell.height:.0f}m)"
            
            position = f"({drone.pos[0]}, {drone.pos[1]})" if drone.pos else "未知"
            target = f"({drone.target[0]}, {drone.target[1]})" if drone.target else "无"
            
            self.status_tree.insert("", tk.END, values=(
                drone.unique_id,
                f"{battery_icon} {drone.battery}%",
                drone.status,
                position,
                terrain_info,
                target
            ))
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 限制日志长度
        lines = self.log_text.get(1.0, tk.END).split('\n')
        if len(lines) > 100:
            self.log_text.delete(1.0, f"{len(lines)-100}.0")
    
    def update_display(self):
        """更新显示"""
        self.draw_grid()
        self.update_analysis()
        self.update_status_table()
        
        # 定期更新
        self.root.after(1000, self.update_display)
    
    def run(self):
        """运行UI"""
        self.root.mainloop()

def main():
    """主函数"""
    print("🚁 启动增强型Tkinter交互式UI...")
    print("🗺️ 复杂地形特性:")
    print("   • 多种地形类型：平地、丘陵、山脉、水域、森林、沙漠等")
    print("   • 高度差异：海拔0-2000米，影响移动成本和通信")
    print("   • 动态天气：晴天、雨天、大风、雾天、暴雨")
    print("   • 障碍物系统：建筑、树木、信号塔、废墟等")
    print("🧠 AI增强特性:")
    print("   • 多步推理：环境感知→威胁评估→资源分析→任务规划→路径优化→决策执行")
    print("   • 复杂路径规划：A*算法考虑地形成本，非直线距离")
    print("   • 动态适应：实时响应天气变化和地形挑战")
    print("   • 详细推理记录：完整的AI思考过程可视化")
    
    app = EnhancedDroneUI()
    app.run()

if __name__ == "__main__":
    main()