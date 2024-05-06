import os
from stable_baselines3 import SAC
from quadruped_gym_env import QuadrupedGymEnv


model_dir = './rl/model/'
log_dir = './rl/log/'
os.makedirs(model_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

TIMESTEPS = 5000
env_configs = {"force_max": 40.0,
               "switching_max": 10,
               "reset_noise_scale": 0,
               "total_timesteps": TIMESTEPS,
               } 
env = QuadrupedGymEnv(**env_configs, render_mode="human") 

model = SAC('MlpPolicy', env, device="auto", tensorboard_log=log_dir, verbose=1, learning_rate=0.1)

iter = 0
while True:
    iter += 1
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False)
    model.save(os.path.join(model_dir, "rl_model" + f"{TIMESTEPS*iter}"))