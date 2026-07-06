"""
NPC Family, Marriage, and Children System
Handles dynamic family creation, marriage, divorce, child aging, adoption, and inheritance
"""
import random
import time

class NPCFamily:
    """Represents a family unit for an NPC"""
    def __init__(self, npc_id):
        self.npc_id = npc_id
        self.spouse_id = None
        self.children_ids = []  # List of child NPC IDs
        self.parents_ids = []   # List of parent NPC IDs
        self.married = False
        self.divorced = False
        self.adopted_children_ids = []
        self.family_start_time = None
        self.family_end_time = None

class NPCFamilySystem:
    """Manages all NPC families, marriages, children, and inheritance"""
    def __init__(self, game_time, interaction_system):
        self.game_time = game_time
        self.interaction_system = interaction_system
        self.families = {}  # {npc_id: NPCFamily}
        self.marriage_threshold = 1000  # Positive interaction score to trigger marriage
        self.max_children = 2
        self.child_age_adult = 18 * 365  # 18 years in days
        self.pregnancy_duration = 9 * 30  # 9 months in days

    def can_marry(self, npc_a_id, npc_b_id):
        # Check if both NPCs are single, not already married/divorced, and have enough positive score
        fam_a = self.families.get(npc_a_id)
        fam_b = self.families.get(npc_b_id)
        if not fam_a:
            fam_a = NPCFamily(npc_a_id)
            self.families[npc_a_id] = fam_a
        if not fam_b:
            fam_b = NPCFamily(npc_b_id)
            self.families[npc_b_id] = fam_b
        if fam_a.married or fam_b.married or fam_a.divorced or fam_b.divorced:
            return False
        score = self.interaction_system.get_relationship_score(npc_a_id, npc_b_id)
        return score >= self.marriage_threshold

    def marry(self, npc_a_id, npc_b_id):
        if not self.can_marry(npc_a_id, npc_b_id):
            return False
        fam_a = self.families[npc_a_id]
        fam_b = self.families[npc_b_id]
        fam_a.spouse_id = npc_b_id
        fam_b.spouse_id = npc_a_id
        fam_a.married = True
        fam_b.married = True
        fam_a.family_start_time = self.game_time.day_count if self.game_time else 0
        fam_b.family_start_time = fam_a.family_start_time
        return True

    def divorce(self, npc_a_id, npc_b_id):
        fam_a = self.families.get(npc_a_id)
        fam_b = self.families.get(npc_b_id)
        if fam_a and fam_b and fam_a.married and fam_b.married:
            fam_a.married = False
            fam_b.married = False
            fam_a.divorced = True
            fam_b.divorced = True
            fam_a.spouse_id = None
            fam_b.spouse_id = None
            fam_a.family_end_time = self.game_time.day_count if self.game_time else 0
            fam_b.family_end_time = fam_a.family_end_time
            return True
        return False

    def can_have_child(self, parent_a_id, parent_b_id):
        fam_a = self.families.get(parent_a_id)
        fam_b = self.families.get(parent_b_id)
        if not fam_a or not fam_b or not fam_a.married or not fam_b.married:
            return False
        if len(fam_a.children_ids) >= self.max_children or len(fam_b.children_ids) >= self.max_children:
            return False
        return True

    def have_child(self, parent_a_id, parent_b_id):
        if not self.can_have_child(parent_a_id, parent_b_id):
            return None
        # Create child NPC ID
        child_id = f"CHILD-{parent_a_id}-{parent_b_id}-{random.randint(1000,9999)}"
        fam_a = self.families[parent_a_id]
        fam_b = self.families[parent_b_id]
        fam_a.children_ids.append(child_id)
        fam_b.children_ids.append(child_id)
        # Child's parents
        child_family = NPCFamily(child_id)
        child_family.parents_ids = [parent_a_id, parent_b_id]
        self.families[child_id] = child_family
        # Track birth time
        child_family.family_start_time = self.game_time.day_count if self.game_time else 0
        return child_id

    def age_child(self, child_id):
        # Returns age in days
        child_family = self.families.get(child_id)
        if not child_family or not child_family.family_start_time:
            return 0
        current_time = self.game_time.day_count if self.game_time else 0
        return current_time - child_family.family_start_time

    def is_child_adult(self, child_id):
        return self.age_child(child_id) >= self.child_age_adult

    def is_orphan(self, child_id):
        fam_child = self.families.get(child_id)
        if fam_child and not fam_child.parents_ids:
            return True
        return False

    def can_adopt(self, adopter_id, child_id):
        fam_adopter = self.families.get(adopter_id)
        fam_child = self.families.get(child_id)
        if not fam_adopter or not fam_child:
            return False
        if not self.is_orphan(child_id):
            return False
        # Optionally: check adopter's max children
        if len(fam_adopter.children_ids) + len(fam_adopter.adopted_children_ids) >= self.max_children:
            return False
        return True

    def adopt_child(self, adopter_id, child_id):
        if not self.can_adopt(adopter_id, child_id):
            return False
        fam_adopter = self.families[adopter_id]
        fam_child = self.families[child_id]
        fam_adopter.adopted_children_ids.append(child_id)
        fam_child.parents_ids = [adopter_id]
        # Optionally: set adoption time
        fam_child.family_start_time = self.game_time.day_count if self.game_time else 0
        return True

    def get_orphans(self):
        return [npc_id for npc_id, fam in self.families.items() if not fam.parents_ids]

    def trigger_adoption_event(self, adopter_id):
        # Find orphans and adopt one if possible
        orphans = self.get_orphans()
        for orphan_id in orphans:
            if self.can_adopt(adopter_id, orphan_id):
                self.adopt_child(adopter_id, orphan_id)
                return orphan_id
        return None

    def get_family(self, npc_id):
        return self.families.get(npc_id)

    def get_spouse(self, npc_id):
        fam = self.families.get(npc_id)
        if fam and fam.spouse_id:
            return fam.spouse_id
        return None

    def get_children(self, npc_id):
        fam = self.families.get(npc_id)
        if fam:
            return fam.children_ids + fam.adopted_children_ids
        return []

    def get_parents(self, npc_id):
        fam = self.families.get(npc_id)
        if fam:
            return fam.parents_ids
        return []

    def update(self):
        # This can be called daily to handle aging, pregnancy, etc.
        pass
