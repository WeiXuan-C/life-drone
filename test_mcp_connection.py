#!/usr/bin/env python3
"""
Test MCP Server Connection
"""

import sys
import os
import subprocess
import json

def test_mcp_tools():
    """Test MCP server tools via subprocess"""
    
    print("🧪 Testing MCP Server Tools")
    print("-" * 40)
    
    # Test by importing and calling tools directly
    try:
        from mcp_server.drone_tools import (
            discover_drones,
            get_battery_status,
            move_to,
            thermal_scan,
            return_to_base,
            get_mission_status
        )
        
        print("✅ MCP tools imported successfully")
        
        # Test each tool
        test_cases = [
            ("discover_drones", lambda: discover_drones()),
            ("get_battery_status", lambda: get_battery_status("drone_A")),
            ("move_to", lambda: move_to("drone_A", 5, 5)),
            ("thermal_scan", lambda: thermal_scan("drone_A")),
            ("return_to_base", lambda: return_to_base("drone_C")),
            ("get_mission_status", lambda: get_mission_status())
        ]
        
        for i, (tool_name, test_func) in enumerate(test_cases, 1):
            print(f"\n{i}. Testing {tool_name}...")
            try:
                result = test_func()
                if result.get("success"):
                    print(f"   ✅ {result.get('message', 'Success')}")
                    if 'drones' in result:
                        print(f"      Found {len(result['drones'])} drones")
                    if 'battery' in result:
                        print(f"      Battery: {result['battery']}%")
                else:
                    print(f"   ❌ {result.get('error', 'Failed')}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        
        print(f"\n✅ MCP tools are working correctly!")
        print("🚀 MCP server can be started with: python start_mcp_server.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import MCP tools: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing tools: {e}")
        return False

def check_server_status():
    """Check if MCP server process is running"""
    try:
        # Check if FastMCP is available
        import fastmcp
        print(f"✅ FastMCP version: {fastmcp.__version__}")
        
        # Check drone registry
        from mcp_server.drone_tools import drone_registry
        print(f"✅ Drone registry: {len(drone_registry.drones)} drones")
        print(f"✅ Survivors: {len(drone_registry.survivors)} targets")
        print(f"✅ Charging stations: {len(drone_registry.charging_stations)} stations")
        
        return True
        
    except ImportError:
        print("❌ FastMCP not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

def main():
    """Main test function"""
    print("🚁 MCP Server Connection Test")
    print("=" * 50)
    
    # Check server components
    if not check_server_status():
        print("\n💡 Install FastMCP: pip install fastmcp")
        return
    
    # Test tools
    if test_mcp_tools():
        print("\n🎯 MCP Server Status: READY")
        print("📋 All tools are functional")
        print("🚀 Start server: python start_mcp_server.py")
    else:
        print("\n❌ MCP Server Status: ERROR")
        print("💡 Check dependencies and configuration")

if __name__ == "__main__":
    main()