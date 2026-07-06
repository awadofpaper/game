"""
Weather-Responsive NPC and Town Behavior System
Adds realistic weather reactions for NPCs and dynamic town activities
"""

import time
import random
from typing import Dict, List, Optional, Tuple, Any

class WeatherNPCBehavior:
    """Manages weather-responsive behavior for NPCs"""
    
    def __init__(self):
        self.weather_dialogues = {
            "rain": {
                "greetings": [
                    "Terrible weather we're having, isn't it?",
                    "I hope you have shelter planned for tonight.",
                    "The rain has been good for the crops, at least.",
                    "Best to stay indoors until this passes."
                ],
                "farewells": [
                    "Stay dry out there!",
                    "Mind the puddles on your way.",
                    "Safe travels in this weather."
                ],
                "special_offers": [
                    "I have some waterproof cloaks, might interest you in this weather.",
                    "Hot soup to warm you up? Only 5 dubloons.",
                    "These boots will keep your feet dry - special rain price!"
                ]
            },
            "storm": {
                "greetings": [
                    "You shouldn't be out in this storm!",
                    "Dangerous weather - lightning's been striking all around.",
                    "The storm came in fast. Are you alright?",
                    "Best to take shelter until this passes."
                ],
                "farewells": [
                    "Please, find shelter soon!",
                    "Don't get struck by lightning!",
                    "Be extremely careful out there!"
                ],
                "special_offers": [
                    "I can't sell anything in good conscience - get to safety!",
                    "Take this lantern, no charge. You'll need light in this storm.",
                    "Here, take some food. Storm might last a while."
                ]
            },
            "snow": {
                "greetings": [
                    "Bundle up warm! This cold will freeze you solid.",
                    "Beautiful snow, but deadly cold.",
                    "The winter is harsh this year.",
                    "I hope you're dressed for the weather."
                ],
                "farewells": [
                    "Keep warm out there!",
                    "Don't let the cold get to you.",
                    "Mind the ice patches!"
                ],
                "special_offers": [
                    "Thick winter cloaks - essential in this cold!",
                    "Hot cider to warm your bones? 3 dubloons.",
                    "These fur-lined boots will save your toes!"
                ]
            },
            "fog": {
                "greetings": [
                    "Can barely see you in this fog!",
                    "Careful out there - visibility is terrible.",
                    "This fog came in thick. Hard to navigate.",
                    "You look lost - this fog will do that."
                ],
                "farewells": [
                    "Watch your step in this fog!",
                    "Stay on the paths - easy to get lost!",
                    "The fog should lift by morning."
                ],
                "special_offers": [
                    "I have a compass - might help in this fog.",
                    "Lanterns are selling well today, for obvious reasons.",
                    "Rope to mark your path? Smart thinking in fog like this."
                ]
            },
            "clear": {
                "greetings": [
                    "Beautiful day, isn't it?",
                    "Perfect weather for traveling!",
                    "What lovely clear skies we have.",
                    "A fine day to be outdoors!"
                ],
                "farewells": [
                    "Enjoy this beautiful weather!",
                    "Perfect day for an adventure!",
                    "Make the most of these clear skies!"
                ],
                "special_offers": [
                    "With weather like this, you might want travel supplies.",
                    "Perfect day for a long journey - need provisions?",
                    "Clear roads ahead - might interest you in a map?"
                ]
            }
        }
        
        self.weather_inventory_changes = {
            "rain": {
                "add_items": ["waterproof_cloak", "umbrella", "hot_soup", "rain_boots"],
                "increase_prices": ["shelter_supplies", "dry_goods"],
                "decrease_prices": ["farming_tools", "seeds"]
            },
            "storm": {
                "add_items": ["lightning_rod", "storm_lantern", "emergency_rations"],
                "increase_prices": ["shelter_supplies", "safety_gear"],
                "emergency_mode": True
            },
            "snow": {
                "add_items": ["winter_cloak", "fur_boots", "hot_cider", "fire_starter"],
                "increase_prices": ["warm_clothing", "heating_supplies"],
                "decrease_prices": ["cold_weather_gear"]
            },
            "fog": {
                "add_items": ["compass", "fog_lantern", "navigation_rope"],
                "increase_prices": ["navigation_tools", "light_sources"],
                "decrease_prices": ["outdoor_activities"]
            }
        }
        
        # NPC shelter-seeking behavior
        self.shelter_locations = {}
        self.npc_weather_states = {}
        
    def get_weather_dialogue(self, npc_name: str, weather: str, dialogue_type: str = "greetings") -> str:
        """Get weather-appropriate dialogue for an NPC"""
        weather = weather.lower()
        
        # Handle storm variants
        if weather in ["thunder", "thunderstorm"]:
            weather = "storm"
        elif weather == "light_rain":
            weather = "rain"
            
        if weather in self.weather_dialogues and dialogue_type in self.weather_dialogues[weather]:
            return random.choice(self.weather_dialogues[weather][dialogue_type])
        
        # Fallback to clear weather dialogue
        return random.choice(self.weather_dialogues["clear"][dialogue_type])
    
    def should_npc_seek_shelter(self, weather: str, intensity: float = 1.0) -> bool:
        """Determine if NPCs should seek shelter based on weather"""
        severe_weather = ["storm", "thunder", "thunderstorm", "snow"]
        
        if weather in severe_weather:
            return True
        elif weather == "rain" and intensity > 0.7:
            return True
        
        return False
    
    def get_weather_inventory_changes(self, weather: str) -> Dict[str, Any]:
        """Get inventory changes for weather conditions"""
        weather = weather.lower()
        
        if weather in ["thunder", "thunderstorm"]:
            weather = "storm"
        elif weather == "light_rain":
            weather = "rain"
            
        return self.weather_inventory_changes.get(weather, {})
    
    def update_npc_weather_state(self, npc_name: str, weather: str, intensity: float):
        """Update an NPC's behavior based on current weather"""
        current_time = time.time()
        
        if npc_name not in self.npc_weather_states:
            self.npc_weather_states[npc_name] = {
                "current_weather": weather,
                "last_weather_change": current_time,
                "seeking_shelter": False,
                "weather_dialogue_used": False,
                "inventory_modified": False
            }
        
        npc_state = self.npc_weather_states[npc_name]
        
        # Check if weather changed
        if npc_state["current_weather"] != weather:
            npc_state["current_weather"] = weather
            npc_state["last_weather_change"] = current_time
            npc_state["weather_dialogue_used"] = False
            npc_state["inventory_modified"] = False
        
        # Update shelter-seeking behavior
        npc_state["seeking_shelter"] = self.should_npc_seek_shelter(weather, intensity)
        
        return npc_state

class WeatherTownManager:
    """Manages weather effects on town activities and services"""
    
    def __init__(self):
        self.town_weather_states = {}
        self.weather_events = []
        self.market_schedules = {}
        
        # Define weather-based town activities
        self.weather_activities = {
            "clear": {
                "market_active": True,
                "outdoor_vendors": True,
                "festivals_possible": True,
                "travel_encouraged": True
            },
            "rain": {
                "market_active": True,
                "outdoor_vendors": False,
                "festivals_possible": False,
                "indoor_activities": True,
                "umbrella_vendors": True
            },
            "storm": {
                "market_active": False,
                "outdoor_vendors": False,
                "festivals_possible": False,
                "emergency_services": True,
                "shelter_provision": True
            },
            "snow": {
                "market_active": True,
                "outdoor_vendors": False,
                "winter_activities": True,
                "heating_services": True,
                "snow_clearing": True
            },
            "fog": {
                "market_active": True,
                "outdoor_vendors": True,
                "navigation_services": True,
                "reduced_visibility": True
            }
        }
    
    def update_town_weather_activities(self, town_name: str, weather: str, intensity: float):
        """Update town activities based on weather"""
        if town_name not in self.town_weather_states:
            self.town_weather_states[town_name] = {}
        
        weather = weather.lower()
        if weather in ["thunder", "thunderstorm"]:
            weather = "storm"
        elif weather == "light_rain":
            weather = "rain"
        
        activities = self.weather_activities.get(weather, self.weather_activities["clear"])
        self.town_weather_states[town_name].update(activities)
        
        # Generate weather events
        self._generate_weather_events(town_name, weather, intensity)
    
    def _generate_weather_events(self, town_name: str, weather: str, intensity: float):
        """Generate random weather-related events for towns"""
        current_time = time.time()
        
        # Clear old events (older than 10 minutes)
        self.weather_events = [
            event for event in self.weather_events 
            if current_time - event["timestamp"] < 600
        ]
        
        # Chance to generate new weather events
        if random.random() < 0.01:  # 1% chance per update
            event = None
            
            if weather == "storm" and intensity > 0.8:
                events = [
                    f"Lightning struck near {town_name}! Magical items may be charged.",
                    f"Storm winds damaged some rooftops in {town_name}.",
                    f"The storm has flooded some streets in {town_name}."
                ]
                event = random.choice(events)
                
            elif weather == "snow" and intensity > 0.6:
                events = [
                    f"Heavy snow is blocking some roads to {town_name}.",
                    f"Ice has formed on the wells in {town_name}.",
                    f"A warm fire burns in {town_name}'s tavern."
                ]
                event = random.choice(events)
                
            elif weather == "rain":
                events = [
                    f"The rain has filled water barrels in {town_name}.",
                    f"Muddy streets make travel difficult in {town_name}.",
                    f"Gardens are flourishing from the rain in {town_name}."
                ]
                event = random.choice(events)
            
            if event:
                self.weather_events.append({
                    "message": event,
                    "town": town_name,
                    "weather": weather,
                    "timestamp": current_time
                })
    
    def get_weather_events(self, max_age: float = 300) -> List[Dict]:
        """Get recent weather events for display"""
        current_time = time.time()
        return [
            event for event in self.weather_events 
            if current_time - event["timestamp"] < max_age
        ]
    
    def is_service_available(self, town_name: str, service_type: str) -> bool:
        """Check if a town service is available based on weather"""
        if town_name not in self.town_weather_states:
            return True
        
        town_state = self.town_weather_states[town_name]
        
        service_requirements = {
            "market": town_state.get("market_active", True),
            "outdoor_vendors": town_state.get("outdoor_vendors", True),
            "festivals": town_state.get("festivals_possible", True),
            "travel_services": town_state.get("travel_encouraged", True)
        }
        
        return service_requirements.get(service_type, True)

# Global weather behavior manager
weather_npc_behavior = WeatherNPCBehavior()
weather_town_manager = WeatherTownManager()

def initialize_weather_npc_system():
    """Initialize the weather NPC behavior system"""
    global weather_npc_behavior, weather_town_manager
    weather_npc_behavior = WeatherNPCBehavior()
    weather_town_manager = WeatherTownManager()
    
def update_npc_weather_behavior(npc, weather: str, intensity: float = 1.0):
    """Update a single NPC's weather behavior"""
    if not hasattr(npc, 'name'):
        return
    
    # Update NPC state
    npc_state = weather_npc_behavior.update_npc_weather_state(npc.name, weather, intensity)
    
    # Modify dialogue based on weather
    if not npc_state["weather_dialogue_used"]:
        weather_greeting = weather_npc_behavior.get_weather_dialogue(npc.name, weather, "greetings")
        
        # If NPC has dialogue system, add weather-appropriate responses
        if hasattr(npc, 'dialogue_trees') and 'default' in npc.dialogue_trees:
            # Add weather dialogue to the start node
            start_node = npc.dialogue_trees['default']['start']
            if hasattr(start_node, 'text'):
                start_node.text = f"{weather_greeting}\n\n{start_node.text}"
        
        npc_state["weather_dialogue_used"] = True
    
    # Update inventory if NPC is a merchant
    if hasattr(npc, 'inventory') and not npc_state["inventory_modified"]:
        weather_changes = weather_npc_behavior.get_weather_inventory_changes(weather)
        
        # Add weather-appropriate items
        if "add_items" in weather_changes:
            for item in weather_changes["add_items"]:
                # Simple inventory addition (would need proper item integration)
                if hasattr(npc.inventory, 'add_item'):
                    npc.inventory.add_item(item, random.randint(1, 3))
        
        npc_state["inventory_modified"] = True

def update_town_weather_behavior(town_name: str, weather: str, intensity: float = 1.0):
    """Update town behavior based on weather"""
    weather_town_manager.update_town_weather_activities(town_name, weather, intensity)

def get_weather_town_events() -> List[str]:
    """Get recent weather events for display"""
    events = weather_town_manager.get_weather_events()
    return [event["message"] for event in events]

def is_town_service_available(town_name: str, service: str) -> bool:
    """Check if a town service is available"""
    return weather_town_manager.is_service_available(town_name, service)