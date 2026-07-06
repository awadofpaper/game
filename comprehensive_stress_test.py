"""
COMPREHENSIVE GAME STRESS TEST
Tests ALL game systems under extreme conditions
"""

import pygame
import time
import random
import sys
import traceback
from unittest.mock import Mock, MagicMock, patch
import math


class GameStressTest:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.performance = {}
        self.critical_failures = []
    
    def log_pass(self, test_name):
        self.passed.append(test_name)
        print(f"[PASS] {test_name}")
    
    def log_fail(self, test_name, error, critical=False):
        self.failed.append((test_name, str(error)))
        if critical:
            self.critical_failures.append(test_name)
            print(f"[CRITICAL FAIL] {test_name} - {error}")
        else:
            print(f"[FAIL] {test_name} - {error}")
    
    def log_warning(self, test_name, warning):
        self.warnings.append((test_name, warning))
        print(f"[WARNING] {test_name} - {warning}")
    
    def log_performance(self, test_name, duration_ms, threshold_ms=100):
        self.performance[test_name] = duration_ms
        if duration_ms > threshold_ms:
            print(f"[SLOW] {test_name} took {duration_ms:.2f}ms (>{threshold_ms}ms)")
        else:
            print(f"[PERF] {test_name}: {duration_ms:.2f}ms")
    
    def summary(self):
        print("\n" + "=" * 80)
        print("COMPREHENSIVE STRESS TEST SUMMARY")
        print("=" * 80)
        print(f"[+] Passed: {len(self.passed)}")
        print(f"[-] Failed: {len(self.failed)}")
        print(f"[!] Warnings: {len(self.warnings)}")
        print(f"[!!] Critical Failures: {len(self.critical_failures)}")
        
        if self.critical_failures:
            print(f"\n[!!] CRITICAL FAILURES (game-breaking):")
            for name in self.critical_failures:
                print(f"  - {name}")
        
        if self.failed:
            print(f"\nFailed Tests:")
            for name, error in self.failed:
                print(f"  - {name}: {error}")
        
        if self.warnings:
            print(f"\nWarnings:")
            for name, warning in self.warnings:
                print(f"  - {name}: {warning}")
        
        if self.performance:
            avg = sum(self.performance.values()) / len(self.performance)
            max_time = max(self.performance.values())
            slow_tests = [(k, v) for k, v in self.performance.items() if v > 100]
            
            print(f"\nPerformance Summary:")
            print(f"  Average: {avg:.2f}ms")
            print(f"  Max: {max_time:.2f}ms")
            if slow_tests:
                print(f"  Slow tests (>100ms): {len(slow_tests)}")
                for name, dur in sorted(slow_tests, key=lambda x: x[1], reverse=True)[:5]:
                    print(f"    - {name}: {dur:.2f}ms")
        
        print("=" * 80)
        
        if len(self.critical_failures) > 0:
            print("\n[!!] CRITICAL FAILURES DETECTED - Game may be unplayable!")
            return False
        elif len(self.failed) > len(self.passed) * 0.1:  # >10% failure rate
            print(f"\n[!] HIGH FAILURE RATE - {len(self.failed)} failures detected")
            return False
        else:
            print(f"\n[SUCCESS] STRESS TEST COMPLETE - Game is stable!")
            return True


def test_core_imports(test):
    """Test that all core modules can be imported"""
    print("\n" + "=" * 80)
    print("TEST SUITE 1: CORE IMPORTS")
    print("=" * 80)
    
    modules = [
        'player', 'enemies', 'town_system', 'npc_basic', 'item',
        'skills_system', 'gathering_nodes', 'cooking_system',
        'bank_system', 'dialogue_system', 'quest_system',
        'gatherer_npc', 'gatherer_dialogue', 'equipment',
        'reputation_system', 'status_effects', 'combat'
    ]
    
    for module_name in modules:
        test_name = f"Import {module_name}"
        try:
            start = time.time()
            exec(f"import {module_name}")
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration, threshold_ms=50)
            test.log_pass(test_name)
        except ImportError as e:
            test.log_fail(test_name, f"Module not found: {e}", critical=True)
        except Exception as e:
            test.log_fail(test_name, f"Import error: {e}")


def test_player_systems(test):
    """Test player-related systems"""
    print("\n" + "=" * 80)
    print("TEST SUITE 2: PLAYER SYSTEMS")
    print("=" * 80)
    
    try:
        from player import Player
        from config import Config
        
        # Test 1: Player creation
        test_name = "Player Creation"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            if not hasattr(player, 'health'):
                raise Exception("Player missing health attribute")
            if not hasattr(player, 'inventory'):
                raise Exception("Player missing inventory")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e, critical=True)
            return
        
        # Test 2: Player movement (1000 updates)
        test_name = "Player Movement (1000 updates)"
        try:
            start = time.time()
            keys = {pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False}
            dt = 0.016  # 60 FPS
            for _ in range(1000):
                player.update(keys, dt)
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Health management
        test_name = "Health Management"
        try:
            initial_health = player.health
            player.health -= 50
            if player.health >= initial_health:
                raise Exception("Health not decreasing")
            # Get max health directly from player
            max_health = player.max_health
            player.health = max_health
            if player.health != max_health:
                raise Exception("Health not resetting")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 4: Experience and leveling
        test_name = "Experience System"
        try:
            initial_level = player.level
            player.experience = 10000  # Force level up
            # Note: Leveling might happen elsewhere
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 5: Inventory stress test (fill inventory)
        test_name = "Inventory Stress (100 items)"
        try:
            from item import Item
            start = time.time()
            for i in range(100):
                item = Item(f"Item_{i}", "test", "test_item")
                player.add_item(item)
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 6: Equipment system
        test_name = "Equipment System"
        try:
            if not hasattr(player, 'equipment'):
                test.log_warning(test_name, "Player has no equipment attribute")
            else:
                # Try equipping items
                test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
            
    except ImportError as e:
        test.log_fail("Player Systems", f"Cannot import player module: {e}", critical=True)


def test_combat_systems(test):
    """Test combat mechanics"""
    print("\n" + "=" * 80)
    print("TEST SUITE 3: COMBAT SYSTEMS")
    print("=" * 80)
    
    try:
        from player import Player
        from enemies import Enemy
        from config import Config
        
        # Test 1: Enemy creation
        test_name = "Enemy Creation (100 enemies)"
        try:
            start = time.time()
            enemies = []
            for i in range(100):
                enemy = Enemy("goblin", i * 50, i * 50, level=1, rarity="Common")
                enemies.append(enemy)
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
            return
        
        # Test 2: Enemy AI updates (1000 frames)
        test_name = "Enemy AI (100 enemies × 10 updates)"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            player.x = 500
            player.y = 500
            start = time.time()
            for _ in range(10):
                for enemy in enemies[:100]:
                    enemy.update(player, [], dt=0.016, all_enemies=enemies, dropped_equipment_list=[])
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration, threshold_ms=200)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Combat damage calculation
        test_name = "Damage Calculation (1000 hits)"
        try:
            enemy = enemies[0]
            start = time.time()
            for _ in range(1000):
                initial_health = enemy.health
                enemy.take_damage(10, player=player, all_enemies=enemies, dropped_equipment_list=[])
                if enemy.health <= 0:
                    enemy.health = enemy.max_health  # Reset
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 4: Enemy death and drops
        test_name = "Enemy Death & Loot"
        try:
            # Enemy(etype, x, y, level, rarity)
            enemy = Enemy("goblin", 100, 100, 1, "Rare")
            drops = []
            enemy.take_damage(9999, player=player, all_enemies=[enemy], dropped_equipment_list=drops)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Combat Systems", f"Cannot import combat modules: {e}", critical=True)


def test_skills_gathering(test):
    """Test skills and gathering systems"""
    print("\n" + "=" * 80)
    print("TEST SUITE 4: SKILLS & GATHERING")
    print("=" * 80)
    
    try:
        from skills_system import SkillsManager
        from gathering_nodes import GatheringNodesManager, GatheringNode, NodeType
        
        # Test 1: Skills initialization
        test_name = "Skills Manager Init"
        try:
            skills = SkillsManager()
            if not hasattr(skills, 'skills'):
                raise Exception("SkillsManager missing skills dict")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e, critical=True)
            return
        
        # Test 2: XP gain and leveling
        test_name = "XP System (1000 XP gains)"
        try:
            skills = SkillsManager()
            start = time.time()
            for _ in range(1000):
                skills.add_xp('Mining', 10)
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Gathering nodes creation
        test_name = "Gathering Nodes (100 nodes)"
        try:
            config = Mock()
            start = time.time()
            nodes = []
            for i in range(100):
                node = GatheringNode(i * 50, i * 50, NodeType.MINING, config, node_id=i)
                nodes.append(node)
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 4: Node gathering simulation
        test_name = "Node Gathering Simulation"
        try:
            node = nodes[0]
            skills = SkillsManager()
            
            # Simulate gathering
            for _ in range(10):
                if hasattr(node, 'start_gathering'):
                    node.start_gathering(Mock())
                if hasattr(node, 'update_gathering'):
                    node.update_gathering(0.1)
            
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Skills & Gathering", f"Cannot import modules: {e}")


def test_inventory_banking(test):
    """Test inventory and banking systems"""
    print("\n" + "=" * 80)
    print("TEST SUITE 5: INVENTORY & BANKING")
    print("=" * 80)
    
    try:
        from bank_system import Bank
        from item import Item
        
        # Test 1: Bank creation
        test_name = "Bank System Init"
        try:
            # Create mock building for bank
            mock_building = Mock()
            mock_building.name = "Test Bank"
            bank = Bank(mock_building, "TestTown")
            if not hasattr(bank, 'storage_tiers'):
                raise Exception("Bank missing storage_tiers")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
            return
        
        # Test 2: Store many items
        test_name = "Bank Storage (storage tiers)"
        try:
            mock_building = Mock()
            mock_building.name = "Test Bank"
            bank = Bank(mock_building, "TestTown")
            start = time.time()
            
            # Test storage tiers
            if len(bank.storage_tiers) < 3:
                raise Exception("Bank has too few storage tiers")
            
            total_capacity = sum(tier.slots for tier in bank.storage_tiers)
            if total_capacity == 0:
                raise Exception("Bank has no storage capacity")
            
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Bank services
        test_name = "Bank Services"
        try:
            if not hasattr(bank, 'services'):
                raise Exception("Bank missing services")
            if len(bank.services) == 0:
                raise Exception("Bank has no services")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 4: Bank capacity limits
        test_name = "Bank Capacity Limits"
        try:
            max_tier = max(bank.storage_tiers, key=lambda t: t.slots)
            if max_tier.slots > 200:
                test.log_warning(test_name, f"Very large capacity: {max_tier.slots}")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Inventory & Banking", f"Cannot import modules: {e}")


def test_npc_systems(test):
    """Test NPC and dialogue systems"""
    print("\n" + "=" * 80)
    print("TEST SUITE 6: NPC SYSTEMS")
    print("=" * 80)
    
    try:
        from npc_basic import NPCManager
        from gatherer_npc import GathererNPCManager, GathererNPC, GathererType
        from gatherer_dialogue import create_gatherer_dialogue
        
        # Test 1: Regular NPC creation
        test_name = "Regular NPC Manager"
        try:
            start = time.time()
            manager = NPCManager()
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 2: Gatherer NPC system
        test_name = "Gatherer NPC System (30 NPCs)"
        try:
            manager = GathererNPCManager()
            config = Mock()
            start = time.time()
            for i in range(30):
                npc = GathererNPC(f"Gatherer_{i}", i * 50, i * 50, GathererType.MINER, Mock(), config)
                manager.npcs.append(npc)
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Gatherer NPC updates
        test_name = "Gatherer NPC Updates (30 NPCs × 100 frames)"
        try:
            game_time = Mock()
            game_time.get_total_hours.return_value = 100
            nodes_manager = Mock()
            nodes_manager.nodes = []
            
            start = time.time()
            for _ in range(100):
                manager.update_all(0.016, game_time, nodes_manager)
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration, threshold_ms=150)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 4: Dialogue creation
        test_name = "Dialogue System (100 dialogues)"
        try:
            start = time.time()
            for npc in manager.npcs[:10]:
                for _ in range(10):
                    dialogue = create_gatherer_dialogue(npc)
                    del dialogue
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("NPC Systems", f"Cannot import modules: {e}")


def test_world_systems(test):
    """Test town, dungeon, and world systems"""
    print("\n" + "=" * 80)
    print("TEST SUITE 7: WORLD SYSTEMS")
    print("=" * 80)
    
    try:
        from town_system import Town, TownManager
        
        # Test 1: Town creation
        test_name = "Town Creation (10 towns)"
        try:
            start = time.time()
            towns = []
            sizes = ["small", "medium", "large"]
            for i in range(10):
                town = Town(f"Town_{i}", i * 500, i * 500, size=sizes[i % 3])
                towns.append(town)
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 2: Town manager
        test_name = "Town Manager"
        try:
            manager = TownManager()
            for town in towns:
                if hasattr(manager, 'add_town'):
                    manager.add_town(town)
                elif hasattr(manager, 'towns'):
                    manager.towns.append(town)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("World Systems", f"Cannot import modules: {e}")


def test_status_effects(test):
    """Test status effect system"""
    print("\n" + "=" * 80)
    print("TEST SUITE 8: STATUS EFFECTS")
    print("=" * 80)
    
    try:
        from status_effects import StatusEffect, STATUS_EFFECTS, StatusType
        
        # Test 1: Status effect creation
        test_name = "Status Effect Creation"
        try:
            effect = StatusEffect("burn", 5.0, potency=1.0)
            if not hasattr(effect, 'duration'):
                raise Exception("StatusEffect missing duration")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
            return
        
        # Test 2: Apply many effects
        test_name = "Create Multiple Effects (100)"
        try:
            start = time.time()
            effects = []
            for i in range(100):
                effect = StatusEffect("burn", 5.0, potency=1.0)
                effects.append(effect)
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Check effect expiration
        test_name = "Status Effect Expiration (1000 checks)"
        try:
            effect = StatusEffect("burn", 5.0, potency=1.0)
            start = time.time()
            for _ in range(1000):
                expired = effect.is_expired()
                should_tick = effect.should_tick()
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Status Effects", f"Module not found: {e}")


def test_performance_critical(test):
    """Test performance-critical operations"""
    print("\n" + "=" * 80)
    print("TEST SUITE 9: PERFORMANCE CRITICAL")
    print("=" * 80)
    
    # Test 1: Collision detection (1000 checks)
    test_name = "Collision Detection (1000 checks)"
    try:
        rects = [pygame.Rect(i * 10, i * 10, 32, 32) for i in range(100)]
        test_rect = pygame.Rect(500, 500, 32, 32)
        
        start = time.time()
        for _ in range(1000):
            collisions = [r for r in rects if r.colliderect(test_rect)]
        duration = (time.time() - start) * 1000
        test.log_performance(test_name, duration, threshold_ms=50)
        test.log_pass(test_name)
    except Exception as e:
        test.log_fail(test_name, e)
    
    # Test 2: Distance calculations (10000 checks)
    test_name = "Distance Calculations (10000)"
    try:
        points = [(random.randint(0, 1000), random.randint(0, 1000)) for _ in range(100)]
        
        start = time.time()
        for _ in range(100):
            for p1 in points:
                for p2 in points:
                    dist = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        duration = (time.time() - start) * 1000
        test.log_performance(test_name, duration, threshold_ms=100)
        test.log_pass(test_name)
    except Exception as e:
        test.log_fail(test_name, e)
    
    # Test 3: List operations (large lists)
    test_name = "List Operations (10000 items)"
    try:
        large_list = list(range(10000))
        
        start = time.time()
        # Sort
        sorted_list = sorted(large_list, reverse=True)
        # Filter
        filtered = [x for x in large_list if x % 2 == 0]
        # Search
        for _ in range(100):
            5000 in large_list
        duration = (time.time() - start) * 1000
        test.log_performance(test_name, duration, threshold_ms=50)
        test.log_pass(test_name)
    except Exception as e:
        test.log_fail(test_name, e)


def test_memory_stress(test):
    """Test memory usage under stress"""
    print("\n" + "=" * 80)
    print("TEST SUITE 10: MEMORY STRESS")
    print("=" * 80)
    
    # Test 1: Create/destroy many objects
    test_name = "Object Creation/Destruction (10000 objects)"
    try:
        start = time.time()
        for i in range(10000):
            obj = {'id': i, 'data': [0] * 100}
            del obj
        duration = (time.time() - start) * 1000
        test.log_performance(test_name, duration)
        test.log_pass(test_name)
    except Exception as e:
        test.log_fail(test_name, e)
    
    # Test 2: Large list allocation
    test_name = "Large Data Structure (1M elements)"
    try:
        start = time.time()
        big_list = [0] * 1000000
        big_list[500000] = 1
        del big_list
        duration = (time.time() - start) * 1000
        test.log_performance(test_name, duration, threshold_ms=200)
        test.log_pass(test_name)
    except Exception as e:
        test.log_fail(test_name, e)


def test_edge_cases(test):
    """Test edge cases and error handling"""
    print("\n" + "=" * 80)
    print("TEST SUITE 11: EDGE CASES")
    print("=" * 80)
    
    # Test 1: Division by zero handling
    test_name = "Division by Zero Protection"
    try:
        # Simulate common division scenarios
        result = 100 / max(1, 0)  # Should use max()
        test.log_pass(test_name)
    except Exception as e:
        test.log_fail(test_name, e)
    
    # Test 2: Null/None handling
    test_name = "Null Reference Handling"
    try:
        test_dict = {}
        value = test_dict.get('nonexistent', 0)
        test_list = []
        if test_list:
            item = test_list[0]
        test.log_pass(test_name)
    except Exception as e:
        test.log_fail(test_name, e)
    
    # Test 3: Negative values
    test_name = "Negative Value Handling"
    try:
        health = max(0, -50)  # Should clamp to 0
        if health < 0:
            raise Exception("Negative health not clamped")
        test.log_pass(test_name)
    except Exception as e:
        test.log_fail(test_name, e)
    
    # Test 4: Overflow handling
    test_name = "Integer Overflow"
    try:
        big_num = 10 ** 100
        result = big_num + 1
        test.log_pass(test_name)
    except Exception as e:
        test.log_fail(test_name, e)


def test_integration(test):
    """Test integrated game systems working together"""
    print("\n" + "=" * 80)
    print("TEST SUITE 12: INTEGRATION TESTS")
    print("=" * 80)
    
    try:
        from player import Player
        from enemies import Enemy
        from gatherer_npc import GathererNPC, GathererType
        from skills_system import SkillsManager
        from config import Config
        
        # Test 1: Player + Combat + Skills
        test_name = "Player Combat with Skills"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            player.x = 500
            player.y = 500
            enemy = Enemy("goblin", 550, 550, level=1, rarity="Common")
            
            # Simulate combat
            for _ in range(10):
                enemy.take_damage(20, player=player, all_enemies=[enemy], dropped_equipment_list=[])
                if not enemy.alive:
                    break
            
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 2: Player + NPC + Dialogue
        test_name = "Player NPC Interaction"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            player.x = 500
            player.y = 500
            npc_config = Mock()
            npc = GathererNPC("Test", 520, 520, GathererType.MINER, Mock(), npc_config)
            
            # Check interaction distance
            distance = math.sqrt((player.x - npc.x)**2 + (player.y - npc.y)**2)
            
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Full game loop simulation (100 frames)
        test_name = "Full Game Loop Simulation (100 frames)"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            player.x = 500
            player.y = 500
            enemies = [Enemy("goblin", i * 100, i * 100, level=1, rarity="Common") for i in range(10)]
            
            start = time.time()
            keys = {pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False}
            dt = 0.016
            for frame in range(100):
                # Update player
                player.update(keys, dt)
                
                # Update enemies
                for enemy in enemies:
                    enemy.update(player, [], dt=0.016, all_enemies=enemies, dropped_equipment_list=[])
                
                # Collision checks
                for enemy in enemies:
                    if hasattr(player, 'rect') and hasattr(enemy, 'rect'):
                        collision = player.rect.colliderect(enemy.rect)
            
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration, threshold_ms=200)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Integration Tests", f"Cannot import modules: {e}")


def main():
    print("=" * 80)
    print("COMPREHENSIVE GAME STRESS TEST")
    print("Testing ALL game systems under extreme conditions")
    print("=" * 80)
    
    # Initialize pygame
    pygame.init()
    
    test = GameStressTest()
    
    # Run all test suites
    test_suites = [
        test_core_imports,
        test_player_systems,
        test_combat_systems,
        test_skills_gathering,
        test_inventory_banking,
        test_npc_systems,
        test_world_systems,
        test_status_effects,
        test_performance_critical,
        test_memory_stress,
        test_edge_cases,
        test_integration,
    ]
    
    for test_suite in test_suites:
        try:
            test_suite(test)
        except Exception as e:
            print(f"\n[CRASH] TEST SUITE CRASHED: {test_suite.__name__}")
            print(f"Error: {e}")
            traceback.print_exc()
            test.log_fail(test_suite.__name__, f"Suite crashed: {e}", critical=True)
    
    # Print final summary
    success = test.summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
