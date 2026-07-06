"""
Criminal Underworld System
- Crime Syndicates/Guilds (Thieves Guild, Assassins Guild)
- Gang System with Treaties/Alliances
- Criminal Rank Progression
- Protection Racket
- Money Laundering
- Criminal Enterprises (passive income)
- Heist Progression System
- Underworld Favors
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


# ===== CRIME SYNDICATES/GUILDS =====

class CrimeSyndicate:
    """Base class for criminal organizations"""
    
    def __init__(self, name: str, specialty: str, headquarters_town: str):
        self.name = name
        self.specialty = specialty  # 'theft', 'assassination', 'smuggling', 'extortion'
        self.headquarters_town = headquarters_town
        self.members = []
        self.influence = 0  # 0-100 influence in city
        self.treasury = 0
        self.active_operations = []
        self.territories = []  # List of town names under control
        
    def add_member(self, member_name: str, rank: str):
        """Add member to syndicate"""
        self.members.append({'name': member_name, 'rank': rank, 'joined_day': 0})
        logger.info(f"[SYNDICATE] {member_name} joined {self.name} as {rank}")
    
    def increase_influence(self, amount: int):
        """Increase syndicate influence"""
        self.influence = min(100, self.influence + amount)
    
    def collect_tribute(self):
        """Collect tribute from territories"""
        tribute = len(self.territories) * random.randint(50, 150)
        self.treasury += tribute
        return tribute


class ThievesGuild(CrimeSyndicate):
    """Thieves Guild - specializes in theft, burglary, pickpocketing"""
    
    RANKS = [
        {'name': 'Initiate', 'crimes_required': 0, 'perks': []},
        {'name': 'Footpad', 'crimes_required': 5, 'perks': ['fence_discount']},
        {'name': 'Cutpurse', 'crimes_required': 15, 'perks': ['fence_discount', 'lockpick_bonus']},
        {'name': 'Burglar', 'crimes_required': 30, 'perks': ['fence_discount', 'lockpick_bonus', 'stealth_bonus']},
        {'name': 'Cat Burglar', 'crimes_required': 50, 'perks': ['fence_discount', 'lockpick_bonus', 'stealth_bonus', 'alarm_reduction']},
        {'name': 'Master Thief', 'crimes_required': 100, 'perks': ['fence_discount', 'lockpick_bonus', 'stealth_bonus', 'alarm_reduction', 'heist_access']},
        {'name': 'Guild Master', 'crimes_required': 200, 'perks': ['all_perks', 'syndicate_control']}
    ]
    
    def __init__(self, headquarters_town: str = "Port Town"):
        super().__init__("The Shadowhand Guild", "theft", headquarters_town)
        self.contracts = []  # Available theft contracts
        self.fence_network = []  # Connected fences
        
    def get_rank_for_crimes(self, crime_count: int) -> dict:
        """Get appropriate rank based on crime count"""
        for rank in reversed(self.RANKS):
            if crime_count >= rank['crimes_required']:
                return rank
        return self.RANKS[0]
    
    def generate_contract(self, difficulty: str) -> dict:
        """Generate a theft contract"""
        contracts = {
            'easy': [
                {'target': 'Merchant Shop', 'reward': 100, 'item': 'merchant_ledger', 'penalty': 50},
                {'target': 'Tavern Storage', 'reward': 80, 'item': 'wine_barrel', 'penalty': 30},
                {'target': 'Blacksmith', 'reward': 150, 'item': 'steel_ingot', 'penalty': 75}
            ],
            'medium': [
                {'target': 'Bank Deposit Box', 'reward': 300, 'item': 'gold_bars', 'penalty': 150},
                {'target': 'Noble Estate', 'reward': 400, 'item': 'family_jewels', 'penalty': 200},
                {'target': 'Temple Reliquary', 'reward': 350, 'item': 'holy_artifact', 'penalty': 175}
            ],
            'hard': [
                {'target': 'Royal Treasury', 'reward': 1000, 'item': 'crown_jewels', 'penalty': 500},
                {'target': 'Mage Tower', 'reward': 800, 'item': 'arcane_grimoire', 'penalty': 400},
                {'target': 'Guild Vault', 'reward': 900, 'item': 'master_records', 'penalty': 450}
            ]
        }
        return random.choice(contracts.get(difficulty, contracts['easy']))


class AssassinsGuild(CrimeSyndicate):
    """Assassins Guild - specializes in contracts, poisons, stealth kills"""
    
    RANKS = [
        {'name': 'Recruit', 'kills_required': 0, 'perks': []},
        {'name': 'Blade', 'kills_required': 3, 'perks': ['poison_access']},
        {'name': 'Shadow', 'kills_required': 10, 'perks': ['poison_access', 'stealth_kill']},
        {'name': 'Silencer', 'kills_required': 25, 'perks': ['poison_access', 'stealth_kill', 'clean_kills']},
        {'name': 'Master Assassin', 'kills_required': 50, 'perks': ['poison_access', 'stealth_kill', 'clean_kills', 'legendary_targets']},
        {'name': 'Guildmaster', 'kills_required': 100, 'perks': ['all_perks', 'syndicate_control']}
    ]
    
    def __init__(self, headquarters_town: str = "Shadow City"):
        super().__init__("The Silent Hand", "assassination", headquarters_town)
        self.contracts = []
        self.poison_recipes = []
        
    def get_rank_for_kills(self, kill_count: int) -> dict:
        """Get appropriate rank based on kill count"""
        for rank in reversed(self.RANKS):
            if kill_count >= rank['kills_required']:
                return rank
        return self.RANKS[0]
    
    def generate_contract(self, difficulty: str) -> dict:
        """Generate an assassination contract"""
        contracts = {
            'easy': [
                {'target': 'Corrupt Guard', 'reward': 200, 'witnesses_allowed': True, 'penalty': 100},
                {'target': 'Rival Merchant', 'reward': 250, 'witnesses_allowed': True, 'penalty': 125},
                {'target': 'Gang Member', 'reward': 150, 'witnesses_allowed': True, 'penalty': 75}
            ],
            'medium': [
                {'target': 'Noble', 'reward': 500, 'witnesses_allowed': False, 'penalty': 300},
                {'target': 'Guild Master', 'reward': 600, 'witnesses_allowed': False, 'penalty': 350},
                {'target': 'Corrupt Official', 'reward': 550, 'witnesses_allowed': False, 'penalty': 325}
            ],
            'hard': [
                {'target': 'Royal Advisor', 'reward': 1500, 'witnesses_allowed': False, 'penalty': 1000},
                {'target': 'Crime Lord', 'reward': 1200, 'witnesses_allowed': False, 'penalty': 800},
                {'target': 'Archmage', 'reward': 1800, 'witnesses_allowed': False, 'penalty': 1200}
            ]
        }
        return random.choice(contracts.get(difficulty, contracts['easy']))


# ===== GANG SYSTEM =====

class Gang:
    """Street gang/criminal organization"""
    
    def __init__(self, name: str, territory: str, specialty: str):
        self.name = name
        self.territory = territory
        self.specialty = specialty  # 'protection', 'smuggling', 'drugs', 'weapons'
        self.strength = random.randint(20, 60)
        self.reputation = 0
        self.allies = []
        self.enemies = []
        self.controlled_businesses = []
        self.income_per_day = 0
        
    def add_ally(self, gang_name: str):
        """Form alliance with another gang"""
        if gang_name not in self.allies and gang_name != self.name:
            self.allies.append(gang_name)
            if gang_name in self.enemies:
                self.enemies.remove(gang_name)
            logger.info(f"[GANG] {self.name} allied with {gang_name}")
    
    def add_enemy(self, gang_name: str):
        """Declare war on another gang"""
        if gang_name not in self.enemies and gang_name != self.name:
            self.enemies.append(gang_name)
            if gang_name in self.allies:
                self.allies.remove(gang_name)
            logger.info(f"[GANG] {self.name} now hostile to {gang_name}")
    
    def control_business(self, business_name: str, income: int):
        """Take control of a business"""
        self.controlled_businesses.append({'name': business_name, 'income': income})
        self.income_per_day += income
        logger.info(f"[GANG] {self.name} controls {business_name} (+{income}g/day)")


class GangManager:
    """Manages all gangs and gang interactions"""
    
    def __init__(self):
        self.gangs = {}  # {town: [Gang]}
        self.treaties = []  # [(gang1, gang2, treaty_type)]
        self.gang_wars = []  # [(gang1, gang2, start_day)]
        
    def create_gang(self, name: str, territory: str, specialty: str) -> Gang:
        """Create a new gang"""
        gang = Gang(name, territory, specialty)
        if territory not in self.gangs:
            self.gangs[territory] = []
        self.gangs[territory].append(gang)
        return gang
    
    def initialize_default_gangs(self):
        """Create default gangs for major cities"""
        gangs_data = [
            ("The Iron Fists", "Port Town", "protection"),
            ("Crimson Blades", "Port Town", "smuggling"),
            ("The Syndicate", "Capital City", "drugs"),
            ("Black Market Crew", "Capital City", "weapons"),
            ("The Dockworkers", "Harbor District", "smuggling"),
            ("Poison Ring", "Shadow District", "assassination"),
        ]
        
        for name, territory, specialty in gangs_data:
            self.create_gang(name, territory, specialty)
    
    def form_treaty(self, gang1_name: str, gang2_name: str, treaty_type: str):
        """Form treaty between two gangs"""
        self.treaties.append((gang1_name, gang2_name, treaty_type))
        logger.info(f"[GANG] Treaty formed: {gang1_name} <-> {gang2_name} ({treaty_type})")
    
    def start_gang_war(self, gang1_name: str, gang2_name: str, current_day: int):
        """Start a gang war"""
        self.gang_wars.append((gang1_name, gang2_name, current_day))
        logger.info(f"[GANG] War started: {gang1_name} vs {gang2_name}")
    
    def get_gangs_in_territory(self, territory: str) -> List[Gang]:
        """Get all gangs in a territory"""
        return self.gangs.get(territory, [])
    
    def get_player_gang_standing(self, player_crimes: int, player_reputation: int) -> str:
        """Determine player's standing with gangs"""
        if player_crimes >= 50 and player_reputation >= 100:
            return "Respected"
        elif player_crimes >= 20:
            return "Known"
        elif player_crimes >= 5:
            return "Noticed"
        else:
            return "Unknown"


# ===== CRIMINAL RANK PROGRESSION =====

class CriminalRankSystem:
    """Tracks player's criminal reputation and rank"""
    
    RANKS = [
        {'name': 'Civilian', 'crimes': 0, 'perks': [], 'title': 'Law-Abiding Citizen'},
        {'name': 'Petty Criminal', 'crimes': 5, 'perks': ['fence_access'], 'title': 'Troublemaker'},
        {'name': 'Thug', 'crimes': 15, 'perks': ['fence_access', 'gang_contact'], 'title': 'Street Tough'},
        {'name': 'Enforcer', 'crimes': 30, 'perks': ['fence_access', 'gang_contact', 'protection_racket'], 'title': 'Made Man'},
        {'name': 'Criminal', 'crimes': 50, 'perks': ['fence_access', 'gang_contact', 'protection_racket', 'laundering'], 'title': 'Professional Criminal'},
        {'name': 'Crime Boss', 'crimes': 100, 'perks': ['fence_access', 'gang_contact', 'protection_racket', 'laundering', 'enterprises'], 'title': 'Boss'},
        {'name': 'Kingpin', 'crimes': 200, 'perks': ['all_perks'], 'title': 'Underworld Kingpin'}
    ]
    
    def __init__(self):
        self.crime_count = 0
        self.notoriety = 0  # Public awareness of criminal status
        self.underworld_rep = 0  # Respect in criminal circles
        self.heat = 0  # Current law enforcement pressure (0-100)
        self.criminal_contacts = []
        self.aliases = []  # Fake identities
        
    def add_crime(self, crime_type: str, value: int = 1):
        """Record a crime"""
        self.crime_count += value
        
        # Different crimes affect notoriety/rep differently
        crime_effects = {
            'theft': {'notoriety': 1, 'rep': 2, 'heat': 5},
            'burglary': {'notoriety': 3, 'rep': 5, 'heat': 10},
            'assault': {'notoriety': 5, 'rep': 3, 'heat': 15},
            'murder': {'notoriety': 10, 'rep': 8, 'heat': 30},
            'heist': {'notoriety': 8, 'rep': 15, 'heat': 25},
        }
        
        effects = crime_effects.get(crime_type, {'notoriety': 2, 'rep': 2, 'heat': 5})
        self.notoriety += effects['notoriety']
        self.underworld_rep += effects['rep']
        self.heat += effects['heat']
        
        logger.info(f"[CRIME] {crime_type} recorded. Total crimes: {self.crime_count}")
    
    def get_current_rank(self) -> dict:
        """Get player's current criminal rank"""
        for rank in reversed(self.RANKS):
            if self.crime_count >= rank['crimes']:
                return rank
        return self.RANKS[0]
    
    def reduce_heat(self, amount: int):
        """Reduce heat through bribes, time, or other means"""
        self.heat = max(0, self.heat - amount)
    
    def create_alias(self, alias_name: str, cost: int) -> bool:
        """Create a fake identity"""
        if alias_name not in self.aliases:
            self.aliases.append(alias_name)
            logger.info(f"[CRIMINAL] New alias created: {alias_name}")
            return True
        return False


# ===== PROTECTION RACKET =====

class ProtectionRacket:
    """Protection racket system"""
    
    def __init__(self):
        self.protected_businesses = {}  # {business_id: ProtectionContract}
        self.collection_day = 0
        
    def start_protection(self, business_id: str, business_name: str, 
                        weekly_payment: int, current_day: int) -> bool:
        """Start protecting a business"""
        if business_id in self.protected_businesses:
            return False
        
        self.protected_businesses[business_id] = {
            'name': business_name,
            'weekly_payment': weekly_payment,
            'start_day': current_day,
            'last_collection': current_day,
            'missed_payments': 0,
            'satisfied': True
        }
        logger.info(f"[PROTECTION] Now protecting {business_name} for {weekly_payment}g/week")
        return True
    
    def collect_payment(self, business_id: str, current_day: int) -> Tuple[int, str]:
        """Collect protection money"""
        if business_id not in self.protected_businesses:
            return 0, "Business not under protection"
        
        contract = self.protected_businesses[business_id]
        days_since = current_day - contract['last_collection']
        
        if days_since < 7:
            return 0, f"Too soon. Come back in {7 - days_since} days"
        
        # Calculate payment
        weeks_passed = days_since // 7
        payment = contract['weekly_payment'] * weeks_passed
        
        # Update contract
        contract['last_collection'] = current_day
        contract['missed_payments'] = 0
        contract['satisfied'] = True
        
        logger.info(f"[PROTECTION] Collected {payment}g from {contract['name']}")
        return payment, f"Collected {payment}g"
    
    def check_missed_payments(self, current_day: int) -> List[dict]:
        """Check for businesses with missed payments"""
        missed = []
        for business_id, contract in self.protected_businesses.items():
            days_since = current_day - contract['last_collection']
            if days_since >= 14:  # 2 weeks late
                contract['missed_payments'] += 1
                contract['satisfied'] = False
                missed.append({
                    'id': business_id,
                    'name': contract['name'],
                    'owed': contract['weekly_payment'] * (days_since // 7)
                })
        return missed
    
    def intimidate_business(self, business_id: str) -> str:
        """Intimidate a business to keep paying"""
        if business_id not in self.protected_businesses:
            return "Business not under protection"
        
        contract = self.protected_businesses[business_id]
        contract['satisfied'] = True
        contract['missed_payments'] = 0
        
        return f"{contract['name']} has been... persuaded to pay on time"


# ===== MONEY LAUNDERING =====

class MoneyLaundering:
    """Money laundering system to convert dirty money to clean"""
    
    LAUNDERING_METHODS = {
        'tavern': {'rate': 0.75, 'capacity': 500, 'time_days': 3, 'suspicion': 5},
        'shop': {'rate': 0.80, 'capacity': 1000, 'time_days': 5, 'suspicion': 8},
        'trade_company': {'rate': 0.85, 'capacity': 5000, 'time_days': 7, 'suspicion': 3},
        'casino': {'rate': 0.70, 'capacity': 10000, 'time_days': 1, 'suspicion': 15},
        'real_estate': {'rate': 0.90, 'capacity': 50000, 'time_days': 14, 'suspicion': 2},
    }
    
    def __init__(self):
        self.dirty_money = 0
        self.clean_money = 0
        self.active_operations = []  # [(method, amount, start_day, end_day)]
        self.suspicion_level = 0  # 0-100
        
    def add_dirty_money(self, amount: int):
        """Add dirty money from crimes"""
        self.dirty_money += amount
        logger.info(f"[LAUNDERING] Added {amount}g dirty money. Total: {self.dirty_money}g")
    
    def start_laundering(self, method: str, amount: int, current_day: int) -> Tuple[bool, str]:
        """Start a laundering operation"""
        if method not in self.LAUNDERING_METHODS:
            return False, "Invalid method"
        
        method_data = self.LAUNDERING_METHODS[method]
        
        if amount > method_data['capacity']:
            return False, f"Amount exceeds capacity ({method_data['capacity']}g)"
        
        if amount > self.dirty_money:
            return False, "Insufficient dirty money"
        
        # Deduct dirty money
        self.dirty_money -= amount
        
        # Start operation
        end_day = current_day + method_data['time_days']
        clean_amount = int(amount * method_data['rate'])
        
        self.active_operations.append({
            'method': method,
            'dirty_amount': amount,
            'clean_amount': clean_amount,
            'start_day': current_day,
            'end_day': end_day
        })
        
        # Increase suspicion
        self.suspicion_level = min(100, self.suspicion_level + method_data['suspicion'])
        
        logger.info(f"[LAUNDERING] Started {method} operation: {amount}g -> {clean_amount}g in {method_data['time_days']} days")
        return True, f"Laundering {amount}g through {method}"
    
    def update(self, current_day: int) -> List[dict]:
        """Update laundering operations and return completed ones"""
        completed = []
        remaining = []
        
        for op in self.active_operations:
            if current_day >= op['end_day']:
                # Operation complete
                self.clean_money += op['clean_amount']
                completed.append(op)
                logger.info(f"[LAUNDERING] Completed: {op['clean_amount']}g clean money")
            else:
                remaining.append(op)
        
        self.active_operations = remaining
        
        # Slowly reduce suspicion over time
        if not self.active_operations:
            self.suspicion_level = max(0, self.suspicion_level - 1)
        
        return completed
    
    def get_suspicion_status(self) -> str:
        """Get current suspicion status"""
        if self.suspicion_level < 20:
            return "Clear"
        elif self.suspicion_level < 50:
            return "Monitored"
        elif self.suspicion_level < 80:
            return "Under Investigation"
        else:
            return "Hot - Lay Low!"


# ===== CRIMINAL ENTERPRISES =====

class CriminalEnterprise:
    """Passive income criminal business"""
    
    def __init__(self, name: str, enterprise_type: str, income_per_day: int, 
                 upkeep_cost: int, heat_generation: int):
        self.name = name
        self.type = enterprise_type  # 'brothel', 'gambling_den', 'smuggling_ring', 'chop_shop', 'counterfeit_mint'
        self.income_per_day = income_per_day
        self.upkeep_cost = upkeep_cost
        self.heat_generation = heat_generation
        self.active = True
        self.days_operated = 0
        self.total_profit = 0
        self.busted_risk = 0  # 0-100 chance of getting busted
        
    def operate_day(self) -> int:
        """Run enterprise for one day, return profit"""
        if not self.active:
            return 0
        
        profit = self.income_per_day - self.upkeep_cost
        self.total_profit += profit
        self.days_operated += 1
        
        # Increase bust risk slightly each day
        self.busted_risk = min(100, self.busted_risk + 0.5)
        
        return profit
    
    def reduce_heat(self, amount: int):
        """Pay bribes or lay low to reduce heat"""
        self.busted_risk = max(0, self.busted_risk - amount)
    
    def shutdown(self):
        """Temporarily shut down to avoid bust"""
        self.active = False
        self.busted_risk = max(0, self.busted_risk - 20)
    
    def reopen(self):
        """Reopen enterprise"""
        self.active = True


class EnterpriseManager:
    """Manages criminal enterprises"""
    
    ENTERPRISE_TYPES = {
        'brothel': {'cost': 5000, 'income': 100, 'upkeep': 30, 'heat': 5},
        'gambling_den': {'cost': 3000, 'income': 80, 'upkeep': 20, 'heat': 8},
        'smuggling_ring': {'cost': 10000, 'income': 200, 'upkeep': 50, 'heat': 15},
        'chop_shop': {'cost': 8000, 'income': 150, 'upkeep': 40, 'heat': 12},
        'counterfeit_mint': {'cost': 15000, 'income': 300, 'upkeep': 80, 'heat': 25},
        'drug_lab': {'cost': 12000, 'income': 250, 'upkeep': 60, 'heat': 20},
    }
    
    def __init__(self):
        self.enterprises = []
        
    def purchase_enterprise(self, enterprise_type: str, name: str, player_gold: int) -> Tuple[bool, str, int]:
        """Purchase a new enterprise"""
        if enterprise_type not in self.ENTERPRISE_TYPES:
            return False, "Invalid enterprise type", 0
        
        data = self.ENTERPRISE_TYPES[enterprise_type]
        cost = data['cost']
        
        if player_gold < cost:
            return False, f"Need {cost}g to purchase", 0
        
        enterprise = CriminalEnterprise(
            name,
            enterprise_type,
            data['income'],
            data['upkeep'],
            data['heat']
        )
        
        self.enterprises.append(enterprise)
        logger.info(f"[ENTERPRISE] Purchased {name} ({enterprise_type}) for {cost}g")
        return True, f"Purchased {name}", cost
    
    def run_daily_operations(self) -> int:
        """Run all enterprises for one day"""
        total_profit = 0
        for enterprise in self.enterprises:
            profit = enterprise.operate_day()
            total_profit += profit
        
        return total_profit
    
    def get_total_heat(self) -> int:
        """Calculate total heat from all enterprises"""
        return sum(e.heat_generation for e in self.enterprises if e.active)
    
    def get_enterprises_at_risk(self) -> List[CriminalEnterprise]:
        """Get enterprises with high bust risk"""
        return [e for e in self.enterprises if e.busted_risk > 70]


# ===== HEIST SYSTEM =====

class HeistStage:
    """A stage in a multi-stage heist"""
    
    def __init__(self, name: str, description: str, skill_check: dict, 
                 failure_consequence: str):
        self.name = name
        self.description = description
        self.skill_check = skill_check  # {'skill': str, 'difficulty': int}
        self.failure_consequence = failure_consequence
        self.completed = False
    
    def attempt(self, player_skill: int) -> Tuple[bool, str]:
        """Attempt this stage"""
        required = self.skill_check['difficulty']
        
        # Add some randomness
        roll = random.randint(1, 20) + player_skill
        success = roll >= required
        
        if success:
            self.completed = True
            return True, f"Success! {self.description} completed"
        else:
            return False, self.failure_consequence


class Heist:
    """Multi-stage heist"""
    
    def __init__(self, name: str, target: str, stages: List[HeistStage], 
                 reward: int, heat_cost: int):
        self.name = name
        self.target = target
        self.stages = stages
        self.reward = reward
        self.heat_cost = heat_cost
        self.current_stage = 0
        self.completed = False
        self.failed = False
        self.crew = []  # List of crew members
        
    def add_crew_member(self, name: str, specialty: str, bonus: int):
        """Add crew member to heist"""
        self.crew.append({'name': name, 'specialty': specialty, 'bonus': bonus})
    
    def attempt_current_stage(self, player_skill: int) -> Tuple[bool, str, bool]:
        """
        Attempt current stage
        Returns (success, message, heist_complete)
        """
        if self.completed or self.failed:
            return False, "Heist already finished", False
        
        if self.current_stage >= len(self.stages):
            return False, "No more stages", False
        
        stage = self.stages[self.current_stage]
        
        # Apply crew bonuses
        crew_bonus = sum(c['bonus'] for c in self.crew if c['specialty'] == stage.skill_check['skill'])
        
        success, message = stage.attempt(player_skill + crew_bonus)
        
        if success:
            self.current_stage += 1
            if self.current_stage >= len(self.stages):
                self.completed = True
                return True, f"HEIST COMPLETE! {message}", True
            else:
                return True, message, False
        else:
            self.failed = True
            return False, f"HEIST FAILED! {message}", False
    
    def get_progress(self) -> str:
        """Get heist progress"""
        return f"Stage {self.current_stage + 1}/{len(self.stages)}"


class HeistManager:
    """Manages heists"""
    
    def __init__(self):
        self.available_heists = []
        self.active_heist = None
        self.completed_heists = []
        
    def generate_heist(self, difficulty: str) -> Heist:
        """Generate a heist based on difficulty"""
        if difficulty == 'easy':
            stages = [
                HeistStage("Case the Joint", "Scout the target", 
                          {'skill': 'observation', 'difficulty': 15}, "Guards spotted you!"),
                HeistStage("Infiltration", "Sneak inside", 
                          {'skill': 'stealth', 'difficulty': 20}, "Alarm triggered!"),
                HeistStage("The Score", "Grab the loot", 
                          {'skill': 'lockpicking', 'difficulty': 25}, "Vault too difficult!"),
                HeistStage("Escape", "Get away clean", 
                          {'skill': 'agility', 'difficulty': 20}, "Guards caught you!")
            ]
            return Heist("Small Bank Job", "Community Bank", stages, 1000, 30)
            
        elif difficulty == 'medium':
            stages = [
                HeistStage("Gather Intel", "Research target security", 
                          {'skill': 'intelligence', 'difficulty': 25}, "Incomplete intel!"),
                HeistStage("Disable Security", "Hack or disable alarms", 
                          {'skill': 'technical', 'difficulty': 30}, "Alarms active!"),
                HeistStage("Infiltration", "Enter without detection", 
                          {'skill': 'stealth', 'difficulty': 35}, "Guards alerted!"),
                HeistStage("Vault Access", "Crack the vault", 
                          {'skill': 'lockpicking', 'difficulty': 40}, "Lockdown initiated!"),
                HeistStage("The Heist", "Secure the goods", 
                          {'skill': 'strength', 'difficulty': 30}, "Too much to carry!"),
                HeistStage("Exfiltration", "Escape to safehouse", 
                          {'skill': 'driving', 'difficulty': 35}, "Chase initiated!")
            ]
            return Heist("Diamond Exchange Robbery", "Diamond Exchange", stages, 5000, 60)
            
        else:  # hard
            stages = [
                HeistStage("Recruitment", "Assemble elite crew", 
                          {'skill': 'charisma', 'difficulty': 40}, "Can't find skilled crew!"),
                HeistStage("Planning", "Detailed blueprint study", 
                          {'skill': 'intelligence', 'difficulty': 45}, "Floor plans outdated!"),
                HeistStage("Inside Man", "Plant insider or mole", 
                          {'skill': 'deception', 'difficulty': 50}, "Insider exposed!"),
                HeistStage("Equipment", "Acquire specialized tools", 
                          {'skill': 'resources', 'difficulty': 40}, "Equipment malfunction!"),
                HeistStage("Infiltration", "Bypass maximum security", 
                          {'skill': 'stealth', 'difficulty': 55}, "Detected by security!"),
                HeistStage("Vault Breach", "Crack legendary vault", 
                          {'skill': 'lockpicking', 'difficulty': 60}, "Vault impenetrable!"),
                HeistStage("The Score", "Secure the treasure", 
                          {'skill': 'coordination', 'difficulty': 50}, "Guards responding!"),
                HeistStage("Extraction", "Escape master plan", 
                          {'skill': 'planning', 'difficulty': 55}, "Surrounded!")
            ]
            return Heist("Royal Treasury Heist", "Royal Treasury", stages, 25000, 100)
    
    def start_heist(self, heist: Heist) -> bool:
        """Start a heist"""
        if self.active_heist:
            return False
        self.active_heist = heist
        self.available_heists.remove(heist)
        logger.info(f"[HEIST] Started: {heist.name}")
        return True
    
    def complete_current_heist(self, success: bool):
        """Complete current heist"""
        if self.active_heist:
            if success:
                self.completed_heists.append(self.active_heist)
            self.active_heist = None


# ===== UNDERWORLD FAVORS =====

class UnderworldFavor:
    """Favor token system"""
    
    def __init__(self, owed_by: str, favor_type: str, value: int):
        self.owed_by = owed_by
        self.favor_type = favor_type  # 'minor', 'major', 'life_debt'
        self.value = value
        self.used = False
        
    def redeem(self) -> str:
        """Redeem this favor"""
        if self.used:
            return "Favor already used"
        self.used = True
        return f"{self.owed_by} owes you a {self.favor_type} favor"


class FavorSystem:
    """Manages underworld favors"""
    
    def __init__(self):
        self.favors_owed_to_player = []
        self.favors_player_owes = []
        
    def earn_favor(self, owed_by: str, favor_type: str):
        """Earn a favor"""
        values = {'minor': 1, 'major': 3, 'life_debt': 10}
        value = values.get(favor_type, 1)
        
        favor = UnderworldFavor(owed_by, favor_type, value)
        self.favors_owed_to_player.append(favor)
        logger.info(f"[FAVOR] {owed_by} now owes you a {favor_type} favor")
    
    def owe_favor(self, owed_to: str, favor_type: str):
        """Player owes a favor"""
        values = {'minor': 1, 'major': 3, 'life_debt': 10}
        value = values.get(favor_type, 1)
        
        favor = UnderworldFavor(owed_to, favor_type, value)
        self.favors_player_owes.append(favor)
        logger.info(f"[FAVOR] You now owe {owed_to} a {favor_type} favor")
    
    def redeem_favor(self, owed_by: str, service: str) -> Tuple[bool, str]:
        """Redeem a favor for a service"""
        available = [f for f in self.favors_owed_to_player if not f.used and f.owed_by == owed_by]
        
        if not available:
            return False, f"No favors owed by {owed_by}"
        
        # Use the smallest favor that covers the service
        favor = available[0]
        message = favor.redeem()
        
        return True, f"Redeemed favor: {message} for {service}"
    
    def get_favor_count(self) -> Tuple[int, int]:
        """Get count of favors (owed_to_player, player_owes)"""
        owed_to = len([f for f in self.favors_owed_to_player if not f.used])
        player_owes = len([f for f in self.favors_player_owes if not f.used])
        return owed_to, player_owes


# To be continued in next file due to length...
