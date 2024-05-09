import os
import argparse
from stable_baselines3 import SAC
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.env_util import make_vec_env
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

parser = argparse.ArgumentParser(description="Train or test the model")
parser.add_argument('mode', type=str, help='Mode to run the program in')
args = parser.parse_args()

if args.mode == 'train':
    env = QuadrupedGymEnv(**env_configs, render_mode="human", mode="train") 
    env = Monitor(env, log_dir, info_keywords=('x_position', 'x_velocity', 'actions', 'reward_forward', 'reward_ctrl'))
    
    model = SAC('MlpPolicy', env, device="auto", tensorboard_log=log_dir, verbose=1)

    iter = 0
    while True:
        iter += 1
        model.learn(total_timesteps=NSTEPS, reset_num_timesteps=False)
        model.save(os.path.join(model_dir, "rl_model" + f"{NSTEPS*iter}"))
elif args.mode == 'test':
    env = lambda: QuadrupedGymEnv(**env_configs, render_mode="human", mode="test")
    env = make_vec_env(env, n_envs=1)
    
    model_name = os.path.join(model_dir, "rl_model210000.zip")
    model = SAC.load(model_name, env)
    print("\nLoaded model", model_name, "\n")

    obs = env.reset()
    episode_reward = 0

    while True:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, done, info = env.step(action)    
        if done:
            obs = env.reset()