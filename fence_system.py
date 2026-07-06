"""
Fence NPC System
Handles black market fences who buy stolen goods
"""
import random

class FenceNPC:
    """A fence who buys stolen goods"""
    
    def __init__(self, name, town_name, tavern_x, tavern_y):
        self.name = name
        self.town_name = town_name
        # Fence hangs out near tavern
        self.x = tavern_x + random.randint(-50, 50)
        self.y = tavern_y + random.randint(-50, 50)
        self.active_hours = (22, 4)  # 10pm to 4am
        self.discovered = False
        self.reputation = 0  # Player's fence reputation
        
    def is_active(self, game_time):
        """Check if fence is currently available (night time)"""
        hour, _ = game_time.get_time_hm()
        start, end = self.active_hours
        
        # Handle overnight hours
        if start > end:
            return hour >= start or hour < end
        else:
            return start <= hour < end
    
    def get_buy_rate(self):
        """
        Calculate how much of item value fence pays
        Better reputation = better rates
        """
        base_rate = 0.4
        rep_bonus = min(0.2, self.reputation / 500 * 0.2)
        return base_rate + rep_bonus
    
    def buy_stolen_item(self, stolen_item, player):
        """
        Buy a stolen item from player
        Returns (gold_paid, success)
        """
        if not hasattr(stolen_item, 'is_stolen') or not stolen_item.is_stolen:
            return 0, False
        
        # Estimate value
        item_value = self._estimate_value(stolen_item.name)
        buy_rate = self.get_buy_rate()
        price = int(item_value * buy_rate)
        
        # Remove from player's stolen items list
        if stolen_item in player.stolen_items:
            player.stolen_items.remove(stolen_item)
        
        # Remove from inventory
        current = player.inventory.get(stolen_item.name, 0)
        if current > 0:
            player.inventory[stolen_item.name] = current - 1
        
        # Increase fence reputation slightly
        self.reputation += 1
        
        return price, True
    
    def _estimate_value(self, item_name):
        """Estimate item value"""
        values = {
            'health_potion': 20,
            'mana_potion': 25,
            'stamina_potion': 15,
            'iron_ore': 10,
            'steel_ingot': 30,
            'repair_kit': 40,
            'ale': 5,
            'wine': 12,
            'bread': 3,
            'cheese': 8,
            'cooked_meat': 15,
            'town_records': 100,
            'bank_records': 80,
            'tax_ledger': 120,
            'election_documents': 150,
            'lockpick': 25,
            'rope': 10,
            'torch': 5,
            'iron_sword': 100,
            'iron_armor': 120,
            'steel_sword': 200,
            'diamond': 500,
            'ruby': 300,
            'gold_bar': 400,
            'holy_relic': 250,
        }
        return values.get(item_name, 10)


class FenceManager:
    """Manages fences across all towns"""
    
    FENCE_NAMES = [
        "Shady Sam",
        "Fingers McGee",
        "The Broker",
        "Silent Eddie",
        "Black Market Bess",
        "Quick Nick",
        "No-Questions Quinn",
    ]
    
    def __init__(self):
        self.fences = {}  # {town_name: FenceNPC}
        
    def create_fence_for_town(self, town_name, tavern_x, tavern_y):
        """Create a fence for a town"""
        fence_name = random.choice(self.FENCE_NAMES)
        fence = FenceNPC(fence_name, town_name, tavern_x, tavern_y)
        self.fences[town_name] = fence
        return fence
    
    def get_fence(self, town_name):
        """Get fence for a town, or None if not discovered"""
        return self.fences.get(town_name)
    
    def discover_fence(self, town_name):
        """Mark fence as discovered for a town"""
        fence = self.fences.get(town_name)
        if fence:
            fence.discovered = True
    
    def get_nearby_fence(self, player_x, player_y, town_name, game_time, max_distance=100):
        """
        Get fence near player if:
        - Fence exists for this town
        - Fence is discovered
        - Fence is active (night time)
        - Player is within range
        """
        fence = self.fences.get(town_name)
        if not fence or not fence.discovered:
            return None
        
        if not fence.is_active(game_time):
            return None
        
        dx = abs(player_x - fence.x)
        dy = abs(player_y - fence.y)
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance <= max_distance:
            return fence
        
        return None
