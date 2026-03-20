"""
Central Command Center for Drone Swarm Operations
Main coordination point for all drone activities, mission planning, and status monitoring
"""

import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from agent.memory import MissionMemory
from mcp_server.drone_tools import DroneRegistry, DroneStatus, DroneInfo, SurvivorInfo


class MissionStatus(Enum):
    """Mission status enumeration"""
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABORTED = "aborted"
    PAUSED = "paused"


class CommandPriority(Enum):
    """Command priority levels"""
    CRITICAL = 1    # Emergency situations
    HIGH = 2        # Urgent rescue operations
    NORMAL = 3      # Standard operations
    LOW = 4         # Maintenance and patrol


@dataclass
class Mission:
    """Mission data structure"""
    id: str
    name: str
    status: MissionStatus
    priority: CommandPriority
    assigned_drones: List[str]
    target_locations: List[Tuple[int, int]]
    created_at: datetime
    updated_at: datetime
    completion_percentage: float = 0.0
    description: str = ""


@dataclass
class CommandOrder:
    """Command order for drone operations"""
    id: str
    drone_id: str
    command_type: str  # "move", "rescue", "charge", "patrol", "return"
    target_position: Optional[Tuple[int, int]]
    priority: CommandPriority
    issued_at: datetime
    status: str = "pending"  # "pending", "executing", "completed", "failed"
    parameters: Dict = None


class CentralCommandCenter:
    """
    Central Command Center for coordinating all drone operations
    
    This serves as the main hub where:
    - All drones report their status
    - Missions are planned and coordinated
    - Resources are allocated and managed
    - Real-time monitoring and control
    """
    
    def __init__(self):
        """Initialize the Central Command Center"""
        self.drone_registry = DroneRegistry()
        self.mission_memory = MissionMemory()
        
        # Command center state
        self.active_missions: Dict[str, Mission] = {}
        self.pending_orders: Dict[str, CommandOrder] = {}
        self.completed_orders: List[CommandOrder] = []
        
        # System status
        self.command_center_status = "operational"
        self.total_missions_completed = 0
        self.total_rescues_completed = 0
        self.system_start_time = datetime.now()
        
        # Real-time tracking
        self.drone_positions: Dict[str, Tuple[int, int]] = {}
        self.survivor_locations: Dict[str, SurvivorInfo] = {}
        self.charging_stations: List[Tuple[int, int]] = []
        
        # Home base configuration
        self.home_base_position = (10, 10)  # Default home base position
        self.emergency_recall_active = False
    
    def register_drone(self, drone_info: DroneInfo) -> bool:
        """Register a new drone with the command center"""
        success = self.drone_registry.register_drone(drone_info)
        if success:
            self.drone_positions[drone_info.drone_id] = drone_info.position
            self.mission_memory.add_event(f"Drone {drone_info.drone_id} registered at position {drone_info.position}")
            print(f"✅ Drone {drone_info.drone_id} registered with Command Center")
        return success
    
    def update_drone_status(self, drone_id: str, status: DroneStatus, position: Tuple[int, int]) -> None:
        """Update drone status and position"""
        if self.drone_registry.update_drone_status(drone_id, status):
            self.drone_positions[drone_id] = position
            
            # Log critical status changes
            if status == DroneStatus.CHARGING:
                # Check if this is due to low battery (critical situation)
                drone_info = self.drone_registry.get_drone_info(drone_id)
                if drone_info and drone_info.battery < 20:
                    self.mission_memory.add_event(f"CRITICAL: Drone {drone_id} low battery at {position}")
                    self._issue_emergency_return_order(drone_id)
            elif status == DroneStatus.RETURNING:
                self.mission_memory.add_event(f"Drone {drone_id} returning to base from {position}")
            elif status == DroneStatus.SCANNING:
                self.mission_memory.add_event(f"Drone {drone_id} performing rescue scan at {position}")
    
    def create_mission(self, name: str, target_locations: List[Tuple[int, int]], 
                      priority: CommandPriority = CommandPriority.NORMAL, 
                      description: str = "") -> str:
        """Create a new mission and assign drones"""
        mission_id = f"mission_{int(time.time())}"
        
        # Select available drones for the mission
        available_drones = self._select_available_drones(len(target_locations))
        
        mission = Mission(
            id=mission_id,
            name=name,
            status=MissionStatus.PLANNING,
            priority=priority,
            assigned_drones=available_drones,
            target_locations=target_locations,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            description=description
        )
        
        self.active_missions[mission_id] = mission
        self.mission_memory.add_event(f"Mission created: {name} with {len(available_drones)} drones")
        
        print(f"📋 Mission '{name}' created with ID: {mission_id}")
        print(f"🚁 Assigned drones: {', '.join(available_drones)}")
        
        return mission_id
    
    def start_mission(self, mission_id: str) -> bool:
        """Start executing a planned mission"""
        if mission_id not in self.active_missions:
            return False
        
        mission = self.active_missions[mission_id]
        mission.status = MissionStatus.ACTIVE
        mission.updated_at = datetime.now()
        
        # Issue orders to assigned drones
        for i, drone_id in enumerate(mission.assigned_drones):
            if i < len(mission.target_locations):
                target = mission.target_locations[i]
                self._issue_move_order(drone_id, target, mission.priority)
        
        self.mission_memory.add_event(f"Mission {mission.name} started")
        print(f"🚀 Mission '{mission.name}' started")
        return True
    
    def issue_command(self, drone_id: str, command_type: str, 
                     target_position: Optional[Tuple[int, int]] = None,
                     priority: CommandPriority = CommandPriority.NORMAL,
                     parameters: Dict = None) -> str:
        """Issue a direct command to a specific drone"""
        order_id = f"order_{int(time.time())}_{drone_id}"
        
        order = CommandOrder(
            id=order_id,
            drone_id=drone_id,
            command_type=command_type,
            target_position=target_position,
            priority=priority,
            issued_at=datetime.now(),
            parameters=parameters or {}
        )
        
        self.pending_orders[order_id] = order
        self.mission_memory.add_event(f"Command issued to {drone_id}: {command_type}")
        
        print(f"📡 Command '{command_type}' issued to drone {drone_id}")
        return order_id
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        total_drones = len(self.drone_registry.drones)
        active_drones = len([d for d in self.drone_registry.drones.values() 
                           if d.status not in [DroneStatus.OFFLINE, DroneStatus.CHARGING]])
        
        active_missions = len([m for m in self.active_missions.values() 
                             if m.status == MissionStatus.ACTIVE])
        
        # Count drones at home base
        drones_at_home = len([pos for pos in self.drone_positions.values() 
                             if pos == self.home_base_position])
        
        return {
            "command_center_status": self.command_center_status,
            "system_uptime": str(datetime.now() - self.system_start_time),
            "home_base_position": self.home_base_position,
            "drones_at_home_base": drones_at_home,
            "emergency_recall_active": self.emergency_recall_active,
            "total_drones": total_drones,
            "active_drones": active_drones,
            "active_missions": active_missions,
            "pending_orders": len(self.pending_orders),
            "completed_missions": self.total_missions_completed,
            "total_rescues": self.total_rescues_completed,
            "drone_positions": self.drone_positions,
            "survivor_count": len(self.survivor_locations)
        }
    
    def get_mission_status(self, mission_id: str) -> Optional[Dict]:
        """Get detailed status of a specific mission"""
        if mission_id not in self.active_missions:
            return None
        
        mission = self.active_missions[mission_id]
        
        # Calculate progress
        completed_objectives = 0
        for drone_id in mission.assigned_drones:
            drone_info = self.drone_registry.get_drone_info(drone_id)
            if drone_info and drone_info.status == DroneStatus.IDLE:
                # Consider idle drones as having completed their objectives
                completed_objectives += 1
        
        progress = (completed_objectives / len(mission.assigned_drones)) * 100 if mission.assigned_drones else 0
        mission.completion_percentage = progress
        
        return asdict(mission)
    
    def emergency_recall_all(self) -> None:
        """Emergency recall of all drones to home base"""
        print("🚨 EMERGENCY RECALL INITIATED - ALL DRONES RETURN TO HOME BASE")
        self.mission_memory.add_event("EMERGENCY: All drones recalled to home base")
        self.emergency_recall_active = True
        
        for drone_id in self.drone_registry.drones.keys():
            self.issue_command(
                drone_id, 
                "return_to_home_base", 
                self.home_base_position, 
                CommandPriority.CRITICAL
            )
        
        # Pause all active missions
        for mission in self.active_missions.values():
            if mission.status == MissionStatus.ACTIVE:
                mission.status = MissionStatus.PAUSED
                mission.updated_at = datetime.now()
    
    def cancel_emergency_recall(self) -> None:
        """Cancel emergency recall and resume normal operations"""
        print("✅ Emergency recall cancelled - drones resume normal operations")
        self.mission_memory.add_event("Emergency recall cancelled")
        self.emergency_recall_active = False
        
        # Resume paused missions
        for mission in self.active_missions.values():
            if mission.status == MissionStatus.PAUSED:
                mission.status = MissionStatus.ACTIVE
                mission.updated_at = datetime.now()
    
    def set_home_base_position(self, position: Tuple[int, int]) -> None:
        """Set the home base position"""
        old_position = self.home_base_position
        self.home_base_position = position
        self.mission_memory.add_event(f"Home base relocated from {old_position} to {position}")
        print(f"🏠 Home base relocated to {position}")
    
    def get_home_base_status(self) -> Dict:
        """Get home base status and drone count"""
        drones_at_home = len([pos for pos in self.drone_positions.values() 
                             if pos == self.home_base_position])
        
        return {
            "position": self.home_base_position,
            "drones_at_base": drones_at_home,
            "emergency_recall_active": self.emergency_recall_active,
            "total_drones": len(self.drone_registry.drones)
        }
    
    def order_return_to_base(self, drone_id: str) -> str:
        """Order a specific drone to return to home base"""
        return self.issue_command(
            drone_id,
            "return_to_home_base",
            self.home_base_position,
            CommandPriority.HIGH,
            {"reason": "ordered_return"}
        )
    
    def add_survivor_location(self, survivor_info: SurvivorInfo) -> None:
        """Register a new survivor location"""
        self.survivor_locations[survivor_info.id] = survivor_info
        self.mission_memory.add_event(f"Survivor detected at {survivor_info.position}")
        
        # Auto-assign nearest available drone for rescue
        self._auto_assign_rescue_mission(survivor_info)
    
    def _select_available_drones(self, count: int) -> List[str]:
        """Select available drones for mission assignment"""
        available = []
        for drone_id, drone_info in self.drone_registry.drones.items():
            if (drone_info.status in [DroneStatus.IDLE] and 
                len(available) < count):
                available.append(drone_id)
        return available
    
    def _issue_move_order(self, drone_id: str, target: Tuple[int, int], 
                         priority: CommandPriority) -> None:
        """Issue a move order to a drone"""
        self.issue_command(drone_id, "move", target, priority)
    
    def _issue_emergency_return_order(self, drone_id: str) -> None:
        """Issue emergency return to base order"""
        # Find nearest charging station
        drone_pos = self.drone_positions.get(drone_id, (0, 0))
        nearest_station = self._find_nearest_charging_station(drone_pos)
        
        self.issue_command(
            drone_id, 
            "emergency_return", 
            nearest_station, 
            CommandPriority.CRITICAL
        )
    
    def _find_nearest_charging_station(self, position: Tuple[int, int]) -> Tuple[int, int]:
        """Find the nearest charging station to a position"""
        if not self.charging_stations:
            return (0, 0)  # Default base position
        
        min_distance = float('inf')
        nearest = self.charging_stations[0]
        
        for station in self.charging_stations:
            distance = abs(station[0] - position[0]) + abs(station[1] - position[1])
            if distance < min_distance:
                min_distance = distance
                nearest = station
        
        return nearest
    
    def _auto_assign_rescue_mission(self, survivor_info: SurvivorInfo) -> None:
        """Automatically assign the nearest available drone for rescue"""
        available_drones = self._select_available_drones(1)
        
        if available_drones:
            drone_id = available_drones[0]
            mission_id = self.create_mission(
                f"Rescue {survivor_info.id}",
                [survivor_info.position],
                CommandPriority.HIGH,
                f"Emergency rescue of survivor at {survivor_info.position}"
            )
            self.start_mission(mission_id)
            print(f"🆘 Auto-assigned drone {drone_id} for rescue mission")
    
    def shutdown(self) -> None:
        """Gracefully shutdown the command center"""
        print("🏢 Central Command Center shutting down...")
        self.emergency_recall_all()
        self.command_center_status = "shutdown"
        self.mission_memory.add_event("Central Command Center shutdown")


# Global command center instance
command_center = CentralCommandCenter()


def get_command_center() -> CentralCommandCenter:
    """Get the global command center instance"""
    return command_center


if __name__ == "__main__":
    # Demo of command center functionality
    print("🏢 Central Command Center Demo")
    print("=" * 50)
    
    # Initialize command center
    cc = CentralCommandCenter()
    
    # Register some drones
    from mcp_server.drone_tools import DroneInfo, DroneStatus
    
    drone1 = DroneInfo("drone_001", (5, 5), DroneStatus.IDLE, 85.0)
    drone2 = DroneInfo("drone_002", (10, 10), DroneStatus.IDLE, 92.0)
    drone3 = DroneInfo("drone_003", (15, 15), DroneStatus.IDLE, 78.0)
    
    cc.register_drone(drone1)
    cc.register_drone(drone2)
    cc.register_drone(drone3)
    
    # Create and start a mission
    mission_id = cc.create_mission(
        "Search and Rescue Alpha",
        [(8, 12), (16, 8), (3, 18)],
        CommandPriority.HIGH,
        "Multi-point search and rescue operation"
    )
    
    cc.start_mission(mission_id)
    
    # Show system status
    status = cc.get_system_status()
    print("\n📊 System Status:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Command Center demo completed")