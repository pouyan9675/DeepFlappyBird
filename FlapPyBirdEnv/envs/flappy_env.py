import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
from FlapPyBirdEnv.core import FlappyGame

SCREEN_HEIGHT = 512

class FlapPyEnv(gym.Env):
    def __init__(self, render=False):
        self.game = FlappyGame(render=render)
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(np.array([0, 0]), np.array([SCREEN_HEIGHT + 100, SCREEN_HEIGHT + 100]), dtype=np.float32)

    def step(self, action):
        if not self.game.is_done():
            self.game.action(action)
            observation = self.game.observe()
            reward = self.game.evaluate()
            done = self.game.is_done()
            return observation, reward, done, {}
        else:
            return None

    def reset(self, render=True):
        del self.game
        self.game = FlappyGame(render)
        obervation = self.game.observe()
        return obervation

    def render(self):
        self.game.view()

    def close(self):
        pass