"""
Advanced Trading Systems
- Item Quality/Condition System
- Time-Based Sales (Weekend/Night Markets)
- Item Appraisal System
- Consignment/Auction System
"""

import random
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ===== QUALITY/CONDITION SYSTEM =====

class ItemCondition:
    """Represents the condition/quality of an item"""
    
    CONDITIONS = [
        {'name': 'Broken', 'value_mult': 0.10, 'durability_mult': 0.0, 'color': (100, 100, 100)},
        {'name': 'Damaged', 'value_mult': 0.30, 'durability_mult': 0.40, 'color': (180, 100, 100)},
        {'name': 'Worn', 'value_mult': 0.60, 'durability_mult': 0.70, 'color': (200, 150, 100)},
        {'name': 'Good', 'value_mult': 0.85, 'durability_mult': 0.90, 'color': (200, 200, 200)},
        {'name': 'Fine', 'value_mult': 1.00, 'durability_mult': 1.00, 'color': (100, 200, 100)},
        {'name': 'Excellent', 'value_mult': 1.25, 'durability_mult': 1.20, 'color': (100, 150, 255)},
        {'name': 'Masterwork', 'value_mult': 1.75, 'durability_mult': 1.50, 'color': (200, 100, 255)},
        {'name': 'Legendary', 'value_mult': 3.00, 'durability_mult': 2.00, 'color': (255, 215, 0)},
    ]
    
    def __init__(self, condition_level: int = 4):
        """Initialize with condition level (0=Broken, 4=Fine, 7=Legendary)"""
        self.condition_level = max(0, min(7, condition_level))
        
    def get_condition_data(self) -> dict:
        """Get current condition data"""
        return self.CONDITIONS[self.condition_level]
    
    def get_name(self) -> str:
        return self.get_condition_data()['name']
    
    def get_value_multiplier(self) -> float:
        return self.get_condition_data()['value_mult']
    
    def get_durability_multiplier(self) -> float:
        return self.get_condition_data()['durability_mult']
    
    def get_color(self) -> tuple:
        return self.get_condition_data()['color']
    
    def degrade(self, amount: int = 1):
        """Degrade condition by amount"""
        self.condition_level = max(0, self.condition_level - amount)
        logger.info(f"[CONDITION] Item degraded to {self.get_name()}")
    
    def repair(self, amount: int = 1):
        """Repair condition by amount"""
        old_level = self.condition_level
        self.condition_level = min(7, self.condition_level + amount)
        if self.condition_level > old_level:
            logger.info(f"[CONDITION] Item repaired to {self.get_name()}")
    
    def to_dict(self) -> dict:
        return {'condition_level': self.condition_level}
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data.get('condition_level', 4))


class QualitySystemManager:
    """Manages item quality/condition across the game"""
    
    def __init__(self):
        self.item_conditions = {}  # {item_instance_id: ItemCondition}
        self.clearance_bins = {}  # {shop_id: [damaged_items]}
        
    def add_item(self, item_id: str, condition_level: int = 4) -> str:
        """Add item with condition, returns unique instance ID"""
        instance_id = f"{item_id}_{random.randint(1000, 9999)}"
        self.item_conditions[instance_id] = ItemCondition(condition_level)
        return instance_id
    
    def get_condition(self, instance_id: str) -> Optional[ItemCondition]:
        """Get item condition"""
        return self.item_conditions.get(instance_id)
    
    def calculate_price(self, base_price: int, instance_id: str) -> int:
        """Calculate price based on condition"""
        condition = self.get_condition(instance_id)
        if condition:
            return int(base_price * condition.get_value_multiplier())
        return base_price
    
    def add_to_clearance(self, shop_id: str, item_id: str, base_price: int, condition_level: int):
        """Add damaged item to shop's clearance bin"""
        if shop_id not in self.clearance_bins:
            self.clearance_bins[shop_id] = []
        
        instance_id = self.add_item(item_id, condition_level)
        self.clearance_bins[shop_id].append({
            'instance_id': instance_id,
            'item_id': item_id,
            'base_price': base_price,
            'condition_level': condition_level
        })
        
    def get_clearance_items(self, shop_id: str) -> List[dict]:
        """Get clearance items for a shop"""
        return self.clearance_bins.get(shop_id, [])


# ===== TIME-BASED SALES SYSTEM =====

class SpecialMarketEvent:
    """Represents a special market event"""
    
    def __init__(self, event_type: str, day_of_week: int = None, hour_range: tuple = None):
        self.event_type = event_type
        self.day_of_week = day_of_week  # 0-6 (Monday-Sunday)
        self.hour_range = hour_range  # (start_hour, end_hour)
        self.active_vendors = []
        self.price_modifiers = {}
        self.special_items = []
        
    def is_active(self, game_time) -> bool:
        """Check if event is currently active"""
        if self.day_of_week is not None:
            current_day = game_time.day_count % 7
            if current_day != self.day_of_week:
                return False
        
        if self.hour_range is not None:
            hour, _ = game_time.get_time_hm()
            start, end = self.hour_range
            if start > end:  # Overnight event
                if not (hour >= start or hour < end):
                    return False
            else:
                if not (start <= hour < end):
                    return False
        
        return True


class TimeBasedSalesManager:
    """Manages time-based market events"""
    
    def __init__(self, game_time):
        self.game_time = game_time
        self.events = self._create_events()
        
    def _create_events(self) -> List[SpecialMarketEvent]:
        """Create special market events"""
        events = []
        
        # Weekend Market (Saturday & Sunday, 8am-6pm)
        weekend_sat = SpecialMarketEvent('weekend_market', day_of_week=5, hour_range=(8, 18))
        weekend_sat.special_items = ['exotic_spice', 'rare_herb', 'foreign_wine', 'silk_cloth']
        weekend_sat.price_modifiers = {'food': 0.9, 'luxury': 1.1}
        events.append(weekend_sat)
        
        weekend_sun = SpecialMarketEvent('weekend_market', day_of_week=6, hour_range=(8, 18))
        weekend_sun.special_items = ['exotic_spice', 'rare_herb', 'foreign_wine', 'silk_cloth']
        weekend_sun.price_modifiers = {'food': 0.9, 'luxury': 1.1}
        events.append(weekend_sun)
        
        # Night Market (Every day, 10pm-4am)
        night_market = SpecialMarketEvent('night_market', hour_range=(22, 4))
        night_market.special_items = ['moonstone', 'shadow_essence', 'night_bloom', 'star_metal']
        night_market.price_modifiers = {'potion': 1.2, 'magic': 0.85}
        events.append(night_market)
        
        # Fisherman's Dawn (Every day, 5am-9am)
        dawn_market = SpecialMarketEvent('dawn_market', hour_range=(5, 9))
        dawn_market.special_items = ['fresh_fish', 'morning_dew', 'sunrise_pearl']
        dawn_market.price_modifiers = {'fish': 0.7, 'food': 0.9}
        events.append(dawn_market)
        
        # Midweek Flash Sale (Wednesday, 12pm-2pm)
        flash_sale = SpecialMarketEvent('flash_sale', day_of_week=2, hour_range=(12, 14))
        flash_sale.price_modifiers = {'weapon': 0.75, 'armor': 0.75, 'tool': 0.8}
        events.append(flash_sale)
        
        return events
    
    def get_active_events(self) -> List[SpecialMarketEvent]:
        """Get currently active market events"""
        return [event for event in self.events if event.is_active(self.game_time)]
    
    def get_price_modifier(self, item_category: str) -> float:
        """Get combined price modifier from all active events"""
        modifier = 1.0
        for event in self.get_active_events():
            if item_category in event.price_modifiers:
                modifier *= event.price_modifiers[item_category]
        return modifier
    
    def get_available_special_items(self) -> List[str]:
        """Get all special items available from active events"""
        items = []
        for event in self.get_active_events():
            items.extend(event.special_items)
        return list(set(items))


# ===== ITEM APPRAISAL SYSTEM =====

class AppraisalSystem:
    """Manages item identification and appraisal"""
    
    APPRAISAL_COST = 10  # Base cost to appraise an item
    
    def __init__(self):
        self.unidentified_items = {}  # {item_instance_id: true_item_data}
        self.player_appraisal_skill = 0  # 0-100
        
    def add_unidentified_item(self, item_id: str, true_value: int, true_name: str, 
                             rarity: str = 'common') -> str:
        """Add an unidentified item"""
        instance_id = f"unknown_{random.randint(1000, 9999)}"
        self.unidentified_items[instance_id] = {
            'true_id': item_id,
            'true_value': true_value,
            'true_name': true_name,
            'rarity': rarity,
            'identified': False
        }
        return instance_id
    
    def auto_identify_check(self, instance_id: str, player=None) -> bool:
        """Check if player's skill auto-identifies item"""
        if instance_id not in self.unidentified_items:
            return False
        
        item_data = self.unidentified_items[instance_id]
        if item_data['identified']:
            return True
        
        # Check merchant skill perks for auto-identification
        if player and hasattr(player, 'skills_manager'):
            item_rarity = item_data.get('rarity', 'common')
            if player.skills_manager.can_auto_identify(item_rarity):
                item_data['identified'] = True
                return True
        
        # Higher skill = better chance to auto-identify
        # At 100 skill, always identify items worth <500g
        if self.player_appraisal_skill >= 100 or item_data['true_value'] < 50:
            return True
        
        success_chance = self.player_appraisal_skill / 100.0
        value_difficulty = min(1.0, item_data['true_value'] / 1000.0)
        
        return random.random() < (success_chance - value_difficulty * 0.5)
    
    def appraise_item(self, instance_id: str, player) -> Tuple[bool, str, int]:
        """
        Appraise an item for a fee
        Returns (success, item_name, item_value)
        """
        if instance_id not in self.unidentified_items:
            return False, "Unknown item", 0
        
        item_data = self.unidentified_items[instance_id]
        
        # Check merchant skill for transaction fee reduction
        cost = self.APPRAISAL_COST
        if hasattr(player, 'skills_manager'):
            if player.skills_manager.has_transaction_fee_reduction():
                cost = int(cost * 0.75)  # 25% reduction
        
        # Check if player can afford
        if player.dubloons < cost:
            return False, "Cannot afford appraisal", 0
        
        # Deduct cost
        player.dubloons -= cost
        
        # Identify item
        item_data['identified'] = True
        
        # Gain merchant XP for appraisals
        if hasattr(player, 'skills_manager'):
            xp_reward = max(1, int(item_data['true_value'] / 10))  # 1 XP per 10g value
            player.skills_manager.add_xp('Merchant', xp_reward)
        
        # Gain legacy appraisal skill (for backwards compatibility)
        self.player_appraisal_skill = min(100, self.player_appraisal_skill + 1)
        
        logger.info(f"[APPRAISAL] Identified {item_data['true_name']} for {cost}g")
        
        return True, item_data['true_name'], item_data['true_value']
    
    def get_display_name(self, instance_id: str, player=None) -> str:
        """Get display name for item (??? if unidentified)"""
        if instance_id not in self.unidentified_items:
            return "Unknown"
        
        item_data = self.unidentified_items[instance_id]
        if item_data['identified'] or self.auto_identify_check(instance_id, player):
            return item_data['true_name']
        return "??? Mysterious Item"
    
    def get_estimated_value(self, instance_id: str, player=None) -> str:
        """Get value estimate for unidentified item"""
        if instance_id not in self.unidentified_items:
            return "Unknown"
        
        item_data = self.unidentified_items[instance_id]
        if item_data['identified']:
            return str(item_data['true_value'])
        
        # Calculate effective appraisal skill
        effective_skill = self.player_appraisal_skill
        
        # Add bonus from merchant skill perks
        if player and hasattr(player, 'skills_manager'):
            appraisal_bonus = player.skills_manager.get_appraisal_bonus()
            effective_skill = min(100, effective_skill + appraisal_bonus)
        
        # Give rough estimate based on effective skill
        true_value = item_data['true_value']
        if effective_skill >= 75:
            variance = 0.15  # ±15% (very accurate)
        elif effective_skill >= 50:
            variance = 0.3  # ±30%
        elif effective_skill >= 25:
            variance = 0.5  # ±50%
        else:
            variance = 1.0  # ±100%
        
        low = int(true_value * (1 - variance))
        high = int(true_value * (1 + variance))
        return f"{low}-{high}g"


# ===== CONSIGNMENT/AUCTION SYSTEM =====

class ConsignmentItem:
    """Item left at shop to sell over time"""
    
    def __init__(self, item_id: str, item_name: str, quantity: int, 
                 asking_price: int, consigner_id: str, shop_id: str, list_day: int):
        self.item_id = item_id
        self.item_name = item_name
        self.quantity = quantity
        self.asking_price = asking_price
        self.consigner_id = consigner_id  # 'player' or NPC ID
        self.shop_id = shop_id
        self.list_day = list_day
        self.sold_quantity = 0
        self.sale_proceeds = 0
        
    def sell_unit(self, price: int):
        """Sell one unit"""
        if self.sold_quantity < self.quantity:
            self.sold_quantity += 1
            self.sale_proceeds += price
            return True
        return False
    
    def is_fully_sold(self) -> bool:
        return self.sold_quantity >= self.quantity
    
    def get_commission(self, commission_rate: float = 0.1) -> int:
        """Calculate shop commission"""
        return int(self.sale_proceeds * commission_rate)
    
    def get_payout(self, commission_rate: float = 0.1) -> int:
        """Calculate payout to consigner after commission"""
        return self.sale_proceeds - self.get_commission(commission_rate)


class AuctionItem:
    """Item in auction"""
    
    def __init__(self, item_id: str, item_name: str, starting_bid: int, 
                 buyout_price: int, seller_id: str, duration_days: int, start_day: int):
        self.item_id = item_id
        self.item_name = item_name
        self.starting_bid = starting_bid
        self.current_bid = starting_bid
        self.buyout_price = buyout_price
        self.seller_id = seller_id
        self.duration_days = duration_days
        self.start_day = start_day
        self.end_day = start_day + duration_days
        self.current_bidder = None
        self.bid_history = []
        self.sold = False
        
    def place_bid(self, bidder_id: str, amount: int) -> Tuple[bool, str]:
        """Place a bid"""
        if self.sold:
            return False, "Auction already ended"
        
        if amount < self.current_bid + 10:
            return False, f"Bid must be at least {self.current_bid + 10}g"
        
        if amount >= self.buyout_price:
            # Instant buyout
            self.current_bid = self.buyout_price
            self.current_bidder = bidder_id
            self.sold = True
            self.bid_history.append((bidder_id, amount, 'buyout'))
            return True, f"Buyout successful! Won for {self.buyout_price}g"
        
        # Regular bid
        self.current_bid = amount
        self.current_bidder = bidder_id
        self.bid_history.append((bidder_id, amount, 'bid'))
        return True, f"Bid placed: {amount}g"
    
    def is_expired(self, current_day: int) -> bool:
        """Check if auction has expired"""
        return current_day >= self.end_day
    
    def days_remaining(self, current_day: int) -> int:
        """Days remaining in auction"""
        return max(0, self.end_day - current_day)


class ConsignmentAuctionManager:
    """Manages consignment and auction systems"""
    
    CONSIGNMENT_COMMISSION = 0.15  # 15% commission
    AUCTION_COMMISSION = 0.10  # 10% commission
    
    def __init__(self, game_time):
        self.game_time = game_time
        self.consignment_items = []  # List of ConsignmentItem
        self.auctions = []  # List of AuctionItem
        self.player_proceeds = 0  # Uncollected proceeds from sales
        
    def add_consignment(self, item_id: str, item_name: str, quantity: int, 
                       asking_price: int, shop_id: str) -> str:
        """Add item to consignment"""
        consignment = ConsignmentItem(
            item_id, item_name, quantity, asking_price,
            'player', shop_id, self.game_time.day_count
        )
        self.consignment_items.append(consignment)
        logger.info(f"[CONSIGNMENT] Listed {quantity}x {item_name} for {asking_price}g each")
        return f"Listed {quantity}x {item_name} for {asking_price}g each (15% commission on sale)"
    
    def add_auction(self, item_id: str, item_name: str, starting_bid: int,
                   buyout_price: int, duration_days: int) -> str:
        """Add item to auction"""
        auction = AuctionItem(
            item_id, item_name, starting_bid, buyout_price,
            'player', duration_days, self.game_time.day_count
        )
        self.auctions.append(auction)
        logger.info(f"[AUCTION] Listed {item_name}, starting {starting_bid}g, buyout {buyout_price}g")
        return f"Auction created for {item_name} ({duration_days} days)"
    
    def update_daily(self):
        """Daily update - simulate sales"""
        current_day = self.game_time.day_count
        
        # Process consignment sales
        for consignment in self.consignment_items[:]:
            if consignment.consigner_id != 'player':
                continue
            
            if consignment.is_fully_sold():
                continue
            
            # Chance to sell units each day (30% per unit)
            for _ in range(consignment.quantity - consignment.sold_quantity):
                if random.random() < 0.3:
                    # Sold! Price varies ±10%
                    sale_price = int(consignment.asking_price * random.uniform(0.9, 1.1))
                    consignment.sell_unit(sale_price)
                    logger.info(f"[CONSIGNMENT] Sold 1x {consignment.item_name} for {sale_price}g")
            
            # If fully sold, add proceeds
            if consignment.is_fully_sold():
                payout = consignment.get_payout(self.CONSIGNMENT_COMMISSION)
                self.player_proceeds += payout
                logger.info(f"[CONSIGNMENT] {consignment.item_name} fully sold. Payout: {payout}g")
        
        # Process auction expirations
        for auction in self.auctions[:]:
            if auction.seller_id != 'player':
                continue
            
            if auction.sold:
                continue
            
            if auction.is_expired(current_day):
                if auction.current_bidder:
                    # Auction won
                    proceeds = int(auction.current_bid * (1 - self.AUCTION_COMMISSION))
                    self.player_proceeds += proceeds
                    auction.sold = True
                    logger.info(f"[AUCTION] {auction.item_name} sold to {auction.current_bidder} for {auction.current_bid}g")
                else:
                    # No bids, auction failed
                    logger.info(f"[AUCTION] {auction.item_name} expired with no bids")
                    self.auctions.remove(auction)
        
        # Simulate NPC bids on player auctions
        for auction in self.auctions:
            if auction.seller_id == 'player' and not auction.sold:
                # 20% chance per day an NPC bids
                if random.random() < 0.2:
                    npc_bid = auction.current_bid + random.randint(10, 50)
                    auction.place_bid(f"NPC_Bidder_{random.randint(1, 100)}", npc_bid)
                    logger.info(f"[AUCTION] NPC bid {npc_bid}g on {auction.item_name}")
    
    def collect_proceeds(self, player) -> int:
        """Collect all proceeds from sales"""
        amount = self.player_proceeds
        player.dubloons += amount
        self.player_proceeds = 0
        return amount
    
    def get_player_consignments(self) -> List[ConsignmentItem]:
        """Get player's active consignments"""
        return [c for c in self.consignment_items if c.consigner_id == 'player']
    
    def get_player_auctions(self) -> List[AuctionItem]:
        """Get player's active auctions"""
        return [a for a in self.auctions if a.seller_id == 'player']
    
    def get_active_auctions(self) -> List[AuctionItem]:
        """Get all active auctions (for browsing/bidding)"""
        current_day = self.game_time.day_count
        return [a for a in self.auctions if not a.sold and not a.is_expired(current_day)]
