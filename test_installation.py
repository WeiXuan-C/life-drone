#!/usr/bin/env python
"""
Life-Drone Installation Test Script
Quickly verify all core dependencies are correctly installed
"""

import sys

def test_imports():
    """Test all required module imports"""
    print("🔍 Testing core dependency packages...")
    print("=" * 50)
    
    tests = [
        ("Mesa", "mesa"),
        ("NumPy", "numpy"),
        ("Pandas", "pandas"),
        ("Matplotlib", "matplotlib"),
        ("NetworkX", "networkx"),
        ("Tornado", "tornado"),
        ("Requests", "requests"),
        ("Python-dateutil", "dateutil"),
    ]
    
    failed = []
    
    for name, module in tests:
        try:
            __import__(module)
            print(f"✅ {name:20s} - OK")
        except ImportError as e:
            print(f"❌ {name:20s} - FAILED: {e}")
            failed.append((name, module))
    
    print("\n" + "=" * 50)
    
    # Test optional dependencies
    print("\n🔍 Testing optional dependency packages...")
    print("=" * 50)
    
    optional_tests = [
        ("LangChain", "langchain_community"),
        ("FastMCP", "fastmcp"),
        ("Solara", "solara"),
    ]
    
    for name, module in optional_tests:
        try:
            __import__(module)
            print(f"✅ {name:20s} - OK")
        except ImportError:
            print(f"⚠️  {name:20s} - Not installed (optional)")
    
    print("\n" + "=" * 50)
    
    return failed


def test_core_modules():
    """Test Life-Drone core modules"""
    print("\n🔍 Testing Life-Drone core modules...")
    print("=" * 50)
    
    tests = [
        ("Simulation Model", "simulation.simple_model", "SimpleDroneSwarmModel"),
        ("Mission Memory", "agent.memory", "MissionMemory"),
        ("Drone Agent", "simulation.simple_model", "SimpleDroneAgent"),
    ]
    
    failed = []
    
    for name, module, cls in tests:
        try:
            mod = __import__(module, fromlist=[cls])
            getattr(mod, cls)
            print(f"✅ {name:20s} - OK")
        except Exception as e:
            print(f"❌ {name:20s} - FAILED: {e}")
            failed.append(name)
    
    print("\n" + "=" * 50)
    
    return failed


def test_simulation():
    """Test basic simulation functionality"""
    print("\n🔍 Testing basic simulation functionality...")
    print("=" * 50)
    
    try:
        from simulation.simple_model import SimpleDroneSwarmModel
        
        print("Creating simulation model...")
        model = SimpleDroneSwarmModel(
            n_drones=3,
            n_survivors=5,
            n_charging_stations=2
        )
        
        print("Executing simulation steps...")
        model.step()
        model.step()
        model.step()
        
        print(f"✅ Simulation test successful!")
        print(f"   - Agent count: {len(model.custom_agents)}")
        print(f"   - Current step: {model.schedule.steps}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation test failed: {e}")
        return False


def main():
    """Main test function"""
    print("\n" + "=" * 50)
    print("🚁 Life-Drone Installation Test")
    print("=" * 50 + "\n")
    
    # Test dependency packages
    failed_imports = test_imports()
    
    # Test core modules
    failed_modules = test_core_modules()
    
    # Test simulation
    sim_ok = test_simulation()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    if not failed_imports and not failed_modules and sim_ok:
        print("\n🎉 All tests passed! System is ready!")
        print("\n🚀 Quick start command:")
        print("   python ui/enhanced_tkinter_ui.py")
        return 0
    else:
        print("\n⚠️  Issues found:")
        if failed_imports:
            print(f"   - {len(failed_imports)} dependency packages missing")
            print("   Run: python -m pip install -r requirements.txt")
        if failed_modules:
            print(f"   - {len(failed_modules)} core modules have issues")
        if not sim_ok:
            print("   - Simulation functionality test failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
