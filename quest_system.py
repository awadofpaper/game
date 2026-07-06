"""
Quest System - Manage quests, objectives, and progression
"""

import random
from enum import Enum

class QuestType(Enum):
    MAIN = "main"
    SIDE = "side"

class QuestCategory(Enum):
    TUTORIAL = "tutorial"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    RESCUE = "rescue"
    DELIVERY = "delivery"
    DIALOGUE = "dialogue"
    MISCELLANEOUS = "misc"

class QuestState(Enum):
    AVAILABLE = "available"  # Can be accepted
    ACTIVE = "active"  # Currently working on
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"  # Failed to complete
    TURNED_IN = "turned_in"  # Rewards claimed

class ObjectiveType(Enum):
    KILL = "kill"
    TALK = "talk"
    REACH = "reach"
    COLLECT = "collect"
    RESCUE = "rescue"
    ESCORT = "escort"
    SURVIVE = "survive"

class QuestObjective:
    """Individual quest objective"""
    
    def __init__(self, objective_type, description, target=None, count=1, location=None, optional=False):
        self.type = objective_type
        self.description = description
        self.target = target  # Enemy type, NPC id, item name, etc
        self.required_count = count
        self.current_count = 0
        self.location = location  # (x, y) for reach objectives
        self.optional = optional
        self.completed = False
        
    def update_progress(self, amount=1):
        """Update objective progress"""
        self.current_count = min(self.current_count + amount, self.required_count)
        if self.current_count >= self.required_count:
            self.completed = True
        return self.completed
    
    def get_progress_text(self):
        """Get progress as text"""
        if self.type == ObjectiveType.REACH:
            return f"{'[OPTIONAL] ' if self.optional else ''}{self.description}"
        else:
            return f"{'[OPTIONAL] ' if self.optional else ''}{self.description}: {self.current_count}/{self.required_count}"

class Quest:
    """Individual quest data"""
    
    def __init__(self, quest_id, name, description, quest_type, category, 
                 giver_npc_id=None, objectives=None, rewards=None, 
                 required_reputation=0, reputation_rewards=None, level_requirement=0,
                 prerequisite_quests=None):
        self.id = quest_id
        self.name = name
        self.description = description
        self.quest_type = quest_type  # QuestType.MAIN or SIDE
        self.category = category  # QuestCategory enum
        self.giver_npc_id = giver_npc_id
        self.objectives = objectives or []
        self.rewards = rewards or {'xp': 0, 'gold': 0, 'items': []}
        self.required_reputation = required_reputation
        self.reputation_rewards = reputation_rewards or {}  # {npc_id/faction: amount}
        self.level_requirement = level_requirement
        self.prerequisite_quests = prerequisite_quests or []
        
        self.state = QuestState.AVAILABLE
        self.tracked = True  # Show in tracker by default
        
    def can_accept(self, player, reputation_system):
        """Check if player can accept this quest"""
        # Check level requirement
        if player.level < self.level_requirement:
            return False, f"Requires level {self.level_requirement}"
        
        # Check prerequisite quests
        for prereq_id in self.prerequisite_quests:
            if prereq_id not in player.completed_quests:
                return False, "Complete prerequisite quests first"
        
        # Check reputation requirement
        if self.giver_npc_id and self.required_reputation > 0:
            if not reputation_system.can_access_quest(self.required_reputation, npc_id=self.giver_npc_id):
                rep_level = reputation_system.get_reputation_level(self.required_reputation)
                return False, f"Requires {rep_level} reputation"
        
        return True, "Can accept"
    
    def accept_quest(self):
        """Accept the quest"""
        self.state = QuestState.ACTIVE
        
    def is_completed(self):
        """Check if all required objectives are done"""
        for obj in self.objectives:
            if not obj.optional and not obj.completed:
                return False
        return True
    
    def complete_quest(self):
        """Mark quest as completed"""
        if self.is_completed():
            self.state = QuestState.COMPLETED
            return True
        return False
    
    def turn_in_quest(self, player, reputation_system):
        """Turn in quest and claim rewards"""
        if self.state != QuestState.COMPLETED:
            return False, "Quest not completed"
        
        # Give XP
        if 'xp' in self.rewards and self.rewards['xp'] > 0:
            player.gain_experience(self.rewards['xp'])
        
        # Give gold
        if 'gold' in self.rewards and self.rewards['gold'] > 0:
            gold_reward = self.rewards['gold']
            
            # Apply racial quest gold modifiers (Human: +10%)
            if hasattr(player, 'trait_manager') and player.trait_manager:
                modified_gold = player.trait_manager.apply_quest_gold_modifier(gold_reward)
                if modified_gold != gold_reward:
                    import logging
                    logger = logging.getLogger(__name__)
                    bonus = modified_gold - gold_reward
                    logger.info(f"[RACIAL TRAIT] Quest gold bonus: {gold_reward} → {modified_gold} (+{bonus})")
                gold_reward = modified_gold
            
            player.dubloons += gold_reward
        
        # Give items
        if 'items' in self.rewards:
            for item in self.rewards['items']:
                player.add_item(item)
        
        # Give reputation
        for entity, amount in self.reputation_rewards.items():
            if entity.startswith('faction_'):
                faction_name = entity.replace('faction_', '')
                reputation_system.modify_faction_reputation(faction_name, amount)
            else:
                reputation_system.modify_npc_reputation(entity, amount)
        
        self.state = QuestState.TURNED_IN
        if not hasattr(player, 'completed_quests'):
            player.completed_quests = set()
        player.completed_quests.add(self.id)
        
        return True, "Quest completed!"

class QuestManager:
    """Manages all quests in the game"""
    
    def __init__(self, reputation_system):
        self.reputation_system = reputation_system
        self.all_quests = {}  # All quest definitions
        self.active_quests = {}  # Currently active quests
        self.completed_quests = set()  # IDs of completed quests
        
        # Initialize with some starter quests
        self._create_starter_quests()
    
    def _create_starter_quests(self):
        """Create initial quests"""
        
        # Tutorial quest - teaches basic mechanics
        tutorial_quest = Quest(
            quest_id="tutorial_basics",
            name="First Steps",
            description="Learn the fundamental skills every adventurer needs to survive in this dangerous world.",
            quest_type=QuestType.MAIN,
            category=QuestCategory.TUTORIAL,
            giver_npc_id="tutorial_guide",
            objectives=[
                QuestObjective(ObjectiveType.COLLECT, "Find 3 sticks", target="stick", count=3),
                QuestObjective(ObjectiveType.KILL, "Defeat 2 enemies", target="any", count=2)
            ],
            rewards={'xp': 50, 'gold': 100, 'items': ['Wooden Sword', 'Health Potion', 'Health Potion', 'Health Potion']},
            reputation_rewards={'tutorial_guide': 50}
        )
        self.all_quests[tutorial_quest.id] = tutorial_quest
        
        # The hilarious kill quest (EXACTLY as requested)
        kill_quest = Quest(
            quest_id="absolutely_vital_mission",
            name="The Most Important Mission Ever",
            description='Well Please go Dark Forest and kill these 10 slimes, This is possibly the most important thing you can do in these lands, NOTHING and i mean NOTHING will help the people here then to kill 10 random things and return to ONLY tell me about it and no one else, this absolutley will not waste your time i promise you',
            quest_type=QuestType.SIDE,
            category=QuestCategory.COMBAT,
            giver_npc_id="quest_giver_1",
            objectives=[
                QuestObjective(ObjectiveType.KILL, "Slay slimes in Dark Forest", target="slime", count=10)
            ],
            rewards={'xp': 100, 'gold': 50},
            reputation_rewards={'quest_giver_1': 25, 'faction_townspeople': 10}
        )
        self.all_quests[kill_quest.id] = kill_quest
        
        # Welcome quest - talk to townspeople
        welcome_quest = Quest(
            quest_id="meet_the_locals",
            name="Meet the Locals",
            description="New to town? Let me introduce you to some of the fine folk around here. They'll help you get your bearings.",
            quest_type=QuestType.SIDE,
            category=QuestCategory.DIALOGUE,
            giver_npc_id="town_elder",
            objectives=[
                QuestObjective(ObjectiveType.TALK, "Speak with the Blacksmith", target="blacksmith"),
                QuestObjective(ObjectiveType.TALK, "Speak with the Innkeeper", target="innkeeper"),
                QuestObjective(ObjectiveType.TALK, "Speak with the Merchant", target="merchant")
            ],
            rewards={'xp': 50, 'gold': 20},
            reputation_rewards={'faction_townspeople': 25}
        )
        self.all_quests[welcome_quest.id] = welcome_quest
        
        # Rescue quest
        rescue_quest = Quest(
            quest_id="rescue_traveler",
            name="Lost Traveler",
            description="A traveler was heading to the caves but hasn't returned. If you find them, help them get back safely - though I warn you, the journey back won't be easy.",
            quest_type=QuestType.SIDE,
            category=QuestCategory.RESCUE,
            giver_npc_id="town_elder",
            objectives=[
                QuestObjective(ObjectiveType.REACH, "Find the traveler in the caves", location=(2000, 1500)),
                QuestObjective(ObjectiveType.ESCORT, "Help the traveler return safely", target="lost_traveler")
            ],
            rewards={'xp': 200, 'gold': 100, 'items': []},
            reputation_rewards={'town_elder': 50, 'faction_townspeople': 30},
            level_requirement=3
        )
        self.all_quests[rescue_quest.id] = rescue_quest
        
        # Delivery quest
        delivery_quest = Quest(
            quest_id="urgent_delivery",
            name="Urgent Delivery",
            description="I need someone trustworthy to deliver this package to the merchant in the eastern village. It's important it arrives safely.",
            quest_type=QuestType.SIDE,
            category=QuestCategory.DELIVERY,
            giver_npc_id="blacksmith",
            objectives=[
                QuestObjective(ObjectiveType.TALK, "Deliver package to eastern merchant", target="eastern_merchant")
            ],
            rewards={'xp': 75, 'gold': 40},
            reputation_rewards={'blacksmith': 35, 'eastern_merchant': 20}
        )
        self.all_quests[delivery_quest.id] = delivery_quest
        
        # Exploration quest
        exploration_quest = Quest(
            quest_id="explore_ruins",
            name="Ancient Ruins",
            description="Strange ruins have been spotted to the north. Explore them and report back what you find.",
            quest_type=QuestType.MAIN,
            category=QuestCategory.EXPLORATION,
            giver_npc_id="town_elder",
            objectives=[
                QuestObjective(ObjectiveType.REACH, "Reach the ancient ruins", location=(1000, 500)),
                QuestObjective(ObjectiveType.REACH, "Investigate the shrine", location=(1050, 450), optional=True)
            ],
            rewards={'xp': 150, 'gold': 75, 'items': []},
            reputation_rewards={'town_elder': 40, 'faction_townspeople': 20},
            level_requirement=2
        )
        self.all_quests[exploration_quest.id] = exploration_quest
    
    def get_available_quests(self, player):
        """Get quests that player can accept"""
        available = []
        for quest_id, quest in self.all_quests.items():
            if quest.state == QuestState.AVAILABLE and quest_id not in self.active_quests:
                can_accept, _ = quest.can_accept(player, self.reputation_system)
                if can_accept:
                    available.append(quest)
        return available
    
    def get_active_quests(self):
        """Get currently active quests"""
        return list(self.active_quests.values())
    
    def get_tracked_quests(self):
        """Get quests that should be shown in tracker"""
        return [q for q in self.active_quests.values() if q.tracked]
    
    def accept_quest(self, quest_id, player):
        """Accept a quest"""
        if quest_id not in self.all_quests:
            return False, "Quest not found"
        
        quest = self.all_quests[quest_id]
        can_accept, reason = quest.can_accept(player, self.reputation_system)
        
        if not can_accept:
            return False, reason
        
        quest.accept_quest()
        self.active_quests[quest_id] = quest
        return True, f"Accepted: {quest.name}"
    
    def complete_quest(self, quest_id):
        """Complete a quest"""
        if quest_id not in self.active_quests:
            return False, "Quest not active"
        
        quest = self.active_quests[quest_id]
        if quest.complete_quest():
            return True, f"Quest completed: {quest.name}"
        return False, "Objectives not complete"
    
    def turn_in_quest(self, quest_id, player):
        """Turn in a completed quest"""
        if quest_id not in self.active_quests:
            return False, "Quest not active"
        
        quest = self.active_quests[quest_id]
        success, message = quest.turn_in_quest(player, self.reputation_system)
        
        if success:
            self.completed_quests.add(quest_id)
            del self.active_quests[quest_id]
        
        return success, message
    
    def update_objective(self, objective_type, target, amount=1):
        """Update quest objectives (called when player does something)"""
        completed_quests = []
        
        for quest_id, quest in self.active_quests.items():
            if quest.state != QuestState.ACTIVE:
                continue
            
            for obj in quest.objectives:
                if obj.completed:
                    continue
                
                # Check if this action matches the objective
                if obj.type == objective_type and obj.target == target:
                    obj.update_progress(amount)
            
            # Check if quest is now complete
            if quest.is_completed() and quest.state == QuestState.ACTIVE:
                quest.complete_quest()
                completed_quests.append(quest.name)
        
        return completed_quests
    
    def toggle_quest_tracking(self, quest_id):
        """Toggle whether a quest is shown in tracker"""
        if quest_id in self.active_quests:
            quest = self.active_quests[quest_id]
            quest.tracked = not quest.tracked
            return quest.tracked
        return False
