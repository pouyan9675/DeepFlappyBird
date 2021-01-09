#!venv/bin/python

import numpy as np
import FlapPyBirdEnv
import gym
from agents import *
import random
import time
from collections import defaultdict

def simulate(agent):
    total_r = []    # total rewards of each episode
    average_r = []  # average rewards of each episode
    best_reward = float('-inf')
    start = time.time()
    for episode in range(MAX_EPISODES):
        state = env.reset(render=False)
        episode_reward = 0
        actions_reward = []
        done = False
        i = 0
        global EPSILON
        if episode > NO_DECAY_EPISODES:
            EPSILON = max(MIN_EPSILON, EPSILON - EP_DECAY)

        while not done:
            state = agent.preprocess(state)
            
            if i == 0:      # game starts by flapping
                action = 1
            else:
                action = agent.act(state, EPSILON)
            
            next_state, reward, done, _ = env.step(action)
            
            episode_reward += reward
            actions_reward.append(reward)

            agent.add_experience({'s': state, 'a': action, 'r': reward, 's2': next_state, 'done': done})
            agent.train()

            state = next_state

            i += 1
            if i % COPY_STEP == 0:
                agent.align_target_model()

        total_r.append(episode_reward)
        ep_mean = np.array(actions_reward).mean()
        average_r.append(ep_mean)
        
        if episode % 100 == 0:
            end = time.time()
            print('Episode: {} \t Total: {:.2f} \t Mean: {:.5f} \t Time: {}s'
                                                .format(episode, episode_reward, ep_mean, int(end - start)))
            start = end
            with open('rewards.txt', 'w') as txt:
                txt.write(str(total_r) + '\n')
                txt.write(str(average_r))
        

        if episode_reward > best_reward:            # save weights on the best performance so far
            agent.save_model('weights/model.h5')
            best_reward = episode_reward


    with open('rewards.txt', 'w') as txt:
        txt.write(str(total_r) + '\n')
        txt.write(str(average_r))


def play(agent):
    state = env.reset(render=True)
    done = False
    rs = 0
    while not done:
        state = agent.preprocess(state)
        action = agent.act(state, 0)
        next_state, reward, done, _ = env.step(action)

        rs += reward
        state = next_state 

    print('Total : ' + str(rs))
    # while True:
    #     pass


if __name__ == "__main__":
    env = gym.make('flappy-v0')
    s = env.reset(render=True)

    MAX_EPISODES = 100000
    BATCH_SIZE = 32
    COPY_STEP = 100
    EPSILON = 0.1
    MIN_EPSILON = 0.00001
    NO_DECAY_EPISODES = 10000
    EP_DECAY = (EPSILON - MIN_EPSILON) / (50000 - NO_DECAY_EPISODES)

    agent = deepQ_agent(env)

    agent.load_model('weights/pretrained.h5')
    play(agent)
