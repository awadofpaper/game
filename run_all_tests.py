#!/usr/bin/env python3
"""
Run all 22 test suites and generate comprehensive summary
"""
import subprocess
import time
import os

# Define all test suites in order
TEST_SUITES = [
    ("Suite 1", "test_new_features.py", "Core Features"),
    ("Suite 2", "test_integration.py", "Integration"),
    ("Suite 3", "test_stress.py", "Performance & Stress"),
    ("Suite 4", "test_edge_cases.py", "Edge Cases"),
    ("Suite 5", "test_combat_spells.py", "Combat & Spells"),
    ("Suite 6", "test_save_load.py", "Save/Load"),
    ("Suite 7", "test_world_generation.py", "World Generation"),
    ("Suite 8", "test_npc_ai.py", "NPC AI"),
    ("Suite 9", "test_ui_graphics.py", "UI & Graphics"),
    ("Suite 10", "test_input_controls.py", "Input Controls"),
    ("Suite 11", "test_quest_system.py", "Quest System"),
    ("Suite 12", "test_status_effects.py", "Status Effects"),
    ("Suite 13", "test_resource_management.py", "Resource Management"),
    ("Suite 14", "test_economy_trading.py", "Economy & Trading"),
    ("Suite 15", "test_pathfinding.py", "Pathfinding"),
    ("Suite 16", "test_configuration.py", "Configuration"),
    ("Suite 17", "test_skill_progression.py", "Skill Progression"),
    ("Suite 18", "test_particles_animations.py", "Particles & Animations"),
    ("Suite 19", "test_loot_drops.py", "Loot & Drops"),
    ("Suite 20", "test_magic_spells.py", "Magic & Spells"),
    ("Suite 21", "test_audio_system.py", "Audio System"),
    ("Suite 22", "test_crafting_system.py", "Crafting System"),
]

def run_test_suite(suite_num, suite_file, suite_name):
    """Run a single test suite and extract results"""
    print(f"\n{'='*70}")
    print(f"Running {suite_num}: {suite_name}")
    print(f"{'='*70}")
    
    if not os.path.exists(suite_file):
        print(f"⚠️  Test file not found: {suite_file}")
        return None
    
    try:
        result = subprocess.run(
            ['python', suite_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        
        # Extract test results
        if "PASSED" in output:
            # Look for pattern like "15/15 PASSED"
            lines = output.split('\n')
            for line in lines:
                if "TEST RESULTS:" in line and "PASSED" in line:
                    # Extract X/Y from "TEST RESULTS: X/Y PASSED"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if '/' in part:
                            passed, total = part.split('/')
                            return {
                                'passed': int(passed),
                                'total': int(total),
                                'status': '✅' if int(passed) == int(total) else '⚠️'
                            }
        
        return None
        
    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout running {suite_file}")
        return None
    except Exception as e:
        print(f"❌ Error running {suite_file}: {e}")
        return None

def main():
    print("="*70)
    print("RPG GAME - COMPREHENSIVE TEST SUITE RUNNER")
    print("Testing 22 Complete Test Suites")
    print("="*70)
    
    start_time = time.time()
    results = []
    
    for suite_num, suite_file, suite_name in TEST_SUITES:
        result = run_test_suite(suite_num, suite_file, suite_name)
        results.append({
            'suite': suite_num,
            'name': suite_name,
            'file': suite_file,
            'result': result
        })
    
    end_time = time.time()
    
    # Generate summary
    print("\n" + "="*70)
    print("FINAL RESULTS SUMMARY")
    print("="*70)
    print(f"\n{'Suite':<10} {'Name':<30} {'Result':<15} {'Status'}")
    print("-"*70)
    
    total_passed = 0
    total_tests = 0
    perfect_suites = 0
    
    for r in results:
        suite = r['suite']
        name = r['name'][:28]
        result = r['result']
        
        if result:
            passed = result['passed']
            total = result['total']
            status = result['status']
            result_str = f"{passed}/{total}"
            
            total_passed += passed
            total_tests += total
            if passed == total:
                perfect_suites += 1
            
            print(f"{suite:<10} {name:<30} {result_str:<15} {status}")
        else:
            print(f"{suite:<10} {name:<30} {'N/A':<15} ❓")
    
    print("-"*70)
    print(f"\n{'TOTALS':<10} {'':<30} {total_passed}/{total_tests}")
    
    if total_tests > 0:
        pass_rate = (total_passed / total_tests) * 100
        print(f"\n📊 Overall Pass Rate: {pass_rate:.1f}%")
        print(f"✅ Perfect Suites: {perfect_suites}/{len(TEST_SUITES)}")
        print(f"⏱️  Total Time: {end_time - start_time:.1f}s")
        
        if pass_rate >= 97:
            print("\n🎉 EXCELLENT! Production-ready quality!")
        elif pass_rate >= 90:
            print("\n✅ VERY GOOD! Minor improvements recommended.")
        elif pass_rate >= 80:
            print("\n⚠️  GOOD - Several issues to address.")
        else:
            print("\n❌ Needs significant work.")
    
    print("="*70)

if __name__ == "__main__":
    main()
