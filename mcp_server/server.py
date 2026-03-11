"""
MCP Server for Drone Control System

This module creates the FastMCP server that exposes all drone tools
for the AI reasoning agent. The server runs locally and provides
a standardized interface for drone operations.

The server exposes the following MCP tools:
- discover_drones: Get list of available drones
- get_battery_status: Check drone battery levels
- move_to: Move drones to specific coordinates
- thermal_scan: Scan for survivors
- return_to_base: Send drones to charging stations
- get_mission_status: Get overall mission statistics

Usage:
    python mcp_server/server.py

The server will start on localhost:8000 by default.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    print("Warning: FastMCP not available. Using mock server implementation.")

from drone_tools import (
    discover_drones,
    get_battery_status,
    move_to,
    thermal_scan,
    return_to_base,
    get_mission_status,
    drone_registry
)


class MockMCPServer:
    """
    Mock MCP server implementation when FastMCP is not available.
    Provides the same interface for testing and development.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        self.running = False
    
    def tool(self, name: str = None, description: str = None):
        """Decorator to register tools."""
        def decorator(func):
            tool_name = name or func.__name__
            self.tools[tool_name] = {
                "function": func,
                "description": description or func.__doc__ or f"Tool: {tool_name}"
            }
            return func
        return decorator
    
    async def serve(self, host: str = "localhost", port: int = 8000):
        """Mock serve method."""
        print(f"🚀 Mock MCP Server '{self.name}' starting on {host}:{port}")
        print(f"📡 Registered {len(self.tools)} tools:")
        
        for tool_name, tool_info in self.tools.items():
            print(f"   - {tool_name}: {tool_info['description']}")
        
        self.running = True
        
        # Simulate server running
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            self.running = False
    
    def stop(self):
        """Stop the mock server."""
        self.running = False
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a registered tool (for testing)."""
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
        
        try:
            result = self.tools[tool_name]["function"](**kwargs)
            return result
        except Exception as e:
            return {"success": False, "error": f"Tool execution failed: {str(e)}"}


class DroneControlServer:
    """
    Main MCP server class for drone control operations.
    
    This server provides a standardized interface for AI agents
    to control drones in the disaster rescue simulation.
    """
    
    def __init__(self, server_name: str = "Drone Control Server"):
        """
        Initialize the drone control server.
        
        Args:
            server_name: Name of the MCP server
        """
        self.server_name = server_name
        
        # Initialize MCP server (FastMCP or mock)
        if FASTMCP_AVAILABLE:
            self.mcp = FastMCP(server_name)
        else:
            self.mcp = MockMCPServer(server_name)
        
        # Register all drone tools
        self._register_tools()
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for the server."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/mcp_server.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("DroneControlServer")
    
    def _register_tools(self):
        """Register all drone control tools with the MCP server."""
        
        # Tool 1: Discover Drones
        @self.mcp.tool(
            name="discover_drones",
            description="Discover all available drones in the fleet and return their basic information"
        )
        def mcp_discover_drones() -> Dict[str, Any]:
            """MCP wrapper for discover_drones tool."""
            self.logger.info("MCP Tool called: discover_drones")
            result = discover_drones()
            self.logger.info(f"discover_drones result: {result.get('message', 'OK')}")
            return result
        
        # Tool 2: Get Battery Status
        @self.mcp.tool(
            name="get_battery_status",
            description="Get battery level and status information for a specific drone"
        )
        def mcp_get_battery_status(drone_id: str) -> Dict[str, Any]:
            """MCP wrapper for get_battery_status tool."""
            self.logger.info(f"MCP Tool called: get_battery_status(drone_id={drone_id})")
            result = get_battery_status(drone_id)
            self.logger.info(f"get_battery_status result: {result.get('message', 'OK')}")
            return result
        
        # Tool 3: Move To Position
        @self.mcp.tool(
            name="move_to",
            description="Move a drone to specified coordinates on the grid"
        )
        def mcp_move_to(drone_id: str, x: int, y: int) -> Dict[str, Any]:
            """MCP wrapper for move_to tool."""
            self.logger.info(f"MCP Tool called: move_to(drone_id={drone_id}, x={x}, y={y})")
            result = move_to(drone_id, x, y)
            self.logger.info(f"move_to result: {result.get('message', 'OK')}")
            return result
        
        # Tool 4: Thermal Scan
        @self.mcp.tool(
            name="thermal_scan",
            description="Perform thermal scanning for survivors at drone's current position"
        )
        def mcp_thermal_scan(drone_id: str) -> Dict[str, Any]:
            """MCP wrapper for thermal_scan tool."""
            self.logger.info(f"MCP Tool called: thermal_scan(drone_id={drone_id})")
            result = thermal_scan(drone_id)
            self.logger.info(f"thermal_scan result: {result.get('message', 'OK')}")
            return result
        
        # Tool 5: Return to Base
        @self.mcp.tool(
            name="return_to_base",
            description="Send a drone back to the nearest charging station"
        )
        def mcp_return_to_base(drone_id: str) -> Dict[str, Any]:
            """MCP wrapper for return_to_base tool."""
            self.logger.info(f"MCP Tool called: return_to_base(drone_id={drone_id})")
            result = return_to_base(drone_id)
            self.logger.info(f"return_to_base result: {result.get('message', 'OK')}")
            return result
        
        # Tool 6: Get Mission Status
        @self.mcp.tool(
            name="get_mission_status",
            description="Get overall mission statistics and fleet status information"
        )
        def mcp_get_mission_status() -> Dict[str, Any]:
            """MCP wrapper for get_mission_status tool."""
            self.logger.info("MCP Tool called: get_mission_status")
            result = get_mission_status()
            self.logger.info(f"get_mission_status result: {result.get('message', 'OK')}")
            return result
        
        self.logger.info(f"Registered 6 MCP tools for {self.server_name}")
    
    async def start_server(self, host: str = "localhost", port: int = 8000):
        """
        Start the MCP server.
        
        Args:
            host: Server host address
            port: Server port number
        """
        try:
            self.logger.info(f"Starting {self.server_name} on {host}:{port}")
            
            # Print server information
            print(f"\n🚁 {self.server_name}")
            print("=" * 60)
            print(f"🚀 Server starting on {host}:{port}")
            print(f"📡 FastMCP Available: {FASTMCP_AVAILABLE}")
            print(f"🔧 Drone Registry: {len(drone_registry.drones)} drones initialized")
            print(f"🎯 Survivors: {len(drone_registry.survivors)} targets available")
            print(f"⚡ Charging Stations: {len(drone_registry.charging_stations)} stations")
            
            print("\n📋 Available MCP Tools:")
            tools = [
                "discover_drones() - Get list of available drones",
                "get_battery_status(drone_id) - Check drone battery level",
                "move_to(drone_id, x, y) - Move drone to coordinates",
                "thermal_scan(drone_id) - Scan for survivors",
                "return_to_base(drone_id) - Send drone to charging station",
                "get_mission_status() - Get mission statistics"
            ]
            
            for i, tool in enumerate(tools, 1):
                print(f"   {i}. {tool}")
            
            print(f"\n🔗 Server URL: http://{host}:{port}")
            print("🛑 Press Ctrl+C to stop the server")
            print("=" * 60)
            
            # Start the server
            if FASTMCP_AVAILABLE:
                await self.mcp.serve(host=host, port=port)
            else:
                await self.mcp.serve(host=host, port=port)
        
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise
    
    def stop_server(self):
        """Stop the MCP server."""
        self.logger.info("Stopping MCP server")
        if hasattr(self.mcp, 'stop'):
            self.mcp.stop()


async def test_server_tools():
    """Test all server tools to ensure they work correctly."""
    print("\n🧪 Testing MCP Server Tools")
    print("-" * 40)
    
    # Create server instance
    server = DroneControlServer("Test Drone Server")
    
    if not FASTMCP_AVAILABLE:
        # Test tools directly with mock server
        test_cases = [
            ("discover_drones", {}),
            ("get_battery_status", {"drone_id": "drone_A"}),
            ("move_to", {"drone_id": "drone_A", "x": 5, "y": 5}),
            ("thermal_scan", {"drone_id": "drone_A"}),
            ("get_battery_status", {"drone_id": "drone_A"}),  # Check battery after scan
            ("return_to_base", {"drone_id": "drone_C"}),  # Low battery drone
            ("get_mission_status", {})
        ]
        
        for i, (tool_name, params) in enumerate(test_cases, 1):
            print(f"\n{i}. Testing {tool_name}({params})")
            try:
                result = await server.mcp.call_tool(tool_name, **params)
                if result.get("success"):
                    print(f"   ✅ {result.get('message', 'Success')}")
                else:
                    print(f"   ❌ {result.get('error', 'Failed')}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
    
    print("\n✅ Tool testing completed")


async def main():
    """Main server entry point."""
    
    # Test tools first
    await test_server_tools()
    
    # Create and start the server
    server = DroneControlServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested")
        server.stop_server()
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        server.stop_server()


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Run the server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)