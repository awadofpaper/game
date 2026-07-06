"""
Reputation System - Track player standing with NPCs and Factions
"""

class ReputationSystem:
    """Manages player reputation with individual NPCs and factions"""
    
    # Reputation levels and thresholds
    REPUTATION_LEVELS = {
        'Hated': -1000,
        'Hostile': -500,
        'Unfriendly': -100,
        'Neutral': 0,
        'Friendly': 100,
        'Honored': 500,
        'Revered': 1000,
        'Exalted': 2000
    }
    
    def __init__(self):
        self.npc_reputation = {}  # {npc_id: reputation_points}
        self.faction_reputation = {}  # {faction_name: reputation_points}
        
    def get_npc_reputation(self, npc_id):
        """Get reputation points with specific NPC"""
        return self.npc_reputation.get(npc_id, 0)
    
    def get_faction_reputation(self, faction_name):
        """Get reputation points with faction"""
        return self.faction_reputation.get(faction_name, 0)
    
    def modify_npc_reputation(self, npc_id, amount):
        """Change reputation with an NPC"""
        current = self.npc_reputation.get(npc_id, 0)
        self.npc_reputation[npc_id] = current + amount
        
        # Cap at extremes
        self.npc_reputation[npc_id] = max(-1000, min(2500, self.npc_reputation[npc_id]))
        
        return self.npc_reputation[npc_id]
    
    def modify_faction_reputation(self, faction_name, amount):
        """Change reputation with a faction"""
        current = self.faction_reputation.get(faction_name, 0)
        self.faction_reputation[faction_name] = current + amount
        
        # Cap at extremes
        self.faction_reputation[faction_name] = max(-1000, min(2500, self.faction_reputation[faction_name]))
        
        return self.faction_reputation[faction_name]
    
    def get_reputation_level(self, reputation_points):
        """Convert reputation points to level name"""
        for level, threshold in reversed(list(self.REPUTATION_LEVELS.items())):
            if reputation_points >= threshold:
                return level
        return 'Neutral'
    
    def get_npc_reputation_level(self, npc_id):
        """Get reputation level name with NPC"""
        points = self.get_npc_reputation(npc_id)
        return self.get_reputation_level(points)
    
    def get_faction_reputation_level(self, faction_name):
        """Get reputation level name with faction"""
        points = self.get_faction_reputation(faction_name)
        return self.get_reputation_level(points)
    
    def get_price_modifier(self, npc_id=None, faction_name=None):
        """Calculate price modifier based on reputation (1.0 = normal, 0.8 = 20% discount, 1.5 = 50% markup)"""
        reputation = 0
        
        if npc_id:
            reputation = max(reputation, self.get_npc_reputation(npc_id))
        
        if faction_name:
            reputation = max(reputation, self.get_faction_reputation(faction_name))
        
        # Calculate modifier
        if reputation >= 1000:  # Revered+
            return 0.7  # 30% discount
        elif reputation >= 500:  # Honored
            return 0.8  # 20% discount
        elif reputation >= 100:  # Friendly
            return 0.9  # 10% discount
        elif reputation >= -100:  # Neutral/Unfriendly
            return 1.0  # Normal price
        elif reputation >= -500:  # Hostile
            return 1.3  # 30% markup
        else:  # Hated
            return 1.5  # 50% markup
    
    def can_access_quest(self, required_reputation, npc_id=None, faction_name=None):
        """Check if player meets reputation requirement for quest"""
        reputation = 0
        
        if npc_id:
            reputation = self.get_npc_reputation(npc_id)
        
        if faction_name:
            reputation = max(reputation, self.get_faction_reputation(faction_name))
        
        return reputation >= required_reputation
    
    def get_dialogue_attitude(self, npc_id=None, faction_name=None):
        """Get NPC dialogue attitude based on reputation"""
        reputation = 0
        
        if npc_id:
            reputation = self.get_npc_reputation(npc_id)
        
        if faction_name:
            reputation = max(reputation, self.get_faction_reputation(faction_name))
        
        if reputation >= 1000:
            return 'adoring'
        elif reputation >= 500:
            return 'respectful'
        elif reputation >= 100:
            return 'friendly'
        elif reputation >= -100:
            return 'neutral'
        elif reputation >= -500:
            return 'rude'
        else:
            return 'hostile'
