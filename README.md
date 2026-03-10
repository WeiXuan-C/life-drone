# 🚁 Autonomous Drone Swarm Command System

An interactive Mesa-based simulation dashboard for disaster rescue operations using AI-driven drone swarms.

## ✅ 主要功能特性

### 🎮 交互式控制界面 (完全功能)
- **Tkinter桌面GUI**：完整的图形用户界面，支持点击操作
- **手动添加智能体**：用户可以在任意位置添加无人机和幸存者
- **实时参数调节**：动态设置无人机电量、位置等参数
- **可视化网格**：20x20灾区环境，实时显示所有智能体状态

### 🧠 AI决策分析系统
- **实时决策监控**：显示每架无人机的AI思考过程
- **状态分布分析**：统计无人机各种状态的分布情况
- **性能指标追踪**：救援效率、电量管理、任务完成率
- **决策日志记录**：完整的AI决策历史和用户操作记录

### 🤖 智能无人机行为
- **自主决策**：基于电量、距离、任务优先级的智能决策
- **电量管理**：自动充电策略和能耗优化
- **协同救援**：多无人机协调完成救援任务
- **动态适应**：实时响应环境变化和新增任务

## 🚀 Quick Start

### Installation & Setup
```bash
# Install dependencies (Mesa 3.x compatible)
pip install mesa>=3.0.0 numpy pandas matplotlib

# Run the system
python main.py
```

### Available Interfaces

#### 1. Tkinter Interactive UI (推荐 - 完全交互式)
```bash
python ui/tkinter_interactive_ui.py
# 或通过主菜单选择选项2
```
- **完整的桌面GUI界面**
- **点击网格选择位置**
- **手动添加无人机和幸存者**
- **实时AI决策分析**
- **详细状态监控表格**
- **自动/手动模拟控制**

#### 2. Console UI (终端界面)
```bash
python ui/console_ui.py
```
- Interactive terminal interface
- Real-time grid visualization
- Manual and auto-stepping modes
- Full drone status monitoring

#### 3. Mesa 3.x Web UI (实验性)
```bash
python ui/mesa3_interactive_ui.py
```
- Web-based interface (需要solara)
- Browser access at localhost:8521

#### 4. Demo Mode (演示模式)
```bash
python demo.py
```
- Automated demonstration
- Shows AI decision-making in action
- Visual progress tracking

## 🎯 System Components

### Core Simulation (`simulation/simple_model.py`)
- **SimpleDroneSwarmModel**: Mesa 3.x compatible model
- **SimpleDroneAgent**: AI-driven drone with autonomous behavior
- **SimpleSurvivorAgent**: Rescue targets with signal detection
- **SimpleChargingStationAgent**: Power stations for drone recharging

### User Interfaces
- **Console UI** (`ui/console_ui.py`): Interactive terminal interface
- **Demo Mode** (`demo.py`): Automated demonstration
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
🆘 Survivor (needs rescue)
✅ Rescued Survivor
⚡ Charging Station
.  Empty Cell
```

## 🧠 AI Behavior

### Drone Decision Making
1. **Battery Critical (≤20%)**: Return to charging station immediately
2. **At Charging Station**: Charge until 80% battery
3. **Survivor Detection**: Move towards nearest unrescued survivor
4. **Rescue Range**: Rescue survivors within 1 grid cell
5. **Patrol Mode**: Random movement when no survivors detected

### Smart Features
- **Energy Management**: Automatic charging when battery is low
- **Pathfinding**: Direct movement towards targets
- **Priority System**: Battery management overrides rescue operations
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