"""
Mission Memory Module for Disaster Rescue Drone System

This module handles mission memory and logs for the AI agent.
It provides functionality to:
1. Read mission history from logs
2. Append new mission events
3. Provide mission context to the AI agent
4. Manage mission log lifecycle

The memory module is used by the reasoning agent to reflect on past actions
and make informed decisions based on mission history.
"""

import os
import datetime
from typing import List, Optional
from pathlib import Path


class MissionMemory:
    """
    Handles mission memory and logging for the rescue command agent.
    
    This class manages the mission log file and provides methods to:
    - Load existing mission history
    - Add new mission events with timestamps
    - Retrieve recent events for context
    - Clear mission logs when needed
    
    Log format: [HH:MM] Event description
    Example: [00:01] 3 drones discovered
    """
    
    def __init__(self, log_file: str = "logs/mission.log"):
        """
        Initialize the mission memory system.
        
        Args:
            log_file: Path to the mission log file
        """
        self.log_file = Path(log_file)
        self.mission_start_time = datetime.datetime.now()
        
        # Ensure logs directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file if it doesn't exist
        if not self.log_file.exists():
            self._initialize_log()
    
    def _initialize_log(self) -> None:
        """Initialize a new mission log file with header."""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== MISSION LOG STARTED: {self.mission_start_time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    def _get_mission_time(self) -> str:
        """
        Get current mission time in [MM:SS] format.
        
        Returns:
            Formatted time string since mission start
        """
        elapsed = datetime.datetime.now() - self.mission_start_time
        total_seconds = int(elapsed.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"[{minutes:02d}:{seconds:02d}]"
    
    def load_memory(self) -> List[str]:
        """
        Read the complete mission history from the log file.
        
        Returns:
            List of all mission events as strings
        """
        try:
            if not self.log_file.exists():
                return []
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filter out header lines and empty lines
            events = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('==='):
                    events.append(line)
            
            return events
        
        except Exception as e:
            print(f"Error loading mission memory: {e}")
            return []
    
    def add_event(self, text: str) -> None:
        """
        Append a new mission event to the log with timestamp.
        
        Args:
            text: Description of the mission event
        """
        try:
            timestamp = self._get_mission_time()
            event_line = f"{timestamp} {text}\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(event_line)
            
            print(f"Mission Log: {timestamp} {text}")
        
        except Exception as e:
            print(f"Error adding event to mission log: {e}")
    
    def get_recent_events(self, n: int = 10) -> List[str]:
        """
        Return the last n mission events for context.
        
        Args:
            n: Number of recent events to retrieve
            
        Returns:
            List of the most recent n mission events
        """
        all_events = self.load_memory()
        return all_events[-n:] if all_events else []
    
    def clear_memory(self) -> None:
        """
        Reset the mission log by clearing all events.
        This starts a fresh mission log.
        """
        try:
            self.mission_start_time = datetime.datetime.now()
            self._initialize_log()
            print("Mission memory cleared - new mission started")
        
        except Exception as e:
            print(f"Error clearing mission memory: {e}")
    
    def get_mission_summary(self) -> dict:
        """
        Get a summary of the current mission state.
        
        Returns:
            Dictionary containing mission statistics and recent events
        """
        events = self.load_memory()
        elapsed = datetime.datetime.now() - self.mission_start_time
        
        return {
            "mission_duration": str(elapsed).split('.')[0],  # Remove microseconds
            "total_events": len(events),
            "recent_events": self.get_recent_events(5),
            "mission_start": self.mission_start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def search_events(self, keyword: str) -> List[str]:
        """
        Search for events containing a specific keyword.
        
        Args:
            keyword: Keyword to search for in mission events
            
        Returns:
            List of events containing the keyword
        """
        all_events = self.load_memory()
        return [event for event in all_events if keyword.lower() in event.lower()]


# Example usage and testing
if __name__ == "__main__":
    # Create mission memory instance
    memory = MissionMemory()
    
    # Example mission events
    memory.add_event("Mission started - initializing drone fleet")
    memory.add_event("3 drones discovered")
    memory.add_event("Drone A scanning sector 2")
    memory.add_event("Drone B battery 25%")
    memory.add_event("Survivor detected at position (5, 8)")
    memory.add_event("Drone C dispatched to rescue survivor")
    
    # Display recent events
    print("\n=== Recent Mission Events ===")
    recent = memory.get_recent_events(3)
    for event in recent:
        print(event)
    
    # Display mission summary
    print("\n=== Mission Summary ===")
    summary = memory.get_mission_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Search for battery-related events
    print("\n=== Battery Events ===")
    battery_events = memory.search_events("battery")
    for event in battery_events:
        print(event)