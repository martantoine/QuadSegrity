import os
from datetime import datetime
from stable_baselines3 import SAC
from quadruped_gym_env import QuadrupedGymEnv
from stable_baselines3.common.vec_env import VecNormalize
from stable_baselines3.common.env_util import make_vec_env

# after implementing, you will want to test how well the agent learns with your MDP: 



model_dir = './rl/model/'#+ datetime.now().strftime("%m%d%y%H%M%S") + '/'
log_dir = './rl/log/'#+ datetime.now().strftime("%m%d%y%H%M%S") + '/'
os.makedirs(model_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)
# checkpoint to save policy network periodically
#checkpoint_callback = CheckpointCallback(save_freq=3000, save_path=SAVE_PATH,name_prefix='rl_model', verbose=2)


TIMESTEPS = 5000
env_configs = {"force_max": 40.0,
               "switching_max": 10,
               "total_timesteps": TIMESTEPS,
               } 
env = QuadrupedGymEnv(**env_configs, render_mode="human") 
#env = QuadrupedGymEnv(**env_configs)  

#env = lambda: QuadrupedGymEnv(**env_configs, render_mode="human")
#env = make_vec_env(env, monitor_dir=log_dir,n_envs=1)
# normalize observations to stabilize learning (why?)
#env = VecNormalize(env, norm_obs=True, norm_reward=False, clip_obs=100.)

#env = make_vec_env(env, monitor_dir=SAVE_PATH,n_envs=1)
# normalize observations to stabilize learning (why?)
#env = VecNormalize(env, norm_obs=True, norm_reward=False, clip_obs=100.)

model = SAC('MlpPolicy', env, device="auto", tensorboard_log=log_dir, verbose=1, learning_rate=0.1)

iter = 0
while True:
    iter += 1
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False)
    model.save(os.path.join(model_dir, "rl_model" + f"{TIMESTEPS*iter}"))