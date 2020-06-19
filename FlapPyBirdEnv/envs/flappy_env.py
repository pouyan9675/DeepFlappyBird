import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
from FlapPyBirdEnv improt flappy

class FlapPyEnv(gym.env):
    # metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(np.array([0, 0, 0], np.array([100,100,100]), dtype=np.int32))

    def step(self, action):
        pass

    def reset(self):
        pass

    def render(self, mode='human'):
        pass

    def close(self):
        pass