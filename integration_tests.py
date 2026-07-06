"""
INTEGRATION TEST SUITE
======================

Automated tests for game systems integration
"""

import sys
import os

# Test results tracker
tests_passed = 0
tests_failed = 0
tests_total = 0

def test_result(test_name, passed, details=""):
    global tests_passed, tests_failed, tests_total
    tests_total += 1
    if passed:
        tests_passed += 1
        print(f"✅ PASS: {test_name}")
    else:
        tests_failed += 1
        print(f"❌ FAIL: {test_name}")
    if details:
        print(f"   {details}")

print("=" * 70)
print("RUNNING INTEGRATION TESTS")
print("=" * 70)

# Test 1: Module Imports
print("\n[1/10] Testing Module Imports...")
try:
    import pygame
    test_result("pygame import", True)
except ImportError as e:
    test_result("pygame import", False, str(e))

try:
    sys.path.insert(0, "C:/Users/Public/rpg_game")
    from config import Config
    from world import World
    from player import Player
    test_result("Core modules import", True)
except ImportError as e:
    test_result("Core modules import", False, str(e))

try:
    from dialogue_system import DialogueManager
    from quest_system import QuestManager
    from reputation_system import ReputationSystem
    test_result("New systems import", True)
except ImportError as e:
    test_result("New systems import", False, str(e))

# Test 2: Config Initialization
print("\n[2/10] Testing Config Initialization...")
try:
    config = Config()
    assert config.SCREEN_WIDTH > 0
    assert config.SCREEN_HEIGHT > 0
    assert config.TILE_SIZE > 0
    test_result("Config values valid", True)
except Exception as e:
    test_result("Config values valid", False, str(e))

# Test 3: Dialogue System Structure
print("\n[3/10] Testing Dialogue System...")
try:
    from dialogue_system import DialogueNodeType, DialogueChoice, DialogueNode
    
    # Test dialogue choice creation
    choice = DialogueChoice("Test choice", "next_node", requirements={'level': 5})
    assert choice.text == "Test choice"
    assert choice.next_node_id == "next_node"
    
    # Test dialogue node creation
    node = DialogueNode("test_node", DialogueNodeType.TEXT, content="Test text")
    assert node.id == "test_node"
    assert node.content == "Test text"
    
    test_result("Dialogue system structure", True)
except Exception as e:
    test_result("Dialogue system structure", False, str(e))

# Test 4: Quest System Structure
print("\n[4/10] Testing Quest System...")
try:
    from quest_system import Quest, QuestType, QuestCategory, ObjectiveType
    
    # Test quest creation
    quest = Quest(
        quest_id="test_quest",
        name="Test Quest",
        description="Test description",
        quest_type=QuestType.SIDE,
        category=QuestCategory.COMBAT
    )
    assert quest.quest_id == "test_quest"
    assert quest.name == "Test Quest"
    
    test_result("Quest system structure", True)
except Exception as e:
    test_result("Quest system structure", False, str(e))

# Test 5: Reputation System
print("\n[5/10] Testing Reputation System...")
try:
    rep_system = ReputationSystem()
    
    # Test reputation modification
    rep_system.modify_npc_reputation("test_npc", 100)
    current_rep = rep_system.get_npc_reputation("test_npc")
    assert current_rep == 100
    
    # Test reputation level
    rep_level = rep_system.get_npc_reputation_level("test_npc")
    assert rep_level in ["Hated", "Hostile", "Unfriendly", "Neutral", "Friendly", "Honored", "Revered", "Exalted"]
    
    test_result("Reputation system logic", True)
except Exception as e:
    test_result("Reputation system logic", False, str(e))

# Test 6: Performance Monitor
print("\n[6/10] Testing Performance Monitor...")
try:
    from performance_monitor_overlay import get_performance_monitor
    
    monitor = get_performance_monitor()
    monitor.add_frame_time(16.67)
    monitor.update_counts(enemies=5, projectiles=2)
    
    fps = monitor.get_fps()
    assert fps >= 0
    
    test_result("Performance monitor", True)
except Exception as e:
    test_result("Performance monitor", False, str(e))

# Test 7: Dialogue Manager Integration
print("\n[7/10] Testing Dialogue Manager Integration...")
try:
    rep_system = ReputationSystem()
    quest_manager = QuestManager(rep_system)
    dialogue_manager = DialogueManager(rep_system, quest_manager)
    
    # Check starter dialogues exist
    assert "quest_giver_1" in dialogue_manager.dialogue_trees
    assert "town_elder" in dialogue_manager.dialogue_trees
    assert "merchant" in dialogue_manager.dialogue_trees
    
    test_result("Dialogue manager integration", True)
except Exception as e:
    test_result("Dialogue manager integration", False, str(e))

# Test 8: Quest Manager with Reputation
print("\n[8/10] Testing Quest Manager with Reputation...")
try:
    rep_system = ReputationSystem()
    quest_manager = QuestManager(rep_system)
    
    # Check starter quests
    quests = quest_manager.get_available_quests()
    assert len(quests) > 0
    
    test_result("Quest manager integration", True)
except Exception as e:
    test_result("Quest manager integration", False, str(e))

# Test 9: File Structure
print("\n[9/10] Testing File Structure...")
try:
    required_files = [
        "main.py",
        "config.py",
        "world.py",
        "player.py",
        "dialogue_system.py",
        "dialogue_ui.py",
        "quest_system.py",
        "quest_ui.py",
        "reputation_system.py",
        "performance_monitor_overlay.py",
        "minimap.py"
    ]
    
    base_path = "C:/Users/Public/rpg_game"
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join(base_path, file)):
            missing_files.append(file)
    
    if missing_files:
        test_result("File structure", False, f"Missing: {', '.join(missing_files)}")
    else:
        test_result("File structure", True, "All required files present")
        
except Exception as e:
    test_result("File structure", False, str(e))

# Test 10: Dialogue Tree Validation
print("\n[10/10] Testing Dialogue Tree Validation...")
try:
    rep_system = ReputationSystem()
    quest_manager = QuestManager(rep_system)
    dialogue_manager = DialogueManager(rep_system, quest_manager)
    
    # Validate quest_giver_1 tree
    tree = dialogue_manager.dialogue_trees["quest_giver_1"]
    assert tree.root_node_id == "greeting"
    assert tree.root_node_id in tree.nodes
    
    # Check for complete conversation paths
    greeting_node = tree.nodes["greeting"]
    assert len(greeting_node.choices) > 0
    
    test_result("Dialogue tree validation", True)
except Exception as e:
    test_result("Dialogue tree validation", False, str(e))

# Print summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"Total Tests: {tests_total}")
print(f"Passed: {tests_passed} ✅")
print(f"Failed: {tests_failed} ❌")
print(f"Success Rate: {(tests_passed/tests_total*100):.1f}%")

if tests_failed == 0:
    print("\n🎉 ALL TESTS PASSED! 🎉")
    print("The game systems are properly integrated and functional.")
else:
    print(f"\n⚠️  {tests_failed} test(s) failed. Review errors above.")

print("\n" + "=" * 70)
print("INTEGRATION TEST COMPLETE")
print("=" * 70)
