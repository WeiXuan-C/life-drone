"""
LangGraph 工作流实现 - 无人机救援任务编排
使用状态图来管理复杂的救援任务流程
"""

from typing import Dict, List, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
import json

from .memory import MissionMemory
from mcp_server.drone_tools import (
    discover_drones, get_battery_status, move_to, 
    thermal_scan, return_to_base
)


class RescueState(TypedDict):
    """救援任务状态定义"""
    messages: List[BaseMessage]
    mission_goal: str
    available_drones: List[str]
    drone_status: Dict[str, Any]
    survivors_found: List[Dict[str, Any]]
    current_phase: str  # "planning", "execution", "monitoring", "completion"
    next_action: Optional[Dict[str, Any]]  # Changed from str to Dict for action details
    decision: Optional[str]  # Added for workflow decisions
    memory_context: List[str]
    failure_count: int  # Track consecutive failures
    max_failures: int  # Maximum allowed failures before giving up


class LangGraphRescueWorkflow:
    """
    基于 LangGraph 的救援工作流程管理器
    
    工作流程阶段：
    1. 任务分析 (analyze_mission)
    2. 资源发现 (discover_resources) 
    3. 任务规划 (plan_mission)
    4. 执行监控 (execute_and_monitor)
    5. 结果评估 (evaluate_results)
    """
    
    def __init__(self, model_name: str = "qwen2", base_url: str = "http://localhost:11434"):
        self.llm = ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0.1
        )
        self.memory = MissionMemory()
        
        # 定义可用工具
        self.tools = [
            self._create_tool_function("discover_drones", discover_drones),
            self._create_tool_function("get_battery_status", get_battery_status),
            self._create_tool_function("move_to", move_to),
            self._create_tool_function("thermal_scan", thermal_scan),
            self._create_tool_function("return_to_base", return_to_base),
        ]
        
        self.tool_node = ToolNode(self.tools)
        
        # 构建状态图
        self.workflow = self._build_workflow()
    
    def _create_tool_function(self, name: str, func):
        """将 MCP 工具转换为 LangGraph 兼容的工具"""
        @tool
        def tool_wrapper(**kwargs):
            """Tool wrapper for MCP functions"""
            return func(**kwargs)
        
        # Set the tool name manually
        tool_wrapper.name = name
        return tool_wrapper
    
    def _build_workflow(self) -> StateGraph:
        """构建 LangGraph 工作流程图"""
        
        workflow = StateGraph(RescueState)
        
        # 添加节点
        workflow.add_node("analyze_mission", self.analyze_mission)
        workflow.add_node("discover_resources", self.discover_resources)
        workflow.add_node("plan_mission", self.plan_mission)
        workflow.add_node("execute_action", self.execute_action)
        workflow.add_node("monitor_progress", self.monitor_progress)
        workflow.add_node("evaluate_results", self.evaluate_results)
        
        # 定义流程边
        workflow.set_entry_point("analyze_mission")
        
        workflow.add_edge("analyze_mission", "discover_resources")
        workflow.add_edge("discover_resources", "plan_mission")
        workflow.add_edge("plan_mission", "execute_action")
        
        # 条件边：从执行行动决定下一步
        workflow.add_conditional_edges(
            "execute_action",
            self.should_continue,
            {
                "continue": "monitor_progress",
                "evaluate": "evaluate_results",
                "replan": "plan_mission"
            }
        )
        
        # 条件边：从进度监控决定下一步
        workflow.add_conditional_edges(
            "monitor_progress",
            self.should_continue,
            {
                "continue": "execute_action",
                "evaluate": "evaluate_results",
                "replan": "plan_mission"
            }
        )
        
        workflow.add_edge("evaluate_results", END)
        
        return workflow.compile()
    
    def analyze_mission(self, state: RescueState) -> RescueState:
        """阶段1：分析任务目标和当前状况"""
        
        print("🧠 阶段1：任务分析")
        
        # 获取历史上下文
        recent_events = self.memory.get_recent_events(5)
        
        analysis_prompt = f"""
        作为救援指挥官，分析以下任务：
        
        任务目标：{state['mission_goal']}
        
        最近事件：
        {chr(10).join(recent_events) if recent_events else "无历史记录"}
        
        请分析：
        1. 任务的紧急程度和复杂性
        2. 需要的资源类型
        3. 潜在的挑战和风险
        4. 建议的执行策略
        
        以JSON格式回复，包含：analysis, urgency_level, required_resources, strategy
        """
        
        response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
        
        # 解析分析结果
        try:
            analysis = json.loads(response.content)
        except:
            analysis = {
                "analysis": response.content,
                "urgency_level": "medium",
                "required_resources": ["drones"],
                "strategy": "systematic_search"
            }
        
        # 更新状态
        state["current_phase"] = "resource_discovery"
        state["messages"].append(AIMessage(content=f"任务分析完成：{analysis['analysis']}"))
        
        self.memory.add_event(f"任务分析：{analysis['analysis']}")
        
        return state
    
    def discover_resources(self, state: RescueState) -> RescueState:
        """阶段2：发现可用资源（无人机、设备等）"""
        
        print("🔍 阶段2：资源发现")
        
        # 发现无人机
        drone_result = discover_drones()
        
        if drone_result["success"]:
            state["available_drones"] = drone_result["drones"]
            
            # 获取每个无人机的状态
            drone_status = {}
            for drone_id in state["available_drones"]:
                status = get_battery_status(drone_id=drone_id)
                drone_status[drone_id] = status
            
            state["drone_status"] = drone_status
            
            message = f"发现 {len(state['available_drones'])} 架无人机"
            state["messages"].append(AIMessage(content=message))
            self.memory.add_event(message)
        
        state["current_phase"] = "mission_planning"
        return state
    
    def plan_mission(self, state: RescueState) -> RescueState:
        """阶段3：制定详细的任务执行计划"""
        
        print("📋 阶段3：任务规划")
        
        planning_prompt = f"""
        基于以下信息制定救援计划：
        
        任务目标：{state['mission_goal']}
        可用无人机：{state['available_drones']}
        无人机状态：{state['drone_status']}
        
        可用行动类型（只能使用以下行动）：
        1. thermal_scan - 热成像扫描搜索幸存者（需要至少5%电量）
        2. move_to - 移动无人机到指定位置（参数：x, y坐标）
        3. return_to_base - 返回基地充电
        
        制定一个分步骤的执行计划，考虑：
        1. 无人机电量管理（电量不足时使用return_to_base）
        2. 搜索区域分配
        3. 任务优先级
        4. 风险控制
        
        以JSON格式回复，包含步骤列表：
        {{"steps": [{{"action": "thermal_scan", "drone_id": "drone_1", "parameters": {{}}, "priority": 1}}]}}
        
        注意：action字段只能是 thermal_scan, move_to, 或 return_to_base
        """
        
        response = self.llm.invoke([HumanMessage(content=planning_prompt)])
        
        try:
            plan = json.loads(response.content)
            state["next_action"] = plan["steps"][0] if plan["steps"] else None
        except:
            # 检查是否有可用的无人机和足够的电量
            available_drone = None
            if state["available_drones"]:
                for drone_id in state["available_drones"]:
                    drone_status = state["drone_status"].get(drone_id, {})
                    battery = drone_status.get("battery_level", 0)
                    if battery >= 5:  # 需要至少5%电量进行热扫描
                        available_drone = drone_id
                        break
            
            if available_drone:
                # 默认计划 - 有足够电量的无人机
                state["next_action"] = {
                    "action": "thermal_scan",
                    "drone_id": available_drone,
                    "parameters": {},
                    "priority": 1
                }
            else:
                # 没有可用无人机或电量不足
                state["next_action"] = None
                print("⚠️  没有可用的无人机或电量不足，无法执行任务")
        
        state["current_phase"] = "execution"
        self.memory.add_event("任务计划制定完成")
        
        return state
    
    def execute_action(self, state: RescueState) -> RescueState:
        """阶段4：执行具体行动"""
        
        print("🎯 阶段4：执行行动")
        
        if not state["next_action"]:
            state["current_phase"] = "evaluation"
            state["decision"] = "evaluate"  # Force evaluation when no action available
            message = "无可执行的行动，任务结束"
            state["messages"].append(AIMessage(content=message))
            self.memory.add_event(message)
            return state
        
        action = state["next_action"]
        action_name = action["action"]
        
        # 执行对应的工具
        if action_name == "thermal_scan":
            result = thermal_scan(drone_id=action["drone_id"])
        elif action_name == "move_to":
            result = move_to(
                drone_id=action["drone_id"],
                x=action["parameters"].get("x", 0),
                y=action["parameters"].get("y", 0)
            )
        elif action_name == "return_to_base":
            result = return_to_base(drone_id=action["drone_id"])
        else:
            result = {"success": False, "error": f"未知行动：{action_name}"}
        
        # 记录结果
        if result.get("success"):
            message = f"行动成功：{action_name} - {result.get('message', '')}"
            state["failure_count"] = 0  # Reset failure count on success
            
            # 如果发现幸存者，记录位置
            if action_name == "thermal_scan" and result.get("survivors_detected", 0) > 0:
                survivors = result.get("positions", [])
                state["survivors_found"].extend([
                    {"position": pos, "drone_id": action["drone_id"]} 
                    for pos in survivors
                ])
        else:
            message = f"行动失败：{action_name} - {result.get('error', '')}"
            state["failure_count"] += 1  # Increment failure count
        
        state["messages"].append(AIMessage(content=message))
        self.memory.add_event(message)
        
        return state
    
    def monitor_progress(self, state: RescueState) -> RescueState:
        """阶段5：监控任务进度"""
        
        print("📊 阶段5：进度监控")
        
        # 评估当前进度
        progress_prompt = f"""
        评估当前救援任务进度：
        
        任务目标：{state['mission_goal']}
        已发现幸存者：{len(state['survivors_found'])}
        可用无人机：{len(state['available_drones'])}
        连续失败次数：{state['failure_count']}
        
        判断是否需要：
        1. 继续当前计划 (continue) - 仅在没有连续失败时选择
        2. 重新规划 (replan) - 当有失败但还可以尝试时选择
        3. 结束任务 (evaluate) - 当连续失败过多或任务完成时选择
        
        注意：如果连续失败次数超过2次，应该选择 evaluate 结束任务。
        
        只回复一个词：continue/replan/evaluate
        """
        
        response = self.llm.invoke([HumanMessage(content=progress_prompt)])
        decision = response.content.strip().lower()
        
        # Force evaluation if too many failures
        if state["failure_count"] >= state["max_failures"]:
            decision = "evaluate"
            print(f"⚠️  连续失败 {state['failure_count']} 次，强制结束任务")
        
        if decision not in ["continue", "replan", "evaluate"]:
            decision = "evaluate"  # Default to evaluate instead of continue
        
        # Store the decision for should_continue method
        state["decision"] = decision
        
        # Clear next_action if we're not continuing with the current plan
        if decision != "continue":
            state["next_action"] = None
        
        return state
    
    def should_continue(self, state: RescueState) -> str:
        """决定工作流程的下一步"""
        return state.get("decision", "evaluate")
    
    def evaluate_results(self, state: RescueState) -> RescueState:
        """阶段6：评估任务结果"""
        
        print("✅ 阶段6：结果评估")
        
        summary = f"""
        任务完成总结：
        - 目标：{state['mission_goal']}
        - 发现幸存者：{len(state['survivors_found'])} 人
        - 参与无人机：{len(state['available_drones'])} 架
        - 执行步骤：{len(state['messages'])} 个
        """
        
        state["messages"].append(AIMessage(content=summary))
        state["current_phase"] = "completed"
        
        self.memory.add_event(f"任务完成：发现 {len(state['survivors_found'])} 名幸存者")
        
        return state
    
    def run_mission(self, mission_goal: str) -> Dict[str, Any]:
        """运行完整的救援任务工作流程"""
        
        print(f"🚁 启动 LangGraph 救援工作流程")
        print(f"📋 任务目标：{mission_goal}")
        print("=" * 50)
        
        # 初始化状态
        initial_state = RescueState(
            messages=[HumanMessage(content=f"开始救援任务：{mission_goal}")],
            mission_goal=mission_goal,
            available_drones=[],
            drone_status={},
            survivors_found=[],
            current_phase="analysis",
            next_action=None,
            decision=None,
            memory_context=[],
            failure_count=0,
            max_failures=3
        )
        
        # 运行工作流程
        try:
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": True,
                "mission_goal": mission_goal,
                "survivors_found": final_state["survivors_found"],
                "messages": [msg.content for msg in final_state["messages"]],
                "final_phase": final_state["current_phase"]
            }
        
        except Exception as e:
            error_msg = f"工作流程执行错误：{str(e)}"
            self.memory.add_event(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "mission_goal": mission_goal
            }


# 使用示例
if __name__ == "__main__":
    # 创建 LangGraph 工作流程
    workflow = LangGraphRescueWorkflow()
    
    # 运行救援任务
    result = workflow.run_mission("在灾区搜索并营救幸存者")
    
    print("\n" + "=" * 50)
    print("🎯 任务执行结果：")
    print(f"成功：{result['success']}")
    
    if result["success"]:
        print(f"发现幸存者：{len(result['survivors_found'])} 人")
        print("\n执行步骤：")
        for i, message in enumerate(result["messages"], 1):
            print(f"{i}. {message}")
    else:
        print(f"错误：{result['error']}")