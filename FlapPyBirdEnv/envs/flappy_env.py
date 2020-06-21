import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
from FlapPyBirdEnv.flappy import FlappyGame

class FlapPyEnv(gym.Env):
    # metadata = {'render.modes': ['human']}

    def __init__(self):
        self.game = FlappyGame()
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(np.array([-100, -10, 0]), np.array([512, 512, 300]), dtype=np.int32)

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