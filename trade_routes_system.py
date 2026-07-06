"""
Trade Routes and Caravans System
Traveling merchants, escort quests, dynamic trade between towns
"""

import logging
import random
from typing import Dict, List, Optional, Tuple
import math

logger = logging.getLogger(__name__)


class Caravan:
    """Represents a traveling caravan between towns"""
    
    def __init__(self, caravan_id: str, origin_town: str, destination_town: str,
                 merchant_name: str, cargo_value: int, travel_speed: float = 40.0):
        self.caravan_id = caravan_id
        self.origin_town = origin_town
        self.destination_town = destination_town
        self.merchant_name = merchant_name
        self.cargo_value = cargo_value
        self.travel_speed = travel_speed
        
        # Position
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        
        # State
        self.progress = 0.0  # 0.0 to 1.0
        self.is_active = True
        self.is_under_attack = False
        self.has_escort = False
        self.escort_payment = 0
        
        # Inventory
        self.cargo = []  # List of goods being transported
        
        # Guards
        self.guard_count = random.randint(2, 5)
        self.guard_strength = random.randint(10, 30)
        
    def update(self, dt: float):
        """Update caravan position"""
        if not self.is_active:
            return
        
        # Move toward destination
        self.progress += (self.travel_speed * dt) / 1000.0
        
        if self.progress >= 1.0:
            self.progress = 1.0
            self.arrive_at_destination()
    
    def arrive_at_destination(self):
        """Called when caravan reaches destination"""
        self.is_active = False
        logger.info(f"[CARAVAN] {self.caravan_id} arrived at {self.destination_town}")
    
    def get_position(self, origin_pos: Tuple[int, int], dest_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate current position between origin and destination"""
        ox, oy = origin_pos
        dx, dy = dest_pos
        
        current_x = ox + (dx - ox) * self.progress
        current_y = oy + (dy - oy) * self.progress
        
        return int(current_x), int(current_y)
    
    def initiate_attack(self, bandit_strength: int) -> bool:
        """
        Initiate bandit attack on caravan
        Returns: True if caravan is destroyed
        """
        self.is_under_attack = True
        
        total_defense = self.guard_strength * self.guard_count
        if self.has_escort:
            total_defense += 50  # Player escort bonus
        
        if bandit_strength > total_defense:
            # Caravan destroyed
            self.is_active = False
            logger.warning(f"[CARAVAN] {self.caravan_id} was destroyed by bandits!")
            return True
        else:
            # Caravan survives
            self.is_under_attack = False
            logger.info(f"[CARAVAN] {self.caravan_id} defended against bandits")
            return False
    
    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'caravan_id': self.caravan_id,
            'origin_town': self.origin_town,
            'destination_town': self.destination_town,
            'merchant_name': self.merchant_name,
            'cargo_value': self.cargo_value,
            'progress': self.progress,
            'is_active': self.is_active,
            'has_escort': self.has_escort,
            'escort_payment': self.escort_payment,
            'guard_count': self.guard_count,
            'guard_strength': self.guard_strength
        }


class TradeRoute:
    """Represents an established trade route between two towns"""
    
    def __init__(self, route_id: str, town_a: str, town_b: str):
        self.route_id = route_id
        self.town_a = town_a
        self.town_b = town_b
        self.traffic_level = random.randint(1, 5)  # 1-5, affects caravan frequency
        self.danger_level = random.randint(1, 10)  # 1-10, bandit activity
        self.is_active = True
        
        # Trade goods flowing on this route
        self.primary_exports_a = []  # What town A exports
        self.primary_exports_b = []  # What town B exports
        
        # Statistics
        self.successful_trips = 0
        self.failed_trips = 0
        self.total_value_traded = 0
    
    def record_trip(self, success: bool, value: int):
        """Record caravan trip statistics"""
        if success:
            self.successful_trips += 1
            self.total_value_traded += value
        else:
            self.failed_trips += 1
        
        # Adjust danger level based on failures
        failure_rate = self.failed_trips / max(1, self.successful_trips + self.failed_trips)
        if failure_rate > 0.3:
            self.danger_level = min(10, self.danger_level + 1)
        elif failure_rate < 0.1:
            self.danger_level = max(1, self.danger_level - 1)


class TravelingMerchant:
    """A merchant who travels between towns selling rare goods"""
    
    def __init__(self, merchant_id: str, name: str, specialty: str):
        self.merchant_id = merchant_id
        self.name = name
        self.specialty = specialty  # "exotic", "weapons", "potions", etc.
        self.current_town = None
        self.next_town = None
        self.arrival_day = 0
        self.stay_duration = random.randint(2, 4)  # Days to stay in town
        self.inventory = []
        self.prices_multiplier = random.uniform(1.2, 1.8)  # More expensive than normal shops
        
    def generate_inventory(self):
        """Generate special inventory based on specialty"""
        # This would generate special items based on specialty
        self.inventory = []
        # TODO: Generate rare items based on specialty
    
    def schedule_next_visit(self, current_day: int, town: str):
        """Schedule visit to a town"""
        self.next_town = town
        self.arrival_day = current_day + random.randint(3, 7)
    
    def arrive(self, current_day: int):
        """Merchant arrives in town"""
        self.current_town = self.next_town
        self.next_town = None
        self.generate_inventory()
        logger.info(f"[TRAVELING MERCHANT] {self.name} arrived in {self.current_town}")


class CaravanManager:
    """Manages all trade routes and caravans"""
    
    def __init__(self):
        self.trade_routes: Dict[str, TradeRoute] = {}
        self.active_caravans: Dict[str, Caravan] = {}
        self.traveling_merchants: Dict[str, TravelingMerchant] = {}
        self.next_caravan_id = 1
        
        # Escort quest tracking
        self.available_escorts: List[str] = []  # Caravan IDs available for escort
        self.player_escorting: Optional[str] = None  # Current escort caravan ID
        
        # Town positions cache
        self.town_positions: Dict[str, Tuple[int, int]] = {}
    
    def register_town_position(self, town_name: str, x: int, y: int):
        """Register town center position for caravan routing"""
        self.town_positions[town_name] = (x, y)
    
    def create_trade_route(self, town_a: str, town_b: str) -> TradeRoute:
        """Create a trade route between two towns"""
        route_id = f"{town_a}_{town_b}"
        route = TradeRoute(route_id, town_a, town_b)
        self.trade_routes[route_id] = route
        logger.info(f"[TRADE ROUTE] Created route {route_id}")
        return route
    
    def spawn_caravan(self, origin: str, destination: str, 
                     escort_available: bool = True) -> Optional[Caravan]:
        """Spawn a new caravan"""
        if origin not in self.town_positions or destination not in self.town_positions:
            logger.warning(f"[CARAVAN] Cannot spawn caravan, town positions not registered")
            return None
        
        caravan_id = f"CARAVAN_{self.next_caravan_id}"
        self.next_caravan_id += 1
        
        merchant_names = ["Merchant Aldric", "Trader Mira", "Vendor Thom", 
                         "Dealer Elara", "Peddler Bron"]
        merchant_name = random.choice(merchant_names)
        
        cargo_value = random.randint(500, 5000)
        
        caravan = Caravan(caravan_id, origin, destination, merchant_name, cargo_value)
        
        # Set position
        origin_pos = self.town_positions[origin]
        dest_pos = self.town_positions[destination]
        caravan.x, caravan.y = origin_pos
        caravan.target_x, caravan.target_y = dest_pos
        
        self.active_caravans[caravan_id] = caravan
        
        # Make available for escort if requested
        if escort_available:
            escort_payment = int(cargo_value * 0.15)  # 15% of cargo value
            caravan.escort_payment = escort_payment
            self.available_escorts.append(caravan_id)
        
        logger.info(f"[CARAVAN] Spawned {caravan_id} from {origin} to {destination} (value: {cargo_value}g)")
        return caravan
    
    def accept_escort_quest(self, caravan_id: str, player) -> Tuple[bool, str]:
        """Player accepts escort quest"""
        if caravan_id not in self.active_caravans:
            return False, "Caravan not found"
        
        if self.player_escorting:
            return False, "Already escorting a caravan"
        
        caravan = self.active_caravans[caravan_id]
        caravan.has_escort = True
        self.player_escorting = caravan_id
        
        if caravan_id in self.available_escorts:
            self.available_escorts.remove(caravan_id)
        
        return True, f"Escorting {caravan.merchant_name}'s caravan to {caravan.destination_town} for {caravan.escort_payment}g"
    
    def complete_escort(self, player) -> Tuple[bool, int]:
        """Complete escort quest when caravan arrives"""
        if not self.player_escorting:
            return False, 0
        
        caravan_id = self.player_escorting
        if caravan_id not in self.active_caravans:
            self.player_escorting = None
            return False, 0
        
        caravan = self.active_caravans[caravan_id]
        
        if not caravan.is_active:
            # Caravan arrived or was destroyed
            payment = caravan.escort_payment if caravan.progress >= 1.0 else 0
            self.player_escorting = None
            return True, payment
        
        return False, 0
    
    def update(self, dt: float, current_day: int):
        """Update all caravans"""
        # Update active caravans
        completed = []
        for caravan_id, caravan in self.active_caravans.items():
            caravan.update(dt)
            
            if not caravan.is_active:
                completed.append(caravan_id)
                
                # Update route statistics
                route_id = f"{caravan.origin_town}_{caravan.destination_town}"
                if route_id in self.trade_routes:
                    success = caravan.progress >= 1.0
                    self.trade_routes[route_id].record_trip(success, caravan.cargo_value)
        
        # Remove completed caravans
        for caravan_id in completed:
            del self.active_caravans[caravan_id]
            if caravan_id in self.available_escorts:
                self.available_escorts.remove(caravan_id)
        
        # Random chance to spawn new caravans
        if random.random() < 0.01:  # 1% chance per update
            self.spawn_random_caravan()
        
        # Update traveling merchants
        for merchant in self.traveling_merchants.values():
            if merchant.next_town and current_day >= merchant.arrival_day:
                merchant.arrive(current_day)
    
    def spawn_random_caravan(self):
        """Spawn a random caravan between towns"""
        if len(self.town_positions) < 2:
            return
        
        towns = list(self.town_positions.keys())
        origin = random.choice(towns)
        destination = random.choice([t for t in towns if t != origin])
        
        self.spawn_caravan(origin, destination, escort_available=True)
    
    def get_available_escort_quests(self) -> List[Tuple[str, Caravan]]:
        """Get list of available escort quests"""
        quests = []
        for caravan_id in self.available_escorts:
            if caravan_id in self.active_caravans:
                caravan = self.active_caravans[caravan_id]
                if caravan.is_active and not caravan.has_escort:
                    quests.append((caravan_id, caravan))
        return quests
    
    def get_caravan_position(self, caravan_id: str) -> Optional[Tuple[int, int]]:
        """Get current position of a caravan"""
        if caravan_id not in self.active_caravans:
            return None
        
        caravan = self.active_caravans[caravan_id]
        origin_pos = self.town_positions.get(caravan.origin_town)
        dest_pos = self.town_positions.get(caravan.destination_town)
        
        if not origin_pos or not dest_pos:
            return None
        
        return caravan.get_position(origin_pos, dest_pos)
    
    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'active_caravans': {cid: caravan.to_dict() for cid, caravan in self.active_caravans.items()},
            'next_caravan_id': self.next_caravan_id,
            'player_escorting': self.player_escorting,
            'available_escorts': self.available_escorts
        }
    
    def from_dict(self, data: dict):
        """Load from save data"""
        # Note: Would need to reconstruct Caravan objects from dict
        self.next_caravan_id = data.get('next_caravan_id', 1)
        self.player_escorting = data.get('player_escorting')
        self.available_escorts = data.get('available_escorts', [])
