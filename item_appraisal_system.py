"""
Item Appraisal System
Unknown items need identification, appraisal skill progression
"""

import random
from typing import Optional, Tuple
from logger_config import logger


class UnidentifiedItem:
    """Represents an item that hasn't been identified yet"""
    
    def __init__(self, item_id: str, true_name: str, true_value: int,
                 rarity: str, category: str):
        self.item_id = item_id
        self.true_name = true_name
        self.true_value = true_value
        self.rarity = rarity  # 'common', 'uncommon', 'rare', 'legendary'
        self.category = category
        self.identified = False
        
        # Mystery appearance
        self.mystery_name = self._generate_mystery_name()
        self.estimated_value = self._estimate_value()
        
    def _generate_mystery_name(self) -> str:
        """Generate a mystery name based on category and rarity"""
        prefixes = {
            'common': 'Ordinary',
            'uncommon': 'Strange',
            'rare': 'Mysterious',
            'legendary': 'Ancient'
        }
        
        category_names = {
            'weapons': 'Weapon',
            'armor': 'Armor',
            'potions': 'Potion',
            'jewelry': 'Jewelry',
            'materials': 'Material',
            'scrolls': 'Scroll',
            'artifacts': 'Artifact'
        }
        
        prefix = prefixes.get(self.rarity, 'Unknown')
        cat_name = category_names.get(self.category, 'Item')
        
        return f"{prefix} {cat_name}"
    
    def _estimate_value(self) -> str:
        """Generate vague value estimate"""
        if self.true_value < 50:
            return "Worthless"
        elif self.true_value < 200:
            return "A few coins"
        elif self.true_value < 500:
            return "Modest value"
        elif self.true_value < 1000:
            return "Valuable"
        elif self.true_value < 2000:
            return "Very valuable"
        else:
            return "Priceless"
    
    def identify(self) -> str:
        """Identify the item, returns discovery message"""
        self.identified = True
        message = f"Identified: {self.mystery_name} is actually {self.true_name}! (Worth {self.true_value}g)"
        logger.info(f"[APPRAISAL] {message}")
        return message


class AppraisalSkill:
    """Player's appraisal skill progression"""
    
    def __init__(self):
        self.level = 1
        self.experience = 0
        self.auto_identify_threshold = 100  # Auto-identify items worth < 100g
        
    def get_appraisal_chance(self, item_rarity: str) -> float:
        """Get chance to successfully appraise an item"""
        base_chances = {
            'common': 0.9,
            'uncommon': 0.7,
            'rare': 0.5,
            'legendary': 0.2
        }
        
        base = base_chances.get(item_rarity, 0.5)
        level_bonus = self.level * 0.05  # +5% per level
        
        return min(0.95, base + level_bonus)  # Max 95%
    
    def can_auto_identify(self, item_value: int) -> bool:
        """Check if item is automatically identified"""
        return item_value < self.auto_identify_threshold
    
    def gain_experience(self, item_rarity: str):
        """Gain appraisal experience"""
        xp_values = {
            'common': 5,
            'uncommon': 15,
            'rare': 40,
            'legendary': 100
        }
        
        xp = xp_values.get(item_rarity, 10)
        self.experience += xp
        
        # Level up check
        xp_needed = self.level * 100
        if self.experience >= xp_needed:
            self.level_up()
    
    def level_up(self):
        """Level up appraisal skill"""
        self.level += 1
        self.experience = 0
        self.auto_identify_threshold = self.level * 100
        logger.info(f"[APPRAISAL] Skill level up! Now level {self.level}")
        return f"Appraisal skill increased to {self.level}! Auto-identify items worth < {self.auto_identify_threshold}g"


class AppraisalSystem:
    """Manages item appraisal across the game"""
    
    APPRAISAL_BASE_COST = 10
    
    def __init__(self):
        self.unidentified_items = {}  # item_id → UnidentifiedItem
        self.player_skill = AppraisalSkill()
        self.merchants_who_appraise = [
            'general_merchant',
            'jewelry_merchant',
            'antique_dealer',
            'wise_merchant'
        ]
        
    def create_unidentified_item(self, item_id: str, true_name: str,
                                true_value: int, rarity: str, category: str) -> UnidentifiedItem:
        """Create a new unidentified item"""
        item = UnidentifiedItem(item_id, true_name, true_value, rarity, category)
        
        # Auto-identify if skill is high enough
        if self.player_skill.can_auto_identify(true_value):
            item.identified = True
            logger.info(f"[APPRAISAL] Auto-identified {true_name} (skill level {self.player_skill.level})")
        else:
            self.unidentified_items[item_id] = item
            
        return item
    
    def is_identified(self, item_id: str) -> bool:
        """Check if item is identified"""
        if item_id not in self.unidentified_items:
            return True  # Not in system = already identified
        return self.unidentified_items[item_id].identified
    
    def get_display_name(self, item_id: str) -> str:
        """Get name to display (mystery name or true name)"""
        if item_id not in self.unidentified_items:
            return item_id  # Use original name
        
        item = self.unidentified_items[item_id]
        if item.identified:
            return item.true_name
        return item.mystery_name
    
    def get_display_value(self, item_id: str) -> str:
        """Get value to display (??? or actual value)"""
        if item_id not in self.unidentified_items:
            return "known"
        
        item = self.unidentified_items[item_id]
        if item.identified:
            return f"{item.true_value}g"
        return f"??? ({item.estimated_value})"
    
    def calculate_appraisal_cost(self, item_id: str) -> int:
        """Calculate cost to appraise an item"""
        if item_id not in self.unidentified_items:
            return 0
        
        item = self.unidentified_items[item_id]
        
        # Cost based on rarity
        rarity_costs = {
            'common': 5,
            'uncommon': 10,
            'rare': 25,
            'legendary': 50
        }
        
        return rarity_costs.get(item.rarity, 10)
    
    def attempt_merchant_appraisal(self, item_id: str, merchant_id: str,
                                   player) -> Tuple[bool, str, int]:
        """
        Player pays merchant to appraise item
        Returns (success, message, cost)
        """
        if item_id not in self.unidentified_items:
            return False, "This item is already identified!", 0
        
        item = self.unidentified_items[item_id]
        
        if item.identified:
            return False, "This item is already identified!", 0
        
        cost = self.calculate_appraisal_cost(item_id)
        
        if player.dubloons < cost:
            return False, f"Appraisal costs {cost}g. You can't afford it!", 0
        
        # Merchant always succeeds (player is paying for the service)
        player.dubloons -= cost
        message = item.identify()
        
        # Player gains appraisal XP
        level_up_msg = self.player_skill.gain_experience(item.rarity)
        if level_up_msg:
            message += f"\n{level_up_msg}"
        
        return True, message, cost
    
    def attempt_self_appraisal(self, item_id: str) -> Tuple[bool, str]:
        """
        Player attempts to identify item themselves
        Returns (success, message)
        """
        if item_id not in self.unidentified_items:
            return False, "This item is already identified!"
        
        item = self.unidentified_items[item_id]
        
        if item.identified:
            return False, "This item is already identified!"
        
        # Check skill chance
        chance = self.player_skill.get_appraisal_chance(item.rarity)
        
        if random.random() < chance:
            # Success!
            message = item.identify()
            level_up_msg = self.player_skill.gain_experience(item.rarity)
            if level_up_msg:
                message += f"\n{level_up_msg}"
            return True, message
        else:
            # Failure - still gain small XP
            self.player_skill.gain_experience('common')
            return False, f"You failed to identify the {item.mystery_name}. Try again or pay a merchant."
    
    def get_unidentified_count(self) -> int:
        """Get count of unidentified items"""
        return sum(1 for item in self.unidentified_items.values() if not item.identified)
    
    def get_all_unidentified(self) -> list:
        """Get list of all unidentified items"""
        return [
            {
                'item_id': item.item_id,
                'mystery_name': item.mystery_name,
                'estimated_value': item.estimated_value,
                'rarity': item.rarity,
                'appraisal_cost': self.calculate_appraisal_cost(item.item_id)
            }
            for item in self.unidentified_items.values()
            if not item.identified
        ]
    
    def to_dict(self) -> dict:
        """Serialize"""
        return {
            'unidentified_items': {
                item_id: {
                    'true_name': item.true_name,
                    'true_value': item.true_value,
                    'rarity': item.rarity,
                    'category': item.category,
                    'identified': item.identified
                }
                for item_id, item in self.unidentified_items.items()
            },
            'player_skill': {
                'level': self.player_skill.level,
                'experience': self.player_skill.experience,
                'auto_identify_threshold': self.player_skill.auto_identify_threshold
            }
        }
    
    def from_dict(self, data: dict):
        """Deserialize"""
        # Restore unidentified items
        for item_id, item_data in data.get('unidentified_items', {}).items():
            item = UnidentifiedItem(
                item_id,
                item_data['true_name'],
                item_data['true_value'],
                item_data['rarity'],
                item_data['category']
            )
            item.identified = item_data.get('identified', False)
            self.unidentified_items[item_id] = item
        
        # Restore player skill
        skill_data = data.get('player_skill', {})
        self.player_skill.level = skill_data.get('level', 1)
        self.player_skill.experience = skill_data.get('experience', 0)
        self.player_skill.auto_identify_threshold = skill_data.get('auto_identify_threshold', 100)
