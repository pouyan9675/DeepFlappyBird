from gym.envs.registration import register

register(
    id='flappy-v0',
    entry_point='FlapPyBirdEnv.envs:FlapPyEnv',
)