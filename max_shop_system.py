"""
MaXxS Silicon Dioxide Shop - A parody of predatory microtransaction systems

Features Max, a suspicious NPC who sells overpriced loot boxes filled with
cosmetics that provide absolutely no gameplay advantage.
"""

import random
from typing import Dict, List, Tuple, Optional, Any
from cosmetic_system import CosmeticGenerator, CosmeticManager


class MaxDialogue:
    """Handles Max's dialogue with complex branching based on player state"""
    
    # The opening greeting (always the same)
    INITIAL_GREETING = "hehehe another unsuspec........ OH sorry I didnt see you there, welcome to MaXxS Silicon Dioxide Shop. Max that's me the extra X is for Xtremley STUp.....SMART Xtremley smart"
    
    # Player dialogue choices after greeting
    PLAYER_CHOICE_RUDE = "uhhh wow you are probably the rudest fucking person I've met so far."
    PLAYER_CHOICE_SARCASTIC = "ok i guess thats one way to greet *looks around*, your literal only customer. what is it you do here anyway?"
    PLAYER_CHOICE_SPECIAL = "special"  # For mayor/business/family
    
    # Max's responses to rude comment (if player is criminal)
    MAX_RESPONSE_TO_CRIMINAL = "Yah well at least I don't go around acting like a Monster raping and killing whoever I want because I have aboslutley no self control over my impluses, now do you want to get on with this or do you want fuck off?"
    
    # Player options after Max's criminal response
    PLAYER_YES_WHAT_DO_YOU_DO = "Yes, what do you even do here"
    PLAYER_NO_FUCK_OFF = "No, not the way you talk to your customers dickhead"
    
    # New sarcastic path dialogue
    MAX_HAPPINESS_RESPONSE = "I bring happiness and joy to the community, and absolutley don't waste peoples time or dubloons on junk that means nothing"
    PLAYER_HIGH_CHARISMA_CHALLENGE = "ok but that doesnt really explain what you do here, can you just explain yourself and not be a twat"
    MAX_HONEST_HIGH_CHARISMA = "fine look I take people's dubloons and they lose everytime, I have no idea why but they are so stupid and just keep coming back to gamble it away and get absoluley nothing in return, since you ask so kindly ill give you a discount on every 200th draw of this lovely chest"
    MAX_LOW_CHARISMA_PENALTY = "Oh uhhh dont worry there's something special for you on every 200th draw I cant tell you what it is though youll have to wait and see"
    
    # Max explains his service
    MAX_EXPLAIN_SERVICE = "I provide a service unlike any other, for a small fee *cough* 3000 Dubloons *cough* you get to have an Xtremely HIGH, see what I did there? chance of winning a new fashionable look for you or your pet or even your armor, so would you like to take a chance?"
    
    # Max's fuck off response
    MAX_FUCK_OFF = "Ok, well fuck off then I have others who want a turn"
    
    # Charisma threshold for special dialogue
    CHARISMA_THRESHOLD = 50
    
    # Special greetings for VIPs
    @staticmethod
    def get_vip_greeting(player: Any) -> Optional[str]:
        """Get special greeting for mayor/business owner/family"""
        is_mayor = getattr(player, 'is_mayor', False)
        has_family = hasattr(player, 'spouse') and player.spouse is not None
        is_business_owner = hasattr(player, 'owned_businesses') and player.owned_businesses
        
        player_name = getattr(player, 'name', 'friend')
        
        if is_mayor:
            return "OH snap its you mayor sorry i didnt know it was you the shop is just so busy right now"
        elif has_family:
            return f"hey {player_name} how's the family going"
        elif is_business_owner:
            return f"hey {player_name} how's the shop going"
        
        return None
    
    @staticmethod
    def is_criminal(player: Any) -> bool:
        """Check if player has criminal history"""
        has_bounty = getattr(player, 'wanted_level', 0) > 0 or getattr(player, 'crime_levels', {}).get('total_bounty', 0) > 0
        been_to_jail = getattr(player, 'times_jailed', 0) > 0 or getattr(player, 'jail_days', 0) > 0
        return has_bounty or been_to_jail
    
    @staticmethod
    def has_high_charisma(player: Any) -> bool:
        """Check if player has high enough charisma for special dialogue"""
        charisma = getattr(player, 'charisma', 0)
        return charisma >= MaxDialogue.CHARISMA_THRESHOLD


class LootBoxShop:
    """Handles the loot box purchase and cosmetic generation"""
    
    COST = 3000  # Dubloons
    DUPLICATE_REFUND = 30  # 1% refund for duplicates (predatory!)
    
    def __init__(self):
        self.total_boxes_opened = 0
        self.total_spent = 0
        self.duplicates_received = 0
        self.discount_unlocked = False  # 30% discount on every 200th draw
        self.penalty_active = False  # 30% price increase on every 200th draw (for low charisma)
    
    def can_afford(self, player: Any) -> bool:
        """Check if player can afford a loot box"""
        return player.money >= self.COST
    
    def get_current_cost(self) -> int:
        """Get the current cost for the next loot box (with discount/penalty if applicable)"""
        if self.total_boxes_opened > 0 and ((self.total_boxes_opened + 1) % 200) == 0:
            if self.discount_unlocked:
                return int(self.COST * 0.7)  # 30% discount on every 200th draw
            elif self.penalty_active:
                return int(self.COST * 1.3)  # 30% increase on every 200th draw
        return self.COST
    
    def is_discount_draw(self) -> bool:
        """Check if the next draw will be discounted"""
        if not self.discount_unlocked:
            return False
        if self.total_boxes_opened == 0:
            return False
        return ((self.total_boxes_opened + 1) % 200) == 0
    
    def is_penalty_draw(self) -> bool:
        """Check if the next draw will have a price increase"""
        if not self.penalty_active:
            return False
        if self.total_boxes_opened == 0:
            return False
        return ((self.total_boxes_opened + 1) % 200) == 0
    
    def purchase_loot_box(self, player: Any, cosmetic_manager: CosmeticManager,
                          preferred_type: str = "player") -> Tuple[bool, Optional[Any], bool]:
        """
        Purchase and open a loot box
        
        Args:
            player: Player object
            cosmetic_manager: Cosmetic manager
            preferred_type: Type of cosmetic to generate (player/pet/armor/weapon)
        
        Returns:
            Tuple of (success, cosmetic, is_duplicate)
        """
        if not self.can_afford(player):
            return (False, None, False)
        
        # Check if this is a special draw (every 200th if discount/penalty active)
        cost = self.COST
        if self.total_boxes_opened > 0 and ((self.total_boxes_opened + 1) % 200) == 0:
            if self.discount_unlocked:
                cost = int(self.COST * 0.7)  # 30% discount
            elif self.penalty_active:
                cost = int(self.COST * 1.3)  # 30% increase
        
        # Charge the player
        player.money -= cost
        self.total_spent += cost
        self.total_boxes_opened += 1
        
        # Generate cosmetic
        cosmetic = CosmeticGenerator.generate_cosmetic(applies_to=preferred_type)
        
        # Check if duplicate
        is_duplicate = not cosmetic_manager.unlock_cosmetic(cosmetic)
        
        if is_duplicate:
            # Give pathetic refund
            player.money += self.DUPLICATE_REFUND
            self.duplicates_received += 1
        
        return (True, cosmetic, is_duplicate)
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about boxes opened"""
        return {
            'total_opened': self.total_boxes_opened,
            'total_spent': self.total_spent,
            'duplicates': self.duplicates_received,
            'average_cost': self.total_spent // max(1, self.total_boxes_opened)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for saving"""
        return {
            'total_boxes_opened': self.total_boxes_opened,
            'total_spent': self.total_spent,
            'duplicates_received': self.duplicates_received,
            'discount_unlocked': self.discount_unlocked,
            'penalty_active': self.penalty_active
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LootBoxShop':
        """Deserialize from save data"""
        shop = LootBoxShop()
        shop.total_boxes_opened = data.get('total_boxes_opened', 0)
        shop.total_spent = data.get('total_spent', 0)
        shop.duplicates_received = data.get('duplicates_received', 0)
        shop.discount_unlocked = data.get('discount_unlocked', False)
        shop.penalty_active = data.get('penalty_active', False)
        return shop


class MaxShopInteraction:
    """Manages the full interaction with Max's shop"""
    
    # Dialogue states
    STATE_CLOSED = "closed"
    STATE_GREETING = "greeting"
    STATE_PLAYER_CHOICE = "player_choice"
    STATE_VIP_RESPONSE = "vip_response"
    STATE_VIP_PLAYER_REPLY = "vip_player_reply"
    STATE_CRIMINAL_RESPONSE = "criminal_response"
    STATE_PLAYER_SECOND_CHOICE = "player_second_choice"
    STATE_SARCASTIC_RESPONSE = "sarcastic_response"
    STATE_HIGH_CHARISMA_CHALLENGE = "high_charisma_challenge"
    STATE_HONEST_RESPONSE = "honest_response"
    STATE_LOW_CHARISMA_DISMISSIVE = "low_charisma_dismissive"
    STATE_EXPLANATION = "explanation"
    STATE_DECLINE = "decline"
    STATE_OFFER = "offer"
    STATE_PROCESSING = "processing"
    STATE_OPENING_BOX = "opening_box"
    STATE_RESULT = "result"
    STATE_CANT_AFFORD = "cant_afford"
    
    def __init__(self):
        self.state = self.STATE_CLOSED
        self.dialogue_index = 0
        self.current_dialogue: List[str] = []
        self.waiting_for_choice = False
        self.choice_options: List[str] = []
        self.selected_choice_index = 0  # For arrow key navigation
        self.last_purchase_duplicate = False
        self.last_cosmetic = None
        self.player_is_vip = False
        self.player_is_criminal = False
    
    def start_interaction(self, player: Any):
        """Start interaction with Max"""
        self.state = self.STATE_GREETING
        self.dialogue_index = 0
        self.current_dialogue = [MaxDialogue.INITIAL_GREETING]
        self.waiting_for_choice = False
        self.selected_choice_index = 0  # Reset selection
        self.choice_options = []
        
        # Check player status
        self.player_is_vip = MaxDialogue.get_vip_greeting(player) is not None
        self.player_is_criminal = MaxDialogue.is_criminal(player)
    
    def advance_dialogue(self, player: Any, loot_box_shop: LootBoxShop):
        """Advance to next dialogue line or state"""
        if self.waiting_for_choice:
            return  # Can't advance during choice
        
        self.dialogue_index += 1
        
        if self.dialogue_index >= len(self.current_dialogue):
            # Move to next state
            if self.state == self.STATE_GREETING:
                # After greeting, check if VIP or show player choice
                if self.player_is_vip:
                    vip_greeting = MaxDialogue.get_vip_greeting(player)
                    self.state = self.STATE_VIP_RESPONSE
                    self.dialogue_index = 0
                    self.current_dialogue = [vip_greeting]
                else:
                    self.state = self.STATE_PLAYER_CHOICE
                    self.dialogue_index = 0
                    self.waiting_for_choice = True
                    self.current_dialogue = [""]
                    self.choice_options = [
                        "[1] uhhh wow you are probably the rudest fucking person I've met so far.",
                        "[2] ok i guess thats one way to greet *looks around*, your literal only customer. what is it you do here anyway?"
                    ]
                    self.selected_choice_index = 0
            
            elif self.state == self.STATE_VIP_RESPONSE:
                # Show player's VIP response
                self.state = self.STATE_VIP_PLAYER_REPLY
                self.dialogue_index = 0
                self.current_dialogue = ["Things are going well Max how about another shot at a new look"]
            
            elif self.state == self.STATE_VIP_PLAYER_REPLY:
                # After player's VIP reply, Max explains service
                self.state = self.STATE_EXPLANATION
                self.dialogue_index = 0
                self.current_dialogue = [MaxDialogue.MAX_EXPLAIN_SERVICE]
                
            elif self.state == self.STATE_CRIMINAL_RESPONSE:
                # After Max's criminal response, show player second choice
                self.state = self.STATE_PLAYER_SECOND_CHOICE
                self.dialogue_index = 0
                self.waiting_for_choice = True
                self.current_dialogue = [""]
                self.choice_options = [
                    "[1] Yes, what do you even do here",
                    "[2] No, not the way you talk to your customers dickhead"
                ]
                self.selected_choice_index = 0
            
            elif self.state == self.STATE_SARCASTIC_RESPONSE:
                # After Max's happiness response, check charisma and branch immediately
                if MaxDialogue.has_high_charisma(player):
                    # High charisma - give player option to call out Max
                    self.state = self.STATE_HIGH_CHARISMA_CHALLENGE
                    self.dialogue_index = 0
                    self.waiting_for_choice = True
                    self.current_dialogue = [""]
                    self.choice_options = [
                        "[1] ok but that doesnt really explain what you do here, can you just explain yourself and not be a twat"
                    ]
                    self.selected_choice_index = 0
                else:
                    # Low charisma - Max gives cryptic penalty warning
                    self.state = self.STATE_LOW_CHARISMA_DISMISSIVE
                    self.dialogue_index = 0
                    self.current_dialogue = [MaxDialogue.MAX_LOW_CHARISMA_PENALTY]
            
            elif self.state == self.STATE_HIGH_CHARISMA_CHALLENGE:
                # After high charisma challenge, Max gives honest response
                self.state = self.STATE_HONEST_RESPONSE
                self.dialogue_index = 0
                self.current_dialogue = [MaxDialogue.MAX_HONEST_HIGH_CHARISMA]
            
            elif self.state == self.STATE_HONEST_RESPONSE:
                # After honest response with discount, go to explanation
                self.state = self.STATE_EXPLANATION
                self.dialogue_index = 0
                self.current_dialogue = [MaxDialogue.MAX_EXPLAIN_SERVICE]
            
            elif self.state == self.STATE_LOW_CHARISMA_DISMISSIVE:
                # After dismissive response, go to explanation
                # Activate penalty permanently
                loot_box_shop.penalty_active = True
                self.state = self.STATE_EXPLANATION
                self.dialogue_index = 0
                self.current_dialogue = [MaxDialogue.MAX_EXPLAIN_SERVICE]
            
            elif self.state == self.STATE_EXPLANATION:
                # After explanation, show offer
                self.state = self.STATE_OFFER
                self.dialogue_index = 0
                self.waiting_for_choice = True
                self.current_dialogue = [""]
                
                # Check if this is a discounted or penalty draw
                if loot_box_shop.is_discount_draw():
                    cost = loot_box_shop.get_current_cost()
                    self.choice_options = [
                        f"[A] Buy Loot Box ({cost} dubloons - 30% DISCOUNT!)",
                        "[D] No thanks"
                    ]
                elif loot_box_shop.is_penalty_draw():
                    cost = loot_box_shop.get_current_cost()
                    self.choice_options = [
                        f"[A] Buy Loot Box ({cost} dubloons)",
                        "[D] No thanks"
                    ]
                else:
                    self.choice_options = [
                        "[A] Buy Loot Box (3000 dubloons)",
                        "[D] No thanks"
                    ]
                self.selected_choice_index = 0
            
            elif self.state == self.STATE_DECLINE:
                # Close after decline
                self.close_interaction()
            
            elif self.state == self.STATE_CANT_AFFORD:
                # Close after can't afford message
                self.close_interaction()
            
            elif self.state == self.STATE_RESULT:
                # Can buy again after result
                self.state = self.STATE_OFFER
                self.dialogue_index = 0
                self.waiting_for_choice = True
                self.current_dialogue = ["Want to try another?"]
                
                # Check if this is a discounted or penalty draw
                if loot_box_shop.is_discount_draw():
                    cost = loot_box_shop.get_current_cost()
                    self.choice_options = [
                        f"[A] Buy Loot Box ({cost} dubloons - 30% DISCOUNT!)",
                        "[D] No thanks"
                    ]
                elif loot_box_shop.is_penalty_draw():
                    cost = loot_box_shop.get_current_cost()
                    self.choice_options = [
                        f"[A] Buy Loot Box ({cost} dubloons)",
                        "[D] No thanks"
                    ]
                else:
                    self.choice_options = [
                        "[A] Buy Loot Box (3000 dubloons)",
                        "[D] No thanks"
                    ]
                self.selected_choice_index = 0
    
    def make_choice(self, choice_num: int, player: Any, loot_box_shop: LootBoxShop) -> Optional[Any]:
        """
        Handle player choice
        
        Args:
            choice_num: Choice number (1, 2, etc) or special "accept"/"decline"
            player: Player object
            loot_box_shop: Shop instance
        
        Returns:
            "purchase" if purchased, None otherwise
        """
        self.waiting_for_choice = False
        self.choice_options = []
        
        if self.state == self.STATE_PLAYER_CHOICE:
            if choice_num == 1:
                # Player chose the rude option
                if self.player_is_criminal:
                    # Max responds to criminal
                    self.state = self.STATE_CRIMINAL_RESPONSE
                    self.dialogue_index = 0
                    self.current_dialogue = [MaxDialogue.MAX_RESPONSE_TO_CRIMINAL]
                else:
                    # For non-criminals, skip to explanation
                    self.state = self.STATE_EXPLANATION
                    self.dialogue_index = 0
                    self.current_dialogue = [MaxDialogue.MAX_EXPLAIN_SERVICE]
            elif choice_num == 2:
                # Player chose the sarcastic option
                self.state = self.STATE_SARCASTIC_RESPONSE
                self.dialogue_index = 0
                self.current_dialogue = [MaxDialogue.MAX_HAPPINESS_RESPONSE]
        
        elif self.state == self.STATE_HIGH_CHARISMA_CHALLENGE:
            if choice_num == 1:
                # Player used high charisma to challenge Max
                self.state = self.STATE_HONEST_RESPONSE
                self.dialogue_index = 0
                self.current_dialogue = [MaxDialogue.MAX_HONEST_HIGH_CHARISMA]
                # Unlock discount permanently
                loot_box_shop.discount_unlocked = True
        
        elif self.state == self.STATE_PLAYER_SECOND_CHOICE:
            if choice_num == 1:
                # "Yes, what do you even do here"
                self.state = self.STATE_EXPLANATION
                self.dialogue_index = 0
                self.current_dialogue = [MaxDialogue.MAX_EXPLAIN_SERVICE]
            elif choice_num == 2:
                # "No fuck off"
                self.state = self.STATE_DECLINE
                self.dialogue_index = 0
                self.current_dialogue = [MaxDialogue.MAX_FUCK_OFF]
        
        elif self.state == self.STATE_OFFER:
            if choice_num == "accept":
                # Check affordability with actual current cost
                current_cost = loot_box_shop.get_current_cost()
                if player.money >= current_cost:
                    return "purchase"  # Signal to start loot box animation
                else:
                    self.state = self.STATE_CANT_AFFORD
                    self.dialogue_index = 0
                    self.current_dialogue = [f"You don't have enough dubloons! Come back when you have {current_cost}."]
            elif choice_num == "decline":
                self.state = self.STATE_DECLINE
                self.dialogue_index = 0
                self.current_dialogue = [MaxDialogue.MAX_FUCK_OFF]
        
        return None
    
    def show_result(self, is_duplicate: bool):
        """Show result of loot box opening"""
        self.state = self.STATE_RESULT
        self.dialogue_index = 0
        self.last_purchase_duplicate = is_duplicate
        
        if is_duplicate:
            self.current_dialogue = ["Oh... you already have that one.", "Here's your refund of 30 dubloons. Better luck next time!"]
        else:
            self.current_dialogue = ["Congratulations! A brand new cosmetic!", "Come back any time!"]
    
    def close_interaction(self):
        """Close the interaction"""
        self.state = self.STATE_CLOSED
        self.dialogue_index = 0
        self.current_dialogue = []
        self.waiting_for_choice = False
        self.choice_options = []
        self.selected_choice_index = 0
    
    def move_selection_up(self):
        """Move selection up (arrow key navigation)"""
        if self.waiting_for_choice and self.choice_options:
            self.selected_choice_index = (self.selected_choice_index - 1) % len(self.choice_options)
    
    def move_selection_down(self):
        """Move selection down (arrow key navigation)"""
        if self.waiting_for_choice and self.choice_options:
            self.selected_choice_index = (self.selected_choice_index + 1) % len(self.choice_options)
    
    def get_selected_choice_number(self):
        """Get the choice number based on selected index (for make_choice compatibility)"""
        if not self.waiting_for_choice or not self.choice_options:
            return None
        
        # Check what type of option is selected
        selected_option = self.choice_options[self.selected_choice_index]
        
        if "[1]" in selected_option:
            return 1
        elif "[2]" in selected_option:
            return 2
        elif "[A]" in selected_option or "Buy Loot Box" in selected_option:
            return 'accept'
        elif "[D]" in selected_option or "No thanks" in selected_option:
            return 'decline'
        
        # Fallback to index + 1
        return self.selected_choice_index + 1
    
    def get_current_line(self) -> str:
        """Get current dialogue line"""
        if self.dialogue_index < len(self.current_dialogue):
            return self.current_dialogue[self.dialogue_index]
        return ""
    
    def get_all_visible_lines(self) -> List[str]:
        """Get all dialogue lines plus choice options"""
        lines = self.current_dialogue[:self.dialogue_index + 1]
        if self.waiting_for_choice and self.choice_options:
            lines.extend(self.choice_options)
        return lines
    
    def is_active(self) -> bool:
        """Check if interaction is active"""
        return self.state != self.STATE_CLOSED
    
    def is_waiting_for_input(self) -> bool:
        """Check if waiting for player input"""
        # Can advance if:
        # 1. Waiting for numbered choice, OR
        # 2. Showing dialogue (any line) and not in processing/opening state
        return self.waiting_for_choice or (
            self.is_active() and 
            self.state not in [self.STATE_PROCESSING, self.STATE_OPENING_BOX] and
            len(self.current_dialogue) > 0
        )
