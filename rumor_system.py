"""
Rumor System
Handles spreading of information (rumors) between NPCs and to the player
"""
import time

class Rumor:
    """Represents a single rumor/event in the world"""
    def __init__(self, rumor_id, text, origin_npc, start_time, duration_days=30):
        self.rumor_id = rumor_id
        self.text = text
        self.origin_npc = origin_npc
        self.start_time = start_time  # In-game day rumor started
        self.duration_days = duration_days  # How long rumor spreads (default 1 month)
        self.npcs_heard = set([origin_npc])  # NPCs who know the rumor
        self.player_heard = False
        self.expired = False

    def is_active(self, current_time):
        return not self.expired and (current_time - self.start_time) < self.duration_days

    def mark_expired(self):
        self.expired = True

class RumorSystem:
    """Manages all rumors in the world and their spread"""
    def __init__(self, game_time):
        self.game_time = game_time
        self.rumors = {}  # {rumor_id: Rumor}
        self.next_rumor_id = 1

    def create_rumor(self, text, origin_npc, duration_days=30):
        rumor_id = f"RUMOR-{self.next_rumor_id}"
        self.next_rumor_id += 1
        start_time = self.game_time.day_count if self.game_time else 0
        rumor = Rumor(rumor_id, text, origin_npc, start_time, duration_days)
        self.rumors[rumor_id] = rumor
        return rumor

    def spread_rumors(self, npcs):
        """
        Spread rumors between NPCs (called daily)
        Each day, each NPC who knows a rumor can tell 1-2 other NPCs in their town
        """
        current_time = self.game_time.day_count if self.game_time else 0
        for rumor in self.rumors.values():
            if not rumor.is_active(current_time):
                rumor.mark_expired()
                continue
            # For each NPC who knows the rumor, spread to 1-2 others
            new_heard = set()
            for npc in rumor.npcs_heard:
                # Find up to 2 NPCs in same town who don't know rumor
                if hasattr(npc, 'town'):
                    town_npcs = [n for n in npcs if hasattr(n, 'town') and n.town == npc.town and n not in rumor.npcs_heard]
                    to_tell = town_npcs[:2]
                    for n in to_tell:
                        new_heard.add(n)
            rumor.npcs_heard.update(new_heard)

    def player_hear_rumor(self, player, rumor_id):
        """
        Player hears a rumor (by talking to an NPC who knows it)
        """
        if rumor_id in self.rumors:
            self.rumors[rumor_id].player_heard = True

    def get_active_rumors_for_player(self):
        """
        Get all rumors the player can hear (not expired, not yet heard)
        """
        current_time = self.game_time.day_count if self.game_time else 0
        return [r for r in self.rumors.values() if r.is_active(current_time) and not r.player_heard]

    def get_rumors_known_by_npc(self, npc):
        """
        Get all rumors an NPC knows
        """
        current_time = self.game_time.day_count if self.game_time else 0
        return [r for r in self.rumors.values() if r.is_active(current_time) and npc in r.npcs_heard]

    def update(self, npcs):
        """
        Call daily to spread rumors and expire old ones
        """
        self.spread_rumors(npcs)
        # Expire old rumors
        current_time = self.game_time.day_count if self.game_time else 0
        for rumor in self.rumors.values():
            if not rumor.is_active(current_time):
                rumor.mark_expired()
