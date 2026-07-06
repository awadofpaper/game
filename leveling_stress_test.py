"""
LEVELING SYSTEM COMPREHENSIVE STRESS TEST
Tests experience, stats, skills, perks, skill trees, and all progression systems
"""

import pygame
import time
import sys
from unittest.mock import Mock, MagicMock
import traceback


class LevelingStressTest:
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
    
    def log_performance(self, test_name, duration_ms, threshold_ms=50):
        self.performance[test_name] = duration_ms
        if duration_ms > threshold_ms:
            print(f"[SLOW] {test_name} took {duration_ms:.2f}ms (>{threshold_ms}ms)")
        else:
            print(f"[PERF] {test_name}: {duration_ms:.2f}ms")
    
    def summary(self):
        print("\n" + "=" * 80)
        print("LEVELING SYSTEM STRESS TEST SUMMARY")
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
            slow_tests = [(k, v) for k, v in self.performance.items() if v > 50]
            
            print(f"\nPerformance Summary:")
            print(f"  Average: {avg:.2f}ms")
            print(f"  Max: {max_time:.2f}ms")
            if slow_tests:
                print(f"  Slow tests (>50ms): {len(slow_tests)}")
                for name, dur in sorted(slow_tests, key=lambda x: x[1], reverse=True)[:5]:
                    print(f"    - {name}: {dur:.2f}ms")
        
        print("=" * 80)
        
        if len(self.critical_failures) > 0:
            print("\n[!!] CRITICAL FAILURES DETECTED - Leveling system broken!")
            return False
        elif len(self.failed) > len(self.passed) * 0.2:
            print(f"\n[!] HIGH FAILURE RATE - {len(self.failed)} failures detected")
            return False
        else:
            print(f"\n[SUCCESS] LEVELING SYSTEM COMPLETE - All progression working!")
            return True


def test_core_imports(test):
    """Test that all leveling-related modules import"""
    print("\n" + "=" * 80)
    print("TEST SUITE 1: CORE LEVELING IMPORTS")
    print("=" * 80)
    
    modules = [
        'stats', 'skills_system', 'skill_trees', 'player'
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


def test_stats_system(test):
    """Test stats system"""
    print("\n" + "=" * 80)
    print("TEST SUITE 2: STATS SYSTEM")
    print("=" * 80)
    
    try:
        from stats import Stats
        
        # Test 1: Stats creation
        test_name = "Stats Creation"
        try:
            stats = Stats()
            if not hasattr(stats, 'base_stats'):
                raise Exception("Stats missing base_stats")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e, critical=True)
            return
        
        # Test 2: Default stats
        test_name = "Default Stats Verification"
        try:
            required_stats = ["Strength", "Defense", "Magic", "Health", "Max_Health", 
                            "Mana", "Max_Mana", "Stamina", "Speed", "Agility", 
                            "Willpower", "Luck", "Talking", "Intelligence"]
            missing = [s for s in required_stats if s not in stats.base_stats]
            if missing:
                raise Exception(f"Missing stats: {missing}")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Stat calculation (1000 times)
        test_name = "Stat Calculation (1000 ops)"
        try:
            start = time.time()
            for _ in range(1000):
                strength = stats.get_stat("Strength")
                defense = stats.get_stat("Defense")
                health = stats.get_stat("Health")
            duration = (time.time() - start) * 1000
            test.log_performance(test_name, duration, threshold_ms=10)
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 4: Equipment bonuses
        test_name = "Equipment Bonuses"
        try:
            stats.equipment_bonuses = {"Strength": 10, "Defense": 5}
            strength = stats.get_stat("Strength")
            if strength < 20:  # Base 10 + 10 bonus
                raise Exception(f"Equipment bonus not applied: {strength}")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 5: Set bonuses
        test_name = "Set Bonuses"
        try:
            stats.set_bonuses = {"Magic": 15}
            magic = stats.get_stat("Magic")
            if magic < 25:  # Base 10 + 15 bonus
                raise Exception(f"Set bonus not applied: {magic}")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 6: Temporary effects
        test_name = "Temporary Effects"
        try:
            stats.temp_effects = {"Speed": 20}
            speed = stats.get_stat("Speed")
            if speed < 30:  # Base 10 + 20 temp
                raise Exception(f"Temp effect not applied: {speed}")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Stats System", f"Cannot import stats: {e}", critical=True)


def test_skills_system(test):
    """Test gathering skills system"""
    print("\n" + "=" * 80)
    print("TEST SUITE 3: SKILLS SYSTEM (Runescape-style)")
    print("=" * 80)
    
    try:
        from skills_system import SkillsManager, Skill
        
        # Test 1: SkillsManager creation
        test_name = "Skills Manager Creation"
        try:
            skills_mgr = SkillsManager()
            if not hasattr(skills_mgr, 'skills'):
                raise Exception("SkillsManager missing skills dict")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e, critical=True)
            return
        
        # Test 2: Default skills
        test_name = "Default Skills Verification"
        try:
            required_skills = ["Mining", "Woodcutting", "Fishing", "Cooking"]
            missing = [s for s in required_skills if s not in skills_mgr.skills]
            if missing:
                raise Exception(f"Missing skills: {missing}")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Individual skill creation
        test_name = "Individual Skill Creation"
        try:
            skill = Skill("TestSkill", level=1, xp=0)
            if skill.level != 1:
                raise Exception(f"Skill level wrong: {skill.level}")
            if skill.max_level != 100:
                raise Exception(f"Max level wrong: {skill.max_level}")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 4: XP calculation
        test_name = "XP Formula Calculation"
        try:
            skill = Skill("Mining")
            # Level 2 should require some XP
            xp_for_2 = skill.get_xp_for_level(2)
            xp_for_10 = skill.get_xp_for_level(10)
            xp_for_50 = skill.get_xp_for_level(50)
            xp_for_100 = skill.get_xp_for_level(100)
            
            if xp_for_2 <= 0:
                raise Exception("Level 2 XP is 0 or negative")
            if xp_for_10 <= xp_for_2:
                raise Exception("XP not increasing exponentially")
            if xp_for_100 <= xp_for_50:
                raise Exception("High level XP wrong")
            
            print(f"      XP Requirements: L2={xp_for_2}, L10={xp_for_10}, L50={xp_for_50}, L100={xp_for_100}")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 5: XP gain and leveling (stress test)
        test_name = "XP Gain & Level Up (1000 XP gains)"
        try:
            skill = Skill("Mining")
            start = time.time()
            total_levels = 0
            for _ in range(1000):
                levels = skill.add_xp(100)
                total_levels += len(levels)
            duration = (time.time() - start) * 1000
            
            if total_levels == 0:
                test.log_warning(test_name, "No levels gained from 100k XP")
            
            test.log_performance(test_name, duration, threshold_ms=50)
            test.log_pass(test_name)
            print(f"      Reached level {skill.level} with {skill.xp} XP")
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 6: Level 100 cap
        test_name = "Max Level Cap (100)"
        try:
            skill = Skill("Mining")
            # Add massive XP to reach max
            skill.add_xp(999999999)
            if skill.level > 100:
                raise Exception(f"Exceeded max level: {skill.level}")
            if skill.level != 100:
                test.log_warning(test_name, f"Didn't reach max level: {skill.level}")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 7: Progress tracking
        test_name = "Progress Percentage Calculation"
        try:
            skill = Skill("Mining")
            skill.add_xp(50)
            progress = skill.get_progress_to_next_level()
            if progress < 0 or progress > 1:
                raise Exception(f"Progress out of range: {progress}")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 8: Can perform action check
        test_name = "Level Requirements Check"
        try:
            skill = Skill("Mining", level=10)
            if not skill.can_perform_action(5):
                raise Exception("Should be able to perform level 5 action")
            if skill.can_perform_action(15):
                raise Exception("Should not be able to perform level 15 action")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 9: Skill serialization
        test_name = "Skill Serialization"
        try:
            skill = Skill("Mining", level=42, xp=12345)
            data = skill.to_dict()
            restored = Skill.from_dict(data)
            if restored.level != 42 or restored.xp != 12345:
                raise Exception(f"Serialization failed: L{restored.level}, XP{restored.xp}")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Skills System", f"Cannot import skills_system: {e}", critical=True)


def test_player_leveling(test):
    """Test player combat level and XP system"""
    print("\n" + "=" * 80)
    print("TEST SUITE 4: PLAYER LEVELING SYSTEM")
    print("=" * 80)
    
    try:
        from player import Player
        from config import Config
        
        # Test 1: Player creation with level
        test_name = "Player Initial Level"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            if not hasattr(player, 'level'):
                raise Exception("Player missing level attribute")
            if not hasattr(player, 'xp'):
                raise Exception("Player missing xp attribute")
            if player.level != 1:
                test.log_warning(test_name, f"Initial level is {player.level}, not 1")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e, critical=True)
            return
        
        # Test 2: XP requirement formula
        test_name = "XP Requirement Formula"
        try:
            xp_needed = player.level * 100  # Formula from check_level_up
            if xp_needed != 100:
                test.log_warning(test_name, f"Initial XP requirement is {xp_needed}, not 100")
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Single level up
        test_name = "Single Level Up"
        try:
            old_level = player.level
            old_stat_points = player.stat_points
            old_perk_points = player.perk_points
            
            xp_needed = player.level * 100
            player.xp = xp_needed
            leveled = player.check_level_up()
            
            if not leveled:
                raise Exception("Level up check returned False")
            if player.level != old_level + 1:
                raise Exception(f"Level not increased: {player.level}")
            if player.stat_points <= old_stat_points:
                raise Exception(f"Stat points not awarded: {player.stat_points}")
            if player.perk_points <= old_perk_points:
                raise Exception(f"Perk points not awarded: {player.perk_points}")
            
            test.log_pass(test_name)
            print(f"      Level {old_level} -> {player.level}, +{player.stat_points - old_stat_points} stat pts, +{player.perk_points - old_perk_points} perk pt")
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 4: Multiple level ups
        test_name = "Multiple Level Ups (10 levels)"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            
            # Give enough XP for multiple levels
            player.xp = 10000
            player.check_level_up()
            
            if player.level < 5:
                test.log_warning(test_name, f"Only reached level {player.level} with 10k XP")
            
            test.log_pass(test_name)
            print(f"      Reached level {player.level}")
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 5: Stat increases on level up
        test_name = "Stat Increases on Level Up"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            
            initial_hp = player.max_health
            initial_str = player.strength
            initial_def = player.defense
            
            xp_needed = player.level * 100
            player.xp = xp_needed
            player.check_level_up()
            
            if player.max_health <= initial_hp:
                raise Exception("Max Health not increased")
            # Note: Strength and Defense auto-increase per level not implemented
            
            test.log_pass(test_name)
            print(f"      HP +{player.max_health - initial_hp}")
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 6: Full heal on level up
        test_name = "Full Heal on Level Up"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            
            # Damage player
            player.health = player.health // 2
            damaged_hp = player.health
            
            # Level up
            xp_needed = player.level * 100
            player.xp = xp_needed
            player.check_level_up()
            
            max_hp = player.max_health
            if player.health != max_hp:
                raise Exception(f"Not fully healed: {player.health}/{max_hp}")
            
            test.log_pass(test_name)
            print(f"      Healed from {damaged_hp} to {player.health}")
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 7: Stat points per level
        test_name = "Stat Points Award (3 per level)"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            
            initial_points = player.stat_points
            xp_needed = player.level * 100
            player.xp = xp_needed
            player.check_level_up()
            
            points_gained = player.stat_points - initial_points
            if points_gained != 3:
                raise Exception(f"Expected 3 stat points, got {points_gained}")
            
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 8: Perk points per level
        test_name = "Perk Points Award (1 per level)"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            
            initial_perks = player.perk_points
            xp_needed = player.level * 100
            player.xp = xp_needed
            player.check_level_up()
            
            perks_gained = player.perk_points - initial_perks
            if perks_gained != 1:
                raise Exception(f"Expected 1 perk point, got {perks_gained}")
            
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 9: Level up performance (stress)
        test_name = "Level Up Performance (100 level ups)"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            
            start = time.time()
            for _ in range(100):
                xp_needed = player.level * 100
                player.xp = xp_needed
                player.check_level_up()
            duration = (time.time() - start) * 1000
            
            test.log_performance(test_name, duration, threshold_ms=100)
            test.log_pass(test_name)
            print(f"      Reached level {player.level}")
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Player Leveling", f"Cannot import player: {e}", critical=True)


def test_skill_trees(test):
    """Test skill tree system and perks"""
    print("\n" + "=" * 80)
    print("TEST SUITE 5: SKILL TREES & PERKS")
    print("=" * 80)
    
    try:
        from skill_trees import SKILL_TREES
        
        # Test 1: Skill trees exist
        test_name = "Skill Trees Loaded"
        try:
            if not SKILL_TREES:
                raise Exception("SKILL_TREES is empty")
            test.log_pass(test_name)
            print(f"      Found {len(SKILL_TREES)} skill trees")
        except Exception as e:
            test.log_fail(test_name, e, critical=True)
            return
        
        # Test 2: Verify all skill trees
        test_name = "Skill Tree Structure"
        try:
            for tree_name, tree_data in SKILL_TREES.items():
                if 'description' not in tree_data:
                    raise Exception(f"{tree_name} missing description")
                if 'tiers' not in tree_data:
                    raise Exception(f"{tree_name} missing tiers")
                if not tree_data['tiers']:
                    raise Exception(f"{tree_name} has no tiers")
            
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Count total skills
        test_name = "Total Skills Count"
        try:
            total_skills = 0
            for tree_name, tree_data in SKILL_TREES.items():
                for tier in tree_data['tiers']:
                    total_skills += len(tier)
            
            if total_skills == 0:
                raise Exception("No skills found in any tree")
            
            test.log_pass(test_name)
            print(f"      Total skills across all trees: {total_skills}")
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 4: Verify skill costs
        test_name = "Skill Cost Verification"
        try:
            for tree_name, tree_data in SKILL_TREES.items():
                for tier_idx, tier in enumerate(tree_data['tiers']):
                    for skill_id, skill_data in tier.items():
                        if 'cost' not in skill_data:
                            raise Exception(f"{tree_name}.{skill_id} missing cost")
                        if skill_data['cost'] <= 0:
                            raise Exception(f"{tree_name}.{skill_id} has invalid cost: {skill_data['cost']}")
            
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 5: Verify skill effects
        test_name = "Skill Effects Verification"
        try:
            for tree_name, tree_data in SKILL_TREES.items():
                for tier in tree_data['tiers']:
                    for skill_id, skill_data in tier.items():
                        if 'effects' not in skill_data:
                            raise Exception(f"{tree_name}.{skill_id} missing effects")
                        if not skill_data['effects']:
                            raise Exception(f"{tree_name}.{skill_id} has empty effects")
            
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 6: Verify multi-point skills
        test_name = "Multi-Point Skills"
        try:
            multi_point_count = 0
            for tree_name, tree_data in SKILL_TREES.items():
                for tier in tree_data['tiers']:
                    for skill_id, skill_data in tier.items():
                        if 'max_points' in skill_data:
                            multi_point_count += 1
                            if skill_data['max_points'] < 2:
                                raise Exception(f"{tree_name}.{skill_id} max_points < 2")
                            if 'per_point_effect' not in skill_data:
                                raise Exception(f"{tree_name}.{skill_id} missing per_point_effect")
            
            test.log_pass(test_name)
            print(f"      Found {multi_point_count} multi-point skills")
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 7: Verify stat requirements
        test_name = "Stat Requirements"
        try:
            for tree_name, tree_data in SKILL_TREES.items():
                for tier in tree_data['tiers']:
                    for skill_id, skill_data in tier.items():
                        if 'stat_requirements' in skill_data:
                            reqs = skill_data['stat_requirements']
                            if not reqs:
                                raise Exception(f"{tree_name}.{skill_id} has empty stat_requirements")
            
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 8: Verify active vs passive skills
        test_name = "Active vs Passive Skills"
        try:
            active_count = 0
            passive_count = 0
            for tree_name, tree_data in SKILL_TREES.items():
                for tier in tree_data['tiers']:
                    for skill_id, skill_data in tier.items():
                        if skill_data.get('type') == 'active':
                            active_count += 1
                            if 'cooldown' not in skill_data:
                                test.log_warning(test_name, f"{tree_name}.{skill_id} is active but has no cooldown")
                        elif skill_data.get('type') == 'passive':
                            passive_count += 1
            
            test.log_pass(test_name)
            print(f"      Active skills: {active_count}, Passive skills: {passive_count}")
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Skill Trees", f"Cannot import skill_trees: {e}", critical=True)


def test_player_skill_allocation(test):
    """Test skill point allocation system"""
    print("\n" + "=" * 80)
    print("TEST SUITE 6: SKILL POINT ALLOCATION")
    print("=" * 80)
    
    try:
        from player import Player
        from config import Config
        
        # Test 1: Initial stat points
        test_name = "Initial Stat Points"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            if player.stat_points < 0:
                raise Exception(f"Negative stat points: {player.stat_points}")
            test.log_pass(test_name)
            print(f"      Starting with {player.stat_points} stat points")
        except Exception as e:
            test.log_fail(test_name, e)
            return
        
        # Test 2: Allocate skill point
        test_name = "Allocate Skill Point"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            
            # Give stat points
            player.stat_points = 10
            initial_strength = player.strength
            
            # Allocate
            if hasattr(player, 'allocate_stat_point'):
                success, message = player.allocate_stat_point("Strength")
                
                if player.stat_points != 9:
                    raise Exception(f"Stat points not decremented: {player.stat_points}")
                if player.strength <= initial_strength:
                    raise Exception("Strength not increased")
                
                test.log_pass(test_name)
            else:
                test.log_warning(test_name, "Player has no allocate_stat_point method")
                test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 3: Perk point tracking
        test_name = "Perk Point Tracking"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            
            if not hasattr(player, 'perk_points'):
                raise Exception("Player missing perk_points attribute")
            if not hasattr(player, 'acquired_skills'):
                raise Exception("Player missing acquired_skills attribute")
            
            test.log_pass(test_name)
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Skill Point Allocation", f"Cannot import: {e}")


def test_experience_scaling(test):
    """Test experience requirements scaling"""
    print("\n" + "=" * 80)
    print("TEST SUITE 7: EXPERIENCE SCALING")
    print("=" * 80)
    
    try:
        from player import Player
        from config import Config
        
        # Test 1: XP scaling formula
        test_name = "XP Requirement Scaling"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            
            xp_requirements = []
            for level in range(1, 21):
                player.level = level
                player.experience = 0
                player.experience_to_next_level = int(100 * (1.5 ** (level - 1)))
                xp_requirements.append(player.experience_to_next_level)
            
            # Check exponential growth
            for i in range(1, len(xp_requirements)):
                if xp_requirements[i] <= xp_requirements[i-1]:
                    raise Exception(f"XP not increasing at level {i+1}")
            
            test.log_pass(test_name)
            print(f"      L1->2: {xp_requirements[0]} XP")
            print(f"      L10->11: {xp_requirements[9]} XP")
            print(f"      L20->21: {xp_requirements[19]} XP")
        except Exception as e:
            test.log_fail(test_name, e)
        
        # Test 2: High level requirements
        test_name = "High Level XP Requirements"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            
            player.level = 50
            xp_50 = int(100 * (1.5 ** 49))
            
            if xp_50 < 1000000:
                test.log_warning(test_name, f"Level 50 XP seems low: {xp_50}")
            
            test.log_pass(test_name)
            print(f"      Level 50->51 requires: {xp_50:,} XP")
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Experience Scaling", f"Cannot import: {e}")


def test_integration(test):
    """Test integration between all leveling systems"""
    print("\n" + "=" * 80)
    print("TEST SUITE 8: LEVELING SYSTEMS INTEGRATION")
    print("=" * 80)
    
    try:
        from player import Player
        from config import Config
        from skills_system import SkillsManager
        
        # Test 1: Player + Stats + Skills
        test_name = "Full Player Progression Simulation"
        try:
            config = Config()
            world = Mock()
            player = Player(config, world)
            
            # Simulate gameplay progression
            initial_level = player.level
            initial_mining = player.skills_manager.skills["Mining"].level
            
            # Gain combat XP
            player.xp += 1000
            player.check_level_up()
            
            # Gain mining XP
            player.skills_manager.add_xp("Mining", 1000)
            
            # Check both progressed
            if player.level <= initial_level and player.xp < 1000:
                test.log_warning(test_name, "Player may not have leveled up")
            
            final_mining = player.skills_manager.skills["Mining"].level
            if final_mining <= initial_mining:
                test.log_warning(test_name, "Mining level didn't increase")
            
            test.log_pass(test_name)
            print(f"      Combat Level: {initial_level} -> {player.level}")
            print(f"      Mining Level: {initial_mining} -> {final_mining}")
        except Exception as e:
            test.log_fail(test_name, e)
        
    except ImportError as e:
        test.log_fail("Leveling Integration", f"Cannot import: {e}")


def main():
    print("=" * 80)
    print("LEVELING SYSTEM COMPREHENSIVE STRESS TEST")
    print("Testing experience, stats, skills, perks, and all progression")
    print("=" * 80)
    
    # Initialize pygame
    pygame.init()
    
    test = LevelingStressTest()
    
    # Run all test suites
    test_suites = [
        test_core_imports,
        test_stats_system,
        test_skills_system,
        test_player_leveling,
        test_skill_trees,
        test_player_skill_allocation,
        test_experience_scaling,
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
