"""
Resource Respawn System with Weather and Seasonal Effects
Tracks harvested resources and manages respawn based on weather conditions
"""

import time
import json
import os

class ResourceRespawnManager:
    def __init__(self, game_time, weather_system):
        self.game_time = game_time
        self.weather_system = weather_system
        self.harvested_resources = {}  # {(x, y): {resource_type, harvested_day, harvested_year, harvested_month}}
        self.save_file = "resource_respawn.json"
        self.load_data()
        
        # Base respawn times in game days (forces strategic resource planning)
        self.base_respawn_times = {
            'tree': 14,      # 2 weeks (long growth time - plan carefully)
            'bush': 7,       # 1 week
            'mushroom': 9,   # 9 days (moderately rare)
            'mushroom_patch': 9  # 9 days
        }
        
    def register_harvest(self, x, y, resource_type):
        """Register a resource harvest at coordinates"""
        # Ensure coordinates are integers to prevent float/int key mismatches
        x, y = int(x), int(y)
        
        # Only track resources that actually respawn
        # Grass is abundant and not tracked (reduces overhead)
        # Trees: 7 days, Bushes: 7 days, Mushrooms: 5 days
        respawnable_types = ('tree', 'bush', 'mushroom', 'mushroom_patch')
        if resource_type not in respawnable_types:
            return  # Don't track this harvest
        
        key = f"{x},{y}"
        self.harvested_resources[key] = {
            'type': resource_type,
            'harvested_day': self.game_time.day_count,
            'harvested_month': self.game_time.month_count,
            'harvested_year': self.game_time.year_count,
            'harvest_time': time.time()  # Real-world time for reference
        }
        self.save_data()
    
    def get_weather_modifier(self, resource_type, weather):
        """Get respawn time multiplier based on weather"""
        weather = weather.lower()
        
        modifiers = {
            'mushroom_patch': {
                'light_rain': 0.7,
                'heavy_rain': 0.7,
                'fog': 0.8,
                'clear': 1.3,
                'heatwave': 1.5,
                'storm': 0.9,  # After storm, good for mushrooms
                'snow': 2.0,
                'default': 1.0
            },
            'tree': {
                'light_rain': 0.9,
                'heavy_rain': 0.85,
                'clear': 1.1,
                'heatwave': 1.5,  # Drought stress
                'storm': 1.2,
                'snow': 2.0,  # Dormant
                'fog': 1.0,
                'default': 1.0
            },
            'bush': {
                'light_rain': 0.95,
                'heavy_rain': 1.1,  # Too much water
                'clear': 1.0,
                'heatwave': 1.4,
                'storm': 1.3,
                'snow': 1.6,
                'fog': 1.1,
                'default': 1.0
            },
            'mushroom': {
                'light_rain': 0.7,
                'heavy_rain': 0.7,
                'fog': 0.8,
                'clear': 1.3,
                'heatwave': 1.5,
                'storm': 0.9,
                'snow': 2.0,
                'default': 1.0
            }
        }
        
        resource_modifiers = modifiers.get(resource_type, {})
        return resource_modifiers.get(weather, resource_modifiers.get('default', 1.0))
    
    def get_seasonal_modifier(self, season):
        """Get respawn time multiplier based on season"""
        modifiers = {
            'Spring': 0.8,   # Growth burst
            'Summer': 1.0,   # Normal growth
            'Autumn': 1.1,   # Preparing for winter
            'Winter': 1.5    # Dormant/slow
        }
        return modifiers.get(season, 1.0)
    
    def is_growth_halted(self, weather):
        """Check if extreme weather halts all growth"""
        weather = weather.lower()
        halt_weather = ['snow', 'heatwave', 'tornado', 'tsunami']
        return weather in halt_weather
    
    def calculate_growth_progress(self, harvest_data):
        """Calculate how much a resource has grown (0.0 to 1.0)"""
        resource_type = harvest_data['type']
        base_days = self.base_respawn_times.get(resource_type, 7)
        
        # Calculate days passed
        harvest_year = harvest_data['harvested_year']
        harvest_month = harvest_data['harvested_month']
        harvest_day = harvest_data['harvested_day']
        
        current_year = self.game_time.year_count
        current_month = self.game_time.month_count
        current_day = self.game_time.day_count
        
        # Simple day calculation (could be more complex with calendar)
        days_passed = (current_year - harvest_year) * 360  # Assuming 360 days/year
        days_passed += (current_month - harvest_month) * 30  # Assuming 30 days/month
        days_passed += (current_day - harvest_day)
        
        if days_passed < 0:
            days_passed = 0
        
        # Get current weather and season modifiers
        current_weather, _ = self.weather_system.get_current_weather()
        current_season = self.game_time.get_season()
        
        # Check if growth is halted
        if self.is_growth_halted(current_weather):
            # No growth during extreme weather, but count the time
            pass
        
        weather_mod = self.get_weather_modifier(resource_type, current_weather)
        season_mod = self.get_seasonal_modifier(current_season)
        
        # Effective days needed (base * modifiers)
        effective_days_needed = base_days * weather_mod * season_mod
        
        # Calculate progress
        progress = days_passed / effective_days_needed
        return min(progress, 1.0)
    
    def get_visual_state(self, progress):
        """Get visual state based on growth progress"""
        if progress < 0.25:
            return 'dormant'  # Just harvested, bare ground/stump
        elif progress < 0.50:
            return 'sprout'   # Sapling/sprout visible
        elif progress < 0.75:
            return 'growing'  # Young tree/bush
        elif progress < 1.0:
            return 'mature'   # Nearly ready (could show slightly transparent)
        else:
            return 'ready'    # Fully harvestable
    
    def check_respawns(self, world, player_x=None, player_y=None):
        """Check and respawn ready resources"""
        respawned = []
        to_remove = []
        nearby_respawned = []  # Resources that respawned near player
        
        for coord_key, harvest_data in self.harvested_resources.items():
            progress = self.calculate_growth_progress(harvest_data)
            
            if progress >= 1.0:
                # Resource is ready to respawn
                # Parse coordinates and ensure they're integers
                coord_parts = coord_key.split(',')
                x = int(float(coord_parts[0]))
                y = int(float(coord_parts[1]))
                resource_type = harvest_data['type']
                
                # Respawn the resource
                from tile import Tile
                new_tile = Tile(ground=resource_type)
                world.set_tile(x, y, new_tile)
                
                respawned.append((x, y, resource_type))
                to_remove.append(coord_key)
                
                # Check if respawn is near player (for notifications)
                if player_x is not None and player_y is not None:
                    distance = ((x - player_x)**2 + (y - player_y)**2)**0.5
                    if distance < 300:  # Within ~6 tiles
                        nearby_respawned.append((x, y, resource_type, distance))
        
        # Remove respawned resources from tracking
        for key in to_remove:
            del self.harvested_resources[key]
        
        if to_remove:
            self.save_data()
        
        return respawned, nearby_respawned
    
    def get_resource_state(self, x, y):
        """Get the current state of a resource at coordinates"""
        # Ensure coordinates are integers to prevent float/int key mismatches
        x, y = int(x), int(y)
        key = f"{x},{y}"
        if key not in self.harvested_resources:
            return None
        
        harvest_data = self.harvested_resources[key]
        progress = self.calculate_growth_progress(harvest_data)
        visual_state = self.get_visual_state(progress)
        
        return {
            'type': harvest_data['type'],
            'progress': progress,
            'visual_state': visual_state,
            'days_since_harvest': self._calculate_days_passed(harvest_data)
        }
    
    def _calculate_days_passed(self, harvest_data):
        """Helper to calculate days passed"""
        harvest_year = harvest_data['harvested_year']
        harvest_month = harvest_data['harvested_month']
        harvest_day = harvest_data['harvested_day']
        
        current_year = self.game_time.year_count
        current_month = self.game_time.month_count
        current_day = self.game_time.day_count
        
        days_passed = (current_year - harvest_year) * 360
        days_passed += (current_month - harvest_month) * 30
        days_passed += (current_day - harvest_day)
        
        return max(days_passed, 0)
    
    def get_all_respawning_resources(self):
        """Get all tracked resources with their progress (for debug menu)"""
        resources_info = []
        
        for coord_key, harvest_data in self.harvested_resources.items():
            progress = self.calculate_growth_progress(harvest_data)
            coord_parts = coord_key.split(',')
            x = int(float(coord_parts[0]))
            y = int(float(coord_parts[1]))
            
            # Calculate time remaining
            base_time = self.base_respawn_times.get(harvest_data['type'], 7)
            days_passed = self._calculate_days_passed(harvest_data)
            
            # Get current weather and seasonal modifiers
            weather_mod = self.get_weather_modifier(harvest_data['type'])
            seasonal_mod = self.get_seasonal_modifier()
            total_mod = weather_mod * seasonal_mod
            
            # Estimate days remaining
            adjusted_time = base_time * total_mod
            days_remaining = adjusted_time - days_passed
            
            resources_info.append({
                'x': x,
                'y': y,
                'type': harvest_data['type'],
                'progress': progress,
                'days_remaining': max(0, days_remaining),
                'visual_state': self.get_visual_state(progress)
            })
        
        return resources_info
    
    def save_data(self):
        """Save harvest data to file"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.harvested_resources, f)
        except Exception as e:
            print(f"Error saving respawn data: {e}")
    
    def load_data(self):
        """Load harvest data from file"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    self.harvested_resources = json.load(f)
            except Exception as e:
                print(f"Error loading respawn data: {e}")
                self.harvested_resources = {}
