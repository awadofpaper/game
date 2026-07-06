
import numpy as np
import gym
from gym import spaces
from main import Game

class RPGGameEnv(gym.Env):
    """
    OpenAI Gym-compatible environment wrapper for the RPG game.
    This allows RL agents to interact with the game for training.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, config=None):
        super(RPGGameEnv, self).__init__()
        self.game = Game(config)
        # 0: up, 1: down, 2: left, 3: right, 4: attack, 5: talk, 6: train skill, 7: pick skill, 8: use perk
        self.action_space = spaces.Discrete(9)
        # Observation: x, y, health, level, xp, gold, perk_points, strength, agility, intelligence, charisma, inventory count, quest progress
        # Allow 0 for all values since menu/character creation phases may have zeros
        obs_low = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32)
        obs_high = np.array([100000, 100000, 100, 100, 1e6, 1e6, 100, 100, 100, 100, 100, 1e4, 100], dtype=np.float32)
        self.observation_space = spaces.Box(low=obs_low, high=obs_high, dtype=np.float32)

    def reset(self):
        obs = self.game.reset()
        return np.array(obs, dtype=np.float32)

    def step(self, action):
        obs, reward, done, info = self.game.step(action)
        return np.array(obs, dtype=np.float32), reward, done, info

    def render(self, mode='human'):
        # Optionally render the game (for debugging)
        pass

    def close(self):
        # Clean up resources
        pass
