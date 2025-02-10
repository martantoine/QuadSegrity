__credits__ = ["Antoine Vincent Martin", "Kallinteris-Andreas", "Rushiv Arora"]

from typing import Dict, Union

import numpy as np
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="stable_baselines3.common.save_util")
from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box, Tuple
from gymnasium.spaces.utils import flatten_space
import mujoco as mj
import matplotlib


DEFAULT_CAMERA_CONFIG = {
    "distance": 4.0,
}


class QuadrupedGymEnv(MujocoEnv, utils.EzPickle):
    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
    }

    def __init__(
        self,
        xml_file: str = "./leg_parametric.xml",
        frame_skip: int = 50,
        default_camera_config: Dict[str, Union[float, int]] = DEFAULT_CAMERA_CONFIG,
        forward_reward_weight: float = 1.0,
        force_cost_weight: float = 0.1,
        switching_rate_cost_weight: float = 0.1,
        reset_noise_scale: float = 0.1,
        force_max: float = 40.0,
        switching_max: int = 10,
        total_timesteps: int = 1000,
        mode: str = "train",
        **kwargs,
    ):
        utils.EzPickle.__init__(
            self,
            xml_file,
            frame_skip,
            default_camera_config,
            forward_reward_weight,
            force_cost_weight,
            switching_rate_cost_weight,
            reset_noise_scale,
            force_max,
            switching_max,
            total_timesteps,
            mode,
            **kwargs,
        )

        self._forward_reward_weight = forward_reward_weight
        self._force_cost_weight = force_cost_weight
        self._switching_rate_cost_weight = switching_rate_cost_weight
        self._reset_noise_scale = reset_noise_scale
        self._switching_max = switching_max
        self.total_timesteps = total_timesteps
        self._mode = mode

        MujocoEnv.__init__(
            self,
            xml_file,
            frame_skip,
            observation_space=None,
            default_camera_config=default_camera_config,
            **kwargs,
        )

        self.metadata = {
            "render_modes": [
                "human",
                "rgb_array",
                "depth_array",
            ],
            "render_fps": int(np.round(1.0 / self.dt)),
        }

        obs_size = (
            3 #zaxis
            + 8 #actuators force
        )
        
        self.observation_structure = {
            "zaxis": 3,
            "actuators related": 8,
            #"body height": 1,
            #"body velocity": 3,
        }

        self.observation_space = Box(
            low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float64
        )
        
        self.action_space = Box(low=0, high=force_max, shape=(8,), dtype=np.float32)
    
        self.old_forces = np.zeros(8)
        self.time = 0

    def control_cost(self, action):
        control_cost = self._force_cost_weight * np.sum(np.abs(action)) \
                     + self._switching_rate_cost_weight * np.sum(np.abs(action - self.old_forces))
        return control_cost

    def step(self, action):
        x_position_before = self.data.qpos[1]

        if self._mode == "train":
            self.do_simulation(action, self.frame_skip)
            self.time += self.frame_skip
            if self.render_mode == "human":
                        self.render()
        else:
            for i in range(self.frame_skip):
                self.do_simulation(action, 1)
                self.time += 1
                if self.render_mode == "human":
                            self.render()
        
        x_position_after = self.data.qpos[1]
        x_velocity = -(x_position_after - x_position_before) / self.dt

        observation = self._get_obs()
        reward, reward_info = self._get_rew(x_velocity, action, observation)
        info = {"x_position": x_position_after, "x_velocity": x_velocity, "actions": action, **reward_info}

        
        out_of_time = self.time >= self.total_timesteps - 1
        
        return observation, reward, False, out_of_time, info

    def _get_rew(self, x_velocity: float, action, obs):
        forward_reward = self._forward_reward_weight * x_velocity
        ctrl_cost = self.control_cost(action)
        contact_penalty = 0
        for c in self.data.contact:
            body_colliding_name = mj.mj_id2name(self.model, mj.mjtObj.mjOBJ_BODY, self.model.geom_bodyid[c.geom2])
            if "humerus" in body_colliding_name:
                contact_penalty += 1
        stil_cost = np.exp(-np.abs(x_velocity))
        verticality_reward = np.dot(obs[0:3], [0, 0, 1])
        reward = forward_reward - ctrl_cost - contact_penalty + verticality_reward# - stil_cost
        
        reward_info = {
            "reward_forward": forward_reward,
            "reward_ctrl": -ctrl_cost,
        }
        return reward, reward_info

    def _get_obs(self):
        #velocity = self.data.qvel[0:3].flatten() #velocity of the body

        zaxis = self.data.sensordata[0:3].flatten() #zaxis

        forces   = self.data.sensordata[3:].flatten() #force sensors for each muscle
        #dforces  = forces - self.old_forces
        forces_history.append(self.data.sensordata[3:].flatten())
        
        plt.plot(forces_history.append(self.data.sensordata[3:].flatten()), self.time)
        plt.savefig("force_sensor.png")

        self.old_forces = forces

        
        return np.concatenate((zaxis, forces)).ravel()
        
    # def do_simulation(self, ctrl, n_frames) -> None:
    #     """
    #     Step the simulation n number of frames and applying a control action.
    #     """

    #     # converting the crtl to ctrl final
    #     # ctrl: 2 Forces and 8 on/off valves
    #     # ctrl_final: 8 forces

    #     ctrl_final = np.zeros((8,))
    #     for i in range(len(ctrl_final)):
    #         if ctrl[2+i] == self._switching_max:
    #             ctrl_final[i] = ctrl[i%2]
    #         else:
    #             ctrl_final[i] = self.old_forces[i]
    #     # Check control input is contained in thet action space
    #     if np.array(ctrl_final).shape != (self.model.nu,):
    #         raise ValueError(
    #             f"Action dimension mismatch. Expected {(self.model.nu,)}, found {np.array(ctrl_final).shape}"
    #         )
    #     self._step_mujoco_simulation(ctrl_final, n_frames)

    def reset_model(self):
        noise_low = -self._reset_noise_scale
        noise_high = self._reset_noise_scale

        qpos = self.init_qpos + self.np_random.uniform(
            low=noise_low, high=noise_high, size=self.model.nq
        )
        qvel = (
            self.init_qvel
            + self._reset_noise_scale * self.np_random.standard_normal(self.model.nv)
        )

        self.set_state(qpos, qvel)
        self.time = 0
        observation = self._get_obs()
        return observation

    def _get_reset_info(self):
        return {
            "x_position": self.data.qpos[0],
        }
