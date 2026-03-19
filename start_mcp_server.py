#!/usr/bin/env python3
"""
Simple MCP Server Starter
Fixed version that works with FastMCP's run() method
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    print("❌ FastMCP not available. Please install: pip install fastmcp")
    sys.exit(1)

from mcp_server.drone_tools import (
    discover_drones,
    get_battery_status,
    move_to,
    thermal_scan,
    return_to_base,
    get_mission_status,
    drone_registry
)

def main():
    """Start the MCP server with FastMCP"""
    
    # Create FastMCP server
    mcp = FastMCP("Drone Control Server")
    
    print("🚁 Drone Control Server")
    print("=" * 60)
    print(f"📡 FastMCP Available: {FASTMCP_AVAILABLE}")
    print(f"🔧 Drone Registry: {len(drone_registry.drones)} drones initialized")
    print(f"🎯 Survivors: {len(drone_registry.survivors)} targets available")
    print(f"⚡ Charging Stations: {len(drone_registry.charging_stations)} stations")
    
    # Register tools
    @mcp.tool()
    def discover_drones_tool():
        """Discover all available drones in the fleet"""
        return discover_drones()
    
    @mcp.tool()
    def get_battery_status_tool(drone_id: str):
        """Get battery level for a specific drone"""
        return get_battery_status(drone_id)
    
    @mcp.tool()
    def move_to_tool(drone_id: str, x: int, y: int):
        """Move a drone to specified coordinates"""
        return move_to(drone_id, x, y)
    
    @mcp.tool()
    def thermal_scan_tool(drone_id: str):
        """Perform thermal scanning for survivors"""
        return thermal_scan(drone_id)
    
    @mcp.tool()
    def return_to_base_tool(drone_id: str):
        """Send drone back to charging station"""
        return return_to_base(drone_id)
    
    @mcp.tool()
    def get_mission_status_tool():
        """Get overall mission statistics"""
        return get_mission_status()
    
    print("\n📋 Available MCP Tools:")
    print("   1. discover_drones_tool() - Get list of available drones")
    print("   2. get_battery_status_tool(drone_id) - Check drone battery level")
    print("   3. move_to_tool(drone_id, x, y) - Move drone to coordinates")
    print("   4. thermal_scan_tool(drone_id) - Scan for survivors")
    print("   5. return_to_base_tool(drone_id) - Send drone to charging station")
    print("   6. get_mission_status_tool() - Get mission statistics")
    
    print(f"\n🚀 Starting MCP server...")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the server
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()