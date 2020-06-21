import numpy as np
import FlapPyBirdEnv
import gym

from agents import random_agent, conditional_agent

def simulate(agent):

    for episode in range(MAX_EPISODES):
        state = env.reset()
        total_reward = 0

        for t in range(MAX_TRY):
            action = agent.act(state)

            next_state, reward, done, _ = env.step(action)
            
            total_reward += reward
            if done:
                print('Total reward in episode ' + str(episode) + ' is : ' + str(total_reward))
                break
            state = next_state

            env.render()


if __name__ == "__main__":
    env = gym.make('flappy-v0')

    MAX_EPISODES = 300
    MAX_TRY = 1000000

    agent = conditional_agent(env)
    simulate(agent)