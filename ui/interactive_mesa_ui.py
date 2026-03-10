"""
Mesa 3.x 交互式UI界面
支持用户手动添加无人机并实时查看AI反应和分析
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mesa
import solara
from typing import Dict, Any
import matplotlib.pyplot as plt
import pandas as pd
from simulation.simple_model import SimpleDroneSwarmModel, SimpleDroneAgent, SimpleSurvivorAgent, SimpleChargingStationAgent

# 全局状态管理
model_state = solara.reactive(None)
step_count = solara.reactive(0)
auto_run = solara.reactive(False)
selected_position = solara.reactive((0, 0))
drone_count = solara.reactive(3)
survivor_count = solara.reactive(5)
analysis_data = solara.reactive({})

def agent_portrayal(agent):
    """定义智能体在网格中的显示方式"""
    if isinstance(agent, SimpleDroneAgent):
        # 根据电池电量设置颜色
        if agent.battery > 60:
            color = "#28a745"  # 绿色 - 健康
        elif agent.battery > 30:
            color = "#ffc107"  # 黄色 - 中等
        else:
            color = "#dc3545"  # 红色 - 低电量
        
        return {
            "color": color,
            "size": 25,
            "shape": "circle",
            "layer": 2,
            "tooltip": f"无人机 {agent.unique_id}\n电量: {agent.battery}%\n状态: {agent.status}\n位置: {agent.pos}"
        }
    
    elif isinstance(agent, SimpleSurvivorAgent):
        color = "#6c757d" if agent.found else "#dc3545"
        return {
            "color": color,
            "size": 20,
            "shape": "rect",
            "layer": 1,
            "tooltip": f"幸存者 {agent.unique_id}\n状态: {'已救援' if agent.found else '待救援'}\n位置: {agent.pos}"
        }
    
    elif isinstance(agent, SimpleChargingStationAgent):
        return {
            "color": "#17a2b8",
            "size": 30,
            "shape": "rect",
            "layer": 0,
            "tooltip": f"充电站 {agent.unique_id}\n位置: {agent.pos}"
        }

@solara.component
def DroneControlPanel():
    """无人机控制面板组件"""
    
    def create_new_model():
        """创建新的模型"""
        new_model = SimpleDroneSwarmModel(
            width=20, height=20,
            n_drones=drone_count.value,
            n_survivors=survivor_count.value,
            n_charging_stations=2
        )
        model_state.set(new_model)
        step_count.set(0)
        update_analysis()
    
    def add_drone_at_position():
        """在选定位置添加无人机"""
        if model_state.value:
            model = model_state.value
            drone_id = f"manual_drone_{len([a for a in model.custom_agents if isinstance(a, SimpleDroneAgent)])}"
            
            # 创建新无人机
            new_drone = SimpleDroneAgent(drone_id, model)
            model.custom_agents.append(new_drone)
            
            # 放置在选定位置
            x, y = selected_position.value
            model.grid.place_agent(new_drone, (x, y))
            model.log_event(f"用户手动添加无人机 {drone_id} 在位置 ({x}, {y})")
            
            # 更新分析
            update_analysis()
    
    def add_survivor_at_position():
        """在选定位置添加幸存者"""
        if model_state.value:
            model = model_state.value
            survivor_id = f"manual_survivor_{len([a for a in model.custom_agents if isinstance(a, SimpleSurvivorAgent)])}"
            
            # 创建新幸存者
            new_survivor = SimpleSurvivorAgent(survivor_id, model)
            model.custom_agents.append(new_survivor)
            
            # 放置在选定位置
            x, y = selected_position.value
            model.grid.place_agent(new_survivor, (x, y))
            model.log_event(f"用户手动添加幸存者信号 {survivor_id} 在位置 ({x}, {y})")
            
            # 更新分析
            update_analysis()
    
    def step_simulation():
        """执行一步模拟"""
        if model_state.value:
            model_state.value.step()
            step_count.set(step_count.value + 1)
            update_analysis()
    
    def reset_simulation():
        """重置模拟"""
        create_new_model()
    
    # UI布局
    with solara.Card("🎮 无人机群控制面板", margin=0, elevation=2):
        with solara.Column():
            # 模型参数设置
            solara.SliderInt("无人机数量", value=drone_count, min=1, max=10)
            solara.SliderInt("幸存者数量", value=survivor_count, min=1, max=15)
            
            # 位置选择
            with solara.Row():
                solara.InputInt("X坐标", value=selected_position.value[0], 
                               on_value=lambda x: selected_position.set((x, selected_position.value[1])))
                solara.InputInt("Y坐标", value=selected_position.value[1],
                               on_value=lambda y: selected_position.set((selected_position.value[0], y)))
            
            # 控制按钮
            with solara.Row():
                solara.Button("创建新模拟", on_click=create_new_model, color="primary")
                solara.Button("重置", on_click=reset_simulation, color="warning")
            
            with solara.Row():
                solara.Button("添加无人机", on_click=add_drone_at_position, color="success")
                solara.Button("添加幸存者", on_click=add_survivor_at_position, color="danger")
            
            with solara.Row():
                solara.Button("执行一步", on_click=step_simulation, color="info")
                solara.Checkbox("自动运行", value=auto_run)

@solara.component
def AIAnalysisPanel():
    """AI分析面板组件"""
    
    def update_analysis():
        """更新AI分析数据"""
        if not model_state.value:
            return
        
        model = model_state.value
        drones = [a for a in model.custom_agents if isinstance(a, SimpleDroneAgent)]
        survivors = [a for a in model.custom_agents if isinstance(a, SimpleSurvivorAgent)]
        
        # 计算统计数据
        total_drones = len(drones)
        active_drones = len([d for d in drones if d.status != 'charging'])
        total_survivors = len(survivors)
        rescued_survivors = len([s for s in survivors if s.found])
        avg_battery = sum([d.battery for d in drones]) / total_drones if total_drones > 0 else 0
        
        # AI决策分析
        status_distribution = {}
        for drone in drones:
            status_distribution[drone.status] = status_distribution.get(drone.status, 0) + 1
        
        # 效率分析
        rescue_efficiency = (rescued_survivors / total_survivors * 100) if total_survivors > 0 else 0
        battery_efficiency = avg_battery
        
        analysis_data.set({
            "total_drones": total_drones,
            "active_drones": active_drones,
            "total_survivors": total_survivors,
            "rescued_survivors": rescued_survivors,
            "avg_battery": avg_battery,
            "rescue_efficiency": rescue_efficiency,
            "battery_efficiency": battery_efficiency,
            "status_distribution": status_distribution,
            "step_count": model.step_count
        })
    
    # 实时更新分析
    update_analysis()
    
    with solara.Card("🧠 AI决策分析", margin=0, elevation=2):
        if analysis_data.value:
            data = analysis_data.value
            
            # 关键指标
            with solara.Columns([1, 1, 1, 1]):
                with solara.Card("活跃无人机"):
                    solara.Markdown(f"## {data['active_drones']}/{data['total_drones']}")
                    solara.Markdown("架无人机在执行任务")
                
                with solara.Card("救援进度"):
                    solara.Markdown(f"## {data['rescued_survivors']}/{data['total_survivors']}")
                    solara.Markdown(f"救援效率: {data['rescue_efficiency']:.1f}%")
                
                with solara.Card("平均电量"):
                    solara.Markdown(f"## {data['avg_battery']:.1f}%")
                    battery_status = "优秀" if data['avg_battery'] > 60 else "良好" if data['avg_battery'] > 30 else "警告"
                    solara.Markdown(f"电量状态: {battery_status}")
                
                with solara.Card("模拟步数"):
                    solara.Markdown(f"## {data['step_count']}")
                    solara.Markdown("步执行完成")
            
            # 无人机状态分布
            if data['status_distribution']:
                with solara.Card("无人机状态分布"):
                    status_text = ""
                    for status, count in data['status_distribution'].items():
                        status_names = {
                            'idle': '待机',
                            'scanning': '扫描',
                            'moving': '移动',
                            'charging': '充电',
                            'rescuing': '救援'
                        }
                        status_text += f"- {status_names.get(status, status)}: {count}架\n"
                    solara.Markdown(status_text)

@solara.component
def MissionLogPanel():
    """任务日志面板组件"""
    
    with solara.Card("📝 任务日志", margin=0, elevation=2):
        if model_state.value and model_state.value.mission_log:
            # 显示最近的10条日志
            recent_logs = model_state.value.mission_log[-10:]
            log_text = ""
            for log_entry in reversed(recent_logs):  # 最新的在上面
                log_text += f"{log_entry}\n"
            
            with solara.Column():
                solara.Markdown("### 最近活动")
                solara.Preformatted(log_text, style={"height": "200px", "overflow-y": "scroll"})
        else:
            solara.Markdown("*暂无日志记录*")

@solara.component
def DroneStatusTable():
    """无人机状态表格组件"""
    
    with solara.Card("🚁 无人机详细状态", margin=0, elevation=2):
        if model_state.value:
            drones = [a for a in model_state.value.custom_agents if isinstance(a, SimpleDroneAgent)]
            
            if drones:
                # 创建表格数据
                table_data = []
                for drone in drones:
                    battery_icon = "🟢" if drone.battery > 60 else "🟡" if drone.battery > 30 else "🔴"
                    status_names = {
                        'idle': '待机',
                        'scanning': '扫描', 
                        'moving': '移动',
                        'charging': '充电',
                        'rescuing': '救援'
                    }
                    
                    table_data.append({
                        "ID": drone.unique_id,
                        "电量": f"{battery_icon} {drone.battery}%",
                        "状态": status_names.get(drone.status, drone.status),
                        "位置": f"({drone.pos[0]}, {drone.pos[1]})",
                        "目标": f"({drone.target[0]}, {drone.target[1]})" if drone.target else "无"
                    })
                
                # 显示表格
                df = pd.DataFrame(table_data)
                solara.DataFrame(df, items_per_page=10)
            else:
                solara.Markdown("*暂无无人机*")
        else:
            solara.Markdown("*请先创建模拟*")

def update_analysis():
    """更新分析数据的全局函数"""
    if not model_state.value:
        return
    
    model = model_state.value
    drones = [a for a in model.custom_agents if isinstance(a, SimpleDroneAgent)]
    survivors = [a for a in model.custom_agents if isinstance(a, SimpleSurvivorAgent)]
    
    # 计算统计数据
    total_drones = len(drones)
    active_drones = len([d for d in drones if d.status != 'charging'])
    total_survivors = len(survivors)
    rescued_survivors = len([s for s in survivors if s.found])
    avg_battery = sum([d.battery for d in drones]) / total_drones if total_drones > 0 else 0
    
    # AI决策分析
    status_distribution = {}
    for drone in drones:
        status_distribution[drone.status] = status_distribution.get(drone.status, 0) + 1
    
    # 效率分析
    rescue_efficiency = (rescued_survivors / total_survivors * 100) if total_survivors > 0 else 0
    battery_efficiency = avg_battery
    
    analysis_data.set({
        "total_drones": total_drones,
        "active_drones": active_drones,
        "total_survivors": total_survivors,
        "rescued_survivors": rescued_survivors,
        "avg_battery": avg_battery,
        "rescue_efficiency": rescue_efficiency,
        "battery_efficiency": battery_efficiency,
        "status_distribution": status_distribution,
        "step_count": model.step_count
    })

@solara.component
def InteractiveDroneUI():
    """主UI组件"""
    
    # 自动运行逻辑
    def auto_step():
        if auto_run.value and model_state.value:
            model_state.value.step()
            step_count.set(step_count.value + 1)
            update_analysis()
    
    # 使用定时器实现自动运行
    solara.use_interval(auto_step, 2.0, active=auto_run.value)
    
    # 页面布局
    with solara.AppLayout(title="🚁 自主无人机群指挥系统"):
        with solara.Sidebar():
            DroneControlPanel()
        
        # 主内容区域
        with solara.Column():
            # 网格可视化
            if model_state.value:
                with solara.Card("🗺️ 灾区模拟网格", margin=0, elevation=2):
                    # 使用Mesa的空间可视化
                    space_component = mesa.visualization.make_space_component(agent_portrayal)
                    space_component(model_state.value)
            
            # 分析面板
            with solara.Row():
                with solara.Column():
                    AIAnalysisPanel()
                with solara.Column():
                    MissionLogPanel()
            
            # 详细状态表格
            DroneStatusTable()

def create_mesa_app():
    """创建Mesa应用"""
    
    # 初始化模型
    initial_model = SimpleDroneSwarmModel(
        width=20, height=20,
        n_drones=3, n_survivors=5,
        n_charging_stations=2
    )
    model_state.set(initial_model)
    update_analysis()
    
    # 返回Solara应用
    return InteractiveDroneUI

# 启动应用
if __name__ == "__main__":
    print("🚁 启动Mesa交互式UI...")
    print("📊 功能特性:")
    print("   • 手动添加无人机和幸存者")
    print("   • 实时AI决策分析")
    print("   • 交互式网格可视化")
    print("   • 详细状态监控")
    print("   • 自动/手动模拟控制")
    print("\n🌐 访问地址: http://localhost:8765")
    
    # 创建并启动应用
    app = create_mesa_app()
    solara.run(app, host="localhost", port=8765)