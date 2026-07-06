"""
Master Test Suite Runner
Runs all available system tests and provides comprehensive report
"""

import sys
import os
import subprocess
import time

def run_test(test_file, test_name):
    """Run a single test file and capture results"""
    print(f"\n{'='*70}")
    print(f"Running: {test_name}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        elapsed = time.time() - start_time
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print("STDERR:")
            print(result.stderr)
        
        success = result.returncode == 0
        status = "[PASS]" if success else "[FAIL]"
        
        print(f"\n{status} {test_name} completed in {elapsed:.2f}s")
        
        return {
            'name': test_name,
            'file': test_file,
            'success': success,
            'time': elapsed,
            'returncode': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"\n[TIMEOUT] {test_name} exceeded 60 seconds")
        return {
            'name': test_name,
            'file': test_file,
            'success': False,
            'time': elapsed,
            'returncode': -1
        }
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n[ERROR] {test_name} crashed: {e}")
        return {
            'name': test_name,
            'file': test_file,
            'success': False,
            'time': elapsed,
            'returncode': -2
        }

def main():
    print("="*70)
    print("COMPREHENSIVE GAME SYSTEMS TEST SUITE")
    print("="*70)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define all tests to run
    tests = [
        ("test_town_systems.py", "Town Systems (Buildings, NPCs, Services)"),
        ("test_quest_system.py", "Quest System"),
        ("test_dialogue_system.py", "Dialogue System"),
        ("test_npc_family_systems_simple.py", "NPC Family Systems (Marriage, Children, Adoption)"),
        ("test_resource_management.py", "Resource Management"),
        ("test_magic_spells.py", "Magic & Spells"),
        ("test_combat_spells.py", "Combat & Spells"),
        ("test_skill_progression.py", "Skill Progression"),
        ("test_crafting_system.py", "Crafting System"),
        ("test_status_effects.py", "Status Effects"),
        ("test_loot_drops.py", "Loot System"),
        ("test_save_load.py", "Save/Load System"),
        ("test_world_generation.py", "World Generation"),
    ]
    
    results = []
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run each test
    for test_file, test_name in tests:
        full_path = os.path.join(test_dir, test_file)
        
        if not os.path.exists(full_path):
            print(f"\n[SKIP] {test_name} - File not found: {test_file}")
            results.append({
                'name': test_name,
                'file': test_file,
                'success': None,
                'time': 0,
                'returncode': -3
            })
            continue
        
        result = run_test(full_path, test_name)
        results.append(result)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUITE SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results if r['success'] == True)
    failed = sum(1 for r in results if r['success'] == False)
    skipped = sum(1 for r in results if r['success'] is None)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    print(f"[SKIP] Skipped: {skipped}")
    
    if total > skipped:
        pass_rate = (passed / (total - skipped)) * 100
        print(f"\nPass Rate: {pass_rate:.1f}%")
    
    # Detailed results
    print("\n" + "-"*70)
    print("Detailed Results:")
    print("-"*70)
    
    for result in results:
        if result['success'] is None:
            status = "[SKIP]"
        elif result['success']:
            status = "[PASS]"
        else:
            status = "[FAIL]"
        
        time_str = f"{result['time']:.2f}s" if result['time'] > 0 else "N/A"
        print(f"{status} {result['name']:<45} {time_str:>8}")
    
    # Performance summary
    valid_times = [r['time'] for r in results if r['time'] > 0]
    if valid_times:
        total_time = sum(valid_times)
        avg_time = total_time / len(valid_times)
        print(f"\nTotal Test Time: {total_time:.2f}s")
        print(f"Average Test Time: {avg_time:.2f}s")
    
    print(f"\nCompleted at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return success if all non-skipped tests passed
    if failed > 0:
        return 1
    elif passed == 0:
        return 2  # No tests ran
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())
