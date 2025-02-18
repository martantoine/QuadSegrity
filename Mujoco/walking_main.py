import os, re, argparse, sys
import numpy as np
import torch as th
import onnxruntime as ort
from stable_baselines3 import SAC
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.env_util import make_vec_env
from quadruped_gym_env import QuadrupedGymEnv

def get_latest_zip(directory, prefix):
    # Regular expression to extract numbers after the prefix and before ".zip"
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)\.zip$")
    
    max_number = -1
    max_file = None

    # Iterate through the files in the directory
    for file in os.listdir(directory):
        match = pattern.match(file)
        if match:
            number = int(match.group(1))
            if number > max_number:
                max_number = number
                max_file = file
    if max_number == -1:
        return False
    return max_file

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
               "forward_reward_weight": 50.0,
               "force_cost_weight": 0.0001,
               "switching_rate_cost_weight": 0.001,
               "total_timesteps": NSTEPS,
               "frame_skip": control_step_skip,
               }

parser = argparse.ArgumentParser(description="Train, test, or export the model")
parser.add_argument('mode', type=str, help='Mode to run the program in: train, test, onnx')
parser.add_argument('name', type=str, help='Base name of the model to use')
parser.add_argument('xml', type=str, help='path and name of the Mujoco .xml')
args = parser.parse_args()

if not os.path.isfile(args.xml):
    print("Critical Error!: Mujoco .xml " + args.xml + " not found")
    print("Exiting script")
    sys.exit()

if args.mode == 'train':
    env = QuadrupedGymEnv(**env_configs, xml_file=args.xml, mode="train") 
    env = Monitor(env, log_dir, info_keywords=('x_position', 'x_velocity', 'actions', 'reward_forward', 'reward_ctrl'))
    
    model = SAC('MlpPolicy', env, device="auto", tensorboard_log=log_dir, verbose=1, learning_rate=0.01)

    iter = 0
    while True:
        iter += 1
        model.learn(total_timesteps=NSTEPS, reset_num_timesteps=False)
        model.save(os.path.join(model_dir, args.name + f"{NSTEPS*iter}"))

elif args.mode == 'test':
    env = lambda: QuadrupedGymEnv(**env_configs, render_mode="human", xml_file=args.xml, mode="test")
    env = make_vec_env(env, n_envs=1)
    
    model_name = get_latest_zip(model_dir, args.name)
    if not model_name:
        print(f"Critical Error!: There no model with prefix {args.name} under {model_dir} found")
        print("Exiting script")
        sys.exit()
    model_name = os.path.join(model_dir, model_name)

    model = SAC.load(model_name, env)
    print("Loaded model", model_name)

    obs = env.reset()
    episode_reward = 0

    while True:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, done, info = env.step(action)    
        if done:
            obs = env.reset()

elif args.mode == 'onnx':
    class OnnxablePolicy(th.nn.Module):
        def __init__(self, actor: th.nn.Module):
            super().__init__()
            self.actor = actor

        def forward(self, observation: th.Tensor) -> th.Tensor:
            # NOTE: You may have to postprocess (unnormalize) actions
            # to the correct bounds (see commented code below)
            return self.actor(observation, deterministic=True)
    
    env = lambda: QuadrupedGymEnv(**env_configs, xml_file=args.xml, mode="test")
    env = make_vec_env(env, n_envs=1)
    
    model_name = get_latest_zip(model_dir, args.name)
    if not model_name:
        print(f"Critical Error!: There no model with prefix {args.name} under {model_dir} found")
        print("Exiting script")
        sys.exit()
    model_name = os.path.join(model_dir, model_name)

    model = SAC.load(model_name, env)
    print("Loaded model", model_name)

    onnxable_model = OnnxablePolicy(model.policy.actor)

    observation_size = model.observation_space.shape
    dummy_input = th.randn(1, *observation_size)
    onnx_path = os.path.join(model_dir, args.name + "_actor.onnx")
    th.onnx.export(
        onnxable_model,
        dummy_input,
        onnx_path,
        opset_version=17,
        input_names=["input"],
    )


    observation = np.zeros((1, *observation_size)).astype(np.float32)
    ort_sess = ort.InferenceSession(onnx_path)
    scaled_action = ort_sess.run(None, {"input": observation})[0]
    
    # print the policy neural network size
    #print(model.policy.actor)
    print(scaled_action)
    
    # Post-process: rescale to correct space
    # Rescale the action from [-1, 1] to [low, high]
    # low, high = model.action_space.low, model.action_space.high
    # post_processed_action = low + (0.5 * (scaled_action + 1.0) * (high - low))

    # Check that the predictions are the same
    with th.no_grad():
        print(model.actor(th.as_tensor(observation), deterministic=True))

    sys.exit()