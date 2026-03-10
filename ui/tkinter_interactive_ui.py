"""
基于Tkinter的交互式无人机控制UI
支持手动添加无人机、实时AI分析和可视化
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from simulation.simple_model import SimpleDroneSwarmModel, SimpleDroneAgent, SimpleSurvivorAgent, SimpleChargingStationAgent

class InteractiveDroneUI:
    """交互式无人机控制界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚁 自主无人机群指挥系统 - 交互式控制台")
        self.root.geometry("1400x900")
        
        # 模型和状态
        self.model = None
        self.auto_run = False
        self.selected_pos = (10, 10)
        self.canvas_size = 600
        self.cell_size = 30
        
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
        left_frame = ttk.LabelFrame(main_frame, text="🗺️ 灾区模拟网格", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 网格画布
        self.canvas = tk.Canvas(left_frame, width=self.canvas_size, height=self.canvas_size, 
                               bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # 图例
        legend_frame = ttk.Frame(left_frame)
        legend_frame.pack(fill=tk.X, pady=10)
        
        legend_text = """
🟢 健康无人机(>60%) | 🟡 中等电量(30-60%) | 🔴 低电量(<30%)
🔵 充电中 | 🟣 救援中 | ⚡ 充电站 | 🔴 幸存者 | ⚪ 已救援
        """
        ttk.Label(legend_frame, text=legend_text, font=('Arial', 9)).pack()
        
        # 右侧：控制和分析面板
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        # 控制面板
        self.create_control_panel(right_frame)
        
        # AI分析面板
        self.create_analysis_panel(right_frame)
        
        # 状态表格
        self.create_status_table(right_frame)
        
        # 日志面板
        self.create_log_panel(right_frame)
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="🎮 控制面板", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 位置选择
        pos_frame = ttk.Frame(control_frame)
        pos_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pos_frame, text="选择位置:").pack(side=tk.LEFT)
        self.x_var = tk.IntVar(value=10)
        self.y_var = tk.IntVar(value=10)
        
        ttk.Label(pos_frame, text="X:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Spinbox(pos_frame, from_=0, to=19, width=5, textvariable=self.x_var).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(pos_frame, text="Y:").pack(side=tk.LEFT)
        ttk.Spinbox(pos_frame, from_=0, to=19, width=5, textvariable=self.y_var).pack(side=tk.LEFT)
        
        # 无人机电量设置
        battery_frame = ttk.Frame(control_frame)
        battery_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(battery_frame, text="无人机电量:").pack(side=tk.LEFT)
        self.battery_var = tk.IntVar(value=100)
        battery_scale = ttk.Scale(battery_frame, from_=20, to=100, orient=tk.HORIZONTAL, 
                                 variable=self.battery_var, length=150)
        battery_scale.pack(side=tk.LEFT, padx=(10, 5))
        
        self.battery_label = ttk.Label(battery_frame, text="100%")
        self.battery_label.pack(side=tk.LEFT)
        battery_scale.configure(command=self.update_battery_label)
        
        # 添加按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="➕ 添加无人机", 
                  command=self.add_drone).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🆘 添加幸存者", 
                  command=self.add_survivor).pack(side=tk.LEFT, padx=5)
        
        # 模拟控制
        sim_frame = ttk.Frame(control_frame)
        sim_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(sim_frame, text="▶️ 执行一步", 
                  command=self.step_simulation).pack(side=tk.LEFT, padx=(0, 5))
        
        self.auto_var = tk.BooleanVar()
        ttk.Checkbutton(sim_frame, text="自动运行", 
                       variable=self.auto_var, command=self.toggle_auto_run).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(sim_frame, text="🔄 重置", 
                  command=self.reset_simulation).pack(side=tk.LEFT, padx=5)
    
    def create_analysis_panel(self, parent):
        """创建AI分析面板"""
        analysis_frame = ttk.LabelFrame(parent, text="🧠 AI决策分析", padding=10)
        analysis_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 关键指标
        metrics_frame = ttk.Frame(analysis_frame)
        metrics_frame.pack(fill=tk.X)
        
        # 创建指标标签
        self.metrics_labels = {}
        metrics = ["活跃无人机", "救援进度", "平均电量", "模拟步数"]
        
        for i, metric in enumerate(metrics):
            frame = ttk.Frame(metrics_frame)
            frame.grid(row=i//2, column=i%2, padx=5, pady=2, sticky="w")
            
            ttk.Label(frame, text=f"{metric}:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
            self.metrics_labels[metric] = ttk.Label(frame, text="0", font=('Arial', 9))
            self.metrics_labels[metric].pack(side=tk.LEFT, padx=(5, 0))
        
        # 状态分布
        status_frame = ttk.Frame(analysis_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(status_frame, text="无人机状态分布:", font=('Arial', 9, 'bold')).pack(anchor="w")
        self.status_text = tk.Text(status_frame, height=3, width=40, font=('Arial', 8))
        self.status_text.pack(fill=tk.X, pady=(5, 0))
    
    def create_status_table(self, parent):
        """创建状态表格"""
        table_frame = ttk.LabelFrame(parent, text="🚁 无人机详细状态", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建表格
        columns = ("ID", "电量", "状态", "位置", "目标")
        self.status_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        # 设置列标题
        for col in columns:
            self.status_tree.heading(col, text=col)
            self.status_tree.column(col, width=80)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.status_tree.yview)
        self.status_tree.configure(yscrollcommand=scrollbar.set)
        
        self.status_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_log_panel(self, parent):
        """创建日志面板"""
        log_frame = ttk.LabelFrame(parent, text="📝 任务日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=50, 
                                                 font=('Courier', 8), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def create_model(self):
        """创建模拟模型"""
        self.model = SimpleDroneSwarmModel(
            width=20, height=20,
            n_drones=3, n_survivors=5,
            n_charging_stations=2
        )
        self.log_message("✅ 模拟系统初始化完成")
        self.log_message(f"📊 初始状态: 3架无人机, 5个幸存者信号, 2个充电站")
    
    def on_canvas_click(self, event):
        """处理画布点击事件"""
        x = int(event.x // self.cell_size)
        y = int(event.y // self.cell_size)
        
        if 0 <= x < 20 and 0 <= y < 20:
            self.x_var.set(x)
            self.y_var.set(y)
            self.selected_pos = (x, y)
    
    def update_battery_label(self, value):
        """更新电量标签"""
        self.battery_label.config(text=f"{int(float(value))}%")
    
    def add_drone(self):
        """添加无人机"""
        if not self.model:
            return
        
        x, y = self.x_var.get(), self.y_var.get()
        battery = self.battery_var.get()
        
        # 检查位置是否有充电站
        cell_contents = self.model.grid.get_cell_list_contents([(x, y)])
        if any(isinstance(agent, SimpleChargingStationAgent) for agent in cell_contents):
            messagebox.showwarning("位置冲突", "该位置已有充电站，请选择其他位置")
            return
        
        # 创建新无人机
        drone_count = len([a for a in self.model.custom_agents if isinstance(a, SimpleDroneAgent)])
        drone_id = f"user_drone_{drone_count}"
        
        new_drone = SimpleDroneAgent(drone_id, self.model)
        new_drone.battery = battery
        
        self.model.custom_agents.append(new_drone)
        self.model.grid.place_agent(new_drone, (x, y))
        
        message = f"用户在({x},{y})添加无人机{drone_id}，电量{battery}%"
        self.model.log_event(message)
        self.log_message(f"➕ {message}")
        
        messagebox.showinfo("添加成功", f"无人机{drone_id}已添加到位置({x},{y})")
    
    def add_survivor(self):
        """添加幸存者"""
        if not self.model:
            return
        
        x, y = self.x_var.get(), self.y_var.get()
        
        # 检查位置是否有充电站
        cell_contents = self.model.grid.get_cell_list_contents([(x, y)])
        if any(isinstance(agent, SimpleChargingStationAgent) for agent in cell_contents):
            messagebox.showwarning("位置冲突", "该位置已有充电站，请选择其他位置")
            return
        
        # 创建新幸存者
        survivor_count = len([a for a in self.model.custom_agents if isinstance(a, SimpleSurvivorAgent)])
        survivor_id = f"user_survivor_{survivor_count}"
        
        new_survivor = SimpleSurvivorAgent(survivor_id, self.model)
        self.model.custom_agents.append(new_survivor)
        self.model.grid.place_agent(new_survivor, (x, y))
        
        message = f"用户在({x},{y})添加幸存者信号{survivor_id}"
        self.model.log_event(message)
        self.log_message(f"🆘 {message}")
        
        messagebox.showinfo("添加成功", f"幸存者信号{survivor_id}已添加到位置({x},{y})")
    
    def step_simulation(self):
        """执行一步模拟"""
        if self.model:
            self.model.step()
            self.log_message(f"▶️ 执行第{self.model.step_count}步模拟")
    
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
                time.sleep(1)  # 1秒间隔
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def reset_simulation(self):
        """重置模拟"""
        if messagebox.askyesno("确认重置", "确定要重置模拟吗？这将清除所有当前数据。"):
            self.auto_var.set(False)
            self.auto_run = False
            self.create_model()
            self.log_message("🔄 模拟已重置")
    
    def draw_grid(self):
        """绘制网格"""
        self.canvas.delete("all")
        
        if not self.model:
            return
        
        # 绘制网格线
        for i in range(21):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.canvas_size, fill="lightgray")
            self.canvas.create_line(0, x, self.canvas_size, x, fill="lightgray")
        
        # 绘制智能体
        for agent in self.model.custom_agents:
            if agent.pos:
                x, y = agent.pos
                x1 = x * self.cell_size + 2
                y1 = y * self.cell_size + 2
                x2 = (x + 1) * self.cell_size - 2
                y2 = (y + 1) * self.cell_size - 2
                
                if isinstance(agent, SimpleDroneAgent):
                    # 根据电池电量设置颜色
                    if agent.battery > 60:
                        color = "green"
                    elif agent.battery > 30:
                        color = "orange"
                    else:
                        color = "red"
                    
                    # 根据状态设置边框
                    outline = "blue" if agent.status == "charging" else "purple" if agent.status == "rescuing" else "black"
                    
                    self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline=outline, width=2)
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="D", fill="white", font=('Arial', 8, 'bold'))
                
                elif isinstance(agent, SimpleSurvivorAgent):
                    color = "gray" if agent.found else "red"
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                    text = "✓" if agent.found else "S"
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=text, fill="white", font=('Arial', 8, 'bold'))
                
                elif isinstance(agent, SimpleChargingStationAgent):
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="cyan", outline="black", width=2)
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="⚡", font=('Arial', 10))
        
        # 高亮选中位置
        x, y = self.x_var.get(), self.y_var.get()
        x1 = x * self.cell_size
        y1 = y * self.cell_size
        x2 = (x + 1) * self.cell_size
        y2 = (y + 1) * self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=3, fill="", stipple="gray25")
    
    def update_analysis(self):
        """更新AI分析"""
        if not self.model:
            return
        
        drones = [a for a in self.model.custom_agents if isinstance(a, SimpleDroneAgent)]
        survivors = [a for a in self.model.custom_agents if isinstance(a, SimpleSurvivorAgent)]
        
        # 更新指标
        total_drones = len(drones)
        active_drones = len([d for d in drones if d.status != 'charging'])
        total_survivors = len(survivors)
        rescued_survivors = len([s for s in survivors if s.found])
        avg_battery = sum([d.battery for d in drones]) / total_drones if total_drones > 0 else 0
        
        self.metrics_labels["活跃无人机"].config(text=f"{active_drones}/{total_drones}")
        self.metrics_labels["救援进度"].config(text=f"{rescued_survivors}/{total_survivors}")
        self.metrics_labels["平均电量"].config(text=f"{avg_battery:.1f}%")
        self.metrics_labels["模拟步数"].config(text=str(self.model.step_count))
        
        # 更新状态分布
        status_distribution = {}
        status_names = {
            'idle': '待机',
            'scanning': '扫描',
            'moving': '移动',
            'charging': '充电',
            'rescuing': '救援'
        }
        
        for drone in drones:
            status = status_names.get(drone.status, drone.status)
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        self.status_text.delete(1.0, tk.END)
        for status, count in status_distribution.items():
            self.status_text.insert(tk.END, f"{status}: {count}架\n")
    
    def update_status_table(self):
        """更新状态表格"""
        if not self.model:
            return
        
        # 清空表格
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)
        
        # 添加无人机数据
        drones = [a for a in self.model.custom_agents if isinstance(a, SimpleDroneAgent)]
        status_names = {
            'idle': '待机',
            'scanning': '扫描',
            'moving': '移动',
            'charging': '充电',
            'rescuing': '救援'
        }
        
        for drone in drones:
            battery_icon = "🟢" if drone.battery > 60 else "🟡" if drone.battery > 30 else "🔴"
            status = status_names.get(drone.status, drone.status)
            position = f"({drone.pos[0]}, {drone.pos[1]})" if drone.pos else "未知"
            target = f"({drone.target[0]}, {drone.target[1]})" if drone.target else "无"
            
            self.status_tree.insert("", tk.END, values=(
                drone.unique_id,
                f"{battery_icon} {drone.battery}%",
                status,
                position,
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
    print("🚁 启动Tkinter交互式UI...")
    print("📊 功能特性:")
    print("   • 点击网格选择位置")
    print("   • 手动添加无人机（可设置电量）")
    print("   • 手动添加幸存者信号")
    print("   • 实时AI决策分析")
    print("   • 详细状态监控")
    print("   • 自动/手动模拟控制")
    print("   • 任务日志记录")
    
    app = InteractiveDroneUI()
    app.run()

if __name__ == "__main__":
    main()