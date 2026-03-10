"""
Setup script for Autonomous Drone Swarm Command System
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "ui", "simulation", "agent", "mcp_server", "docs"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def setup_project():
    """Complete project setup"""
    print("🚁 Setting up Autonomous Drone Swarm Command System...")
    print("=" * 60)
    
    # Create directories
    create_directories()
    
    # Install requirements
    if install_requirements():
        print("\n🎉 Setup completed successfully!")
        print("\n🚀 To run the system:")
        print("   python main.py")
        print("\n📊 Or run the UI directly:")
        print("   python ui/mesa_ui.py")
        print("   python ui/advanced_ui.py")
        
        return True
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    setup_project()