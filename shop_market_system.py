"""
Shop & Market System
Handles market/shop distinction, shop types, inheritance, auctions, merchant combat, and shady merchants.
"""
import random

SHOP_TYPES = [
    "general", "weaponsmith", "armorer", "alchemist", "jewelry", "magic", "food", "furniture", "pet"
]

class Shop:
    def __init__(self, shop_id, owner_id, shop_type):
        self.shop_id = shop_id
        self.owner_id = owner_id
        self.shop_type = shop_type
        self.inventory = []
        self.is_auction = False
        self.auction_bid = 2000
        self.takeover_fee = 30000
        self.inheritance_mode = False
        self.child_owner_id = None
        self.child_owner_age = None

    def sell_item(self, item):
        self.inventory.append(item)

    def start_auction(self):
        self.is_auction = True
        self.auction_bid = 2000

    def bid(self, amount):
        if self.is_auction and amount > self.auction_bid:
            self.auction_bid = amount
            return True
        return False

    def takeover(self, amount):
        if amount >= self.takeover_fee:
            self.is_auction = False
            return True
        return False

    def handle_inheritance(self, wife_id, kid_id, kid_age):
        if wife_id:
            self.owner_id = wife_id
        elif kid_id:
            self.owner_id = kid_id
            self.child_owner_id = kid_id
            self.child_owner_age = kid_age
            self.inheritance_mode = kid_age < 18

class Market:
    def __init__(self):
        self.inventory = []

    def sell_item(self, item):
        # Only common/uncommon items
        if item.rarity in ['common', 'uncommon']:
            self.inventory.append(item)

class ShopMarketSystem:
    def __init__(self):
        self.shops = {}  # {shop_id: Shop}
        self.markets = {}  # {market_id: Market}
        self.shady_merchants = {}  # {inn_id: merchant_id}

    def add_shop(self, shop_id, owner_id, shop_type):
        shop = Shop(shop_id, owner_id, shop_type)
        self.shops[shop_id] = shop
        return shop

    def add_market(self, market_id):
        market = Market()
        self.markets[market_id] = market
        return market

    def add_shady_merchant(self, inn_id, merchant_id):
        self.shady_merchants[inn_id] = merchant_id

    def get_shady_merchant(self, inn_id):
        return self.shady_merchants.get(inn_id)

    def shady_merchant_sell_disguise(self, merchant_id, player_gold):
        disguise_price = 10000
        if player_gold >= disguise_price:
            return True, player_gold - disguise_price
        return False, player_gold
