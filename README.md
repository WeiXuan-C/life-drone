# 🚁 LifeDrone: Agentic AI Disaster Rescue System

**LifeDrone** is an advanced AI-powered disaster rescue drone coordination system that combines simulation-based modeling, chain-of-thought reasoning, and Model Context Protocol (MCP) integration for autonomous emergency response operations.

## 🎯 About LifeDrone

LifeDrone represents the next generation of disaster response technology, utilizing autonomous drone swarms coordinated by advanced AI agents to locate and rescue survivors in emergency situations. The system integrates multiple cutting-edge technologies to provide a comprehensive solution for disaster management scenarios.

### Key Capabilities
- **🤖 Agentic AI Coordination**: Advanced AI agents with chain-of-thought reasoning
- **🌍 Complex Terrain Simulation**: Mountains, water bodies, forests with dynamic weather
- **🔄 Real-time Decision Making**: ReAct pattern (Thought → Action → Observation → Reflection)
- **📡 MCP Integration**: Model Context Protocol for tool coordination
- **🎮 Interactive Interfaces**: Multiple UI options for different use cases
- **📊 Mission Analytics**: Comprehensive logging and performance tracking

## 🛠️ Tech Stack

### Core Technologies
- **🐍 Python 3.8+**: Primary development language
- **🤖 Mesa Framework**: Agent-based modeling and simulation
- **🧠 Ollama + Qwen2**: Local LLM for AI reasoning and decision making
- **🔄 LangGraph**: Advanced workflow orchestration for AI agents
- **📡 FastMCP**: Model Context Protocol server for tool integration
- **🎮 Tkinter**: Desktop GUI for interactive control
- **📊 Pandas + NumPy**: Data analysis and performance metrics

### AI & Reasoning
- **ReAct Pattern**: Structured reasoning (Thought → Action → Observation → Reflection)
- **Chain-of-Thought**: Detailed decision process logging
- **Memory System**: Mission context and learning from past operations
- **Tool Integration**: MCP-based drone control and coordination

### Simulation & Modeling
- **Complex Terrain**: Multi-layer terrain system with obstacles and weather
- **Dynamic Environment**: Real-time weather changes and environmental challenges
- **A* Pathfinding**: Intelligent navigation with terrain cost analysis
- **Multi-Agent Coordination**: Distributed decision making with conflict resolution

## 🚀 Quick Start Guide

### Prerequisites Check
Before starting, ensure you have Python 3.8+ installed:
```bash
python --version  # Should show 3.8 or higher
```

### 1. Installation

#### Install Core Dependencies
```bash
# Install all dependencies at once
pip install -r requirements.txt
```

Or install individually:
```bash
# Core simulation and AI dependencies
pip install mesa>=3.0.0 numpy pandas matplotlib

# AI and reasoning components
pip install requests langchain-community

# MCP server (optional but recommended)
pip install fastmcp
```

#### Verify Installation
```bash
python verify_installation.py
```
Expected output: 🎉 All checks passed!

### 2. Launch the System

**That's it! Just run:**

```bash
python main.py
```

The system will automatically launch the redesigned UI with all features ready to use.

### 3. Optional: Start Ollama (for AI Reasoning)

If you want to use AI reasoning features:

#### Install Ollama
- **Windows**: Download from [ollama.ai](https://ollama.ai)
- **macOS**: `brew install ollama`
- **Linux**: `curl -fsSL https://ollama.ai/install.sh | sh`

#### Start Ollama and Install Qwen2
```bash
# Start Ollama service
ollama serve

# In a new terminal, install Qwen2 model
ollama pull qwen2
```

### 4. Optional: Start MCP Server (for Advanced Features)

```bash
# Start MCP server
python start_mcp_server.py
```

Expected output:
```
🚁 Drone Control Server
📡 FastMCP Available: True
🔧 Drone Registry: 5 drones initialized
🚀 Starting MCP server...
```

**Keep this terminal open** - the MCP server needs to run continuously.

### 4. Start JSON Response Viewer (AI Monitoring)

Monitor AI reasoning and responses in real-time:

```bash
# In a new terminal
python simple_json_ui.py
```

This opens a window showing:
- 🧠 AI reasoning processes
- 📊 Decision analysis
- 🔄 Tool execution results
- 📝 Mission logs

### 5. Launch Main Interface

Simply run:

```bash
python main.py
```

This will launch the **Redesigned UI** - a modern, streamlined interface featuring:
- 🗺️ Real-time terrain visualization with complex environments
- 🚁 Interactive drone control and monitoring
- 🤖 AI decision-making with chain-of-thought reasoning
- 📊 Live mission analytics and performance metrics
- 🎮 Click-to-command drone operations
- 🌦️ Dynamic weather and terrain effects

**That's it!** The system is ready to use.

## 🎮 User Interface Features

### 🎮 Redesigned UI (Main Interface)
The redesigned UI provides a complete mission control experience:

- **Complex Terrain Visualization**: Mountains, water, forests, urban areas with realistic rendering
- **Real-time Weather**: Dynamic weather conditions (clear, rain, fog, wind, storm) affecting operations
- **Interactive Drone Control**: 
  - Click on map to add drones, survivors, or charging stations
  - Real-time status monitoring for all agents
  - Battery level tracking and alerts
- **AI Decision Monitoring**: 
  - Live chain-of-thought reasoning display
  - Decision history and reasoning logs
  - Multi-step AI analysis visualization
- **Mission Planning**: 
  - Multi-drone coordination
  - Automatic task assignment
  - Conflict resolution
- **Performance Analytics**: 
  - Real-time rescue statistics
  - Success rates and efficiency metrics
  - Distance traveled and battery consumption
- **Mission Complete Auto-Return**: 
  - Drones automatically return to base when all survivors rescued
  - Intelligent path planning for return journey

### 🤖 AI Reasoning Features
- **Ollama Integration**: Direct connection to Qwen2 reasoning engine
- **Chain-of-Thought Display**: Step-by-step AI decision processes
- **Tool Execution Logs**: MCP tool calls and responses
- **Mission Memory**: Historical context and learning
- **Error Monitoring**: AI reasoning validation and debugging

### 🏢 Command Center Dashboard
- **Mission Control**: Central coordination hub for all operations
- **Fleet Management**: Real-time drone status and deployment
- **Emergency Controls**: Immediate recall and emergency protocols
- **Strategic Planning**: Long-term mission coordination
- **Performance Monitoring**: System-wide analytics and reporting

## 🧠 AI Reasoning System

### ReAct Pattern Implementation
LifeDrone implements the ReAct (Reasoning and Acting) pattern for AI decision making:

1. **🤔 Thought**: Analyze current situation and available information
2. **🎯 Action**: Choose and execute appropriate drone operations
3. **👁️ Observation**: Monitor results and environmental feedback
4. **🔄 Reflection**: Learn from outcomes and adjust future decisions

### Chain-of-Thought Features
- **Structured Reasoning**: Each decision includes detailed thought process
- **Context Awareness**: Considers terrain, weather, battery levels, mission priorities
- **Learning Memory**: Builds knowledge from past operations and outcomes
- **Multi-Agent Coordination**: Coordinates decisions across multiple drones
- **Emergency Protocols**: Rapid decision making for critical situations

### LangGraph Workflow Integration
- **Advanced Orchestration**: Complex multi-step mission workflows
- **State Management**: Maintains mission context across operations
- **Tool Coordination**: Seamless integration with MCP drone tools
- **Error Recovery**: Automatic handling of failed operations
- **Scalable Architecture**: Supports complex, multi-phase rescue missions

## 🛠️ System Architecture

### Core Components

#### 1. Simulation Engine (`simulation/`)
- **Enhanced Model**: Complex terrain and weather simulation
- **Drone Agents**: AI-powered autonomous drone behavior
- **Environment System**: Dynamic terrain, obstacles, and weather
- **Performance Tracking**: Comprehensive mission analytics

#### 2. AI Reasoning (`agent/`)
- **Rescue Agent**: Main AI coordinator with Ollama integration
- **Memory System**: Mission context and historical learning
- **Reasoning Engine**: ReAct pattern implementation
- **LangGraph Workflow**: Advanced mission orchestration

#### 3. MCP Server (`mcp_server/`)
- **Drone Tools**: Complete set of drone control operations
- **FastMCP Integration**: Modern MCP protocol implementation
- **Tool Registry**: Centralized drone and resource management
- **API Interface**: Standardized tool access for AI agents

#### 4. User Interfaces (`ui/`)
- **Enhanced Terrain UI**: Primary interactive interface
- **JSON Viewer**: AI reasoning monitoring
- **Command Center**: Mission control dashboard
- **Combined Launcher**: Integrated multi-window experience

## 📋 Available MCP Tools

The system provides 6 core MCP tools for drone operations:

1. **`discover_drones_tool()`** - Get list of available drones and their status
2. **`get_battery_status_tool(drone_id)`** - Check specific drone battery level
3. **`move_to_tool(drone_id, x, y)`** - Move drone to specified coordinates
4. **`thermal_scan_tool(drone_id)`** - Perform thermal scanning for survivors
5. **`return_to_base_tool(drone_id)`** - Send drone to nearest charging station
6. **`get_mission_status_tool()`** - Get overall mission statistics and progress

## 🎯 Usage Scenarios

### 🚨 Emergency Response Training
- **Disaster Simulation**: Realistic emergency scenarios with complex terrain
- **Multi-Agent Coordination**: Train teams on coordinating multiple rescue units
- **Decision Making**: Practice critical decisions under time pressure
- **Resource Management**: Optimize battery usage and charging station placement
- **Weather Adaptation**: Handle changing environmental conditions

### 🎓 Educational & Research
- **AI Behavior Study**: Analyze chain-of-thought reasoning in autonomous systems
- **Multi-Agent Systems**: Research coordination and communication patterns
- **Simulation Modeling**: Study complex system interactions and emergent behavior
- **Performance Optimization**: Test different strategies and algorithms
- **Technology Integration**: Explore MCP, LangGraph, and LLM integration patterns

### 🏢 Professional Development
- **System Integration**: Learn modern AI architecture patterns
- **Protocol Implementation**: Understand MCP and tool integration
- **Workflow Orchestration**: Master LangGraph for complex AI workflows
- **Performance Monitoring**: Implement comprehensive system analytics
- **User Interface Design**: Create effective human-AI interaction interfaces

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve

# Verify Qwen2 model is installed
ollama list | grep qwen2
```

#### MCP Server Not Starting
```bash
# Test MCP components
python test_mcp_connection.py

# Check FastMCP installation
pip show fastmcp

# Reinstall if needed
pip install --upgrade fastmcp
```

#### UI Not Loading
```bash
# Check Python version
python --version  # Should be 3.8+

# Test core simulation
python -c "from simulation.enhanced_model import EnhancedDroneSwarmModel; print('✅ Simulation ready')"

# Check Tkinter availability
python -c "import tkinter; print('✅ Tkinter available')"
```

#### Performance Issues
- **Reduce simulation size**: Lower `width`, `height`, or `n_drones` parameters
- **Disable weather**: Set `weather_enabled=False` in model initialization
- **Limit AI reasoning**: Reduce reasoning frequency in agent settings
- **Close unused UIs**: Run only necessary interface components

## 📊 Performance Metrics

LifeDrone tracks comprehensive performance metrics:

### Mission Effectiveness
- **Rescue Success Rate**: Percentage of survivors successfully rescued
- **Mission Completion Time**: Average time to complete rescue operations
- **Coverage Efficiency**: Area searched per unit time
- **Resource Utilization**: Battery usage optimization and charging efficiency

### AI Performance
- **Decision Quality**: Accuracy of AI reasoning and action selection
- **Response Time**: Speed of AI decision making under pressure
- **Learning Progress**: Improvement in performance over multiple missions
- **Error Recovery**: Ability to handle and recover from failed operations

### System Performance
- **Simulation Speed**: Steps per second in real-time operation
- **Memory Usage**: System resource consumption during operation
- **Network Latency**: MCP tool response times
- **UI Responsiveness**: Interface update frequency and smoothness

## 🔮 Future Enhancements

### Planned Features
- **🌐 Multi-Site Coordination**: Connect multiple disaster sites
- **📱 Mobile Interface**: Tablet and smartphone control interfaces
- **🎥 3D Visualization**: Advanced terrain and drone visualization
- **🔊 Voice Commands**: Natural language mission control
- **📡 Real Hardware Integration**: Connect to actual drone hardware
- **🤝 Multi-User Collaboration**: Team-based mission coordination

### Research Directions
- **Advanced AI Models**: Integration with newer LLMs and reasoning systems
- **Swarm Intelligence**: Enhanced collective behavior algorithms
- **Predictive Analytics**: Forecast disaster patterns and optimal responses
- **Adaptive Learning**: Continuous improvement from mission outcomes
- **Ethical AI**: Ensure responsible AI decision making in critical situations

## 📚 Documentation

### Additional Resources
- **🌐 DeepWiki**: [https://deepwiki.com/WeiXuan-C/Life-Drone] - Comprehensive knowledge base and advanced documentation
- **Architecture Guide**: `docs/architecture.md` - System design and component interaction
- **API Reference**: `docs/mcp_design.md` - MCP tool documentation
- **Tech Deep Dive**: `docs/tech_architecture.md` - Technical implementation details
- **AI Guide**: `docs/agentic_ai.md` - AI reasoning and decision making

### Code Examples
```python
# Basic simulation setup
from simulation.enhanced_model import EnhancedDroneSwarmModel

model = EnhancedDroneSwarmModel(
    width=20, height=20,
    n_drones=5, n_survivors=8,
    n_charging_stations=3,
    weather_enabled=True
)

# Run with AI reasoning
from agent.rescue_agent import RescueAgent
agent = RescueAgent()
result = agent.execute_reasoning_cycle("Locate and rescue all survivors")
```

## 🤝 Contributing

We welcome contributions to LifeDrone! Areas where you can help:

- **🐛 Bug Reports**: Report issues and help improve system stability
- **✨ Feature Requests**: Suggest new capabilities and enhancements
- **📝 Documentation**: Improve guides and add usage examples
- **🧪 Testing**: Add test cases and improve system reliability
- **🎨 UI/UX**: Enhance user interfaces and user experience
- **🤖 AI Improvements**: Contribute to reasoning algorithms and decision making

## 📄 License

LifeDrone is released under the MIT License. See LICENSE file for details.

---

## 🚀 Ready to Deploy

LifeDrone is production-ready for:
- **Emergency Response Training**: Realistic disaster simulation scenarios
- **Research & Development**: AI behavior analysis and multi-agent coordination
- **Educational Programs**: Teaching AI, simulation, and emergency management
- **Technology Demonstration**: Showcase modern AI architecture and integration
- **Professional Development**: Learn cutting-edge AI and system integration skills

**🎯 Start your first rescue mission today!**

For support and questions, please check the documentation or create an issue in the repository.
