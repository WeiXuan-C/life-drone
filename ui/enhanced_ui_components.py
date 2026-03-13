"""
Enhanced UI component methods
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
from simulation.terrain_system import TerrainType, ObstacleType, WeatherCondition

def create_legend(parent_frame):
    """Create terrain legend"""
    legend_frame = ttk.LabelFrame(parent_frame, text="🔤 Terrain Legend", padding=5)
    legend_frame.pack(fill=tk.X, pady=5)
    
    # Terrain colors
    terrain_colors = {
        "Flat": "#90EE90",      # Light green
        "Hill": "#DEB887",      # Light brown
        "Mountain": "#8B4513",  # Dark brown
        "Water": "#4169E1",     # Blue
        "Forest": "#228B22",    # Dark green
        "Desert": "#F4A460",    # Sand
        "Swamp": "#556B2F",     # Olive green
        "Urban": "#696969",     # Gray
        "Cliff": "#2F4F4F",     # Dark gray
        "Valley": "#9ACD32"     # Yellow green
    }
    
    legend_text = "Terrain: "
    for terrain, color in list(terrain_colors.items())[:5]:
        legend_text += f"■{terrain} "
    legend_text += "\nObstacles: 🏢Building 🌳Tree 📡Tower 🚗Vehicle | Weather: ☀Clear 🌧Rain 💨Wind 🌫Fog ⛈Storm"
    legend_text += "\nAgents: 🚁Drone S=Survivor ✓=Rescued ⚡=Charging Station"
    
    ttk.Label(legend_frame, text=legend_text, font=('Arial', 11)).pack()

def create_control_panel(parent_frame, ui_instance):
    """Create control panel"""
    control_frame = ttk.LabelFrame(parent_frame, text="🎮 Enhanced Control Panel", padding=10)
    control_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Terrain generation control
    terrain_frame = ttk.Frame(control_frame)
    terrain_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(terrain_frame, text="Terrain Seed:").pack(side=tk.LEFT)
    ui_instance.terrain_seed_var = tk.IntVar(value=42)
    ttk.Entry(terrain_frame, textvariable=ui_instance.terrain_seed_var, width=10).pack(side=tk.LEFT, padx=(5, 10))
    
    ttk.Button(terrain_frame, text="🗺️ Regenerate Terrain", 
              command=ui_instance.regenerate_terrain).pack(side=tk.LEFT, padx=5)
    
    # Position selection
    pos_frame = ttk.Frame(control_frame)
    pos_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(pos_frame, text="Select Position:").pack(side=tk.LEFT)
    ui_instance.x_var = tk.IntVar(value=10)
    ui_instance.y_var = tk.IntVar(value=10)
    
    ttk.Label(pos_frame, text="X:").pack(side=tk.LEFT, padx=(10, 0))
    ttk.Spinbox(pos_frame, from_=0, to=19, width=5, textvariable=ui_instance.x_var).pack(side=tk.LEFT, padx=(0, 10))
    
    ttk.Label(pos_frame, text="Y:").pack(side=tk.LEFT)
    ttk.Spinbox(pos_frame, from_=0, to=19, width=5, textvariable=ui_instance.y_var).pack(side=tk.LEFT)
    
    # Drone parameters
    drone_frame = ttk.Frame(control_frame)
    drone_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(drone_frame, text="Drone Battery:").pack(side=tk.LEFT)
    ui_instance.battery_var = tk.IntVar(value=100)
    battery_scale = ttk.Scale(drone_frame, from_=20, to=100, orient=tk.HORIZONTAL, 
                             variable=ui_instance.battery_var, length=120)
    battery_scale.pack(side=tk.LEFT, padx=(10, 5))
    
    ui_instance.battery_label = ttk.Label(drone_frame, text="100%")
    ui_instance.battery_label.pack(side=tk.LEFT)
    battery_scale.configure(command=lambda v: ui_instance.battery_label.config(text=f"{int(float(v))}%"))
    
    # Add buttons
    button_frame = ttk.Frame(control_frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="🚁 Add Drone", 
              command=ui_instance.add_drone).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(button_frame, text="🆘 Add Survivor", 
              command=ui_instance.add_survivor).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="⚡ Add Charging Station", 
              command=ui_instance.add_charging_station).pack(side=tk.LEFT, padx=5)
    
    # Simulation control
    sim_frame = ttk.Frame(control_frame)
    sim_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(sim_frame, text="▶️ Execute Step", 
              command=ui_instance.step_simulation).pack(side=tk.LEFT, padx=(0, 5))
    
    ui_instance.auto_var = tk.BooleanVar()
    ttk.Checkbutton(sim_frame, text="Auto Run", 
                   variable=ui_instance.auto_var, 
                   command=ui_instance.toggle_auto_run).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(sim_frame, text="🔄 Reset", 
              command=ui_instance.reset_simulation).pack(side=tk.LEFT, padx=5)

def create_enhanced_analysis_panel(parent_frame, ui_instance):
    """Create enhanced analysis panel with tabs"""
    analysis_frame = ttk.LabelFrame(parent_frame, text="🧠 Enhanced AI Analysis", padding=10)
    analysis_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))

    # Create notebook for tabs
    analysis_notebook = ttk.Notebook(analysis_frame)
    analysis_notebook.pack(fill=tk.BOTH, expand=True)

    # Tab 1: Mission Status
    mission_tab = ttk.Frame(analysis_notebook, padding=10)
    analysis_notebook.add(mission_tab, text="Mission Status")

    ui_instance.metrics_labels = {}

    # Mission metrics
    mission_metrics = ["Active Drones", "Rescue Progress", "Rescue Success Rate"]
    for i, metric in enumerate(mission_metrics):
        frame = ttk.Frame(mission_tab)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text=f"{metric}:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        ui_instance.metrics_labels[metric] = ttk.Label(frame, text="0", font=('Arial', 11))
        ui_instance.metrics_labels[metric].pack(side=tk.LEFT, padx=(10, 0))

    # Tab 2: Resource Status
    resource_tab = ttk.Frame(analysis_notebook, padding=10)
    analysis_notebook.add(resource_tab, text="Resources")

    resource_metrics = ["Avg Battery"]
    for metric in resource_metrics:
        frame = ttk.Frame(resource_tab)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text=f"{metric}:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        ui_instance.metrics_labels[metric] = ttk.Label(frame, text="0", font=('Arial', 11))
        ui_instance.metrics_labels[metric].pack(side=tk.LEFT, padx=(10, 0))

    # Tab 3: Environment Challenges
    env_tab = ttk.Frame(analysis_notebook, padding=10)
    analysis_notebook.add(env_tab, text="Challenges")

    env_metrics = ["Terrain Challenges", "Weather Delays"]
    for metric in env_metrics:
        frame = ttk.Frame(env_tab)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text=f"{metric}:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        ui_instance.metrics_labels[metric] = ttk.Label(frame, text="0", font=('Arial', 11))
        ui_instance.metrics_labels[metric].pack(side=tk.LEFT, padx=(10, 0))


def create_ai_reasoning_panel(parent_frame, ui_instance):
    """Create AI reasoning panel"""
    reasoning_frame = ttk.Frame(parent_frame)
    reasoning_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create notebook widget to display reasoning for different drones
    ui_instance.reasoning_notebook = ttk.Notebook(reasoning_frame)
    ui_instance.reasoning_notebook.pack(fill=tk.BOTH, expand=True)
    
    # Initialize reasoning display areas
    ui_instance.reasoning_displays = {}

def create_terrain_analysis_panel(parent_frame, ui_instance):
    """Create terrain analysis panel"""
    terrain_frame = ttk.Frame(parent_frame)
    terrain_frame.pack(fill=tk.BOTH, expand=True)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(terrain_frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Terrain statistics with scrollbar
    ui_instance.terrain_stats_text = tk.Text(terrain_frame, font=('Arial', 11),
                                             wrap=tk.WORD, yscrollcommand=scrollbar.set)
    ui_instance.terrain_stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=ui_instance.terrain_stats_text.yview)

def get_terrain_color(terrain_type, height=0, weather=None, obstacle=None):
    """Get terrain color"""
    base_colors = {
        TerrainType.FLAT: "#90EE90",      # Light green
        TerrainType.HILL: "#DEB887",      # Light brown
        TerrainType.MOUNTAIN: "#8B4513",  # Dark brown
        TerrainType.WATER: "#4169E1",     # Blue
        TerrainType.FOREST: "#228B22",    # Dark green
        TerrainType.DESERT: "#F4A460",    # Sand
        TerrainType.SWAMP: "#556B2F",     # Olive green
        TerrainType.URBAN: "#696969",     # Gray
        TerrainType.CLIFF: "#2F4F4F",     # Dark gray
        TerrainType.VALLEY: "#9ACD32"     # Yellow green
    }
    
    color = base_colors.get(terrain_type, "#FFFFFF")
    
    # Adjust color depth based on height
    if height > 1500:
        # High altitude, darker color
        color = darken_color(color, 0.3)
    elif height > 800:
        color = darken_color(color, 0.15)
    
    # Weather effects
    if weather == WeatherCondition.STORM:
        color = darken_color(color, 0.4)
    elif weather == WeatherCondition.FOG:
        color = lighten_color(color, 0.3)
    elif weather == WeatherCondition.RAIN:
        color = darken_color(color, 0.2)
    
    return color

def darken_color(color, factor):
    """Darken color"""
    if color.startswith('#'):
        color = color[1:]
    
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    
    return f"#{r:02x}{g:02x}{b:02x}"

def lighten_color(color, factor):
    """Lighten color"""
    if color.startswith('#'):
        color = color[1:]
    
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    
    return f"#{r:02x}{g:02x}{b:02x}"

def get_obstacle_symbol(obstacle_type):
    """Get obstacle symbol"""
    symbols = {
        ObstacleType.BUILDING: "🏢",
        ObstacleType.TREE: "🌳",
        ObstacleType.TOWER: "📡",
        ObstacleType.DEBRIS: "🗿",
        ObstacleType.VEHICLE: "🚗",
        ObstacleType.BRIDGE: "🌉",
        ObstacleType.TUNNEL: "🕳️"
    }
    return symbols.get(obstacle_type, "")

def get_weather_symbol(weather):
    """Get weather symbol"""
    symbols = {
        WeatherCondition.CLEAR: "☀",
        WeatherCondition.RAIN: "🌧",
        WeatherCondition.WIND: "💨",
        WeatherCondition.FOG: "🌫",
        WeatherCondition.STORM: "⛈"
    }
    return symbols.get(weather, "")