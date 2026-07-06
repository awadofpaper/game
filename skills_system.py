"""
Skills System - Runescape-style gathering and production skills
Mining, Woodcutting, Fishing, Cooking (1-100 levels each)
"""

import math
import json

class Skill:
    """Individual skill with level and XP tracking"""
    
    def __init__(self, name, level=1, xp=0):
        self.name = name
        self.level = level
        self.xp = xp
        self.max_level = 100
        
    def get_xp_for_level(self, level):
        """Calculate total XP needed to reach a level (exponential curve)"""
        if level <= 1:
            return 0
        # Exponential formula: XP = sum of (level^2.5 * 10) for each level
        # This creates a MAJOR GRIND - level 99 requires ~5.6 million copper ore
        total_xp = 0
        for lvl in range(2, level + 1):
            total_xp += int((lvl ** 2.5) * 10)
        return total_xp
    
    def get_xp_to_next_level(self):
        """Get XP needed to reach next level"""
        if self.level >= self.max_level:
            return 0
        current_level_xp = self.get_xp_for_level(self.level)
        next_level_xp = self.get_xp_for_level(self.level + 1)
        return next_level_xp - current_level_xp
    
    def get_progress_to_next_level(self):
        """Get progress percentage to next level (0.0 - 1.0)"""
        if self.level >= self.max_level:
            return 1.0
        current_level_xp = self.get_xp_for_level(self.level)
        next_level_xp = self.get_xp_for_level(self.level + 1)
        xp_in_level = self.xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        return xp_in_level / xp_needed if xp_needed > 0 else 0.0
    
    def add_xp(self, amount):
        """Add XP and check for level ups. Returns list of levels gained."""
        if self.level >= self.max_level:
            return []
        
        self.xp += amount
        levels_gained = []
        
        # Check for level ups
        while self.level < self.max_level:
            xp_needed = self.get_xp_for_level(self.level + 1)
            if self.xp >= xp_needed:
                self.level += 1
                levels_gained.append(self.level)
            else:
                break
        
        return levels_gained
    
    def can_perform_action(self, required_level):
        """Check if skill level is high enough"""
        return self.level >= required_level
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'name': self.name,
            'level': self.level,
            'xp': self.xp
        }
    
    @staticmethod
    def from_dict(data):
        """Deserialize from dictionary"""
        return Skill(data['name'], data['level'], data['xp'])


class SkillsManager:
    """Manages all skills for a player or NPC"""
    
    # Skill definitions
    MINING = "Mining"
    WOODCUTTING = "Woodcutting"
    FISHING = "Fishing"
    COOKING = "Cooking"
    MERCHANT = "Merchant"
    ATHLETICS = "Athletics"
    
    def __init__(self):
        self.skills = {
            self.MINING: Skill(self.MINING),
            self.WOODCUTTING: Skill(self.WOODCUTTING),
            self.FISHING: Skill(self.FISHING),
            self.COOKING: Skill(self.COOKING),
            self.MERCHANT: Skill(self.MERCHANT),
            self.ATHLETICS: Skill(self.ATHLETICS)
        }
        # Perks tracking (unlocked at specific levels)
        self.perks = {
            # Gathering perks
            'auto_bank_mining': False,
            'auto_bank_woodcutting': False,
            'auto_bank_fishing': False,
            
            # Merchant skill perks (Trading/Commerce)
            'novice_appraiser': False,    # Level 10: +10% appraisal accuracy
            'sharp_eye': False,           # Level 20: Auto-identify common items
            'market_insight': False,      # Level 25: See price trends
            'silver_tongue': False,       # Level 30: +10% haggling success
            'expert_appraiser': False,    # Level 40: +25% appraisal accuracy, auto-identify uncommon
            'negotiator': False,          # Level 50: 25% transaction fee reduction
            'deal_finder': False,         # Level 60: 5% discount on all purchases
            'master_appraiser': False,    # Level 70: +50% appraisal accuracy, auto-identify rare
            'bulk_trader': False,         # Level 75: Double transaction limits
            'persuasion_expert': False,   # Level 80: +25% haggling success
            'arbitrage_master': False,    # Level 90: See prices in all towns
            'trade_baron': False,         # Level 95: +10% gold from all sales
            
            # Athletics skill perks
            'basic_diver': False,         # Level 10: +10 seconds breath
            'marathon_runner': False,     # Level 25: Reduce running stamina drain by 25%
            'trained_swimmer': False,     # Level 30: +20 seconds breath
            'iron_lungs': False,          # Level 50: Reduce sprinting stamina drain by 25%
            'pearl_diver': False,         # Level 60: +30 seconds breath
            'second_wind': False,         # Level 75: Stamina regenerates 50% faster
            'master_freediver': False,    # Level 85: +40 seconds breath
            'endurance_training': False,  # Level 90: Increase max stamina by 50
        }
    
    def get_skill(self, skill_name):
        """Get a specific skill"""
        return self.skills.get(skill_name)
    
    def get_level(self, skill_name):
        """Get level of a specific skill"""
        skill = self.skills.get(skill_name)
        return skill.level if skill else 1
    
    def get_xp(self, skill_name):
        """Get XP of a specific skill"""
        skill = self.skills.get(skill_name)
        return skill.xp if skill else 0
    
    def add_xp(self, skill_name, amount):
        """Add XP to a skill. Returns levels gained."""
        skill = self.skills.get(skill_name)
        if skill:
            levels_gained = skill.add_xp(amount)
            # Check for perk unlocks at level 75
            if levels_gained:
                self.check_perk_unlocks(skill_name)
            return levels_gained
        return []
    
    def check_perk_unlocks(self, skill_name):
        """Check for available perks based on skill levels (does not auto-unlock)"""
        skill = self.skills.get(skill_name)
        if not skill:
            return
        
        # Note: Perks are now available but must be manually unlocked by player
        # This function is kept for compatibility but does not auto-unlock
        pass
    
    def get_available_perks(self, skill_name):
        """Get list of perks available for a skill at current level"""
        skill = self.skills.get(skill_name)
        if not skill:
            return []
        
        available = []
        
        # Auto-bank perks
        if skill_name == self.MINING and skill.level >= 75:
            available.append(('auto_bank_mining', 'Auto-Bank Mining', 75, 'Mined resources automatically go to your bank'))
        elif skill_name == self.WOODCUTTING and skill.level >= 75:
            available.append(('auto_bank_woodcutting', 'Auto-Bank Woodcutting', 75, 'Woodcutting resources automatically go to your bank'))
        elif skill_name == self.FISHING and skill.level >= 75:
            available.append(('auto_bank_fishing', 'Auto-Bank Fishing', 75, 'Fishing resources automatically go to your bank'))
        
        # Merchant skill perks
        if skill_name == self.MERCHANT:
            merchant_perks = [
                (10, 'novice_appraiser', 'Novice Appraiser', '+10% appraisal accuracy'),
                (20, 'sharp_eye', 'Sharp Eye', 'Auto-identify common items'),
                (25, 'market_insight', 'Market Insight', 'View price trends and history'),
                (30, 'silver_tongue', 'Silver Tongue', '+10% haggling success chance'),
                (40, 'expert_appraiser', 'Expert Appraiser', '+25% appraisal accuracy, identify uncommon items'),
                (50, 'negotiator', 'Negotiator', '25% transaction fee reduction'),
                (60, 'deal_finder', 'Deal Finder', '5% discount on all purchases'),
                (70, 'master_appraiser', 'Master Appraiser', '+50% appraisal accuracy, identify rare items'),
                (75, 'bulk_trader', 'Bulk Trader', 'Double transaction limits'),
                (80, 'persuasion_expert', 'Persuasion Expert', '+25% haggling success chance'),
                (90, 'arbitrage_master', 'Arbitrage Master', 'See prices in all towns'),
                (95, 'trade_baron', 'Trade Baron', '+10% bonus gold from all sales')
            ]
            for req_level, perk_key, perk_name, perk_desc in merchant_perks:
                if skill.level >= req_level:
                    available.append((perk_key, perk_name, req_level, perk_desc))
        
        # Athletics skill perks
        if skill_name == self.ATHLETICS:
            athletics_perks = [
                (10, 'basic_diver', 'Basic Diver', '+10 seconds breath underwater'),
                (25, 'marathon_runner', 'Marathon Runner', 'Reduce running stamina drain by 25%'),
                (30, 'trained_swimmer', 'Trained Swimmer', '+20 seconds breath underwater'),
                (50, 'iron_lungs', 'Iron Lungs', 'Reduce sprinting stamina drain by 25%'),
                (60, 'pearl_diver', 'Pearl Diver', '+30 seconds breath underwater'),
                (75, 'second_wind', 'Second Wind', 'Stamina regenerates 50% faster'),
                (85, 'master_freediver', 'Master Freediver', '+40 seconds breath underwater'),
                (90, 'endurance_training', 'Endurance Training', 'Increase max stamina by 50')
            ]
            for req_level, perk_key, perk_name, perk_desc in athletics_perks:
                if skill.level >= req_level:
                    available.append((perk_key, perk_name, req_level, perk_desc))
        
        return available
    
    def unlock_perk(self, perk_key):
        """Manually unlock a perk (returns success boolean)"""
        if perk_key in self.perks:
            if not self.perks[perk_key]:
                self.perks[perk_key] = True
                return True
        return False
    
    def has_auto_bank(self, skill_name):
        """Check if player has auto-bank perk for a skill"""
        perk_mapping = {
            self.MINING: 'auto_bank_mining',
            self.WOODCUTTING: 'auto_bank_woodcutting',
            self.FISHING: 'auto_bank_fishing',
        }
        perk_name = perk_mapping.get(skill_name)
        return self.perks.get(perk_name, False) if perk_name else False
    
    def get_appraisal_bonus(self):
        """Get total appraisal accuracy bonus from merchant perks"""
        bonus = 0
        if self.perks.get('novice_appraiser', False):
            bonus += 10
        if self.perks.get('expert_appraiser', False):
            bonus += 25
        if self.perks.get('master_appraiser', False):
            bonus += 50
        return min(bonus, 85)  # Cap at 85% bonus
    
    def get_haggling_bonus(self):
        """Get total haggling success bonus from merchant perks"""
        bonus = 0
        if self.perks.get('silver_tongue', False):
            bonus += 10
        if self.perks.get('persuasion_expert', False):
            bonus += 25
        return min(bonus, 35)  # Cap at 35% bonus
    
    def get_purchase_discount(self):
        """Get purchase discount percentage from merchant perks"""
        if self.perks.get('deal_finder', False):
            return 5
        return 0
    
    def get_sales_bonus(self):
        """Get sales bonus percentage from merchant perks"""
        if self.perks.get('trade_baron', False):
            return 10
        return 0
    
    def can_auto_identify(self, item_rarity: str):
        """Check if player can auto-identify an item based on rarity"""
        rarity_lower = item_rarity.lower()
        
        # Master Appraiser: identify up to rare
        if self.perks.get('master_appraiser', False):
            return rarity_lower in ['common', 'uncommon', 'rare']
        
        # Expert Appraiser: identify up to uncommon
        if self.perks.get('expert_appraiser', False):
            return rarity_lower in ['common', 'uncommon']
        
        # Sharp Eye: identify common only
        if self.perks.get('sharp_eye', False):
            return rarity_lower == 'common'
        
        return False
    
    def has_transaction_fee_reduction(self):
        """Check if player has transaction fee reduction"""
        return self.perks.get('negotiator', False)
    
    def has_bulk_trading(self):
        """Check if player has bulk trading perk"""
        return self.perks.get('bulk_trader', False)
    
    def has_arbitrage_vision(self):
        """Check if player can see prices in all towns"""
        return self.perks.get('arbitrage_master', False)
    
    def get_total_level(self):
        """Get sum of all skill levels"""
        return sum(skill.level for skill in self.skills.values())
    
    def get_total_xp(self):
        """Get sum of all skill XP"""
        return sum(skill.xp for skill in self.skills.values())
    
    def can_perform_action(self, skill_name, required_level):
        """Check if can perform an action requiring a skill level"""
        skill = self.skills.get(skill_name)
        return skill.can_perform_action(required_level) if skill else False
    
    def to_dict(self):
        """Serialize all skills"""
        return {name: skill.to_dict() for name, skill in self.skills.items()}
    
    def from_dict(self, data):
        """Deserialize all skills"""
        for name, skill_data in data.items():
            if name in self.skills:
                self.skills[name] = Skill.from_dict(skill_data)


# Resource definitions with XP rewards and level requirements
MINING_RESOURCES = {
    'copper': {'level': 1, 'xp': 5, 'respawn_days': 1, 'color': (184, 115, 51)},
    'tin': {'level': 1, 'xp': 5, 'respawn_days': 1, 'color': (192, 192, 192)},
    'iron': {'level': 15, 'xp': 15, 'respawn_days': 2, 'color': (169, 169, 169)},
    'coal': {'level': 30, 'xp': 25, 'respawn_days': 3, 'color': (64, 64, 64)},
    'silver': {'level': 40, 'xp': 40, 'respawn_days': 4, 'color': (211, 211, 211)},
    'gold': {'level': 50, 'xp': 50, 'respawn_days': 5, 'color': (255, 215, 0)},
    'mithril': {'level': 55, 'xp': 80, 'respawn_days': 6, 'color': (100, 149, 237)},
    'adamantite': {'level': 70, 'xp': 100, 'respawn_days': 8, 'color': (0, 255, 127)},
    'runite': {'level': 85, 'xp': 125, 'respawn_days': 10, 'color': (0, 255, 255)}
}

WOODCUTTING_RESOURCES = {
    'wood': {'level': 1, 'xp': 5, 'respawn_days': 1, 'color': (139, 90, 43)},
    'oak_logs': {'level': 15, 'xp': 15, 'respawn_days': 2, 'color': (160, 120, 60)},
    'willow_logs': {'level': 30, 'xp': 30, 'respawn_days': 3, 'color': (180, 180, 120)},
    'maple_logs': {'level': 45, 'xp': 50, 'respawn_days': 5, 'color': (205, 133, 63)},
    'yew_logs': {'level': 60, 'xp': 80, 'respawn_days': 7, 'color': (107, 142, 35)},
    'magic_logs': {'level': 75, 'xp': 125, 'respawn_days': 10, 'color': (138, 43, 226)}
}

FISHING_RESOURCES = {
    'shrimp': {'level': 1, 'xp': 5, 'respawn_days': 1, 'color': (255, 182, 193)},
    'sardine': {'level': 5, 'xp': 8, 'respawn_days': 1, 'color': (176, 196, 222)},
    'herring': {'level': 10, 'xp': 12, 'respawn_days': 2, 'color': (192, 192, 192)},
    'trout': {'level': 20, 'xp': 20, 'respawn_days': 3, 'color': (189, 183, 107)},
    'salmon': {'level': 30, 'xp': 30, 'respawn_days': 4, 'color': (250, 128, 114)},
    'tuna': {'level': 35, 'xp': 40, 'respawn_days': 5, 'color': (70, 130, 180)},
    'lobster': {'level': 40, 'xp': 50, 'respawn_days': 6, 'color': (220, 20, 60)},
    'swordfish': {'level': 50, 'xp': 75, 'respawn_days': 8, 'color': (106, 90, 205)},
    'shark': {'level': 76, 'xp': 110, 'respawn_days': 10, 'color': (105, 105, 105)}
}

# Cooking XP and requirements (burns at low levels)
COOKING_RESOURCES = {
    'shrimp': {'level': 1, 'xp': 5, 'burn_level': 35, 'heals': 3},
    'sardine': {'level': 5, 'xp': 8, 'burn_level': 40, 'heals': 5},
    'herring': {'level': 10, 'xp': 12, 'burn_level': 45, 'heals': 7},
    'trout': {'level': 20, 'xp': 20, 'burn_level': 50, 'heals': 10},
    'salmon': {'level': 30, 'xp': 30, 'burn_level': 60, 'heals': 15},
    'tuna': {'level': 35, 'xp': 40, 'burn_level': 65, 'heals': 18},
    'lobster': {'level': 40, 'xp': 50, 'burn_level': 75, 'heals': 22},
    'swordfish': {'level': 50, 'xp': 75, 'burn_level': 85, 'heals': 28},
    'shark': {'level': 76, 'xp': 110, 'burn_level': 99, 'heals': 35}
}

# Tool definitions (tied to mining level)
MINING_TOOLS = {
    'bronze_pickaxe': {'level': 1, 'speed': 1.0, 'craft_level': 1, 'materials': {'copper': 1, 'tin': 1}},
    'iron_pickaxe': {'level': 10, 'speed': 0.8, 'craft_level': 15, 'materials': {'iron': 3}},
    'steel_pickaxe': {'level': 20, 'speed': 0.65, 'craft_level': 30, 'materials': {'iron': 2, 'coal': 2}},
    'mithril_pickaxe': {'level': 30, 'speed': 0.5, 'craft_level': 55, 'materials': {'mithril': 3}},
    'adamant_pickaxe': {'level': 40, 'speed': 0.4, 'craft_level': 70, 'materials': {'adamantite': 3}},
    'rune_pickaxe': {'level': 50, 'speed': 0.3, 'craft_level': 85, 'materials': {'runite': 3}}
}

WOODCUTTING_TOOLS = {
    'bronze_axe': {'level': 1, 'speed': 1.0, 'craft_level': 1, 'materials': {'copper': 1, 'tin': 1}},
    'iron_axe': {'level': 10, 'speed': 0.8, 'craft_level': 15, 'materials': {'iron': 3}},
    'steel_axe': {'level': 20, 'speed': 0.65, 'craft_level': 30, 'materials': {'iron': 2, 'coal': 2}},
    'mithril_axe': {'level': 30, 'speed': 0.5, 'craft_level': 55, 'materials': {'mithril': 3}},
    'adamant_axe': {'level': 40, 'speed': 0.4, 'craft_level': 70, 'materials': {'adamantite': 3}},
    'rune_axe': {'level': 50, 'speed': 0.3, 'craft_level': 85, 'materials': {'runite': 3}}
}

FISHING_TOOLS = {
    'fishing_net': {'level': 1, 'speed': 1.0, 'fish_types': ['shrimp', 'sardine']},
    'fishing_rod': {'level': 10, 'speed': 0.8, 'fish_types': ['herring', 'trout', 'salmon']},
    'harpoon': {'level': 35, 'speed': 0.6, 'fish_types': ['tuna', 'swordfish']},
    'lobster_pot': {'level': 40, 'speed': 0.7, 'fish_types': ['lobster']},
    'shark_harpoon': {'level': 76, 'speed': 0.5, 'fish_types': ['shark']}
}
