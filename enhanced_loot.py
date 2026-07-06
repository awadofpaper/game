"""
Enhanced loot system with unique boss drops, set items, and smart loot
"""
import random
from typing import Dict, List, Optional, Tuple

# Unique boss drops - Guaranteed legendary items from specific bosses
UNIQUE_BOSS_DROPS = {
    "stone_titan": {
        "guaranteed_drop": {
            "item": "earthshaker_hammer",
            "name": "Earthshaker Hammer",
            "type": "weapon",
            "slot": "main_hand",
            "rarity": "legendary",
            "damage": 85,
            "stats": {
                "Strength": 25,
                "Stamina": 15,
                "Ground_Slam_Damage": 50
            },
            "special_ability": "earthquake",
            "description": "The legendary hammer of the Stone Titan. Ground attacks have 25% chance to stun enemies."
        },
        "rare_drops": [
            {
                "item": "titan_stone_armor",
                "chance": 0.3,
                "rarity": "epic",
                "stats": {"Defense": 45, "Strength": 15}
            },
            {
                "item": "boulder_shield",
                "chance": 0.2,
                "rarity": "epic",
                "stats": {"Defense": 50, "Block_Chance": 25}
            }
        ]
    },
    
    "lich_king": {
        "guaranteed_drop": {
            "item": "crown_of_undeath",
            "name": "Crown of the Lich King",
            "type": "armor",
            "slot": "head",
            "rarity": "legendary",
            "defense": 30,
            "stats": {
                "Willpower": 30,
                "Magic": 25,
                "Necromantic_Power": 40
            },
            "special_ability": "raise_dead",
            "description": "The cursed crown of the Lich King. Grants ability to summon skeleton minions."
        },
        "rare_drops": [
            {
                "item": "phylactery_amulet",
                "chance": 0.3,
                "rarity": "epic",
                "stats": {"Willpower": 20, "Life_Drain": 15}
            },
            {
                "item": "soulreaver_staff",
                "chance": 0.25,
                "rarity": "epic",
                "stats": {"Magic": 40, "Dark_Damage": 30}
            }
        ]
    },
    
    "dragon_lord": {
        "guaranteed_drop": {
            "item": "dragonfire_blade",
            "name": "Dragonfire Blade",
            "type": "weapon",
            "slot": "main_hand",
            "rarity": "legendary",
            "damage": 95,
            "stats": {
                "Strength": 30,
                "Fire_Damage": 50,
                "Critical_Chance": 20
            },
            "special_ability": "dragon_breath",
            "description": "Forged from a dragon's fang. Attacks leave burning wounds that deal damage over time."
        },
        "rare_drops": [
            {
                "item": "dragonscale_armor",
                "chance": 0.35,
                "rarity": "epic",
                "stats": {"Defense": 60, "Fire_Resistance": 50}
            }
        ]
    },
    
    "void_horror": {
        "guaranteed_drop": {
            "item": "void_reaver",
            "name": "Void Reaver",
            "type": "weapon",
            "slot": "main_hand",
            "rarity": "legendary",
            "damage": 80,
            "stats": {
                "Magic": 35,
                "Void_Damage": 45,
                "Life_Steal": 15
            },
            "special_ability": "dimensional_rift",
            "description": "A weapon that tears through reality itself. Chance to banish enemies to the void."
        },
        "rare_drops": [
            {
                "item": "voidwalker_cloak",
                "chance": 0.3,
                "rarity": "epic",
                "stats": {"Stealth": 40, "Magic": 20}
            }
        ]
    }
}

# Loot quality scaling based on dungeon difficulty
DIFFICULTY_RARITY_MULTIPLIERS = {
    "easy": {
        "common": 0.60,
        "uncommon": 0.25,
        "rare": 0.10,
        "epic": 0.04,
        "legendary": 0.01
    },
    "normal": {
        "common": 0.50,
        "uncommon": 0.30,
        "rare": 0.15,
        "epic": 0.04,
        "legendary": 0.01
    },
    "hard": {
        "common": 0.40,
        "uncommon": 0.30,
        "rare": 0.20,
        "epic": 0.08,
        "legendary": 0.02
    },
    "nightmare": {
        "common": 0.25,
        "uncommon": 0.30,
        "rare": 0.25,
        "epic": 0.15,
        "legendary": 0.05
    },
    "hell": {
        "common": 0.15,
        "uncommon": 0.25,
        "rare": 0.30,
        "epic": 0.20,
        "legendary": 0.10
    }
}

# Equipment slot requirements for smart loot
EQUIPMENT_REQUIREMENTS = {
    "weapon": {
        "main_hand": {"min_strength": 0},
        "two_hand": {"min_strength": 10}
    },
    "armor": {
        "head": {"min_level": 1},
        "body": {"min_level": 1},
        "arms": {"min_level": 1},
        "hands": {"min_level": 1},
        "legs": {"min_level": 1},
        "feet": {"min_level": 1}
    }
}


class EnhancedLootSystem:
    """Enhanced loot system with smart drops and quality scaling"""
    
    def __init__(self):
        self.boss_drops = UNIQUE_BOSS_DROPS
        self.difficulty_multipliers = DIFFICULTY_RARITY_MULTIPLIERS
    
    def get_dungeon_difficulty_name(self, dungeon_level: int) -> str:
        """Convert dungeon level to difficulty name"""
        if dungeon_level <= 5:
            return "easy"
        elif dungeon_level <= 10:
            return "normal"
        elif dungeon_level <= 15:
            return "hard"
        elif dungeon_level <= 20:
            return "nightmare"
        else:
            return "hell"
    
    def get_scaled_rarity(self, base_rarity: str, difficulty: str) -> str:
        """Get rarity adjusted by dungeon difficulty"""
        if difficulty not in self.difficulty_multipliers:
            return base_rarity
        
        # Roll for rarity upgrade based on difficulty
        roll = random.random()
        cumulative = 0.0
        
        rarities = ["common", "uncommon", "rare", "epic", "legendary"]
        for rarity in rarities:
            cumulative += self.difficulty_multipliers[difficulty].get(rarity, 0)
            if roll <= cumulative:
                return rarity
        
        return base_rarity
    
    def can_player_use_item(self, player, item_data: Dict) -> bool:
        """Check if player meets requirements to use an item"""
        # Check level requirement
        min_level = item_data.get("min_level", 0)
        if player.level < min_level:
            return False
        
        # Check stat requirements
        if "requirements" in item_data:
            reqs = item_data["requirements"]
            player_stats = getattr(player, 'stats', {})
            
            for stat, value in reqs.items():
                if stat == "Strength" and player_stats.get("Strength", 0) < value:
                    return False
                elif stat == "Willpower" and player_stats.get("Willpower", 0) < value:
                    return False
                elif stat == "Agility" and player_stats.get("Agility", 0) < value:
                    return False
        
        return True
    
    def get_boss_guaranteed_drop(self, boss_type: str) -> Optional[Dict]:
        """Get the guaranteed unique drop for a boss"""
        if boss_type in self.boss_drops:
            return self.boss_drops[boss_type]["guaranteed_drop"].copy()
        return None
    
    def get_boss_rare_drops(self, boss_type: str) -> List[Dict]:
        """Get list of possible rare drops from a boss"""
        if boss_type in self.boss_drops:
            drops = []
            for drop in self.boss_drops[boss_type]["rare_drops"]:
                if random.random() < drop["chance"]:
                    drops.append(drop.copy())
            return drops
        return []
    
    def get_boss_loot_preview(self, boss_type: str) -> Dict:
        """Get preview of what a boss can drop"""
        if boss_type not in self.boss_drops:
            return {"guaranteed": None, "possible": []}
        
        boss_data = self.boss_drops[boss_type]
        
        return {
            "guaranteed": {
                "name": boss_data["guaranteed_drop"]["name"],
                "rarity": boss_data["guaranteed_drop"]["rarity"],
                "description": boss_data["guaranteed_drop"]["description"],
                "stats": boss_data["guaranteed_drop"].get("stats", {}),
                "special_ability": boss_data["guaranteed_drop"].get("special_ability", None)
            },
            "possible": [
                {
                    "item": drop["item"],
                    "chance": drop["chance"],
                    "rarity": drop["rarity"],
                    "stats": drop.get("stats", {})
                }
                for drop in boss_data["rare_drops"]
            ]
        }
    
    def filter_smart_loot(self, player, loot_items: List[Dict]) -> List[Dict]:
        """Filter loot to only include items the player can use"""
        usable_items = []
        
        for item in loot_items:
            if self.can_player_use_item(player, item):
                usable_items.append(item)
        
        return usable_items
    
    def apply_set_bonuses(self, player, equipped_items: Dict) -> Dict:
        """Calculate active set bonuses from equipped items"""
        from enemies import SET_ITEMS
        
        # Count pieces from each set
        set_counts = {}
        for slot, item in equipped_items.items():
            if item and hasattr(item, 'set_id'):
                set_id = item.set_id
                set_counts[set_id] = set_counts.get(set_id, 0) + 1
        
        # Calculate active bonuses
        active_bonuses = {}
        for set_id, count in set_counts.items():
            if set_id in SET_ITEMS:
                set_data = SET_ITEMS[set_id]
                # Get highest tier bonus player has unlocked
                for tier in sorted(set_data["bonuses"].keys()):
                    if count >= tier:
                        active_bonuses[set_id] = {
                            "name": set_data["name"],
                            "tier": tier,
                            "pieces": count,
                            "bonuses": set_data["bonuses"][tier]
                        }
        
        return active_bonuses


# Global instance
enhanced_loot_system = EnhancedLootSystem()


def get_enhanced_loot_system() -> EnhancedLootSystem:
    """Get the global enhanced loot system instance"""
    return enhanced_loot_system
