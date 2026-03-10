from fastmcp import FastMCP

mcp = FastMCP("Drone Control Server")

drones = {
    "drone_A": {"battery": 80},
    "drone_B": {"battery": 60},
}

@mcp.tool()
def discover_drones():
    return list(drones.keys())

@mcp.tool()
def get_battery_status(drone_id: str):
    return drones[drone_id]["battery"]

if __name__ == "__main__":
    mcp.run()