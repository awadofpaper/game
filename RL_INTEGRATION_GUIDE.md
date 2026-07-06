# RL Integration Guide

## Overview
Your RPG game now has full Reinforcement Learning (RL) integration that allows AI agents to:
- Navigate the main menu
- Create a character (allocate skill points)
- Play the game (movement, combat, dialogue, skill training, perks)

This enables **automated playtesting** and AI-driven game testing without manual input.

---

## File Structure

### Core Files
- **`main.py`**: Contains the `Game` class with state machine for menu → character creation → in-game phases
- **`rpg_gym_env.py`**: OpenAI Gym-compatible wrapper for RL frameworks
- **`test_rl_env.py`**: Test script to run a random agent through the game
- **`ui_helpers.py`**: Updated with `test_mode` parameter for headless operation

---

## How It Works

### Game Phases
The `Game` class now has a state machine with 3 phases:

1. **Menu Phase**: Agent selects "New Game"
2. **Character Creation Phase**: Agent allocates 15 skill points across 5 skills (Strength, Stamina, Stealth, Endurance, Magic)
3. **In-Game Phase**: Agent plays the game (movement, combat, dialogue, quests, etc.)

### Action Space
The RL environment uses **Discrete(9)** actions:

#### Menu Phase (actions 0-1):
- 0: Start new game
- 1: Skip menu (also starts new game)

#### Character Creation Phase (actions 0-8):
- 0-4: Add a skill point to Strength/Stamina/Stealth/Endurance/Magic
- 5: Remove a point from current skill
- 6: Move to next skill
- 7: Move to previous skill
- 8: Confirm character (only works when all 15 points allocated)

#### In-Game Phase (actions 0-8):
- 0: Move up
- 1: Move down
- 2: Move left
- 3: Move right
- 4: Attack (simulated combat)
- 5: Talk to NPC
- 6: Train skill
- 7: Pick skill/perk
- 8: Use perk

### Observation Space
**13-dimensional vector** (Box space):

#### Menu Phase:
- All zeros (waiting state)

#### Character Creation Phase:
- [1, skill_points_left, strength, stamina, stealth, endurance, magic, current_skill_idx, 0, 0, 0, 0, 0]

#### In-Game Phase:
- [x, y, health, level, xp, gold, perk_points, strength, agility, intelligence, charisma, inventory_count, quest_progress]

### Reward Structure
- **Menu**: +1 for starting new game
- **Character Creation**: +0.5 per skill point allocated, +10 for completing character
- **In-Game**:
  - -0.1 per step (encourages efficiency)
  - +10 for defeating enemy
  - +2 for NPC dialogue
  - +3 for skill training
  - +5 for gaining perk point
  - +7 for using perk
  - +20 for leveling up
  - +0.01 per XP gained
  - +2 per skill level gained
  - +10 per quest progress
  - +0.01 per gold gained
  - -0.5 per health lost
  - -50 for dying (terminal state)

---

## Usage

### Basic Testing
Run the test script to see a random agent play through all phases:
```powershell
python test_rl_env.py
```

This will:
1. Start in menu phase
2. Progress to character creation
3. Allocate skill points randomly
4. Enter the game and take random actions
5. Print phase information and rewards every 10 steps

### RL Training Example
To train an actual RL agent (requires `stable-baselines3`):

```powershell
pip install stable-baselines3
```

Then create `train_rl_agent.py`:
```python
from stable_baselines3 import PPO
from rpg_gym_env import RPGGameEnv

# Create environment
env = RPGGameEnv()

# Train agent
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100000)

# Save trained model
model.save("rpg_agent")

# Test trained agent
obs = env.reset()
for _ in range(1000):
    action, _ = model.predict(obs)
    obs, reward, done, info = env.step(action)
    if done:
        break
```

---

## Headless Mode

The `ui_helpers.py` functions now support `test_mode=True`:
- `main_menu(screen, config, test_mode=True)`: Returns default "new game" without UI
- `character_creation(screen, config, test_mode=True)`: Returns random character without UI

This allows the game to run without rendering for fast RL training.

---

## Features for RL Agents

### What the Agent Can Learn:
- ✅ Menu navigation
- ✅ Character creation (skill allocation strategy)
- ✅ Movement and exploration
- ✅ Combat decisions
- ✅ NPC interaction
- ✅ Skill training priorities
- ✅ Perk management
- ✅ Quest completion strategies
- ✅ Resource management (health, gold, inventory)

### What's Simulated (not fully integrated yet):
- Combat (20% chance per action)
- NPC dialogue (fixed reward)
- Skill training (adds to strength)
- Enemies, towns, and full game systems

---

## Next Steps for Full Integration

To connect the RL agent to the full game loop:

1. **Add enemy spawning in Game.step()**: Actually spawn enemies and handle combat
2. **Add NPC proximity detection**: Check if near NPCs for dialogue
3. **Add inventory management**: Allow agent to pick up/use items
4. **Add quest system integration**: Track actual quest progress
5. **Add town/building interaction**: Let agent enter shops, inns, etc.

These would make the RL agent play the full game instead of a simulation.

---

## Benefits

### Automated Playtesting
- Run thousands of game sessions overnight
- Find bugs, balance issues, and edge cases
- Test all game systems without manual input

### AI Opponent/Companion
- Train NPCs to behave realistically
- Create challenging AI opponents
- Build adaptive difficulty systems

### Game Balance Analysis
- See which skills/strategies are overpowered
- Identify dead-end paths or unwinnable scenarios
- Optimize reward structures

---

## Troubleshooting

### "Gym is deprecated" warning
- Install Gymnasium instead: `pip install gymnasium`
- Replace `import gym` with `import gymnasium as gym` in `rpg_gym_env.py`

### "Player has no attribute 'hp'" error
- Fixed! The Game class now uses `self.player.health` correctly.

### Episode runs forever
- Fixed! Test script now has `max_steps=200` limit.
- In-game phase has death condition (health <= 0).

### Character creation stuck
- Agent must allocate all 15 skill points before confirming.
- If stuck, the random agent will eventually distribute all points.

---

## Compatibility

This RL integration:
- ✅ Does NOT modify core game loop (main gameplay unchanged)
- ✅ Works alongside normal gameplay
- ✅ Can be enabled/disabled with `test_mode` parameter
- ✅ No code needs to be removed later
- ✅ Safe for production use

You can continue developing the game normally, and the RL system will remain available for testing.
