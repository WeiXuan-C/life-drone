"""
LangGraph Workflow Implementation - Drone Rescue Mission Orchestration
Uses state graphs to manage complex rescue mission workflows
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
    thermal_scan, rescue_survivor, return_to_base
)


class RescueState(TypedDict):
    """Rescue mission state definition"""
    messages: List[BaseMessage]
    mission_goal: str
    available_drones: List[str]
    drone_status: Dict[str, Any]
    survivors_found: List[Dict[str, Any]]
    current_phase: str  # "planning", "execution", "monitoring", "completion"
    next_action: Optional[Dict[str, Any]]  # Changed from str to Dict for action details
    planned_actions: List[Dict[str, Any]]  # List of all planned actions
    action_index: int  # Current action index in planned_actions
    decision: Optional[str]  # Added for workflow decisions
    memory_context: List[str]
    failure_count: int  # Track consecutive failures
    max_failures: int  # Maximum allowed failures before giving up


class LangGraphRescueWorkflow:
    """
    LangGraph-based rescue workflow manager
    
    Workflow stages:
    1. Mission Analysis (analyze_mission)
    2. Resource Discovery (discover_resources) 
    3. Mission Planning (plan_mission)
    4. Execution Monitoring (execute_and_monitor)
    5. Results Evaluation (evaluate_results)
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
            self._create_tool_function("rescue_survivor", rescue_survivor),
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
        
        # Conditional edges: from action execution decide next step
        workflow.add_conditional_edges(
            "execute_action",
            self.should_continue,
            {
                "continue": "monitor_progress",
                "evaluate": "evaluate_results",
                "replan": "plan_mission"
            }
        )
        
        # Conditional edges: from progress monitoring decide next step
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
        """Stage 1: Analyze mission objectives and current situation"""
        
        print("🧠 Stage 1: Mission Analysis")
        
        # Get historical context
        recent_events = self.memory.get_recent_events(5)
        
        analysis_prompt = f"""
        As a rescue commander, analyze the following mission:
        
        Mission Objective: {state['mission_goal']}
        
        Recent Events:
        {chr(10).join(recent_events) if recent_events else "No historical records"}
        
        Please analyze:
        1. Mission urgency level and complexity
        2. Required resource types
        3. Potential challenges and risks
        4. Recommended execution strategy
        
        Reply in JSON format, including: analysis, urgency_level, required_resources, strategy
        """
        
        response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
        
        # Parse analysis results
        try:
            analysis = json.loads(response.content)
        except:
            analysis = {
                "analysis": response.content,
                "urgency_level": "medium",
                "required_resources": ["drones"],
                "strategy": "systematic_search"
            }
        
        # Update state
        state["current_phase"] = "resource_discovery"
        state["messages"].append(AIMessage(content=f"Mission analysis completed: {analysis['analysis']}"))
        
        self.memory.add_event(f"Mission analysis: {analysis['analysis']}")
        
        return state
    
    def discover_resources(self, state: RescueState) -> RescueState:
        """Stage 2: Discover available resources (drones, equipment, etc.)"""
        
        print("🔍 Stage 2: Resource Discovery")
        
        # Discover drones
        drone_result = discover_drones()
        
        if drone_result["success"]:
            state["available_drones"] = drone_result["drones"]
            
            # 获取每个无人机的状态
            drone_status = {}
            for drone_id in state["available_drones"]:
                status = get_battery_status(drone_id=drone_id)
                drone_status[drone_id] = status
            
            state["drone_status"] = drone_status
            
            message = f"Discovered {len(state['available_drones'])} drones"
            state["messages"].append(AIMessage(content=message))
            self.memory.add_event(message)
        
        state["current_phase"] = "mission_planning"
        return state
    
    def plan_mission(self, state: RescueState) -> RescueState:
        """Stage 3: Develop detailed mission execution plan"""
        
        print("📋 Stage 3: Mission Planning")
        
        planning_prompt = f"""
        Based on the following information, develop a rescue plan:
        
        Mission Objective: {state['mission_goal']}
        Available Drones: {state['available_drones']}
        Drone Status: {state['drone_status']}
        
        Available action types (only use the following actions):
        1. thermal_scan - Thermal imaging scan to search for survivors (requires at least 5% battery)
        2. move_to - Move drone to specified position (parameters: x, y coordinates)
        3. rescue_survivor - Rescue survivor at specified position (parameters: x, y coordinates, requires at least 10% battery)
        4. return_to_base - Return to base for charging
        
        Develop a multi-drone coordination plan, focusing on:
        1. First deploy healthy drones to search areas for scanning
        2. Immediately arrange rescue after discovering survivors
        3. Only drones with insufficient battery (<20%) should return to base
        4. Prioritize using move_to and thermal_scan for searching
        5. Ensure coverage of different search areas
        
        Develop action plans for each available drone, reply in JSON format:
        {{"actions": [
            {{"action": "move_to", "drone_id": "drone_A", "parameters": {{"x": 5, "y": 8}}, "priority": 1}}, 
            {{"action": "thermal_scan", "drone_id": "drone_A", "parameters": {{}}, "priority": 2}},
            {{"action": "move_to", "drone_id": "drone_B", "parameters": {{"x": 12, "y": 15}}, "priority": 1}},
            {{"action": "thermal_scan", "drone_id": "drone_B", "parameters": {{}}, "priority": 2}}
        ]}}
        
        Important: Prioritize search missions, only use return_to_base when battery is critically low
        Note: action field can only be thermal_scan, move_to, rescue_survivor, or return_to_base
        """
        
        response = self.llm.invoke([HumanMessage(content=planning_prompt)])
        
        try:
            plan = json.loads(response.content)
            state["planned_actions"] = plan.get("actions", [])
        except:
            # Create default plan for each available drone
            planned_actions = []
            search_positions = [(5, 8), (12, 15), (18, 6), (3, 12), (15, 3)]
            
            for i, drone_id in enumerate(state["available_drones"][:5]):
                drone_status = state["drone_status"].get(drone_id, {})
                battery = drone_status.get("battery_level", 0)
                
                if battery < 20:  # Only return to base if battery below 20%
                    # Low battery, return to base
                    planned_actions.append({
                        "action": "return_to_base",
                        "drone_id": drone_id,
                        "parameters": {},
                        "priority": 1
                    })
                else:
                    # Move to search position, scan, rescue survivors if found
                    if i < len(search_positions):
                        pos = search_positions[i]
                        planned_actions.extend([
                            {
                                "action": "move_to",
                                "drone_id": drone_id,
                                "parameters": {"x": pos[0], "y": pos[1]},
                                "priority": 1
                            },
                            {
                                "action": "thermal_scan",
                                "drone_id": drone_id,
                                "parameters": {},
                                "priority": 2
                            }
                            # Note: Rescue actions will be dynamically added after scanning discovers survivors
                        ])
            
            state["planned_actions"] = planned_actions
        
        # Set first batch of actions to execute
        state["next_action"] = state["planned_actions"][0] if state["planned_actions"] else None
        state["action_index"] = 0
        
        state["current_phase"] = "execution"
        self.memory.add_event(f"Mission plan completed, planning to execute {len(state['planned_actions'])} actions")
        
        return state
    
    def execute_action(self, state: RescueState) -> RescueState:
        """Stage 4: Execute specific actions"""
        
        print("🎯 Stage 4: Action Execution")
        
        if not state["next_action"]:
            state["current_phase"] = "evaluation"
            state["decision"] = "evaluate"  # Force evaluation when no action available
            message = "No executable actions, mission ended"
            state["messages"].append(AIMessage(content=message))
            self.memory.add_event(message)
            return state
        
        action = state["next_action"]
        action_name = action["action"]
        
        # Execute corresponding tool
        if action_name == "thermal_scan":
            result = thermal_scan(drone_id=action["drone_id"])
        elif action_name == "move_to":
            result = move_to(
                drone_id=action["drone_id"],
                x=action["parameters"].get("x", 0),
                y=action["parameters"].get("y", 0)
            )
        elif action_name == "rescue_survivor":
            result = rescue_survivor(
                drone_id=action["drone_id"],
                survivor_position=(
                    action["parameters"].get("x", 0),
                    action["parameters"].get("y", 0)
                )
            )
        elif action_name == "return_to_base":
            result = return_to_base(drone_id=action["drone_id"])
        else:
            result = {"success": False, "error": f"Unknown action: {action_name}"}
        
        # 记录结果
        if result.get("success"):
            message = f"行动成功：{action_name} ({action['drone_id']}) - {result.get('message', '')}"
            state["failure_count"] = 0  # Reset failure count on success
            
            # If survivors found, record positions and add rescue actions
            if action_name == "thermal_scan" and result.get("survivors_detected", 0) > 0:
                survivors = result.get("positions", [])
                for pos in survivors:
                    state["survivors_found"].append({
                        "position": pos, 
                        "drone_id": action["drone_id"],
                        "detected_time": result.get("scan_time", 0)
                    })
                    
                    # 动态添加救援行动到计划中
                    rescue_action = {
                        "action": "rescue_survivor",
                        "drone_id": action["drone_id"],
                        "parameters": {"x": pos[0], "y": pos[1]},
                        "priority": 3
                    }
                    
                    # 在当前行动之后插入救援行动
                    action_index = state.get("action_index", 0)
                    planned_actions = state.get("planned_actions", [])
                    planned_actions.insert(action_index + 1, rescue_action)
                    state["planned_actions"] = planned_actions
                    
                    print(f"🚨 Survivor found at {pos}, rescue action added")
            
            # If survivor rescue successful, update status
            elif action_name == "rescue_survivor":
                survivor_pos = (action["parameters"].get("x", 0), action["parameters"].get("y", 0))
                # Update survivor status to rescued
                for survivor in state["survivors_found"]:
                    if survivor["position"] == list(survivor_pos):
                        survivor["rescued"] = True
                        survivor["rescue_time"] = result.get("rescue_time", 0)
                        break
                print(f"✅ Successfully rescued survivor at {survivor_pos}")
        else:
            message = f"行动失败：{action_name} ({action['drone_id']}) - {result.get('error', '')}"
            state["failure_count"] += 1  # Increment failure count
        
        state["messages"].append(AIMessage(content=message))
        self.memory.add_event(message)
        
        # Move to next action
        action_index = state.get("action_index", 0) + 1
        planned_actions = state.get("planned_actions", [])
        
        if action_index < len(planned_actions):
            state["next_action"] = planned_actions[action_index]
            state["action_index"] = action_index
            state["decision"] = "continue"  # Continue executing next action
            print(f"📋 Preparing to execute next action ({action_index + 1}/{len(planned_actions)})")
        else:
            state["next_action"] = None
            state["action_index"] = len(planned_actions)
            state["decision"] = "evaluate"  # All actions completed, enter evaluation stage
            print("✅ All planned actions completed")
        
        return state
    
    def monitor_progress(self, state: RescueState) -> RescueState:
        """Stage 5: Monitor mission progress"""
        
        print("📊 Stage 5: Progress Monitoring")
        
        # Check if there are more actions to execute
        planned_actions = state.get("planned_actions", [])
        action_index = state.get("action_index", 0)
        has_more_actions = action_index < len(planned_actions)
        
        # Evaluate current progress
        progress_prompt = f"""
        Evaluate current rescue mission progress:
        
        Mission Objective: {state['mission_goal']}
        Survivors Found: {len(state['survivors_found'])}
        Available Drones: {len(state['available_drones'])}
        Consecutive Failures: {state['failure_count']}
        Remaining Planned Actions: {len(planned_actions) - action_index}
        
        Determine whether to:
        1. Continue current plan (continue) - Only when there are remaining actions and no consecutive failures
        2. Replan (replan) - When there are failures but can still try
        3. End mission (evaluate) - When too many consecutive failures or all actions completed
        
        Note: If consecutive failures exceed 2, should choose evaluate to end mission.
        If no remaining actions, should choose evaluate to end mission.
        
        Reply with only one word: continue/replan/evaluate
        """
        
        response = self.llm.invoke([HumanMessage(content=progress_prompt)])
        decision = response.content.strip().lower()
        
        # Force evaluation if too many failures or no more actions
        if state["failure_count"] >= state["max_failures"]:
            decision = "evaluate"
            print(f"⚠️  {state['failure_count']} consecutive failures, forcing mission end")
        elif not has_more_actions:
            decision = "evaluate"
            print("✅ All planned actions completed, ending mission")
        
        if decision not in ["continue", "replan", "evaluate"]:
            decision = "evaluate"  # Default to evaluate
        
        print(f"📋 Monitoring decision: {decision}")
        
        # Store the decision for should_continue method
        state["decision"] = decision
        
        # Clear next_action if we're not continuing with the current plan
        if decision != "continue":
            state["next_action"] = None
        
        return state
    
    def should_continue(self, state: RescueState) -> str:
        """Decide the next step of the workflow"""
        decision = state.get("decision", "evaluate")
        print(f"🔄 Workflow decision: {decision}")
        return decision
    
    def evaluate_results(self, state: RescueState) -> RescueState:
        """Stage 6: Evaluate mission results"""
        
        print("✅ Stage 6: Results Evaluation")
        
        summary = f"""
        Mission completion summary:
        - Objective: {state['mission_goal']}
        - Survivors found: {len(state['survivors_found'])} people
        - Participating drones: {len(state['available_drones'])} units
        - Execution steps: {len(state['messages'])} steps
        """
        
        state["messages"].append(AIMessage(content=summary))
        state["current_phase"] = "completed"
        
        self.memory.add_event(f"Mission completed: found {len(state['survivors_found'])} survivors")
        
        return state
    
    def run_mission(self, mission_goal: str) -> Dict[str, Any]:
        """Run complete rescue mission workflow"""
        
        print(f"🚁 Starting LangGraph rescue workflow")
        print(f"📋 Mission objective: {mission_goal}")
        print("=" * 50)
        
        # Initialize state
        initial_state = RescueState(
            messages=[HumanMessage(content=f"Starting rescue mission: {mission_goal}")],
            mission_goal=mission_goal,
            available_drones=[],
            drone_status={},
            survivors_found=[],
            current_phase="analysis",
            next_action=None,
            planned_actions=[],
            action_index=0,
            decision=None,
            memory_context=[],
            failure_count=0,
            max_failures=3
        )
        
        # Run workflow
        try:
            print("🔄 Starting workflow execution...")
            final_state = self.workflow.invoke(initial_state)
            
            print("✅ Workflow execution completed")
            return {
                "success": True,
                "mission_goal": mission_goal,
                "survivors_found": final_state["survivors_found"],
                "messages": [msg.content for msg in final_state["messages"]],
                "final_phase": final_state["current_phase"]
            }
        
        except Exception as e:
            error_msg = f"Workflow execution error: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Add more detailed error information
            import traceback
            traceback.print_exc()
            
            self.memory.add_event(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "mission_goal": mission_goal
            }


# Usage example
if __name__ == "__main__":
    # Create LangGraph workflow
    workflow = LangGraphRescueWorkflow()
    
    # Run rescue mission
    result = workflow.run_mission("Search and rescue survivors in disaster area")
    
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