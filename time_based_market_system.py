"""
Time-Based Market System
Weekend markets, night markets, seasonal vendors, flash sales
"""

import random
from typing import List, Dict, Optional
from logger_config import logger


class SpecialVendor:
    """A special vendor that appears at specific times"""
    
    def __init__(self, vendor_id: str, name: str, specialty: str, 
                 schedule: dict, location: str):
        self.vendor_id = vendor_id
        self.name = name
        self.specialty = specialty  # 'exotic', 'rare_weapons', 'magic_items', etc.
        self.schedule = schedule  # When they appear
        self.location = location
        self.inventory = []
        self.discovered = False
        
    def is_active(self, game_time) -> bool:
        """Check if vendor is currently active"""
        day_of_week = game_time.day_count % 7  # 0-6
        hour, _ = game_time.get_time_hm()
        
        # Check day schedule
        if 'days' in self.schedule:
            if day_of_week not in self.schedule['days']:
                return False
        
        # Check hour schedule
        if 'hours' in self.schedule:
            start, end = self.schedule['hours']
            if start > end:  # Overnight hours
                if not (hour >= start or hour < end):
                    return False
            else:
                if not (start <= hour < end):
                    return False
        
        # Check season
        if 'season' in self.schedule:
            current_season = self._get_season(game_time.day_count)
            if current_season != self.schedule['season']:
                return False
        
        return True
    
    def _get_season(self, day_count: int) -> str:
        """Get current season"""
        day_of_year = day_count % 365
        if 80 <= day_of_year < 172:
            return 'spring'
        elif 172 <= day_of_year < 264:
            return 'summer'
        elif 264 <= day_of_year < 355:
            return 'fall'
        else:
            return 'winter'


class FlashSale:
    """A temporary sale event"""
    
    def __init__(self, sale_id: str, item_category: str, discount: float,
                 start_day: int, duration_hours: int):
        self.sale_id = sale_id
        self.item_category = item_category  # 'all', 'weapons', 'potions', etc.
        self.discount = discount  # 0.0-1.0 (0.3 = 30% off)
        self.start_day = start_day
        self.duration_hours = duration_hours
        self.announced = False
        
    def is_active(self, game_time) -> bool:
        """Check if sale is currently active"""
        current_hour = game_time.day_count * 24 + game_time.get_time_hm()[0]
        start_hour = self.start_day * 24
        end_hour = start_hour + self.duration_hours
        
        return start_hour <= current_hour < end_hour
    
    def get_discount_message(self) -> str:
        """Get sale announcement message"""
        discount_pct = int(self.discount * 100)
        category_name = self.item_category.replace('_', ' ').title()
        return f"FLASH SALE! {discount_pct}% off {category_name}! Limited time only!"


class TimeBasedMarketSystem:
    """Manages time-based market events and special vendors"""
    
    def __init__(self, game_time):
        self.game_time = game_time
        self.special_vendors: Dict[str, SpecialVendor] = {}
        self.active_flash_sales: List[FlashSale] = []
        self.weekend_market_active = False
        
        # Initialize special vendors
        self._initialize_special_vendors()
        
    def _initialize_special_vendors(self):
        """Create special vendors"""
        
        # Weekend Market Vendor (Sat-Sun, 8am-6pm)
        weekend_vendor = SpecialVendor(
            'weekend_merchant',
            'Traveling Merchant Magnus',
            'exotic_goods',
            {'days': [5, 6], 'hours': (8, 18)},  # Weekend
            'town_square'
        )
        self.special_vendors['weekend_merchant'] = weekend_vendor
        
        # Night Market Vendor (Every day, 10pm-4am)
        night_vendor = SpecialVendor(
            'night_merchant',
            'Nocturnal Trader Shade',
            'rare_items',
            {'hours': (22, 4)},  # 10pm to 4am
            'dark_alley'
        )
        self.special_vendors['night_merchant'] = night_vendor
        
        # Summer Festival Vendor (Summer season only)
        summer_vendor = SpecialVendor(
            'summer_merchant',
            'Festival Vendor Sunny',
            'seasonal_items',
            {'season': 'summer', 'hours': (10, 20)},
            'festival_grounds'
        )
        self.special_vendors['summer_merchant'] = summer_vendor
        
        # Winter Holiday Vendor (Winter season only)
        winter_vendor = SpecialVendor(
            'winter_merchant',
            'Frost Merchant Eira',
            'winter_goods',
            {'season': 'winter', 'hours': (9, 17)},
            'town_square'
        )
        self.special_vendors['winter_merchant'] = winter_vendor
        
        # Rare Weapons Dealer (Wednesdays only, 2pm-8pm)
        weapons_dealer = SpecialVendor(
            'weapons_dealer',
            'Master Armorer Steelheart',
            'rare_weapons',
            {'days': [3], 'hours': (14, 20)},  # Wednesday
            'blacksmith_district'
        )
        self.special_vendors['weapons_dealer'] = weapons_dealer
        
        logger.info(f"[TIME MARKET] Initialized {len(self.special_vendors)} special vendors")
    
    def get_active_vendors(self, town_name: str = None) -> List[SpecialVendor]:
        """Get currently active vendors"""
        active = []
        
        for vendor in self.special_vendors.values():
            if vendor.is_active(self.game_time):
                if town_name is None or vendor.location in ['town_square', 'any']:
                    active.append(vendor)
        
        return active
    
    def is_weekend_market_active(self) -> bool:
        """Check if weekend market is active"""
        day_of_week = self.game_time.day_count % 7
        hour, _ = self.game_time.get_time_hm()
        
        # Weekend (Sat-Sun) from 8am to 6pm
        return day_of_week in [5, 6] and 8 <= hour < 18
    
    def is_night_market_active(self) -> bool:
        """Check if night market is active"""
        hour, _ = self.game_time.get_time_hm()
        # 10pm to 4am
        return hour >= 22 or hour < 4
    
    def create_flash_sale(self, category: str, discount: float, duration_hours: int):
        """Create a new flash sale"""
        sale_id = f"flash_{self.game_time.day_count}_{len(self.active_flash_sales)}"
        sale = FlashSale(
            sale_id,
            category,
            discount,
            self.game_time.day_count,
            duration_hours
        )
        self.active_flash_sales.append(sale)
        logger.info(f"[TIME MARKET] Flash sale created: {category} -{int(discount*100)}% for {duration_hours}h")
        return sale
    
    def get_active_flash_sales(self) -> List[FlashSale]:
        """Get currently active flash sales"""
        active = []
        
        for sale in self.active_flash_sales:
            if sale.is_active(self.game_time):
                active.append(sale)
        
        # Clean up expired sales
        self.active_flash_sales = [s for s in self.active_flash_sales if s.is_active(self.game_time)]
        
        return active
    
    def apply_time_discount(self, item_category: str, base_price: int) -> Tuple[int, str]:
        """Apply time-based discounts to price"""
        active_sales = self.get_active_flash_sales()
        
        best_discount = 0.0
        sale_name = ""
        
        for sale in active_sales:
            if sale.item_category == 'all' or sale.item_category == item_category:
                if sale.discount > best_discount:
                    best_discount = sale.discount
                    sale_name = sale.get_discount_message()
        
        if best_discount > 0:
            discounted_price = int(base_price * (1.0 - best_discount))
            return discounted_price, sale_name
        
        return base_price, ""
    
    def daily_update(self):
        """Called each day to potentially create random flash sales"""
        # 15% chance of flash sale each day
        if random.random() < 0.15:
            categories = ['weapons', 'armor', 'potions', 'materials', 'all']
            category = random.choice(categories)
            discount = random.uniform(0.15, 0.40)  # 15-40% off
            duration = random.randint(6, 24)  # 6-24 hours
            
            self.create_flash_sale(category, discount, duration)
    
    def get_vendor_inventory(self, vendor_id: str) -> List[dict]:
        """Get special inventory for a vendor based on their specialty"""
        if vendor_id not in self.special_vendors:
            return []
        
        vendor = self.special_vendors[vendor_id]
        
        # Generate specialty items based on vendor type
        specialty_items = {
            'exotic_goods': [
                {'id': 'silk_robe', 'name': 'Silk Robe', 'price': 500, 'category': 'armor'},
                {'id': 'spice_bundle', 'name': 'Exotic Spices', 'price': 150, 'category': 'materials'},
                {'id': 'foreign_wine', 'name': 'Foreign Wine', 'price': 200, 'category': 'consumables'},
            ],
            'rare_items': [
                {'id': 'shadow_cloak', 'name': 'Shadow Cloak', 'price': 800, 'category': 'armor'},
                {'id': 'nightvision_potion', 'name': 'Nightvision Potion', 'price': 300, 'category': 'potions'},
                {'id': 'stealth_boots', 'name': 'Boots of Silence', 'price': 600, 'category': 'armor'},
            ],
            'seasonal_items': [
                {'id': 'festival_mask', 'name': 'Festival Mask', 'price': 100, 'category': 'cosmetic'},
                {'id': 'firework', 'name': 'Firework', 'price': 50, 'category': 'consumables'},
                {'id': 'party_favor', 'name': 'Party Favor', 'price': 25, 'category': 'consumables'},
            ],
            'winter_goods': [
                {'id': 'warm_coat', 'name': 'Warm Winter Coat', 'price': 400, 'category': 'armor'},
                {'id': 'hot_cocoa', 'name': 'Hot Cocoa', 'price': 15, 'category': 'consumables'},
                {'id': 'ice_skates', 'name': 'Ice Skates', 'price': 120, 'category': 'tools'},
            ],
            'rare_weapons': [
                {'id': 'masterwork_sword', 'name': 'Masterwork Sword', 'price': 1500, 'category': 'weapons'},
                {'id': 'enchanted_bow', 'name': 'Enchanted Bow', 'price': 1200, 'category': 'weapons'},
                {'id': 'legendary_axe', 'name': 'Legendary Axe', 'price': 2000, 'category': 'weapons'},
            ]
        }
        
        return specialty_items.get(vendor.specialty, [])
    
    def to_dict(self) -> dict:
        """Serialize"""
        return {
            'active_flash_sales': [
                {
                    'sale_id': s.sale_id,
                    'category': s.item_category,
                    'discount': s.discount,
                    'start_day': s.start_day,
                    'duration_hours': s.duration_hours,
                    'announced': s.announced
                }
                for s in self.active_flash_sales
            ],
            'discovered_vendors': [
                vendor_id for vendor_id, vendor in self.special_vendors.items()
                if vendor.discovered
            ]
        }
    
    def from_dict(self, data: dict):
        """Deserialize"""
        # Restore flash sales
        for sale_data in data.get('active_flash_sales', []):
            sale = FlashSale(
                sale_data['sale_id'],
                sale_data['category'],
                sale_data['discount'],
                sale_data['start_day'],
                sale_data['duration_hours']
            )
            sale.announced = sale_data.get('announced', False)
            self.active_flash_sales.append(sale)
        
        # Restore discovered vendors
        for vendor_id in data.get('discovered_vendors', []):
            if vendor_id in self.special_vendors:
                self.special_vendors[vendor_id].discovered = True
