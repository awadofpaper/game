"""
Smuggling and Criminal Economy System
Contraband trading, black market expansion, criminal reputation
"""

import logging
import random
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ContrabandItem:
    """Represents an illegal item"""
    
    def __init__(self, item_id: str, name: str, description: str, 
                 base_value: int, detection_risk: float, penalty: int):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.base_value = base_value
        self.detection_risk = detection_risk  # 0.0-1.0, chance of being caught
        self.penalty = penalty  # Fine/jail time if caught
        self.black_market_multiplier = random.uniform(2.0, 4.0)  # Sells for 2-4x value


class CriminalReputation:
    """Tracks reputation in the underworld"""
    
    TIERS = [
        {'name': 'Unknown', 'min_rep': 0, 'benefits': 'No benefits'},
        {'name': 'Petty Criminal', 'min_rep': 100, 'benefits': 'Access to fences'},
        {'name': 'Known Smuggler', 'min_rep': 300, 'benefits': 'Better prices, hidden contacts'},
        {'name': 'Crime Lord', 'min_rep': 600, 'benefits': 'Run protection rackets'},
        {'name': 'Kingpin', 'min_rep': 1000, 'benefits': 'Control black markets'},
        {'name': 'Shadow Ruler', 'min_rep': 1500, 'benefits': 'Immunity from low-level law'},
    ]
    
    def __init__(self):
        self.reputation = 0
        self.successful_smuggles = 0
        self.total_contraband_value = 0
        self.times_caught = 0
        self.protection_rackets = []  # Merchants paying protection
        self.controlled_markets = []  # Black markets under control
        
    def get_tier(self) -> dict:
        """Get current criminal tier"""
        current_tier = self.TIERS[0]
        for tier in self.TIERS:
            if self.reputation >= tier['min_rep']:
                current_tier = tier
        return current_tier
    
    def modify_reputation(self, amount: int, reason: str = ""):
        """Modify criminal reputation"""
        old_tier = self.get_tier()
        self.reputation += amount
        self.reputation = max(0, min(2000, self.reputation))
        new_tier = self.get_tier()
        
        if old_tier['name'] != new_tier['name']:
            logger.info(f"[CRIMINAL REP] {old_tier['name']} → {new_tier['name']} ({reason})")
    
    def on_successful_smuggle(self, value: int):
        """Called when successfully smuggling contraband"""
        self.successful_smuggles += 1
        self.total_contraband_value += value
        rep_gain = max(5, value // 100)  # 1 rep per 100g value, min 5
        self.modify_reputation(rep_gain, f"smuggled {value}g worth")
    
    def on_caught_smuggling(self):
        """Called when caught with contraband"""
        self.times_caught += 1
        self.modify_reputation(-50, "caught smuggling")
    
    def can_run_protection_racket(self) -> bool:
        """Check if can run protection rackets"""
        return self.reputation >= 600  # Crime Lord tier
    
    def can_control_black_market(self) -> bool:
        """Check if can control black markets"""
        return self.reputation >= 1000  # Kingpin tier
    
    def get_black_market_discount(self) -> float:
        """Get discount at black markets based on reputation"""
        tier_index = next((i for i, t in enumerate(self.TIERS) if t['name'] == self.get_tier()['name']), 0)
        return tier_index * 0.05  # 5% per tier
    
    def to_dict(self) -> dict:
        """Serialize"""
        return {
            'reputation': self.reputation,
            'successful_smuggles': self.successful_smuggles,
            'total_contraband_value': self.total_contraband_value,
            'times_caught': self.times_caught,
            'protection_rackets': self.protection_rackets,
            'controlled_markets': self.controlled_markets
        }


class BlackMarketVendor:
    """A hidden black market vendor"""
    
    def __init__(self, vendor_id: str, name: str, location: str, password: str):
        self.vendor_id = vendor_id
        self.name = name
        self.location = location  # Hidden location description
        self.password = password  # Password to access
        self.inventory = []
        self.specializes_in = random.choice(['weapons', 'stolen_goods', 'contraband', 'info'])
        self.discovered = False  # Player has found this vendor
        self.trust_level = 0  # Builds with transactions
        
    def check_password(self, attempt: str) -> bool:
        """Check if password is correct"""
        return attempt.lower() == self.password.lower()
    
    def generate_inventory(self):
        """Generate black market inventory"""
        # High-value illegal items
        self.inventory = []
        # TODO: Generate contraband based on specialization


class ProtectionRacket:
    """A protection racket run on a merchant"""
    
    def __init__(self, merchant_id: str, merchant_name: str, weekly_payment: int):
        self.merchant_id = merchant_id
        self.merchant_name = merchant_name
        self.weekly_payment = weekly_payment
        self.weeks_active = 0
        self.total_collected = 0
        self.resistance_level = random.randint(1, 10)  # How much they resist
        
    def collect_payment(self, player, criminal_rep: CriminalReputation) -> Tuple[bool, str, int]:
        """Attempt to collect protection money"""
        # Higher criminal rep makes collection easier
        success_chance = 0.5 + (criminal_rep.reputation / 2000.0)  # 50-100%
        
        # Resistance makes it harder
        success_chance -= (self.resistance_level * 0.03)
        
        if random.random() < success_chance:
            # Success
            self.weeks_active += 1
            self.total_collected += self.weekly_payment
            return True, f"Collected {self.weekly_payment}g from {self.merchant_name}", self.weekly_payment
        else:
            # Merchant reports to guards
            return False, f"{self.merchant_name} reported you to the guards!", 0


class SmugglingSystem:
    """Manages smuggling operations and contraband"""
    
    # Define contraband items
    CONTRABAND = [
        ContrabandItem("stolen_gems", "Stolen Gemstones", "Hot jewelry from recent heist", 
                      500, 0.3, 200),
        ContrabandItem("illegal_drugs", "Moonleaf Extract", "Highly illegal stimulant", 
                      300, 0.5, 500),
        ContrabandItem("forbidden_tome", "Forbidden Spellbook", "Banned magical knowledge", 
                      1000, 0.2, 300),
        ContrabandItem("counterfeit_coins", "Counterfeit Currency", "Fake gold pieces", 
                      200, 0.6, 1000),
        ContrabandItem("black_lotus", "Black Lotus", "Extremely illegal narcotic", 
                      800, 0.7, 800),
        ContrabandItem("cursed_artifact", "Cursed Relic", "Possession is a capital crime", 
                      1500, 0.4, 1500),
    ]
    
    def __init__(self):
        self.criminal_reputation = CriminalReputation()
        self.black_market_vendors: Dict[str, BlackMarketVendor] = {}
        self.protection_rackets: Dict[str, ProtectionRacket] = {}
        self.player_contraband: Dict[str, int] = {}  # item_id -> quantity
        
        # Statistics
        self.contraband_smuggled_value = 0
        self.protection_money_collected = 0
        
    def add_contraband(self, item_id: str, quantity: int = 1):
        """Add contraband to player's hidden inventory"""
        self.player_contraband[item_id] = self.player_contraband.get(item_id, 0) + quantity
        logger.info(f"[SMUGGLING] Added {quantity}x {item_id} to contraband inventory")
    
    def attempt_smuggle(self, item_id: str, quantity: int, player) -> Tuple[bool, str, int]:
        """Attempt to smuggle contraband into town"""
        if item_id not in self.player_contraband or self.player_contraband[item_id] < quantity:
            return False, "You don't have that contraband", 0
        
        # Find contraband definition
        contraband = next((c for c in self.CONTRABAND if c.item_id == item_id), None)
        if not contraband:
            return False, "Invalid contraband", 0
        
        # Calculate detection chance
        detection_chance = contraband.detection_risk
        
        # Criminal reputation reduces detection
        rep_reduction = self.criminal_reputation.get_tier()['min_rep'] / 2000.0  # Up to -50%
        detection_chance *= (1.0 - rep_reduction)
        
        if random.random() < detection_chance:
            # Caught!
            penalty = contraband.penalty
            player.dubloons = max(0, player.dubloons - penalty)
            self.player_contraband[item_id] -= quantity
            if self.player_contraband[item_id] <= 0:
                del self.player_contraband[item_id]
            
            self.criminal_reputation.on_caught_smuggling()
            
            return False, f"CAUGHT! Guards confiscated contraband and fined you {penalty}g!", -penalty
        else:
            # Success! Can now sell at black market
            value = contraband.base_value * quantity
            self.criminal_reputation.on_successful_smuggle(value)
            self.contraband_smuggled_value += value
            
            return True, f"Successfully smuggled {quantity}x {contraband.name}!", value
    
    def sell_contraband(self, item_id: str, quantity: int, player, 
                        vendor_id: Optional[str] = None) -> Tuple[bool, str, int]:
        """Sell contraband at black market"""
        if item_id not in self.player_contraband or self.player_contraband[item_id] < quantity:
            return False, "You don't have that contraband", 0
        
        contraband = next((c for c in self.CONTRABAND if c.item_id == item_id), None)
        if not contraband:
            return False, "Invalid contraband", 0
        
        # Calculate price (much higher than normal goods)
        base_value = contraband.base_value * contraband.black_market_multiplier
        
        # Apply criminal reputation discount
        discount = self.criminal_reputation.get_black_market_discount()
        final_price = int(base_value * (1.0 + discount))
        total = final_price * quantity
        
        # Remove contraband
        self.player_contraband[item_id] -= quantity
        if self.player_contraband[item_id] <= 0:
            del self.player_contraband[item_id]
        
        # Pay player
        player.dubloons += total
        
        logger.info(f"[SMUGGLING] Sold {quantity}x {item_id} for {total}g")
        return True, f"Sold {quantity}x {contraband.name} for {total}g", total
    
    def create_black_market_vendor(self, vendor_id: str, name: str, 
                                   location: str, password: str) -> BlackMarketVendor:
        """Create a new black market vendor"""
        vendor = BlackMarketVendor(vendor_id, name, location, password)
        self.black_market_vendors[vendor_id] = vendor
        logger.info(f"[SMUGGLING] Created black market vendor {name}")
        return vendor
    
    def discover_vendor(self, vendor_id: str) -> bool:
        """Player discovers a hidden vendor"""
        if vendor_id in self.black_market_vendors:
            self.black_market_vendors[vendor_id].discovered = True
            return True
        return False
    
    def start_protection_racket(self, merchant_id: str, merchant_name: str,
                                player) -> Tuple[bool, str]:
        """Start a protection racket on a merchant"""
        if not self.criminal_reputation.can_run_protection_racket():
            return False, "Criminal reputation too low (need Crime Lord tier)"
        
        if merchant_id in self.protection_rackets:
            return False, "Already running protection on this merchant"
        
        # Calculate weekly payment based on merchant's revenue
        weekly_payment = random.randint(100, 500)
        
        racket = ProtectionRacket(merchant_id, merchant_name, weekly_payment)
        self.protection_rackets[merchant_id] = racket
        
        logger.info(f"[PROTECTION] Started racket on {merchant_name} ({weekly_payment}g/week)")
        return True, f"Started protection racket on {merchant_name} ({weekly_payment}g per week)"
    
    def collect_protection_money(self, merchant_id: str, player) -> Tuple[bool, str, int]:
        """Collect weekly protection money"""
        if merchant_id not in self.protection_rackets:
            return False, "No active racket on this merchant", 0
        
        racket = self.protection_rackets[merchant_id]
        success, message, amount = racket.collect_payment(player, self.criminal_reputation)
        
        if success:
            player.dubloons += amount
            self.protection_money_collected += amount
            self.criminal_reputation.modify_reputation(5, "collected protection money")
        
        return success, message, amount
    
    def weekly_update(self):
        """Update protection rackets weekly"""
        # Could auto-collect or track resistance
        pass
    
    def get_contraband_inventory(self) -> List[Tuple[ContrabandItem, int]]:
        """Get list of contraband and quantities"""
        items = []
        for item_id, quantity in self.player_contraband.items():
            contraband = next((c for c in self.CONTRABAND if c.item_id == item_id), None)
            if contraband:
                items.append((contraband, quantity))
        return items
    
    def to_dict(self) -> dict:
        """Serialize"""
        return {
            'criminal_reputation': self.criminal_reputation.to_dict(),
            'player_contraband': self.player_contraband,
            'contraband_smuggled_value': self.contraband_smuggled_value,
            'protection_money_collected': self.protection_money_collected
        }
    
    def from_dict(self, data: dict):
        """Load from save"""
        if 'criminal_reputation' in data:
            rep_data = data['criminal_reputation']
            self.criminal_reputation.reputation = rep_data.get('reputation', 0)
            self.criminal_reputation.successful_smuggles = rep_data.get('successful_smuggles', 0)
            self.criminal_reputation.total_contraband_value = rep_data.get('total_contraband_value', 0)
            self.criminal_reputation.times_caught = rep_data.get('times_caught', 0)
        
        self.player_contraband = data.get('player_contraband', {})
        self.contraband_smuggled_value = data.get('contraband_smuggled_value', 0)
        self.protection_money_collected = data.get('protection_money_collected', 0)
