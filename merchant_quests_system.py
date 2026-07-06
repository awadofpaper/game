"""
Merchant Quests and Loyalty Programs
Delivery missions, gathering requests, repeat customer rewards, VIP memberships
"""

import logging
import random
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MerchantQuest:
    """A quest given by a merchant"""
    
    QUEST_TYPES = ['delivery', 'gathering', 'protection', 'retrieval']
    
    def __init__(self, quest_id: str, merchant_id: str, merchant_name: str, quest_type: str):
        self.quest_id = quest_id
        self.merchant_id = merchant_id
        self.merchant_name = merchant_name
        self.quest_type = quest_type
        
        # Quest details
        self.description = ""
        self.objectives: Dict[str, int] = {}  # item_id -> quantity needed
        self.current_progress: Dict[str, int] = {}  # item_id -> quantity delivered
        self.reward_gold = 0
        self.reward_items = []
        self.reputation_reward = 0
        
        # Status
        self.is_active = True
        self.is_completed = False
        self.deadline_day = 0  # Day quest expires
        
        # Generation
        self._generate_quest()
    
    def _generate_quest(self):
        """Generate quest details based on type"""
        if self.quest_type == 'delivery':
            # Deliver items to another town
            self.description = f"Deliver goods to a distant town for {self.merchant_name}"
            item_types = ['sword', 'potion', 'wood', 'iron']
            item = random.choice(item_types)
            quantity = random.randint(5, 15)
            self.objectives[item] = quantity
            self.current_progress[item] = 0
            self.reward_gold = quantity * 50
            self.reputation_reward = 25
            self.deadline_day = 14
            
        elif self.quest_type == 'gathering':
            # Gather materials from the wild
            self.description = f"Gather materials for {self.merchant_name}'s shop"
            materials = ['wood', 'iron', 'herbs', 'leather']
            num_materials = random.randint(1, 3)
            for _ in range(num_materials):
                material = random.choice(materials)
                quantity = random.randint(10, 30)
                self.objectives[material] = quantity
                self.current_progress[material] = 0
            self.reward_gold = sum(self.objectives.values()) * 20
            self.reputation_reward = 30
            self.deadline_day = 21
            
        elif self.quest_type == 'protection':
            # Protect merchant's shipment
            self.description = f"Escort {self.merchant_name}'s caravan to safety"
            self.reward_gold = random.randint(500, 1000)
            self.reputation_reward = 50
            self.deadline_day = 7
            
        elif self.quest_type == 'retrieval':
            # Retrieve stolen goods
            self.description = f"Recover stolen merchandise for {self.merchant_name}"
            self.objectives['stolen_goods'] = 1
            self.current_progress['stolen_goods'] = 0
            self.reward_gold = random.randint(300, 800)
            self.reputation_reward = 40
            self.deadline_day = 10
    
    def update_progress(self, item_id: str, quantity: int) -> bool:
        """Update quest progress"""
        if item_id not in self.objectives:
            return False
        
        self.current_progress[item_id] = min(
            self.current_progress[item_id] + quantity,
            self.objectives[item_id]
        )
        
        # Check if completed
        if self.check_completion():
            self.is_completed = True
            logger.info(f"[QUEST] Completed quest {self.quest_id}")
        
        return True
    
    def check_completion(self) -> bool:
        """Check if all objectives are met"""
        for item_id, needed in self.objectives.items():
            if self.current_progress.get(item_id, 0) < needed:
                return False
        return True
    
    def get_progress_text(self) -> str:
        """Get progress description"""
        if not self.objectives:
            return "Complete the escort mission"
        
        lines = []
        for item_id, needed in self.objectives.items():
            current = self.current_progress.get(item_id, 0)
            lines.append(f"  {item_id}: {current}/{needed}")
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Serialize"""
        return {
            'quest_id': self.quest_id,
            'merchant_id': self.merchant_id,
            'merchant_name': self.merchant_name,
            'quest_type': self.quest_type,
            'objectives': self.objectives,
            'current_progress': self.current_progress,
            'reward_gold': self.reward_gold,
            'reputation_reward': self.reputation_reward,
            'is_active': self.is_active,
            'is_completed': self.is_completed,
            'deadline_day': self.deadline_day
        }


class LoyaltyProgram:
    """Merchant loyalty program with tiers and rewards"""
    
    TIERS = [
        {'name': 'Regular', 'min_purchases': 0, 'discount': 0.0, 'perks': []},
        {'name': 'Bronze Member', 'min_purchases': 10, 'discount': 0.05, 'perks': ['Free appraisal']},
        {'name': 'Silver Member', 'min_purchases': 25, 'discount': 0.10, 'perks': ['Priority restocking', 'Free appraisal']},
        {'name': 'Gold Member', 'min_purchases': 50, 'discount': 0.15, 'perks': ['Exclusive items', 'Priority restocking', 'Free appraisal']},
        {'name': 'VIP', 'min_purchases': 100, 'discount': 0.20, 'perks': ['Exclusive items', 'Priority restocking', 'Free appraisal', 'Free delivery']},
    ]
    
    def __init__(self, merchant_id: str):
        self.merchant_id = merchant_id
        self.purchase_count = 0
        self.total_spent = 0
        self.points = 0  # Loyalty points
        
    def get_tier(self) -> dict:
        """Get current loyalty tier"""
        current_tier = self.TIERS[0]
        for tier in self.TIERS:
            if self.purchase_count >= tier['min_purchases']:
                current_tier = tier
        return current_tier
    
    def record_purchase(self, gold_spent: int):
        """Record a purchase"""
        self.purchase_count += 1
        self.total_spent += gold_spent
        self.points += gold_spent // 10  # 1 point per 10g spent
        
        # Check for tier upgrade
        old_tier = self.get_tier()
        # Recalculate would happen in get_tier()
        new_tier = self.get_tier()
        
        if old_tier['name'] != new_tier['name']:
            logger.info(f"[LOYALTY] Advanced to {new_tier['name']} tier at merchant {self.merchant_id}")
    
    def get_discount(self) -> float:
        """Get loyalty discount"""
        return self.get_tier()['discount']
    
    def has_perk(self, perk: str) -> bool:
        """Check if has a specific perk"""
        return perk in self.get_tier()['perks']
    
    def redeem_points(self, points: int) -> int:
        """Redeem points for gold (100 points = 10g)"""
        if self.points < points:
            return 0
        
        self.points -= points
        return points // 10
    
    def to_dict(self) -> dict:
        """Serialize"""
        return {
            'merchant_id': self.merchant_id,
            'purchase_count': self.purchase_count,
            'total_spent': self.total_spent,
            'points': self.points
        }


class MerchantQuestManager:
    """Manages merchant quests and loyalty programs"""
    
    def __init__(self):
        self.active_quests: Dict[str, MerchantQuest] = {}
        self.completed_quests: List[str] = []
        self.loyalty_programs: Dict[str, LoyaltyProgram] = {}  # merchant_id -> program
        self.next_quest_id = 1
        
    def create_quest(self, merchant_id: str, merchant_name: str, 
                    quest_type: str = None) -> MerchantQuest:
        """Create a new merchant quest"""
        if not quest_type:
            quest_type = random.choice(MerchantQuest.QUEST_TYPES)
        
        quest_id = f"QUEST_{self.next_quest_id}"
        self.next_quest_id += 1
        
        quest = MerchantQuest(quest_id, merchant_id, merchant_name, quest_type)
        self.active_quests[quest_id] = quest
        
        logger.info(f"[QUEST] Created {quest_type} quest for {merchant_name}")
        return quest
    
    def complete_quest(self, quest_id: str, player, reputation_manager) -> Tuple[bool, str]:
        """Complete a quest and give rewards"""
        if quest_id not in self.active_quests:
            return False, "Quest not found"
        
        quest = self.active_quests[quest_id]
        
        if not quest.check_completion():
            return False, "Quest objectives not complete"
        
        # Give rewards
        player.dubloons += quest.reward_gold
        
        # Give reputation
        if reputation_manager:
            rep = reputation_manager.get_reputation(quest.merchant_id)
            if rep:
                rep.modify_reputation(quest.reputation_reward, "quest completion")
        
        # Move to completed
        self.completed_quests.append(quest_id)
        del self.active_quests[quest_id]
        
        message = f"Quest completed! Earned {quest.reward_gold}g and {quest.reputation_reward} reputation"
        logger.info(f"[QUEST] {message}")
        
        return True, message
    
    def get_or_create_loyalty_program(self, merchant_id: str) -> LoyaltyProgram:
        """Get or create loyalty program for merchant"""
        if merchant_id not in self.loyalty_programs:
            self.loyalty_programs[merchant_id] = LoyaltyProgram(merchant_id)
        return self.loyalty_programs[merchant_id]
    
    def record_purchase(self, merchant_id: str, gold_spent: int):
        """Record a purchase for loyalty program"""
        program = self.get_or_create_loyalty_program(merchant_id)
        program.record_purchase(gold_spent)
    
    def get_loyalty_discount(self, merchant_id: str) -> float:
        """Get loyalty discount for merchant"""
        if merchant_id not in self.loyalty_programs:
            return 0.0
        return self.loyalty_programs[merchant_id].get_discount()
    
    def update(self, current_day: int):
        """Update quests (check deadlines)"""
        expired = []
        for quest_id, quest in self.active_quests.items():
            if current_day >= quest.deadline_day:
                quest.is_active = False
                expired.append(quest_id)
                logger.info(f"[QUEST] Quest {quest_id} expired")
        
        for quest_id in expired:
            del self.active_quests[quest_id]
    
    def generate_daily_quests(self, merchants: List[Tuple[str, str]]):
        """Generate new quests from merchants (call daily)"""
        # 20% chance per merchant to offer a quest
        for merchant_id, merchant_name in merchants:
            if random.random() < 0.2:
                # Don't spam quests from same merchant
                active_from_merchant = sum(1 for q in self.active_quests.values() 
                                          if q.merchant_id == merchant_id)
                if active_from_merchant < 2:
                    self.create_quest(merchant_id, merchant_name)
    
    def get_quests_for_merchant(self, merchant_id: str) -> List[MerchantQuest]:
        """Get active quests from a merchant"""
        return [q for q in self.active_quests.values() if q.merchant_id == merchant_id]
    
    def to_dict(self) -> dict:
        """Serialize"""
        return {
            'active_quests': {qid: quest.to_dict() for qid, quest in self.active_quests.items()},
            'completed_quests': self.completed_quests,
            'loyalty_programs': {mid: prog.to_dict() for mid, prog in self.loyalty_programs.items()},
            'next_quest_id': self.next_quest_id
        }
    
    def from_dict(self, data: dict):
        """Load from save"""
        self.completed_quests = data.get('completed_quests', [])
        self.next_quest_id = data.get('next_quest_id', 1)
        # Would need to reconstruct objects
