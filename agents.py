import random
import tensorflow as tf
from collections import deque
import numpy as np

class random_agent:
    def __init__(self, env):
        pass

    def act(self, observation):
        if random.randint(0,100) > 95:
            return 1 
        else:
            return 0


class conditional_agent:
    def __init__(self, env):
        pass

    def act(self, observation):
        if observation[0] > 250:
            return 1
        else:
            return 0


class deepQ_agent:
    def __init__(self, env, optimzer):
        self.env = env
        # self._state_size = env.observation_space.shape[0]
        self._action_space = env.action_space.n
        self._optimizer = optimzer
        self.action_ = None
        
        self.experience_replay = deque(maxlen=2000)
        
        self.gamma = 0.7
        self.epsilon = 0.1
        
        self.q_network = self._build_compile_model()
        self.target_network = self._build_compile_model()
        self.align_target_model()
        
    
    def _build_compile_model(self):
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Embedding(1000, 10, input_length=4))
        model.add(tf.keras.layers.Reshape((40,)))
        model.add(tf.keras.layers.Dense(16, activation='relu'))
        model.add(tf.keras.layers.Dense(8, activation='relu'))
        model.add(tf.keras.layers.Dense(self._action_space, activation='linear'))
        
        model.compile(loss='mse', optimizer=self._optimizer)
        model.summary()

        return model
    
    def align_target_model(self):
        self.target_network.set_weights(self.q_network.get_weights())
    
    def store(self, state, action, reward, next_state, terminated):
        self.experience_replay.append((state, action, reward, next_state, terminated))
        
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            self.action_ = random.randint(0, self._action_space-1)
        else:
            q_values = self.q_network.predict(state)
            self.action_ = int(np.argmax(q_values[0]))
        
        if state[0][3] > 410:
            self.action_ = 0

        return self.action_
    
    def preprocess(self, state):
        return np.maximum(state + 100, 0, state)

    def train(self, batch_size):
        minibatch = random.sample(self.experience_replay, batch_size)
        for state, action, reward, next_state, terminated in minibatch:
            target = self.q_network.predict(state)
            if terminated:
                target[0][action] = reward
            else:
                next_state = self.preprocess(next_state)
                t = self.target_network.predict(next_state)
                target[0][action] = reward + self.gamma * np.amax(t)
                self.q_network.fit(np.array(state), np.array(target), epochs=1, verbose=0)

    def train_sample(self, sample):
        state, action, reward, next_state, terminated = sample
        target = self.q_network.predict(state)
        if terminated:
            target[0][action] = reward
        else:
            next_state = self.preprocess(next_state)
            t = self.target_network.predict(next_state)
            target[0][action] = reward + self.gamma * np.amax(t)
            self.q_network.fit(np.array([state]), np.array(target), epochs=1, verbose=0)