from rpg_gym_env import RPGGameEnv

env = RPGGameEnv()
obs = env.reset()
done = False
total_reward = 0
step_count = 0
max_steps = 200  # Limit steps to avoid infinite loops

print("Starting RL environment test...")
print(f"Initial observation: {obs}")

while not done and step_count < max_steps:
    action = env.action_space.sample()  # Random action
    obs, reward, done, info = env.step(action)
    total_reward += reward
    step_count += 1
    
    # Print every 10 steps or when something interesting happens
    if step_count % 10 == 0 or reward > 1 or 'character_created' in info:
        print(f"Step {step_count}: Phase={info.get('phase', 'unknown')}, Action={action}, Reward={reward:.2f}, Done={done}")
        if 'action' in info:
            print(f"  Action taken: {info['action']}")
        if 'character_created' in info:
            print(f"  Character created! Entering game...")

print(f"\nEpisode finished after {step_count} steps.")
print(f"Total reward: {total_reward:.2f}")
print(f"Final observation: {obs}")
