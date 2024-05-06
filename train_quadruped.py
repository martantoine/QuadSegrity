import os
from stable_baselines3 import SAC
from stable_baselines3.common.monitor import Monitor
from quadruped_gym_env import QuadrupedGymEnv


model_dir = './rl/model/'
log_dir = './rl/log/'
os.makedirs(model_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

NSTEPS = 15000
TIMESTEPS = 0.001
control_period = 0.5
control_step_skip = int(control_period / TIMESTEPS)

env_configs = {"force_max": 40.0,
               "switching_max": 10,
               "reset_noise_scale": 0.0001,
               "forward_reward_weight": 100.0,
               "force_cost_weight": 0.001,
               "switching_rate_cost_weight": 0.01,
               "total_timesteps": NSTEPS,
               "frame_skip": control_step_skip,
               } 
env = QuadrupedGymEnv(**env_configs, render_mode="human") 

env = Monitor(env, log_dir, info_keywords=('x_position', 'x_velocity', 'actions', 'reward_forward', 'reward_ctrl'))
model = SAC('MlpPolicy', env, device="auto", tensorboard_log=log_dir, verbose=1)

iter = 0
while True:
    iter += 1
    model.learn(total_timesteps=NSTEPS, reset_num_timesteps=False)
    model.save(os.path.join(model_dir, "rl_model" + f"{NSTEPS*iter}"))