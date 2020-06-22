import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
from FlapPyBirdEnv.flappy import FlappyGame

SCREEN_HEIGHT = 512

class FlapPyEnv(gym.Env):
    # metadata = {'render.modes': ['human']}

    def __init__(self):
        self.game = FlappyGame()
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(np.array([0, 0, 0, 0]), np.array([SCREEN_HEIGHT + 100, SCREEN_HEIGHT + 100, 300, SCREEN_HEIGHT]), dtype=np.float32)

    def step(self, action):
        self.game.action(action)
        observation = self.game.observe()
        reward = self.game.evaluate()
        done = self.game.is_done()
        return observation, reward, done, {}

    def reset(self):
        del self.game
        self.game = FlappyGame()
        obervation = self.game.observe()
        return obervation

    def render(self, mode='human', close=False):
        self.game.view()

    def close(self):
        pass