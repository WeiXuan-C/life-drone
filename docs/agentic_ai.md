# 🤖 Agentic AI Disaster Rescue Drone System

A complete offline AI system for coordinating drone fleets in disaster rescue operations using Ollama Qwen2, LangGraph reasoning, and FastMCP protocol.

## 🏗️ System Architecture

```
Ollama (Qwen2 LLM)
        ↓
LangGraph Agent (Reasoning + Memory)
        ↓
FastMCP Server (Drone Tools)
        ↓
Drone Simulation (Mesa)
```

## 📦 Core Components

### 1. Mission Memory System (`agent/memory.py`)
- **Purpose**: Handle mission history and context for AI decision making
- **Features**:
  - Timestamped event logging
  - Mission context retrieval
  - Event search and filtering
  - Memory lifecycle management

```python
from agent.memory import MissionMemory

memory = MissionMemory()
memory.add_event("3 drones discovered")
recent = memory.get_recent_events(5)
```

### 2. AI Reasoning Agent (`agent/reasoning.py`)
- **Purpose**: ReAct pattern reasoning using Ollama Qwen2
- **Features**:
  - Thought → Action → Observation → Reflection cycle
  - MCP tool integration
  - Mission planning and coordination
  - Battery management strategies

```python
from agent.reasoning import RescueAgent

agent = RescueAgent()
result = agent.execute_reasoning_cycle("Scan area for survivors")
```

### 3. MCP Drone Tools (`mcp_server/drone_tools.py`)
- **Purpose**: Expose drone operations as standardized MCP tools
- **Available Tools**:
  - `discover_drones()` - Get available drone list
  - `get_battery_status(drone_id)` - Check battery levels
  - `move_to(drone_id, x, y)` - Move drone to coordinates
  - `thermal_scan(drone_id)` - Scan for survivors
  - `return_to_base(drone_id)` - Send to charging station
  - `get_mission_status()` - Overall mission statistics

### 4. MCP Server (`mcp_server/server.py`)
- **Purpose**: FastMCP server exposing all drone tools
- **Features**:
  - RESTful API interface
  - Tool registration and management
  - Request/response logging
  - Error handling and validation

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama and Qwen2 model**:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Qwen2 model
ollama pull qwen2
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

### Running the System

1. **Start Ollama server**:
```bash
ollama serve
# Server runs on http://localhost:11434
```

2. **Test the complete system**:
```bash
python test_agentic_system.py
```

3. **Start MCP server** (optional):
```bash
python mcp_server/server.py
# Server runs on http://localhost:8000
```

4. **Run AI reasoning agent**:
```python
from agent.reasoning import RescueAgent

agent = RescueAgent()
result = agent.execute_reasoning_cycle("Coordinate rescue mission")
```

## 🧠 AI Reasoning Process

The system implements the **ReAct pattern** for structured AI reasoning:

### 1. **THOUGHT** Phase
- Analyze current mission state
- Review recent mission events
- Consider available resources (drones, battery levels)
- Identify priorities and constraints

### 2. **ACTION** Phase  
- Select appropriate MCP tool
- Determine tool parameters
- Execute drone operation
- Handle tool responses

### 3. **OBSERVATION** Phase
- Process tool execution results
- Update mission context
- Identify new information or changes

### 4. **REFLECTION** Phase
- Learn from action outcomes
- Plan next steps
- Update mission strategy
- Record insights in memory

### Example Reasoning Cycle

```
🧠 THOUGHT: Drone C has 15% battery, which is critical. I should return it to base immediately.

🎯 ACTION: return_to_base(drone_id="drone_C")

👁️ OBSERVATION: {"success": true, "message": "Drone C returned to charging station at (0, 0)"}

🤔 REFLECTION: Successfully managed battery crisis. Drone C is now charging safely. Should check other drones for similar issues.
```

## 🛠️ MCP Tools Reference

### `discover_drones()`
Discover all available drones in the fleet.

**Returns**:
```json
{
  "success": true,
  "drones": ["drone_A", "drone_B", "drone_C"],
  "total_count": 3,
  "message": "Discovered 3 drones"
}
```

### `get_battery_status(drone_id: str)`
Get battery level and status for a specific drone.

**Parameters**:
- `drone_id`: ID of the drone to check

**Returns**:
```json
{
  "success": true,
  "drone_id": "drone_A",
  "battery": 85,
  "battery_status": "healthy",
  "needs_charging": false
}
```

### `move_to(drone_id: str, x: int, y: int)`
Move drone to specified grid coordinates.

**Parameters**:
- `drone_id`: ID of the drone to move
- `x`: Target X coordinate (0-19)
- `y`: Target Y coordinate (0-19)

**Returns**:
```json
{
  "success": true,
  "drone_id": "drone_A",
  "new_position": [10, 10],
  "battery_consumed": 6,
  "remaining_battery": 79
}
```

### `thermal_scan(drone_id: str)`
Perform thermal scanning for survivors at current position.

**Parameters**:
- `drone_id`: ID of the drone performing scan

**Returns**:
```json
{
  "success": true,
  "drone_id": "drone_A",
  "survivors_detected": 2,
  "survivor_details": [
    {"position": [8, 12], "signal_strength": 0.85}
  ],
  "battery_consumed": 5
}
```

### `return_to_base(drone_id: str)`
Send drone back to nearest charging station.

**Parameters**:
- `drone_id`: ID of the drone to recall

**Returns**:
```json
{
  "success": true,
  "drone_id": "drone_C",
  "charging_station": [0, 0],
  "status": "charging"
}
```

## 📊 Mission Memory Format

Mission events are logged with timestamps in `logs/mission.log`:

```
=== MISSION LOG STARTED: 2024-03-11 14:30:00 ===
[00:01] Mission started - initializing drone fleet
[00:03] 3 drones discovered
[00:05] Drone A scanning sector 2
[00:07] Drone B battery 25%
[00:09] Survivor detected at position (5, 8)
[00:12] Drone C dispatched to rescue survivor
```

## 🔧 Configuration

### Ollama Configuration
```python
agent = RescueAgent(
    model_name="qwen2",
    base_url="http://localhost:11434"
)
```

### MCP Server Configuration
```python
server = DroneControlServer("Rescue Command Server")
await server.start_server(host="localhost", port=8000)
```

### Mission Memory Configuration
```python
memory = MissionMemory(log_file="logs/custom_mission.log")
```

## 🎯 Usage Examples

### Basic Mission Coordination
```python
from agent.reasoning import RescueAgent
from agent.memory import MissionMemory

# Initialize system
agent = RescueAgent()
memory = MissionMemory()

# Execute mission goals
goals = [
    "Discover available drones and assess fleet status",
    "Deploy drones for systematic area coverage", 
    "Coordinate survivor rescue operations",
    "Manage battery levels and charging cycles"
]

for goal in goals:
    result = agent.execute_reasoning_cycle(goal)
    print(f"Goal: {goal}")
    print(f"Success: {result['success']}")
```

### Direct Tool Usage
```python
from mcp_server.drone_tools import *

# Discover fleet
drones = discover_drones()
print(f"Available drones: {drones['drones']}")

# Check battery levels
for drone_id in drones['drones']:
    status = get_battery_status(drone_id)
    print(f"{drone_id}: {status['battery']}%")

# Deploy for scanning
move_to("drone_A", 10, 10)
scan_result = thermal_scan("drone_A")
print(f"Survivors found: {scan_result['survivors_detected']}")
```

### Mission Memory Analysis
```python
from agent.memory import MissionMemory

memory = MissionMemory()

# Search for specific events
battery_events = memory.search_events("battery")
survivor_events = memory.search_events("survivor")

# Get mission summary
summary = memory.get_mission_summary()
print(f"Mission duration: {summary['mission_duration']}")
print(f"Total events: {summary['total_events']}")
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_agentic_system.py
```

This will test:
- ✅ Mission memory system
- ✅ MCP drone tools
- ✅ AI reasoning (requires Ollama)
- ✅ Integrated mission simulation

## 🔍 Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Verify qwen2 model is available
ollama list
```

### MCP Server Issues
```bash
# Test MCP tools directly
python -c "from mcp_server.drone_tools import discover_drones; print(discover_drones())"

# Check server logs
tail -f logs/mcp_server.log
```

### Memory System Issues
```bash
# Check log file permissions
ls -la logs/mission.log

# Test memory system
python -c "from agent.memory import MissionMemory; m = MissionMemory(); m.add_event('test')"
```

## 🚀 Integration with Existing System

The agentic AI system integrates seamlessly with the existing Mesa simulation:

```python
# In your existing simulation code
from agent.reasoning import RescueAgent
from agent.memory import MissionMemory

class EnhancedDroneModel(SimpleDroneSwarmModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ai_agent = RescueAgent()
        self.mission_memory = MissionMemory()
    
    def step(self):
        # AI-driven mission coordination
        goal = "Coordinate current rescue operations"
        reasoning_result = self.ai_agent.execute_reasoning_cycle(goal)
        
        # Execute normal simulation step
        super().step()
        
        # Log mission progress
        active_drones = len([a for a in self.schedule.agents if a.agent_type == "drone"])
        self.mission_memory.add_event(f"Simulation step: {active_drones} drones active")
```

## 📈 Performance Metrics

The system tracks comprehensive mission metrics:

- **Drone Fleet Status**: Active/offline drone counts
- **Battery Management**: Average levels, low-battery alerts
- **Rescue Progress**: Survivors found/rescued ratios
- **Mission Efficiency**: Time to complete objectives
- **AI Decision Quality**: Reasoning cycle success rates

## 🔮 Future Enhancements

1. **Advanced AI Models**: Support for larger language models
2. **Multi-Agent Coordination**: Swarm intelligence algorithms  
3. **Real-time Adaptation**: Dynamic strategy adjustment
4. **Performance Optimization**: Faster reasoning cycles
5. **Extended Tool Set**: Additional drone capabilities
6. **Web Dashboard**: Real-time mission monitoring UI

## 📝 License

This agentic AI system is part of the Autonomous Drone Swarm Command System project and follows the same licensing terms.

---

**🤖 Intelligent drone coordination powered by offline AI reasoning!**