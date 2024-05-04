# import gymnasium as gym
# env = gym.make("CartPole-v1")

# observation, info = env.reset(seed=42)
# for _ in range(1000):
#     action = env.action_space.sample()
#     observation, reward, terminated, truncated, info = env.step(action)

#     if terminated or truncated:
#         observation, info = env.reset()
# env.close()



import os
import gymnasium as gym
from gymnasium.spaces.box import Box
from gymnasium.wrappers import FlattenObservation
from datetime import datetime
# stable baselines 3
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize, SubprocVecEnv
from stable_baselines3 import PPO, SAC
from stable_baselines3.common.env_util import make_vec_env
# utils
from utils.utils import CheckpointCallback
from utils.file_utils import get_latest_model
# gym environment
from quadruped_gym_env import QuadrupedGymEnv

from typing import Callable
import numpy as np
from stable_baselines3.common.monitor import Monitor

# after implementing, you will want to test how well the agent learns with your MDP: 
env_configs = {"force_max": 40.0,
               "switching_max": 10}


# directory to save policies and normalization parameters
SAVE_PATH = './logs/intermediate_models/'+ datetime.now().strftime("%m%d%y%H%M%S") + '/'
os.makedirs(SAVE_PATH, exist_ok=True)
# checkpoint to save policy network periodically
checkpoint_callback = CheckpointCallback(save_freq=30000, save_path=SAVE_PATH,name_prefix='rl_model', verbose=2)


env = lambda: QuadrupedGymEnv(**env_configs)  
env = make_vec_env(env, monitor_dir=SAVE_PATH,n_envs=4)
# normalize observations to stabilize learning (why?)
env = VecNormalize(env, norm_obs=True, norm_reward=False, clip_obs=100.)

# Multi-layer perceptron (MLP) policy of two layers of size _,_ 
policy_kwargs = dict(net_arch=[256,256])
# What are these hyperparameters? Check here: https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html
n_steps = 4096 

learning_rate = 5e-3 # lambda f: 1e-4 

# What are these hyperparameters? Check here: https://stable-baselines3.readthedocs.io/en/master/modules/sac.html
sac_config={"learning_rate":learning_rate,
            "buffer_size":300000, # times 10
            "batch_size":256, # times 10
            "ent_coef":'auto', 
            "gamma":0.99, 
            "tau":0.005,
            "train_freq":1, 
            "gradient_steps":1,
            "learning_starts": 10000,
            "verbose":1, 
            "tensorboard_log":None,
            "policy_kwargs": policy_kwargs,
            "seed":None, 
            "device": "cpu"}

model = SAC('MlpPolicy', env, **sac_config)
model.learn(total_timesteps=1000000, log_interval=1,callback=checkpoint_callback)
model.save(os.path.join(SAVE_PATH, "rl_model")) 
env.save(os.path.join(SAVE_PATH, "vec_normalize.pkl"))

model.save_replay_buffer(os.path.join(SAVE_PATH,"off_policy_replay_buffer"))