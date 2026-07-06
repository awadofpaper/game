"""
Merchant Reputation System
Tracks individual reputation with each merchant/shop for pricing and exclusive access
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ReputationTier:
    """Reputation tier with benefits"""
    def __init__(self, name: str, min_rep: int, discount: float, description: str):
        self.name = name
        self.min_rep = min_rep
        self.discount = discount  # Percentage discount (0.0 to 1.0)
        self.description = description


class MerchantReputation:
    """Tracks reputation with a single merchant"""
    
    # Reputation tiers
    TIERS = [
        ReputationTier("Hostile", -1000, -0.50, "Refuses to trade or charges 50% extra"),
        ReputationTier("Distrusted", -100, -0.20, "Charges 20% extra, limited stock"),
        ReputationTier("Neutral", 0, 0.0, "Normal prices and service"),
        ReputationTier("Known", 100, 0.05, "5% discount, friendly service"),
        ReputationTier("Respected", 300, 0.10, "10% discount, access to rare items"),
        ReputationTier("Trusted", 600, 0.15, "15% discount, special orders available"),
        ReputationTier("Valued Customer", 1000, 0.20, "20% discount, exclusive items unlock"),
        ReputationTier("Partner", 1500, 0.25, "25% discount, best prices, early access to new stock"),
    ]
    
    def __init__(self, merchant_id: str, merchant_name: str):
        self.merchant_id = merchant_id
        self.merchant_name = merchant_name
        self.reputation = 0  # Current reputation points
        self.total_spent = 0  # Total gold spent with this merchant
        self.total_sold = 0  # Total gold earned from selling to merchant
        self.transactions = 0  # Number of transactions
        self.last_interaction_day = 0  # Game day of last interaction
        
        # Flags
        self.has_been_stolen_from = False
        self.has_been_scammed = False
        self.trust_broken = False  # Permanent negative flag
        
    def get_current_tier(self) -> ReputationTier:
        """Get current reputation tier"""
        current_tier = self.TIERS[0]  # Default to lowest
        for tier in self.TIERS:
            if self.reputation >= tier.min_rep:
                current_tier = tier
        return current_tier
    
    def get_discount_multiplier(self) -> float:
        """Get price multiplier based on reputation (1.0 = normal, 0.8 = 20% off)"""
        tier = self.get_current_tier()
        return 1.0 - tier.discount
    
    def can_trade(self) -> bool:
        """Check if merchant will trade with player"""
        # Hostile merchants refuse to trade
        return self.reputation > -1000
    
    def can_access_exclusive_items(self) -> bool:
        """Check if player can access exclusive items"""
        return self.reputation >= 1000  # Valued Customer tier
    
    def can_special_order(self) -> bool:
        """Check if player can place special orders"""
        return self.reputation >= 600  # Trusted tier
    
    def can_access_rare_items(self) -> bool:
        """Check if player can see rare items"""
        return self.reputation >= 300  # Respected tier
    
    def modify_reputation(self, amount: int, reason: str = ""):
        """Modify reputation with this merchant"""
        old_tier = self.get_current_tier()
        self.reputation += amount
        new_tier = self.get_current_tier()
        
        # Log tier changes
        if old_tier.name != new_tier.name:
            logger.info(f"[MERCHANT REP] {self.merchant_name}: {old_tier.name} → {new_tier.name} ({reason})")
        
        # Clamp reputation
        self.reputation = max(-2000, min(2000, self.reputation))
    
    def on_purchase(self, gold_spent: int):
        """Called when player buys from merchant"""
        self.total_spent += gold_spent
        self.transactions += 1
        
        # Gain reputation from purchases (1 rep per 10g spent)
        rep_gain = max(1, gold_spent // 10)
        self.modify_reputation(rep_gain, f"purchased {gold_spent}g worth")
    
    def on_sale(self, gold_earned: int):
        """Called when player sells to merchant"""
        self.total_sold += gold_earned
        self.transactions += 1
        
        # Gain small reputation from sales (1 rep per 20g sold)
        rep_gain = max(1, gold_earned // 20)
        self.modify_reputation(rep_gain, f"sold {gold_earned}g worth")
    
    def on_theft_detected(self):
        """Called when player is caught stealing from this merchant"""
        self.has_been_stolen_from = True
        self.modify_reputation(-150, "caught stealing")
    
    def on_scam_detected(self):
        """Called when merchant discovers they were scammed"""
        self.has_been_scammed = True
        self.modify_reputation(-200, "scammed with fake item")
    
    def on_trust_broken(self):
        """Called for major betrayals (permanent damage)"""
        self.trust_broken = True
        self.modify_reputation(-500, "major betrayal")
    
    def on_quest_completed(self, quest_reward_rep: int):
        """Called when completing merchant's quest"""
        self.modify_reputation(quest_reward_rep, "completed quest")
    
    def on_haggle_success(self):
        """Called when successfully haggling"""
        # Small rep loss for aggressive haggling
        self.modify_reputation(-2, "haggled aggressively")
    
    def on_haggle_failure(self):
        """Called when haggling fails and offends merchant"""
        self.modify_reputation(-10, "offended during haggling")
    
    def get_greeting(self) -> str:
        """Get merchant greeting based on reputation"""
        tier = self.get_current_tier()
        
        if tier.name == "Hostile":
            return "I don't want your business. Get out!"
        elif tier.name == "Distrusted":
            return "I'm watching you closely..."
        elif tier.name == "Neutral":
            return "Welcome. What can I help you with?"
        elif tier.name == "Known":
            return "Ah, good to see you again!"
        elif tier.name == "Respected":
            return "Welcome back, friend! Let me show you something special."
        elif tier.name == "Trusted":
            return "My trusted customer! I've been saving the best for you."
        elif tier.name == "Valued Customer":
            return "Welcome, valued customer! I have exclusive items just for you."
        elif tier.name == "Partner":
            return "Partner! The best prices and finest goods are yours!"
        else:
            return "Hello there."
    
    def get_status_text(self) -> str:
        """Get status text for UI"""
        tier = self.get_current_tier()
        next_tier = None
        
        # Find next tier
        for t in self.TIERS:
            if t.min_rep > self.reputation:
                next_tier = t
                break
        
        status = f"Status: {tier.name}\n"
        status += f"Reputation: {self.reputation}\n"
        status += f"Discount: {int(tier.discount * 100)}%\n"
        
        if next_tier:
            rep_needed = next_tier.min_rep - self.reputation
            status += f"\nNext Tier: {next_tier.name} ({rep_needed} rep needed)"
        else:
            status += f"\nYou've reached maximum reputation!"
        
        return status


class MerchantReputationManager:
    """Manages reputation with all merchants"""
    
    def __init__(self):
        self.reputations: Dict[str, MerchantReputation] = {}  # merchant_id -> MerchantReputation
        
    def get_or_create_reputation(self, merchant_id: str, merchant_name: str) -> MerchantReputation:
        """Get or create reputation entry for a merchant"""
        if merchant_id not in self.reputations:
            self.reputations[merchant_id] = MerchantReputation(merchant_id, merchant_name)
        return self.reputations[merchant_id]
    
    def get_reputation(self, merchant_id: str) -> Optional[MerchantReputation]:
        """Get reputation with a merchant"""
        return self.reputations.get(merchant_id)
    
    def get_discount_multiplier(self, merchant_id: str) -> float:
        """Get price multiplier for a merchant (1.0 = normal price)"""
        rep = self.reputations.get(merchant_id)
        if rep:
            return rep.get_discount_multiplier()
        return 1.0  # Neutral if no reputation yet
    
    def can_trade_with(self, merchant_id: str) -> bool:
        """Check if player can trade with merchant"""
        rep = self.reputations.get(merchant_id)
        if rep:
            return rep.can_trade()
        return True  # Can trade if no history
    
    def record_purchase(self, merchant_id: str, merchant_name: str, gold_spent: int):
        """Record a purchase from a merchant"""
        rep = self.get_or_create_reputation(merchant_id, merchant_name)
        rep.on_purchase(gold_spent)
    
    def record_sale(self, merchant_id: str, merchant_name: str, gold_earned: int):
        """Record a sale to a merchant"""
        rep = self.get_or_create_reputation(merchant_id, merchant_name)
        rep.on_sale(gold_earned)
    
    def record_theft(self, merchant_id: str, merchant_name: str):
        """Record theft detection"""
        rep = self.get_or_create_reputation(merchant_id, merchant_name)
        rep.on_theft_detected()
    
    def record_scam(self, merchant_id: str, merchant_name: str):
        """Record scam detection"""
        rep = self.get_or_create_reputation(merchant_id, merchant_name)
        rep.on_scam_detected()
    
    def get_all_reputations(self) -> List[MerchantReputation]:
        """Get list of all merchant reputations"""
        return list(self.reputations.values())
    
    def get_reputation_summary(self) -> str:
        """Get text summary of all reputations"""
        if not self.reputations:
            return "No merchant relationships established."
        
        summary = "MERCHANT REPUTATIONS:\n\n"
        for rep in sorted(self.reputations.values(), key=lambda r: r.reputation, reverse=True):
            tier = rep.get_current_tier()
            summary += f"{rep.merchant_name}: {tier.name} ({rep.reputation} rep)\n"
        
        return summary
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for saving"""
        return {
            merchant_id: {
                'merchant_name': rep.merchant_name,
                'reputation': rep.reputation,
                'total_spent': rep.total_spent,
                'total_sold': rep.total_sold,
                'transactions': rep.transactions,
                'has_been_stolen_from': rep.has_been_stolen_from,
                'has_been_scammed': rep.has_been_scammed,
                'trust_broken': rep.trust_broken,
            }
            for merchant_id, rep in self.reputations.items()
        }
    
    def from_dict(self, data: dict):
        """Load from dictionary"""
        self.reputations.clear()
        for merchant_id, rep_data in data.items():
            rep = MerchantReputation(merchant_id, rep_data['merchant_name'])
            rep.reputation = rep_data['reputation']
            rep.total_spent = rep_data['total_spent']
            rep.total_sold = rep_data['total_sold']
            rep.transactions = rep_data['transactions']
            rep.has_been_stolen_from = rep_data.get('has_been_stolen_from', False)
            rep.has_been_scammed = rep_data.get('has_been_scammed', False)
            rep.trust_broken = rep_data.get('trust_broken', False)
            self.reputations[merchant_id] = rep
