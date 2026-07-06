"""
Consignment and Auction System
Leave items at shops to sell over time, bid on rare items
"""

import random
from typing import Dict, List, Optional, Tuple
from logger_config import logger


class ConsignmentItem:
    """An item left at a shop for consignment"""
    
    def __init__(self, item_id: str, item_name: str, quantity: int,
                 asking_price: int, shop_id: str, day_listed: int):
        self.item_id = item_id
        self.item_name = item_name
        self.quantity = quantity
        self.asking_price = asking_price  # Per unit
        self.shop_id = shop_id
        self.day_listed = day_listed
        self.quantity_sold = 0
        
        # Shop takes 10% commission
        self.commission_rate = 0.10
        
    def get_net_price(self) -> int:
        """Get price after shop commission"""
        return int(self.asking_price * (1.0 - self.commission_rate))
    
    def attempt_sale(self, game_time) -> Tuple[int, int]:
        """
        Attempt to sell some quantity
        Returns (quantity_sold, gold_earned)
        """
        remaining = self.quantity - self.quantity_sold
        if remaining <= 0:
            return 0, 0
        
        # Sell 0-2 items per day based on price reasonableness
        # Lower prices = faster sales
        sell_chance = random.random()
        if sell_chance < 0.3:  # 30% chance per day
            qty_to_sell = min(random.randint(1, 2), remaining)
            self.quantity_sold += qty_to_sell
            gold_earned = qty_to_sell * self.get_net_price()
            logger.info(f"[CONSIGNMENT] Sold {qty_to_sell}x {self.item_name} for {gold_earned}g")
            return qty_to_sell, gold_earned
        
        return 0, 0
    
    def is_fully_sold(self) -> bool:
        """Check if all items have sold"""
        return self.quantity_sold >= self.quantity
    
    def days_listed(self, current_day: int) -> int:
        """Get number of days item has been listed"""
        return current_day - self.day_listed


class AuctionItem:
    """An item up for auction"""
    
    def __init__(self, item_id: str, item_name: str, description: str,
                 starting_bid: int, buyout_price: int, end_day: int, seller: str = 'npc'):
        self.item_id = item_id
        self.item_name = item_name
        self.description = description
        self.starting_bid = starting_bid
        self.current_bid = starting_bid
        self.buyout_price = buyout_price
        self.end_day = end_day
        self.seller = seller  # 'player' or 'npc'
        
        self.current_bidder = None
        self.bid_history = []  # List of (bidder, amount, day)
        self.sold = False
        
    def place_bid(self, bidder: str, amount: int, current_day: int) -> Tuple[bool, str]:
        """
        Place a bid on the item
        Returns (success, message)
        """
        if self.sold:
            return False, "Auction has ended!"
        
        if current_day >= self.end_day:
            return False, "Auction has expired!"
        
        if amount < self.current_bid + 10:  # Minimum 10g increment
            return False, f"Bid must be at least {self.current_bid + 10}g!"
        
        if amount >= self.buyout_price:
            # Instant buyout
            self.current_bid = self.buyout_price
            self.current_bidder = bidder
            self.sold = True
            self.bid_history.append((bidder, amount, current_day))
            logger.info(f"[AUCTION] {bidder} bought out {self.item_name} for {amount}g")
            return True, f"Buyout successful! You won the {self.item_name} for {amount}g!"
        
        # Regular bid
        self.current_bid = amount
        self.current_bidder = bidder
        self.bid_history.append((bidder, amount, current_day))
        logger.info(f"[AUCTION] {bidder} bid {amount}g on {self.item_name}")
        return True, f"Bid placed! Current bid: {amount}g"
    
    def finalize_auction(self, current_day: int) -> Tuple[bool, Optional[str], int]:
        """
        Finalize the auction
        Returns (sold, winner, final_price)
        """
        if current_day < self.end_day and not self.sold:
            return False, None, 0
        
        if self.current_bidder:
            self.sold = True
            return True, self.current_bidder, self.current_bid
        
        return False, None, 0
    
    def time_remaining(self, current_day: int) -> int:
        """Get days remaining in auction"""
        return max(0, self.end_day - current_day)


class ConsignmentAuctionSystem:
    """Manages consignment sales and auctions"""
    
    def __init__(self, game_time):
        self.game_time = game_time
        self.consignment_items: Dict[str, List[ConsignmentItem]] = {}  # shop_id → items
        self.auction_items: Dict[str, AuctionItem] = {}  # auction_id → item
        self.player_earnings = 0  # Total earned from consignment
        self.npc_bidders = [
            'Wealthy Collector',
            'Noble Lord',
            'Mysterious Buyer',
            'Adventurer Guild',
            'Merchant Consortium'
        ]
        
    def list_item_for_consignment(self, item_id: str, item_name: str,
                                  quantity: int, asking_price: int,
                                  shop_id: str, player) -> Tuple[bool, str]:
        """
        List an item for consignment at a shop
        Returns (success, message)
        """
        # Check if player has the item
        if not hasattr(player, 'inventory'):
            return False, "No inventory!"
        
        if player.inventory.get(item_id, 0) < quantity:
            return False, f"You don't have {quantity}x {item_name}!"
        
        # Remove from player inventory
        player.inventory[item_id] -= quantity
        if player.inventory[item_id] <= 0:
            del player.inventory[item_id]
        
        # Create consignment item
        consignment = ConsignmentItem(
            item_id, item_name, quantity, asking_price,
            shop_id, self.game_time.day_count
        )
        
        if shop_id not in self.consignment_items:
            self.consignment_items[shop_id] = []
        
        self.consignment_items[shop_id].append(consignment)
        
        commission_pct = int(consignment.commission_rate * 100)
        logger.info(f"[CONSIGNMENT] Listed {quantity}x {item_name} for {asking_price}g each at {shop_id}")
        return True, f"Listed {quantity}x {item_name} for consignment at {asking_price}g each ({commission_pct}% shop fee)"
    
    def get_player_consignments(self, shop_id: str = None) -> List[ConsignmentItem]:
        """Get player's consignment items"""
        if shop_id:
            return self.consignment_items.get(shop_id, [])
        
        # All consignments
        all_items = []
        for items in self.consignment_items.values():
            all_items.extend(items)
        return all_items
    
    def collect_consignment_earnings(self, shop_id: str) -> Tuple[int, List[str]]:
        """
        Collect earnings from sold consignment items
        Returns (total_gold, messages)
        """
        if shop_id not in self.consignment_items:
            return 0, []
        
        total = 0
        messages = []
        items_to_remove = []
        
        for consignment in self.consignment_items[shop_id]:
            if consignment.quantity_sold > 0:
                earnings = consignment.quantity_sold * consignment.get_net_price()
                total += earnings
                messages.append(
                    f"Sold {consignment.quantity_sold}/{consignment.quantity}x "
                    f"{consignment.item_name} for {earnings}g"
                )
                
                # If fully sold, mark for removal
                if consignment.is_fully_sold():
                    items_to_remove.append(consignment)
                else:
                    # Reset sold count after collection
                    consignment.quantity_sold = 0
        
        # Remove fully sold items
        for item in items_to_remove:
            self.consignment_items[shop_id].remove(item)
        
        if total > 0:
            self.player_earnings += total
            logger.info(f"[CONSIGNMENT] Player collected {total}g from {shop_id}")
        
        return total, messages
    
    def create_auction(self, item_id: str, item_name: str, description: str,
                      starting_bid: int, buyout_price: int, duration_days: int,
                      seller: str = 'npc') -> str:
        """
        Create a new auction
        Returns auction_id
        """
        auction_id = f"auction_{len(self.auction_items)}_{self.game_time.day_count}"
        end_day = self.game_time.day_count + duration_days
        
        auction = AuctionItem(
            item_id, item_name, description,
            starting_bid, buyout_price, end_day, seller
        )
        
        self.auction_items[auction_id] = auction
        logger.info(f"[AUCTION] Created auction for {item_name}, ends day {end_day}")
        return auction_id
    
    def get_active_auctions(self) -> List[Tuple[str, AuctionItem]]:
        """Get all active auctions"""
        active = []
        
        for auction_id, auction in self.auction_items.items():
            if not auction.sold and auction.time_remaining(self.game_time.day_count) > 0:
                active.append((auction_id, auction))
        
        return active
    
    def place_bid(self, auction_id: str, bidder: str, amount: int) -> Tuple[bool, str]:
        """Place a bid on an auction"""
        if auction_id not in self.auction_items:
            return False, "Auction not found!"
        
        auction = self.auction_items[auction_id]
        return auction.place_bid(bidder, amount, self.game_time.day_count)
    
    def npc_bidding_activity(self):
        """NPCs place bids on auctions"""
        active_auctions = self.get_active_auctions()
        
        for auction_id, auction in active_auctions:
            # 30% chance NPC bids each day
            if random.random() < 0.3:
                npc_bidder = random.choice(self.npc_bidders)
                # NPC bids 10-30% over current bid
                bid_increase = int(auction.current_bid * random.uniform(0.1, 0.3))
                bid_amount = auction.current_bid + bid_increase
                
                # Don't exceed buyout
                if bid_amount >= auction.buyout_price:
                    bid_amount = auction.buyout_price
                
                auction.place_bid(npc_bidder, bid_amount, self.game_time.day_count)
    
    def daily_update(self):
        """Called each day to update consignments and auctions"""
        # Process consignment sales
        for shop_id, items in self.consignment_items.items():
            for item in items:
                item.attempt_sale(self.game_time)
        
        # NPCs bid on auctions
        self.npc_bidding_activity()
        
        # Finalize ended auctions
        to_remove = []
        for auction_id, auction in self.auction_items.items():
            if auction.time_remaining(self.game_time.day_count) <= 0 and not auction.sold:
                sold, winner, price = auction.finalize_auction(self.game_time.day_count)
                if sold:
                    logger.info(f"[AUCTION] {auction.item_name} won by {winner} for {price}g")
                else:
                    logger.info(f"[AUCTION] {auction.item_name} auction ended with no winner")
                    to_remove.append(auction_id)
        
        # Remove unsold auctions after 7 days
        for auction_id in to_remove:
            del self.auction_items[auction_id]
    
    def get_auction_house_items(self) -> List[dict]:
        """Get formatted list of auction items for display"""
        items = []
        
        for auction_id, auction in self.get_active_auctions():
            items.append({
                'auction_id': auction_id,
                'item_name': auction.item_name,
                'description': auction.description,
                'current_bid': auction.current_bid,
                'buyout_price': auction.buyout_price,
                'current_bidder': auction.current_bidder or 'None',
                'time_remaining': auction.time_remaining(self.game_time.day_count),
                'seller': auction.seller
            })
        
        return items
    
    def to_dict(self) -> dict:
        """Serialize"""
        return {
            'consignment_items': {
                shop_id: [
                    {
                        'item_id': item.item_id,
                        'item_name': item.item_name,
                        'quantity': item.quantity,
                        'asking_price': item.asking_price,
                        'day_listed': item.day_listed,
                        'quantity_sold': item.quantity_sold
                    }
                    for item in items
                ]
                for shop_id, items in self.consignment_items.items()
            },
            'auction_items': {
                auction_id: {
                    'item_id': auction.item_id,
                    'item_name': auction.item_name,
                    'description': auction.description,
                    'starting_bid': auction.starting_bid,
                    'current_bid': auction.current_bid,
                    'buyout_price': auction.buyout_price,
                    'end_day': auction.end_day,
                    'seller': auction.seller,
                    'current_bidder': auction.current_bidder,
                    'bid_history': auction.bid_history,
                    'sold': auction.sold
                }
                for auction_id, auction in self.auction_items.items()
            },
            'player_earnings': self.player_earnings
        }
    
    def from_dict(self, data: dict):
        """Deserialize"""
        # Restore consignment items
        for shop_id, items_data in data.get('consignment_items', {}).items():
            items = []
            for item_data in items_data:
                item = ConsignmentItem(
                    item_data['item_id'],
                    item_data['item_name'],
                    item_data['quantity'],
                    item_data['asking_price'],
                    shop_id,
                    item_data['day_listed']
                )
                item.quantity_sold = item_data.get('quantity_sold', 0)
                items.append(item)
            self.consignment_items[shop_id] = items
        
        # Restore auction items
        for auction_id, auction_data in data.get('auction_items', {}).items():
            auction = AuctionItem(
                auction_data['item_id'],
                auction_data['item_name'],
                auction_data['description'],
                auction_data['starting_bid'],
                auction_data['buyout_price'],
                auction_data['end_day'],
                auction_data.get('seller', 'npc')
            )
            auction.current_bid = auction_data.get('current_bid', auction.starting_bid)
            auction.current_bidder = auction_data.get('current_bidder')
            auction.bid_history = auction_data.get('bid_history', [])
            auction.sold = auction_data.get('sold', False)
            self.auction_items[auction_id] = auction
        
        self.player_earnings = data.get('player_earnings', 0)
