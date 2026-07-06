"""
Shop Investment & Stock Market System
- Players and NPCs can buy shares in shops
- Shops generate daily profits/losses
- Shareholders receive dividends
- Stock prices fluctuate based on performance
- Trading of shares between players and NPCs
"""

import random
import time
from logger_config import logger


class ShopStock:
    """Represents tradeable stock in a shop"""
    
    def __init__(self, shop_id, shop_name, total_shares=1000, initial_price=50):
        self.shop_id = shop_id
        self.shop_name = shop_name
        self.total_shares = total_shares
        self.available_shares = total_shares  # Shares available for purchase
        self.share_price = initial_price
        
        # Shareholders {owner_id: shares_owned}
        self.shareholders = {}
        
        # Performance tracking
        self.daily_revenue = 0
        self.daily_expenses = 0
        self.daily_profit = 0
        self.profit_history = []  # Last 7 days
        
        # Stock metrics
        self.weekly_high = initial_price
        self.weekly_low = initial_price
        self.price_change_percent = 0.0
        
        # Dividend settings
        self.dividend_rate = 0.01  # 1% of profits distributed to shareholders
        self.last_dividend_day = 0
    
    def buy_shares(self, buyer_id, quantity, price_per_share):
        """Buy shares of this shop"""
        if quantity > self.available_shares:
            return False, "Not enough shares available"
        
        cost = quantity * price_per_share
        
        # Add to shareholders
        if buyer_id not in self.shareholders:
            self.shareholders[buyer_id] = 0
        
        self.shareholders[buyer_id] += quantity
        self.available_shares -= quantity
        
        logger.info(f"[STOCK] Buyer {buyer_id} bought {quantity} shares of {self.shop_name} @ {price_per_share}g each")
        return True, f"Purchased {quantity} shares for {cost}g"
    
    def sell_shares(self, seller_id, quantity, price_per_share):
        """Sell shares back to market"""
        if seller_id not in self.shareholders:
            return False, "You don't own any shares"
        
        if self.shareholders[seller_id] < quantity:
            return False, "You don't have that many shares"
        
        revenue = quantity * price_per_share
        
        # Remove from shareholder
        self.shareholders[seller_id] -= quantity
        if self.shareholders[seller_id] <= 0:
            del self.shareholders[seller_id]
        
        self.available_shares += quantity
        
        logger.info(f"[STOCK] Seller {seller_id} sold {quantity} shares of {self.shop_name} @ {price_per_share}g each")
        return True, f"Sold {quantity} shares for {revenue}g"
    
    def update_daily_performance(self, revenue, expenses):
        """Update shop's daily financial performance"""
        self.daily_revenue = revenue
        self.daily_expenses = expenses
        self.daily_profit = revenue - expenses
        
        # Add to history
        self.profit_history.append(self.daily_profit)
        if len(self.profit_history) > 7:
            self.profit_history.pop(0)
        
        # Update stock price based on performance
        self._update_stock_price()
    
    def _update_stock_price(self):
        """Update stock price based on recent performance"""
        if not self.profit_history:
            return
        
        # Calculate average weekly profit
        avg_profit = sum(self.profit_history) / len(self.profit_history)
        
        # Price change based on profit performance
        # Positive profits increase price, losses decrease it
        if avg_profit > 0:
            # Profitable shop - price increases
            increase_percent = min(0.10, avg_profit / 10000)  # Max 10% increase per day
            self.share_price *= (1 + increase_percent)
        else:
            # Losing money - price decreases
            decrease_percent = min(0.10, abs(avg_profit) / 10000)  # Max 10% decrease per day
            self.share_price *= (1 - decrease_percent)
        
        # Add some randomness (market volatility)
        volatility = random.uniform(-0.05, 0.05)  # ±5%
        self.share_price *= (1 + volatility)
        
        # Minimum price floor
        self.share_price = max(10, self.share_price)
        
        # Update price change percentage
        if len(self.profit_history) >= 2:
            old_price = self.share_price / (1 + increase_percent if avg_profit > 0 else 1 - decrease_percent)
            self.price_change_percent = ((self.share_price - old_price) / old_price) * 100
        
        # Update weekly high/low
        self.weekly_high = max(self.weekly_high, self.share_price)
        self.weekly_low = min(self.weekly_low, self.share_price)
    
    def pay_dividends(self, current_day):
        """Pay dividends to all shareholders (weekly)"""
        if current_day - self.last_dividend_day < 7:
            return {}
        
        if not self.profit_history or sum(self.profit_history) <= 0:
            return {}  # No dividends if not profitable
        
        # Calculate total dividends to distribute
        weekly_profit = sum(self.profit_history)
        total_dividends = weekly_profit * self.dividend_rate
        
        # Calculate per-share dividend
        owned_shares = self.total_shares - self.available_shares
        if owned_shares == 0:
            return {}
        
        dividend_per_share = total_dividends / owned_shares
        
        # Distribute to shareholders
        dividends = {}
        for shareholder_id, shares in self.shareholders.items():
            dividend_amount = shares * dividend_per_share
            dividends[shareholder_id] = dividend_amount
        
        self.last_dividend_day = current_day
        
        logger.info(f"[STOCK] {self.shop_name} paid {total_dividends}g in dividends to {len(dividends)} shareholders")
        return dividends
    
    def get_ownership_percentage(self, owner_id):
        """Get percentage of shop owned by entity"""
        if owner_id not in self.shareholders:
            return 0.0
        
        return (self.shareholders[owner_id] / self.total_shares) * 100
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'shop_id': self.shop_id,
            'shop_name': self.shop_name,
            'share_price': self.share_price,
            'available_shares': self.available_shares,
            'total_shares': self.total_shares,
            'price_change': self.price_change_percent,
            'weekly_high': self.weekly_high,
            'weekly_low': self.weekly_low,
            'daily_profit': self.daily_profit,
            'shareholders_count': len(self.shareholders)
        }


class StockMarket:
    """Central stock market for all shop investments"""
    
    def __init__(self, shop_manager, game_time):
        self.shop_manager = shop_manager
        self.game_time = game_time
        
        # All tradeable stocks {shop_id: ShopStock}
        self.stocks = {}
        
        # Trading activity
        self.daily_volume = 0  # Shares traded today
        self.daily_transactions = []
        
        # Market sentiment
        self.market_sentiment = 0.5  # 0 = bearish, 1 = bullish
        
        logger.info("[STOCK MARKET] Initialized")
    
    def list_shop_on_market(self, shop_id, shop_name, total_shares=1000):
        """List a shop on the stock market (IPO)"""
        if shop_id in self.stocks:
            return False, "Shop already listed"
        
        # Calculate initial share price based on shop type
        initial_price = random.randint(30, 100)
        
        stock = ShopStock(shop_id, shop_name, total_shares, initial_price)
        self.stocks[shop_id] = stock
        
        logger.info(f"[STOCK MARKET] Listed {shop_name} - {total_shares} shares @ {initial_price}g")
        return True, f"IPO successful! {shop_name} now trading @ {initial_price}g/share"
    
    def buy_stock(self, shop_id, buyer_id, quantity, buyer_gold):
        """Buy shares of a shop"""
        if shop_id not in self.stocks:
            return False, "Shop not found on market", 0
        
        stock = self.stocks[shop_id]
        
        if quantity > stock.available_shares:
            return False, f"Only {stock.available_shares} shares available", 0
        
        cost = quantity * stock.share_price
        
        if buyer_gold < cost:
            return False, f"Need {cost}db, have {buyer_gold}db", 0
        
        success, message = stock.buy_shares(buyer_id, quantity, stock.share_price)
        
        if success:
            self.daily_volume += quantity
            self.daily_transactions.append({
                'type': 'BUY',
                'shop_id': shop_id,
                'quantity': quantity,
                'price': stock.share_price,
                'buyer_id': buyer_id
            })
        
        return success, message, cost
    
    def sell_stock(self, shop_id, seller_id, quantity):
        """Sell shares of a shop"""
        if shop_id not in self.stocks:
            return False, "Shop not found on market", 0
        
        stock = self.stocks[shop_id]
        
        success, message = stock.sell_shares(seller_id, quantity, stock.share_price)
        
        revenue = quantity * stock.share_price if success else 0
        
        if success:
            self.daily_volume += quantity
            self.daily_transactions.append({
                'type': 'SELL',
                'shop_id': shop_id,
                'quantity': quantity,
                'price': stock.share_price,
                'seller_id': seller_id
            })
        
        return success, message, revenue
    
    def update_daily(self):
        """Daily update for all stocks"""
        # Get actual shop performance from shop manager
        for shop_id, stock in self.stocks.items():
            revenue = 0
            expenses = 0
            
            # Try to get actual shop data
            if self.shop_manager and shop_id in self.shop_manager.shops:
                shop_data = self.shop_manager.shops[shop_id]
                shop = shop_data['shop']
                
                # Get financial data from shop
                financial_data = shop.get_financial_data()
                revenue = financial_data['revenue']
                expenses = financial_data['expenses']
                
                logger.info(f"[STOCK] {shop.merchant_name}: Revenue={revenue}g, Expenses={expenses}g, Profit={revenue-expenses}g, Transactions={financial_data['transactions']}")
            else:
                # Fallback to simulated performance for shops without data
                # Base revenue on shop type and market sentiment
                base_revenue = {
                    'general': (200, 800),
                    'weaponsmith': (300, 1000),
                    'armorer': (250, 900),
                    'alchemist': (300, 1100)
                }
                
                # Get shop type from stock name (rough estimate)
                shop_type = 'general'
                for shop_data in self.shop_manager.shops.values() if self.shop_manager else []:
                    if shop_data['shop'].merchant_name == stock.shop_name:
                        shop_type = shop_data['shop'].merchant_type
                        break
                
                revenue_range = base_revenue.get(shop_type, (200, 800))
                
                # Market sentiment affects revenue
                sentiment_modifier = 0.5 + (self.market_sentiment * 1.0)  # 0.5x to 1.5x
                revenue = int(random.randint(revenue_range[0], revenue_range[1]) * sentiment_modifier)
                
                # Expenses are typically 40-70% of revenue
                expense_ratio = random.uniform(0.4, 0.7)
                expenses = int(revenue * expense_ratio)
                
                logger.info(f"[STOCK] {stock.shop_name} (simulated): Revenue={revenue}g, Expenses={expenses}g, Profit={revenue-expenses}g")
            
            stock.update_daily_performance(revenue, expenses)
        
        # Update market sentiment
        self._update_market_sentiment()
        
        # Reset daily tracking
        self.daily_volume = 0
        self.daily_transactions = []
    
    def pay_weekly_dividends(self):
        """Pay dividends to all shareholders across all stocks"""
        all_dividends = {}  # {owner_id: total_dividend}
        
        for stock in self.stocks.values():
            dividends = stock.pay_dividends(self.game_time.day_count)
            
            for owner_id, amount in dividends.items():
                if owner_id not in all_dividends:
                    all_dividends[owner_id] = 0
                all_dividends[owner_id] += amount
        
        logger.info(f"[STOCK MARKET] Paid dividends to {len(all_dividends)} shareholders")
        return all_dividends
    
    def _update_market_sentiment(self):
        """Update overall market sentiment based on stock performance"""
        if not self.stocks:
            return
        
        # Calculate average profit across all stocks
        total_profit = sum(stock.daily_profit for stock in self.stocks.values())
        
        if total_profit > 0:
            self.market_sentiment = min(1.0, self.market_sentiment + 0.05)
        else:
            self.market_sentiment = max(0.0, self.market_sentiment - 0.05)
        
        # Add randomness
        self.market_sentiment += random.uniform(-0.02, 0.02)
        self.market_sentiment = max(0.0, min(1.0, self.market_sentiment))
    
    def get_market_status(self):
        """Get overall market status"""
        if not self.stocks:
            return "No stocks listed"
        
        avg_change = sum(s.price_change_percent for s in self.stocks.values()) / len(self.stocks)
        
        if avg_change > 2:
            return "🟢 BULLISH"
        elif avg_change < -2:
            return "🔴 BEARISH"
        else:
            return "🟡 STABLE"
    
    def get_player_portfolio(self, player_id):
        """Get all stocks owned by player"""
        portfolio = []
        total_value = 0
        
        for shop_id, stock in self.stocks.items():
            if player_id in stock.shareholders:
                shares = stock.shareholders[player_id]
                value = shares * stock.share_price
                ownership = stock.get_ownership_percentage(player_id)
                
                portfolio.append({
                    'shop_name': stock.shop_name,
                    'shop_id': shop_id,
                    'shares': shares,
                    'current_value': value,
                    'ownership_percent': ownership,
                    'share_price': stock.share_price,
                    'price_change': stock.price_change_percent
                })
                
                total_value += value
        
        return portfolio, total_value
    
    def get_top_stocks(self, limit=10):
        """Get top performing stocks"""
        stock_list = [(shop_id, stock) for shop_id, stock in self.stocks.items()]
        stock_list.sort(key=lambda x: x[1].price_change_percent, reverse=True)
        
        return [stock.to_dict() for _, stock in stock_list[:limit]]
    
    def get_all_stocks(self):
        """Get all available stocks"""
        return [stock.to_dict() for stock in self.stocks.values()]


class NPCInvestor:
    """NPC that invests in shops and trades stocks"""
    
    def __init__(self, npc):
        self.npc = npc
        self.portfolio = {}  # {shop_id: shares_owned}
        self.investment_strategy = random.choice(['conservative', 'balanced', 'aggressive'])
        self.last_trade_day = 0
        
    def should_invest(self, game_time):
        """Check if NPC should make investment decision"""
        if game_time.day_count - self.last_trade_day < 3:
            return False
        
        if not hasattr(self.npc, 'dubloons'):
            return False
        
        # Need capital to invest
        min_capital = {'conservative': 1000, 'balanced': 500, 'aggressive': 200}
        return self.npc.dubloons >= min_capital.get(self.investment_strategy, 500)
    
    def make_investment_decision(self, stock_market, game_time):
        """NPC decides whether to buy or sell stocks"""
        if not self.should_invest(game_time):
            return
        
        # 50% chance to buy, 50% chance to sell
        if random.random() < 0.5:
            self._attempt_buy(stock_market)
        else:
            self._attempt_sell(stock_market)
        
        self.last_trade_day = game_time.day_count
    
    def _attempt_buy(self, stock_market):
        """Attempt to buy stocks"""
        # Find stocks with good performance
        stocks = stock_market.get_top_stocks(5)
        
        if not stocks:
            return
        
        # Pick a stock based on strategy
        if self.investment_strategy == 'conservative':
            # Buy stable, low-volatility stocks
            target_stock = stocks[-1]  # Least volatile
        elif self.investment_strategy == 'aggressive':
            # Buy high-growth stocks
            target_stock = stocks[0]  # Highest growth
        else:
            # Balanced - random from top performers
            target_stock = random.choice(stocks)
        
        # Calculate quantity to buy
        max_investment = self.npc.dubloons * 0.1  # Invest max 10% of capital
        quantity = int(max_investment / target_stock['share_price'])
        
        if quantity > 0:
            success, message, cost = stock_market.buy_stock(
                target_stock['shop_id'], 
                id(self.npc), 
                quantity, 
                self.npc.dubloons
            )
            
            if success:
                self.npc.dubloons -= cost
                self.portfolio[target_stock['shop_id']] = self.portfolio.get(target_stock['shop_id'], 0) + quantity
                logger.info(f"[INVESTOR] {self.npc.name} bought {quantity} shares of {target_stock['shop_name']}")
    
    def _attempt_sell(self, stock_market):
        """Attempt to sell stocks"""
        if not self.portfolio:
            return
        
        # Find stocks that have grown enough to sell
        for shop_id, shares in list(self.portfolio.items()):
            if shop_id in stock_market.stocks:
                stock = stock_market.stocks[shop_id]
                
                # Sell if price has changed significantly
                if stock.price_change_percent > 5 or stock.price_change_percent < -5:
                    success, message, revenue = stock_market.sell_stock(shop_id, id(self.npc), shares)
                    
                    if success:
                        self.npc.dubloons += revenue
                        del self.portfolio[shop_id]
                        logger.info(f"[INVESTOR] {self.npc.name} sold {shares} shares of {stock.shop_name} for {revenue}g")
                        break


class InvestmentSystem:
    """Central system managing all investments"""
    
    def __init__(self, shop_manager, game_time):
        self.stock_market = StockMarket(shop_manager, game_time)
        self.npc_investors = {}  # {npc_id: NPCInvestor}
        self.game_time = game_time
    
    def initialize_market(self, shop_manager):
        """List all shops on the stock market"""
        if not hasattr(shop_manager, 'shops'):
            return
        
        for shop_id, shop_data in shop_manager.shops.items():
            if 'shop' in shop_data:
                shop_name = shop_data['shop'].merchant_name
                self.stock_market.list_shop_on_market(shop_id, shop_name)
        
        logger.info(f"[INVESTMENT] Listed {len(self.stock_market.stocks)} shops on market")
    
    def register_npc_investor(self, npc):
        """Register an NPC as a potential investor"""
        npc_id = id(npc)
        if npc_id not in self.npc_investors:
            self.npc_investors[npc_id] = NPCInvestor(npc)
    
    def update_daily(self):
        """Daily update for investment system"""
        # Update stock prices
        self.stock_market.update_daily()
        
        # NPCs make investment decisions
        for npc_id, investor in self.npc_investors.items():
            investor.make_investment_decision(self.stock_market, self.game_time)
    
    def update_weekly(self):
        """Weekly update - pay dividends"""
        dividends = self.stock_market.pay_weekly_dividends()
        
        # Distribute dividends to recipients
        for owner_id, amount in dividends.items():
            # Check if owner is NPC
            if owner_id in self.npc_investors:
                investor = self.npc_investors[owner_id]
                if hasattr(investor.npc, 'dubloons'):
                    investor.npc.dubloons += amount
                    logger.info(f"[DIVIDEND] {investor.npc.name} received {amount}g dividend")
    
    def get_statistics(self):
        """Get investment system statistics"""
        return {
            'total_stocks': len(self.stock_market.stocks),
            'market_status': self.stock_market.get_market_status(),
            'market_sentiment': self.stock_market.market_sentiment,
            'daily_volume': self.stock_market.daily_volume,
            'npc_investors': len(self.npc_investors)
        }
