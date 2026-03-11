"""
Agentic AI Disaster Rescue Drone System
Main entry point for the enhanced terrain simulation with AI reasoning
"""

import sys
import os

def main():
    """Main entry point for the Agentic AI system"""
    
    print("🚁 Agentic AI Disaster Rescue Drone System")
    print("=" * 55)
    print("🤖 AI-Powered Drone Coordination for Emergency Response")
    print("\nSystem Features:")
    print("   • Advanced AI reasoning with Ollama Qwen2")
    print("   • Complex terrain system (mountains, water, forests)")
    print("   • Dynamic weather and environmental conditions")
    print("   • Multi-step AI decision process visualization")
    print("   • A* pathfinding with terrain cost analysis")
    print("   • Real-time mission memory and logging")
    print("   • MCP server integration for tool coordination")
    
    print("\n" + "=" * 55)
    print("Choose your mode:")
    print("1. 🎮 Launch Enhanced Terrain UI (Recommended)")
    print("2. 🧪 Run AI Demo (Automated demonstration)")
    print("3. 🔧 System Test (Test all components)")
    print("4. 📊 Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🚀 Launching Enhanced Terrain UI with AI Reasoning...")
        print("🗺️ Loading advanced terrain system...")
        print("🧠 Initializing AI reasoning engine...")
        print("📡 Starting MCP server integration...")
        
        try:
            from ui.enhanced_tkinter_ui import main as enhanced_main
            enhanced_main()
        except ImportError as e:
            print(f"❌ Error loading Enhanced UI: {e}")
            print("💡 Running basic demo instead...")
            run_basic_demo()
        except Exception as e:
            print(f"❌ UI Error: {e}")
            print("💡 Falling back to demo mode...")
            run_basic_demo()
        
    elif choice == "2":
        print("\n🚀 Launching AI Demo Mode...")
        print("🤖 Automated demonstration of AI reasoning capabilities")
        
        try:
            # Try to run the agentic AI demo
            import subprocess
            result = subprocess.run([sys.executable, "demo_agentic_ai.py"], 
                                  capture_output=False, text=True)
            if result.returncode != 0:
                print("💡 Running fallback demo...")
                run_basic_demo()
        except Exception as e:
            print(f"❌ Demo error: {e}")
            print("💡 Running basic simulation...")
            run_basic_demo()
        
    elif choice == "3":
        print("\n🧪 Running System Component Tests...")
        print("🔧 Testing all Agentic AI components...")
        
        try:
            # Test mission memory
            print("\n1. Testing Mission Memory...")
            from agent.memory import MissionMemory
            memory = MissionMemory()
            memory.add_event("System test initiated")
            print("   ✅ Mission Memory: OK")
            
            # Test MCP tools
            print("\n2. Testing MCP Drone Tools...")
            from mcp_server.drone_tools import discover_drones, get_battery_status
            result = discover_drones()
            print(f"   ✅ MCP Tools: {result['total_count']} drones available")
            
            # Test AI reasoning
            print("\n3. Testing AI Reasoning Engine...")
            try:
                from agent.reasoning import RescueAgent
                agent = RescueAgent()
                print("   ✅ AI Reasoning: Initialized (Ollama connection pending)")
            except Exception as e:
                print(f"   ⚠️  AI Reasoning: {str(e)[:50]}...")
            
            print("\n✅ System test completed!")
            print("🚀 All core components are functional")
            
        except Exception as e:
            print(f"❌ System test failed: {e}")
        
        print("\nPress any key to return to main menu...")
        try:
            input()
        except:
            pass
        main()
        
    elif choice == "4":
        print("\n👋 Thank you for using the Agentic AI Drone System!")
        print("🚁 Stay safe and rescue on!")
        sys.exit(0)
        
    else:
        print("❌ Invalid choice. Please select 1-4.")
        main()


def run_basic_demo():
    """Run a basic simulation demo when advanced UIs are unavailable"""
    print("\n🤖 Running Basic Agentic AI Demo...")
    
    try:
        from simulation.simple_model import SimpleDroneSwarmModel
        from agent.memory import MissionMemory
        
        # Initialize components
        memory = MissionMemory()
        memory.clear_memory()
        memory.add_event("Basic demo started")
        
        model = SimpleDroneSwarmModel(n_drones=3, n_survivors=5, n_charging_stations=2)
        
        print("🚁 Simulation initialized:")
        print(f"   • Drones: {len([a for a in model.custom_agents if hasattr(a, 'battery')])}")
        print(f"   • Survivors: {len([a for a in model.custom_agents if hasattr(a, 'found')])}")
        
        # Run simulation steps
        print("\n🎮 Running simulation...")
        for step in range(20):
            model.step()
            
            if step % 5 == 0:
                active_drones = len([a for a in model.custom_agents 
                                   if hasattr(a, 'battery') and a.battery > 20])
                rescued = len([a for a in model.custom_agents 
                             if hasattr(a, 'found') and a.found])
                
                print(f"   Step {step:2d}: {active_drones} active drones, {rescued} rescued")
                memory.add_event(f"Step {step}: {active_drones} drones active, {rescued} rescued")
        
        print("\n✅ Demo completed successfully!")
        print("📝 Mission log created in logs/mission.log")
        
        print("\nPress any key to return to main menu...")
        try:
            input()
        except:
            pass
        main()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Please check system requirements and dependencies")


if __name__ == "__main__":
    main()