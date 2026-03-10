"""
Mesa 3.x 交互式Web UI
基于Mesa 3.x的SolaraViz创建交互式无人机控制界面
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mesa
import mesa.visualization
from simulation.simple_model import SimpleDroneSwarmModel, SimpleDroneAgent, SimpleSurvivorAgent, SimpleChargingStationAgent

class InteractiveDroneModel(SimpleDroneSwarmModel):
    """扩展的交互式无人机模型"""
    
    def __init__(self, width=20, height=20, n_drones=3, n_survivors=5, n_charging_stations=2):
        super().__init__(width, height, n_drones, n_survivors, n_charging_stations)
        self.user_actions = []  # 记录用户操作
        self.ai_decisions = []  # 记录AI决策
        
    def add_drone_manually(self, x, y, battery=100):
        """用户手动添加无人机"""
        drone_id = f"user_drone_{len([a for a in self.custom_agents if isinstance(a, SimpleDroneAgent)])}"
        new_drone = SimpleDroneAgent(drone_id, self)
        new_drone.battery = battery
        
        self.custom_agents.append(new_drone)
        self.grid.place_agent(new_drone, (x, y))
        
        action = f"用户在({x},{y})添加无人机{drone_id}，电量{battery}%"
        self.user_actions.append(action)
        self.log_event(action)
        
        return new_drone
    
    def add_survivor_manually(self, x, y):
        """用户手动添加幸存者"""
        survivor_id = f"user_survivor_{len([a for a in self.custom_agents if isinstance(a, SimpleSurvivorAgent)])}"
        new_survivor = SimpleSurvivorAgent(survivor_id, self)
        
        self.custom_agents.append(new_survivor)
        self.grid.place_agent(new_survivor, (x, y))
        
        action = f"用户在({x},{y})添加幸存者信号{survivor_id}"
        self.user_actions.append(action)
        self.log_event(action)
        
        return new_survivor
    
    def get_ai_analysis(self):
        """获取AI决策分析"""
        drones = [a for a in self.custom_agents if isinstance(a, SimpleDroneAgent)]
        survivors = [a for a in self.custom_agents if isinstance(a, SimpleSurvivorAgent)]
        
        analysis = {
            "总无人机数": len(drones),
            "活跃无人机": len([d for d in drones if d.status != 'charging']),
            "总幸存者": len(survivors),
            "已救援": len([s for s in survivors if s.found]),
            "平均电量": sum([d.battery for d in drones]) / len(drones) if drones else 0,
            "状态分布": {},
            "AI决策": self.ai_decisions[-5:] if self.ai_decisions else [],
            "用户操作": self.user_actions[-5:] if self.user_actions else []
        }
        
        # 统计无人机状态分布
        for drone in drones:
            status = drone.status
            analysis["状态分布"][status] = analysis["状态分布"].get(status, 0) + 1
        
        return analysis
    
    def step(self):
        """重写step方法，记录AI决策"""
        # 记录步骤前的状态
        pre_step_analysis = self.get_ai_analysis()
        
        # 执行原始step
        super().step()
        
        # 记录AI决策
        drones = [a for a in self.custom_agents if isinstance(a, SimpleDroneAgent)]
        for drone in drones:
            if hasattr(drone, 'last_decision'):
                decision = f"无人机{drone.unique_id}: {drone.last_decision}"
                self.ai_decisions.append(decision)

def agent_portrayal(agent):
    """智能体可视化配置"""
    if isinstance(agent, SimpleDroneAgent):
        # 根据电池电量和状态设置颜色和大小
        if agent.battery > 60:
            color = "Green"
        elif agent.battery > 30:
            color = "Orange"
        else:
            color = "Red"
        
        # 根据状态设置边框
        if agent.status == "charging":
            stroke_color = "Blue"
        elif agent.status == "rescuing":
            stroke_color = "Purple"
        else:
            stroke_color = "Black"
        
        return {
            "color": color,
            "stroke_color": stroke_color,
            "size": 1.0,
            "shape": "circle",
            "layer": 2,
            "text": f"D{agent.unique_id.split('_')[-1]}",
            "text_color": "White"
        }
    
    elif isinstance(agent, SimpleSurvivorAgent):
        color = "Gray" if agent.found else "Red"
        return {
            "color": color,
            "size": 0.8,
            "shape": "rect",
            "layer": 1,
            "text": "S" if not agent.found else "✓",
            "text_color": "White"
        }
    
    elif isinstance(agent, SimpleChargingStationAgent):
        return {
            "color": "Cyan",
            "size": 1.2,
            "shape": "rect",
            "layer": 0,
            "text": "⚡",
            "text_color": "Black"
        }

class AIAnalysisComponent:
    """AI分析组件"""
    
    def __init__(self):
        self.name = "AI决策分析"
    
    def render(self, model):
        """渲染AI分析面板"""
        analysis = model.get_ai_analysis()
        
        html = f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3 style="color: #007bff; margin-top: 0;">🧠 AI决策分析</h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0;">
                <div style="background: white; padding: 10px; border-radius: 5px; border-left: 4px solid #28a745;">
                    <h4 style="margin: 0; color: #28a745;">无人机状态</h4>
                    <p style="margin: 5px 0; font-size: 18px; font-weight: bold;">{analysis['活跃无人机']}/{analysis['总无人机数']}</p>
                    <small>活跃/总数</small>
                </div>
                
                <div style="background: white; padding: 10px; border-radius: 5px; border-left: 4px solid #dc3545;">
                    <h4 style="margin: 0; color: #dc3545;">救援进度</h4>
                    <p style="margin: 5px 0; font-size: 18px; font-weight: bold;">{analysis['已救援']}/{analysis['总幸存者']}</p>
                    <small>已救援/总数 ({analysis['已救援']/analysis['总幸存者']*100 if analysis['总幸存者'] > 0 else 0:.1f}%)</small>
                </div>
                
                <div style="background: white; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;">
                    <h4 style="margin: 0; color: #ffc107;">平均电量</h4>
                    <p style="margin: 5px 0; font-size: 18px; font-weight: bold;">{analysis['平均电量']:.1f}%</p>
                    <small>{'优秀' if analysis['平均电量'] > 60 else '良好' if analysis['平均电量'] > 30 else '警告'}</small>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                <div style="background: white; padding: 10px; border-radius: 5px;">
                    <h4 style="margin-top: 0; color: #17a2b8;">无人机状态分布</h4>
                    <ul style="margin: 0; padding-left: 20px;">
        """
        
        status_names = {
            'idle': '待机',
            'scanning': '扫描',
            'moving': '移动', 
            'charging': '充电',
            'rescuing': '救援'
        }
        
        for status, count in analysis['状态分布'].items():
            html += f"<li>{status_names.get(status, status)}: {count}架</li>"
        
        html += """
                    </ul>
                </div>
                
                <div style="background: white; padding: 10px; border-radius: 5px;">
                    <h4 style="margin-top: 0; color: #6f42c1;">最近AI决策</h4>
                    <div style="font-size: 12px; max-height: 100px; overflow-y: auto;">
        """
        
        for decision in analysis['AI决策']:
            html += f"<div style='margin: 2px 0; padding: 2px; background: #f1f3f4; border-radius: 3px;'>{decision}</div>"
        
        if not analysis['AI决策']:
            html += "<div style='color: #666; font-style: italic;'>暂无AI决策记录</div>"
        
        html += """
                    </div>
                </div>
            </div>
            
            <div style="background: white; padding: 10px; border-radius: 5px; margin-top: 15px;">
                <h4 style="margin-top: 0; color: #fd7e14;">用户操作记录</h4>
                <div style="font-size: 12px; max-height: 80px; overflow-y: auto;">
        """
        
        for action in analysis['用户操作']:
            html += f"<div style='margin: 2px 0; padding: 2px; background: #e9ecef; border-radius: 3px;'>{action}</div>"
        
        if not analysis['用户操作']:
            html += "<div style='color: #666; font-style: italic;'>暂无用户操作记录</div>"
        
        html += """
                </div>
            </div>
        </div>
        """
        
        return html

class UserControlComponent:
    """用户控制组件"""
    
    def __init__(self):
        self.name = "用户控制面板"
    
    def render(self, model):
        """渲染用户控制面板"""
        html = f"""
        <div style="background-color: #e9ecef; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3 style="color: #495057; margin-top: 0;">🎮 用户控制面板</h3>
            
            <div style="margin: 15px 0;">
                <h4>手动添加智能体</h4>
                <p style="font-size: 12px; color: #666;">
                    点击网格上的位置来选择坐标，然后使用下面的按钮添加无人机或幸存者
                </p>
                
                <div style="margin: 10px 0;">
                    <label>X坐标: </label>
                    <input type="number" id="x_coord" value="10" min="0" max="{model.width-1}" style="width: 60px;">
                    <label style="margin-left: 10px;">Y坐标: </label>
                    <input type="number" id="y_coord" value="10" min="0" max="{model.height-1}" style="width: 60px;">
                </div>
                
                <div style="margin: 10px 0;">
                    <label>无人机电量: </label>
                    <input type="range" id="battery_level" min="20" max="100" value="100" style="width: 100px;">
                    <span id="battery_display">100%</span>
                </div>
                
                <div style="margin: 10px 0;">
                    <button onclick="addDrone()" style="background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; margin-right: 10px; cursor: pointer;">
                        ➕ 添加无人机
                    </button>
                    <button onclick="addSurvivor()" style="background: #dc3545; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                        🆘 添加幸存者
                    </button>
                </div>
            </div>
            
            <div style="margin: 15px 0; padding-top: 15px; border-top: 1px solid #ccc;">
                <h4>模拟控制</h4>
                <button onclick="stepSimulation()" style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; margin-right: 10px; cursor: pointer;">
                    ▶️ 执行一步
                </button>
                <button onclick="resetSimulation()" style="background: #ffc107; color: black; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                    🔄 重置模拟
                </button>
            </div>
            
            <div style="margin: 15px 0; padding-top: 15px; border-top: 1px solid #ccc;">
                <h4>图例说明</h4>
                <div style="font-size: 12px;">
                    <div>🟢 健康无人机 (>60%电量) | 🟠 中等电量 (30-60%) | 🔴 低电量 (<30%)</div>
                    <div>🔵 充电中 | 🟣 救援中 | ⚡ 充电站 | 🔴 幸存者 | ⚪ 已救援</div>
                </div>
            </div>
        </div>
        
        <script>
            // 更新电量显示
            document.getElementById('battery_level').oninput = function() {{
                document.getElementById('battery_display').textContent = this.value + '%';
            }};
            
            // 添加无人机
            function addDrone() {{
                const x = parseInt(document.getElementById('x_coord').value);
                const y = parseInt(document.getElementById('y_coord').value);
                const battery = parseInt(document.getElementById('battery_level').value);
                
                // 这里需要与后端通信来添加无人机
                alert(`准备在位置(${x}, ${y})添加电量${battery}%的无人机`);
                console.log('Add drone at', x, y, 'with battery', battery);
            }}
            
            // 添加幸存者
            function addSurvivor() {{
                const x = parseInt(document.getElementById('x_coord').value);
                const y = parseInt(document.getElementById('y_coord').value);
                
                alert(`准备在位置(${x}, ${y})添加幸存者信号`);
                console.log('Add survivor at', x, y);
            }}
            
            // 执行模拟步骤
            function stepSimulation() {{
                alert('执行一步模拟');
                console.log('Step simulation');
            }}
            
            // 重置模拟
            function resetSimulation() {{
                if (confirm('确定要重置模拟吗？')) {{
                    alert('重置模拟');
                    console.log('Reset simulation');
                }}
            }}
        </script>
        """
        
        return html

def create_interactive_ui():
    """创建交互式UI"""
    
    # 创建模型
    model = InteractiveDroneModel(
        width=20, height=20,
        n_drones=3, n_survivors=5,
        n_charging_stations=2
    )
    
    # 创建可视化组件
    try:
        # 尝试使用Mesa 3.x的SolaraViz
        page = mesa.visualization.SolaraViz(
            model_class=InteractiveDroneModel,
            components=[
                mesa.visualization.make_space_component(agent_portrayal),
                AIAnalysisComponent(),
                UserControlComponent(),
            ],
            model_params={
                "width": 20,
                "height": 20,
                "n_drones": {
                    "type": "SliderInt",
                    "value": 3,
                    "label": "初始无人机数量",
                    "min": 1,
                    "max": 10,
                    "step": 1
                },
                "n_survivors": {
                    "type": "SliderInt",
                    "value": 5,
                    "label": "初始幸存者数量", 
                    "min": 1,
                    "max": 15,
                    "step": 1
                },
                "n_charging_stations": {
                    "type": "SliderInt",
                    "value": 2,
                    "label": "充电站数量",
                    "min": 1,
                    "max": 4,
                    "step": 1
                }
            },
            name="🚁 自主无人机群指挥系统 - 交互式控制台"
        )
        
        return page
        
    except Exception as e:
        print(f"SolaraViz创建失败: {e}")
        print("请确保安装了solara: pip install solara")
        return None

if __name__ == "__main__":
    print("🚁 启动Mesa 3.x交互式UI...")
    print("📊 功能特性:")
    print("   • 手动添加无人机（可设置电量）")
    print("   • 手动添加幸存者信号")
    print("   • 实时AI决策分析和可视化")
    print("   • 交互式网格操作")
    print("   • 详细状态监控和统计")
    print("   • 用户操作记录")
    
    # 创建UI
    ui = create_interactive_ui()
    
    if ui:
        print("\n🌐 启动Web服务器...")
        print("📱 访问地址: http://localhost:8521")
        ui.launch(port=8521)
    else:
        print("\n❌ UI创建失败，请检查依赖安装")
        print("💡 尝试运行: pip install solara mesa>=3.0.0")
        
        # 回退到控制台UI
        print("\n🔄 启动控制台UI作为备选...")
        from ui.console_ui import main as console_main
        console_main()