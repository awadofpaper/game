"""
Merchant Feedback System
Provides dynamic merchant comments and reactions for immersion
"""

import random
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class MerchantFeedbackSystem:
    """Manages dynamic merchant comments and reactions"""
    
    def __init__(self):
        self.last_comment = ""
        self.comment_cooldown = 0
        
        # Comment templates organized by context
        self.greeting_comments = {
            'novice': [  # Merchant skill 1-24
                "Welcome! First time trading?",
                "Hello there, new customer!",
                "Ah, a fresh face! Let me show you what we have.",
                "Welcome! Don't be shy, take a look around.",
                "Greetings! Let me know if you need help finding anything."
            ],
            'apprentice': [  # Merchant skill 25-49
                "Ah, back again I see!",
                "Welcome back, friend!",
                "Good to see a familiar face!",
                "You're becoming quite the regular!",
                "Pleasure doing business with you again!"
            ],
            'skilled': [  # Merchant skill 50-74
                "Ah, a seasoned trader! Welcome!",
                "Good day! I have some rare items that might interest you.",
                "Welcome! Your reputation precedes you.",
                "Greetings, merchant! Let's make a deal.",
                "Always a pleasure to trade with a professional!"
            ],
            'expert': [  # Merchant skill 75-89
                "Master trader! An honor to serve you!",
                "Ah! Let me get my finest wares for you!",
                "Your expertise is well known here!",
                "Welcome! I've been saving some treasures for you.",
                "A true merchant! Let's discuss serious business."
            ],
            'master': [  # Merchant skill 90+
                "Grandmaster of trade! Your presence honors my shop!",
                "Ah, a legend walks into my humble establishment!",
                "Your trading prowess is spoken of throughout the land!",
                "Master! I have exclusive items worthy of your skill!",
                "The finest trader in all the realm! Welcome!"
            ]
        }
        
        self.buying_comments = {
            'cheap_item': [  # <50g
                "A fine choice for the price!",
                "Good value, this one!",
                "You won't find better at this price!",
                "Practical and affordable!",
                "A wise purchase!"
            ],
            'moderate_item': [  # 50-200g
                "Excellent choice! This will serve you well.",
                "Quality goods at a fair price!",
                "You have a good eye for value!",
                "One of our better items!",
                "This has served many adventurers well!"
            ],
            'expensive_item': [  # 200-1000g
                "Ah, one of our premium items!",
                "Excellent taste! This is top quality!",
                "You know quality when you see it!",
                "A significant investment, but worth every coin!",
                "This is among my finest wares!"
            ],
            'luxury_item': [  # >1000g
                "A purchase fit for nobility!",
                "Truly exceptional! You have exquisite taste!",
                "This is a once-in-a-lifetime item!",
                "I rarely sell items of this caliber!",
                "Your wealth matches your wisdom!"
            ]
        }
        
        self.selling_comments = {
            'junk': [  # Low value/broken items
                "I'll take it off your hands, I suppose...",
                "Not much, but I can use it for parts.",
                "I might be able to sell this... eventually.",
                "Well, every bit helps, I suppose.",
                "Hmm, I'll add it to the bargain bin."
            ],
            'common': [  # Common items
                "I can always use more of these.",
                "Fair enough, I'll take it.",
                "These sell reasonably well.",
                "Good, I was running low on these!",
                "Thank you, this will restock my shelves."
            ],
            'rare': [  # Rare/valuable items
                "Oh my! Where did you find this?",
                "Excellent! This will fetch a good price!",
                "I haven't seen one of these in years!",
                "My customers will love this!",
                "This is quite valuable! Well done!"
            ],
            'legendary': [  # Legendary/exotic items
                "By the gods! Is that...?!",
                "Incredible! This belongs in a museum!",
                "How did you acquire such a treasure?!",
                "I can't believe my eyes! This is priceless!",
                "Word of this will spread throughout the land!"
            ],
            'bulk': [  # Selling many items
                "Quite the haul! Let me get my counting board.",
                "Business is good for you, I see!",
                "This will take a moment to tally up...",
                "My coffers will be lighter after this!",
                "You've been busy! Impressive!"
            ]
        }
        
        self.haggling_comments = {
            'success': [
                "Alright, alright! You drive a hard bargain!",
                "You're good at this... deal!",
                "Very well, I can accept that.",
                "Your negotiation skills are impressive!",
                "Fine, but don't tell my other customers!",
                "You've bested me. We have a deal.",
                "I can't say no to that. Agreed!"
            ],
            'failure': [
                "I'm sorry, but I can't go that low.",
                "That's simply not possible, friend.",
                "I'd be losing money at that price!",
                "My final offer stands.",
                "I have a business to run, you know!",
                "That's asking too much, I'm afraid.",
                "I can't accept that, my apologies."
            ],
            'annoyed': [  # Multiple failed attempts
                "Please, I've already given my best price!",
                "Enough! This is my final offer!",
                "You're testing my patience now...",
                "I won't budge further. Take it or leave it.",
                "This haggling is going nowhere!",
                "I'm a merchant, not a charity!"
            ],
            'player_overpaying': [
                "Are you sure? That's more than the asking price!",
                "I won't argue with generosity!",
                "Well, if you insist! Much appreciated!",
                "Your generosity is noted and appreciated!",
                "Thank you kindly! You're too generous!"
            ]
        }
        
        self.appraisal_comments = {
            'low_skill': [  # Player has low appraisal skill
                "I can examine this for you, for a small fee...",
                "This appears to be... well, I'm not entirely certain.",
                "Let me take a closer look at this...",
                "Hmm, interesting piece. Hard to value exactly.",
                "Give me a moment to assess this properly..."
            ],
            'high_skill': [  # Player has high skill
                "Ah, you already know what this is worth, don't you?",
                "No need to examine this - you know your goods!",
                "A practiced eye! You know value when you see it.",
                "Clearly you don't need my assessment!",
                "You could appraise this better than I could!"
            ],
            'rare_item': [
                "This is extraordinary! Very rare indeed!",
                "I've only seen one of these once before!",
                "This is worth a small fortune!",
                "The craftsmanship is exquisite!",
                "This is museum-quality!"
            ],
            'cursed_item': [
                "Wait... there's something wrong with this...",
                "I sense dark magic about this item.",
                "Be careful with this one - it feels... off.",
                "This has a troubling aura...",
                "I'd recommend not using this..."
            ]
        }
        
        self.reputation_comments = {
            'hostile': [
                "I suppose I must serve you... *sigh*",
                "Make it quick.",
                "I'm watching you carefully...",
                "Don't try anything funny.",
                "Pay upfront. I don't trust you."
            ],
            'unfriendly': [
                "What do you want?",
                "Yes? What is it?",
                "I'm busy. Make it quick.",
                "State your business.",
                "I hope you're not here to cause trouble."
            ],
            'friendly': [
                "Always happy to see you!",
                "My friend! What can I do for you?",
                "Good to see a trusted customer!",
                "Welcome back! I've missed our trades!",
                "You're always welcome here!"
            ],
            'honored': [
                "Your patronage is an honor!",
                "My doors are always open to you!",
                "For you, I have special items!",
                "Please, take your time browsing!",
                "I've set aside some items just for you!"
            ]
        }
        
        self.time_based_comments = {
            'morning': [
                "Good morning! Fresh stock just arrived!",
                "Early bird gets the best deals!",
                "Starting the day with business - excellent!",
                "Morning! Coffee's brewing if you'd like some.",
                "You're my first customer today!"
            ],
            'afternoon': [
                "Good afternoon! Business is steady today.",
                "Afternoon! Take a look at what's left.",
                "Welcome! The lunch crowd just cleared out.",
                "Perfect timing - just restocked!",
                "Afternoon! How can I help you?"
            ],
            'evening': [
                "Good evening! Winding down for the day.",
                "Evening! I'll be closing soon, but take your time.",
                "Late shopper, eh? I like your style!",
                "Almost closing time, but you're welcome!",
                "Evening! Looking for anything specific?"
            ],
            'night': [
                "Open late for special customers!",
                "Midnight trading! My favorite!",
                "Couldn't sleep either? Let's trade!",
                "Late night deals for night owls!",
                "Welcome! Not many shop at this hour."
            ]
        }
        
        self.special_comments = {
            'first_purchase': [
                "Ah, your first purchase! I'll remember you!",
                "Welcome to the world of commerce!",
                "Every great merchant starts somewhere!",
                "Your first trade - how exciting!",
                "The beginning of a profitable relationship!"
            ],
            'repeat_customer': [
                "Back again? I like your style!",
                "You're becoming one of my best customers!",
                "Always a pleasure!",
                "I should offer you a loyalty discount!",
                "You know quality when you see it!"
            ],
            'poor_player': [  # Player has little money
                "Don't worry, I have some affordable options!",
                "Every coin counts - I understand!",
                "Let me show you what's in your price range.",
                "Hard times? These might help you get back on your feet.",
                "I remember those days... take a look at these."
            ],
            'rich_player': [  # Player has lots of money
                "Ah, let me show you my premium collection!",
                "I can see you appreciate the finer things!",
                "For someone of your means, I have something special...",
                "Your success is evident! Have you considered...?",
                "Let me get my exclusive catalog!"
            ],
            'festival': [
                "Festival prices! Everything must go!",
                "Special event discounts today!",
                "Celebrating with special deals!",
                "Festival special - you picked a great time!",
                "Holiday prices - enjoy!"
            ]
        }
        
        self.item_quality_comments = {
            'broken': [
                "This is in rough shape...",
                "Barely functional, I'm afraid.",
                "Would need serious repairs...",
                "It's seen better days, that's for sure.",
                "I can offer scrap value at best."
            ],
            'damaged': [
                "Shows some wear and tear.",
                "Could use some maintenance.",
                "Still functional, but needs work.",
                "Definitely used, but salvageable.",
                "A bit rough around the edges."
            ],
            'excellent': [
                "In pristine condition!",
                "Like new! Excellent!",
                "Hardly used at all!",
                "The craftsmanship is superb!",
                "Mint condition! Wonderful!"
            ],
            'masterwork': [
                "This is a work of art!",
                "Master-crafted! Incredible!",
                "I've never seen better quality!",
                "The maker was a true artisan!",
                "This is perfection itself!"
            ]
        }
        
    def get_greeting(self, merchant_skill: int) -> str:
        """Get greeting based on player's merchant skill"""
        if merchant_skill < 25:
            tier = 'novice'
        elif merchant_skill < 50:
            tier = 'apprentice'
        elif merchant_skill < 75:
            tier = 'skilled'
        elif merchant_skill < 90:
            tier = 'expert'
        else:
            tier = 'master'
            
        return random.choice(self.greeting_comments[tier])
    
    def get_buying_comment(self, price: int, merchant_skill: int = 0) -> str:
        """Get comment for buying an item"""
        if price < 50:
            tier = 'cheap_item'
        elif price < 200:
            tier = 'moderate_item'
        elif price < 1000:
            tier = 'expensive_item'
        else:
            tier = 'luxury_item'
            
        comment = random.choice(self.buying_comments[tier])
        
        # High skill merchants might add extra comments
        if merchant_skill >= 75 and random.random() < 0.3:
            comment += " You clearly know what you're looking for!"
            
        return comment
    
    def get_selling_comment(self, item_value: int, item_rarity: str = 'common', 
                           quantity: int = 1) -> str:
        """Get comment for selling an item"""
        if quantity > 10:
            tier = 'bulk'
        elif item_value < 20:
            tier = 'junk'
        elif item_rarity in ['legendary', 'exotic', 'mythic']:
            tier = 'legendary'
        elif item_rarity in ['rare', 'epic']:
            tier = 'rare'
        else:
            tier = 'common'
            
        return random.choice(self.selling_comments[tier])
    
    def get_haggling_comment(self, success: bool, attempts: int = 1, 
                            overpaying: bool = False) -> str:
        """Get comment for haggling attempt"""
        if overpaying:
            return random.choice(self.haggling_comments['player_overpaying'])
        elif success:
            return random.choice(self.haggling_comments['success'])
        elif attempts >= 3:
            return random.choice(self.haggling_comments['annoyed'])
        else:
            return random.choice(self.haggling_comments['failure'])
    
    def get_appraisal_comment(self, appraisal_skill: int, item_rarity: str = 'common',
                             is_cursed: bool = False) -> str:
        """Get comment for item appraisal"""
        if is_cursed:
            return random.choice(self.appraisal_comments['cursed_item'])
        elif item_rarity in ['legendary', 'exotic', 'rare', 'epic']:
            return random.choice(self.appraisal_comments['rare_item'])
        elif appraisal_skill >= 75:
            return random.choice(self.appraisal_comments['high_skill'])
        else:
            return random.choice(self.appraisal_comments['low_skill'])
    
    def get_reputation_comment(self, reputation_tier: str) -> str:
        """Get comment based on reputation"""
        tier_map = {
            'Hostile': 'hostile',
            'Unfriendly': 'unfriendly',
            'Neutral': None,  # Use standard greeting
            'Friendly': 'friendly',
            'Honored': 'honored',
            'Revered': 'honored'
        }
        
        tier = tier_map.get(reputation_tier)
        if tier and tier in self.reputation_comments:
            return random.choice(self.reputation_comments[tier])
        return ""
    
    def get_time_comment(self, hour: int) -> str:
        """Get time-of-day comment"""
        if 6 <= hour < 12:
            tier = 'morning'
        elif 12 <= hour < 17:
            tier = 'afternoon'
        elif 17 <= hour < 22:
            tier = 'evening'
        else:
            tier = 'night'
            
        return random.choice(self.time_based_comments[tier])
    
    def get_special_comment(self, context: str, player_gold: int = 0) -> str:
        """Get special contextual comment"""
        if context == 'poor_player' and player_gold < 100:
            return random.choice(self.special_comments['poor_player'])
        elif context == 'rich_player' and player_gold > 10000:
            return random.choice(self.special_comments['rich_player'])
        elif context in self.special_comments:
            return random.choice(self.special_comments[context])
        return ""
    
    def get_quality_comment(self, condition_name: str) -> str:
        """Get comment about item quality/condition"""
        if condition_name in ['Broken', 'Damaged']:
            tier = condition_name.lower()
        elif condition_name in ['Excellent', 'Fine']:
            tier = 'excellent'
        elif condition_name in ['Masterwork', 'Legendary']:
            tier = 'masterwork'
        else:
            return ""
            
        if tier in self.item_quality_comments:
            return random.choice(self.item_quality_comments[tier])
        return ""
    
    def get_contextual_comment(self, context: Dict) -> str:
        """
        Get a contextual comment based on multiple factors
        
        Context dict can include:
        - action: 'greeting', 'buying', 'selling', 'haggling', 'appraisal'
        - merchant_skill: player's merchant skill level
        - price: item price
        - item_rarity: item rarity
        - item_condition: item condition name
        - reputation: reputation tier
        - hour: current hour (0-23)
        - player_gold: player's current gold
        - quantity: number of items
        - success: haggling success
        - attempts: haggling attempts
        """
        action = context.get('action', 'greeting')
        
        if action == 'greeting':
            merchant_skill = context.get('merchant_skill', 0)
            base_comment = self.get_greeting(merchant_skill)
            
            # Maybe add reputation comment
            if context.get('reputation') and random.random() < 0.4:
                rep_comment = self.get_reputation_comment(context['reputation'])
                if rep_comment:
                    return rep_comment
                    
            return base_comment
            
        elif action == 'buying':
            price = context.get('price', 0)
            merchant_skill = context.get('merchant_skill', 0)
            return self.get_buying_comment(price, merchant_skill)
            
        elif action == 'selling':
            item_value = context.get('price', 0)
            item_rarity = context.get('item_rarity', 'common')
            quantity = context.get('quantity', 1)
            comment = self.get_selling_comment(item_value, item_rarity, quantity)
            
            # Maybe add quality comment
            if context.get('item_condition') and random.random() < 0.5:
                quality_comment = self.get_quality_comment(context['item_condition'])
                if quality_comment:
                    comment += " " + quality_comment
                    
            return comment
            
        elif action == 'haggling':
            success = context.get('success', False)
            attempts = context.get('attempts', 1)
            overpaying = context.get('overpaying', False)
            return self.get_haggling_comment(success, attempts, overpaying)
            
        elif action == 'appraisal':
            appraisal_skill = context.get('merchant_skill', 0)
            item_rarity = context.get('item_rarity', 'common')
            is_cursed = context.get('is_cursed', False)
            return self.get_appraisal_comment(appraisal_skill, item_rarity, is_cursed)
            
        return ""
    
    def should_show_comment(self) -> bool:
        """Check if enough time has passed to show another comment"""
        if self.comment_cooldown > 0:
            self.comment_cooldown -= 1
            return False
        return True
    
    def set_cooldown(self, frames: int = 180):
        """Set comment cooldown (default 3 seconds at 60fps)"""
        self.comment_cooldown = frames
    
    def format_comment(self, comment: str, merchant_name: str = "Merchant") -> str:
        """Format comment with merchant name"""
        return f"[{merchant_name}] {comment}"


# Global instance for easy access
merchant_feedback = MerchantFeedbackSystem()
