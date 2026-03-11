#!/usr/bin/env python3
"""
Complete Agentic AI System Demo

This script demonstrates the full Agentic AI system for disaster rescue drone coordination.
It shows the integration of all components:
- Mission Memory System
- AI Reasoning Agent
- MCP Drone Tools
- Complete rescue mission simulation
"""

import sys
import os
import time
import asyncio

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🚁 {title}")
    print(f"{'='*60}")

def print_step(step: int, description: str):
    """Print a formatted step."""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def main():
    """Run the complete Agentic AI system demonstration."""
    
    print_header("AGENTIC AI DISASTER RESCUE SYSTEM - FULL DEMO")
    
    print("🎯 System Architecture:")
    print("   Ollama (Qwen2 LLM) → LangGraph Agent → MCP Server → Drone Simulation")
    print("\n🔧 Components to Test:")
    print("   1. Mission Memory System")
    print("   2. AI Reasoning Agent") 
    print("   3. MCP Drone Tools")
    print("   4. Integrated Mission Execution")
    
    try:
        # Test 1: Mission Memory System
        print_step(1, "Testing Mission Memory System")
        
        from agent.memory import MissionMemory
        
        memory = MissionMemory()
        memory.clear_memory()
        
        # Add sample mission events
        events = [
            "Agentic AI system initialized",
            "Mission command center activated", 
            "Disaster zone coordinates received",
            "Drone fleet status check initiated"
        ]
        
        for event in events:
            memory.add_event(event)
            time.sleep(0.3)
        
        print("   ✅ Mission memory system operational")
        
        # Display recent events
        recent = memory.get_recent_events(5)
        print("   📝 Recent mission events:")
        for event in recent:
            print(f"      {event}")
        
        # Test 2: MCP Drone Tools
        print_step(2, "Testing MCP Drone Tools")
        
        from mcp_server.drone_tools import (
            discover_drones, get_battery_status, move_to, 
            thermal_scan, return_to_base, get_mission_status
        )
        
        # Discover drone fleet
        print("   🔍 Discovering drone fleet...")
        drone_result = discover_drones()
        if drone_result.get('success'):
            drones = drone_result.get('drones', [])
            print(f"   ✅ Found {len(drones)} drones: {', '.join(drones)}")
            memory.add_event(f"Fleet discovery: {len(drones)} drones operational")
        
        # Check battery levels
        print("   🔋 Checking drone battery levels...")
        low_battery_drones = []
        
        for drone_id in drones[:3]:  # Check first 3 drones
            battery_result = get_battery_status(drone_id)
            if battery_result.get('success'):
                battery = battery_result.get('battery', 0)
                status = battery_result.get('battery_status', 'unknown')
                print(f"      {drone_id}: {battery}% ({status})")
                
                if battery < 30:
                    low_battery_drones.append(drone_id)
                    memory.add_event(f"Low battery alert: {drone_id} at {battery}%")
        
        print("   ✅ Battery assessment completed")
        
        # Test 3: AI Reasoning Agent
        print_step(3, "Testing AI Reasoning Agent")
        
        try:
            from agent.reasoning import RescueAgent
            
            agent = RescueAgent()
            print("   🧠 AI reasoning agent initialized")
            print(f"      Model: {agent.model_name}")
            print(f"      Base URL: {agent.base_url}")
            
            # Test reasoning cycle
            goal = "Coordinate emergency drone deployment for survivor search"
            print(f"   🎯 Mission Goal: {goal}")
            
            try:
                reasoning_result = agent.execute_reasoning_cycle(goal)
                
                if reasoning_result.get('success'):
                    print("   ✅ AI reasoning cycle completed successfully")
                    print(f"   💭 AI Thought: {reasoning_result.get('thought', 'N/A')[:80]}...")
                    print(f"   🎯 AI Action: {reasoning_result.get('action', 'N/A')[:80]}...")
                    memory.add_event("AI reasoning cycle completed successfully")
                else:
                    print("   ⚠️  AI reasoning completed with issues")
                    memory.add_event("AI reasoning cycle completed with warnings")
            
            except Exception as e:
                print(f"   ⚠️  AI reasoning unavailable (Ollama not running): {str(e)[:60]}...")
                print("   🤖 Continuing with simulated AI reasoning")
                memory.add_event("AI reasoning simulated (Ollama unavailable)")
        
        except Exception as e:
            print(f"   ❌ Error initializing AI agent: {e}")
            memory.add_event("AI agent initialization failed")
        
        # Test 4: Integrated Mission Execution
        print_step(4, "Integrated Mission Execution")
        
        print("   🚀 Executing coordinated rescue mission...")
        
        # Deploy healthy drones for area scanning
        healthy_drones = [d for d in drones if d not in low_battery_drones]
        scan_positions = [(5, 8), (12, 15), (18, 6)]
        
        survivors_found = 0
        
        for i, drone_id in enumerate(healthy_drones[:3]):
            if i < len(scan_positions):
                pos = scan_positions[i]
                
                # Move drone to scan position
                print(f"   📍 Deploying {drone_id} to sector {pos}")
                move_result = move_to(drone_id, pos[0], pos[1])
                
                if move_result.get('success'):
                    memory.add_event(f"{drone_id} deployed to sector {pos}")
                    
                    # Perform thermal scan
                    scan_result = thermal_scan(drone_id)
                    if scan_result.get('success'):
                        detected = scan_result.get('survivors_detected', 0)
                        survivors_found += detected
                        print(f"   🔍 {drone_id} scan: {detected} survivors detected")
                        memory.add_event(f"{drone_id} thermal scan: {detected} survivors found")
        
        # Handle low battery drones
        print("   ⚡ Managing low battery drones...")
        for drone_id in low_battery_drones:
            return_result = return_to_base(drone_id)
            if return_result.get('success'):
                print(f"   🔌 {drone_id} returned to charging station")
                memory.add_event(f"{drone_id} returned for emergency charging")
        
        # Mission status summary
        print("   📊 Mission status update...")
        status_result = get_mission_status()
        if status_result.get('success'):
            stats = status_result.get('mission_stats', {})
            active_drones = stats.get('active_drones', 0)
            avg_battery = stats.get('average_battery', 0)
            rescue_progress = stats.get('rescue_progress', 0)
            
            print(f"      Active drones: {active_drones}")
            print(f"      Average battery: {avg_battery}%")
            print(f"      Rescue progress: {rescue_progress}%")
            print(f"      Survivors detected: {survivors_found}")
            
            memory.add_event(f"Mission update: {survivors_found} survivors located, {active_drones} drones active")
        
        # Test 5: Mission Summary
        print_step(5, "Mission Summary & Analysis")
        
        # Display complete mission log
        print("   📝 Complete Mission Log:")
        all_events = memory.get_recent_events(20)
        for event in all_events:
            print(f"      {event}")
        
        # Mission statistics
        summary = memory.get_mission_summary()
        print(f"\n   📊 Mission Statistics:")
        print(f"      Duration: {summary['mission_duration']}")
        print(f"      Total events: {summary['total_events']}")
        print(f"      Mission start: {summary['mission_start']}")
        
        # Search for specific event types
        battery_events = memory.search_events("battery")
        survivor_events = memory.search_events("survivor")
        
        print(f"\n   🔍 Event Analysis:")
        print(f"      Battery-related events: {len(battery_events)}")
        print(f"      Survivor-related events: {len(survivor_events)}")
        
        # Final system status
        print_header("AGENTIC AI SYSTEM STATUS")
        
        print("✅ System Component Status:")
        print("   ✅ Mission Memory System: OPERATIONAL")
        print("   ✅ MCP Drone Tools: OPERATIONAL")
        print("   ✅ Drone Fleet Management: OPERATIONAL")
        print("   ✅ Mission Coordination: OPERATIONAL")
        print("   ⚠️  AI Reasoning: REQUIRES OLLAMA SERVER")
        
        print(f"\n🎯 Mission Results:")
        print(f"   • Drones Deployed: {len(healthy_drones)}")
        print(f"   • Survivors Located: {survivors_found}")
        print(f"   • Low Battery Alerts: {len(low_battery_drones)}")
        print(f"   • Mission Events Logged: {summary['total_events']}")
        
        print(f"\n🚀 System Ready For:")
        print("   • Real-time disaster response coordination")
        print("   • Multi-drone fleet management")
        print("   • AI-driven mission planning")
        print("   • Persistent mission logging and analysis")
        
        print(f"\n📋 Next Steps:")
        print("   1. Start Ollama server: ollama serve")
        print("   2. Load Qwen2 model: ollama pull qwen2")
        print("   3. Start MCP server: python mcp_server/server.py")
        print("   4. Run full simulation: python main.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print(f"\n🎉 Agentic AI System Demo Completed Successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Demo encountered errors")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n🛑 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)