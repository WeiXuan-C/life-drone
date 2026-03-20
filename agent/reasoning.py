"""
AI Reasoning Module for Disaster Rescue Drone System

This module implements AI reasoning using Ollama Qwen2 LLM.
It follows the ReAct pattern: Thought → Action → Observation → Reflection

The RescueAgent class coordinates drone operations through MCP tools
and maintains mission context through the memory system.

Key Features:
- ReAct reasoning pattern implementation
- Integration with Ollama Qwen2 model
- MCP tool calling for drone operations
- Mission memory integration
- Structured decision making process
"""

import json
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from langchain_community.llms import Ollama
    from langchain_community.chat_models import ChatOllama
    LANGCHAIN_AVAILABLE = True
    
    # Try to import LangGraph
    try:
        from .langgraph_workflow import LangGraphRescueWorkflow
        LANGGRAPH_AVAILABLE = True
    except ImportError:
        LANGGRAPH_AVAILABLE = False
        print("Warning: LangGraph workflow not available. Using basic ReAct pattern.")
        
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LANGGRAPH_AVAILABLE = False
    print("Warning: LangChain not available. Using direct Ollama API calls.")

from .memory import MissionMemory


class ActionType(Enum):
    """Available action types for the rescue agent."""
    DISCOVER_DRONES = "discover_drones"
    GET_BATTERY_STATUS = "get_battery_status"
    MOVE_TO = "move_to"
    THERMAL_SCAN = "thermal_scan"
    RETURN_TO_BASE = "return_to_base"
    ANALYZE_SITUATION = "analyze_situation"


@dataclass
class ReasoningStep:
    """Represents a single step in the ReAct reasoning process."""
    thought: str
    action: str
    observation: str
    reflection: str
    timestamp: str


class RescueAgent:
    """
    AI-powered rescue command agent using ReAct reasoning pattern.
    
    This agent coordinates drone operations for disaster rescue missions.
    It uses Ollama Qwen2 for reasoning and calls MCP tools for drone control.
    
    The reasoning process follows:
    1. Analyze current mission state and goal
    2. Think about the best next action
    3. Execute action through MCP tool
    4. Observe results and reflect
    5. Update mission memory
    """
    
    def __init__(self, 
                 model_name: str = "qwen2",
                 base_url: str = "http://localhost:11434",
                 mcp_server_url: str = "http://localhost:8000",
                 use_langgraph: bool = True):
        """
        Initialize the rescue agent.
        
        Args:
            model_name: Ollama model name (default: qwen2)
            base_url: Ollama server URL
            mcp_server_url: MCP server URL for drone tools
            use_langgraph: Whether to use LangGraph workflow (default: True)
        """
        self.model_name = model_name
        self.base_url = base_url
        self.mcp_server_url = mcp_server_url
        self.memory = MissionMemory()
        self.reasoning_history: List[ReasoningStep] = []
        self.use_langgraph = use_langgraph and LANGGRAPH_AVAILABLE
        
        # Initialize LangGraph workflow if available
        if self.use_langgraph:
            try:
                self.langgraph_workflow = LangGraphRescueWorkflow(model_name, base_url)
                print("✅ LangGraph workflow enabled")
            except Exception as e:
                print(f"⚠️  LangGraph initialization failed, using basic ReAct mode: {e}")
                self.use_langgraph = False
                self.langgraph_workflow = None
        else:
            self.langgraph_workflow = None
            if not LANGGRAPH_AVAILABLE:
                print("ℹ️  LangGraph not available, using basic ReAct mode")
        
        # Initialize LLM
        if LANGCHAIN_AVAILABLE:
            self.llm = ChatOllama(
                model=model_name,
                base_url=base_url,
                temperature=0.1  # Low temperature for consistent reasoning
            )
        else:
            self.llm = None
        
        # Build system prompt dynamically (will be updated with discovered tools)
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """
        Build system prompt dynamically with tools discovered from MCP server.
        
        Returns:
            System prompt string with current available tools
        """
        # Try to get tools from MCP client
        tool_descriptions = []
        
        try:
            from mcp_client.client import get_mcp_client
            
            mcp_client = get_mcp_client()
            
            if mcp_client.connect():
                tools_info = mcp_client.get_available_tools()
                
                if tools_info and "tools" in tools_info:
                    for tool in tools_info["tools"]:
                        # Build parameter list
                        params = ""
                        if "inputSchema" in tool and "properties" in tool["inputSchema"]:
                            param_names = list(tool["inputSchema"]["properties"].keys())
                            params = f"({', '.join(param_names)})"
                        
                        # Add tool description
                        description = tool.get("description", "No description available")
                        tool_descriptions.append(f"- {tool['name']}{params}: {description}")
        
        except Exception as e:
            print(f"⚠️  Could not discover MCP tools for system prompt: {e}")
            # Fallback to generic description
            tool_descriptions = [
                "- Tools will be discovered dynamically from MCP server",
                "- Use discover_drones() to see available drones",
                "- Use get_battery_status(drone_id) to check battery",
                "- Use move_to(drone_id, x, y) to move drones",
                "- Use thermal_scan(drone_id) to scan for survivors"
            ]
        
        # Build complete system prompt
        tools_section = "\n".join(tool_descriptions) if tool_descriptions else "No tools available"
        
        return f"""
You are a Rescue Command Agent coordinating drone operations in a disaster zone.

Your mission: Coordinate a fleet of drones to locate and rescue survivors efficiently.

Available MCP Tools (dynamically discovered):
{tools_section}

Reasoning Process:
1. THOUGHT: Analyze the situation and decide what to do next
2. ACTION: Choose and execute an MCP tool
3. OBSERVATION: Review the results
4. REFLECTION: Learn from the outcome and plan next steps

Key Priorities:
- Battery management (recall drones with <20% battery)
- Systematic area coverage
- Efficient survivor rescue
- Drone safety and coordination

Always think step by step and explain your reasoning clearly.
"""
    
    def _call_ollama_direct(self, prompt: str) -> str:
        """
        Direct API call to Ollama when LangChain is not available.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Model response text
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"Error: Ollama API returned status {response.status_code}"
        
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    def _generate_response(self, prompt: str) -> str:
        """
        Generate response using available LLM interface.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Model response text
        """
        if LANGCHAIN_AVAILABLE and self.llm:
            try:
                response = self.llm.invoke(prompt)
                return response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                print(f"LangChain error, falling back to direct API: {e}")
                return self._call_ollama_direct(prompt)
        else:
            return self._call_ollama_direct(prompt)
    
    def analyze_mission(self, goal: str) -> Dict[str, Any]:
        """
        Analyze the current mission state and generate reasoning.
        
        Args:
            goal: The mission objective
            
        Returns:
            Dictionary containing analysis and recommended actions
        """
        # Get recent mission context
        recent_events = self.memory.get_recent_events(10)
        mission_summary = self.memory.get_mission_summary()
        
        # Build context prompt
        context_prompt = f"""
{self.system_prompt}

MISSION GOAL: {goal}

RECENT MISSION EVENTS:
{chr(10).join(recent_events) if recent_events else "No recent events"}

MISSION SUMMARY:
Duration: {mission_summary['mission_duration']}
Total Events: {mission_summary['total_events']}

Based on this context, analyze the situation and recommend the next action.
Follow the THOUGHT → ACTION → OBSERVATION format.

THOUGHT: What should I do next and why?
ACTION: Which MCP tool should I call and with what parameters?
"""
        
        # Generate reasoning
        response = self._generate_response(context_prompt)
        
        # Parse the response to extract thought and action
        analysis = self._parse_reasoning_response(response)
        
        return {
            "goal": goal,
            "context": recent_events,
            "reasoning": response,
            "recommended_action": analysis.get("action"),
            "thought_process": analysis.get("thought")
        }
    
    def _parse_reasoning_response(self, response: str) -> Dict[str, str]:
        """
        Parse the LLM response to extract structured reasoning components.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Dictionary with parsed thought and action components
        """
        result = {"thought": "", "action": ""}
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("THOUGHT:"):
                current_section = "thought"
                result["thought"] = line.replace("THOUGHT:", "").strip()
            elif line.startswith("ACTION:"):
                current_section = "action"
                result["action"] = line.replace("ACTION:", "").strip()
            elif current_section and line:
                result[current_section] += " " + line
        
        return result
    
    def plan_actions(self, goal: str, available_drones: List[str]) -> List[Dict[str, Any]]:
        """
        Plan a sequence of actions to achieve the mission goal.
        
        Args:
            goal: Mission objective
            available_drones: List of available drone IDs
            
        Returns:
            List of planned actions with priorities
        """
        planning_prompt = f"""
{self.system_prompt}

MISSION GOAL: {goal}
AVAILABLE DRONES: {', '.join(available_drones)}

Create a step-by-step action plan to achieve this goal efficiently.
Consider:
1. Battery levels of all drones
2. Area coverage strategy
3. Survivor rescue priorities
4. Drone coordination

Provide a prioritized list of actions in this format:
1. ACTION: action_name(parameters) - REASON: why this action
2. ACTION: action_name(parameters) - REASON: why this action
...
"""
        
        response = self._generate_response(planning_prompt)
        self.memory.add_event(f"Generated action plan for goal: {goal}")
        
        # Parse the plan (simplified parsing)
        actions = []
        lines = response.split('\n')
        
        for line in lines:
            if line.strip() and ('ACTION:' in line or line[0].isdigit()):
                actions.append({
                    "description": line.strip(),
                    "priority": len(actions) + 1
                })
        
        return actions
    
    def call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool via real MCP client (no hardcoded simulations).
        
        Args:
            tool_name: Name of the MCP tool to call
            parameters: Parameters for the tool
            
        Returns:
            Tool execution result from real MCP server
        """
        self.memory.add_event(f"Calling MCP tool: {tool_name} with params: {parameters}")
        
        try:
            # Import and use real MCP client
            from mcp_client.client import get_mcp_client
            
            mcp_client = get_mcp_client()
            
            # Ensure connection
            if not mcp_client.connect():
                error_msg = "Failed to connect to MCP server"
                self.memory.add_event(f"MCP connection failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
            # Call tool dynamically via MCP client
            result = mcp_client.call_tool(tool_name, **parameters)
            
            # Log the result
            if result.get("success"):
                self.memory.add_event(f"MCP tool {tool_name} succeeded: {result.get('message', 'OK')}")
            else:
                self.memory.add_event(f"MCP tool {tool_name} failed: {result.get('error', 'Unknown error')}")
            
            return result
        
        except Exception as e:
            error_msg = f"Error calling MCP tool {tool_name}: {str(e)}"
            self.memory.add_event(error_msg)
            return {"success": False, "error": error_msg}
    
    def update_memory(self, event: str) -> None:
        """
        Update mission memory with a new event.
        
        Args:
            event: Event description to add to memory
        """
        self.memory.add_event(event)
    
    def execute_mission_with_langgraph(self, goal: str) -> Dict[str, Any]:
        """
        Execute complete mission using LangGraph workflow
        
        Args:
            goal: Mission objective
            
        Returns:
            Mission execution results
        """
        if not self.use_langgraph or not self.langgraph_workflow:
            return {
                "success": False,
                "error": "LangGraph 工作流程不可用",
                "fallback": "使用基础推理模式"
            }
        
        print(f"\n🚀 Using LangGraph to execute mission: {goal}")
        
        try:
            result = self.langgraph_workflow.run_mission(goal)
            
            # 将结果同步到本地内存
            if result.get("success"):
                for message in result.get("messages", []):
                    self.memory.add_event(f"LangGraph: {message}")
            
            return result
        
        except Exception as e:
            error_msg = f"LangGraph 执行失败：{str(e)}"
            self.memory.add_event(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "goal": goal
            }
    
    def execute_reasoning_cycle(self, goal: str, use_langgraph: bool = None) -> Dict[str, Any]:
        """
        Execute a complete ReAct reasoning cycle.
        
        Args:
            goal: The mission goal to work towards
            use_langgraph: Override the default LangGraph usage setting
            
        Returns:
            Dictionary containing the complete reasoning cycle results
        """
        # 决定使用哪种推理模式
        should_use_langgraph = (use_langgraph if use_langgraph is not None 
                               else self.use_langgraph)
        
        if should_use_langgraph and self.langgraph_workflow:
            print(f"\n🧠 Using LangGraph workflow to execute mission")
            return self.execute_mission_with_langgraph(goal)
        else:
            print(f"\n🧠 Using basic ReAct reasoning mode to execute mission")
            return self._execute_basic_reasoning_cycle(goal)
    
    def _execute_basic_reasoning_cycle(self, goal: str) -> Dict[str, Any]:
        """
        Execute a complete ReAct reasoning cycle using dynamic tool calling.
        
        Args:
            goal: The mission goal to work towards
            
        Returns:
            Dictionary containing the complete reasoning cycle results
        """
        print(f"\n🧠 Starting reasoning cycle for goal: {goal}")
        
        # Step 1: Analyze mission
        analysis = self.analyze_mission(goal)
        thought = analysis["thought_process"]
        
        print(f"💭 THOUGHT: {thought}")
        
        # Step 2: Execute action based on LLM recommendation
        action_description = analysis["recommended_action"]
        print(f"🎯 ACTION: {action_description}")
        
        # Parse action from LLM response and execute dynamically
        # The LLM should provide tool name and parameters
        observation = self._parse_and_execute_action(action_description)
        
        print(f"👁️ OBSERVATION: {observation}")
        
        # Step 3: Reflect on results
        reflection_prompt = f"""
Based on this action result: {observation}
What should be the next priority? What did we learn?
Keep the reflection brief and actionable.
"""
        
        reflection = self._generate_response(reflection_prompt)
        print(f"🤔 REFLECTION: {reflection}")
        
        # Record reasoning step
        reasoning_step = ReasoningStep(
            thought=thought,
            action=action_description,
            observation=str(observation),
            reflection=reflection,
            timestamp=self.memory._get_mission_time()
        )
        
        self.reasoning_history.append(reasoning_step)
        
        return {
            "goal": goal,
            "thought": thought,
            "action": action_description,
            "observation": observation,
            "reflection": reflection,
            "success": observation.get("success", True)
        }
    
    def _parse_and_execute_action(self, action_description: str) -> Dict[str, Any]:
        """
        Parse action description from LLM and execute via MCP dynamically.
        
        Args:
            action_description: Natural language action description from LLM
            
        Returns:
            Action execution result
        """
        # Ask LLM to convert natural language to structured tool call
        parse_prompt = f"""
Convert this action description into a structured tool call:
"{action_description}"

Reply in JSON format:
{{
    "tool_name": "exact_mcp_tool_name",
    "parameters": {{"param1": "value1"}}
}}

Available tools: discover_drones, get_battery_status, move_to, thermal_scan, 
                rescue_survivor, return_to_base
"""
        
        try:
            response = self._generate_response(parse_prompt)
            
            # Try to parse JSON response
            import json
            tool_call = json.loads(response)
            
            tool_name = tool_call.get("tool_name")
            parameters = tool_call.get("parameters", {})
            
            # Execute via MCP dynamically
            return self.call_mcp_tool(tool_name, parameters)
            
        except Exception as e:
            # Fallback: try to extract tool name from description
            action_lower = action_description.lower()
            
            if "discover" in action_lower and "drone" in action_lower:
                return self.call_mcp_tool("discover_drones", {})
            elif "battery" in action_lower or "status" in action_lower:
                # Need to get drone_id from available drones
                return self.call_mcp_tool("get_mission_status", {})
            else:
                return {
                    "success": False,
                    "error": f"Could not parse action: {action_description}",
                    "message": "Action parsing failed"
                }


# Example usage and testing
if __name__ == "__main__":
    # Create rescue agent
    agent = RescueAgent()
    
    print("🚁 Rescue Command Agent Initialized")
    print("=" * 50)
    
    # Example mission goals
    goals = [
        "Discover all available drones and check their status",
        "Scan the disaster area for survivors",
        "Coordinate drone battery management"
    ]
    
    # Execute reasoning cycles for each goal
    for goal in goals:
        try:
            result = agent.execute_reasoning_cycle(goal)
            print(f"✅ Goal completed: {result['success']}")
        except Exception as e:
            print(f"❌ Error executing goal: {e}")
        
        print("-" * 30)
    
    # Display mission summary
    print("\n📊 Mission Summary:")
    summary = agent.memory.get_mission_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")