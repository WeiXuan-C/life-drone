3️⃣ MCP Tool Design

sources/mcp_tool_design.md

MCP Tool Interface Design

The system uses FastMCP to expose drone capabilities as standardized tools.

These tools allow the AI agent to interact with drones without direct access to simulation code.

Tool 1: Discover Drones
Function

Returns all active drones in the environment.

Tool Name
discover_drones
Output
[
 { "id": "drone_A", "status": "idle" },
 { "id": "drone_B", "status": "scanning" },
 { "id": "drone_C", "status": "charging" }
]

Purpose:

dynamic drone discovery

prevent hard-coded drone IDs

Tool 2: Get Battery Status
Tool Name
get_battery_status
Parameters
drone_id
Output
{
 "drone_id": "drone_A",
 "battery": 45
}

Purpose:

resource management

mission planning optimization

Tool 3: Move Drone
Tool Name
move_to
Parameters
drone_id
x
y
Example
move_to(drone_B, 10, 6)

Purpose:

sector navigation

grid movement

Tool 4: Thermal Scan
Tool Name
thermal_scan
Parameters
drone_id
Output
{
 "sector": [10,6],
 "thermal_signal": true
}

Purpose:

detect survivors

collect mission data

Tool 5: Return to Base
Tool Name
return_to_base

Purpose:

battery management

drone safety

MCP Server Structure

Example FastMCP server structure:

mcp_server/
 ├─ server.py
 ├─ drone_tools.py
 ├─ drone_simulation.py
 └─ config.py
Example MCP Tool Implementation

Example simplified tool:

@mcp.tool()
def get_battery_status(drone_id: str):
    return drones[drone_id].battery

The AI agent calls the tool through MCP instead of directly accessing drone objects.