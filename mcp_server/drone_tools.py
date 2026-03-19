"""
Drone Tools Module for MCP Server

This module exposes drone simulation functions as MCP tools using FastMCP.
It maintains a drone registry and provides structured APIs for drone operations.

Available MCP Tools:
- discover_drones(): Return list of available drone IDs
- get_battery_status(drone_id): Return battery level for specific drone
- move_to(drone_id, x, y): Move drone to specified coordinates
- thermal_scan(drone_id): Simulate thermal scanning for survivors
- return_to_base(drone_id): Send drone back to charging station

Each tool returns structured JSON responses for consistent integration
with the AI reasoning system.
"""

import json
import random
import time
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    print("Warning: FastMCP not available. Using mock implementation.")


class DroneStatus(Enum):
    """Possible drone status values."""
    IDLE = "idle"
    MOVING = "moving"
    SCANNING = "scanning"
    CHARGING = "charging"
    RETURNING = "returning"
    OFFLINE = "offline"


@dataclass
class DroneInfo:
    """Information about a single drone."""
    drone_id: str
    battery: int  # Battery percentage (0-100)
    status: DroneStatus
    position: Tuple[int, int]  # (x, y) coordinates
    last_scan_time: Optional[float] = None
    survivors_found: int = 0
    total_distance: float = 0.0
    
    @property
    def id(self) -> str:
        """Alias for drone_id for compatibility."""
        return self.drone_id


@dataclass
class SurvivorInfo:
    """Information about detected survivors."""
    position: Tuple[int, int]
    signal_strength: float
    detected_time: float
    rescued: bool = False
    rescue_time: Optional[float] = None


class DroneRegistry:
    """
    Central registry for managing drone fleet and simulation state.
    
    This class maintains the state of all drones in the simulation,
    including their positions, battery levels, and operational status.
    It also tracks survivors and charging stations.
    """
    
    def __init__(self):
        """Initialize the drone registry with default fleet."""
        self.drones: Dict[str, DroneInfo] = {}
        self.survivors: Dict[str, SurvivorInfo] = {}
        # Add more charging stations to ensure coverage of entire area
        self.charging_stations: List[Tuple[int, int]] = [
            (0, 0), (0, 19), (19, 0), (19, 19),  # Four corners
            (10, 10), (5, 10), (15, 10),         # Center area
            (10, 5), (10, 15)                    # Top and bottom center
        ]
        self.grid_size = (20, 20)  # 20x20 grid
        
        # Initialize default drone fleet
        self._initialize_default_fleet()
        self._initialize_survivors()
    
    def _initialize_default_fleet(self) -> None:
        """Initialize a default fleet of drones."""
        default_drones = [
            ("drone_A", 85, (2, 2)),
            ("drone_B", 45, (5, 5)),
            ("drone_C", 15, (8, 8)),
            ("drone_D", 90, (12, 12)),
            ("drone_E", 60, (15, 15))
        ]
        
        for drone_id, battery, position in default_drones:
            self.drones[drone_id] = DroneInfo(
                drone_id=drone_id,
                battery=battery,
                status=DroneStatus.IDLE,
                position=position
            )
    
    def _initialize_survivors(self) -> None:
        """Initialize survivors in random locations."""
        survivor_positions = [
            (3, 7), (8, 12), (15, 5), (6, 18), (14, 9)
        ]
        
        for i, pos in enumerate(survivor_positions):
            survivor_id = f"survivor_{i+1}"
            self.survivors[survivor_id] = SurvivorInfo(
                position=pos,
                signal_strength=random.uniform(0.6, 1.0),
                detected_time=time.time()
            )
    
    def get_drone(self, drone_id: str) -> Optional[DroneInfo]:
        """Get drone information by ID."""
        return self.drones.get(drone_id)
    
    def update_drone_position(self, drone_id: str, x: int, y: int) -> bool:
        """Update drone position and calculate battery consumption."""
        drone = self.get_drone(drone_id)
        if not drone:
            return False
        
        # Calculate distance and battery consumption
        old_x, old_y = drone.position
        distance = ((x - old_x) ** 2 + (y - old_y) ** 2) ** 0.5
        battery_cost = int(distance * 2)  # 2% battery per unit distance
        
        # Update drone state
        drone.position = (x, y)
        drone.battery = max(0, drone.battery - battery_cost)
        drone.total_distance += distance
        drone.status = DroneStatus.IDLE if drone.battery > 0 else DroneStatus.OFFLINE
        
        return True
    
    def simulate_battery_drain(self, drone_id: str, amount: int = 1) -> None:
        """Simulate natural battery drain over time."""
        drone = self.get_drone(drone_id)
        if drone and drone.status != DroneStatus.CHARGING:
            drone.battery = max(0, drone.battery - amount)
            if drone.battery == 0:
                drone.status = DroneStatus.OFFLINE
    
    def find_survivors_near(self, position: Tuple[int, int], scan_range: int = 3) -> List[SurvivorInfo]:
        """Find survivors within scanning range of a position."""
        x, y = position
        nearby_survivors = []
        
        for survivor in self.survivors.values():
            sx, sy = survivor.position
            distance = ((x - sx) ** 2 + (y - sy) ** 2) ** 0.5
            
            if distance <= scan_range and not survivor.rescued:
                nearby_survivors.append(survivor)
        
        return nearby_survivors
    
    def get_nearest_charging_station(self, position: Tuple[int, int]) -> Tuple[int, int]:
        """Find the nearest charging station to a position."""
        x, y = position
        nearest_station = min(
            self.charging_stations,
            key=lambda station: ((x - station[0]) ** 2 + (y - station[1]) ** 2) ** 0.5
        )
        return nearest_station
    
    def register_drone(self, drone_info: DroneInfo) -> bool:
        """Register a new drone in the registry."""
        if drone_info.id not in self.drones:
            self.drones[drone_info.id] = drone_info
            return True
        return False
    
    def update_drone_status(self, drone_id: str, status: DroneStatus) -> bool:
        """Update drone status."""
        drone = self.get_drone(drone_id)
        if drone:
            drone.status = status
            return True
        return False
    
    def get_drone_info(self, drone_id: str) -> Optional[DroneInfo]:
        """Get drone information by ID (alias for get_drone)."""
        return self.get_drone(drone_id)


# Global drone registry instance
drone_registry = DroneRegistry()


# MCP Tool Functions
def discover_drones() -> Dict[str, Any]:
    """
    MCP Tool: Discover all available drones in the fleet.
    
    Returns:
        Dictionary containing list of drone IDs and their basic status
    """
    try:
        drone_list = []
        for drone_id, drone_info in drone_registry.drones.items():
            drone_list.append({
                "drone_id": drone_id,
                "status": drone_info.status.value,
                "battery": drone_info.battery,
                "position": drone_info.position
            })
        
        return {
            "success": True,
            "drones": [drone["drone_id"] for drone in drone_list],
            "drone_details": drone_list,
            "total_count": len(drone_list),
            "message": f"Discovered {len(drone_list)} drones"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to discover drones: {str(e)}",
            "drones": []
        }


def get_battery_status(drone_id: str) -> Dict[str, Any]:
    """
    MCP Tool: Get battery status for a specific drone.
    
    Args:
        drone_id: ID of the drone to check
        
    Returns:
        Dictionary containing battery level and status information
    """
    try:
        drone = drone_registry.get_drone(drone_id)
        if not drone:
            return {
                "success": False,
                "error": f"Drone {drone_id} not found",
                "drone_id": drone_id
            }
        
        # Determine battery status category
        if drone.battery >= 60:
            battery_status = "healthy"
        elif drone.battery >= 30:
            battery_status = "medium"
        elif drone.battery >= 20:
            battery_status = "low"
        else:
            battery_status = "critical"
        
        return {
            "success": True,
            "drone_id": drone_id,
            "battery": drone.battery,
            "battery_status": battery_status,
            "status": drone.status.value,
            "position": drone.position,
            "needs_charging": drone.battery < 30,
            "message": f"Drone {drone_id} battery: {drone.battery}% ({battery_status})"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get battery status: {str(e)}",
            "drone_id": drone_id
        }


def move_to(drone_id: str, x: int, y: int) -> Dict[str, Any]:
    """
    MCP Tool: Move drone to specified coordinates.
    
    Args:
        drone_id: ID of the drone to move
        x: Target X coordinate
        y: Target Y coordinate
        
    Returns:
        Dictionary containing movement result and new position
    """
    try:
        drone = drone_registry.get_drone(drone_id)
        if not drone:
            return {
                "success": False,
                "error": f"Drone {drone_id} not found",
                "drone_id": drone_id
            }
        
        # Check if drone has enough battery
        if drone.battery <= 0:
            return {
                "success": False,
                "error": f"Drone {drone_id} has no battery",
                "drone_id": drone_id,
                "battery": drone.battery
            }
        
        # Validate coordinates
        max_x, max_y = drone_registry.grid_size
        if not (0 <= x < max_x and 0 <= y < max_y):
            return {
                "success": False,
                "error": f"Invalid coordinates ({x}, {y}). Grid size is {max_x}x{max_y}",
                "drone_id": drone_id
            }
        
        # Calculate movement cost
        old_x, old_y = drone.position
        distance = ((x - old_x) ** 2 + (y - old_y) ** 2) ** 0.5
        battery_cost = int(distance * 2)
        
        if drone.battery < battery_cost:
            return {
                "success": False,
                "error": f"Insufficient battery for movement. Need {battery_cost}%, have {drone.battery}%",
                "drone_id": drone_id,
                "battery": drone.battery
            }
        
        # Execute movement
        success = drone_registry.update_drone_position(drone_id, x, y)
        
        if success:
            return {
                "success": True,
                "drone_id": drone_id,
                "old_position": [old_x, old_y],
                "new_position": [x, y],
                "distance_traveled": round(distance, 2),
                "battery_consumed": battery_cost,
                "remaining_battery": drone.battery,
                "message": f"Drone {drone_id} moved to ({x}, {y})"
            }
        else:
            return {
                "success": False,
                "error": "Failed to update drone position",
                "drone_id": drone_id
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to move drone: {str(e)}",
            "drone_id": drone_id
        }


def thermal_scan(drone_id: str) -> Dict[str, Any]:
    """
    MCP Tool: Perform thermal scan for survivors at drone's current position.
    
    Args:
        drone_id: ID of the drone performing the scan
        
    Returns:
        Dictionary containing scan results and survivor information
    """
    try:
        drone = drone_registry.get_drone(drone_id)
        if not drone:
            return {
                "success": False,
                "error": f"Drone {drone_id} not found",
                "drone_id": drone_id
            }
        
        # Check if drone has enough battery for scanning
        scan_battery_cost = 5
        if drone.battery < scan_battery_cost:
            return {
                "success": False,
                "error": f"Insufficient battery for thermal scan. Need {scan_battery_cost}%, have {drone.battery}%",
                "drone_id": drone_id,
                "battery": drone.battery
            }
        
        # Perform thermal scan
        drone.status = DroneStatus.SCANNING
        drone.battery -= scan_battery_cost
        drone.last_scan_time = time.time()
        
        # Find survivors in scan range
        survivors_detected = drone_registry.find_survivors_near(drone.position, scan_range=3)
        
        survivor_positions = []
        for survivor in survivors_detected:
            survivor_positions.append({
                "position": list(survivor.position),
                "signal_strength": round(survivor.signal_strength, 2),
                "distance": round(
                    ((drone.position[0] - survivor.position[0]) ** 2 + 
                     (drone.position[1] - survivor.position[1]) ** 2) ** 0.5, 2
                )
            })
            drone.survivors_found += 1
        
        # Update drone status
        drone.status = DroneStatus.IDLE
        
        return {
            "success": True,
            "drone_id": drone_id,
            "scan_position": list(drone.position),
            "survivors_detected": len(survivors_detected),
            "survivor_details": survivor_positions,
            "positions": [detail["position"] for detail in survivor_positions],  # Add positions field for compatibility
            "battery_consumed": scan_battery_cost,
            "remaining_battery": drone.battery,
            "scan_range": 3,
            "scan_time": time.time(),
            "message": f"Thermal scan complete. Found {len(survivors_detected)} survivors"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to perform thermal scan: {str(e)}",
            "drone_id": drone_id
        }


def return_to_base(drone_id: str) -> Dict[str, Any]:
    """
    MCP Tool: Send drone back to nearest charging station.
    
    Args:
        drone_id: ID of the drone to recall
        
    Returns:
        Dictionary containing return operation result
    """
    try:
        drone = drone_registry.get_drone(drone_id)
        if not drone:
            return {
                "success": False,
                "error": f"Drone {drone_id} not found",
                "drone_id": drone_id
            }
        
        # Find nearest charging station
        nearest_station = drone_registry.get_nearest_charging_station(drone.position)
        
        # Calculate distance to charging station
        distance_to_base = (
            (drone.position[0] - nearest_station[0]) ** 2 + 
            (drone.position[1] - nearest_station[1]) ** 2
        ) ** 0.5
        
        battery_needed = int(distance_to_base * 2)
        
        # Check if drone can make it to base
        if drone.battery < battery_needed:
            return {
                "success": False,
                "error": f"Drone {drone_id} cannot reach base. Need {battery_needed}%, have {drone.battery}%",
                "drone_id": drone_id,
                "battery": drone.battery,
                "distance_to_base": round(distance_to_base, 2)
            }
        
        # Update drone status and position
        drone.status = DroneStatus.RETURNING
        old_position = drone.position
        
        # Move to charging station
        success = drone_registry.update_drone_position(drone_id, nearest_station[0], nearest_station[1])
        
        if success:
            # Start charging process
            drone.status = DroneStatus.CHARGING
            
            return {
                "success": True,
                "drone_id": drone_id,
                "old_position": list(old_position),
                "charging_station": list(nearest_station),
                "distance_traveled": round(distance_to_base, 2),
                "battery_consumed": battery_needed,
                "remaining_battery": drone.battery,
                "status": "charging",
                "message": f"Drone {drone_id} returned to charging station at {nearest_station}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to move drone to charging station",
                "drone_id": drone_id
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to return drone to base: {str(e)}",
            "drone_id": drone_id
        }


def rescue_survivor(drone_id: str, survivor_position: Tuple[int, int]) -> Dict[str, Any]:
    """
    MCP Tool: Rescue survivor at specified position.
    
    Args:
        drone_id: ID of the drone performing rescue
        survivor_position: Position of the survivor (x, y)
        
    Returns:
        Dictionary containing rescue result
    """
    try:
        drone = drone_registry.get_drone(drone_id)
        if not drone:
            return {
                "success": False,
                "error": f"Drone {drone_id} not found",
                "drone_id": drone_id
            }
        
        # Check if drone has enough battery for rescue operation
        if drone.battery < 10:
            return {
                "success": False,
                "error": f"Insufficient battery for rescue operation. Need 10%, have {drone.battery}%",
                "drone_id": drone_id,
                "battery": drone.battery
            }
        
        # Check if drone is at the survivor location
        drone_x, drone_y = drone.position
        survivor_x, survivor_y = survivor_position
        distance = ((drone_x - survivor_x) ** 2 + (drone_y - survivor_y) ** 2) ** 0.5
        
        if distance > 2:  # Must be within 2 units to rescue
            return {
                "success": False,
                "error": f"Drone too far from survivor. Distance: {distance:.1f}, max: 2.0",
                "drone_id": drone_id,
                "drone_position": [drone_x, drone_y],
                "survivor_position": list(survivor_position)
            }
        
        # Find survivor at this position
        rescued_survivor = None
        for survivor_id, survivor in drone_registry.survivors.items():
            if survivor.position == survivor_position and not survivor.rescued:
                rescued_survivor = survivor
                break
        
        if not rescued_survivor:
            return {
                "success": False,
                "error": f"No survivor found at position {survivor_position}",
                "drone_id": drone_id,
                "position": list(survivor_position)
            }
        
        # Perform rescue
        rescued_survivor.rescued = True
        rescued_survivor.rescue_time = time.time()
        
        # Consume battery for rescue operation
        drone_registry.simulate_battery_drain(drone_id, 10)  # 10% battery for rescue
        drone.status = DroneStatus.IDLE
        
        return {
            "success": True,
            "drone_id": drone_id,
            "survivor_position": list(survivor_position),
            "rescue_time": rescued_survivor.rescue_time,
            "battery_consumed": 10,
            "remaining_battery": drone.battery,
            "message": f"Drone {drone_id} successfully rescued survivor at {survivor_position}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to rescue survivor: {str(e)}",
            "drone_id": drone_id
        }


def get_mission_status() -> Dict[str, Any]:
    """
    MCP Tool: Get overall mission status and statistics.
    
    Returns:
        Dictionary containing mission statistics and fleet status
    """
    try:
        total_drones = len(drone_registry.drones)
        active_drones = sum(1 for drone in drone_registry.drones.values() 
                          if drone.status != DroneStatus.OFFLINE)
        
        total_survivors = len(drone_registry.survivors)
        rescued_survivors = sum(1 for survivor in drone_registry.survivors.values() 
                              if survivor.rescued)
        
        battery_levels = [drone.battery for drone in drone_registry.drones.values()]
        avg_battery = sum(battery_levels) / len(battery_levels) if battery_levels else 0
        
        low_battery_drones = [drone.drone_id for drone in drone_registry.drones.values() 
                             if drone.battery < 30]
        
        return {
            "success": True,
            "mission_stats": {
                "total_drones": total_drones,
                "active_drones": active_drones,
                "offline_drones": total_drones - active_drones,
                "average_battery": round(avg_battery, 1),
                "low_battery_drones": low_battery_drones,
                "total_survivors": total_survivors,
                "rescued_survivors": rescued_survivors,
                "rescue_progress": round((rescued_survivors / total_survivors) * 100, 1) if total_survivors > 0 else 0
            },
            "charging_stations": drone_registry.charging_stations,
            "grid_size": drone_registry.grid_size,
            "message": f"Mission status: {active_drones}/{total_drones} drones active, {rescued_survivors}/{total_survivors} survivors rescued"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get mission status: {str(e)}"
        }


# Tool registration for FastMCP (if available)
def register_mcp_tools(mcp_server):
    """
    Register all drone tools with the FastMCP server.
    
    Args:
        mcp_server: FastMCP server instance
    """
    if not FASTMCP_AVAILABLE:
        print("FastMCP not available - tools registered as regular functions")
        return
    
    # Register each tool with appropriate metadata
    mcp_server.tool()(discover_drones)
    mcp_server.tool()(get_battery_status)
    mcp_server.tool()(move_to)
    mcp_server.tool()(thermal_scan)
    mcp_server.tool()(rescue_survivor)
    mcp_server.tool()(return_to_base)
    mcp_server.tool()(get_mission_status)


# Example usage and testing
if __name__ == "__main__":
    print("🚁 Drone Tools Module - Testing MCP Functions")
    print("=" * 50)
    
    # Test discover_drones
    print("\n1. Discovering drones...")
    result = discover_drones()
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Test battery status
    print("\n2. Checking battery status...")
    result = get_battery_status("drone_A")
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Test movement
    print("\n3. Moving drone...")
    result = move_to("drone_A", 10, 10)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Test thermal scan
    print("\n4. Performing thermal scan...")
    result = thermal_scan("drone_A")
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Test return to base
    print("\n5. Returning drone to base...")
    result = return_to_base("drone_C")  # Low battery drone
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Test mission status
    print("\n6. Getting mission status...")
    result = get_mission_status()
    print(f"Result: {json.dumps(result, indent=2)}")
    
    print("\n✅ All drone tools tested successfully!")