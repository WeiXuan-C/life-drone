"""
Mission Logging Utility
Handles logging of mission events and system activities
"""

import datetime
import os

def log_event(text):
    """Log an event to the mission log file"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {text}"
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Write to file
    with open("logs/mission.log", "a") as f:
        f.write(log_entry + "\n")
    
    return log_entry

def clear_log():
    """Clear the mission log file"""
    try:
        with open("logs/mission.log", "w") as f:
            f.write("")
        return True
    except Exception:
        return False

def read_log(lines=None):
    """Read mission log entries"""
    try:
        with open("logs/mission.log", "r") as f:
            log_lines = f.readlines()
        
        if lines:
            return log_lines[-lines:]
        return log_lines
    except FileNotFoundError:
        return []