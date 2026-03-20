"""
Real MCP Client Implementation
Uses actual JSON-RPC protocol to communicate with FastMCP server
"""

import asyncio
import json
import subprocess
import sys
import logging
from typing import Dict, Any, List, Optional
import uuid

class RealMCPClient:
    """
    Real MCP Client that uses JSON-RPC protocol to communicate with FastMCP server
    This is the proper way to implement MCP protocol
    """
    
    def __init__(self, server_command: List[str] = None):
        """
        Initialize real MCP client
        
        Args:
            server_command: Command to start MCP server
        """
        self.server_command = server_command or [sys.executable, "start_mcp_server.py"]
        self.process = None
        self.connected = False
        self.request_id = 0
        
        # Setup logging
        self.logger = logging.getLogger("RealMCPClient")
        
        # Available tools (discovered from server)
        self.available_tools = {}
    
    async def connect(self) -> bool:
        """
        Connect to MCP server using stdio transport
        
        Returns:
            bool: True if connection successful
        """
        try:
            self.logger.info(f"Starting MCP server: {' '.join(self.server_command)}")
            
            # Start MCP server process with stdio transport
            self.process = await asyncio.create_subprocess_exec(
                *self.server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for server to start (increased timeout)
            await asyncio.sleep(3)
            
            # Check if process is still running
            if self.process.returncode is not None:
                # Process died, read error output
                stderr = await self.process.stderr.read()
                error_msg = stderr.decode() if stderr else "Unknown error"
                self.logger.error(f"❌ MCP server process died: {error_msg}")
                return False
            
            # Initialize MCP protocol
            if await self._initialize_protocol():
                self.connected = True
                self.logger.info("✅ Real MCP protocol connection established")
                return True
            else:
                self.logger.error("❌ Failed to initialize MCP protocol")
                # Clean up process
                if self.process and self.process.returncode is None:
                    self.process.terminate()
                    await self.process.wait()
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to MCP server: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _initialize_protocol(self) -> bool:
        """Initialize MCP protocol with handshake"""
        try:
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "LifeDrone MCP Client",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await self._send_request(init_request)
            
            if response and "result" in response:
                self.logger.info("🤝 MCP protocol initialized")
                
                # Discover available tools
                await self._discover_tools()
                
                return True
            else:
                self.logger.error(f"❌ Initialize failed: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Protocol initialization error: {e}")
            return False
    
    async def _discover_tools(self):
        """Discover available tools from server"""
        try:
            # Send tools/list request
            list_request = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/list",
                "params": {}
            }
            
            response = await self._send_request(list_request)
            
            if response and "result" in response:
                tools = response["result"].get("tools", [])
                
                for tool in tools:
                    self.available_tools[tool["name"]] = {
                        "description": tool.get("description", ""),
                        "inputSchema": tool.get("inputSchema", {})
                    }
                
                self.logger.info(f"📋 Discovered {len(self.available_tools)} MCP tools")
            
        except Exception as e:
            self.logger.error(f"❌ Tool discovery error: {e}")
    
    async def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send JSON-RPC request to MCP server
        
        Args:
            request: JSON-RPC request object
            
        Returns:
            JSON-RPC response or None if failed
        """
        try:
            if not self.process or not self.process.stdin:
                self.logger.error("❌ No active MCP server process")
                return None
            
            # Send request
            request_line = json.dumps(request) + "\n"
            self.logger.debug(f"📤 Sending request: {request_line.strip()}")
            
            self.process.stdin.write(request_line.encode())
            await self.process.stdin.drain()
            
            # Read response with timeout
            try:
                response_line = await asyncio.wait_for(
                    self.process.stdout.readline(),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                self.logger.error("❌ Request timeout: No response from server")
                return None
            
            if response_line:
                response = json.loads(response_line.decode().strip())
                self.logger.debug(f"📥 Received response: {json.dumps(response)[:200]}")
                return response
            else:
                self.logger.error("❌ Connection lost: Empty response from server")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Request failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _next_id(self) -> int:
        """Generate next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call MCP tool using JSON-RPC protocol (REAL MCP IMPLEMENTATION)
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool parameters
            
        Returns:
            Tool result
        """
        if not self.connected:
            return {
                "success": False,
                "error": "MCP client not connected"
            }
        
        if tool_name not in self.available_tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not available"
            }
        
        try:
            # Create tools/call request using REAL MCP JSON-RPC protocol
            call_request = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": kwargs
                }
            }
            
            # Send request and get response via MCP protocol
            response = await self._send_request(call_request)
            
            if response and "result" in response:
                result = response["result"]
                
                self.logger.info(f"🔧 MCP Tool called via JSON-RPC: {tool_name}({kwargs}) -> Success")
                
                # Extract content from MCP response format
                if "content" in result and result["content"]:
                    # MCP returns content as array of content blocks
                    content = result["content"][0]
                    if content["type"] == "text":
                        # Parse the text content as JSON (our tools return JSON)
                        try:
                            tool_result = json.loads(content["text"])
                            return tool_result
                        except json.JSONDecodeError:
                            return {
                                "success": True,
                                "message": content["text"]
                            }
                
                return {
                    "success": True,
                    "result": result
                }
            
            elif response and "error" in response:
                error_msg = response["error"].get("message", "Unknown error")
                self.logger.error(f"❌ MCP Tool error: {tool_name} -> {error_msg}")
                
                return {
                    "success": False,
                    "error": error_msg,
                    "tool_name": tool_name
                }
            
            else:
                return {
                    "success": False,
                    "error": "No response from MCP server",
                    "tool_name": tool_name
                }
                
        except Exception as e:
            error_msg = f"MCP protocol error: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "tool_name": tool_name
            }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """
        Get list of available tools from MCP server
        
        Returns:
            Dict containing:
                - tools: List of tool definitions with name, description, inputSchema
        """
        # Convert internal format to standard format expected by workflow
        tools_list = []
        for tool_name, tool_info in self.available_tools.items():
            tools_list.append({
                "name": tool_name,
                "description": tool_info.get("description", ""),
                "inputSchema": tool_info.get("inputSchema", {})
            })
        
        return {
            "tools": tools_list
        }
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.process and self.process.returncode is None:
            self.logger.info("🔌 Disconnecting from MCP server")
            self.process.terminate()
            await self.process.wait()
        
        self.connected = False
        self.process = None


# Synchronous wrapper for LangGraph compatibility
class SyncRealMCPClient:
    """
    Synchronous wrapper for real MCP client
    
    Provides a clean, generic interface for calling MCP tools without hardcoded methods.
    All tool calls go through the universal call_tool() method.
    """
    
    def __init__(self):
        self.async_client = RealMCPClient()
        self.loop = None
        self._connected = False
    
    def _get_loop(self):
        """Get or create event loop"""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def connect(self) -> bool:
        """Connect to MCP server (synchronous)"""
        if self._connected:
            return True
            
        loop = self._get_loop()
        result = loop.run_until_complete(self.async_client.connect())
        self._connected = result
        return result
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Universal method to call any MCP tool dynamically
        
        Args:
            tool_name: Name of the tool to call (discovered via get_available_tools)
            **kwargs: Tool-specific parameters
            
        Returns:
            Dict with tool execution results
            
        Example:
            client.call_tool("discover_drones")
            client.call_tool("thermal_scan", drone_id="drone_A")
            client.call_tool("move_to", drone_id="drone_A", x=10, y=20)
        """
        if not self._connected:
            if not self.connect():
                return {"success": False, "error": "Failed to connect to MCP server"}
        
        loop = self._get_loop()
        return loop.run_until_complete(self.async_client.call_tool(tool_name, **kwargs))
    
    def get_available_tools(self) -> Dict[str, Any]:
        """
        Get list of available tools from MCP server
        
        Returns:
            Dict containing:
                - tools: List of tool definitions with name, description, inputSchema
                
        Use this to discover what tools are available before calling them.
        """
        return self.async_client.get_available_tools()
    
    def disconnect(self):
        """Disconnect from MCP server (synchronous)"""
        if self._connected:
            loop = self._get_loop()
            loop.run_until_complete(self.async_client.disconnect())
            self._connected = False


# Usage example
if __name__ == "__main__":
    async def test_real_mcp():
        """Test real MCP client with dynamic tool calling"""
        print("🧪 Testing Real MCP Client")
        print("-" * 40)
        
        client = RealMCPClient()
        
        if await client.connect():
            print("✅ Connected to MCP server via JSON-RPC")
            
            # Test dynamic tool calling (no hardcoded methods)
            result = await client.call_tool("discover_drones")
            print(f"🔍 Discover drones: {result.get('success', False)}")
            
            result = await client.call_tool("get_battery_status", drone_id="drone_A")
            print(f"🔋 Battery status: {result.get('success', False)}")
            
            await client.disconnect()
        else:
            print("❌ Failed to connect")
    
    asyncio.run(test_real_mcp())


# Global MCP client instance (singleton pattern)
_mcp_client_instance = None


def get_mcp_client() -> SyncRealMCPClient:
    """
    Get global MCP client instance (singleton pattern).
    
    Returns:
        SyncRealMCPClient: Global synchronous MCP client instance
    """
    global _mcp_client_instance
    
    if _mcp_client_instance is None:
        _mcp_client_instance = SyncRealMCPClient()
    
    return _mcp_client_instance


def reset_mcp_client():
    """Reset the global MCP client instance (useful for testing)."""
    global _mcp_client_instance
    
    if _mcp_client_instance is not None:
        try:
            _mcp_client_instance.disconnect()
        except:
            pass
        _mcp_client_instance = None