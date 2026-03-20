"""
全新设计的无人机指挥系统UI
简洁现代的配色和布局，专注于Mesa和Tkinter的原生渲染
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import json
import random
from datetime import datetime

from simulation.enhanced_model import EnhancedDroneSwarmModel
from simulation.enhanced_drone_agent import EnhancedDroneAgent, SimpleSurvivorAgent, SimpleChargingStationAgent
from simulation.terrain_system import WeatherCondition, TerrainType, ObstacleType
from agent.rescue_agent import get_rescue_agent


# 简洁现代配色方案
COLORS = {
    'bg': '#F8F9FA',           # 浅灰背景
    'card': '#FFFFFF',         # 白色卡片
    'primary': '#2C3E50',      # 深蓝灰
    'accent': '#3498DB',       # 蓝色强调
    'text': '#2C3E50',         # 深色文字
    'text_light': '#7F8C8D',   # 浅色文字
    'border': '#E1E8ED',       # 边框
    'success': '#27AE60',      # 成功绿
    'warning': '#F39C12',      # 警告橙
    'danger': '#E74C3C',       # 危险红
}

# 地形颜色 - 更加鲜明易识别
TERRAIN_COLORS = {
    TerrainType.FLAT: '#90EE90',      # 浅绿色 - 平地
    TerrainType.FOREST: '#228B22',    # 深绿色 - 森林
    TerrainType.MOUNTAIN: '#8B7355',  # 棕色 - 山地
    TerrainType.WATER: '#4169E1',     # 蓝色 - 水域
    TerrainType.URBAN: '#A9A9A9',     # 灰色 - 城市
}


class RedesignedDroneUI:
    """全新设计的无人机UI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Drone Command System")
        self.root.geometry("1600x900")
        self.root.configure(bg=COLORS['bg'])
        
        # 初始化RescueAgent
        self.rescue_agent = get_rescue_agent()
        
        # 状态变量
        self.model = None
        self.auto_run = False
        self.canvas_size = 700
        self.cell_size = 35
        self.current_seed = None
        
        # AI通信日志
        self.ai_responses = []
        self.mcp_communications = []
        
        # 配置样式
        self._setup_styles()
        
        # 创建UI
        self._create_layout()
        
        # 初始化模型
        self.create_model()
        
        # 启动更新循环
        self.update_loop()
    
    def _setup_styles(self):
        """配置ttk样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 按钮样式
        style.configure('Action.TButton',
                       font=('Segoe UI', 10),
                       padding=(16, 8),
                       background=COLORS['accent'],
                       foreground='white')
        
        style.map('Action.TButton',
                 background=[('active', '#2980B9')])
        
        # 标签样式
        style.configure('Card.TLabel',
                       background=COLORS['card'],
                       foreground=COLORS['text'],
                       font=('Segoe UI', 9))
        
        style.configure('Title.TLabel',
                       background=COLORS['card'],
                       foreground=COLORS['primary'],
                       font=('Segoe UI', 11, 'bold'))
    
    def _create_layout(self):
        """创建主布局"""
        # 主容器
        main_container = tk.Frame(self.root, bg=COLORS['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 左侧：地图区域
        left_panel = self._create_map_panel(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 右侧：控制和信息区域
        right_panel = self._create_control_panel(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
    
    def _create_map_panel(self, parent):
        """创建地图面板"""
        panel = tk.Frame(parent, bg=COLORS['card'], relief='flat')
        
        # 标题栏
        header = tk.Frame(panel, bg=COLORS['card'], height=50)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        header.pack_propagate(False)
        
        tk.Label(header, text="Mission Area", 
                font=('Segoe UI', 14, 'bold'),
                bg=COLORS['card'], fg=COLORS['primary']).pack(side=tk.LEFT)
        
        # 添加随机地图按钮
        random_btn = tk.Button(header, text="🎲 Random Map", 
                              command=self.generate_random_map,
                              font=('Segoe UI', 9),
                              bg=COLORS['accent'], fg='white',
                              relief='flat', padx=12, pady=5,
                              cursor='hand2')
        random_btn.pack(side=tk.RIGHT)
        random_btn.bind('<Enter>', lambda e: random_btn.config(bg='#2980B9'))
        random_btn.bind('<Leave>', lambda e: random_btn.config(bg=COLORS['accent']))
        
        # 地图画布
        canvas_frame = tk.Frame(panel, bg=COLORS['card'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, 
                               width=self.canvas_size, 
                               height=self.canvas_size,
                               bg='#FAFAFA',
                               highlightthickness=1,
                               highlightbackground=COLORS['border'])
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_hover)
        
        # 地形信息显示
        self.terrain_info_label = tk.Label(panel, text="Hover over map to see terrain details",
                                          font=('Segoe UI', 9),
                                          bg=COLORS['card'], fg=COLORS['text_light'],
                                          anchor=tk.W)
        self.terrain_info_label.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        # 图例 - 更详细
        legend_frame = tk.Frame(panel, bg=COLORS['card'])
        legend_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        self._create_legend(legend_frame)
        
        return panel
    
    def _create_legend(self, parent):
        """创建图例"""
        # 地形图例
        terrain_label = tk.Label(parent, text="Terrain:", 
                                font=('Segoe UI', 9, 'bold'),
                                bg=COLORS['card'], fg=COLORS['text'])
        terrain_label.pack(side=tk.LEFT, padx=(0, 10))
        
        terrain_items = [
            (TERRAIN_COLORS[TerrainType.FLAT], "Flat"),
            (TERRAIN_COLORS[TerrainType.FOREST], "Forest"),
            (TERRAIN_COLORS[TerrainType.MOUNTAIN], "Mountain"),
            (TERRAIN_COLORS[TerrainType.WATER], "Water"),
            (TERRAIN_COLORS[TerrainType.URBAN], "Urban"),
        ]
        
        for color, label in terrain_items:
            item_frame = tk.Frame(parent, bg=COLORS['card'])
            item_frame.pack(side=tk.LEFT, padx=5)
            
            # 颜色方块
            color_box = tk.Canvas(item_frame, width=16, height=16, 
                                 bg=color, highlightthickness=1,
                                 highlightbackground=COLORS['border'])
            color_box.pack(side=tk.LEFT, padx=(0, 3))
            
            tk.Label(item_frame, text=label,
                    bg=COLORS['card'], fg=COLORS['text_light'],
                    font=('Segoe UI', 8)).pack(side=tk.LEFT)
        
        # 分隔符
        tk.Label(parent, text="|", bg=COLORS['card'], 
                fg=COLORS['border']).pack(side=tk.LEFT, padx=10)
        
        # Agent图例 - 更详细
        agent_label = tk.Label(parent, text="Agents:", 
                              font=('Segoe UI', 9, 'bold'),
                              bg=COLORS['card'], fg=COLORS['text'])
        agent_label.pack(side=tk.LEFT, padx=(0, 10))
        
        agent_items = [
            (COLORS['accent'], "D", "Drone"),
            (COLORS['danger'], "!", "Survivor"),
            (COLORS['success'], "✓", "Rescued"),
            (COLORS['warning'], "⚡", "Station"),
        ]
        
        for color, symbol, label in agent_items:
            item_frame = tk.Frame(parent, bg=COLORS['card'])
            item_frame.pack(side=tk.LEFT, padx=5)
            
            # 创建小图标
            icon_canvas = tk.Canvas(item_frame, width=18, height=18, 
                                   bg=COLORS['card'], highlightthickness=0)
            icon_canvas.pack(side=tk.LEFT, padx=(0, 3))
            
            if label == "Station":
                # 方形
                icon_canvas.create_rectangle(3, 3, 15, 15, fill=color, outline='gray')
            else:
                # 圆形
                icon_canvas.create_oval(3, 3, 15, 15, fill=color, outline='gray')
            
            icon_canvas.create_text(9, 9, text=symbol, fill='white', 
                                   font=('Arial', 8, 'bold'))
            
            tk.Label(item_frame, text=label,
                    bg=COLORS['card'], fg=COLORS['text_light'],
                    font=('Segoe UI', 8)).pack(side=tk.LEFT)
    
    def _create_control_panel(self, parent):
        """创建控制面板"""
        panel = tk.Frame(parent, bg=COLORS['bg'], width=450)
        panel.pack_propagate(False)
        
        # 控制按钮卡片
        control_card = self._create_card(panel, "Control")
        control_card.pack(fill=tk.X, pady=(0, 10))
        
        self._create_control_buttons(control_card)
        
        # 统计信息卡片
        stats_card = self._create_card(panel, "Statistics")
        stats_card.pack(fill=tk.X, pady=(0, 10))
        
        self._create_stats_display(stats_card)
        
        # 创建Notebook用于切换不同视图
        notebook = ttk.Notebook(panel)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: AI Mission Log
        ai_log_frame = tk.Frame(notebook, bg=COLORS['card'])
        notebook.add(ai_log_frame, text="🤖 AI Mission Log")
        self._create_ai_log_display(ai_log_frame)
        
        # Tab 2: MCP Communications
        mcp_frame = tk.Frame(notebook, bg=COLORS['card'])
        notebook.add(mcp_frame, text="📡 MCP Comms")
        self._create_mcp_display(mcp_frame)
        
        # Tab 3: Drone Status
        drone_frame = tk.Frame(notebook, bg=COLORS['card'])
        notebook.add(drone_frame, text="🚁 Drones")
        self._create_drone_list(drone_frame)
        
        return panel
    
    def _create_card(self, parent, title):
        """创建卡片容器"""
        card = tk.Frame(parent, bg=COLORS['card'], relief='flat')
        
        # 标题
        title_frame = tk.Frame(card, bg=COLORS['card'], height=40)
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text=title,
                font=('Segoe UI', 11, 'bold'),
                bg=COLORS['card'], fg=COLORS['primary']).pack(side=tk.LEFT)
        
        return card
    
    def _create_control_buttons(self, parent):
        """创建控制按钮"""
        btn_frame = tk.Frame(parent, bg=COLORS['card'])
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        buttons = [
            ("▶ Start", self.start_mission),
            ("⏸ Pause", self.pause_mission),
            ("⟳ Reset", self.reset_mission),
        ]
        
        for text, command in buttons:
            btn = tk.Button(btn_frame, text=text, command=command,
                           font=('Segoe UI', 10),
                           bg=COLORS['accent'], fg='white',
                           relief='flat', padx=20, pady=8,
                           cursor='hand2')
            btn.pack(side=tk.LEFT, padx=5)
            
            # 悬停效果
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#2980B9'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=COLORS['accent']))
    
    def _create_stats_display(self, parent):
        """创建统计显示"""
        stats_frame = tk.Frame(parent, bg=COLORS['card'])
        stats_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.stat_labels = {}
        stats = [
            ("drones", "Active Drones", "0/0"),
            ("rescued", "Rescued", "0/0"),
            ("battery", "Avg Battery", "0%"),
        ]
        
        for key, label, default in stats:
            row = tk.Frame(stats_frame, bg=COLORS['card'])
            row.pack(fill=tk.X, pady=5)
            
            tk.Label(row, text=label + ":",
                    bg=COLORS['card'], fg=COLORS['text_light'],
                    font=('Segoe UI', 9)).pack(side=tk.LEFT)
            
            value_label = tk.Label(row, text=default,
                                  bg=COLORS['card'], fg=COLORS['text'],
                                  font=('Segoe UI', 10, 'bold'))
            value_label.pack(side=tk.RIGHT)
            
            self.stat_labels[key] = value_label
    
    def _create_drone_list(self, parent):
        """创建无人机列表"""
        list_frame = tk.Frame(parent, bg=COLORS['card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 创建表格式显示
        columns = ("Drone", "Status", "Battery", "Position", "Target", "Terrain")
        self.drone_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # 设置列宽和标题
        column_widths = {
            "Drone": 80,
            "Status": 100,
            "Battery": 70,
            "Position": 70,
            "Target": 70,
            "Terrain": 100
        }
        
        for col in columns:
            self.drone_tree.heading(col, text=col)
            self.drone_tree.column(col, width=column_widths[col], anchor='center')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.drone_tree.yview)
        self.drone_tree.configure(yscrollcommand=scrollbar.set)
        
        self.drone_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 详细信息显示区域
        detail_frame = tk.Frame(list_frame, bg=COLORS['card'])
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        tk.Label(detail_frame, text="Latest Decision:",
                font=('Segoe UI', 9, 'bold'),
                bg=COLORS['card'], fg=COLORS['primary']).pack(anchor=tk.W)
        
        self.drone_detail_text = tk.Text(detail_frame,
                                        font=('Segoe UI', 9),
                                        bg='#F5F5F5',
                                        fg=COLORS['text'],
                                        relief='flat',
                                        wrap=tk.WORD,
                                        height=6)
        self.drone_detail_text.pack(fill=tk.BOTH, expand=True)
        
        # 绑定选择事件
        self.drone_tree.bind('<<TreeviewSelect>>', self.on_drone_select)
    
    def _create_ai_log_display(self, parent):
        """创建AI任务日志显示"""
        log_frame = tk.Frame(parent, bg=COLORS['card'])
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 标题
        title_frame = tk.Frame(log_frame, bg=COLORS['card'])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(title_frame, text="AI Analysis & Decision Log",
                font=('Segoe UI', 10, 'bold'),
                bg=COLORS['card'], fg=COLORS['primary']).pack(side=tk.LEFT)
        
        # 清除按钮
        clear_btn = tk.Button(title_frame, text="Clear", 
                             command=self.clear_ai_log,
                             font=('Segoe UI', 8),
                             bg=COLORS['text_light'], fg='white',
                             relief='flat', padx=10, pady=3,
                             cursor='hand2')
        clear_btn.pack(side=tk.RIGHT)
        
        # 日志文本框
        self.ai_log_text = scrolledtext.ScrolledText(log_frame,
                                                     font=('Consolas', 9),
                                                     bg='#282C34',
                                                     fg='#ABB2BF',
                                                     relief='flat',
                                                     wrap=tk.WORD)
        self.ai_log_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置颜色标签
        self.ai_log_text.tag_configure("timestamp", foreground="#61AFEF")
        self.ai_log_text.tag_configure("drone_id", foreground="#E5C07B")
        self.ai_log_text.tag_configure("action", foreground="#98C379")
        self.ai_log_text.tag_configure("analysis", foreground="#C678DD")
        self.ai_log_text.tag_configure("error", foreground="#E06C75")
    
    def _create_mcp_display(self, parent):
        """创建MCP通信显示"""
        mcp_frame = tk.Frame(parent, bg=COLORS['card'])
        mcp_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 标题
        title_frame = tk.Frame(mcp_frame, bg=COLORS['card'])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(title_frame, text="MCP Server Communications",
                font=('Segoe UI', 10, 'bold'),
                bg=COLORS['card'], fg=COLORS['primary']).pack(side=tk.LEFT)
        
        # 清除按钮
        clear_btn = tk.Button(title_frame, text="Clear", 
                             command=self.clear_mcp_log,
                             font=('Segoe UI', 8),
                             bg=COLORS['text_light'], fg='white',
                             relief='flat', padx=10, pady=3,
                             cursor='hand2')
        clear_btn.pack(side=tk.RIGHT)
        
        # MCP通信文本框
        self.mcp_text = scrolledtext.ScrolledText(mcp_frame,
                                                  font=('Consolas', 9),
                                                  bg='#1E1E1E',
                                                  fg='#D4D4D4',
                                                  relief='flat',
                                                  wrap=tk.WORD)
        self.mcp_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置颜色标签
        self.mcp_text.tag_configure("request", foreground="#4EC9B0")
        self.mcp_text.tag_configure("response", foreground="#DCDCAA")
        self.mcp_text.tag_configure("json", foreground="#CE9178")
        self.mcp_text.tag_configure("success", foreground="#4EC9B0")
        self.mcp_text.tag_configure("error", foreground="#F48771")
    
    def create_model(self, seed=None):
        """创建模型"""
        if seed is None:
            seed = random.randint(1, 10000)
        
        self.current_seed = seed
        self.model = EnhancedDroneSwarmModel(
            width=20, height=20,
            n_drones=3, n_survivors=5,
            n_charging_stations=2,
            terrain_seed=seed
        )
        self.log_ai(f"System initialized with terrain seed: {seed}")
        self.log_mcp("MCP Server", "System Ready", {"seed": seed, "status": "initialized"})
    
    def draw_grid(self):
        """绘制网格"""
        if not self.model:
            return
        
        self.canvas.delete("all")
        
        # 绘制网格背景
        for y in range(self.model.height):
            for x in range(self.model.width):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # 获取地形信息
                terrain = self.model.terrain[y][x]
                color = self._get_terrain_color(terrain)
                
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                            fill=color, outline=COLORS['border'])
        
        # 绘制agents
        for agent in self.model.custom_agents:
            if agent.pos:
                self._draw_agent(agent)
    
    def _get_terrain_color(self, terrain):
        """获取地形颜色"""
        return TERRAIN_COLORS.get(terrain.terrain_type, '#FFFFFF')
    
    def _draw_agent(self, agent):
        """绘制agent"""
        x, y = agent.pos
        cx = x * self.cell_size + self.cell_size // 2
        cy = y * self.cell_size + self.cell_size // 2
        r = self.cell_size // 3
        
        if isinstance(agent, EnhancedDroneAgent):
            # 无人机 - 蓝色圆形
            color = COLORS['accent']
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                   fill=color, outline='white', width=2)
            # 添加文字标识
            self.canvas.create_text(cx, cy, text="D", 
                                   fill='white', font=('Arial', 10, 'bold'))
            
        elif isinstance(agent, SimpleSurvivorAgent):
            # 幸存者 - 红色/绿色圆形，更大更明显
            if agent.found:
                color = COLORS['success']  # 绿色 - 已救援
                outline_color = '#1E8449'
                text = "✓"
            else:
                color = COLORS['danger']   # 红色 - 待救援
                outline_color = '#C0392B'
                text = "!"
            
            # 绘制更大的圆形
            r_large = r + 3
            self.canvas.create_oval(cx-r_large, cy-r_large, cx+r_large, cy+r_large,
                                   fill=color, outline=outline_color, width=3)
            # 添加文字标识
            self.canvas.create_text(cx, cy, text=text, 
                                   fill='white', font=('Arial', 12, 'bold'))
            
        elif isinstance(agent, SimpleChargingStationAgent):
            # 充电站 - 橙色方形
            self.canvas.create_rectangle(cx-r, cy-r, cx+r, cy+r,
                                        fill=COLORS['warning'], outline='white', width=2)
            # 添加闪电符号
            self.canvas.create_text(cx, cy, text="⚡", 
                                   fill='white', font=('Arial', 10))
    
    def update_stats(self):
        """更新统计信息"""
        if not self.model:
            return
        
        analysis = self.model.get_ai_analysis()
        
        self.stat_labels['drones'].config(
            text=f"{analysis['active_drones']}/{analysis['total_drones']}")
        self.stat_labels['rescued'].config(
            text=f"{analysis['rescued']}/{analysis['total_survivors']}")
        self.stat_labels['battery'].config(
            text=f"{analysis['avg_battery']:.0f}%")
    
    def update_drone_list(self):
        """更新无人机列表"""
        if not self.model:
            return
        
        # 清空表格
        for item in self.drone_tree.get_children():
            self.drone_tree.delete(item)
        
        drones = [a for a in self.model.custom_agents 
                 if isinstance(a, EnhancedDroneAgent)]
        
        for drone in drones:
            # 电池图标
            if drone.battery > 60:
                battery_icon = "🟢"
            elif drone.battery > 30:
                battery_icon = "🟡"
            else:
                battery_icon = "🔴"
            
            # 获取地形信息
            terrain_info = "Unknown"
            if drone.pos:
                terrain = drone.get_current_terrain()
                if terrain:
                    terrain_info = terrain.terrain_type.value
            
            # 插入数据
            values = (
                drone.unique_id,
                drone.status,
                f"{battery_icon} {drone.battery:.0f}%",
                f"{drone.pos}" if drone.pos else "N/A",
                f"{drone.target}" if drone.target else "None",
                terrain_info
            )
            
            self.drone_tree.insert("", tk.END, values=values)
    
    def on_drone_select(self, event):
        """处理无人机选择事件"""
        selection = self.drone_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.drone_tree.item(item)['values']
        drone_id = values[0]
        
        # 查找对应的无人机
        drone = None
        for agent in self.model.custom_agents:
            if isinstance(agent, EnhancedDroneAgent) and agent.unique_id == drone_id:
                drone = agent
                break
        
        if not drone:
            return
        
        # 显示详细信息
        self.drone_detail_text.delete(1.0, tk.END)
        
        detail = f"Drone: {drone.unique_id}\n"
        detail += f"Status: {drone.status}\n"
        detail += f"Battery: {drone.battery:.1f}%\n"
        detail += f"Position: {drone.pos}\n"
        
        if drone.target:
            detail += f"Target: {drone.target}\n"
        
        if drone.pos:
            terrain = drone.get_current_terrain()
            if terrain:
                detail += f"\nTerrain Details:\n"
                detail += f"  Type: {terrain.terrain_type.value}\n"
                detail += f"  Altitude: {terrain.height:.0f}m\n"
                detail += f"  Weather: {terrain.weather.value}\n"
        
        if drone.decision_history:
            latest = drone.decision_history[-1]
            detail += f"\nLatest Decision:\n"
            detail += f"  {latest['thought']}\n"
            detail += f"  Action: {latest['decision']}\n"
        
        self.drone_detail_text.insert(1.0, detail)
    
    def log_ai(self, message, tag=None):
        """添加AI日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.ai_log_text.insert(tk.END, log_entry)
        if tag:
            # 应用标签到最后插入的文本
            start_idx = self.ai_log_text.index(f"end-{len(log_entry)+1}c")
            self.ai_log_text.tag_add(tag, start_idx, "end-1c")
        
        self.ai_log_text.see(tk.END)
        
        # 限制日志长度
        lines = self.ai_log_text.get(1.0, tk.END).split('\n')
        if len(lines) > 500:
            self.ai_log_text.delete(1.0, f"{len(lines)-500}.0")
    
    def log_mcp(self, source, action, data):
        """添加MCP通信日志"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        log_entry = f"\n{'='*60}\n"
        log_entry += f"[{timestamp}] {source} → {action}\n"
        log_entry += f"{'='*60}\n"
        
        # 格式化JSON数据
        if isinstance(data, dict):
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            log_entry += f"{json_str}\n"
        else:
            log_entry += f"{data}\n"
        
        self.mcp_text.insert(tk.END, log_entry)
        self.mcp_text.see(tk.END)
        
        # 限制日志长度
        lines = self.mcp_text.get(1.0, tk.END).split('\n')
        if len(lines) > 1000:
            self.mcp_text.delete(1.0, f"{len(lines)-1000}.0")
    
    def clear_ai_log(self):
        """清除AI日志"""
        self.ai_log_text.delete(1.0, tk.END)
        self.log_ai("AI log cleared")
    
    def clear_mcp_log(self):
        """清除MCP日志"""
        self.mcp_text.delete(1.0, tk.END)
        self.log_mcp("System", "Log Cleared", {"status": "cleared"})
    
    def generate_random_map(self):
        """生成随机地图"""
        self.auto_run = False
        new_seed = random.randint(1, 10000)
        self.create_model(seed=new_seed)
        self.log_ai(f"Generated new random map with seed: {new_seed}", "action")
        self.log_mcp("Terrain Generator", "New Map Generated", {
            "seed": new_seed,
            "size": "20x20",
            "timestamp": datetime.now().isoformat()
        })
    
    def on_canvas_hover(self, event):
        """处理鼠标悬停"""
        if not self.model:
            return
        
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.model.width and 0 <= y < self.model.height:
            terrain = self.model.terrain[y][x]
            
            # 构建详细信息
            info = f"({x},{y}) | {terrain.terrain_type.value} | "
            info += f"Alt: {terrain.height:.0f}m | "
            info += f"{terrain.weather.value}"
            
            if terrain.obstacle:
                info += f" | {terrain.obstacle.value}"
            
            # 检查是否有agent
            agents = self.model.grid.get_cell_list_contents([(x, y)])
            if agents:
                agent_types = []
                for agent in agents:
                    if isinstance(agent, EnhancedDroneAgent):
                        agent_types.append(f"Drone({agent.unique_id})")
                    elif isinstance(agent, SimpleSurvivorAgent):
                        agent_types.append("Survivor")
                    elif isinstance(agent, SimpleChargingStationAgent):
                        agent_types.append("Station")
                
                if agent_types:
                    info += f" | {', '.join(agent_types)}"
            
            self.terrain_info_label.config(text=info)
    
    def start_mission(self):
        """开始任务"""
        self.auto_run = True
        self.log_ai("Mission started - AI analysis active", "action")
        self.log_mcp("Command Center", "Mission Start", {
            "status": "active",
            "drones": len([a for a in self.model.custom_agents if isinstance(a, EnhancedDroneAgent)]),
            "survivors": len([a for a in self.model.custom_agents if isinstance(a, SimpleSurvivorAgent)])
        })
        
        # 模拟AI分析
        self._simulate_ai_analysis()
    
    def pause_mission(self):
        """暂停任务"""
        self.auto_run = False
        self.log_ai("Mission paused", "action")
        self.log_mcp("Command Center", "Mission Pause", {"status": "paused"})
    
    def reset_mission(self):
        """重置任务"""
        self.auto_run = False
        self.create_model(seed=self.current_seed)
        self.log_ai("Mission reset to initial state", "action")
        self.log_mcp("Command Center", "Mission Reset", {
            "status": "reset",
            "seed": self.current_seed
        })
    
    def _simulate_ai_analysis(self):
        """模拟AI分析过程"""
        if not self.model:
            return
        
        analysis = self.model.get_ai_analysis()
        
        # 记录AI分析 - 更清晰的格式
        self.log_ai("╔" + "═"*58 + "╗")
        self.log_ai("║" + " "*18 + "AI MISSION ANALYSIS" + " "*19 + "║")
        self.log_ai("╚" + "═"*58 + "╝")
        
        self.log_ai(f"📊 Mission Status:")
        self.log_ai(f"   • Active Drones: {analysis['active_drones']}/{analysis['total_drones']}")
        self.log_ai(f"   • Survivors: {analysis['rescued']}/{analysis['total_survivors']} rescued")
        self.log_ai(f"   • Average Battery: {analysis['avg_battery']:.1f}%")
        self.log_ai("")
        
        # 为每个无人机生成任务
        drones = [a for a in self.model.custom_agents if isinstance(a, EnhancedDroneAgent)]
        survivors = [a for a in self.model.custom_agents if isinstance(a, SimpleSurvivorAgent) and not a.found]
        
        if survivors:
            self.log_ai("🎯 Task Assignments:")
            
            for i, drone in enumerate(drones[:len(survivors)], 1):
                target = survivors[min(i-1, len(survivors)-1)]
                
                self.log_ai(f"\n   [{i}] {drone.unique_id} → Survivor at {target.pos}")
                self.log_ai(f"       Battery: {drone.battery:.0f}% | Status: {drone.status}")
                
                # 模拟MCP通信
                mcp_request = {
                    "drone_id": drone.unique_id,
                    "action": "search_and_rescue",
                    "target_position": list(target.pos),
                    "current_battery": round(drone.battery, 1),
                    "terrain_analysis": {
                        "type": drone.get_current_terrain().terrain_type.value if drone.pos else "unknown",
                        "weather": drone.get_current_terrain().weather.value if drone.pos else "unknown"
                    }
                }
                
                self.log_mcp("AI Planner", f"Task Assignment → {drone.unique_id}", mcp_request)
                
                # 模拟MCP响应
                mcp_response = {
                    "status": "acknowledged",
                    "drone_id": drone.unique_id,
                    "estimated_time": "5 steps",
                    "battery_required": "15%",
                    "route_planned": True
                }
                
                self.log_mcp(f"Drone {drone.unique_id}", "Task Acknowledged", mcp_response)
        
        self.log_ai("\n" + "─"*60)
    
    def on_canvas_click(self, event):
        """处理画布点击"""
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.model.width and 0 <= y < self.model.height:
            terrain = self.model.terrain[y][x]
            
            # 记录点击信息
            click_info = {
                "position": [x, y],
                "terrain": terrain.terrain_type.value,
                "altitude": terrain.height,
                "weather": terrain.weather.value,
                "obstacle": terrain.obstacle.value if terrain.obstacle else None
            }
            
            self.log_ai(f"Clicked position ({x},{y}) - {terrain.terrain_type.value}", "action")
            self.log_mcp("User Interface", "Cell Selected", click_info)
    
    def update_loop(self):
        """更新循环"""
        if self.auto_run and self.model:
            self.model.step()
            
            # 每10步记录一次AI决策
            if self.model.step_count % 10 == 0:
                self._log_drone_decisions()
        
        self.draw_grid()
        self.update_stats()
        self.update_drone_list()
        
        self.root.after(500, self.update_loop)
    
    def _log_drone_decisions(self):
        """记录无人机决策"""
        drones = [a for a in self.model.custom_agents if isinstance(a, EnhancedDroneAgent)]
        
        for drone in drones:
            if drone.decision_history:
                latest = drone.decision_history[-1]
                
                # 更清晰的格式
                self.log_ai(f"\n🤖 {drone.unique_id} Decision:")
                self.log_ai(f"   💭 Thought: {latest['thought']}")
                self.log_ai(f"   ⚡ Action: {latest['decision']}")
                self.log_ai(f"   📍 Position: {drone.pos} | 🔋 Battery: {drone.battery:.0f}%")
                
                # 记录MCP通信
                decision_data = {
                    "drone_id": drone.unique_id,
                    "thought_process": latest['thought'],
                    "action_taken": latest['decision'],
                    "position": list(drone.pos) if drone.pos else None,
                    "battery": round(drone.battery, 1),
                    "status": drone.status
                }
                
                self.log_mcp(f"Drone {drone.unique_id}", "Decision Update", decision_data)
    
    def run(self):
        """运行UI"""
        self.root.mainloop()


def main():
    app = RedesignedDroneUI()
    app.run()


if __name__ == "__main__":
    main()
