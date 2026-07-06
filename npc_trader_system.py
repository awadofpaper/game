"""
NPC Trader System - NPCs that actively participate in the economy
- Sell gathered resources to shops/markets
- Buy items they need (tools, food, equipment)
- Travel between towns for arbitrage
- Respond to market conditions
- Impact supply/demand dynamically
"""

import random
import math
import pygame
from logger_config import logger


class NPCTraderBehavior:
    """AI behavior for NPCs engaging in trade"""
    
    def __init__(self, npc):
        self.npc = npc
        self.last_trade_day = 0
        self.trade_cooldown_days = 1  # Trade once per day minimum
        self.preferred_shop = None
        self.arbitrage_target_town = None
        self.arbitrage_items = []  # Items to buy low and sell high
        
        # Trading personality
        self.risk_tolerance = random.uniform(0.3, 1.0)  # 0 = conservative, 1 = aggressive
        self.sell_threshold = random.uniform(0.6, 0.9)  # Sell when inventory reaches this %
        self.buy_eagerness = random.uniform(0.3, 0.8)  # Likelihood to buy useful items
        
    def should_sell_resources(self, game_time):
        """Check if NPC should sell gathered resources"""
        # Don't sell too frequently
        if game_time.day_count - self.last_trade_day < self.trade_cooldown_days:
            return False
        
        # Check inventory fullness
        if hasattr(self.npc, 'current_weight') and hasattr(self.npc, 'base_weight_capacity'):
            inventory_percent = self.npc.current_weight / self.npc.base_weight_capacity
            if inventory_percent >= self.sell_threshold:
                return True
        
        # Check item count
        if hasattr(self.npc, 'inventory'):
            total_items = sum(self.npc.inventory.values())
            if total_items >= 10:  # Has enough items to make trip worthwhile
                return True
        
        return False
    
    def should_buy_supplies(self, game_time):
        """Check if NPC should buy supplies"""
        if game_time.day_count - self.last_trade_day < self.trade_cooldown_days:
            return False
        
        # Check if low on tools or consumables
        if hasattr(self.npc, 'dubloons') and self.npc.dubloons >= 100:
            # Can afford to shop
            if random.random() < self.buy_eagerness:
                return True
        
        return False
    
    def get_sellable_items(self):
        """Get list of items NPC can sell"""
        sellable = {}
        
        if not hasattr(self.npc, 'inventory'):
            return sellable
        
        # Resources are sellable (not tools or equipment)
        tool_keywords = ['pickaxe', 'axe', 'fishing', 'sword', 'armor', 'helmet', 'boots', 'shield']
        
        for item_name, count in self.npc.inventory.items():
            if count > 0:
                # Don't sell tools/equipment
                is_tool = any(keyword in item_name.lower() for keyword in tool_keywords)
                if not is_tool:
                    sellable[item_name] = count
        
        return sellable
    
    def calculate_sell_quantity(self, item_name, available_count):
        """Calculate how many of an item to sell (keep some for self)"""
        # Keep at least 2 of consumables, sell all resources
        consumable_keywords = ['cooked', 'potion', 'bread', 'food']
        is_consumable = any(keyword in item_name.lower() for keyword in consumable_keywords)
        
        if is_consumable:
            return max(0, available_count - 2)
        else:
            # Sell all resources
            return available_count
    
    def should_attempt_arbitrage(self, market_manager):
        """Check if NPC should try arbitrage trading between towns"""
        if not market_manager or not hasattr(self.npc, 'dubloons'):
            return False
        
        # Need capital to do arbitrage
        if self.npc.dubloons < 500:
            return False
        
        # Only high risk-tolerance NPCs do arbitrage
        if self.risk_tolerance < 0.6:
            return False
        
        # Random chance based on risk tolerance
        return random.random() < (self.risk_tolerance * 0.1)  # Max ~10% chance
    
    def find_arbitrage_opportunity(self, current_town, market_manager, town_manager):
        """Find best arbitrage opportunity across towns"""
        if not market_manager or not town_manager:
            return None
        
        best_opportunity = None
        best_profit_margin = 0
        
        # Check all tradeable commodities
        from market_system import TRADEABLE_COMMODITIES
        
        for commodity_id, commodity in TRADEABLE_COMMODITIES.items():
            # Find arbitrage opportunity
            opportunity = market_manager.find_arbitrage_opportunities(commodity_id)
            
            if opportunity:
                profit_margin = opportunity['profit_margin']
                if profit_margin > best_profit_margin:
                    best_profit_margin = profit_margin
                    best_opportunity = {
                        'commodity_id': commodity_id,
                        'buy_town': opportunity['buy_town'],
                        'sell_town': opportunity['sell_town'],
                        'buy_price': opportunity['buy_price'],
                        'sell_price': opportunity['sell_price'],
                        'profit_margin': profit_margin
                    }
        
        # Only pursue if profit margin > 20%
        if best_opportunity and best_profit_margin > 0.2:
            return best_opportunity
        
        return None


class TravelingMerchantNPC:
    """Special NPC that travels between towns doing arbitrage"""
    
    def __init__(self, name, start_town, config):
        self.name = name
        self.current_town = start_town
        self.target_town = None
        self.home_town = start_town
        
        # Position
        self.x = start_town.center_x
        self.y = start_town.center_y
        self.rect = pygame.Rect(int(self.x) - 16, int(self.y) - 16, 32, 32)
        
        # Trading
        self.inventory = {}
        self.dubloons = random.randint(1000, 5000)  # Start with capital
        self.trade_history = []
        
        # Movement
        self.speed = 150  # Faster than gatherers
        self.traveling = False
        self.travel_progress = 0.0
        
        # AI
        self.trader_behavior = NPCTraderBehavior(self)
        self.trader_behavior.risk_tolerance = random.uniform(0.7, 1.0)  # High risk traders
        
        # Schedule
        self.days_in_town = 0
        self.min_days_per_town = 2
        self.max_days_per_town = 5
        
        # Combat stats (merchants can defend themselves)
        self.level = random.randint(10, 20)  # Higher level than basic gatherers
        self.max_health = random.randint(80, 120)
        self.health = self.max_health
        self.base_damage = random.randint(10, 20)
        self.alive = True
        self.last_attack_time = 0
        self.attack_cooldown = 1.2  # seconds
        self.attack_range = 50
        
        # Combat targets
        self.combat_target = None
        self.is_recovering = False
        self.current_weight = 0
        
        # Equipment (merchants buy protection)
        self.weapon = {'name': 'merchant_dagger', 'damage': 10}
        self.armor = {'name': 'leather_vest', 'defense': 5}
        self.town = start_town  # For ally detection
        
    def update(self, dt, game_time, market_manager, town_manager):
        """Update traveling merchant AI"""
        # If traveling, update position
        if self.traveling:
            self._update_travel(dt)
            return
        
        # If in town, do business
        self.days_in_town += dt / (24 * 60 * 60)  # Convert to game days
        
        # Trade if we've been here long enough
        if self.days_in_town >= random.uniform(self.min_days_per_town, self.max_days_per_town):
            # Find next destination and arbitrage opportunity
            opportunity = self.trader_behavior.find_arbitrage_opportunity(
                self.current_town, market_manager, town_manager
            )
            
            if opportunity:
                # Buy items in current town (if we're in buy town)
                if opportunity['buy_town'] == self.current_town.name:
                    self._buy_for_arbitrage(opportunity)
                
                # Set target to sell town
                self.target_town = self._get_town_by_name(opportunity['sell_town'], town_manager)
                if self.target_town:
                    self.traveling = True
                    self.travel_progress = 0.0
                    logger.info(f"[TRADER] {self.name} traveling to {self.target_town.name}")
            else:
                # No opportunity, pick random town
                self.target_town = random.choice([t for t in town_manager.towns if t != self.current_town])
                self.traveling = True
                self.travel_progress = 0.0
            
            self.days_in_town = 0
    
    def _update_travel(self, dt):
        """Update travel between towns"""
        if not self.target_town:
            self.traveling = False
            return
        
        # Calculate distance
        dx = self.target_town.center_x - self.current_town.center_x
        dy = self.target_town.center_y - self.current_town.center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Update progress
        travel_speed = self.speed * dt
        progress_increment = travel_speed / distance if distance > 0 else 1.0
        self.travel_progress += progress_increment
        
        # Update position
        self.x = self.current_town.center_x + dx * self.travel_progress
        self.y = self.current_town.center_y + dy * self.travel_progress
        
        # Check arrival
        if self.travel_progress >= 1.0:
            self.current_town = self.target_town
            self.x = self.current_town.center_x
            self.y = self.current_town.center_y
            self.traveling = False
            self.days_in_town = 0
            logger.info(f"[TRADER] {self.name} arrived at {self.current_town.name}")
            
            # Sell items upon arrival
            self._sell_arbitrage_items()
    
    def _buy_for_arbitrage(self, opportunity):
        """Buy items for arbitrage"""
        commodity_id = opportunity['commodity_id']
        buy_price = opportunity['buy_price']
        
        # Calculate how many we can afford
        max_affordable = int(self.dubloons / buy_price)
        quantity_to_buy = min(max_affordable, random.randint(5, 20))
        
        if quantity_to_buy > 0:
            cost = quantity_to_buy * buy_price
            self.dubloons -= cost
            self.inventory[commodity_id] = self.inventory.get(commodity_id, 0) + quantity_to_buy
            
            logger.info(f"[TRADER] {self.name} bought {quantity_to_buy}x {commodity_id} for {cost}g")
    
    def _sell_arbitrage_items(self):
        """Sell items at destination"""
        # This will be called when trader arrives at destination
        # Will integrate with shop system
        pass
    
    def _get_town_by_name(self, town_name, town_manager):
        """Get town object by name"""
        for town in town_manager.towns:
            if town.name == town_name:
                return town
        return None
    
    def take_damage(self, damage, attacker=None):
        """Take damage from attack"""
        actual_damage = max(1, damage - self.armor.get('defense', 0))
        self.health -= actual_damage
        
        print(f"[MERCHANT {self.name}] Took {actual_damage} damage! HP: {self.health}/{self.max_health}")
        
        if self.health <= 0:
            self.health = 0
            # Merchant dies - handled by combat system
        else:
            # Fight back
            if attacker and not self.combat_target:
                self.combat_target = attacker
    
    def attack_target(self, target, current_time):
        """Attack a target"""
        import time
        if time.time() - self.last_attack_time < self.attack_cooldown:
            return False
        
        # Calculate damage
        damage = self.base_damage + self.weapon.get('damage', 0)
        
        # Deal damage
        if hasattr(target, 'take_damage'):
            target.take_damage(damage, self)
        elif hasattr(target, 'health'):
            target.health -= damage
        
        self.last_attack_time = time.time()
        print(f"[MERCHANT {self.name}] Attacked {getattr(target, 'name', 'target')} for {damage} damage")
        return True
    
    def die(self, killer=None):
        """Merchant dies - drops all inventory"""
        self.alive = False
        print(f"[MERCHANT {self.name}] Defeated by {getattr(killer, 'name', 'unknown')}!")
        
        # Return dropped items
        dropped = self.inventory.copy()
        self.inventory.clear()
        return dropped


class NPCTradeEngine:
    """Central system managing all NPC trading activity"""
    
    def __init__(self, shop_manager, market_manager, town_manager):
        self.shop_manager = shop_manager
        self.market_manager = market_manager
        self.town_manager = town_manager
        
        # Track all NPC traders
        self.gatherer_traders = {}  # {npc_id: NPCTraderBehavior}
        self.traveling_merchants = []
        
        # Statistics
        self.total_npc_sales = 0
        self.total_npc_purchases = 0
        self.daily_npc_trade_volume = 0
        
    def register_gatherer_npc(self, npc):
        """Register a gatherer NPC for trading"""
        npc_id = id(npc)
        if npc_id not in self.gatherer_traders:
            self.gatherer_traders[npc_id] = NPCTraderBehavior(npc)
            logger.info(f"[TRADE] Registered {npc.name} for trading")
    
    def spawn_traveling_merchant(self, town, config):
        """Spawn a traveling merchant NPC"""
        merchant_names = [
            "Marco the Trader", "Silk Road Sam", "Merchant Maya",
            "Trading Tom", "Caravan Carl", "Nomad Nancy"
        ]
        name = random.choice(merchant_names)
        merchant = TravelingMerchantNPC(name, town, config)
        self.traveling_merchants.append(merchant)
        logger.info(f"[TRADE] Spawned traveling merchant: {name} at {town.name}")
        return merchant
    
    def update_npc_trading(self, game_time):
        """Update all NPC trading activity (called daily)"""
        # Update gatherer NPC trading
        for npc_id, trader_behavior in list(self.gatherer_traders.items()):
            npc = trader_behavior.npc
            
            # Check if NPC should sell resources
            if trader_behavior.should_sell_resources(game_time):
                self._npc_sell_resources(npc, trader_behavior, game_time)
            
            # Check if NPC should buy supplies
            if trader_behavior.should_buy_supplies(game_time):
                self._npc_buy_supplies(npc, trader_behavior, game_time)
        
        # Reset daily volume
        self.daily_npc_trade_volume = 0
    
    def update_traveling_merchants(self, dt, game_time):
        """Update all traveling merchants"""
        for merchant in self.traveling_merchants:
            merchant.update(dt, game_time, self.market_manager, self.town_manager)
    
    def _npc_sell_resources(self, npc, trader_behavior, game_time):
        """NPC sells gathered resources to shops"""
        if not hasattr(npc, 'inventory') or not hasattr(npc, 'dubloons'):
            return
        
        # Get sellable items
        sellable = trader_behavior.get_sellable_items()
        if not sellable:
            return
        
        # Find nearest shop
        shop = self._find_nearest_shop(npc)
        if not shop:
            logger.warning(f"[TRADE] {npc.name} couldn't find shop to sell to")
            return
        
        total_earned = 0
        items_sold = []
        
        # Sell each item
        for item_name, available_count in sellable.items():
            quantity_to_sell = trader_behavior.calculate_sell_quantity(item_name, available_count)
            
            if quantity_to_sell > 0:
                # Find item in shop to get sell price
                sell_price = self._get_item_sell_price(item_name, shop)
                
                if sell_price > 0:
                    # Sell the items
                    earnings = sell_price * quantity_to_sell
                    npc.dubloons += earnings
                    npc.inventory[item_name] -= quantity_to_sell
                    
                    if npc.inventory[item_name] <= 0:
                        del npc.inventory[item_name]
                    
                    total_earned += earnings
                    items_sold.append(f"{quantity_to_sell}x {item_name}")
                    
                    # Update market supply (if market system available)
                    self._update_market_supply(item_name, quantity_to_sell, increase=True)
        
        if total_earned > 0:
            trader_behavior.last_trade_day = game_time.day_count
            self.total_npc_sales += total_earned
            self.daily_npc_trade_volume += total_earned
            logger.info(f"[TRADE] {npc.name} sold {', '.join(items_sold)} for {total_earned}g")
            
            # Update NPC weight
            if hasattr(npc, 'get_current_weight'):
                npc.current_weight = npc.get_current_weight()
    
    def _npc_buy_supplies(self, npc, trader_behavior, game_time):
        """NPC buys supplies from shops"""
        if not hasattr(npc, 'dubloons') or npc.dubloons < 50:
            return
        
        # Find nearest shop
        shop = self._find_nearest_shop(npc)
        if not shop:
            return
        
        # Determine what to buy based on needs
        items_to_buy = self._determine_npc_needs(npc, shop)
        
        total_spent = 0
        items_bought = []
        
        for item_name, quantity in items_to_buy:
            buy_price = self._get_item_buy_price(item_name, shop)
            
            if buy_price > 0:
                cost = buy_price * quantity
                
                if npc.dubloons >= cost:
                    # Buy the item
                    npc.dubloons -= cost
                    npc.inventory[item_name] = npc.inventory.get(item_name, 0) + quantity
                    
                    total_spent += cost
                    items_bought.append(f"{quantity}x {item_name}")
                    
                    # Update market supply (if market system available)
                    self._update_market_supply(item_name, quantity, increase=False)
        
        if total_spent > 0:
            trader_behavior.last_trade_day = game_time.day_count
            self.total_npc_purchases += total_spent
            self.daily_npc_trade_volume += total_spent
            logger.info(f"[TRADE] {npc.name} bought {', '.join(items_bought)} for {total_spent}g")
    
    def _find_nearest_shop(self, npc):
        """Find nearest shop to NPC"""
        if not self.shop_manager or not hasattr(self.shop_manager, 'shops'):
            return None
        
        nearest_shop = None
        nearest_dist = float('inf')
        
        for shop_id, shop_data in self.shop_manager.shops.items():
            if 'shop' in shop_data and 'position' in shop_data:
                shop_x, shop_y = shop_data['position']
                dist = math.sqrt((npc.x - shop_x) ** 2 + (npc.y - shop_y) ** 2)
                
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_shop = shop_data['shop']
        
        return nearest_shop
    
    def _get_item_sell_price(self, item_name, shop):
        """Get price shop will pay for an item"""
        # Check shop inventory for this item
        if hasattr(shop, 'inventory'):
            for shop_item in shop.inventory:
                if shop_item.item_id == item_name or shop_item.name.lower().replace(' ', '_') == item_name:
                    return shop_item.sell_price
        
        # Default price for resources not in shop
        default_prices = {
            'iron_ore': 15, 'coal': 12, 'gold_ore': 50, 'mithril_ore': 100,
            'wood': 8, 'oak': 12, 'willow': 15, 'yew': 25, 'magic_wood': 50,
            'raw_shrimp': 5, 'raw_sardine': 8, 'raw_salmon': 12, 'raw_tuna': 18,
            'raw_lobster': 25, 'raw_swordfish': 35
        }
        
        return default_prices.get(item_name, 10)
    
    def _get_item_buy_price(self, item_name, shop):
        """Get price to buy an item from shop"""
        if hasattr(shop, 'inventory'):
            for shop_item in shop.inventory:
                if shop_item.item_id == item_name or shop_item.name.lower().replace(' ', '_') == item_name:
                    return shop_item.buy_price
        
        return 0
    
    def _determine_npc_needs(self, npc, shop):
        """Determine what items NPC should buy"""
        needs = []
        
        # Check for food/consumables
        if hasattr(npc, 'inventory'):
            food_count = sum(count for item, count in npc.inventory.items() 
                           if 'cooked' in item or 'bread' in item or 'food' in item)
            
            if food_count < 3:
                # Buy food
                needs.append(('bread', 3))
        
        # Check for tools (if current tool is basic)
        if hasattr(npc, 'tool'):
            if 'bronze' in npc.tool and npc.dubloons >= 150:
                # Upgrade to iron tool
                gatherer_type = getattr(npc, 'gatherer_type', 'miner')
                if gatherer_type == 'miner':
                    needs.append(('iron_pickaxe', 1))
                elif gatherer_type == 'woodcutter':
                    needs.append(('iron_axe', 1))
        
        return needs
    
    def _update_market_supply(self, item_name, quantity, increase=True):
        """Update market supply levels based on NPC trading"""
        if not self.market_manager:
            return
        
        # Find commodity ID for this item
        from market_system import TRADEABLE_COMMODITIES
        
        commodity_id = None
        for cid, commodity in TRADEABLE_COMMODITIES.items():
            if cid == item_name or commodity.name.lower().replace(' ', '_') == item_name:
                commodity_id = cid
                break
        
        if not commodity_id:
            return
        
        # Update supply in all town markets
        for town_name, town_market in self.market_manager.town_markets.items():
            market_data = town_market.get_or_create_market_data(commodity_id)
            
            if increase:
                market_data.supply += quantity
            else:
                market_data.supply = max(0, market_data.supply - quantity)
            
            # Recalculate price
            from price_engine import PriceCalculator
            calculator = PriceCalculator()
            market_data.current_price = calculator.calculate_price(market_data, {})
    
    def get_statistics(self):
        """Get trading statistics"""
        return {
            'total_npc_sales': self.total_npc_sales,
            'total_npc_purchases': self.total_npc_purchases,
            'daily_trade_volume': self.daily_npc_trade_volume,
            'registered_traders': len(self.gatherer_traders),
            'traveling_merchants': len(self.traveling_merchants)
        }
