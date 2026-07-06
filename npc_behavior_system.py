"""
NPC Behavior System
Handles personality types, abandonment, aging, pregnancy, memory, decision formulas, merchant leaving, and wilderness survival.
"""
import random
import time

PERSONALITY_TYPES = ["Honest", "Corrupt", "Opportunist", "Cowardly", "Brave", "Greedy"]

class NPC:
    def __init__(self, npc_id, name, age=None):
        self.npc_id = npc_id
        self.name = name
        self.personality = random.choice(PERSONALITY_TYPES)
        self.age = age if age is not None else random.randint(18, 60)
        self.children = []
        self.spouse_id = None
        self.memory = []  # List of (event, day)
        self.memory_duration = 180  # 6 months in days
        self.pregnant = False
        self.pregnancy_start_day = None
        self.in_jail = False
        self.jail_time = 0
        self.equipment = {}
        self.combat_stats = {'strength': 10, 'endurance': 10, 'stealth': 5}
        self.is_merchant = False
        self.stock_level = 100
        self.in_town = True
        self.danger_level = 0
        self.survival_skills = {'crafting': 5, 'fighting': 5, 'selling': 5}
        self.is_shady_merchant = False

    def abandon_family(self, reason):
        # Divorce, murder, move towns
        if reason == 'divorce':
            self.spouse_id = None
        elif reason == 'murder':
            self.children = []
        elif reason == 'move':
            self.in_town = False

    def age_up(self, game_time):
        self.age += 1 / 365  # Age up linearly per day
        for child in self.children:
            child.age += 1 / 365

    def start_pregnancy(self, game_time):
        self.pregnant = True
        self.pregnancy_start_day = game_time.day_count

    def update_pregnancy(self, game_time):
        if self.pregnant and self.pregnancy_start_day is not None:
            if game_time.day_count - self.pregnancy_start_day >= 270:  # 9 months
                # Birth child
                child = NPC(f"CHILD-{self.npc_id}-{random.randint(1000,9999)}", "Child", age=0)
                self.children.append(child)
                self.pregnant = False
                self.pregnancy_start_day = None

    def remember_event(self, event, game_time):
        self.memory.append((event, game_time.day_count))

    def update_memory(self, game_time):
        self.memory = [(e, d) for (e, d) in self.memory if game_time.day_count - d < self.memory_duration]

    def make_decision(self):
        # Decision formula: personality + equipment + combat stats + jail time
        score = 0
        if self.personality == "Brave":
            score += self.combat_stats['strength']
        if self.personality == "Cowardly":
            score -= self.jail_time
        if self.personality == "Greedy":
            score += self.stock_level
        score += sum(self.equipment.values()) if self.equipment else 0
        return score

    def merchant_leave_town(self):
        # Based on personality + danger + stock
        if self.is_merchant:
            if self.personality in ["Cowardly", "Opportunist"] and self.danger_level > 5:
                self.in_town = False
            elif self.stock_level < 20:
                self.in_town = False

    def wilderness_survival(self):
        # Craft, fight, sell loot
        if not self.in_town:
            self.survival_skills['crafting'] += random.randint(0, 2)
            self.survival_skills['fighting'] += random.randint(0, 2)
            self.survival_skills['selling'] += random.randint(0, 2)

class NPCBehaviorSystem:
    def __init__(self, game_time):
        self.game_time = game_time
        self.npcs = {}  # {npc_id: NPC}

    def add_npc(self, npc_id, name, age=None, is_merchant=False, is_shady_merchant=False):
        npc = NPC(npc_id, name, age)
        npc.is_merchant = is_merchant
        npc.is_shady_merchant = is_shady_merchant
        self.npcs[npc_id] = npc
        return npc

    def update_all(self):
        for npc in self.npcs.values():
            npc.age_up(self.game_time)
            npc.update_pregnancy(self.game_time)
            npc.update_memory(self.game_time)
            npc.merchant_leave_town()
            npc.wilderness_survival()
