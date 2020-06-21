import random

class random_agent:
    def __init__(self, env):
        pass

    def act(self, observation):
        return random.randint(0,1)


class conditional_agent:
    def __init__(self, env):
        pass

    def act(self, observation):
        if observation[0] > 250:
            return 1
        else:
            return 0