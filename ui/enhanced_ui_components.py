"""
增强UI的组件方法
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
from simulation.terrain_system import TerrainType, ObstacleType, WeatherCondition

def create_legend(parent_frame):
    """创建地形图例"""
    legend_frame = ttk.LabelFrame(parent_frame, text="🔤 地形图例", padding=5)
    legend_frame.pack(fill=tk.X, pady=5)
    
    # 地形颜色
    terrain_colors = {
        "平地": "#90EE90",      # 浅绿
        "丘陵": "#DEB887",      # 浅棕
        "山脉": "#8B4513",      # 深棕
        "水域": "#4169E1",      # 蓝色
        "森林": "#228B22",      # 深绿
        "沙漠": "#F4A460",      # 沙色
        "沼泽": "#556B2F",      # 橄榄绿
        "城市": "#696969",      # 灰色
        "悬崖": "#2F4F4F",      # 深灰
        "山谷": "#9ACD32"       # 黄绿
    }
    
    legend_text = "地形: "
    for terrain, color in list(terrain_colors.items())[:5]:
        legend_text += f"■{terrain} "
    legend_text += "\n障碍: 🏢建筑 🌳树木 📡信号塔 🚗车辆 | 天气: ☀晴 🌧雨 💨风 🌫雾 ⛈暴雨"
    
    ttk.Label(legend_frame, text=legend_text, font=('Arial', 11)).pack()

def create_control_panel(parent_frame, ui_instance):
    """创建控制面板"""
    control_frame = ttk.LabelFrame(parent_frame, text="🎮 增强控制面板", padding=10)
    control_frame.pack(fill=tk.X, pady=(0, 10))
    
    # 地形生成控制
    terrain_frame = ttk.Frame(control_frame)
    terrain_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(terrain_frame, text="地形种子:").pack(side=tk.LEFT)
    ui_instance.terrain_seed_var = tk.IntVar(value=42)
    ttk.Entry(terrain_frame, textvariable=ui_instance.terrain_seed_var, width=10).pack(side=tk.LEFT, padx=(5, 10))
    
    ttk.Button(terrain_frame, text="🗺️ 重新生成地形", 
              command=ui_instance.regenerate_terrain).pack(side=tk.LEFT, padx=5)
    
    # 位置选择
    pos_frame = ttk.Frame(control_frame)
    pos_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(pos_frame, text="选择位置:").pack(side=tk.LEFT)
    ui_instance.x_var = tk.IntVar(value=10)
    ui_instance.y_var = tk.IntVar(value=10)
    
    ttk.Label(pos_frame, text="X:").pack(side=tk.LEFT, padx=(10, 0))
    ttk.Spinbox(pos_frame, from_=0, to=19, width=5, textvariable=ui_instance.x_var).pack(side=tk.LEFT, padx=(0, 10))
    
    ttk.Label(pos_frame, text="Y:").pack(side=tk.LEFT)
    ttk.Spinbox(pos_frame, from_=0, to=19, width=5, textvariable=ui_instance.y_var).pack(side=tk.LEFT)
    
    # 无人机参数
    drone_frame = ttk.Frame(control_frame)
    drone_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(drone_frame, text="无人机电量:").pack(side=tk.LEFT)
    ui_instance.battery_var = tk.IntVar(value=100)
    battery_scale = ttk.Scale(drone_frame, from_=20, to=100, orient=tk.HORIZONTAL, 
                             variable=ui_instance.battery_var, length=120)
    battery_scale.pack(side=tk.LEFT, padx=(10, 5))
    
    ui_instance.battery_label = ttk.Label(drone_frame, text="100%")
    ui_instance.battery_label.pack(side=tk.LEFT)
    battery_scale.configure(command=lambda v: ui_instance.battery_label.config(text=f"{int(float(v))}%"))
    
    # 添加按钮
    button_frame = ttk.Frame(control_frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="🚁 添加无人机", 
              command=ui_instance.add_drone).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(button_frame, text="🆘 添加幸存者", 
              command=ui_instance.add_survivor).pack(side=tk.LEFT, padx=5)
    
    # 模拟控制
    sim_frame = ttk.Frame(control_frame)
    sim_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(sim_frame, text="▶️ 执行一步", 
              command=ui_instance.step_simulation).pack(side=tk.LEFT, padx=(0, 5))
    
    ui_instance.auto_var = tk.BooleanVar()
    ttk.Checkbutton(sim_frame, text="自动运行", 
                   variable=ui_instance.auto_var, 
                   command=ui_instance.toggle_auto_run).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(sim_frame, text="🔄 重置", 
              command=ui_instance.reset_simulation).pack(side=tk.LEFT, padx=5)

def create_enhanced_analysis_panel(parent_frame, ui_instance):
    """创建增强分析面板"""
    analysis_frame = ttk.LabelFrame(parent_frame, text="🧠 增强AI分析", padding=10)
    analysis_frame.pack(fill=tk.X, pady=(0, 10))
    
    # 关键指标
    metrics_frame = ttk.Frame(analysis_frame)
    metrics_frame.pack(fill=tk.X)
    
    ui_instance.metrics_labels = {}
    metrics = ["活跃无人机", "救援进度", "平均电量", "地形挑战", "天气延误", "救援成功率"]
    
    for i, metric in enumerate(metrics):
        frame = ttk.Frame(metrics_frame)
        frame.grid(row=i//3, column=i%3, padx=5, pady=2, sticky="w")
        
        ttk.Label(frame, text=f"{metric}:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        ui_instance.metrics_labels[metric] = ttk.Label(frame, text="0", font=('Arial', 11))
        ui_instance.metrics_labels[metric].pack(side=tk.LEFT, padx=(5, 0))

def create_ai_reasoning_panel(parent_frame, ui_instance):
    """创建AI推理面板"""
    reasoning_frame = ttk.LabelFrame(parent_frame, text="🤔 AI多步推理过程", padding=10)
    reasoning_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    # 创建笔记本控件用于显示不同无人机的推理
    ui_instance.reasoning_notebook = ttk.Notebook(reasoning_frame)
    ui_instance.reasoning_notebook.pack(fill=tk.BOTH, expand=True)
    
    # 初始化推理显示区域
    ui_instance.reasoning_displays = {}

def create_terrain_analysis_panel(parent_frame, ui_instance):
    """创建地形分析面板"""
    terrain_frame = ttk.LabelFrame(parent_frame, text="🗺️ 地形环境分析", padding=10)
    terrain_frame.pack(fill=tk.X, pady=(0, 10))
    
    # 地形统计
    ui_instance.terrain_stats_text = tk.Text(terrain_frame, height=4, width=50, font=('Arial', 11))
    ui_instance.terrain_stats_text.pack(fill=tk.X)

def get_terrain_color(terrain_type, height=0, weather=None, obstacle=None):
    """获取地形颜色"""
    base_colors = {
        TerrainType.FLAT: "#90EE90",      # 浅绿
        TerrainType.HILL: "#DEB887",      # 浅棕
        TerrainType.MOUNTAIN: "#8B4513",  # 深棕
        TerrainType.WATER: "#4169E1",     # 蓝色
        TerrainType.FOREST: "#228B22",    # 深绿
        TerrainType.DESERT: "#F4A460",    # 沙色
        TerrainType.SWAMP: "#556B2F",     # 橄榄绿
        TerrainType.URBAN: "#696969",     # 灰色
        TerrainType.CLIFF: "#2F4F4F",     # 深灰
        TerrainType.VALLEY: "#9ACD32"     # 黄绿
    }
    
    color = base_colors.get(terrain_type, "#FFFFFF")
    
    # 根据高度调整颜色深度
    if height > 1500:
        # 高海拔，颜色更深
        color = darken_color(color, 0.3)
    elif height > 800:
        color = darken_color(color, 0.15)
    
    # 天气影响
    if weather == WeatherCondition.STORM:
        color = darken_color(color, 0.4)
    elif weather == WeatherCondition.FOG:
        color = lighten_color(color, 0.3)
    elif weather == WeatherCondition.RAIN:
        color = darken_color(color, 0.2)
    
    return color

def darken_color(color, factor):
    """使颜色变深"""
    if color.startswith('#'):
        color = color[1:]
    
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    
    return f"#{r:02x}{g:02x}{b:02x}"

def lighten_color(color, factor):
    """使颜色变浅"""
    if color.startswith('#'):
        color = color[1:]
    
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    
    return f"#{r:02x}{g:02x}{b:02x}"

def get_obstacle_symbol(obstacle_type):
    """获取障碍物符号"""
    symbols = {
        ObstacleType.BUILDING: "🏢",
        ObstacleType.TREE: "🌳",
        ObstacleType.TOWER: "📡",
        ObstacleType.DEBRIS: "🗿",
        ObstacleType.VEHICLE: "🚗",
        ObstacleType.BRIDGE: "🌉",
        ObstacleType.TUNNEL: "🕳️"
    }
    return symbols.get(obstacle_type, "")

def get_weather_symbol(weather):
    """获取天气符号"""
    symbols = {
        WeatherCondition.CLEAR: "☀",
        WeatherCondition.RAIN: "🌧",
        WeatherCondition.WIND: "💨",
        WeatherCondition.FOG: "🌫",
        WeatherCondition.STORM: "⛈"
    }
    return symbols.get(weather, "")