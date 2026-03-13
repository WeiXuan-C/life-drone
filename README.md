# 🚁 Autonomous Drone Swarm Command System

An interactive Mesa-based simulation dashboard for disaster rescue operations using AI-driven drone swarms.

## ✅ Main Features

### 🎮 Interactive Control Interface (Full Functionality)
- **Tkinter Desktop GUI**: Complete graphical user interface with click operations
- **Manual Agent Addition**: Users can add drones and survivors at any location
- **Real-time Parameter Adjustment**: Dynamically set drone battery, position and other parameters
- **Visualization Grid**: 20x20 disaster area environment, real-time display of all agent states

### 🧠 AI Decision Analysis System
- **Real-time Decision Monitoring**: Display AI thinking process of each drone
- **Status Distribution Analysis**: Statistics of drone status distribution
- **Performance Metrics Tracking**: Rescue efficiency, battery management, task completion rate
- **Decision Log Recording**: Complete AI decision history and user operation records

### 🤖 Intelligent Drone Behavior
- **Autonomous Decision Making**: Intelligent decisions based on battery, distance, task priority
- **Battery Management**: Automatic charging strategy and energy consumption optimization
- **Coordinated Rescue**: Multiple drones coordinate to complete rescue missions
- **Dynamic Adaptation**: Real-time response to environmental changes and new tasks
- **🏠 Home Base Operations**: Central return point for all drones with emergency recall capability

## 🚀 Quick Start

### Installation & Setup
```bash
# Install dependencies (Mesa 3.x compatible)
pip install mesa>=3.0.0 numpy pandas matplotlib

# Run the system
python main.py
```

### Available Interfaces

#### 1. Tkinter Interactive UI (Recommended - Fully Interactive)
```bash
python ui/tkinter_interactive_ui.py
# Or select option 2 from main menu
```
- **Complete Desktop GUI Interface**
- **Click Grid to Select Position**
- **Manually Add Drones and Survivors**
- **Real-time AI Decision Analysis**
- **Detailed Status Monitoring Table**
- **Auto/Manual Simulation Control**

#### 2. Console UI (Terminal Interface)
```bash
python ui/console_ui.py
```
- Interactive terminal interface
- Real-time grid visualization
- Manual and auto-stepping modes
- Full drone status monitoring

#### 3. Mesa 3.x Web UI (Experimental)
```bash
python ui/mesa3_interactive_ui.py
```
- Web-based interface (requires solara)
- Browser access at localhost:8521

#### 4. Command Center UI (New - Home Base Management)
```bash
python ui/command_center_ui.py
```
- **Home Base Operations Interface**
- **Emergency Recall All Drones**
- **Real-time Home Base Status**
- **Drone Return Configuration**
- **Integrated Simulation Control**

#### 5. Demo Mode (Demonstration Mode)
```bash
python demo.py
```
#### 6. Home Base Demo (New Feature)
```bash
python demo_home_base.py
```
- Demonstrates home base functionality
- Shows emergency recall operations
- Tests drone return behavior

## 🎯 System Components

### Core Simulation (`simulation/simple_model.py`)
- **SimpleDroneSwarmModel**: Mesa 3.x compatible model with home base support
- **SimpleDroneAgent**: AI-driven drone with autonomous behavior and home return capability
- **SimpleSurvivorAgent**: Rescue targets with signal detection
- **SimpleChargingStationAgent**: Power stations for drone recharging
- **SimpleHomeBaseAgent**: Central command point where all drones can return

### Command Center (`command_center.py`)
- **CentralCommandCenter**: Main coordination hub for all drone operations
- **Home Base Management**: Emergency recall and return-to-base functionality
- **Mission Planning**: Coordinated multi-drone operations
- **Real-time Monitoring**: Live status tracking and control

### User Interfaces
- **Command Center UI** (`ui/command_center_ui.py`): Home base management and emergency controls
- **Console UI** (`ui/console_ui.py`): Interactive terminal interface
- **Demo Mode** (`demo.py`): Automated demonstration
- **Home Base Demo** (`demo_home_base.py`): Home base functionality demonstration
- **Simple UI** (`ui/simple_ui.py`): Mesa 3.x visualization (experimental)

### Legacy Components (Mesa 2.x)
- **Advanced UI** (`ui/mesa_ui.py`, `ui/advanced_ui.py`): Web-based interfaces
- **Original Model** (`simulation/model.py`): Full-featured model with scheduling

## 🎮 Console UI Controls

```
🎮 Controls:
   [ENTER] - Single Step
   [a] - Auto Step (toggle)
   [r] - Reset Simulation
   [s] - Show Statistics
   [l] - Show Legend
   [q] - Quit
```

## 🔤 Visual Legend

```
🟢 Healthy Drone (>60% battery)
🟡 Medium Drone (30-60% battery)  
🔴 Low Battery Drone (<30% battery)
🏠 Drone at Home Base
🆘 Survivor (needs rescue)
✅ Rescued Survivor
⚡ Charging Station
🏢 Home Base
.  Empty Cell
```

## 🧠 AI Behavior

### Drone Decision Making
1. **Emergency Recall**: Return to home base immediately when emergency recall is active
2. **Battery Critical (≤20%)**: Return to charging station immediately
3. **At Charging Station**: Charge until 80% battery
4. **Survivor Detection**: Move towards nearest unrescued survivor
5. **Rescue Range**: Rescue survivors within 1 grid cell
6. **Home Base Return**: Return to home base when idle (configurable)
7. **Patrol Mode**: Random movement when no survivors detected and not returning home

### Smart Features
- **Energy Management**: Automatic charging when battery is low
- **Pathfinding**: Direct movement towards targets
- **Priority System**: Emergency recall overrides all other operations
- **Home Base Operations**: Centralized return point for mission coordination
- **Coordination**: Multiple drones work independently but efficiently

## 📊 Performance Metrics

The system tracks:
- Active drone count
- Survivor rescue rate
- Average battery levels
- Mission completion time
- AI decision frequency

## 🔧 Integration Ready

### Architecture Designed For:
- **FastMCP Server**: External drone control via MCP protocol
- **LangGraph Workflows**: Complex mission orchestration
- **Ollama/Qwen2 AI**: Advanced reasoning and natural language planning
- **Mesa Visualization**: Web-based dashboard (when compatible)

### Extension Points:
- Custom agent behaviors in `SimpleDroneAgent.step()`
- Additional UI components in console interface
- External API integration via MCP tools
- Advanced AI reasoning modules

## 🛠️ Development

### Project Structure
```
├── main.py                    # Main entry point
├── demo.py                   # Automated demonstration
├── simulation/
│   ├── simple_model.py       # Mesa 3.x compatible model ✅
│   ├── model.py             # Original Mesa 2.x model
│   └── drone_agent.py       # Legacy agent classes
├── ui/
│   ├── console_ui.py        # Working console interface ✅
│   ├── simple_ui.py         # Mesa 3.x visualization
│   ├── mesa_ui.py           # Legacy web UI
│   └── visualization.py     # Legacy components
├── utils/
│   └── logging.py           # Mission logging utilities
└── logs/
    └── mission.log          # Mission event log
```

### Testing
```bash
# Test core functionality
python -c "
from simulation.simple_model import SimpleDroneSwarmModel
model = SimpleDroneSwarmModel()
model.step()
print('✅ Core system working!')
"

# Run full demo
python demo.py
```

## 🎯 Current Status

### ✅ Working Components
- Mesa 3.x compatible simulation engine
- Console-based interactive UI
- AI-driven drone behavior
- Real-time mission logging
- Performance monitoring
- Demo mode with visualization

### 🔄 Integration Points
- MCP server integration (architecture ready)
- LangGraph workflow orchestration (hooks prepared)
- Ollama/Qwen2 AI reasoning (interface designed)
- Web UI (requires Mesa version compatibility)

### 🚀 Ready to Use
The system is fully functional for:
- Disaster rescue simulation
- AI behavior research
- Multi-agent coordination studies
- Educational demonstrations
- Performance benchmarking

## 📝 Usage Examples

### Basic Simulation
```python
from simulation.simple_model import SimpleDroneSwarmModel

# Create model
model = SimpleDroneSwarmModel(
    width=20, height=20,
    n_drones=5, n_survivors=10,
    n_charging_stations=3
)

# Run simulation
for step in range(100):
    model.step()
    if step % 10 == 0:
        print(f"Step {step}: Mission progress...")
```

### Interactive Console
```bash
python ui/console_ui.py
# Use controls to interact with simulation
# Press 'a' for auto-stepping
# Press 's' for detailed statistics
```

---

**🚁 Autonomous drone swarms ready for disaster rescue operations!**

**🎯 Fully functional with console UI - Web UI ready for Mesa compatibility updates**
