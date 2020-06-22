import numpy as np
import FlapPyBirdEnv
import gym
import tensorflow as tf

from agents import random_agent, conditional_agent, deepQ_agent

def simulate(agent):

    for episode in range(MAX_EPISODES):
        state = env.reset()
        total_reward = 0

        for t in range(MAX_TIME_STEPS):
            state = agent.preprocess(state)

            action = agent.act(state)

            next_state, reward, done, _ = env.step(action)
            agent.store(state, action, reward, next_state, done)
            agent.train_sample((state, action, reward, next_state, done))
            state = next_state
            total_reward += reward

            if done:
                agent.align_target_model()
                print('Total reward in episode ' + str(episode) + ' is : ' + str(total_reward))
                break

            
            # if len(agent.experience_replay) > BATCH_SIZE:
            #     agent.train(BATCH_SIZE)

            env.render()


if __name__ == "__main__":
    env = gym.make('flappy-v0')

    MAX_EPISODES = 500
    MAX_TIME_STEPS = 1000000
    BATCH_SIZE = 64

    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
    agent = deepQ_agent(env, optimizer)
    simulate(agent)