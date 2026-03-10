System Architecture

The proposed system is an offline agentic AI architecture designed to coordinate a swarm of rescue drones in disaster scenarios where internet connectivity is unavailable. The system runs entirely on local infrastructure and integrates a reasoning agent, simulation environment, and standardized communication protocol.

The architecture consists of five major components:

User Interface Layer

Agentic Reasoning Layer

Memory and Planning Layer

MCP Communication Layer

Drone Simulation Layer

The architecture ensures that the AI reasoning engine remains decoupled from the drone control implementation, which improves modularity and extensibility.

Architecture Components
1 User Interface Layer

The system provides an interactive UI using Mesa visualization tools.

Functions include:

Adding or removing drones

Setting drone status

Placing survivor signals

Monitoring mission progress

Viewing AI reasoning steps

Viewing tool calls and mission logs

This allows human operators to simulate real disaster scenarios.

2 Agentic Reasoning Layer

The AI Command Agent is powered by Qwen2, running locally through Ollama.

Responsibilities include:

analyzing the mission objective

discovering available drones

assigning drone tasks

monitoring drone battery levels

coordinating swarm movement

reacting to new observations

The AI uses the ReAct reasoning paradigm, which alternates between reasoning and action.

3 Memory and Planning Layer

The system uses LangGraph to maintain reasoning state and mission memory.

LangGraph enables:

multi-step reasoning

iterative planning

task decomposition

persistent mission memory

Mission history is stored in:

mission.log

This allows the agent to reflect on previous actions and improve decision-making.

4 MCP Communication Layer

The system uses FastMCP to expose drone functionality as tools.

Instead of calling Python functions directly, the AI agent interacts with drones through MCP tool calls.

Advantages:

standardized tool interface

dynamic tool discovery

decoupled architecture

compliance with case study requirements

5 Drone Simulation Layer

The drone environment is implemented using Mesa, a Python agent-based simulation framework.

The simulation includes:

a 2D disaster grid

drone agents

survivor signals

battery consumption

scanning operations

Each drone operates as an independent simulation agent.