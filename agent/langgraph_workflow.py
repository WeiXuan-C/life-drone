"""
LangGraph Workflow Implementation - Drone Rescue Mission Orchestration
Uses state graphs to manage complex rescue mission workflows

KEY FEATURES:
- Dynamic tool selection via LLM reasoning (no hardcoded workflows)
- Real-time tool discovery via MCP protocol
- Adaptive planning based on mission context
- No hardcoded drone IDs or action sequences

WORKFLOW STAGES:
1. Mission Analysis - Understand objectives and constraints
2. Resource Discovery - Use MCP to discover available drones/tools
3. Dynamic Planning - LLM reasons about next action based on context
4. Action Execution - Execute chosen tool via MCP
5. Progress Monitoring - Evaluate results and decide next step
6. Results Evaluation - Final mission assessment
"""

from typing import Dict, List, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
import json
import sys
import os

# Add parent directory to path for MCP client import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .memory import MissionMemory
from mcp_client.client import get_mcp_client


class RescueState(TypedDict):
    """Rescue mission state definition"""
    messages: List[BaseMessage]
    mission_goal: str
    available_drones: List[str]
    drone_status: Dict[str, Any]
    survivors_found: List[Dict[str, Any]]
    current_phase: str  # "planning", "execution", "monitoring", "completion"
    next_action: Optional[Dict[str, Any]]  # Next action determined by reasoning
    planned_actions: List[Dict[str, Any]]  # History of all actions taken
    decision: Optional[str]  # Workflow decision: continue/replan/evaluate
    memory_context: List[str]  # Recent context for reasoning
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
        
        # Initialize MCP client for direct tool calls
        self.mcp_client = get_mcp_client()
        
        # Connect to MCP server
        if not self.mcp_client.connect():
            raise RuntimeError("Failed to connect to MCP server. Please ensure MCP server is running.")
        
        # No tool wrappers needed! We'll call MCP client directly
        # This eliminates the double-wrapping problem
        
        # 构建状态图
        self.workflow = self._build_workflow()
    
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
        """Stage 2: Discover available resources via MCP discovery mechanism"""
        
        print("🔍 Stage 2: Dynamic Resource Discovery (via MCP)")
        
        # Use MCP discovery to find available drones (not hardcoded!)
        try:
            drone_result = self.mcp_client.call_tool("discover_drones")
            
            if drone_result.get("success") and "drones" in drone_result:
                state["available_drones"] = drone_result["drones"]
                
                print(f"✅ Discovered {len(state['available_drones'])} drones via MCP discovery")
                
                # Get battery status for each discovered drone
                drone_status = {}
                for drone_id in state["available_drones"]:
                    try:
                        status = self.mcp_client.call_tool("get_battery_status", drone_id=drone_id)
                        if status.get("success"):
                            drone_status[drone_id] = status
                    except Exception as e:
                        print(f"⚠️  Failed to get status for {drone_id}: {e}")
                
                state["drone_status"] = drone_status
                
                # Update memory context
                state["memory_context"].append(
                    f"Discovered {len(state['available_drones'])} drones: {state['available_drones']}"
                )
                
                message = f"Discovered {len(state['available_drones'])} drones via MCP discovery"
                state["messages"].append(AIMessage(content=message))
                self.memory.add_event(message)
            else:
                error_msg = "Failed to discover drones via MCP"
                print(f"❌ {error_msg}")
                state["messages"].append(AIMessage(content=error_msg))
                state["memory_context"].append(error_msg)
                
        except Exception as e:
            error_msg = f"Exception during resource discovery: {str(e)}"
            print(f"❌ {error_msg}")
            state["messages"].append(AIMessage(content=error_msg))
            state["memory_context"].append(error_msg)
        
        state["current_phase"] = "mission_planning"
        return state
    
    def plan_mission(self, state: RescueState) -> RescueState:
        """Stage 3: Use reasoning to determine next action dynamically"""
        
        print("📋 Stage 3: Dynamic Mission Planning (Reasoning-based)")
        
        # Get available tools from MCP discovery
        available_tools = self.mcp_client.get_available_tools()
        tool_descriptions = []
        
        if available_tools and "tools" in available_tools:
            for tool in available_tools["tools"]:
                tool_desc = f"- {tool['name']}: {tool.get('description', 'No description')}"
                if 'inputSchema' in tool and 'properties' in tool['inputSchema']:
                    params = ', '.join(tool['inputSchema']['properties'].keys())
                    tool_desc += f" (params: {params})"
                tool_descriptions.append(tool_desc)
        
        # Build reasoning prompt with discovered tools
        planning_prompt = f"""
        You are a rescue mission commander. Use reasoning to determine the NEXT SINGLE ACTION.
        
        Mission Objective: {state['mission_goal']}
        Available Drones: {state['available_drones']}
        Drone Status: {state['drone_status']}
        Survivors Found So Far: {len(state['survivors_found'])}
        Previous Actions Taken: {len(state.get('planned_actions', []))}
        
        Available Tools (discovered via MCP):
        {chr(10).join(tool_descriptions) if tool_descriptions else "No tools available"}
        
        Recent Context:
        {chr(10).join(state.get('memory_context', [])[-3:]) if state.get('memory_context') else "No previous context"}
        
        Based on the current situation, reason about:
        1. What is the most important next step to achieve the mission goal?
        2. Which tool should be used and why?
        3. Which drone should execute this action (consider battery levels)?
        4. What parameters are needed for this tool?
        
        Reply in JSON format with your reasoning and the next action:
        {{
            "reasoning": "Explain why this action is chosen",
            "tool_name": "exact_tool_name_from_mcp",
            "drone_id": "selected_drone_id",
            "parameters": {{"param1": "value1"}},
            "expected_outcome": "What you expect to happen"
        }}
        
        Important: Choose ONE action at a time. Do not plan multiple steps ahead.
        """
        
        response = self.llm.invoke([HumanMessage(content=planning_prompt)])
        
        try:
            plan = json.loads(response.content)
            
            # Store reasoning in memory
            reasoning = plan.get("reasoning", "No reasoning provided")
            self.memory.add_event(f"Reasoning: {reasoning}")
            
            # Create single action from reasoning
            next_action = {
                "tool_name": plan.get("tool_name"),
                "drone_id": plan.get("drone_id"),
                "parameters": plan.get("parameters", {}),
                "reasoning": reasoning,
                "expected_outcome": plan.get("expected_outcome", "")
            }
            
            state["next_action"] = next_action
            state["planned_actions"].append(next_action)  # Track all actions taken
            
            print(f"🧠 Reasoning: {reasoning}")
            print(f"🎯 Next action: {next_action['tool_name']} with {next_action['drone_id']}")
            
        except Exception as e:
            print(f"⚠️  Failed to parse reasoning response: {e}")
            # Fallback: ask for tool discovery
            state["next_action"] = {
                "tool_name": "discover_drones",
                "drone_id": None,
                "parameters": {},
                "reasoning": "Fallback to discovery",
                "expected_outcome": "Get available resources"
            }
        
        state["current_phase"] = "execution"
        self.memory.add_event(f"Planned next action: {state['next_action']['tool_name']}")
        
        return state
    
    def execute_action(self, state: RescueState) -> RescueState:
        """Stage 4: Execute action via dynamic MCP tool call"""
        
        print("🎯 Stage 4: Dynamic Action Execution (via MCP)")
        
        if not state["next_action"]:
            state["current_phase"] = "evaluation"
            state["decision"] = "evaluate"
            message = "No action to execute, moving to evaluation"
            state["messages"].append(AIMessage(content=message))
            self.memory.add_event(message)
            return state
        
        action = state["next_action"]
        tool_name = action.get("tool_name")
        drone_id = action.get("drone_id")
        parameters = action.get("parameters", {})
        
        print(f"🔧 Executing tool: {tool_name}")
        print(f"📋 Parameters: {parameters}")
        
        # Dynamic tool call via MCP client
        try:
            # Build parameters for MCP call
            mcp_params = {}
            
            # Add drone_id if present
            if drone_id:
                mcp_params["drone_id"] = drone_id
            
            # Merge additional parameters
            mcp_params.update(parameters)
            
            # Call MCP tool dynamically
            result = self.mcp_client.call_tool(tool_name, **mcp_params)
            
            # Process result
            if result.get("success"):
                message = f"✅ Tool {tool_name} succeeded: {result.get('message', '')}"
                state["failure_count"] = 0
                
                # Handle tool-specific results
                # For thermal_scan: record survivors
                if "survivors_detected" in result and result["survivors_detected"] > 0:
                    survivors = result.get("positions", [])
                    for pos in survivors:
                        state["survivors_found"].append({
                            "position": pos,
                            "drone_id": drone_id,
                            "detected_time": result.get("scan_time", 0),
                            "rescued": False
                        })
                    print(f"🚨 Found {len(survivors)} survivors!")
                    
                    # Update memory context for next reasoning
                    state["memory_context"].append(
                        f"Discovered {len(survivors)} survivors at positions {survivors}"
                    )
                
                # For rescue_survivor: mark as rescued
                elif tool_name == "rescue_survivor" and result.get("success"):
                    survivor_pos = [parameters.get("x"), parameters.get("y")]
                    for survivor in state["survivors_found"]:
                        if survivor["position"] == survivor_pos:
                            survivor["rescued"] = True
                            survivor["rescue_time"] = result.get("rescue_time", 0)
                            break
                    print(f"✅ Rescued survivor at {survivor_pos}")
                    
                    state["memory_context"].append(
                        f"Successfully rescued survivor at {survivor_pos}"
                    )
                
                # For discover_drones: update available drones
                elif tool_name == "discover_drones":
                    if "drones" in result:
                        state["available_drones"] = result["drones"]
                        state["memory_context"].append(
                            f"Discovered {len(result['drones'])} drones: {result['drones']}"
                        )
                
                # For battery status: update drone status
                elif tool_name == "get_battery_status":
                    if drone_id and "battery_level" in result:
                        if "drone_status" not in state:
                            state["drone_status"] = {}
                        state["drone_status"][drone_id] = result
                        state["memory_context"].append(
                            f"Drone {drone_id} battery: {result['battery_level']}%"
                        )
                
            else:
                message = f"❌ Tool {tool_name} failed: {result.get('error', 'Unknown error')}"
                state["failure_count"] += 1
                state["memory_context"].append(f"Failed: {tool_name} - {result.get('error', '')}")
            
            state["messages"].append(AIMessage(content=message))
            self.memory.add_event(message)
            
        except Exception as e:
            error_msg = f"❌ Exception executing {tool_name}: {str(e)}"
            print(error_msg)
            state["messages"].append(AIMessage(content=error_msg))
            state["memory_context"].append(error_msg)
            state["failure_count"] += 1
            self.memory.add_event(error_msg)
        
        # Clear next_action to force re-planning
        state["next_action"] = None
        state["decision"] = "continue"  # Continue to monitoring/re-planning
        
        return state
    
    def monitor_progress(self, state: RescueState) -> RescueState:
        """Stage 5: Monitor progress and decide next step via reasoning"""
        
        print("📊 Stage 5: Progress Monitoring & Reasoning")
        
        # Evaluate current mission state
        progress_prompt = f"""
        You are monitoring a rescue mission. Analyze the current state and decide the next step.
        
        Mission Objective: {state['mission_goal']}
        Available Drones: {state['available_drones']}
        Survivors Found: {len(state['survivors_found'])}
        Survivors Rescued: {sum(1 for s in state['survivors_found'] if s.get('rescued', False))}
        Consecutive Failures: {state['failure_count']}
        Actions Taken: {len(state.get('planned_actions', []))}
        
        Recent Context:
        {chr(10).join(state.get('memory_context', [])[-5:]) if state.get('memory_context') else "No context"}
        
        Analyze the situation and decide:
        1. Should we continue with a new action? (if mission not complete and no critical failures)
        2. Should we replan? (if strategy needs adjustment)
        3. Should we evaluate and end? (if mission complete or too many failures)
        
        Reply in JSON format:
        {{
            "analysis": "Your analysis of current situation",
            "decision": "continue/replan/evaluate",
            "reason": "Why you made this decision"
        }}
        
        Decision criteria:
        - "continue": Mission ongoing, need more actions to achieve goal
        - "replan": Current approach not working, need new strategy
        - "evaluate": Mission complete (all survivors rescued) OR too many failures (>= {state['max_failures']})
        """
        
        response = self.llm.invoke([HumanMessage(content=progress_prompt)])
        
        try:
            analysis = json.loads(response.content)
            decision = analysis.get("decision", "evaluate").lower()
            reason = analysis.get("reason", "No reason provided")
            
            print(f"🧠 Analysis: {analysis.get('analysis', '')}")
            print(f"📋 Decision: {decision} - {reason}")
            
            # Override decision if failure threshold exceeded
            if state["failure_count"] >= state["max_failures"]:
                decision = "evaluate"
                reason = f"Exceeded maximum failures ({state['max_failures']})"
                print(f"⚠️  Forcing evaluation: {reason}")
            
            # Store decision
            state["decision"] = decision
            state["memory_context"].append(f"Monitoring decision: {decision} - {reason}")
            self.memory.add_event(f"Progress monitoring: {decision} - {reason}")
            
        except Exception as e:
            print(f"⚠️  Failed to parse monitoring response: {e}")
            # Default to replan if uncertain
            state["decision"] = "replan"
            state["memory_context"].append("Monitoring failed, defaulting to replan")
        
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
        """Run complete rescue mission workflow with dynamic reasoning"""
        
        print(f"🚁 Starting LangGraph rescue workflow (Reasoning-based)")
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