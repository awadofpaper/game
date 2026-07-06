"""
Dialogue System - Branching conversations with NPCs
"""

import random
from enum import Enum

class DialogueNodeType(Enum):
    TEXT = "text"  # NPC speaks
    CHOICE = "choice"  # Player chooses response
    ACTION = "action"  # Triggers game action (quest, shop, etc)
    END = "end"  # Conversation ends

class DialogueChoice:
    """A single dialogue choice option"""
    
    def __init__(self, text, next_node_id, requirements=None, consequences=None):
        self.text = text
        self.next_node_id = next_node_id  # ID of next node, or None to end
        self.requirements = requirements or {}  # {'stat': value, 'level': value, 'reputation': value}
        self.consequences = consequences or {}  # {'reputation': amount, 'gold': amount, etc}
        
    def can_choose(self, player, reputation_system, npc_id=None):
        """Check if player meets requirements"""
        # Check level requirement
        if 'level' in self.requirements:
            if player.level < self.requirements['level']:
                return False, f"[Level {self.requirements['level']} required]"
        
        # Check stat requirements
        for stat, required_value in self.requirements.items():
            if stat == 'level':
                continue
            if stat in ['Strength', 'Stamina', 'Willpower', 'Magic', 'Dexterity', 'Charisma']:
                player_stat = getattr(player, stat, 0)
                if player_stat < required_value:
                    return False, f"[{stat} {required_value} required]"
        
        # Check reputation requirement
        if 'reputation' in self.requirements and npc_id:
            rep_level = self.requirements['reputation']
            current_rep = reputation_system.get_npc_reputation(npc_id)
            rep_threshold = reputation_system.REPUTATION_LEVELS.get(rep_level, 0)
            if current_rep < rep_threshold:
                return False, f"[{rep_level} reputation required]"
        
        # Check faction reputation
        if 'faction_reputation' in self.requirements:
            faction, rep_level = self.requirements['faction_reputation']
            current_rep = reputation_system.get_faction_reputation(faction)
            rep_threshold = reputation_system.REPUTATION_LEVELS.get(rep_level, 0)
            if current_rep < rep_threshold:
                return False, f"[{rep_level} with {faction} required]"
        
        # Check gold requirement
        if 'gold' in self.requirements:
            if player.dubloons < self.requirements['gold']:
                return False, f"[{self.requirements['gold']} gold required]"
        
        return True, None

class DialogueNode:
    """A node in the dialogue tree"""
    
    def __init__(self, node_id, node_type, content=None, choices=None, action=None, 
                 personality_variants=None, weather_variants=None, reputation_variants=None,
                 next_node_id=None):
        self.id = node_id
        self.type = node_type
        self.content = content  # Text for TEXT nodes
        self.choices = choices or []  # List of DialogueChoice for CHOICE nodes
        self.action = action  # Action dict for ACTION nodes: {'type': 'quest_accept', 'quest_id': '...'}
        self.next_node_id = next_node_id  # For TEXT nodes, ID of the next node to advance to
        
        # Variants based on conditions
        self.personality_variants = personality_variants or {}  # {personality: text}
        self.weather_variants = weather_variants or {}  # {weather: text}
        self.reputation_variants = reputation_variants or {}  # {rep_level: text}
    
    def get_text(self, npc_personality=None, current_weather=None, reputation_level=None):
        """Get text based on conditions"""
        # Check reputation variant first (highest priority)
        if reputation_level and reputation_level in self.reputation_variants:
            return self.reputation_variants[reputation_level]
        
        # Check personality variant
        if npc_personality and npc_personality in self.personality_variants:
            return self.personality_variants[npc_personality]
        
        # Check weather variant
        if current_weather and current_weather in self.weather_variants:
            return self.weather_variants[current_weather]
        
        # Default content
        return self.content

class DialogueTree:
    """Complete dialogue tree for an NPC"""
    
    def __init__(self, tree_id, start_node_id):
        self.id = tree_id
        self.start_node_id = start_node_id
        self.nodes = {}  # {node_id: DialogueNode}
        
    def add_node(self, node):
        """Add a node to the tree"""
        self.nodes[node.id] = node
        
    def get_node(self, node_id):
        """Get a node by ID"""
        return self.nodes.get(node_id)

class DialogueManager:
    """Manages all dialogue trees and active conversations"""
    
    def __init__(self, reputation_system, quest_manager):
        self.reputation_system = reputation_system
        self.quest_manager = quest_manager
        self.dialogue_trees = {}  # {tree_id: DialogueTree}
        self.conversation_history = []  # List of (npc_name, timestamp, summary)
        
        # Current active conversation
        self.active_conversation = None
        self.current_tree = None
        self.current_node = None
        self.current_npc = None
        self.last_visited_node_id = None  # Track last node before closing
        
        # Create starter dialogues
        self._create_starter_dialogues()
    
    def _create_starter_dialogues(self):
        """Create initial dialogue trees"""
        
        # Quest Giver 1 - The one with the hilarious kill quest
        quest_giver_tree = DialogueTree("quest_giver_1", "greeting")
        
        # Greeting node with reputation variants
        greeting = DialogueNode(
            "greeting",
            DialogueNodeType.TEXT,
            content="Greetings, traveler! I have something VERY important to discuss.",
            personality_variants={
                "enthusiastic": "OH! Finally! Someone who looks capable! I've been waiting for you!",
                "grumpy": "You there. Got a minute? I need someone to handle something.",
                "mysterious": "Ah... I've been expecting you. The winds whispered of your coming."
            },
            weather_variants={
                "rain": "Terrible weather, isn't it! But perfect for what I need done!",
                "snow": "Brrr! Cold day, but I have something that'll warm your spirits - well, your coin purse at least."
            },
            reputation_variants={
                "Revered": "My most trusted friend! I have another task that only you can handle.",
                "Hostile": "You've got some nerve showing your face here. But... I'm desperate enough to deal with you."
            },
            next_node_id="greeting_choices"
        )
        quest_giver_tree.add_node(greeting)
        
        # After greeting, show choices
        greeting_choices = DialogueNode(
            "greeting_choices",
            DialogueNodeType.CHOICE,
            choices=[
                DialogueChoice("What do you need?", "explain_quest"),
                DialogueChoice("[Charisma 5] I'm the best there is. What's the job?", "explain_quest_confident", 
                             requirements={'Charisma': 5}),
                DialogueChoice("I'm busy. Maybe later.", "refuse_initial"),
                DialogueChoice("I don't work for free.", "discuss_payment")
            ]
        )
        quest_giver_tree.add_node(greeting_choices)
        
        # Explain the quest (the hilarious one)
        explain_quest = DialogueNode(
            "explain_quest",
            DialogueNodeType.TEXT,
            content="Well Please go Dark Forest and kill these 10 slimes, This is possibly the most important thing you can do in these lands, NOTHING and i mean NOTHING will help the people here then to kill 10 random things and return to ONLY tell me about it and no one else, this absolutley will not waste your time i promise you",
            next_node_id="quest_accept_choices"
        )
        quest_giver_tree.add_node(explain_quest)
        
        # Confident variant
        explain_quest_confident = DialogueNode(
            "explain_quest_confident",
            DialogueNodeType.TEXT,
            content="Ha! I like your confidence. Well Please go Dark Forest and kill these 10 slimes, This is possibly the most important thing you can do in these lands, NOTHING and i mean NOTHING will help the people here then to kill 10 random things and return to ONLY tell me about it and no one else, this absolutley will not waste your time i promise you. Someone with your skills should make quick work of it!",
            next_node_id="quest_accept_choices"
        )
        quest_giver_tree.add_node(explain_quest_confident)
        
        # Quest acceptance choices
        quest_accept_choices = DialogueNode(
            "quest_accept_choices",
            DialogueNodeType.CHOICE,
            choices=[
                DialogueChoice("Alright, I'll do it.", "accept_quest"),
                DialogueChoice("That sounds... suspicious. Why only tell you?", "question_quest"),
                DialogueChoice("Ten slimes? That's ridiculous. I'm out.", "refuse_quest"),
                DialogueChoice("[Intelligence 6] This seems like a complete waste of time...", "call_out_quest",
                             requirements={'Willpower': 6})
            ]
        )
        quest_giver_tree.add_node(quest_accept_choices)
        
        # Question the quest
        question_quest = DialogueNode(
            "question_quest",
            DialogueNodeType.TEXT,
            content="Suspicious? NO! Not at all! It's just... very important that only I know. For... reasons. Secret reasons. Very official secret reasons that definitely exist!",
            next_node_id="quest_accept_choices"
        )
        quest_giver_tree.add_node(question_quest)
        
        # Call out the quest (high Intelligence)
        call_out_quest = DialogueNode(
            "call_out_quest",
            DialogueNodeType.TEXT,
            content="Waste of time?! How dare... okay fine, you got me. It's not THAT important. But I'll still pay you! Come on, help me out here!",
            next_node_id="quest_accept_choices"
        )
        quest_giver_tree.add_node(call_out_quest)
        
        # Accept quest action
        accept_quest = DialogueNode(
            "accept_quest",
            DialogueNodeType.ACTION,
            content="Excellent! Go forth and... do the thing! Return when you're done!",
            action={'type': 'quest_accept', 'quest_id': 'absolutely_vital_mission'}
        )
        quest_giver_tree.add_node(accept_quest)
        
        # Refuse quest (dead end)
        refuse_quest = DialogueNode(
            "refuse_quest",
            DialogueNodeType.TEXT,
            content="What?! But... but it's SO important! Fine! Be that way! I'll find someone else who appreciates the gravity of slime elimination!"
        )
        quest_giver_tree.add_node(refuse_quest)
        
        # Refuse initial (early exit)
        refuse_initial = DialogueNode(
            "refuse_initial",
            DialogueNodeType.TEXT,
            content="Oh. Well. That's... disappointing. Come back when you have time for something VERY important."
        )
        quest_giver_tree.add_node(refuse_initial)
        
        # Discuss payment
        discuss_payment = DialogueNode(
            "discuss_payment",
            DialogueNodeType.TEXT,
            content="Of course not! I'm offering 50 gold AND 100 experience! Plus the satisfaction of knowing you've done something incredibly... uh... vital. Yes.",
            next_node_id="greeting_choices"
        )
        quest_giver_tree.add_node(discuss_payment)
        
        # Quest turn-in dialogue
        quest_complete = DialogueNode(
            "quest_complete",
            DialogueNodeType.TEXT,
            content="You did it! You actually killed 10 slimes! Amazing! Here's your reward. The people of this land owe you a debt they'll never know about!",
            reputation_variants={
                "Friendly": "Excellent work as always! Your dedication is unmatched!",
                "Revered": "My champion returns! The slimes never stood a chance against you!"
            }
        )
        quest_giver_tree.add_node(quest_complete)
        
        # Store the tree
        self.dialogue_trees["quest_giver_1"] = quest_giver_tree
        
        # Town Elder - Serious quest giver
        elder_tree = DialogueTree("town_elder", "elder_greeting")
        
        elder_greeting = DialogueNode(
            "elder_greeting",
            DialogueNodeType.TEXT,
            content="Welcome, traveler. Our town faces many challenges. Perhaps you can help?",
            personality_variants={
                "wise": "Ah, young one. The threads of fate have brought you here for a reason.",
                "stern": "State your business. We don't have time for idle chatter."
            },
            weather_variants={
                "rain": "Come in, come in. No need to stand in the rain. We have much to discuss.",
                "storm": "Terrible storm brewing. An ill omen, or perhaps... an opportunity?"
            },
            next_node_id="elder_choices"
        )
        elder_tree.add_node(elder_greeting)
        
        elder_choices = DialogueNode(
            "elder_choices",
            DialogueNodeType.CHOICE,
            choices=[
                DialogueChoice("How can I help?", "elder_quests"),
                DialogueChoice("Tell me about this town.", "town_info"),
                DialogueChoice("[Level 3+] I hear there are ruins to the north?", "ruins_quest",
                             requirements={'level': 3}),
                DialogueChoice("Farewell.", None)  # Ends conversation
            ]
        )
        elder_tree.add_node(elder_choices)
        
        elder_quests = DialogueNode(
            "elder_quests",
            DialogueNodeType.TEXT,
            content="We have several matters that need attention. Ruins to explore, travelers gone missing, and always the threat of dangerous creatures. What interests you?",
            next_node_id="elder_choices"
        )
        elder_tree.add_node(elder_quests)
        
        town_info = DialogueNode(
            "town_info",
            DialogueNodeType.TEXT,
            content="This is Riverside, a peaceful settlement... mostly. We trade with neighboring villages and try to keep the monster population under control. It's a simple life, but honest.",
            next_node_id="elder_choices"
        )
        elder_tree.add_node(town_info)
        
        ruins_quest = DialogueNode(
            "ruins_quest",
            DialogueNodeType.TEXT,
            content="Ah, so you've heard. Yes, ancient ruins lie to the north. We don't know who built them or what secrets they hold. Many have ventured there, but few return with answers. Are you brave enough to investigate?",
            next_node_id="elder_choices"
        )
        elder_tree.add_node(ruins_quest)
        
        self.dialogue_trees["town_elder"] = elder_tree
        
        # Generic Merchant dialogue
        merchant_tree = DialogueTree("merchant", "merchant_greeting")
        
        merchant_greeting = DialogueNode(
            "merchant_greeting",
            DialogueNodeType.TEXT,
            content="Looking to buy or sell?",
            personality_variants={
                "greedy": "Ah! A customer! I have the finest wares... at the finest prices!",
                "friendly": "Hello friend! What can I do for you today?"
            },
            reputation_variants={
                "Honored": "My best customer! I've set aside some special items just for you!",
                "Hostile": "You again. This better be quick."
            },
            next_node_id="merchant_menu"
        )
        merchant_tree.add_node(merchant_greeting)
        
        # Merchant menu (Buy/Sell/Talk)
        merchant_menu = DialogueNode(
            "merchant_menu",
            DialogueNodeType.CHOICE,
            choices=[
                DialogueChoice("Show me your wares. (Buy)", "action_shop"),
                DialogueChoice("I have items to sell.", "action_shop"),
                DialogueChoice("Let's talk.", "merchant_talk"),
                DialogueChoice("Maybe later.", None)
            ]
        )
        merchant_tree.add_node(merchant_menu)
        
        merchant_talk = DialogueNode(
            "merchant_talk",
            DialogueNodeType.TEXT,
            content="Business has been good lately. Lots of adventurers passing through. Say, if you find any rare items out there, bring them to me first, eh?",
            next_node_id="merchant_menu"
        )
        merchant_tree.add_node(merchant_talk)
        
        self.dialogue_trees["merchant"] = merchant_tree
        
        # Town Guard dialogue - provides bounty and reputation information
        guard_tree = DialogueTree("guard", "guard_greeting")
        
        guard_greeting = DialogueNode(
            "guard_greeting",
            DialogueNodeType.TEXT,
            content="Halt! State your business in this town, traveler.",
            personality_variants={
                "friendly": "Greetings, traveler! Just doing my rounds. Everything alright?",
                "stern": "You there. Keep your nose clean while you're in town.",
                "vigilant": "Eyes sharp, traveler. These are troubled times."
            },
            weather_variants={
                "rain": "Miserable weather for a patrol. What brings you out in this?",
                "snow": "Cold day for guard duty. Stay safe out there."
            },
            reputation_variants={
                "Honored": "Ah, a trusted friend of the town! Welcome back!",
                "Revered": "Our hero returns! Your reputation precedes you!",
                "Hostile": "You again. I'm watching you. One wrong move...",
                "Hated": "You! I should arrest you on sight. Get out of my sight before I change my mind."
            },
            next_node_id="guard_menu"
        )
        guard_tree.add_node(guard_greeting)
        
        # Guard main menu
        guard_menu = DialogueNode(
            "guard_menu",
            DialogueNodeType.CHOICE,
            choices=[
                DialogueChoice("Any trouble in town?", "town_safety"),
                DialogueChoice("Are there any bounties available?", "bounties"),
                DialogueChoice("What's my reputation around here?", "check_reputation"),
                DialogueChoice("Tell me about the law.", "town_laws"),
                DialogueChoice("I should get going.", None)
            ]
        )
        guard_tree.add_node(guard_menu)
        
        # Town safety information
        town_safety = DialogueNode(
            "town_safety",
            DialogueNodeType.TEXT,
            content="Things have been quiet lately. A few monster sightings outside town, but nothing we can't handle. Just watch yourself if you venture into the wilderness.",
            weather_variants={
                "storm": "Weather like this tends to drive the beasts closer to town. Stay alert.",
                "night": "Nights are when the creatures get bold. Keep your weapon handy."
            },
            next_node_id="guard_menu"
        )
        guard_tree.add_node(town_safety)
        
        # Bounty information
        bounties = DialogueNode(
            "bounties",
            DialogueNodeType.TEXT,
            content="Check the bulletin board at the town hall for current bounties. We post wanted posters for dangerous criminals and monster threats. Good gold for a capable adventurer.",
            next_node_id="guard_menu"
        )
        guard_tree.add_node(bounties)
        
        # Reputation check - this will be dynamic based on player's actual reputation
        check_reputation = DialogueNode(
            "check_reputation",
            DialogueNodeType.TEXT,
            content="You're relatively unknown around here. Keep your nose clean and help the townsfolk, and you'll build a good reputation.",
            reputation_variants={
                "Friendly": "People speak well of you. You've been helpful to the town.",
                "Honored": "You're well-respected here. The townsfolk trust you completely.",
                "Revered": "You're a legend in these parts! Everyone knows your name and deeds.",
                "Exalted": "A true hero of the realm! Bards sing songs of your exploits!",
                "Unfriendly": "You've made some folks nervous. Best watch your step.",
                "Hostile": "Your reputation here is... poor. People don't trust you.",
                "Hated": "You're wanted for crimes against this town. I should arrest you now."
            },
            next_node_id="guard_menu"
        )
        guard_tree.add_node(check_reputation)
        
        # Town laws
        town_laws = DialogueNode(
            "town_laws",
            DialogueNodeType.TEXT,
            content="Simple rules: No stealing, no fighting in town, no disturbing the peace. Break the law and you'll answer to us. Pay your fines or face jail time. We keep this town safe.",
            next_node_id="guard_menu"
        )
        guard_tree.add_node(town_laws)
        
        self.dialogue_trees["guard"] = guard_tree
        
        # Generic NPC dialogue (fallback)
        generic_tree = DialogueTree("generic", "generic_greeting")
        
        generic_greeting = DialogueNode(
            "generic_greeting",
            DialogueNodeType.TEXT,
            content="Hello there! How can I help you?",
            personality_variants={
                "friendly": "Hey! Nice to see you!",
                "busy": "Busy right now, but what do you need?",
                "grumpy": "What do you want?"
            },
            next_node_id="generic_choices"
        )
        generic_tree.add_node(generic_greeting)
        
        generic_choices = DialogueNode(
            "generic_choices",
            DialogueNodeType.CHOICE,
            choices=[
                DialogueChoice("How are you?", "generic_response"),
                DialogueChoice("What do you do here?", "generic_job"),
                DialogueChoice("Farewell.", None)
            ]
        )
        generic_tree.add_node(generic_choices)
        
        generic_response = DialogueNode(
            "generic_response",
            DialogueNodeType.TEXT,
            content="I'm doing well, thank you for asking!",
            next_node_id="generic_choices"
        )
        generic_tree.add_node(generic_response)
        
        generic_job = DialogueNode(
            "generic_job",
            DialogueNodeType.TEXT,
            content="I work here in town. Just doing my part to keep things running smoothly.",
            next_node_id="generic_choices"
        )
        generic_tree.add_node(generic_job)
        
        self.dialogue_trees["generic"] = generic_tree
        
        # Tutorial Guide dialogue tree - dynamic based on player progress
        tutorial_tree = DialogueTree("tutorial_guide", "tutorial_greeting")
        
        # Initial greeting - welcomes new players
        tutorial_greeting = DialogueNode(
            "tutorial_greeting",
            DialogueNodeType.TEXT,
            content="Hey hey hey wait come here and talk a little",
            next_node_id="tutorial_initial_choices"
        )
        tutorial_tree.add_node(tutorial_greeting)
        
        # Initial choices
        tutorial_initial_choices = DialogueNode(
            "tutorial_initial_choices",
            DialogueNodeType.CHOICE,
            choices=[
                DialogueChoice("No, think I'll pass. Its late and I need to get going", "response_polite_decline"),
                DialogueChoice("Fuck off you look like a common poor", "response_rude"),
                DialogueChoice("Uhhhh me? Yeah sure, whats going on?", "response_accept")
            ]
        )
        tutorial_tree.add_node(tutorial_initial_choices)
        
        # Response to polite decline
        response_polite_decline = DialogueNode(
            "response_polite_decline",
            DialogueNodeType.TEXT,
            content="Sorry, to have bothered you please get somewhere safe the world is filled with evil."
        )
        tutorial_tree.add_node(response_polite_decline)
        
        # Response when player talks again after declining
        response_declined_followup = DialogueNode(
            "response_declined_followup",
            DialogueNodeType.TEXT,
            content="Sorry there is no time to talk, you are right we need to get to shelter."
        )
        tutorial_tree.add_node(response_declined_followup)
        
        # Response to rude behavior - NPC will disappear after this
        response_rude = DialogueNode(
            "response_rude",
            DialogueNodeType.TEXT,
            content="If this is how you treat others, you will not get far in these lands."
        )
        tutorial_tree.add_node(response_rude)
        
        # Response to acceptance - explain the situation
        response_accept = DialogueNode(
            "response_accept",
            DialogueNodeType.TEXT,
            content="Good! Listen, these lands are dangerous - far more dangerous than they appear. I'm the Wandering Guide, and I've helped countless travelers find their feet in this world.",
            next_node_id="tutorial_explain_quest"
        )
        tutorial_tree.add_node(response_accept)
        
        # Explain the quest
        tutorial_explain_quest = DialogueNode(
            "tutorial_explain_quest",
            DialogueNodeType.TEXT,
            content="Survival requires resources and the ability to defend yourself. Before you venture far, I need you to learn the basics: First, gather 3 sticks from the ground - break grass and bushes by attacking them. Second, prove you can fight by defeating any 2 enemies.",
            next_node_id="tutorial_offer_quest"
        )
        tutorial_tree.add_node(tutorial_explain_quest)
        
        # Quest offer
        tutorial_offer_quest = DialogueNode(
            "tutorial_offer_quest",
            DialogueNodeType.TEXT,
            content="This might seem simple, but it will teach you the fundamentals. Complete these tasks, and I'll reward you with a proper weapon, healing potions, 100 gold, and valuable experience. Will you do this?",
            next_node_id="tutorial_quest_choice"
        )
        tutorial_tree.add_node(tutorial_offer_quest)
        
        # Quest acceptance choice
        tutorial_quest_choice = DialogueNode(
            "tutorial_quest_choice",
            DialogueNodeType.CHOICE,
            choices=[
                DialogueChoice("I'll do it. Gather sticks and defeat enemies - got it!", "quest_accepted_action"),
                DialogueChoice("I'm not sure... what if I can't handle the enemies?", "quest_hesitation")
            ]
        )
        tutorial_tree.add_node(tutorial_quest_choice)
        
        # Quest accepted - triggers quest acceptance
        quest_accepted_action = DialogueNode(
            "quest_accepted_action",
            DialogueNodeType.ACTION,
            content="Excellent! That's the spirit. Sticks can be found lying on the ground - just walk over them, or break grass and bushes by attacking them. As for enemies, slimes are perfect for beginners. Stay alert, fight smart, and come back when you're done. Good luck out there!",
            action={'type': 'quest_accept', 'quest_id': 'tutorial_basics'}
        )
        tutorial_tree.add_node(quest_accepted_action)
        
        # Quest hesitation - encouragement
        quest_hesitation = DialogueNode(
            "quest_hesitation",
            DialogueNodeType.TEXT,
            content="I understand your worry, but you're stronger than you think. Start with weaker enemies like slimes - they're slow and don't hit too hard. Watch your health, use your healing items if needed, and remember: every great warrior started exactly where you are now.",
            next_node_id="quest_hesitation_choice"
        )
        tutorial_tree.add_node(quest_hesitation)
        
        # Hesitation follow-up choice
        quest_hesitation_choice = DialogueNode(
            "quest_hesitation_choice",
            DialogueNodeType.CHOICE,
            choices=[
                DialogueChoice("You're right. I can do this!", "quest_accepted_action"),
                DialogueChoice("I'll think about it...", "quest_declined_polite")
            ]
        )
        tutorial_tree.add_node(quest_hesitation_choice)
        
        # Quest declined politely
        quest_declined_polite = DialogueNode(
            "quest_declined_polite",
            DialogueNodeType.TEXT,
            content="I see... Well, the offer stands if you change your mind. But be warned: these lands don't forgive the unprepared. Come find me again if you reconsider. Stay safe out there, traveler."
        )
        tutorial_tree.add_node(quest_declined_polite)
        
        # ===== QUEST IN PROGRESS NODES =====
        
        # Quest in progress - collecting sticks
        quest_progress_collecting = DialogueNode(
            "quest_progress_collecting",
            DialogueNodeType.TEXT,
            content="How goes the gathering? Sticks can be found on the ground, or you can break grass and bushes by attacking them. You need 3 sticks total - check your inventory to see how many you have. Come back when you've got them all!"
        )
        tutorial_tree.add_node(quest_progress_collecting)
        
        # Quest in progress - sticks collected, need to equip
        quest_progress_sticks_done = DialogueNode(
            "quest_progress_sticks_done",
            DialogueNodeType.TEXT,
            content="Perfect! You've gathered the sticks. Now open your inventory (press I) and equip one of those sticks - it's not much of a weapon, but it's better than your fists! Select a stick and press ENTER to equip it. Then come back and we'll move to the next step.",
            next_node_id="quest_progress_combat_start"
        )
        tutorial_tree.add_node(quest_progress_sticks_done)
        
        # Ready for combat phase
        quest_progress_combat_start = DialogueNode(
            "quest_progress_combat_start",
            DialogueNodeType.TEXT,
            content="Good! Now for the real test: combat. The world is dangerous, filled with creatures that won't hesitate to attack. Go out there and defeat any 2 enemies. Slimes are easy targets if you can find them. Fight smart, watch your health, and return victorious!"
        )
        tutorial_tree.add_node(quest_progress_combat_start)
        
        # Quest in progress - combat phase
        quest_progress_combat = DialogueNode(
            "quest_progress_combat",
            DialogueNodeType.TEXT,
            content="How goes the combat training? Remember, you need to defeat 2 enemies total. Watch your health bar, use healing potions if you need them (press the number key they're assigned to), and don't be afraid to retreat if you're overwhelmed. You can do this!"
        )
        tutorial_tree.add_node(quest_progress_combat)
        
        # ===== QUEST COMPLETION NODES =====
        
        # Quest complete - congratulations
        quest_complete = DialogueNode(
            "quest_complete",
            DialogueNodeType.TEXT,
            content="Outstanding work, adventurer! You've returned victorious. You've mastered the fundamentals: gathering resources, managing your inventory, equipping gear, and defending yourself in combat. These skills will serve you well in the days ahead.",
            next_node_id="quest_complete_rewards"
        )
        tutorial_tree.add_node(quest_complete)
        
        # Give rewards and complete quest
        quest_complete_rewards = DialogueNode(
            "quest_complete_rewards",
            DialogueNodeType.ACTION,
            content="Take these supplies as a reward - you've earned them. I've given you a Wooden Sword (much better than that stick!), three Health Potions, 100 gold, and valuable experience. Remember: always gather resources when you can, keep your equipment upgraded, fight smart not reckless, and explore everywhere - adventure awaits!",
            action={'type': 'quest_complete', 'quest_id': 'tutorial_basics'}
        )
        tutorial_tree.add_node(quest_complete_rewards)
        
        # ===== POST-TUTORIAL NODES =====
        
        # Post-tutorial greeting
        post_tutorial = DialogueNode(
            "post_tutorial",
            DialogueNodeType.TEXT,
            content="Welcome back! How goes your adventure? I'm always here if you need advice, want to trade stories, or are looking for guidance. What can I help you with today?",
            next_node_id="post_tutorial_choices"
        )
        tutorial_tree.add_node(post_tutorial)
        
        # Post-tutorial conversation choices
        post_tutorial_choices = DialogueNode(
            "post_tutorial_choices",
            DialogueNodeType.CHOICE,
            choices=[
                DialogueChoice("Tell me about this region", "region_info"),
                DialogueChoice("Any tips for survival?", "survival_tips"),
                DialogueChoice("Just passing by", "farewell")
            ]
        )
        tutorial_tree.add_node(post_tutorial_choices)
        
        # Region information
        region_info = DialogueNode(
            "region_info",
            DialogueNodeType.TEXT,
            content="This region is rich with opportunity and danger alike. You'll find towns scattered across the land - safe havens with merchants, blacksmiths, and fellow adventurers. Venture too far into the wilderness, though, and you'll encounter dungeons filled with treasure... and monsters. The day-night cycle affects what you'll find - some creatures only come out at night. Weather matters too - rain helps plants grow faster! Stay curious, stay vigilant."
        )
        tutorial_tree.add_node(region_info)
        
        # Survival tips
        survival_tips = DialogueNode(
            "survival_tips",
            DialogueNodeType.TEXT,
            content="Here are some essentials: Keep your stamina up with food and rest at inns to recover fully. Save your dubloons for important upgrades, but don't hoard everything. Repair your equipment regularly - broken gear is useless. Do quests for fast XP and reputation. Most importantly: know your limits - don't fight enemies way above your level. Explore and experiment - that's how you truly learn!"
        )
        tutorial_tree.add_node(survival_tips)
        
        # Farewell
        farewell = DialogueNode(
            "farewell",
            DialogueNodeType.TEXT,
            content="Safe travels, friend! May the road rise to meet you, and may fortune smile upon your journey. Return anytime you need guidance or just want to chat. Adventure awaits!"
        )
        tutorial_tree.add_node(farewell)
        
        self.dialogue_trees["tutorial_guide"] = tutorial_tree
        
        # Add role-specific dialogue trees that use generic as base
        for role in ["innkeeper", "blacksmith", "mayor", "clerk", "bartender", "patron", "priest", "worshipper", "banker", "resident"]:
            self.dialogue_trees[role] = generic_tree
    
    def start_conversation(self, npc, player, current_weather=None):
        """Start a conversation with an NPC"""
        tree_id = getattr(npc, 'dialogue_tree_id', npc.id)
        
        # Fallback to generic dialogue if tree not found
        if tree_id not in self.dialogue_trees:
            tree_id = "generic"
        
        if tree_id not in self.dialogue_trees:
            return False, "This NPC has nothing to say."
        
        self.current_tree = self.dialogue_trees[tree_id]
        
        # Determine entry point based on NPC and quest state
        entry_node_id = self._get_dynamic_entry_point(npc, player, tree_id)
        
        self.current_node = self.current_tree.get_node(entry_node_id)
        self.current_npc = npc
        self.active_conversation = {
            'npc': npc,
            'player': player,
            'weather': current_weather,
            'reputation_level': self.reputation_system.get_npc_reputation_level(npc.id)
        }
        
        return True, "Conversation started"
    
    def _get_dynamic_entry_point(self, npc, player, tree_id):
        """Determine which dialogue node to start at based on game state"""
        # Special handling for tutorial guide
        if tree_id == "tutorial_guide":
            # Check if quest is complete
            if hasattr(player, 'tutorial_completed') and player.tutorial_completed:
                return "post_tutorial"
            
            # Check if quest is in active_quests
            if 'tutorial_basics' in self.quest_manager.active_quests:
                quest = self.quest_manager.active_quests['tutorial_basics']
                
                # Check objectives
                stick_objective_complete = False
                enemy_objective_complete = False
                
                for obj in quest.objectives:
                    if obj.type.name == 'COLLECT' and obj.target == 'stick':
                        stick_objective_complete = obj.current_count >= obj.required_count
                    elif obj.type.name == 'KILL' and obj.target == 'any':
                        enemy_objective_complete = obj.current_count >= obj.required_count
                
                # Both objectives complete - ready to turn in
                if stick_objective_complete and enemy_objective_complete:
                    return "quest_complete"
                
                # Sticks done, working on combat
                elif stick_objective_complete:
                    return "quest_progress_combat"
                
                # Still collecting sticks
                else:
                    # Check if they have 3 sticks in inventory even if not turned in
                    stick_count = player.inventory.get('stick', 0)
                    if stick_count >= 3:
                        return "quest_progress_sticks_done"
                    else:
                        return "quest_progress_collecting"
            
            # Check if player declined before
            if hasattr(npc, 'declined_by_player') and npc.declined_by_player:
                if not hasattr(npc, 'going_to_shelter') or not npc.going_to_shelter:
                    return "response_declined_followup"
            
            # Default: initial greeting
            return self.current_tree.start_node_id
        
        # For other NPCs, use default start node
        return self.current_tree.start_node_id
    
    def get_current_text(self):
        """Get the current dialogue text"""
        if not self.current_node:
            return None
        
        npc_personality = getattr(self.current_npc, 'personality', None)
        current_weather = self.active_conversation.get('weather')
        reputation_level = self.active_conversation.get('reputation_level')
        
        return self.current_node.get_text(npc_personality, current_weather, reputation_level)
    
    def get_current_choices(self, player):
        """Get available choices for current node"""
        if not self.current_node or self.current_node.type != DialogueNodeType.CHOICE:
            return []
        
        choices_with_availability = []
        for choice in self.current_node.choices:
            can_choose, requirement_text = choice.can_choose(
                player, 
                self.reputation_system, 
                self.current_npc.id if self.current_npc else None
            )
            choices_with_availability.append({
                'choice': choice,
                'available': can_choose,
                'requirement_text': requirement_text
            })
        
        return choices_with_availability
    
    def choose_option(self, choice_index, player):
        """Player chooses a dialogue option"""
        if not self.current_node or self.current_node.type != DialogueNodeType.CHOICE:
            return False, "No choices available"
        
        choices = self.get_current_choices(player)
        if choice_index >= len(choices):
            return False, "Invalid choice"
        
        choice_data = choices[choice_index]
        choice = choice_data['choice']
        
        if not choice_data['available']:
            return False, "Requirements not met"
        
        # Apply consequences
        if choice.consequences:
            if 'reputation' in choice.consequences:
                self.reputation_system.modify_npc_reputation(
                    self.current_npc.id, 
                    choice.consequences['reputation']
                )
            if 'gold' in choice.consequences:
                player.dubloons += choice.consequences['gold']
        
        # Move to next node
        if choice.next_node_id is None:
            # End conversation
            self.last_visited_node_id = self.current_node.id if self.current_node else None
            self.end_conversation()
            return True, "Conversation ended"
        
        next_node = self.current_tree.get_node(choice.next_node_id)
        if not next_node:
            self.last_visited_node_id = self.current_node.id if self.current_node else None
            self.end_conversation()
            return True, "Conversation ended"
        
        self.current_node = next_node
        self.last_visited_node_id = next_node.id  # Track the node we just moved to
        
        # Handle action nodes
        if self.current_node.type == DialogueNodeType.ACTION:
            return self._handle_action(player)
        
        return True, "Choice made"
    
    def _handle_action(self, player):
        """Handle action nodes"""
        if not self.current_node.action:
            return True, "No action"
        
        action_type = self.current_node.action.get('type')
        
        if action_type == 'quest_accept':
            quest_id = self.current_node.action.get('quest_id')
            success, message = self.quest_manager.accept_quest(quest_id, player)
            # Set tutorial stage when accepting tutorial quest
            if quest_id == 'tutorial_basics' and success:
                player.tutorial_stage = 'accepted'
                player.tutorial_active = True
            # Return special flag to auto-close dialogue
            return True, "quest_accepted_auto_close"
        
        elif action_type == 'quest_complete':
            quest_id = self.current_node.action.get('quest_id')
            # Complete the quest and give rewards
            if quest_id == 'tutorial_basics':
                if quest_id in self.quest_manager.active_quests:
                    self.quest_manager.complete_quest(quest_id)
                # Give tutorial rewards
                from equipment import create_equipment
                wooden_sword = create_equipment('Wooden Sword', 'weapon')
                player.add_item(wooden_sword)
                player.inventory['Health Potion'] = player.inventory.get('Health Potion', 0) + 3
                player.experience += 50
                player.dubloons += 100
                player.tutorial_stage = 'complete'
                player.tutorial_completed = True
                # Return special flag to auto-close dialogue
                return True, "quest_completed_auto_close"
            return True, "Quest completed"
        
        elif action_type == 'shop':
            # Shop opening will be handled by the UI
            return True, "shop"
        
        return True, "Action completed"
    
    def advance_conversation(self):
        """Move to next node after TEXT node"""
        if not self.current_node or self.current_node.type != DialogueNodeType.TEXT:
            return False
        
        # Check if there's a next node defined
        if not self.current_node.next_node_id:
            # No next node, end conversation
            self.end_conversation()
            return False
        
        # Move to next node
        next_node = self.current_tree.get_node(self.current_node.next_node_id)
        if not next_node:
            self.end_conversation()
            return False
        
        self.current_node = next_node
        return True
    
    def end_conversation(self):
        """End the current conversation"""
        if self.active_conversation and self.current_npc:
            # Add to history
            import time
            self.conversation_history.append({
                'npc_name': getattr(self.current_npc, 'name', 'Unknown'),
                'timestamp': time.time(),
                'summary': f"Spoke with {getattr(self.current_npc, 'name', 'Unknown')}"
            })
        
        self.active_conversation = None
        self.current_tree = None
        self.current_node = None
        self.current_npc = None
    
    def is_in_conversation(self):
        """Check if currently in a conversation"""
        return self.active_conversation is not None
