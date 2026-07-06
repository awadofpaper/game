"""
Criminal Underworld System - Part 2
- Criminal Skill Trees
- Market Manipulation
- Scamming/Fake Items
- Stolen Goods Appraisal
- Criminal Quest Paths
"""

import random
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ===== CRIMINAL SKILL TREES =====

class CriminalSkill:
    """Individual criminal skill"""
    
    def __init__(self, name: str, description: str, max_level: int, 
                 requirements: dict, effects: dict):
        self.name = name
        self.description = description
        self.level = 0
        self.max_level = max_level
        self.requirements = requirements  # {'skill': level, 'crime_count': X}
        self.effects = effects  # What bonuses this provides
        
    def can_level_up(self, player_skills: dict, crime_count: int) -> bool:
        """Check if can level up"""
        if self.level >= self.max_level:
            return False
        
        # Check requirements
        for req_skill, req_level in self.requirements.items():
            if req_skill == 'crime_count':
                if crime_count < req_level:
                    return False
            elif player_skills.get(req_skill, 0) < req_level:
                return False
        
        return True
    
    def level_up(self):
        """Increase skill level"""
        if self.level < self.max_level:
            self.level += 1
            logger.info(f"[CRIMINAL SKILL] {self.name} increased to level {self.level}")
            return True
        return False
    
    def get_effect_value(self, effect_name: str) -> float:
        """Get current effect value based on level"""
        if effect_name not in self.effects:
            return 0.0
        
        base_value = self.effects[effect_name]
        return base_value * self.level


class CriminalSkillTree:
    """Criminal skill tree system"""
    
    def __init__(self):
        self.skills = {}
        self.skill_points = 0
        self._initialize_skills()
        
    def _initialize_skills(self):
        """Initialize all criminal skills"""
        
        # STEALTH TREE
        self.skills['silent_movement'] = CriminalSkill(
            "Silent Movement",
            "Move more quietly, reducing detection range",
            5,
            {'crime_count': 5},
            {'detection_reduction': 10}  # -10% per level
        )
        
        self.skills['shadow_blend'] = CriminalSkill(
            "Shadow Blend",
            "Blend into shadows more effectively",
            5,
            {'crime_count': 10, 'silent_movement': 3},
            {'stealth_bonus': 15}  # +15% per level
        )
        
        self.skills['master_infiltrator'] = CriminalSkill(
            "Master Infiltrator",
            "Expert at infiltration and escape",
            3,
            {'crime_count': 30, 'shadow_blend': 5},
            {'infiltration_bonus': 20, 'escape_bonus': 15}
        )
        
        # LOCKPICKING TREE
        self.skills['nimble_fingers'] = CriminalSkill(
            "Nimble Fingers",
            "Pick locks faster and more reliably",
            5,
            {'crime_count': 5},
            {'lockpick_speed': 10, 'lockpick_success': 5}
        )
        
        self.skills['complex_locks'] = CriminalSkill(
            "Complex Locks",
            "Can pick advanced lock mechanisms",
            5,
            {'crime_count': 15, 'nimble_fingers': 3},
            {'advanced_locks': 1}  # Unlock advanced locks
        )
        
        self.skills['master_locksmith'] = CriminalSkill(
            "Master Locksmith",
            "Can crack any lock given time",
            3,
            {'crime_count': 40, 'complex_locks': 5},
            {'master_locks': 1, 'pick_time_reduction': 30}
        )
        
        # THEFT TREE
        self.skills['quick_hands'] = CriminalSkill(
            "Quick Hands",
            "Pickpocket more effectively",
            5,
            {'crime_count': 3},
            {'pickpocket_chance': 10, 'pickpocket_value': 15}
        )
        
        self.skills['burglar_expertise'] = CriminalSkill(
            "Burglar's Expertise",
            "Better loot from break-ins",
            5,
            {'crime_count': 20, 'quick_hands': 3},
            {'loot_multiplier': 15}  # +15% loot per level
        )
        
        self.skills['master_thief'] = CriminalSkill(
            "Master Thief",
            "Legendary theft abilities",
            3,
            {'crime_count': 50, 'burglar_expertise': 5},
            {'loot_multiplier': 25, 'detection_reduction': 20}
        )
        
        # COMBAT TREE
        self.skills['street_fighter'] = CriminalSkill(
            "Street Fighter",
            "Better at dirty fighting",
            5,
            {'crime_count': 5},
            {'damage_bonus': 10, 'crit_chance': 5}
        )
        
        self.skills['assassin_strike'] = CriminalSkill(
            "Assassin Strike",
            "Deadly sneak attacks",
            5,
            {'crime_count': 25, 'street_fighter': 3},
            {'sneak_attack_damage': 50}  # +50% damage per level
        )
        
        self.skills['silent_killer'] = CriminalSkill(
            "Silent Killer",
            "Kill without alerting others",
            3,
            {'crime_count': 50, 'assassin_strike': 5},
            {'silent_kill_chance': 30}
        )
        
        # DECEPTION TREE
        self.skills['silver_tongue'] = CriminalSkill(
            "Silver Tongue",
            "Better at lying and persuasion",
            5,
            {'crime_count': 5},
            {'persuasion_bonus': 10, 'bribe_discount': 10}
        )
        
        self.skills['master_of_disguise'] = CriminalSkill(
            "Master of Disguise",
            "Disguises are more effective",
            5,
            {'crime_count': 20, 'silver_tongue': 3},
            {'disguise_effectiveness': 20}
        )
        
        self.skills['con_artist'] = CriminalSkill(
            "Con Artist",
            "Expert at scams and cons",
            3,
            {'crime_count': 40, 'master_of_disguise': 5},
            {'scam_success': 25, 'scam_profit': 30}
        )
        
        # INTELLIGENCE TREE
        self.skills['criminal_network'] = CriminalSkill(
            "Criminal Network",
            "Better connections in underworld",
            5,
            {'crime_count': 10},
            {'fence_bonus': 5, 'contract_quality': 10}  # Better fence rates and contracts
        )
        
        self.skills['market_insider'] = CriminalSkill(
            "Market Insider",
            "Knowledge of market vulnerabilities",
            5,
            {'crime_count': 25, 'criminal_network': 3},
            {'market_manipulation': 15}
        )
        
        self.skills['crime_lord'] = CriminalSkill(
            "Crime Lord",
            "Command respect and fear",
            3,
            {'crime_count': 75, 'market_insider': 5},
            {'enterprise_income': 25, 'gang_influence': 30}
        )
    
    def earn_skill_point(self):
        """Earn a criminal skill point"""
        self.skill_points += 1
        logger.info(f"[CRIMINAL SKILLS] Skill point earned. Total: {self.skill_points}")
    
    def can_unlock_skill(self, skill_name: str, player_skills: dict, crime_count: int) -> Tuple[bool, str]:
        """Check if can unlock/level up a skill"""
        if skill_name not in self.skills:
            return False, "Skill not found"
        
        skill = self.skills[skill_name]
        
        if self.skill_points <= 0:
            return False, "No skill points available"
        
        if not skill.can_level_up(player_skills, crime_count):
            return False, "Requirements not met"
        
        return True, "Can unlock"
    
    def unlock_skill(self, skill_name: str) -> Tuple[bool, str]:
        """Unlock or level up a skill"""
        if self.skill_points <= 0:
            return False, "No skill points available"
        
        if skill_name not in self.skills:
            return False, "Skill not found"
        
        skill = self.skills[skill_name]
        if skill.level_up():
            self.skill_points -= 1
            return True, f"{skill.name} increased to level {skill.level}"
        
        return False, "Cannot level up skill"
    
    def get_total_bonus(self, effect_name: str) -> float:
        """Get total bonus from all skills for an effect"""
        total = 0.0
        for skill in self.skills.values():
            total += skill.get_effect_value(effect_name)
        return total


# ===== MARKET MANIPULATION =====

class MarketManipulation:
    """System for manipulating market prices"""
    
    def __init__(self):
        self.manipulated_markets = {}  # {item: {'town': str, 'type': str, 'duration': int}}
        self.cornered_markets = []  # Items player has monopolized
        self.price_history = {}  # Track price changes
        
    def buy_out_stock(self, item_name: str, town_name: str, quantity: int, 
                      price_per_item: int, player_gold: int) -> Tuple[bool, str, int]:
        """Buy out all stock of an item to create scarcity"""
        total_cost = quantity * price_per_item
        
        if player_gold < total_cost:
            return False, "Insufficient gold", 0
        
        # Successfully bought out
        self.manipulated_markets[item_name] = {
            'town': town_name,
            'type': 'scarcity',
            'duration': 7,  # Lasts 7 days
            'quantity_removed': quantity
        }
        
        logger.info(f"[MARKET] Bought out {quantity}x {item_name} in {town_name}")
        return True, f"Bought out {item_name} stock", total_cost
    
    def create_artificial_demand(self, item_name: str, town_name: str, 
                                 cost: int, player_gold: int) -> Tuple[bool, str]:
        """Spread rumors to increase demand"""
        if player_gold < cost:
            return False, "Insufficient gold for rumor campaign"
        
        self.manipulated_markets[item_name] = {
            'town': town_name,
            'type': 'demand',
            'duration': 5,  # Lasts 5 days
            'price_increase': 50  # +50% price
        }
        
        logger.info(f"[MARKET] Created demand for {item_name} in {town_name}")
        return True, f"Rumors spread about {item_name}"
    
    def dump_goods(self, item_name: str, town_name: str, quantity: int) -> bool:
        """Flood market to crash prices (hurt competitors)"""
        self.manipulated_markets[item_name] = {
            'town': town_name,
            'type': 'crash',
            'duration': 7,
            'price_decrease': 40  # -40% price
        }
        
        logger.info(f"[MARKET] Dumped {quantity}x {item_name} in {town_name}")
        return True
    
    def corner_market(self, item_name: str, town_name: str, investment: int) -> bool:
        """Monopolize an item market"""
        if item_name not in self.cornered_markets:
            self.cornered_markets.append(item_name)
            logger.info(f"[MARKET] Cornered market for {item_name}")
            return True
        return False
    
    def get_price_modifier(self, item_name: str, town_name: str) -> float:
        """Get price modifier due to manipulation"""
        if item_name in self.manipulated_markets:
            data = self.manipulated_markets[item_name]
            if data['town'] == town_name and data['duration'] > 0:
                if data['type'] == 'scarcity' or data['type'] == 'demand':
                    return 1.0 + (data.get('price_increase', 50) / 100.0)
                elif data['type'] == 'crash':
                    return 1.0 - (data.get('price_decrease', 40) / 100.0)
        
        # Corner market bonus
        if item_name in self.cornered_markets:
            return 1.3  # 30% markup when you control market
        
        return 1.0
    
    def update(self):
        """Update market manipulations (reduce duration)"""
        for item_name in list(self.manipulated_markets.keys()):
            data = self.manipulated_markets[item_name]
            data['duration'] -= 1
            if data['duration'] <= 0:
                del self.manipulated_markets[item_name]
                logger.info(f"[MARKET] Manipulation of {item_name} expired")


# ===== SCAMMING/FAKE ITEMS =====

class FakeItem:
    """Counterfeit or fake item"""
    
    def __init__(self, fake_name: str, appears_as: str, true_value: int, fake_value: int):
        self.fake_name = fake_name
        self.appears_as = appears_as  # What it looks like
        self.true_value = true_value  # What it's actually worth
        self.fake_value = fake_value  # What you sell it for
        self.quality = random.randint(40, 90)  # How good the fake is
        
    def will_be_detected(self, buyer_skill: int) -> bool:
        """Check if fake will be detected"""
        detection_chance = max(5, buyer_skill - self.quality)
        return random.randint(1, 100) < detection_chance


class ScammingSystem:
    """System for scamming merchants and creating fake items"""
    
    FAKE_RECIPES = {
        'fool_gold': {
            'appears_as': 'gold_bar',
            'materials': {'brass': 1, 'yellow_paint': 1},
            'cost': 20,
            'fake_value': 400,
            'true_value': 5
        },
        'glass_diamond': {
            'appears_as': 'diamond',
            'materials': {'glass': 1, 'polish': 1},
            'cost': 30,
            'fake_value': 500,
            'true_value': 10
        },
        'watered_wine': {
            'appears_as': 'fine_wine',
            'materials': {'cheap_wine': 1, 'water': 1},
            'cost': 5,
            'fake_value': 50,
            'true_value': 8
        },
        'counterfeit_deed': {
            'appears_as': 'property_deed',
            'materials': {'paper': 1, 'ink': 1, 'seal': 1},
            'cost': 50,
            'fake_value': 5000,
            'true_value': 20
        },
        'fake_potion': {
            'appears_as': 'health_potion',
            'materials': {'water': 1, 'red_dye': 1, 'bottle': 1},
            'cost': 3,
            'fake_value': 25,
            'true_value': 1
        },
    }
    
    def __init__(self):
        self.known_recipes = ['fool_gold']  # Start with basic recipe
        self.fake_items_in_circulation = []
        self.successful_scams = 0
        self.failed_scams = 0
        self.reputation_damage = 0  # Accumulates when caught
        
    def learn_recipe(self, recipe_name: str) -> bool:
        """Learn a new fake item recipe"""
        if recipe_name in self.FAKE_RECIPES and recipe_name not in self.known_recipes:
            self.known_recipes.append(recipe_name)
            logger.info(f"[SCAM] Learned recipe: {recipe_name}")
            return True
        return False
    
    def craft_fake_item(self, recipe_name: str, player_inventory: dict) -> Tuple[bool, str, Optional[FakeItem]]:
        """Craft a fake item"""
        if recipe_name not in self.known_recipes:
            return False, "Recipe unknown", None
        
        recipe = self.FAKE_RECIPES[recipe_name]
        
        # Check materials
        for material, qty in recipe['materials'].items():
            if player_inventory.get(material, 0) < qty:
                return False, f"Need {material}", None
        
        # Consume materials
        for material, qty in recipe['materials'].items():
            player_inventory[material] -= qty
        
        # Create fake item
        fake = FakeItem(
            recipe_name,
            recipe['appears_as'],
            recipe['true_value'],
            recipe['fake_value']
        )
        
        self.fake_items_in_circulation.append(fake)
        logger.info(f"[SCAM] Crafted {recipe_name}")
        return True, f"Crafted {recipe_name}", fake
    
    def attempt_scam(self, fake_item: FakeItem, merchant_name: str, 
                    merchant_skill: int) -> Tuple[bool, str, int]:
        """Attempt to sell fake item to merchant"""
        detected = fake_item.will_be_detected(merchant_skill)
        
        if detected:
            # Caught!
            self.failed_scams += 1
            self.reputation_damage += 20
            logger.info(f"[SCAM] Caught selling fake to {merchant_name}!")
            return False, f"{merchant_name} detected the fake! Guards called!", 0
        
        # Success!
        self.successful_scams += 1
        profit = fake_item.fake_value
        logger.info(f"[SCAM] Successfully scammed {merchant_name} for {profit}g")
        return True, f"Sold fake item for {profit}g", profit
    
    def run_confidence_scheme(self, scheme_type: str, target_wealth: int, 
                             player_skill: int) -> Tuple[bool, str, int]:
        """Run a confidence scheme"""
        schemes = {
            'shell_game': {
                'difficulty': 20,
                'profit_mult': 0.3,
                'description': "Classic shell game con"
            },
            'fake_investment': {
                'difficulty': 40,
                'profit_mult': 1.5,
                'description': "Ponzi scheme"
            },
            'long_con': {
                'difficulty': 60,
                'profit_mult': 3.0,
                'description': "Elaborate long con"
            }
        }
        
        if scheme_type not in schemes:
            return False, "Unknown scheme", 0
        
        scheme = schemes[scheme_type]
        success_chance = max(10, min(90, player_skill * 2 - scheme['difficulty']))
        
        if random.randint(1, 100) < success_chance:
            profit = int(target_wealth * scheme['profit_mult'])
            self.successful_scams += 1
            return True, f"{scheme['description']} successful!", profit
        else:
            self.failed_scams += 1
            return False, "Con failed! Target suspicious", 0


# ===== STOLEN GOODS APPRAISAL =====

class StolenGoodsAppraiser:
    """Advanced appraisal system for stolen goods"""
    
    ITEM_VALUES = {
        # Jewelry
        'gold_ring': {'base': 100, 'rare_mult': 2.0},
        'silver_necklace': {'base': 80, 'rare_mult': 1.8},
        'diamond_ring': {'base': 500, 'rare_mult': 3.0},
        'ruby_necklace': {'base': 400, 'rare_mult': 2.5},
        'family_heirloom': {'base': 300, 'rare_mult': 4.0},
        
        # Art
        'painting': {'base': 200, 'rare_mult': 5.0},
        'sculpture': {'base': 250, 'rare_mult': 4.0},
        'antique_vase': {'base': 150, 'rare_mult': 3.5},
        
        # Documents
        'town_records': {'base': 100, 'rare_mult': 1.5},
        'bank_records': {'base': 80, 'rare_mult': 1.3},
        'blackmail_material': {'base': 500, 'rare_mult': 2.0},
        'noble_letters': {'base': 300, 'rare_mult': 2.5},
        
        # Goods
        'silk_cloth': {'base': 40, 'rare_mult': 1.5},
        'spices': {'base': 30, 'rare_mult': 1.8},
        'wine_barrel': {'base': 50, 'rare_mult': 1.6},
        'weapon_cache': {'base': 200, 'rare_mult': 1.4},
    }
    
    def __init__(self):
        self.appraisal_skill = 0
        self.known_high_value_items = []
        
    def appraise_stolen_item(self, item_name: str, is_rare: bool = False) -> dict:
        """Appraise a stolen item"""
        if item_name not in self.ITEM_VALUES:
            # Unknown item - rough estimate
            return {
                'name': item_name,
                'estimated_value': random.randint(10, 100),
                'confidence': 'Low',
                'fence_value': random.randint(5, 50),
                'black_market_value': random.randint(20, 150),
                'heat_risk': random.randint(1, 10)
            }
        
        item_data = self.ITEM_VALUES[item_name]
        base_value = item_data['base']
        
        if is_rare:
            base_value = int(base_value * item_data['rare_mult'])
        
        # Skill affects estimate accuracy
        variance = max(0.1, 0.5 - (self.appraisal_skill / 200))
        estimated = int(base_value * random.uniform(1 - variance, 1 + variance))
        
        # Calculate different sale values
        fence_value = int(estimated * 0.4)  # Fences pay 40%
        black_market_value = int(estimated * 0.7)  # Black market pays 70%
        
        # Heat risk
        heat_risk = self._calculate_heat_risk(item_name, base_value)
        
        # Confidence in appraisal
        if self.appraisal_skill >= 75:
            confidence = 'Very High'
        elif self.appraisal_skill >= 50:
            confidence = 'High'
        elif self.appraisal_skill >= 25:
            confidence = 'Medium'
        else:
            confidence = 'Low'
        
        appraisal = {
            'name': item_name,
            'estimated_value': estimated,
            'confidence': confidence,
            'fence_value': fence_value,
            'black_market_value': black_market_value,
            'collector_value': int(estimated * 1.2),  # Collectors pay premium
            'heat_risk': heat_risk,
            'is_rare': is_rare
        }
        
        # Learn about high-value items
        if estimated > 300 and item_name not in self.known_high_value_items:
            self.known_high_value_items.append(item_name)
        
        logger.info(f"[APPRAISAL] {item_name}: {estimated}g (confidence: {confidence})")
        return appraisal
    
    def _calculate_heat_risk(self, item_name: str, value: int) -> int:
        """Calculate how much heat this item generates (1-10)"""
        base_heat = value // 100  # 1 heat per 100g value
        
        # Certain items generate more heat
        high_heat_items = ['crown', 'royal', 'noble', 'holy', 'artifact', 'relic']
        if any(keyword in item_name.lower() for keyword in high_heat_items):
            base_heat *= 2
        
        return min(10, max(1, base_heat))
    
    def identify_best_buyer(self, item_name: str, appraisal: dict) -> str:
        """Suggest best buyer for item"""
        if appraisal['is_rare']:
            return "Private Collector (highest price, but need to find one)"
        elif appraisal['heat_risk'] >= 7:
            return "Black Market (safer for hot items)"
        elif appraisal['estimated_value'] < 100:
            return "Regular Fence (quick and easy)"
        else:
            return "Elite Fence or Black Market Auction"
    
    def increase_appraisal_skill(self, amount: int):
        """Increase appraisal skill"""
        self.appraisal_skill = min(100, self.appraisal_skill + amount)


# ===== CRIMINAL QUEST PATHS =====

class CriminalQuest:
    """Criminal-themed quest"""
    
    def __init__(self, quest_id: str, name: str, description: str, 
                 quest_type: str, requirements: dict, rewards: dict):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.type = quest_type  # 'initiation', 'contract', 'vengeance', 'rise_to_power'
        self.requirements = requirements
        self.rewards = rewards
        self.completed = False
        self.failed = False
        self.progress = {}
        
    def check_completion(self, player_data: dict) -> bool:
        """Check if quest is complete"""
        for req_type, req_value in self.requirements.items():
            if req_type == 'crimes_committed':
                if player_data.get('crime_count', 0) < req_value:
                    return False
            elif req_type == 'item_stolen':
                if req_value not in player_data.get('stolen_items', []):
                    return False
            elif req_type == 'target_eliminated':
                if req_value not in player_data.get('eliminated_targets', []):
                    return False
            elif req_type == 'heist_completed':
                if req_value not in player_data.get('completed_heists', []):
                    return False
        
        self.completed = True
        return True


class CriminalQuestSystem:
    """Manages criminal quest paths"""
    
    def __init__(self):
        self.available_quests = []
        self.active_quests = []
        self.completed_quests = []
        self._initialize_quests()
        
    def _initialize_quests(self):
        """Create criminal quest paths"""
        
        # CAUGHT PATH - Unlock quests when caught
        caught_quest = CriminalQuest(
            'caught_redemption',
            "The Price of Freedom",
            "A mysterious figure offers to clear your record... for a price.",
            'initiation',
            {'times_caught': 1},
            {'gold': 500, 'unlock': 'criminal_contact'}
        )
        self.available_quests.append(caught_quest)
        
        # THIEVES GUILD PATH
        guild_initiation = CriminalQuest(
            'thieves_initiation',
            "Proving Your Worth",
            "The Thieves Guild wants you to steal a valuable item to prove yourself.",
            'initiation',
            {'item_stolen': 'guild_test_item', 'crimes_committed': 5},
            {'gold': 1000, 'unlock': 'thieves_guild_member', 'perk': 'guild_fence_access'}
        )
        self.available_quests.append(guild_initiation)
        
        guild_promotion = CriminalQuest(
            'thieves_promotion',
            "Master Thief Trial",
            "Complete an impossible heist to become a Master Thief.",
            'rise_to_power',
            {'heist_completed': 'legendary_heist', 'crimes_committed': 100},
            {'gold': 10000, 'rank': 'Master Thief', 'perk': 'legendary_thief'}
        )
        self.available_quests.append(guild_promotion)
        
        # ASSASSINS GUILD PATH
        assassin_initiation = CriminalQuest(
            'assassin_initiation',
            "The First Contract",
            "Eliminate a target to join the Assassins Guild.",
            'contract',
            {'target_eliminated': 'test_target'},
            {'gold': 800, 'unlock': 'assassins_guild_member', 'item': 'poison_kit'}
        )
        self.available_quests.append(assassin_initiation)
        
        # CRIME BOSS PATH
        establish_gang = CriminalQuest(
            'establish_gang',
            "Establishing Territory",
            "Take control of a district to start your own criminal empire.",
            'rise_to_power',
            {'crimes_committed': 50, 'businesses_controlled': 3},
            {'gold': 5000, 'unlock': 'gang_leader', 'passive_income': 100}
        )
        self.available_quests.append(establish_gang)
        
        # VENGEANCE PATH
        revenge = CriminalQuest(
            'vengeance_path',
            "Settling Scores",
            "Someone betrayed you. Time for payback.",
            'vengeance',
            {'target_eliminated': 'betrayer', 'evidence_stolen': 'betrayal_proof'},
            {'gold': 3000, 'reputation': 50, 'favor': 'major_favor'}
        )
        self.available_quests.append(revenge)
        
        # ESCAPE ARTIST PATH
        prison_break = CriminalQuest(
            'master_escape',
            "The Great Escape",
            "Orchestrate a legendary prison break.",
            'contract',
            {'successful_escapes': 3, 'prisoners_freed': 5},
            {'gold': 2000, 'perk': 'escape_artist', 'reputation': 100}
        )
        self.available_quests.append(prison_break)
        
        # KINGPIN PATH
        crime_empire = CriminalQuest(
            'criminal_empire',
            "Underworld Dominance",
            "Control the entire criminal underworld.",
            'rise_to_power',
            {'crimes_committed': 200, 'territories_controlled': 5, 
             'gangs_allied': 3, 'enterprises_owned': 5},
            {'gold': 50000, 'rank': 'Crime Kingpin', 'title': 'Kingpin', 
             'passive_income': 500}
        )
        self.available_quests.append(crime_empire)
    
    def unlock_quests_on_caught(self) -> List[CriminalQuest]:
        """Unlock special quests when player is caught"""
        unlocked = []
        for quest in self.available_quests:
            if 'times_caught' in quest.requirements:
                if quest not in self.active_quests:
                    self.active_quests.append(quest)
                    unlocked.append(quest)
                    logger.info(f"[QUEST] Unlocked: {quest.name}")
        return unlocked
    
    def check_quest_availability(self, player_data: dict) -> List[CriminalQuest]:
        """Check which quests player qualifies for"""
        available = []
        for quest in self.available_quests:
            if quest not in self.active_quests and quest not in self.completed_quests:
                # Check if meets requirements
                qualifies = True
                for req_type, req_value in quest.requirements.items():
                    if req_type == 'crimes_committed':
                        if player_data.get('crime_count', 0) < req_value:
                            qualifies = False
                    # Add more requirement checks as needed
                
                if qualifies:
                    available.append(quest)
        
        return available
    
    def complete_quest(self, quest_id: str, player) -> Tuple[bool, dict]:
        """Complete a quest and grant rewards"""
        quest = next((q for q in self.active_quests if q.quest_id == quest_id), None)
        
        if not quest:
            return False, {}
        
        quest.completed = True
        self.active_quests.remove(quest)
        self.completed_quests.append(quest)
        
        logger.info(f"[QUEST] Completed: {quest.name}")
        return True, quest.rewards


# Export main classes
__all__ = [
    'CriminalSkillTree', 'MarketManipulation', 'ScammingSystem',
    'StolenGoodsAppraiser', 'CriminalQuestSystem'
]
