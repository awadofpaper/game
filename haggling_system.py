"""
Haggling and Bartering System
Allows players to negotiate prices and trade items directly
"""

import logging
import random
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class HagglingSystem:
    """Manages price negotiation with merchants"""
    
    # Haggling difficulty tiers
    DIFFICULTY_EASY = 0.7  # 70% success chance at neutral
    DIFFICULTY_MEDIUM = 0.5  # 50% success chance at neutral
    DIFFICULTY_HARD = 0.3  # 30% success chance at neutral
    
    def __init__(self):
        self.active_haggle = None  # Current haggle session
        
    def start_haggle(self, merchant_id: str, merchant_name: str, item_name: str, 
                     base_price: int, is_buying: bool = True):
        """Start a haggling session"""
        self.active_haggle = {
            'merchant_id': merchant_id,
            'merchant_name': merchant_name,
            'item_name': item_name,
            'base_price': base_price,
            'is_buying': is_buying,
            'player_offer': base_price,
            'attempts': 0,
            'max_attempts': 3
        }
        logger.info(f"[HAGGLE] Started haggling for {item_name} at {base_price}g")
    
    def calculate_success_chance(self, player, reputation_manager, merchant_id: str, 
                                  merchant_name: str, offer_percentage: float) -> float:
        """Calculate chance of successful haggle based on multiple factors"""
        base_chance = 0.5  # 50% base
        
        # Factor 1: Charisma (if player has it)
        if hasattr(player, 'charisma'):
            charisma_bonus = (player.charisma - 10) * 0.02  # +2% per point above 10
            base_chance += charisma_bonus
        
        # Factor 2: Merchant Skill Level (natural improvement)
        if hasattr(player, 'skills_manager'):
            merchant_level = player.skills_manager.get_level('Merchant')
            # +0.2% per merchant level (max +20% at level 100)
            skill_bonus = merchant_level * 0.002
            base_chance += skill_bonus
            
            # Factor 3: Merchant Skill Perks (significant bonuses)
            perk_bonus = player.skills_manager.get_haggling_bonus() / 100.0
            base_chance += perk_bonus
        
        # Factor 4: Reputation with merchant
        if reputation_manager:
            rep = reputation_manager.get_or_create_reputation(merchant_id, merchant_name)
            rep_tier = rep.get_current_tier()
            # Each tier above Neutral adds 5%, each below reduces 10%
            tier_index = next((i for i, t in enumerate(rep.TIERS) if t.name == rep_tier.name), 2)
            neutral_index = 2  # Neutral is 3rd tier (index 2)
            tier_bonus = (tier_index - neutral_index) * 0.05
            base_chance += tier_bonus
        
        # Factor 5: How aggressive the haggle is
        # Asking for 10% off is easier than 50% off
        if offer_percentage < 0.9:  # Asking for more than 10% off
            aggression_penalty = (0.9 - offer_percentage) * 2.0  # 2x penalty for aggressive haggling
            base_chance -= aggression_penalty
        
        # Factor 6: Number of attempts (merchants get annoyed)
        if self.active_haggle:
            attempt_penalty = self.active_haggle['attempts'] * 0.15  # -15% per attempt
            base_chance -= attempt_penalty
        
        # Clamp between 5% and 95%
        return max(0.05, min(0.95, base_chance))
    
    def attempt_haggle(self, player, reputation_manager, merchant_id: str, 
                       merchant_name: str, offered_price: int) -> Tuple[bool, str, int]:
        """
        Attempt to haggle for a better price
        Returns: (success, message, final_price)
        """
        if not self.active_haggle:
            return False, "No active haggle session", 0
        
        self.active_haggle['attempts'] += 1
        base_price = self.active_haggle['base_price']
        is_buying = self.active_haggle['is_buying']
        
        # Calculate offer as percentage of base
        if is_buying:
            offer_percentage = offered_price / base_price
            # Player wants to pay less
            if offered_price >= base_price:
                return False, "That's not haggling, that's paying full price!", base_price
        else:
            offer_percentage = offered_price / base_price
            # Player wants to get more when selling
            if offered_price <= base_price:
                return False, "I'm already offering a fair price!", base_price
        
        # Calculate success chance
        success_chance = self.calculate_success_chance(
            player, reputation_manager, merchant_id, merchant_name, offer_percentage
        )
        
        # Roll for success
        roll = random.random()
        logger.info(f"[HAGGLE] Chance: {success_chance:.2%}, Roll: {roll:.2%}")
        
        if roll < success_chance:
            # Success! Get the offered price
            success_msg = self._get_success_message()
            
            # Small reputation gain for successful haggle (you're a good negotiator)
            if reputation_manager:
                rep = reputation_manager.get_or_create_reputation(merchant_id, merchant_name)
                rep.modify_reputation(5, "successful haggle")
            
            return True, success_msg, offered_price
        else:
            # Failure
            if self.active_haggle['attempts'] >= self.active_haggle['max_attempts']:
                # Out of attempts, merchant is annoyed
                failure_msg = self._get_failure_message_final()
                
                # Reputation loss for annoying merchant
                if reputation_manager:
                    rep = reputation_manager.get_or_create_reputation(merchant_id, merchant_name)
                    rep.on_haggle_failure()  # -10 rep
                
                return False, failure_msg, base_price
            else:
                # Can try again
                failure_msg = self._get_failure_message_attempt(self.active_haggle['attempts'])
                return False, failure_msg, base_price
    
    def _get_success_message(self) -> str:
        """Random success message"""
        messages = [
            "Fine, you drive a hard bargain!",
            "Alright, alright, you win this round.",
            "You're quite the negotiator! Deal.",
            "I like your style. We have a deal.",
            "Okay, but don't tell anyone about this price!",
        ]
        return random.choice(messages)
    
    def _get_failure_message_attempt(self, attempt: int) -> str:
        """Random failure message with attempts left"""
        messages = [
            "I can't go that low, try again.",
            "You're asking too much, be reasonable.",
            "No deal at that price, sorry.",
            "That's insulting! Make a better offer.",
        ]
        return random.choice(messages) + f" ({3 - attempt} attempts left)"
    
    def _get_failure_message_final(self) -> str:
        """Final rejection message"""
        messages = [
            "I've had enough of this! Full price or nothing!",
            "You're wasting my time! Pay the asking price or leave!",
            "No more haggling! Take it or leave it!",
            "I'm done negotiating with you!",
        ]
        return random.choice(messages)
    
    def end_haggle(self):
        """End the current haggle session"""
        self.active_haggle = None


class BarteringSystem:
    """Manages item-for-item trading"""
    
    def __init__(self):
        self.active_barter = None
        
    def start_barter(self, merchant_id: str, merchant_name: str, shop):
        """Start a bartering session"""
        self.active_barter = {
            'merchant_id': merchant_id,
            'merchant_name': merchant_name,
            'shop': shop,
            'player_items': [],  # List of (item_id, quantity, value)
            'merchant_items': [],  # List of (item_id, quantity, value)
        }
    
    def add_player_item(self, item_id: str, quantity: int, value: int):
        """Add item to player's side of barter"""
        if self.active_barter:
            self.active_barter['player_items'].append((item_id, quantity, value))
    
    def add_merchant_item(self, item_id: str, quantity: int, value: int):
        """Add item to merchant's side of barter"""
        if self.active_barter:
            self.active_barter['merchant_items'].append((item_id, quantity, value))
    
    def calculate_fairness(self) -> Tuple[float, str]:
        """
        Calculate how fair the barter is
        Returns: (fairness_ratio, description)
        fairness_ratio: player_value / merchant_value (1.0 = perfectly fair)
        """
        if not self.active_barter:
            return 0.0, "No active barter"
        
        player_total = sum(val * qty for _, qty, val in self.active_barter['player_items'])
        merchant_total = sum(val * qty for _, qty, val in self.active_barter['merchant_items'])
        
        if merchant_total == 0:
            return 0.0, "Merchant offers nothing"
        
        fairness = player_total / merchant_total
        
        if fairness >= 1.2:
            return fairness, "Very favorable for merchant"
        elif fairness >= 1.05:
            return fairness, "Slightly favorable for merchant"
        elif fairness >= 0.95:
            return fairness, "Fair trade"
        elif fairness >= 0.8:
            return fairness, "Slightly favorable for you"
        else:
            return fairness, "Very favorable for you"
    
    def attempt_barter(self, player, reputation_manager) -> Tuple[bool, str]:
        """
        Attempt to complete the barter
        Returns: (success, message)
        """
        if not self.active_barter:
            return False, "No active barter session"
        
        fairness, description = self.calculate_fairness()
        
        # Merchant acceptance based on fairness
        # Merchants want at least 0.85 fairness (player gives 85% of value they receive)
        # But reputation can help
        min_fairness = 0.85
        
        if reputation_manager:
            rep = reputation_manager.get_or_create_reputation(
                self.active_barter['merchant_id'],
                self.active_barter['merchant_name']
            )
            tier = rep.get_current_tier()
            # Better reputation = more lenient (up to 0.70 for max tier)
            tier_index = next((i for i, t in enumerate(rep.TIERS) if t.name == tier.name), 2)
            min_fairness = max(0.70, 0.85 - (tier_index * 0.03))
        
        if fairness >= min_fairness:
            # Accept barter
            # Exchange items
            # Remove player items
            for item_id, quantity, _ in self.active_barter['player_items']:
                if item_id in player.inventory:
                    player.inventory[item_id] -= quantity
                    if player.inventory[item_id] <= 0:
                        del player.inventory[item_id]
            
            # Add merchant items
            for item_id, quantity, _ in self.active_barter['merchant_items']:
                player.inventory[item_id] = player.inventory.get(item_id, 0) + quantity
                # Update shop stock
                shop = self.active_barter['shop']
                for shop_item in shop.inventory:
                    if shop_item.item_id == item_id:
                        shop_item.purchase(quantity)
                        break
            
            # Small reputation gain for fair trades
            if reputation_manager and fairness >= 0.95:
                rep = reputation_manager.get_or_create_reputation(
                    self.active_barter['merchant_id'],
                    self.active_barter['merchant_name']
                )
                rep.modify_reputation(10, "fair barter")
            
            return True, f"Trade accepted! {description}"
        else:
            # Reject barter
            return False, f"I can't accept this trade. {description}. (Need {min_fairness:.0%} fairness, got {fairness:.0%})"
    
    def end_barter(self):
        """End the barter session"""
        self.active_barter = None
    
    def get_player_total(self) -> int:
        """Get total value of player's offered items"""
        if not self.active_barter:
            return 0
        return sum(val * qty for _, qty, val in self.active_barter['player_items'])
    
    def get_merchant_total(self) -> int:
        """Get total value of merchant's offered items"""
        if not self.active_barter:
            return 0
        return sum(val * qty for _, qty, val in self.active_barter['merchant_items'])
