"""
Rescue Agent - Central AI Agent for LifeDrone System
This agent MUST use LangGraph workflow for all operations
"""

from typing import Dict, List, Any, Optional
from langchain_ollama import ChatOllama
from .langgraph_workflow import LangGraphRescueWorkflow
from .memory import MissionMemory
import json


class RescueAgent:
    """
    Central Rescue Agent that coordinates all LifeDrone operations
    MANDATORY: All operations must go through LangGraph workflow
    """
    
    def __init__(self, model_name: str = "qwen2", base_url: str = "http://localhost:11434"):
        """Initialize Rescue Agent with mandatory LangGraph workflow"""
        
        # Initialize Ollama LLM
        self.llm = ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0.1
        )
        
        # MANDATORY: Initialize LangGraph workflow
        self.langgraph_workflow = LangGraphRescueWorkflow(model_name, base_url)
        
        # Initialize memory system
        self.memory = MissionMemory()
    
    def process_ui_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process request from Enhanced Tkinter UI
        MANDATORY: All requests must go through LangGraph workflow
        
        Flow: UI Request → RescueAgent → Ollama → LangGraph → MCP
        """
        
        print(f"📥 Processing UI request: {request.get('type', 'unknown')}")
        
        # Log the request
        self.memory.add_event(f"UI Request: {request}")
        
        # Extract mission goal from UI request
        mission_goal = self._extract_mission_goal(request)
        
        if not mission_goal:
            return {
                "success": False,
                "error": "Invalid request: No mission goal could be extracted",
                "agent_id": self.agent_id
            }
        
        # MANDATORY: Route through LangGraph workflow
        try:
            print(f"🔄 Routing to LangGraph workflow...")
            workflow_result = self.langgraph_workflow.run_mission(mission_goal)
            
            # Process workflow result
            response = self._process_workflow_result(workflow_result, request)
            
            # Update agent state
            self.current_mission = mission_goal if workflow_result.get("success") else None
            self.status = "active" if workflow_result.get("success") else "ready"
            
            return response
            
        except Exception as e:
            error_msg = f"LangGraph workflow error: {str(e)}"
            self.memory.add_event(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "agent_id": self.agent_id
            }
    
    def _extract_mission_goal(self, request: Dict[str, Any]) -> Optional[str]:
        """Extract mission goal from UI request"""
        
        request_type = request.get("type", "")
        
        if request_type == "start_mission":
            return request.get("mission_goal", "Execute rescue mission")
        
        elif request_type == "search_area":
            area = request.get("area", {})
            return f"Search area at coordinates ({area.get('x', 0)}, {area.get('y', 0)})"
        
        elif request_type == "rescue_survivor":
            position = request.get("position", {})
            return f"Rescue survivor at position ({position.get('x', 0)}, {position.get('y', 0)})"
        
        elif request_type == "patrol_area":
            return "Patrol designated area for survivors"
        
        elif request_type == "emergency_response":
            return f"Emergency response: {request.get('details', 'Unknown emergency')}"
        
        else:
            # Generic mission goal
            return f"Process UI request: {request_type}"
    
    def _process_workflow_result(self, workflow_result: Dict[str, Any], 
                               original_request: Dict[str, Any]) -> Dict[str, Any]:
        """Process LangGraph workflow result for UI response"""
        
        if workflow_result.get("success"):
            return {
                "success": True,
                "agent_id": self.agent_id,
                "mission_goal": workflow_result["mission_goal"],
                "survivors_found": workflow_result.get("survivors_found", []),
                "execution_steps": workflow_result.get("messages", []),
                "final_phase": workflow_result.get("final_phase", "completed"),
                "workflow_used": "LangGraph",
                "original_request": original_request
            }
        else:
            return {
                "success": False,
                "agent_id": self.agent_id,
                "error": workflow_result.get("error", "Unknown workflow error"),
                "mission_goal": workflow_result.get("mission_goal", "Unknown"),
                "workflow_used": "LangGraph",
                "original_request": original_request
            }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "current_mission": self.current_mission,
            "langgraph_active": True,  # Always true - mandatory
            "memory_events": len(self.memory.get_recent_events(10)),
            "ollama_connected": self._check_ollama_connection()
        }
    
    def _check_ollama_connection(self) -> bool:
        """Check if Ollama connection is active"""
        try:
            # Simple test query
            response = self.llm.invoke("test")
            return True
        except Exception:
            return False
    
    def shutdown(self):
        """Shutdown agent gracefully"""
        print(f"🔄 Shutting down RescueAgent {self.agent_id}")
        self.status = "shutdown"
        self.current_mission = None
        self.memory.add_event("RescueAgent shutdown")


# Global rescue agent instance
_rescue_agent_instance = None


def get_rescue_agent() -> RescueAgent:
    """Get global rescue agent instance (singleton pattern)"""
    global _rescue_agent_instance
    
    if _rescue_agent_instance is None:
        _rescue_agent_instance = RescueAgent()
    
    return _rescue_agent_instance


def initialize_rescue_agent(model_name: str = "qwen2", 
                          base_url: str = "http://localhost:11434") -> RescueAgent:
    """Initialize rescue agent with specific configuration"""
    global _rescue_agent_instance
    
    _rescue_agent_instance = RescueAgent(model_name, base_url)
    return _rescue_agent_instance


# Usage example
if __name__ == "__main__":
    # Test the rescue agent
    agent = RescueAgent()
    
    # Test UI request processing
    test_request = {
        "type": "start_mission",
        "mission_goal": "Search and rescue survivors in disaster area",
        "area": {"x": 10, "y": 15},
        "priority": "high"
    }
    
    result = agent.process_ui_request(test_request)
    print(f"🎯 Test result: {result}")