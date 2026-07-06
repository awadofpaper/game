"""
NPC Interaction Tracking System
Tracks positive interactions between NPCs for relationships, marriage, and family formation
"""
import time

class NPCInteraction:
    """Represents a single interaction between two NPCs"""
    def __init__(self, npc_a_id, npc_b_id, interaction_type, timestamp, value=1):
        self.npc_a_id = npc_a_id
        self.npc_b_id = npc_b_id
        self.interaction_type = interaction_type  # e.g., 'trade', 'help', 'gift', 'defend', 'quest', 'pay_fee', 'trade_route'
        self.timestamp = timestamp  # In-game day
        self.value = value  # Positive value for positive interaction

class NPCRelationship:
    """Tracks cumulative positive interactions between two NPCs"""
    def __init__(self, npc_a_id, npc_b_id):
        self.npc_a_id = npc_a_id
        self.npc_b_id = npc_b_id
        self.positive_score = 0  # Sum of positive interactions
        self.interactions = []  # List of NPCInteraction objects
        self.last_interaction_time = None

    def add_interaction(self, interaction: NPCInteraction):
        self.interactions.append(interaction)
        self.positive_score += interaction.value
        self.last_interaction_time = interaction.timestamp

    def decay_score(self, current_time, decay_days=730):
        """Decay positive score for interactions older than decay_days (default 2 years)"""
        self.interactions = [i for i in self.interactions if current_time - i.timestamp <= decay_days]
        self.positive_score = sum(i.value for i in self.interactions)

class NPCInteractionSystem:
    """Manages all NPC relationships and interactions"""
    def __init__(self, game_time):
        self.game_time = game_time
        self.relationships = {}  # {(npc_a_id, npc_b_id): NPCRelationship}

    def add_interaction(self, npc_a_id, npc_b_id, interaction_type, value=1):
        """
        Add a positive interaction between two NPCs
        """
        # Validate inputs - reject None values
        if npc_a_id is None or npc_b_id is None:
            return  # Silently ignore invalid interactions
        if not npc_a_id or not npc_b_id:  # Also reject empty strings
            return
        
        current_time = self.game_time.day_count if self.game_time else 0
        key = tuple(sorted([npc_a_id, npc_b_id]))
        if key not in self.relationships:
            self.relationships[key] = NPCRelationship(*key)
        interaction = NPCInteraction(npc_a_id, npc_b_id, interaction_type, current_time, value)
        self.relationships[key].add_interaction(interaction)

    def get_relationship_score(self, npc_a_id, npc_b_id):
        # Return 0 for None or empty values
        if npc_a_id is None or npc_b_id is None:
            return 0
        if not npc_a_id or not npc_b_id:
            return 0
        
        key = tuple(sorted([npc_a_id, npc_b_id]))
        if key in self.relationships:
            return self.relationships[key].positive_score
        return 0

    def get_relationship(self, npc_a_id, npc_b_id):
        # Return None for invalid inputs
        if npc_a_id is None or npc_b_id is None:
            return None
        if not npc_a_id or not npc_b_id:
            return None
        
        key = tuple(sorted([npc_a_id, npc_b_id]))
        return self.relationships.get(key)

    def update(self):
        """
        Decay old interactions for all relationships (called daily)
        """
        current_time = self.game_time.day_count if self.game_time else 0
        for rel in self.relationships.values():
            rel.decay_score(current_time)

    def get_top_relationships(self, npc_id, min_score=1000):
        """
        Get all relationships for an NPC with score above min_score
        """
        if npc_id is None or not npc_id:
            return []
        return [rel for rel in self.relationships.values() if (rel.npc_a_id == npc_id or rel.npc_b_id == npc_id) and rel.positive_score >= min_score]

    def get_all_relationships(self, npc_id):
        """
        Get all relationships for an NPC
        """
        if npc_id is None or not npc_id:
            return []
        return [rel for rel in self.relationships.values() if rel.npc_a_id == npc_id or rel.npc_b_id == npc_id]
