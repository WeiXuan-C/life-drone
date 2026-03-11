# 🏗️ Agentic AI Disaster Rescue System - Technical Architecture Documentation

## System Overview

The Agentic AI Disaster Rescue Drone System implements a sophisticated multi-layer architecture that combines AI reasoning, persistent memory, standardized tool interfaces, and interactive simulation. The system follows a clear data flow pipeline from AI decision-making to drone execution.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Ollama Qwen2   │───▶│  LangGraph Agent │───▶│ Mission Memory  │
│     (LLM)       │    │   (Reasoning)    │    │  (Persistence)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    Mesa UI      │◀───│   MCP Server     │───▶│ Drone Simulation│
│  (Dashboard)    │    │  (Tool Gateway)  │    │  (Mesa Agents)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 1. LangGraph Agent (AI Reasoning Engine)

### Implementation Location
- **Primary File**: `agent/reasoning.py`
- **Supporting Files**: `agent/memory.py` (integration)

### Core Classes & Functions

#### `RescueAgent` Class
```python
class RescueAgent:
    def __init__(self, model_name="qwen2", base_url="http://localhost:11434")
    def analyze_mission(self, goal: str) -> Dict[str, Any]
    def execute_reasoning_cycle(self, goal: str) -> Dict[str, Any]
    def plan_actions(self, goal: str, available_drones: List[str]) -> List[Dict[str, Any]]
    def call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]
```

#### Key Functions
- **`analyze_mission()`**: Processes mission goals and generates reasoning context
- **`execute_reasoning_cycle()`**: Implements ReAct pattern (Thought→Action→Observation→Reflection)
- **`plan_actions()`**: Creates strategic action sequences for mission objectives
- **`call_mcp_tool()`**: Interfaces with MCP server for drone operations

### How It Works
The LangGraph Agent implements the **ReAct reasoning pattern**:

1. **THOUGHT**: Analyzes current mission state using recent memory events
2. **ACTION**: Selects appropriate MCP tool and parameters
3. **OBSERVATION**: Processes tool execution results
4. **REFLECTION**: Updates strategy based on outcomes

```python
# Example reasoning cycle
def execute_reasoning_cycle(self, goal: str):
    # 1. THOUGHT: Analyze situation
    analysis = self.analyze_mission(goal)
    
    # 2. ACTION: Execute MCP tool
    action_result = self.call_mcp_tool(tool_name, params)
    
    # 3. OBSERVATION: Process results
    observation = self._process_results(action_result)
    
    # 4. REFLECTION: Learn and plan next steps
    reflection = self._generate_reflection(observation)
```

### How It Connects to Other Components

```
LangGraph Agent
    ├── Reads from → Mission Memory (context)
    ├── Calls → MCP Server (drone operations)
    ├── Uses → Ollama Qwen2 (reasoning)
    └── Writes to → Mission Memory (decisions)
```

### Example Workflow
1. **Goal Received**: "Scan disaster area for survivors"
2. **Memory Check**: Reviews recent drone deployments and battery levels
3. **Reasoning**: "Drone A has 85% battery, suitable for scanning sector 2"
4. **Action**: Calls `move_to(drone_A, 8, 12)` via MCP
5. **Observation**: "Drone moved successfully, battery now 79%"
6. **Reflection**: "Movement successful, proceed with thermal scan"

---

## 2. MCP Server (Tool Gateway)

### Implementation Location
- **Primary File**: `mcp_server/server.py`
- **Tool Definitions**: `mcp_server/drone_tools.py`

### Core Classes & Functions

#### `DroneControlServer` Class
```python
class DroneControlServer:
    def __init__(self, server_name="Drone Control Server")
    def _register_tools(self) -> None
    async def start_server(self, host="localhost", port=8000)
    def stop_server(self) -> None
```

#### Available MCP Tools
```python
# Tool registration with FastMCP decorators
@mcp.tool(name="discover_drones")
def mcp_discover_drones() -> Dict[str, Any]

@mcp.tool(name="get_battery_status") 
def mcp_get_battery_status(drone_id: str) -> Dict[str, Any]

@mcp.tool(name="move_to")
def mcp_move_to(drone_id: str, x: int, y: int) -> Dict[str, Any]

@mcp.tool(name="thermal_scan")
def mcp_thermal_scan(drone_id: str) -> Dict[str, Any]

@mcp.tool(name="return_to_base")
def mcp_return_to_base(drone_id: str) -> Dict[str, Any]
```

### How It Works
The MCP Server acts as a **standardized API gateway** between AI reasoning and drone simulation:

1. **Tool Registration**: FastMCP decorators expose functions as API endpoints
2. **Request Processing**: Validates parameters and handles authentication
3. **Execution**: Calls underlying drone simulation functions
4. **Response Formatting**: Returns structured JSON responses
5. **Logging**: Records all tool calls for debugging and audit

```python
# MCP tool wrapper pattern
@self.mcp.tool(name="move_to", description="Move drone to coordinates")
def mcp_move_to(drone_id: str, x: int, y: int) -> Dict[str, Any]:
    self.logger.info(f"MCP Tool called: move_to(drone_id={drone_id}, x={x}, y={y})")
    result = move_to(drone_id, x, y)  # Call actual implementation
    self.logger.info(f"move_to result: {result.get('message', 'OK')}")
    return result
```

### How It Connects to Other Components

```
MCP Server
    ├── Receives calls from → LangGraph Agent
    ├── Executes → Drone Tools (drone_tools.py)
    ├── Controls → Drone Simulation (via DroneRegistry)
    └── Returns results to → LangGraph Agent
```

### Example Workflow
1. **Request**: LangGraph Agent calls `move_to(drone_A, 10, 15)`
2. **Validation**: Server validates drone_id exists and coordinates are valid
3. **Execution**: Calls `move_to()` function in drone_tools.py
4. **Simulation Update**: Updates drone position in DroneRegistry
5. **Response**: Returns `{"success": true, "new_position": [10, 15], "battery_consumed": 4}`

---

## 3. Drone Simulation (Mesa Agents)

### Implementation Location
- **Primary File**: `simulation/model.py`
- **Agent Definitions**: `simulation/drone_agent.py`
- **Enhanced Models**: `simulation/enhanced_model.py`, `simulation/simple_model.py`

### Core Classes & Functions

#### `DroneSwarmModel` Class
```python
class DroneSwarmModel(Model):
    def __init__(self, width=20, height=20, n_drones=3, n_survivors=5)
    def step(self) -> None
    def log_mission(self, message: str) -> None
    def get_mission_stats(self) -> Dict[str, Any]
```

#### `DroneAgent` Class
```python
class DroneAgent(Agent):
    def __init__(self, unique_id, model)
    def step(self) -> None
    def move_towards_target(self, target_pos: Tuple[int, int]) -> None
    def scan_for_survivors(self) -> List[SurvivorAgent]
    def return_to_charging_station(self) -> None
```

#### Supporting Agents
- **`SurvivorAgent`**: Represents rescue targets with signal strength
- **`ChargingStationAgent`**: Provides drone battery recharging
- **`TerrainAgent`**: Handles environmental obstacles (enhanced model)

### How It Works
The Mesa simulation provides the **physical environment** where AI decisions are executed:

1. **Grid Environment**: 20x20 coordinate system for drone movement
2. **Agent Scheduling**: Mesa scheduler manages agent turn order
3. **State Management**: Tracks drone positions, battery levels, survivor status
4. **Physics Simulation**: Calculates movement costs, battery consumption
5. **Event Generation**: Produces observable outcomes for AI learning

```python
# Drone agent decision making
def step(self):
    if self.battery <= 20:
        self.return_to_charging_station()
    elif self.status == "idle":
        survivors = self.scan_for_survivors()
        if survivors:
            self.move_towards_target(survivors[0].pos)
    
    self.battery -= self.move_cost  # Simulate battery drain
```

### How It Connects to Other Components

```
Drone Simulation
    ├── Controlled by → MCP Server (via DroneRegistry)
    ├── Provides state to → Mesa UI (visualization)
    ├── Generates events for → Mission Memory
    └── Executes commands from → LangGraph Agent
```

### Example Workflow
1. **MCP Command**: `move_to(drone_A, 8, 12)` received
2. **State Update**: DroneRegistry updates drone_A position to (8, 12)
3. **Battery Calculation**: Consumes battery based on distance traveled
4. **Mesa Integration**: Mesa model reflects new drone position
5. **UI Update**: Mesa UI displays updated drone location
6. **Event Logging**: Mission memory records movement event

---

## 4. Mesa UI (Interactive Dashboard)

### Implementation Location
- **Primary File**: `ui/mesa_ui.py`
- **Visualization Components**: `ui/visualization.py`
- **Alternative UIs**: `ui/console_ui.py`, `ui/tkinter_interactive_ui.py`

### Core Classes & Functions

#### `ModularServer` Configuration
```python
def launch_server():
    server = ModularServer(
        DroneSwarmModel,
        [grid, drone_status, reasoning_panel, mission_log, battery_chart],
        "Autonomous Drone Swarm Command System",
        model_params
    )
```

#### Visualization Modules
- **`grid`**: Main simulation grid display
- **`drone_status`**: Real-time drone status table
- **`reasoning_panel`**: AI decision process visualization
- **`mission_log`**: Mission event timeline
- **`battery_chart`**: Battery level monitoring
- **`activity_chart`**: Drone activity statistics

### How It Works
Mesa UI provides **real-time visualization** of the simulation state:

1. **Web Server**: Tornado-based server hosts dashboard at localhost:8521
2. **Real-time Updates**: WebSocket connections push state changes to browser
3. **Interactive Controls**: Sliders and buttons for parameter adjustment
4. **Multi-panel Layout**: Organized display of different data aspects
5. **Responsive Design**: Adapts to different screen sizes

```python
# Grid visualization with agent portrayal
def agent_portrayal(agent):
    if isinstance(agent, DroneAgent):
        portrayal = {
            "Shape": "circle",
            "Color": get_battery_color(agent.battery),
            "Filled": "true",
            "Layer": 1,
            "r": 0.8
        }
    return portrayal
```

### How It Connects to Other Components

```
Mesa UI
    ├── Visualizes → Drone Simulation (Mesa model state)
    ├── Displays → Mission Memory (event logs)
    ├── Shows → AI Reasoning (decision process)
    └── Provides controls for → System Parameters
```

### Example Workflow
1. **Simulation Step**: Mesa model executes one time step
2. **State Collection**: UI queries model for current agent states
3. **Data Processing**: Converts agent data to visualization format
4. **Browser Update**: WebSocket pushes updates to dashboard
5. **User Interaction**: User adjusts parameters via web controls
6. **Model Update**: Changes propagate back to simulation model

---

## 5. Ollama Integration (LLM Backend)

### Implementation Location
- **Primary Integration**: `agent/reasoning.py` (lines 25-35, 85-95)
- **Configuration**: Model initialization and API calls

### Core Integration Points

#### LangChain Integration
```python
try:
    from langchain_community.chat_models import ChatOllama
    self.llm = ChatOllama(
        model="qwen2",
        base_url="http://localhost:11434",
        temperature=0.1
    )
except ImportError:
    # Fallback to direct API calls
    self.llm = None
```

#### Direct API Integration
```python
def _call_ollama_direct(self, prompt: str) -> str:
    response = requests.post(
        f"{self.base_url}/api/generate",
        json={
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "top_p": 0.9}
        }
    )
    return response.json().get("response", "")
```

### How It Works
Ollama provides the **language model backend** for AI reasoning:

1. **Model Serving**: Ollama server hosts Qwen2 model locally
2. **API Interface**: RESTful API for text generation requests
3. **Prompt Engineering**: Structured prompts for rescue mission reasoning
4. **Response Processing**: Parses LLM output into structured decisions
5. **Fallback Handling**: Graceful degradation when Ollama unavailable

```python
# System prompt for rescue operations
self.system_prompt = """
You are a Rescue Command Agent coordinating drone operations in a disaster zone.

Your mission: Coordinate a fleet of drones to locate and rescue survivors efficiently.

Available MCP Tools:
- discover_drones(): Get list of available drones
- get_battery_status(drone_id): Check drone battery level
- move_to(drone_id, x, y): Move drone to coordinates
- thermal_scan(drone_id): Scan for survivors at current position
- return_to_base(drone_id): Send drone back to charging station

Always think step by step and explain your reasoning clearly.
"""
```

### How It Connects to Other Components

```
Ollama Integration
    ├── Provides reasoning for → LangGraph Agent
    ├── Processes context from → Mission Memory
    ├── Generates decisions for → MCP Server calls
    └── Requires → Local Ollama server (localhost:11434)
```

### Example Workflow
1. **Context Building**: Agent compiles mission state and recent events
2. **Prompt Generation**: Creates structured prompt with system instructions
3. **LLM Request**: Sends prompt to Ollama Qwen2 model
4. **Response Processing**: Parses LLM output for thought/action components
5. **Decision Execution**: Converts reasoning into MCP tool calls

---

## 6. Mission Memory (Persistent Context)

### Implementation Location
- **Primary File**: `agent/memory.py`
- **Log Storage**: `logs/mission.log`

### Core Classes & Functions

#### `MissionMemory` Class
```python
class MissionMemory:
    def __init__(self, log_file="logs/mission.log")
    def add_event(self, text: str) -> None
    def load_memory(self) -> List[str]
    def get_recent_events(self, n: int = 10) -> List[str]
    def search_events(self, keyword: str) -> List[str]
    def clear_memory(self) -> None
```

#### Key Functions
- **`add_event()`**: Appends timestamped events to mission log
- **`get_recent_events()`**: Retrieves context for AI reasoning
- **`search_events()`**: Finds specific event types (battery, survivor, etc.)
- **`get_mission_summary()`**: Provides mission statistics and duration

### How It Works
Mission Memory provides **persistent context** across reasoning cycles:

1. **Timestamped Logging**: Events recorded with `[MM:SS]` format
2. **File Persistence**: Logs stored in `logs/mission.log` for durability
3. **Context Retrieval**: Recent events provide reasoning context
4. **Event Search**: Keyword-based filtering for specific event types
5. **Mission Lifecycle**: Tracks mission duration and event count

```python
# Event logging with timestamps
def add_event(self, text: str) -> None:
    timestamp = self._get_mission_time()  # [MM:SS] format
    event_line = f"{timestamp} {text}\n"
    
    with open(self.log_file, 'a', encoding='utf-8') as f:
        f.write(event_line)
    
    print(f"Mission Log: {timestamp} {text}")
```

### Log Format Example
```
=== MISSION LOG STARTED: 2024-03-11 14:30:00 ===
[00:01] Mission started - initializing drone fleet
[00:03] 3 drones discovered
[00:05] Drone A scanning sector 2
[00:07] Drone B battery 25%
[00:09] Survivor detected at position (5, 8)
[00:12] Drone C dispatched to rescue survivor
```

### How It Connects to Other Components

```
Mission Memory
    ├── Provides context to → LangGraph Agent (reasoning)
    ├── Receives events from → MCP Server (tool results)
    ├── Stores decisions from → AI Reasoning cycles
    └── Displays in → Mesa UI (mission log panel)
```

### Example Workflow
1. **Event Generation**: MCP tool execution generates event
2. **Timestamp Creation**: Current mission time calculated
3. **Log Writing**: Event appended to mission.log file
4. **Context Provision**: Recent events provided to AI for next reasoning cycle
5. **UI Display**: Mission log panel shows recent events in real-time

---

## System Execution Flow

### Complete Mission Execution Pipeline

```
1. User Starts Simulation
   ├── main.py launches chosen UI mode
   ├── Mesa model initializes with drones/survivors
   └── MCP server starts (optional)

2. Mission Goal Received
   ├── User defines mission objective
   ├── LangGraph Agent receives goal
   └── Mission Memory logs mission start

3. AI Reasoning Cycle
   ├── Agent queries Mission Memory for context
   ├── Ollama Qwen2 processes reasoning prompt
   ├── ReAct pattern: Thought→Action→Observation→Reflection
   └── Decision recorded in Mission Memory

4. MCP Tool Execution
   ├── Agent calls MCP server with tool/parameters
   ├── Server validates request and executes drone tool
   ├── Drone simulation state updated via DroneRegistry
   └── Tool result returned to Agent

5. Simulation Update
   ├── Mesa model processes drone state changes
   ├── Agent positions/battery levels updated
   ├── Survivor rescue status checked
   └── Environment state synchronized

6. UI Visualization
   ├── Mesa UI queries model for current state
   ├── Dashboard updates drone positions/status
   ├── Mission log displays recent events
   └── Charts show battery/activity trends

7. Cycle Continuation
   ├── Agent reflects on results
   ├── Next reasoning cycle triggered
   ├── Mission continues until objectives met
   └── Final mission summary generated
```

### Data Flow Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   User      │───▶│ Mesa UI     │───▶│ Mesa Model  │
│ Interaction │    │ Dashboard   │    │ Simulation  │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Mission     │◀───│ LangGraph   │───▶│ MCP Server  │
│ Memory      │    │ Agent       │    │ Tool Gateway│
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ logs/       │    │ Ollama      │    │ Drone       │
│ mission.log │    │ Qwen2 LLM   │    │ Registry    │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Integration Points Summary

| Component | Input | Output | Dependencies |
|-----------|-------|--------|--------------|
| **LangGraph Agent** | Mission goals, Memory context | MCP tool calls, Decisions | Ollama, Mission Memory |
| **MCP Server** | Tool requests from Agent | Structured JSON responses | Drone Tools, FastMCP |
| **Drone Simulation** | MCP commands | State updates, Events | Mesa, DroneRegistry |
| **Mesa UI** | Model state | Visual dashboard | Mesa, Tornado |
| **Ollama Integration** | Reasoning prompts | AI-generated text | Ollama server, Qwen2 |
| **Mission Memory** | Events from all components | Historical context | File system |

This architecture provides a robust, modular system where each component has clear responsibilities and well-defined interfaces, enabling sophisticated AI-driven drone coordination for disaster rescue operations.