"""
Locked chest system for the RPG game.
Chests require lockpicks and skill checks to open.
"""

import pygame
import random

class LockedChest:
    """Represents a locked chest that can be picked"""
    
    CHEST_TYPES = {
        "common": {
            "difficulty": 5,
            "color": (139, 69, 19),
            "loot_multiplier": 1.0,
            "gold_range": (5, 20)
        },
        "uncommon": {
            "difficulty": 15,
            "color": (50, 205, 50),
            "loot_multiplier": 1.5,
            "gold_range": (15, 40)
        },
        "rare": {
            "difficulty": 25,
            "color": (65, 105, 225),
            "loot_multiplier": 2.0,
            "gold_range": (30, 80)
        },
        "epic": {
            "difficulty": 40,
            "color": (138, 43, 226),
            "loot_multiplier": 3.0,
            "gold_range": (60, 150)
        },
        "legendary": {
            "difficulty": 60,
            "color": (255, 215, 0),
            "loot_multiplier": 4.0,
            "gold_range": (100, 300)
        }
    }
    
    def __init__(self, x, y, chest_type="common"):
        self.x = x
        self.y = y
        self.chest_type = chest_type
        self.opened = False
        self.jammed = False
        self.rect = pygame.Rect(x - 16, y - 16, 32, 32)
        
    def get_difficulty(self):
        """Get the lockpicking difficulty for this chest"""
        return self.CHEST_TYPES[self.chest_type]["difficulty"]
    
    def get_color(self):
        """Get the display color for this chest type"""
        return self.CHEST_TYPES[self.chest_type]["color"]
    
    def attempt_lockpick(self, player):
        """
        Attempt to pick the lock
        Returns: (success: bool, message: str, broke_pick: bool)
        """
        if self.opened:
            return False, "This chest is already open!", False
        
        if self.jammed:
            return False, "This lock is jammed! You can't pick it.", False
        
        # Calculate success chance
        base_chance = 10
        difficulty = self.get_difficulty()
        
        # Check for lockpicking skills
        lockpick_bonus = 0
        if hasattr(player, 'acquired_skills'):
            if 'basic_lock_picking' in player.acquired_skills:
                lockpick_bonus += 10
            if 'improved_lock_picking' in player.acquired_skills:
                lockpick_bonus += 15
            if 'advanced_lock_picking' in player.acquired_skills:
                lockpick_bonus += 20
            if 'master_lock_picking' in player.acquired_skills:
                lockpick_bonus += 30
        
        # Add luck bonus
        luck_bonus = 0
        if hasattr(player, 'stats'):
            luck = player.stats.get_stat("Luck")
            luck_bonus = luck // 2  # Each 2 points of luck gives +1% chance
        
        # Calculate total success chance
        success_chance = base_chance + lockpick_bonus + luck_bonus - difficulty
        success_chance = max(5, min(95, success_chance))  # Clamp between 5-95%
        
        # Roll for success
        roll = random.randint(1, 100)
        
        if roll <= success_chance:
            # Success!
            self.opened = True
            return True, f"Successfully picked the {self.chest_type} lock! ({success_chance}% chance)", False
        else:
            # Failure - check for lockpick breaking
            break_chance = 30 - (lockpick_bonus // 2)  # Better skills reduce break chance
            break_chance = max(5, min(50, break_chance))
            
            broke_pick = random.randint(1, 100) <= break_chance
            
            # Check for lock jamming
            if not broke_pick:
                jam_chance = 20
                if random.randint(1, 100) <= jam_chance:
                    self.jammed = True
                    return False, f"Failed to pick lock and it JAMMED! Lock is now unpickable.", False
            
            message = f"Failed to pick the {self.chest_type} lock. ({success_chance}% chance)"
            if broke_pick:
                message += " Your lockpick BROKE!"
            
            return False, message, broke_pick
    
    def get_loot(self, player):
        """Generate loot for this chest"""
        if not self.opened:
            return []
        
        chest_data = self.CHEST_TYPES[self.chest_type]
        loot = []
        
        # Add gold
        gold_amount = random.randint(*chest_data["gold_range"])
        loot.append(("dubloons", gold_amount))
        
        # Add random items based on multiplier
        multiplier = chest_data["loot_multiplier"]
        num_items = int(random.randint(1, 3) * multiplier)
        
        possible_items = [
            "health_potion", "mana_potion", "stamina_potion",
            "strength_potion", "defense_potion", "antidote",
            "herbs", "ore", "cloth", "bones",
            "lockpick", "bomb", "torch", "rope"
        ]
        
        for _ in range(num_items):
            item = random.choice(possible_items)
            count = random.randint(1, int(3 * multiplier))
            loot.append((item, count))
        
        return loot


class LockedChestManager:
    """Manages all locked chests in the world"""
    
    def __init__(self):
        self.chests = []
    
    def spawn_chest(self, x, y, chest_type=None):
        """Spawn a new chest at the given location"""
        if chest_type is None:
            # Random chest type based on weights
            roll = random.randint(1, 100)
            if roll <= 50:
                chest_type = "common"
            elif roll <= 75:
                chest_type = "uncommon"
            elif roll <= 90:
                chest_type = "rare"
            elif roll <= 98:
                chest_type = "epic"
            else:
                chest_type = "legendary"
        
        chest = LockedChest(x, y, chest_type)
        self.chests.append(chest)
        return chest
    
    def get_nearby_chest(self, player_x, player_y, radius=60):
        """Find a chest near the player"""
        for chest in self.chests:
            if chest.opened:
                continue
            dx = chest.x - player_x
            dy = chest.y - player_y
            distance = (dx * dx + dy * dy) ** 0.5
            if distance <= radius:
                return chest
        return None
    
    def remove_opened_chests(self):
        """Remove chests that have been looted"""
        # Keep unopened chests and recently opened chests
        # You might want to add a timer before removing opened chests
        pass


def get_chest_manager():
    """Get the global chest manager instance"""
    if not hasattr(get_chest_manager, 'instance'):
        get_chest_manager.instance = LockedChestManager()
    return get_chest_manager.instance
