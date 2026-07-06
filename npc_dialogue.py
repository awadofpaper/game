"""
Advanced NPC Dialogue and Quest System
Provides interactive NPCs with branching dialogue trees and quest functionality.
Integrated with the RPG game's existing systems.
"""

import pygame
from typing import Dict, List, Optional, Callable

print("Advanced NPC Dialogue System loaded!")

class DialogueNode:
    """Represents a single dialogue node with text and response options"""
    def __init__(self, text: str, speaker: str = "NPC", responses: List = None):
        self.text = text
        self.speaker = speaker
        self.responses = responses or []
        self.action = None  # Optional function to execute when this node is reached
        
    def add_response(self, response_text: str, next_node_id: str, condition: Callable = None):
        """Add a response option that leads to another dialogue node"""
        self.responses.append({
            'text': response_text,
            'next_node': next_node_id,
            'condition': condition  # Function that returns True/False if response is available
        })
        
    def set_action(self, action: Callable):
        """Set an action to execute when this node is displayed"""
        self.action = action


class Quest:
    """Represents a quest with objectives and rewards"""
    def __init__(self, quest_id: str, name: str, description: str):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.objectives = []
        self.rewards = {}
        self.completed = False
        self.active = False
        
    def add_objective(self, objective_id: str, description: str, target_count: int = 1):
        """Add an objective to the quest"""
        self.objectives.append({
            'id': objective_id,
            'description': description,
            'current': 0,
            'target': target_count,
            'completed': False
        })
        
    def add_reward(self, reward_type: str, item: str, amount: int = 1):
        """Add a reward (item, xp, gold, etc.)"""
        if reward_type not in self.rewards:
            self.rewards[reward_type] = []
        self.rewards[reward_type].append({'item': item, 'amount': amount})
        
    def update_objective(self, objective_id: str, amount: int = 1):
        """Update progress on an objective"""
        for obj in self.objectives:
            if obj['id'] == objective_id and not obj['completed']:
                obj['current'] = min(obj['current'] + amount, obj['target'])
                if obj['current'] >= obj['target']:
                    obj['completed'] = True
                return True
        return False
        
    def check_completion(self):
        """Check if all objectives are complete"""
        if not self.active:
            return False
        completed = all(obj['completed'] for obj in self.objectives)
        if completed and not self.completed:
            self.completed = True
            return True
        return False
    
    def get_progress_text(self):
        """Get quest progress as formatted text"""
        if not self.objectives:
            return "No objectives"
        
        progress = []
        for obj in self.objectives:
            status = "✓" if obj['completed'] else "○"
            progress.append(f"{status} {obj['description']} ({obj['current']}/{obj['target']})")
        
        return "\n".join(progress)


class DialogueUI:
    """Manages dialogue UI rendering and interactions"""
    def __init__(self, screen_width, screen_height):
        self.active = False
        self.current_npc = None
        self.current_node_id = "start"
        self.current_node = None
        self.text_display = []
        self.responses = []
        self.selected_response = 0
        
        # UI styling
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 28)
        
        # Colors
        self.bg_color = (20, 20, 30)
        self.border_color = (100, 200, 255)
        self.text_color = (255, 255, 255)
        self.speaker_color = (255, 255, 150)
        self.response_color = (200, 200, 200)
        self.selected_color = (255, 255, 100)
        self.response_bg_color = (50, 50, 70)
        
    def start_dialogue(self, npc, starting_node: str = "start"):
        """Begin dialogue with an NPC"""
        self.active = True
        self.current_npc = npc
        self.current_node_id = starting_node
        self.load_current_node()
        
    def load_current_node(self):
        """Load the current dialogue node"""
        if not self.current_npc:
            return
        
        # Get dialogue tree
        dialogue_tree = self.current_npc.get_current_dialogue()
        self.current_node = dialogue_tree.get(self.current_node_id)
        
        if not self.current_node:
            self.end_dialogue()
            return
        
        # Execute node action if present
        if self.current_node.action:
            self.current_node.action()
        
        # Wrap text for display
        self.text_display = self.wrap_text(self.current_node.text, 70)
        
        # Filter responses by conditions
        self.responses = []
        for response in self.current_node.responses:
            if not response.get('condition') or response['condition']():
                self.responses.append(response)
        
        self.selected_response = 0
    
    def wrap_text(self, text: str, max_chars: int):
        """Wrap text to fit in dialogue box"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) <= max_chars:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def handle_input(self, event):
        """Handle input for dialogue system"""
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.end_dialogue()
                return True
            
            # Navigate responses
            if event.key == pygame.K_UP and self.responses:
                self.selected_response = (self.selected_response - 1) % len(self.responses)
                return True
            elif event.key == pygame.K_DOWN and self.responses:
                self.selected_response = (self.selected_response + 1) % len(self.responses)
                return True
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                if self.responses:
                    # Select response
                    selected = self.responses[self.selected_response]
                    next_node = selected['next_node']
                    if next_node == "end":
                        self.end_dialogue()
                    else:
                        self.current_node_id = next_node
                        self.load_current_node()
                else:
                    # No responses, end dialogue
                    self.end_dialogue()
                return True
        
        return False
    
    def end_dialogue(self):
        """End the current dialogue"""
        self.active = False
        self.current_npc = None
        self.current_node = None
    
    def draw(self, screen):
        """Draw the dialogue UI"""
        if not self.active or not self.current_node:
            return
        
        # Dialogue box dimensions
        box_width = self.screen_width - 100
        box_height = min(350, self.screen_height // 2)
        box_x = 50
        box_y = self.screen_height - box_height - 50
        
        # Draw semi-transparent background overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw dialogue box
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, self.bg_color, box_rect)
        pygame.draw.rect(screen, self.border_color, box_rect, 3)
        
        # Draw speaker name
        speaker_surface = self.large_font.render(f"{self.current_node.speaker}:", True, self.speaker_color)
        screen.blit(speaker_surface, (box_x + 20, box_y + 15))
        
        # Draw dialogue text
        y_offset = 50
        for line in self.text_display:
            text_surface = self.font.render(line, True, self.text_color)
            screen.blit(text_surface, (box_x + 20, box_y + y_offset))
            y_offset += 25
            
            # Stop if we're running out of space
            if y_offset > box_height - 120:
                break
        
        # Draw responses
        if self.responses:
            # Draw response section separator
            response_y = box_y + box_height - 110
            pygame.draw.line(screen, self.border_color, 
                           (box_x + 10, response_y), 
                           (box_x + box_width - 10, response_y), 2)
            
            # Draw responses
            for i, response in enumerate(self.responses):
                resp_y = response_y + 15 + i * 30
                
                # Highlight selected response
                if i == self.selected_response:
                    highlight_rect = pygame.Rect(box_x + 15, resp_y - 3, box_width - 30, 28)
                    pygame.draw.rect(screen, self.response_bg_color, highlight_rect)
                    pygame.draw.rect(screen, self.selected_color, highlight_rect, 2)
                    color = self.selected_color
                    prefix = "► "
                else:
                    color = self.response_color
                    prefix = "  "
                
                # Truncate long responses
                response_text = response['text']
                if len(response_text) > 65:
                    response_text = response_text[:62] + "..."
                
                text_surface = self.font.render(f"{prefix}{response_text}", True, color)
                screen.blit(text_surface, (box_x + 25, resp_y))
        
        # Draw controls hint
        controls_text = "↑↓ Navigate  •  ENTER/E Select  •  ESC Close"
        controls_surface = self.font.render(controls_text, True, (150, 150, 150))
        screen.blit(controls_surface, (box_x + 20, box_y + box_height - 25))


def create_elder_sage_npc(player, start_x=400, start_y=300):
    """
    Create the Elder Sage tutorial NPC with a stick gathering quest.
    
    This NPC offers a starter quest and has multiple dialogue paths including:
    - Tutorial quest (gather 5 sticks for an iron sword)
    - Lore information
    - A "curse" path for rude players (reduces shop prices by 10%)
    
    Returns: BasicNPC with advanced dialogue system
    """
    from npc_basic import BasicNPC
    
    # Create the NPC using BasicNPC class
    elder = BasicNPC(
        name="Elder Sage",
        x=start_x,
        y=start_y,
        npc_type="elder",
        sprite_color=(120, 80, 150)  # Purple robes
    )
    
    # Make the NPC stationary (doesn't wander)
    elder.can_wander = False
    elder.is_patrolling = False
    
    # Initialize dialogue system attributes
    elder.dialogue_trees = {}
    elder.current_tree = "default"
    elder.quests = {}
    elder.has_cursed_player = False
    
    # Create the stick gathering quest
    starter_quest = Quest(
        "gather_sticks",
        "Forest Preparation",
        "The Elder Sage wants you to gather 5 sticks to craft your first weapon."
    )
    starter_quest.add_objective("collect_sticks", "Collect 5 sticks", 5)
    starter_quest.add_reward("items", "iron_sword", 1)
    starter_quest.add_reward("xp", "experience", 50)
    
    elder.quests["gather_sticks"] = starter_quest
    
    # Quest helper functions
    def start_quest():
        """Start the stick gathering quest"""
        quest = elder.quests["gather_sticks"]
        if not quest.active and not quest.completed:
            quest.active = True
            elder.current_tree = "quest_active"
            print(f"Quest started: {quest.name}")
            return True
        return False
    
    def check_stick_count():
        """Check if player has enough sticks"""
        return player.inventory.get("stick", 0) >= 5
    
    def complete_quest():
        """Complete the quest and give rewards"""
        quest = elder.quests["gather_sticks"]
        if quest.active and check_stick_count():
            quest.completed = True
            quest.active = False
            
            # Remove sticks from inventory
            player.inventory["stick"] = max(0, player.inventory.get("stick", 0) - 5)
            
            # Give iron sword reward
            if "iron_sword" not in player.inventory:
                player.inventory["iron_sword"] = 0
            player.inventory["iron_sword"] += 1
            
            # Give XP
            if hasattr(player, 'add_xp'):
                player.add_xp(50)
            
            elder.current_tree = "quest_completed"
            print(f"Quest completed: {quest.name}! Received iron sword and 50 XP!")
            return True
        return False
    
    def curse_player():
        """Apply curse to player - 10% less gold from shops"""
        if not hasattr(player, 'shop_curse_active'):
            player.shop_curse_active = True
            elder.has_cursed_player = True
            elder.current_tree = "cursed"
            
            # Block the starter quest permanently
            if "gather_sticks" in elder.quests:
                elder.quests["gather_sticks"].active = False
                elder.quests["gather_sticks"].completed = True
            
            print("Elder Sage has cursed you! Shop prices will be 10% worse!")
    
    # === DEFAULT DIALOGUE TREE ===
    nodes = {}
    
    start_node = DialogueNode(
        "Greetings, traveler. These lands have grown dangerous of late. "
        "Dark forces corrupt the creatures of the forest, and few brave souls "
        "venture forth anymore. You look like you could use some guidance.",
        "Elder Sage"
    )
    start_node.add_response("What's happening in these lands?", "lore")
    start_node.add_response("I could use some help getting started.", "help")
    start_node.add_response("Do you have any quests for me?", "quest_offer")
    start_node.add_response("I don't need help from an old hermit.", "rude_response")
    start_node.add_response("Goodbye.", "end")
    nodes["start"] = start_node
    
    lore_node = DialogueNode(
        "Dark magic seeps into our world from places unknown, corrupting the wildlife "
        "and making them aggressive. The balance that once kept peace is breaking down. "
        "We need brave souls like yourself to push back this growing darkness.",
        "Elder Sage"
    )
    lore_node.add_response("How can I help fight this darkness?", "help")
    lore_node.add_response("Do you have any quests for me?", "quest_offer")
    lore_node.add_response("I understand. Goodbye.", "end")
    nodes["lore"] = lore_node
    
    help_node = DialogueNode(
        "First, you'll need proper equipment. Your bare hands won't last long against "
        "corrupted creatures. I can craft you a fine iron sword, but I'll need "
        "materials. Wood is essential for the handle.",
        "Elder Sage"
    )
    help_node.add_response("What materials do you need?", "quest_offer")
    help_node.add_response("Where can I find these materials?", "materials_info")
    help_node.add_response("I'll see what I can do.", "end")
    nodes["help"] = help_node
    
    quest_offer_node = DialogueNode(
        "Perfect! I need you to gather 5 wooden sticks. You can find them "
        "by chopping down trees - just walk up and attack them. "
        "Bring them back to me, and I'll forge you a proper iron sword!",
        "Elder Sage"
    )
    quest_offer_node.add_response("I accept this quest!", "accept_quest")
    quest_offer_node.add_response("Where exactly should I look?", "materials_info")
    quest_offer_node.add_response("Maybe later.", "end")
    nodes["quest_offer"] = quest_offer_node
    
    accept_quest_node = DialogueNode(
        "Excellent! Go forth and gather those 5 sticks. Remember, you can chop "
        "trees with your bare hands - just walk up and attack them. "
        "Return when you have all 5 sticks. Good luck, young adventurer!",
        "Elder Sage"
    )
    accept_quest_node.set_action(start_quest)
    accept_quest_node.add_response("I'll be back with those sticks!", "end")
    nodes["accept_quest"] = accept_quest_node
    
    materials_info_node = DialogueNode(
        "Look for trees around the area - they're the brown trunks with green leaves. "
        "Walk up to one and attack it to chop it down. "
        "Each tree should give you some wood and sticks.",
        "Elder Sage"
    )
    materials_info_node.add_response("Got it, I'll start gathering.", "accept_quest")
    materials_info_node.add_response("Sounds simple enough.", "end")
    nodes["materials_info"] = materials_info_node
    
    rude_response_node = DialogueNode(
        "Hmph! An old hermit, am I? I've survived these lands longer than you've been alive, "
        "whelp. But fine, if you don't want my help, go ahead and see how far "
        "you get on your own. Don't come crying to me when the wolves get you.",
        "Elder Sage"
    )
    rude_response_node.add_response("Wait, I didn't mean it like that. I do need help.", "help")
    rude_response_node.add_response("You know what? I'll take my chances alone.", "curse_player")
    rude_response_node.add_response("Do you at least have any quests?", "quest_offer")
    nodes["rude_response"] = rude_response_node
    
    curse_node = DialogueNode(
        "You dare mock me, fool? I offered you guidance and you spat in my face! "
        "Very well - I place a curse upon you! From this day forward, "
        "all merchants will sense your disrespect and charge you MORE for goods. "
        "Be gone, and may you regret your insolence!",
        "Elder Sage"
    )
    curse_node.set_action(curse_player)
    curse_node.add_response("Wait, I didn't mean-", "cursed_dismissal")
    curse_node.add_response("Fine, I don't need you anyway!", "end")
    nodes["curse_player"] = curse_node
    
    cursed_dismissal_node = DialogueNode(
        "Too late! The curse is cast and cannot be undone! "
        "You had your chance for respect and guidance, but chose mockery instead. "
        "Now live with the consequences!",
        "Elder Sage"
    )
    cursed_dismissal_node.add_response("This isn't fair!", "end")
    cursed_dismissal_node.add_response("I... I understand.", "end")
    nodes["cursed_dismissal"] = cursed_dismissal_node
    
    elder.dialogue_trees["default"] = nodes
    
    # === QUEST ACTIVE DIALOGUE TREE ===
    quest_active_nodes = {}
    
    quest_active_start = DialogueNode(
        "Ah, you're back! How goes the stick gathering? Remember, I need 5 sticks "
        "to craft your iron sword.",
        "Elder Sage"
    )
    quest_active_start.add_response("I have the sticks you requested!", "turn_in", check_stick_count)
    quest_active_start.add_response("Still working on it.", "still_gathering")
    quest_active_start.add_response("Remind me what I need to do?", "quest_reminder")
    quest_active_nodes["start"] = quest_active_start
    
    turn_in_node = DialogueNode(
        "Wonderful! These sticks are perfect quality. Let me work my magic... "
        "*chants ancient words* ...There! A fine iron sword, perfectly balanced "
        "and sharp. This should serve you well! Take this experience as well!",
        "Elder Sage"
    )
    turn_in_node.set_action(complete_quest)
    turn_in_node.add_response("Thank you so much!", "end")
    quest_active_nodes["turn_in"] = turn_in_node
    
    still_gathering_node = DialogueNode(
        "Take your time, but don't venture too far without proper equipment. "
        "The corrupted creatures grow stronger at night. Stay safe!",
        "Elder Sage"
    )
    still_gathering_node.add_response("I'll be careful.", "end")
    quest_active_nodes["still_gathering"] = still_gathering_node
    
    quest_reminder_node = DialogueNode(
        "Of course! I need you to collect 5 wooden sticks. You can get them by "
        "chopping down trees - just walk up to any tree and attack it.",
        "Elder Sage"
    )
    quest_reminder_node.add_response("Right, I'll get on that.", "end")
    quest_active_nodes["quest_reminder"] = quest_reminder_node
    
    elder.dialogue_trees["quest_active"] = quest_active_nodes
    
    # === QUEST COMPLETED DIALOGUE TREE ===
    quest_completed_nodes = {}
    
    completed_start = DialogueNode(
        "Hello again, brave adventurer! How is that iron sword treating you? "
        "I hope it serves you well in pushing back the darkness!",
        "Elder Sage"
    )
    completed_start.add_response("The sword is excellent, thank you!", "sword_praise")
    completed_start.add_response("Do you have any other quests?", "no_more_quests")
    completed_start.add_response("Any advice for my journey?", "journey_advice")
    completed_start.add_response("Goodbye, Elder Sage.", "end")
    quest_completed_nodes["start"] = completed_start
    
    sword_praise_node = DialogueNode(
        "I'm delighted to hear that! That blade was forged with old magic - "
        "it should cut through corruption like sunlight through shadow. "
        "May it protect you in your battles!",
        "Elder Sage"
    )
    sword_praise_node.add_response("It certainly feels powerful.", "end")
    quest_completed_nodes["sword_praise"] = sword_praise_node
    
    no_more_quests_node = DialogueNode(
        "For now, your quest is to grow stronger and explore these lands. "
        "Learn the ways of combat, gather resources, and prepare yourself. "
        "Perhaps when you've gained more experience, I'll have greater tasks for you.",
        "Elder Sage"
    )
    no_more_quests_node.add_response("I understand.", "end")
    quest_completed_nodes["no_more_quests"] = no_more_quests_node
    
    journey_advice_node = DialogueNode(
        "Remember: courage is not the absence of fear, but action in spite of it. "
        "Save your progress often (F5), learn from each defeat, and never hesitate to "
        "retreat when overwhelmed. The darkness feeds on recklessness.",
        "Elder Sage"
    )
    journey_advice_node.add_response("Wise words. Thank you.", "end")
    quest_completed_nodes["journey_advice"] = journey_advice_node
    
    elder.dialogue_trees["quest_completed"] = quest_completed_nodes
    
    # === CURSED DIALOGUE TREE ===
    cursed_nodes = {}
    
    cursed_start = DialogueNode(
        "You again? I thought I told you to be gone! "
        "The curse still flows through you - merchants will never give you fair prices. "
        "Perhaps next time you'll think twice before disrespecting those who offer help.",
        "Elder Sage"
    )
    cursed_start.add_response("Is there any way to lift this curse?", "no_redemption")
    cursed_start.add_response("I'm sorry for what I said.", "no_redemption")
    cursed_start.add_response("Fine, I'll leave you alone.", "end")
    cursed_nodes["start"] = cursed_start
    
    no_redemption_node = DialogueNode(
        "Some actions cannot be undone, young one. "
        "You had a chance for guidance and chose scorn instead. "
        "The curse will remain as a reminder of respect and humility. "
        "Now begone!",
        "Elder Sage"
    )
    no_redemption_node.add_response("I understand...", "end")
    cursed_nodes["no_redemption"] = no_redemption_node
    
    elder.dialogue_trees["cursed"] = cursed_nodes
    
    # Add methods to BasicNPC for dialogue tree support
    def get_current_dialogue(self):
        """Get the current dialogue tree"""
        return self.dialogue_trees.get(self.current_tree, {})
    
    def update_quest_marker(self):
        """Update whether NPC should show quest markers"""
        self.has_quest_marker = False
        for quest in self.quests.values():
            if not quest.active and not quest.completed:
                self.has_quest_marker = True  # Has available quest
                break
            elif quest.active and quest.check_completion():
                self.has_quest_marker = True  # Quest ready to turn in
                break
    
    # Bind methods to the NPC instance
    elder.get_current_dialogue = lambda: get_current_dialogue(elder)
    elder.update_quest_marker = lambda: update_quest_marker(elder)
    
    # Update quest marker initially
    elder.update_quest_marker()
    
    return elder
