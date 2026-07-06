"""
Economics Skill Tree - Skills for trading, market manipulation, and wealth generation
Unlocks features in commodity exchange, reduces fees, increases profits
"""

import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class EconomicsSkill:
    """Represents a single skill in the economics tree"""
    
    def __init__(self, skill_id: str, name: str, description: str, 
                 max_level: int, cost_per_level: int, prerequisites: List[str] = None):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.max_level = max_level
        self.cost_per_level = cost_per_level
        self.current_level = 0
        self.prerequisites = prerequisites or []
        
        # Skill effects (calculated based on level)
        self.effects = {}
    
    def can_upgrade(self, player_skills: Dict[str, int], player_level: int) -> Tuple[bool, str]:
        """Check if skill can be upgraded"""
        # Check if already maxed
        if self.current_level >= self.max_level:
            return False, f"{self.name} is already maxed"
        
        # Check prerequisites
        for prereq_id in self.prerequisites:
            if player_skills.get(prereq_id, 0) < 1:
                return False, f"Requires {prereq_id} first"
        
        # Check player level requirement (unlock economics at level 10)
        min_level = 10 + (self.current_level * 5)
        if player_level < min_level:
            return False, f"Requires player level {min_level}"
        
        return True, "Can upgrade"
    
    def upgrade(self, player) -> Tuple[bool, str]:
        """Upgrade the skill"""
        can_upgrade, message = self.can_upgrade(
            player.economics_skills if hasattr(player, 'economics_skills') else {},
            player.level
        )
        
        if not can_upgrade:
            return False, message
        
        # Check cost
        cost = self.get_upgrade_cost()
        if player.dubloons < cost:
            return False, f"Need {cost}g ({cost - player.dubloons}g more)"
        
        # Upgrade
        player.dubloons -= cost
        self.current_level += 1
        
        # Update effects
        self._calculate_effects()
        
        logger.info(f"[ECONOMICS] Player upgraded {self.name} to level {self.current_level}")
        return True, f"Upgraded {self.name} to level {self.current_level}!"
    
    def get_upgrade_cost(self) -> int:
        """Get cost to upgrade to next level"""
        return self.cost_per_level * (self.current_level + 1)
    
    def _calculate_effects(self):
        """Calculate skill effects based on current level"""
        # This will be overridden by specific skill types
        pass
    
    def to_dict(self) -> dict:
        return {
            'skill_id': self.skill_id,
            'name': self.name,
            'description': self.description,
            'current_level': self.current_level,
            'max_level': self.max_level,
            'effects': self.effects
        }


class EconomicsSkillTree:
    """Manages the economics skill tree"""
    
    def __init__(self):
        self.skills = {}
        self._initialize_skills()
    
    def _initialize_skills(self):
        """Create all economics skills"""
        
        # TIER 1: Basic Trading (Level 10+)
        self.skills['basic_trader'] = EconomicsSkill(
            'basic_trader',
            'Basic Trader',
            'Reduce transaction fees by 10% per level\nUnlock: Commodity Exchange at level 15',
            max_level=5,
            cost_per_level=100
        )
        
        self.skills['bulk_buyer'] = EconomicsSkill(
            'bulk_buyer',
            'Bulk Buyer',
            'Increase max transaction limit by 10 per level\nBuy larger quantities at once',
            max_level=5,
            cost_per_level=150
        )
        
        self.skills['haggler'] = EconomicsSkill(
            'haggler',
            'Haggler',
            'Get 2% better prices when buying (per level)\nCumulative with market prices',
            max_level=5,
            cost_per_level=200
        )
        
        # TIER 2: Regional Trading (Level 20+)
        self.skills['regional_trader'] = EconomicsSkill(
            'regional_trader',
            'Regional Trader',
            'See prices in nearby towns\nUnlock at level 40 in Commodity Exchange',
            max_level=1,
            cost_per_level=500,
            prerequisites=['basic_trader']
        )
        
        self.skills['caravan_master'] = EconomicsSkill(
            'caravan_master',
            'Caravan Master',
            'Reduce fast travel cost by 15% per level\nIncreased inventory space for trading',
            max_level=3,
            cost_per_level=300,
            prerequisites=['bulk_buyer']
        )
        
        self.skills['price_memory'] = EconomicsSkill(
            'price_memory',
            'Price Memory',
            'Remember prices in towns youve visited\nSee price history for 7 days',
            max_level=1,
            cost_per_level=400,
            prerequisites=['basic_trader']
        )
        
        # TIER 3: Market Analysis (Level 35+)
        self.skills['market_analyst'] = EconomicsSkill(
            'market_analyst',
            'Market Analyst',
            'See supply and demand levels\nUnlock at level 60 in Commodity Exchange',
            max_level=1,
            cost_per_level=1000,
            prerequisites=['regional_trader', 'price_memory']
        )
        
        self.skills['trend_spotter'] = EconomicsSkill(
            'trend_spotter',
            'Trend Spotter',
            'See 7-day price trends\nPredict price movements',
            max_level=1,
            cost_per_level=800,
            prerequisites=['price_memory']
        )
        
        self.skills['supply_predictor'] = EconomicsSkill(
            'supply_predictor',
            'Supply Predictor',
            'See incoming supply from caravans\nPredict shortages 2 days in advance',
            max_level=1,
            cost_per_level=900,
            prerequisites=['market_analyst']
        )
        
        # TIER 4: Advanced Trading (Level 50+)
        self.skills['arbitrage_master'] = EconomicsSkill(
            'arbitrage_master',
            'Arbitrage Master',
            'See all town prices and arbitrage opportunities\nUnlock full Commodity Exchange features',
            max_level=1,
            cost_per_level=2000,
            prerequisites=['market_analyst', 'trend_spotter']
        )
        
        self.skills['market_manipulator'] = EconomicsSkill(
            'market_manipulator',
            'Market Manipulator',
            'Buy/sell large quantities to influence prices\n+5% price impact per level',
            max_level=3,
            cost_per_level=1500,
            prerequisites=['market_analyst']
        )
        
        self.skills['insider_trading'] = EconomicsSkill(
            'insider_trading',
            'Insider Trading',
            'Get newspaper 1 day early\nSee market events before they happen',
            max_level=1,
            cost_per_level=1200,
            prerequisites=['trend_spotter']
        )
        
        # TIER 5: Monopolist (Level 70+)
        self.skills['monopolist'] = EconomicsSkill(
            'monopolist',
            'Monopolist',
            'Control town markets\nSet prices when you own >50% supply',
            max_level=1,
            cost_per_level=5000,
            prerequisites=['arbitrage_master', 'market_manipulator']
        )
        
        self.skills['tax_haven'] = EconomicsSkill(
            'tax_haven',
            'Tax Haven',
            'Reduce all transaction fees by 50%\nPay 25% less to banks',
            max_level=1,
            cost_per_level=3000,
            prerequisites=['arbitrage_master']
        )
        
        self.skills['economic_genius'] = EconomicsSkill(
            'economic_genius',
            'Economic Genius',
            'Double all trading profits\nPerfect market timing',
            max_level=1,
            cost_per_level=10000,
            prerequisites=['monopolist', 'tax_haven']
        )
    
    def get_skill(self, skill_id: str) -> Optional[EconomicsSkill]:
        """Get a specific skill"""
        return self.skills.get(skill_id)
    
    def has_skill(self, player, skill_id: str, min_level: int = 1) -> bool:
        """Check if player has a skill at minimum level"""
        if not hasattr(player, 'economics_skills'):
            return False
        return player.economics_skills.get(skill_id, 0) >= min_level
    
    def get_available_skills(self, player) -> List[EconomicsSkill]:
        """Get skills that can be upgraded"""
        available = []
        player_skills = player.economics_skills if hasattr(player, 'economics_skills') else {}
        
        for skill in self.skills.values():
            # Update current level from player data
            skill.current_level = player_skills.get(skill.skill_id, 0)
            
            can_upgrade, _ = skill.can_upgrade(player_skills, player.level)
            if can_upgrade:
                available.append(skill)
        
        return available
    
    def get_all_skills_by_tier(self) -> Dict[str, List[EconomicsSkill]]:
        """Get skills organized by tier"""
        tiers = {
            'Tier 1: Basic Trading': [],
            'Tier 2: Regional Trading': [],
            'Tier 3: Market Analysis': [],
            'Tier 4: Advanced Trading': [],
            'Tier 5: Master Trader': []
        }
        
        # Tier 1
        tiers['Tier 1: Basic Trading'].extend([
            self.skills['basic_trader'],
            self.skills['bulk_buyer'],
            self.skills['haggler']
        ])
        
        # Tier 2
        tiers['Tier 2: Regional Trading'].extend([
            self.skills['regional_trader'],
            self.skills['caravan_master'],
            self.skills['price_memory']
        ])
        
        # Tier 3
        tiers['Tier 3: Market Analysis'].extend([
            self.skills['market_analyst'],
            self.skills['trend_spotter'],
            self.skills['supply_predictor']
        ])
        
        # Tier 4
        tiers['Tier 4: Advanced Trading'].extend([
            self.skills['arbitrage_master'],
            self.skills['market_manipulator'],
            self.skills['insider_trading']
        ])
        
        # Tier 5
        tiers['Tier 5: Master Trader'].extend([
            self.skills['monopolist'],
            self.skills['tax_haven'],
            self.skills['economic_genius']
        ])
        
        return tiers
    
    def calculate_transaction_fee_reduction(self, player) -> float:
        """Calculate total transaction fee reduction"""
        reduction = 0.0
        
        # Basic trader: 10% per level
        if self.has_skill(player, 'basic_trader'):
            skill = self.get_skill('basic_trader')
            level = player.economics_skills.get('basic_trader', 0)
            reduction += 0.10 * level
        
        # Tax haven: Additional 50%
        if self.has_skill(player, 'tax_haven'):
            reduction += 0.50
        
        return min(reduction, 0.95)  # Max 95% reduction
    
    def calculate_buying_bonus(self, player) -> float:
        """Calculate bonus when buying (reduces prices)"""
        bonus = 0.0
        
        # Haggler: 2% per level
        if self.has_skill(player, 'haggler'):
            level = player.economics_skills.get('haggler', 0)
            bonus += 0.02 * level
        
        return min(bonus, 0.20)  # Max 20% bonus
    
    def calculate_selling_bonus(self, player) -> float:
        """Calculate bonus when selling (increases prices)"""
        bonus = 0.0
        
        # Haggler also helps selling
        if self.has_skill(player, 'haggler'):
            level = player.economics_skills.get('haggler', 0)
            bonus += 0.02 * level
        
        # Economic genius: Double profits
        if self.has_skill(player, 'economic_genius'):
            bonus += 1.0  # 100% bonus = double
        
        return bonus
    
    def calculate_max_transaction_limit(self, player, base_limit: int = 50) -> int:
        """Calculate maximum transaction quantity"""
        limit = base_limit
        
        # Bulk buyer: +10 per level
        if self.has_skill(player, 'bulk_buyer'):
            level = player.economics_skills.get('bulk_buyer', 0)
            limit += 10 * level
        
        return limit
    
    def can_manipulate_market(self, player) -> bool:
        """Check if player can manipulate market prices"""
        return self.has_skill(player, 'market_manipulator')
    
    def get_market_manipulation_power(self, player) -> float:
        """Get market manipulation power (price impact)"""
        if not self.can_manipulate_market(player):
            return 0.0
        
        level = player.economics_skills.get('market_manipulator', 0)
        return 0.05 * level  # 5% per level
    
    def can_see_early_news(self, player) -> bool:
        """Check if player gets newspaper early"""
        return self.has_skill(player, 'insider_trading')
    
    def can_control_market(self, player) -> bool:
        """Check if player can set prices (monopolist)"""
        return self.has_skill(player, 'monopolist')
    
    def get_fast_travel_discount(self, player) -> float:
        """Get fast travel cost reduction"""
        if not self.has_skill(player, 'caravan_master'):
            return 0.0
        
        level = player.economics_skills.get('caravan_master', 0)
        return 0.15 * level  # 15% per level
    
    def get_skill_summary(self, player) -> Dict[str, any]:
        """Get summary of all active bonuses"""
        return {
            'transaction_fee_reduction': self.calculate_transaction_fee_reduction(player),
            'buying_bonus': self.calculate_buying_bonus(player),
            'selling_bonus': self.calculate_selling_bonus(player),
            'max_transaction_limit': self.calculate_max_transaction_limit(player),
            'fast_travel_discount': self.get_fast_travel_discount(player),
            'can_manipulate_market': self.can_manipulate_market(player),
            'market_manipulation_power': self.get_market_manipulation_power(player),
            'can_see_early_news': self.can_see_early_news(player),
            'can_control_market': self.can_control_market(player)
        }
    
    def initialize_player_skills(self, player):
        """Initialize economics skills on player"""
        if not hasattr(player, 'economics_skills'):
            player.economics_skills = {}
            logger.info("[ECONOMICS] Initialized economics skills on player")
    
    def upgrade_skill(self, player, skill_id: str) -> Tuple[bool, str]:
        """Upgrade a skill for the player"""
        self.initialize_player_skills(player)
        
        skill = self.get_skill(skill_id)
        if not skill:
            return False, f"Skill {skill_id} not found"
        
        # Update current level from player data
        skill.current_level = player.economics_skills.get(skill_id, 0)
        
        # Attempt upgrade
        success, message = skill.upgrade(player)
        
        if success:
            # Update player's skill dict
            player.economics_skills[skill_id] = skill.current_level
        
        return success, message
