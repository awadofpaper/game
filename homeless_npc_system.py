"""
Homeless NPC System
Tracks NPCs without homes, supports wandering, shelter seeking, and integration with adoption/family systems.
"""
import random

class HomelessNPC:
    def __init__(self, npc_id, name, age, last_home_day=None):
        self.npc_id = npc_id
        self.name = name
        self.age = age
        self.last_home_day = last_home_day  # Last day NPC had a home
        self.is_homeless = True
        self.shelter_building_id = None
        self.shelter_town = None
        self.days_homeless = 0
        self.wandering = True
        self.adopted = False

class HomelessNPCSystem:
    def __init__(self, game_time, town_manager, npc_family_system):
        self.game_time = game_time
        self.town_manager = town_manager
        self.npc_family_system = npc_family_system
        self.homeless_npcs = {}  # {npc_id: HomelessNPC}

    def add_homeless_npc(self, npc_id, name, age):
        npc = HomelessNPC(npc_id, name, age, last_home_day=self.game_time.day_count)
        self.homeless_npcs[npc_id] = npc
        return npc

    def update(self):
        # Called daily to update homeless NPCs
        for npc in self.homeless_npcs.values():
            npc.days_homeless = self.game_time.day_count - (npc.last_home_day or 0)
            # Try to find shelter in a town
            if npc.wandering:
                for town in self.town_manager.towns:
                    for building in town.buildings:
                        if building.type in ['INN', 'TAVERN', 'TEMPLE']:
                            # Homeless NPC can seek shelter
                            npc.shelter_building_id = building.id
                            npc.shelter_town = town.name
                            npc.wandering = False
                            break
                    if not npc.wandering:
                        break
            # Optionally: trigger adoption if child and orphan
            if npc.age < 18 and self.npc_family_system.is_orphan(npc.npc_id):
                adopter_id = self.find_adopter()
                if adopter_id:
                    adopted = self.npc_family_system.adopt_child(adopter_id, npc.npc_id)
                    if adopted:
                        npc.adopted = True
                        npc.is_homeless = False

    def find_adopter(self):
        # Find eligible NPCs to adopt
        for npc_id, fam in self.npc_family_system.families.items():
            if len(fam.children_ids) + len(fam.adopted_children_ids) < self.npc_family_system.max_children:
                return npc_id
        return None

    def get_homeless_npcs(self):
        return [npc for npc in self.homeless_npcs.values() if npc.is_homeless]

    def get_sheltered_npcs(self):
        return [npc for npc in self.homeless_npcs.values() if not npc.wandering and npc.shelter_building_id]
