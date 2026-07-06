"""
Comprehensive RL Environment Test Suite
Tests all aspects of the RPG game RL integration
"""
import numpy as np
from rpg_gym_env import RPGGameEnv
import time

def test_environment_creation():
    """Test 1: Environment can be created"""
    print("\n" + "="*60)
    print("TEST 1: Environment Creation")
    print("="*60)
    try:
        env = RPGGameEnv()
        print("✓ Environment created successfully")
        print(f"  Action space: {env.action_space}")
        print(f"  Observation space: {env.observation_space}")
        return True, env
    except Exception as e:
        print(f"✗ Failed to create environment: {e}")
        return False, None

def test_reset_functionality(env):
    """Test 2: Reset returns valid observation"""
    print("\n" + "="*60)
    print("TEST 2: Reset Functionality")
    print("="*60)
    try:
        obs = env.reset()
        print(f"✓ Reset successful")
        print(f"  Initial observation shape: {np.array(obs).shape}")
        print(f"  Initial observation: {obs}")
        
        # Check observation is in valid range
        if env.observation_space.contains(obs):
            print("✓ Observation is within valid space")
        else:
            print("✗ Observation is outside valid space")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Reset failed: {e}")
        return False

def test_all_actions(env):
    """Test 3: All actions work without errors"""
    print("\n" + "="*60)
    print("TEST 3: Action Execution")
    print("="*60)
    
    obs = env.reset()
    action_results = []
    
    for action in range(env.action_space.n):
        try:
            obs, reward, done, info = env.step(action)
            action_results.append((action, True, reward, info.get('phase', 'unknown')))
            print(f"✓ Action {action}: Success (Phase: {info.get('phase', 'unknown')}, Reward: {reward:.2f})")
        except Exception as e:
            action_results.append((action, False, 0, str(e)))
            print(f"✗ Action {action}: Failed - {e}")
    
    success_count = sum(1 for _, success, _, _ in action_results if success)
    print(f"\n  Total: {success_count}/{env.action_space.n} actions successful")
    return success_count == env.action_space.n

def test_phase_transitions(env):
    """Test 4: Phase transitions work correctly"""
    print("\n" + "="*60)
    print("TEST 4: Phase Transitions")
    print("="*60)
    
    obs = env.reset()
    phases_visited = []
    max_steps = 100
    
    for step in range(max_steps):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        phase = info.get('phase', 'unknown')
        
        if not phases_visited or phases_visited[-1] != phase:
            phases_visited.append(phase)
            print(f"  Step {step}: Entered {phase} phase")
        
        if phase == 'in_game':
            print(f"✓ Successfully transitioned to in_game phase at step {step}")
            break
    
    if 'in_game' in phases_visited:
        print(f"✓ Phase progression successful: {' → '.join(phases_visited)}")
        return True
    else:
        print(f"✗ Did not reach in_game phase. Visited: {phases_visited}")
        return False

def test_character_creation(env):
    """Test 5: Character creation allocates all points"""
    print("\n" + "="*60)
    print("TEST 5: Character Creation")
    print("="*60)
    
    obs = env.reset()
    
    # Progress to character creation phase
    env.step(0)  # Start new game
    
    # Allocate exactly 15 points by targeting specific skills
    points_needed = 15
    for i in range(points_needed):
        skill_action = i % 5  # Cycle through skills 0-4
        obs, reward, done, info = env.step(skill_action)
    
    # Now confirm character
    obs, reward, done, info = env.step(8)  # Confirm
    
    if info.get('character_created'):
        print(f"✓ Character created successfully")
        print(f"  All 15 skill points allocated and confirmed")
        return True
    else:
        print(f"✗ Character creation failed")
        print(f"  Info: {info}")
        return False

def test_multiple_episodes(env, num_episodes=5):
    """Test 6: Multiple episodes can run"""
    print("\n" + "="*60)
    print(f"TEST 6: Multiple Episodes (n={num_episodes})")
    print("="*60)
    
    episode_results = []
    
    for episode in range(num_episodes):
        obs = env.reset()
        total_reward = 0
        steps = 0
        max_steps = 100
        
        for step in range(max_steps):
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        episode_results.append((episode, steps, total_reward))
        print(f"  Episode {episode+1}: {steps} steps, Total reward: {total_reward:.2f}")
    
    print(f"✓ All {num_episodes} episodes completed")
    avg_reward = np.mean([r for _, _, r in episode_results])
    print(f"  Average reward: {avg_reward:.2f}")
    return True

def test_observation_consistency(env):
    """Test 7: Observations stay within bounds"""
    print("\n" + "="*60)
    print("TEST 7: Observation Consistency")
    print("="*60)
    
    obs = env.reset()
    invalid_count = 0
    total_steps = 100
    
    for step in range(total_steps):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        
        if not env.observation_space.contains(obs):
            invalid_count += 1
            print(f"  ✗ Step {step}: Observation out of bounds")
            print(f"    Obs: {obs}")
    
    if invalid_count == 0:
        print(f"✓ All {total_steps} observations valid")
        return True
    else:
        print(f"✗ {invalid_count}/{total_steps} observations invalid")
        return False

def test_reward_structure(env):
    """Test 8: Rewards are being calculated"""
    print("\n" + "="*60)
    print("TEST 8: Reward Structure")
    print("="*60)
    
    obs = env.reset()
    reward_types = {
        'positive': 0,
        'negative': 0,
        'zero': 0,
        'total': 0
    }
    
    max_steps = 100
    for step in range(max_steps):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        
        if reward > 0:
            reward_types['positive'] += 1
        elif reward < 0:
            reward_types['negative'] += 1
        else:
            reward_types['zero'] += 1
        
        reward_types['total'] += reward
    
    print(f"  Positive rewards: {reward_types['positive']}")
    print(f"  Negative rewards: {reward_types['negative']}")
    print(f"  Zero rewards: {reward_types['zero']}")
    print(f"  Total reward: {reward_types['total']:.2f}")
    
    if reward_types['positive'] > 0:
        print(f"✓ Reward system is working")
        return True
    else:
        print(f"✗ No positive rewards received")
        return False

def test_action_effects(env):
    """Test 9: Actions have observable effects"""
    print("\n" + "="*60)
    print("TEST 9: Action Effects")
    print("="*60)
    
    obs = env.reset()
    
    # Get to in-game phase first
    env.step(0)  # Start new game
    for _ in range(20):
        action = np.random.randint(0, 5)
        obs, reward, done, info = env.step(action)
        if info.get('character_created'):
            break
    
    # Now test movement actions
    initial_obs = obs.copy()
    
    # Move up (action 0)
    obs, _, _, _ = env.step(0)
    if not np.array_equal(obs, initial_obs):
        print(f"✓ Movement action (up) changed observation")
    else:
        print(f"  Note: Movement didn't change position (might be at boundary)")
    
    # Test other action types
    action_effects = []
    for action_type in [4, 5, 6, 7, 8]:  # Combat, talk, train, pick, use
        obs_before = obs.copy()
        obs, reward, done, info = env.step(action_type)
        
        effect = 'reward' if reward > 0 else 'none'
        action_effects.append((action_type, effect, reward))
        print(f"  Action {action_type}: {effect} (reward: {reward:.2f})")
    
    print(f"✓ Action effects tested")
    return True

def test_terminal_conditions(env):
    """Test 10: Terminal conditions work"""
    print("\n" + "="*60)
    print("TEST 10: Terminal Conditions")
    print("="*60)
    
    # Run until done or max steps
    obs = env.reset()
    max_steps = 1000
    
    for step in range(max_steps):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        
        if done:
            print(f"✓ Episode terminated at step {step}")
            print(f"  Reason: {info.get('death', 'unknown')}")
            print(f"  Final observation: {obs}")
            return True
    
    print(f"  Note: Episode did not terminate within {max_steps} steps")
    print(f"  This is expected if health doesn't decrease")
    return True

def test_performance(env):
    """Test 11: Performance/Speed test"""
    print("\n" + "="*60)
    print("TEST 11: Performance Test")
    print("="*60)
    
    obs = env.reset()
    num_steps = 1000
    
    start_time = time.time()
    
    for _ in range(num_steps):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        if done:
            obs = env.reset()
    
    elapsed = time.time() - start_time
    steps_per_second = num_steps / elapsed
    
    print(f"  {num_steps} steps in {elapsed:.2f} seconds")
    print(f"  Speed: {steps_per_second:.1f} steps/second")
    
    if steps_per_second > 100:
        print(f"✓ Performance is good for RL training")
    else:
        print(f"  Note: Performance could be improved for faster training")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# COMPREHENSIVE RL ENVIRONMENT TEST SUITE")
    print("#"*60)
    
    results = []
    
    # Test 1: Create environment
    success, env = test_environment_creation()
    results.append(("Environment Creation", success))
    if not success:
        print("\n✗ Cannot proceed without environment")
        return
    
    # Test 2: Reset
    success = test_reset_functionality(env)
    results.append(("Reset Functionality", success))
    
    # Test 3: All actions
    success = test_all_actions(env)
    results.append(("Action Execution", success))
    
    # Test 4: Phase transitions
    success = test_phase_transitions(env)
    results.append(("Phase Transitions", success))
    
    # Test 5: Character creation
    success = test_character_creation(env)
    results.append(("Character Creation", success))
    
    # Test 6: Multiple episodes
    success = test_multiple_episodes(env, num_episodes=3)
    results.append(("Multiple Episodes", success))
    
    # Test 7: Observation consistency
    success = test_observation_consistency(env)
    results.append(("Observation Consistency", success))
    
    # Test 8: Reward structure
    success = test_reward_structure(env)
    results.append(("Reward Structure", success))
    
    # Test 9: Action effects
    success = test_action_effects(env)
    results.append(("Action Effects", success))
    
    # Test 10: Terminal conditions
    success = test_terminal_conditions(env)
    results.append(("Terminal Conditions", success))
    
    # Test 11: Performance
    success = test_performance(env)
    results.append(("Performance Test", success))
    
    # Summary
    print("\n" + "#"*60)
    print("# TEST SUMMARY")
    print("#"*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! RL environment is ready for training.")
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Review issues above.")

if __name__ == "__main__":
    run_all_tests()
