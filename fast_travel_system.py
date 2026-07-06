"""
Fast Travel System
Allows players to quickly travel to owned homes and rented inn rooms
"""

class FastTravelSystem:
    def __init__(self):
        self.unlocked_locations = {}  # {location_name: (x, y, description)}
        
    def unlock_location(self, location_name, x, y, description=""):
        """
        Unlock a fast travel location
        
        Args:
            location_name: Unique identifier for the location
            x, y: World coordinates
            description: Human-readable description
        """
        self.unlocked_locations[location_name] = {
            'x': x,
            'y': y,
            'description': description
        }
        
    def remove_location(self, location_name):
        """Remove a fast travel location (e.g., when rental expires)"""
        if location_name in self.unlocked_locations:
            del self.unlocked_locations[location_name]
            
    def get_available_locations(self):
        """Get list of all unlocked fast travel locations"""
        return list(self.unlocked_locations.keys())
    
    def get_location_info(self, location_name):
        """Get coordinates and description for a location"""
        return self.unlocked_locations.get(location_name)
    
    def travel_to(self, player, location_name):
        """
        Fast travel player to a location
        
        Returns:
            tuple: (success: bool, message: str, x: int, y: int)
        """
        if location_name not in self.unlocked_locations:
            return False, f"Location '{location_name}' is not available for fast travel", None, None
            
        location = self.unlocked_locations[location_name]
        return True, f"Fast traveled to {location_name}", location['x'], location['y']
