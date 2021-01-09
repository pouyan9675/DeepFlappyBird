import random
import torch
from torch import nn
import torch.nn.functional as F
from collections import deque
import numpy as np
import pygame
from pygame.locals import *

class random_agent:
    def __init__(self, env):
        pass

    def act(self, observation):
        return random.randint(0,1)


class human_agent:
    def __init__(self, env):
        pass

    def act(self, observation):
        for event in pygame.event.get():
            if (event.type == KEYDOWN and event.key == K_SPACE):
                return 1

        return 0


class conditional_agent:
    def __init__(self, env):
        pass

    def act(self, observation):
        if observation[0] > 250:
            return 1
        else:
            return 0


class _DQN(nn.Module):
        def __init__(self, observation_space, action_space):
            super(_DQN, self).__init__()
            self.fc1 = nn.Linear(observation_space, 8)
            self.fc2 = nn.Linear(8, 4)
            self.fc3 = nn.Linear(4, action_space)


        def forward(self, x):
            x = F.leaky_relu(self.fc1(x), negative_slope=0.1)
            x = F.leaky_relu(self.fc2(x), negative_slope=0.1)
            return self.fc3(x)      # predicted reward


class deepQ_agent:
    def __init__(self, env, gamma=0.99, batch_size=32, lr=1e-6, 
                    max_experiences=50000, min_experiences=10000):
        self.env = env
        self.loss_fn = nn.MSELoss()
        self.action_space = env.action_space.n
        self.observation_dims = env.observation_space.shape[0]
        self.action_ = None
        self.max_experiences = max_experiences
        self.min_experiences = min_experiences
        self.gamma = gamma
        self.batch_size = batch_size
        self.lr = lr
        self.experience = {'s': [], 'a': [], 'r': [], 's2': [], 'done': []}

        self.q_network = self._build_compile_model()
        self.target_network = self._build_compile_model()
        for param in self.target_network.parameters():
            param.requires_grad = False
        self.optimizer = torch.optim.Adam(self.q_network.parameters(), lr=lr)
        self.align_target_model()
        
    
    def _build_compile_model(self):
        return _DQN(observation_space=self.observation_dims, action_space=self.action_space)
    

    def align_target_model(self):
        self.target_network.load_state_dict(self.q_network.state_dict())
        

    def add_experience(self, exp):
        if len(self.experience['s']) >= self.max_experiences:
            for key in self.experience.keys():
                self.experience[key].pop(0)

        for key, value in exp.items():
            self.experience[key].append(value)


    def act(self, state, epsilon):
        if np.random.rand() <= epsilon:
            # return 0 if random.random() < 0.85 else 1
            return random.randint(0,1)
        else:
            state = torch.tensor(np.expand_dims(state, axis=0))
            q_values = self.q_network(state)
            # print(q_values.tolist())
            return int(np.argmax(q_values.detach().cpu().numpy()[0]))
    

    def print_w(self):
        for parameter in self.q_network.parameters():
            print(parameter)


    def preprocess(self, state):
        return state.astype(np.float32)


    def _train_preprocess(self, ten):
        return torch.tensor(ten)


    def save_model(self, path):
        torch.save(self.q_network.state_dict(), path)


    def load_model(self, path):
        self.q_network.load_state_dict(torch.load(path))
        self.q_network.eval()


    def train(self):
        if len(self.experience['s']) <= self.min_experiences:
            return
        elif len(self.experience['s']) <= self.batch_size:
            return

        # sampling of experiences with the size of batch size
        indecies = np.random.randint(low=0, high=len(self.experience['s']), size=self.batch_size)
        states = self._train_preprocess(np.asarray([self.preprocess(self.experience['s'][i]) for i in indecies]))
        actions = self._train_preprocess(np.asarray([self.experience['a'][i] for i in indecies]))
        rewards = self._train_preprocess(np.asarray([self.experience['r'][i] for i in indecies]))
        next_states = self._train_preprocess(np.asarray([self.preprocess(self.experience['s2'][i]) for i in indecies]))
        dones = self._train_preprocess(np.asarray([self.experience['done'][i] for i in indecies]))

        value_next = torch.max(torch.squeeze(self.target_network(next_states.float())), 1)[0]
        target_values = torch.where(dones, rewards, rewards + self.gamma * value_next).float()

        self.optimizer.zero_grad()
        prediction_values = torch.sum(torch.squeeze(self.q_network(states)) * F.one_hot(actions, 
                                        num_classes=self.action_space), 1).float()
        
        loss = self.loss_fn(prediction_values, target_values)
        loss.backward()
        self.optimizer.step()

