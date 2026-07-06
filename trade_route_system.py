"""
Trade Route System
Manages trade routes between towns, traveling merchants/caravans, resource contracts, and inter-town commerce
"""
import random
import math
from logger_config import logger


class TradeRoute:
    """Represents a trade route between two towns"""
    def __init__(self, town_a, town_b, distance):
        self.town_a = town_a
        self.town_b = town_b
        self.distance = distance
        self.active = True
        self.danger_level = random.randint(1, 5)  # 1=safe, 5=dangerous
        self.caravans = []  # Caravans currently on this route
        self.trade_volume = 0  # Total goods traded on this route
        self.established_day = None
        
    def get_travel_time_days(self):
        """Calculate travel time in game days based on distance"""
        # ~100 pixels per hour, 24 hours per day = 2400 pixels per day
        return max(1, int(self.distance / 2400))


class Caravan:
    """Traveling merchant caravan that moves between towns"""
    def __init__(self, caravan_id, origin_town, destination_town, route):
        self.caravan_id = caravan_id
        self.origin_town = origin_town
        self.destination_town = destination_town
        self.route = route
        self.current_x = 0
        self.current_y = 0
        self.inventory = {}  # {item: quantity}
        self.gold = random.randint(500, 2000)
        self.travel_progress = 0.0  # 0.0 to 1.0
        self.status = "traveling"  # traveling, arrived, trading, returning
        self.departure_day = None
        self.arrival_day = None
        self.speed = 100  # pixels per second
        self.goods_value = 0
        
    def update_position(self, origin_coords, dest_coords):
        """Update caravan position based on travel progress"""
        origin_x, origin_y = origin_coords
        dest_x, dest_y = dest_coords
        
        self.current_x = origin_x + (dest_x - origin_x) * self.travel_progress
        self.current_y = origin_y + (dest_y - origin_y) * self.travel_progress
        
    def load_goods(self, item, quantity):
        """Load goods onto caravan"""
        if item not in self.inventory:
            self.inventory[item] = 0
        self.inventory[item] += quantity
        
    def unload_goods(self, item, quantity):
        """Unload goods from caravan"""
        if item in self.inventory:
            removed = min(quantity, self.inventory[item])
            self.inventory[item] -= removed
            if self.inventory[item] <= 0:
                del self.inventory[item]
            return removed
        return 0


class ResourceContract:
    """Contract for resource delivery between towns or NPCs"""
    def __init__(self, contract_id, supplier_town, buyer_town, resource_type, quantity, price_per_unit, deadline_days):
        self.contract_id = contract_id
        self.supplier_town = supplier_town
        self.buyer_town = buyer_town
        self.resource_type = resource_type
        self.quantity = quantity
        self.price_per_unit = price_per_unit
        self.total_value = quantity * price_per_unit
        self.deadline_days = deadline_days
        self.delivered_quantity = 0
        self.status = "active"  # active, completed, failed, cancelled
        self.created_day = None
        self.completed_day = None
        
    def is_expired(self, current_day):
        """Check if contract has expired"""
        if self.created_day is None:
            return False
        return (current_day - self.created_day) > self.deadline_days
    
    def deliver(self, quantity):
        """Deliver goods to fulfill contract"""
        delivered = min(quantity, self.quantity - self.delivered_quantity)
        self.delivered_quantity += delivered
        
        if self.delivered_quantity >= self.quantity:
            self.status = "completed"
        
        return delivered
    
    def get_completion_percentage(self):
        """Get completion percentage"""
        if self.quantity == 0:
            return 100
        return int((self.delivered_quantity / self.quantity) * 100)


class TradeRouteSystem:
    """Manages all trade routes, caravans, and contracts"""
    
    def __init__(self, game_time, town_manager, market_manager=None):
        self.game_time = game_time
        self.town_manager = town_manager
        self.market_manager = market_manager
        self.routes = []
        self.caravans = []
        self.contracts = []
        self.next_caravan_id = 1
        self.next_contract_id = 1
        
        # Configuration
        self.max_caravans_per_route = 2
        self.caravan_spawn_chance = 0.3  # 30% chance per day
        self.contract_offer_chance = 0.2  # 20% chance per day
        
        logger.info("[TRADE] Trade Route System initialized")
    
    def establish_trade_routes(self):
        """Establish trade routes between all towns"""
        towns = self.town_manager.towns
        
        for i, town_a in enumerate(towns):
            for town_b in towns[i+1:]:
                # Calculate distance
                dx = town_b.center_x - town_a.center_x
                dy = town_b.center_y - town_a.center_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Create route
                route = TradeRoute(town_a.name, town_b.name, distance)
                route.established_day = self.game_time.day_count
                self.routes.append(route)
                
                logger.info(f"[TRADE] Established route: {town_a.name} <-> {town_b.name} ({int(distance)} units, {route.get_travel_time_days()} days)")
        
        logger.info(f"[TRADE] Established {len(self.routes)} trade routes between {len(towns)} towns")
        return len(self.routes)
    
    def spawn_caravan(self, route):
        """Spawn a caravan on a route"""
        caravan_id = f"CARAVAN-{self.next_caravan_id}"
        self.next_caravan_id += 1
        
        # Randomly pick direction
        if random.random() < 0.5:
            origin = route.town_a
            destination = route.town_b
        else:
            origin = route.town_b
            destination = route.town_a
        
        caravan = Caravan(caravan_id, origin, destination, route)
        caravan.departure_day = self.game_time.day_count
        caravan.arrival_day = self.game_time.day_count + route.get_travel_time_days()
        
        # Load random trade goods
        trade_goods = ["iron_ore", "wood", "fish", "bread", "cloth", "herbs", "ore"]
        num_goods = random.randint(2, 4)
        for _ in range(num_goods):
            item = random.choice(trade_goods)
            quantity = random.randint(5, 20)
            caravan.load_goods(item, quantity)
        
        self.caravans.append(caravan)
        route.caravans.append(caravan)
        
        logger.info(f"[TRADE] Spawned {caravan_id}: {origin} -> {destination}")
        return caravan
    
    def create_contract(self, supplier_town, buyer_town, resource_type, quantity, price_per_unit, deadline_days):
        """Create a resource delivery contract"""
        contract_id = f"CONTRACT-{self.next_contract_id}"
        self.next_contract_id += 1
        
        contract = ResourceContract(
            contract_id, supplier_town, buyer_town, 
            resource_type, quantity, price_per_unit, deadline_days
        )
        contract.created_day = self.game_time.day_count
        
        self.contracts.append(contract)
        logger.info(f"[TRADE] Contract created: {contract_id} - {quantity}x {resource_type} ({supplier_town} -> {buyer_town})")
        return contract
    
    def update_caravans(self, dt):
        """Update all caravans (movement, trading)"""
        for caravan in self.caravans[:]:
            if caravan.status == "traveling":
                # Update travel progress
                days_elapsed = self.game_time.day_count - caravan.departure_day
                travel_time = caravan.route.get_travel_time_days()
                caravan.travel_progress = min(1.0, days_elapsed / travel_time)
                
                # Update position
                origin_town = self._get_town(caravan.origin_town)
                dest_town = self._get_town(caravan.destination_town)
                
                if origin_town and dest_town:
                    caravan.update_position(
                        (origin_town.center_x, origin_town.center_y),
                        (dest_town.center_x, dest_town.center_y)
                    )
                
                # Check if arrived
                if caravan.travel_progress >= 1.0:
                    caravan.status = "arrived"
                    logger.info(f"[TRADE] {caravan.caravan_id} arrived at {caravan.destination_town}")
                    
            elif caravan.status == "arrived":
                # Trade goods at destination
                self._trade_caravan_goods(caravan)
                caravan.status = "returning"
                
            elif caravan.status == "returning":
                # Return to origin (simplified - instant for now)
                caravan.route.caravans.remove(caravan)
                self.caravans.remove(caravan)
                logger.info(f"[TRADE] {caravan.caravan_id} completed trade route")
    
    def _trade_caravan_goods(self, caravan):
        """Caravan trades goods at destination"""
        if not self.market_manager:
            return
        
        # Sell goods to destination town
        for item, quantity in list(caravan.inventory.items()):
            # Get market price
            price = self._get_town_price(caravan.destination_town, item)
            if price:
                revenue = quantity * price
                caravan.gold += revenue
                caravan.goods_value += revenue
                caravan.unload_goods(item, quantity)
                logger.info(f"[TRADE] {caravan.caravan_id} sold {quantity}x {item} for {revenue}g")
    
    def update_contracts(self):
        """Update all contracts (check expiry, completion)"""
        for contract in self.contracts[:]:
            if contract.status == "active":
                # Check if expired
                if contract.is_expired(self.game_time.day_count):
                    contract.status = "failed"
                    logger.warning(f"[TRADE] Contract {contract.contract_id} expired!")
    
    def update_daily(self):
        """Daily update for spawning caravans and offering contracts"""
        # Spawn caravans on routes
        for route in self.routes:
            if not route.active:
                continue
                
            # Count caravans on this route
            active_caravans = len([c for c in route.caravans if c.status == "traveling"])
            
            # Spawn new caravan if below max
            if active_caravans < self.max_caravans_per_route:
                if random.random() < self.caravan_spawn_chance:
                    self.spawn_caravan(route)
        
        # Generate new contracts
        if random.random() < self.contract_offer_chance:
            self._generate_random_contract()
        
        # Update existing contracts
        self.update_contracts()
    
    def _generate_random_contract(self):
        """Generate a random resource contract"""
        towns = self.town_manager.towns
        if len(towns) < 2:
            return
        
        supplier_town = random.choice(towns)
        buyer_town = random.choice([t for t in towns if t != supplier_town])
        
        resources = ["iron_ore", "wood", "fish", "cloth", "ore"]
        resource = random.choice(resources)
        quantity = random.randint(10, 50)
        price = random.randint(5, 20)
        deadline = random.randint(7, 30)  # 1-4 weeks
        
        self.create_contract(
            supplier_town.name, buyer_town.name,
            resource, quantity, price, deadline
        )
    
    def _get_town(self, town_name):
        """Get town by name"""
        for town in self.town_manager.towns:
            if town.name == town_name:
                return town
        return None
    
    def _get_town_price(self, town_name, item):
        """Get item price in a specific town"""
        if not self.market_manager:
            return 10  # Default price
        
        # Try to get market price (if market system exists)
        return 10
    
    def get_active_contracts(self):
        """Get all active contracts"""
        return [c for c in self.contracts if c.status == "active"]
    
    def get_available_contracts_for_player(self, player_town):
        """Get contracts available to player in their current town"""
        return [c for c in self.contracts if c.status == "active" and c.supplier_town == player_town]
    
    def fulfill_contract(self, contract_id, player, quantity):
        """Player fulfills a contract by delivering goods"""
        contract = next((c for c in self.contracts if c.contract_id == contract_id), None)
        if not contract or contract.status != "active":
            return False, "Contract not found or inactive"
        
        # Check if player has the goods
        if contract.resource_type not in player.inventory:
            return False, f"You don't have {contract.resource_type}"
        
        available = player.inventory[contract.resource_type]
        if available < quantity:
            return False, f"Not enough {contract.resource_type} (need {quantity}, have {available})"
        
        # Deliver goods
        delivered = contract.deliver(quantity)
        player.inventory[contract.resource_type] -= delivered
        
        # Pay player
        payment = delivered * contract.price_per_unit
        player.dubloons += payment
        
        logger.info(f"[TRADE] Player fulfilled {delivered} units of contract {contract_id} for {payment}g")
        
        if contract.status == "completed":
            return True, f"Contract completed! Earned {payment}g total: {contract.total_value}g"
        else:
            return True, f"Delivered {delivered} units. Earned {payment}g. ({contract.get_completion_percentage()}% complete)"
    
    def get_trade_stats(self):
        """Get trade system statistics"""
        return {
            'routes': len(self.routes),
            'active_caravans': len([c for c in self.caravans if c.status == "traveling"]),
            'total_caravans': len(self.caravans),
            'active_contracts': len([c for c in self.contracts if c.status == "active"]),
            'completed_contracts': len([c for c in self.contracts if c.status == "completed"]),
            'failed_contracts': len([c for c in self.contracts if c.status == "failed"])
        }
