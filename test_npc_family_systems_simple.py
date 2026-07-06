"""
Simple NPC Family Systems Test
Tests the actual implemented family, marriage, and adoption systems
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from world import World
from npc_family_system import NPCFamilySystem, NPCFamily
from game_time import GameTime

# Simple mock for interaction system since NPCInteractionSystem may not exist
class MockInteractionSystem:
    def __init__(self):
        self.relationships = {}  # {(npc_a, npc_b): score}
    
    def add_interaction(self, npc_a, npc_b, score):
        key = tuple(sorted([npc_a, npc_b]))
        self.relationships[key] = score
    
    def get_relationship_score(self, npc_a, npc_b):
        key = tuple(sorted([npc_a, npc_b]))
        return self.relationships.get(key, 0)

print("="*70)
print("NPC FAMILY SYSTEMS TEST")
print("="*70)

# Initialize systems
print("\n=== Initializing Systems ===")
config = Config()
world = World(config)
game_time = GameTime()
interaction_system = MockInteractionSystem()
family_system = NPCFamilySystem(game_time, interaction_system)

print("[OK] Config, world, and game time initialized")
print("[OK] Family system initialized")
print(f"[OK] Marriage threshold: {family_system.marriage_threshold}")
print(f"[OK] Max children per family: {family_system.max_children}")

# Test 1: Marriage System
print("\n=== TEST 1: Marriage System ===")
parent1_id = "john_smith"
parent2_id = "jane_smith"

# Build relationship (needs to be >= 1000)
print(f"[OK] Building relationship between {parent1_id} and {parent2_id}")
interaction_system.add_interaction(parent1_id, parent2_id, 1200)

# Check relationship score
score = interaction_system.get_relationship_score(parent1_id, parent2_id)
print(f"[OK] Relationship score: {score}")

# Check if they can marry
can_marry = family_system.can_marry(parent1_id, parent2_id)
print(f"[OK] Can marry? {can_marry}")
assert can_marry, "Should be able to marry with score >= 1000"

# Marry them
married = family_system.marry(parent1_id, parent2_id)
print(f"[OK] Married? {married}")
assert married, "Marriage should succeed"

# Verify marriage in families
fam1 = family_system.families[parent1_id]
fam2 = family_system.families[parent2_id]
assert fam1.married == True, "First parent should be married"
assert fam2.married == True, "Second parent should be married"
assert fam1.spouse_id == parent2_id, "First parent's spouse should be second parent"
assert fam2.spouse_id == parent1_id, "Second parent's spouse should be first parent"
print(f"[OK] Marriage verified: {parent1_id} <-> {parent2_id}")

# Test 2: Children System
print("\n=== TEST 2: Children System ===")

can_have_child = family_system.can_have_child(parent1_id, parent2_id)
print(f"[OK] Can have child? {can_have_child}")
assert can_have_child, "Married couple should be able to have children"

# Have a child
child_id = family_system.have_child(parent1_id, parent2_id)
print(f"[OK] Child born: {child_id}")
assert child_id is not None, "Child should be created"

# Verify child in family
assert child_id in fam1.children_ids, "Child should be in parent1's children list"
assert child_id in fam2.children_ids, "Child should be in parent2's children list"
print(f"[OK] Child added to both parents' family records")

# Check child's family
child_fam = family_system.families[child_id]
assert parent1_id in child_fam.parents_ids, "Parent1 should be in child's parents list"
assert parent2_id in child_fam.parents_ids, "Parent2 should be in child's parents list"
print(f"[OK] Child has both parents in family record")

# Test child aging
child_age = family_system.age_child(child_id)
print(f"[OK] Child age: {child_age} days")

is_adult = family_system.is_child_adult(child_id)
print(f"[OK] Is child an adult? {is_adult}")
assert not is_adult, "Newborn should not be adult"

# Test 3: Adoption System
print("\n=== TEST 3: Adoption System ===")

# Create an orphan by manually creating a family with no parents
orphan_id = "orphan_child"
orphan_fam = NPCFamily(orphan_id)
family_system.families[orphan_id] = orphan_fam

is_orphan = family_system.is_orphan(orphan_id)
print(f"[OK] Is orphan? {is_orphan}")
assert is_orphan, "Child with no parents should be orphan"

# Get list of orphans
orphans = family_system.get_orphans()
print(f"[OK] Found {len(orphans)} orphan(s)")
assert orphan_id in orphans, "Orphan should be in orphans list"

# Test adoption by a single NPC
adopter_id = "kind_soul"
adopter_fam = NPCFamily(adopter_id)
family_system.families[adopter_id] = adopter_fam

can_adopt = family_system.can_adopt(adopter_id, orphan_id)
print(f"[OK] Can adopt? {can_adopt}")
assert can_adopt, "Should be able to adopt orphan"

adopted = family_system.adopt_child(adopter_id, orphan_id)
print(f"[OK] Adopted? {adopted}")
assert adopted, "Adoption should succeed"

# Verify adoption
assert orphan_id in adopter_fam.adopted_children_ids, "Orphan should be in adopted children list"
assert adopter_id in orphan_fam.parents_ids, "Adopter should be in orphan's parents list"
print(f"[OK] Adoption verified: {adopter_id} adopted {orphan_id}")

# Test 4: Max Children Limit
print("\n=== TEST 4: Max Children Limit ===")

# Try to have more children than max
for i in range(family_system.max_children):
    can_have_more = family_system.can_have_child(parent1_id, parent2_id)
    if can_have_more:
        child = family_system.have_child(parent1_id, parent2_id)
        print(f"[OK] Child {i+2} born: {child}")

# Should not be able to have more
can_have_more = family_system.can_have_child(parent1_id, parent2_id)
print(f"[OK] Can have more children after reaching max? {can_have_more}")
assert not can_have_more, "Should not be able to have more than max children"
print(f"[OK] Max children limit enforced: {len(fam1.children_ids)}/{family_system.max_children}")

# Test 5: Divorce System
print("\n=== TEST 5: Divorce System ===")

# Create another married couple for divorce test
spouse1 = "tom"
spouse2 = "alice"
interaction_system.add_interaction(spouse1, spouse2, 1500)
family_system.marry(spouse1, spouse2)
print(f"[OK] Married {spouse1} and {spouse2} for divorce test")

# Divorce them
divorced = family_system.divorce(spouse1, spouse2)
print(f"[OK] Divorced? {divorced}")
assert divorced, "Divorce should succeed"

# Verify divorce
fam_tom = family_system.families[spouse1]
fam_alice = family_system.families[spouse2]
assert not fam_tom.married, "Should not be married after divorce"
assert not fam_alice.married, "Should not be married after divorce"
assert fam_tom.divorced, "Should show as divorced"
assert fam_alice.divorced, "Should show as divorced"
assert fam_tom.spouse_id is None, "Spouse ID should be cleared"
assert fam_alice.spouse_id is None, "Spouse ID should be cleared"
print(f"[OK] Divorce verified")

# Test remarriage after divorce (should fail due to divorced flag)
can_remarry = family_system.can_marry(spouse1, spouse2)
print(f"[OK] Can remarry after divorce? {can_remarry}")
assert not can_remarry, "Should not be able to remarry after divorce"

print("\n" + "="*70)
print("[OK] ALL FAMILY SYSTEM TESTS PASSED!")
print("="*70)

print("\n[STATS] SUMMARY:")
print(f"[OK] Total families: {len(family_system.families)}")
print(f"[OK] Marriages tested: 2")
print(f"[OK] Children tested: {family_system.max_children + 1}")
print(f"[OK] Adoptions tested: 1")
print(f"[OK] Divorces tested: 1")

print("\n" + "="*70)
sys.exit(0)
