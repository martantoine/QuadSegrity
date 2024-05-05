__credits__ = ["Anoine Vincent Martin", "Kallinteris-Andreas", "Rushiv Arora"]

from typing import Dict, Union

import numpy as np

from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box, Tuple
from gymnasium.spaces.utils import flatten_space


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
        frame_skip: int = 5,
        default_camera_config: Dict[str, Union[float, int]] = DEFAULT_CAMERA_CONFIG,
        forward_reward_weight: float = 1.0,
        force_cost_weight: float = 0.1,
        switching_rate_cost_weight: float = 0.1,
        reset_noise_scale: float = 0.1,
        exclude_current_positions_from_observation: bool = True,
        force_max: float = 40.0,
        switching_max: int = 10,
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
            exclude_current_positions_from_observation,
            force_max,
            switching_max,
            **kwargs,
        )

        self._forward_reward_weight = forward_reward_weight
        self._force_cost_weight = force_cost_weight
        self._switching_rate_cost_weight = switching_rate_cost_weight
        self._reset_noise_scale = reset_noise_scale
        self._switching_max = switching_max

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
            8 * 4 #actuators force, dforce, c, dc
            + 3 #body attitude
            + 1 #body height
            + 3 #body velocity
        )
        
        self.observation_space = Box(
            low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float64
        )
        
        # self.action_space = flatten_space(Tuple((
        #     Box(low=0, high=force_max, shape=(2,), dtype=np.float64),
        #     Box(low=0, high=switching_max, shape=(8,), dtype=np.int8)
        # )))
        self.action_space = Box(low=0, high=force_max, shape=(10,), dtype=np.float32)

        self.old_c = np.zeros(8)
        self.c = np.zeros(8)
        self.old_forces = np.zeros(8)

    def control_cost(self, action):
        control_cost = self._force_cost_weight * np.sum(np.square(action[0:2])) \
                     + self._switching_rate_cost_weight * np.sum(np.square(action[3:10] - self.old_c))
        return control_cost

    def step(self, action):
        x_position_before = self.data.qpos[0]
        self.do_simulation(action, self.frame_skip)
        x_position_after = self.data.qpos[0]
        x_velocity = (x_position_after - x_position_before) / self.dt

        observation = self._get_obs()
        reward, reward_info = self._get_rew(x_velocity, action)
        info = {"x_position": x_position_after, "x_velocity": x_velocity, **reward_info}

        if self.render_mode == "human":
            self.render()
        # truncation=False as the time limit is handled by the `TimeLimit` wrapper added during `make`
        return observation, reward, False, False, info

    def _get_rew(self, x_velocity: float, action):
        forward_reward = self._forward_reward_weight * x_velocity
        ctrl_cost = self.control_cost(action)

        reward = forward_reward - ctrl_cost

        reward_info = {
            "reward_forward": forward_reward,
            "reward_ctrl": -ctrl_cost,
        }
        return reward, reward_info

    def _get_obs(self):
        velocity = self.data.qvel[0:3].flatten() #velocity of the body

        #forces   = self.data.sensordata[4:12].flatten() #force sensors for each muscle
        forces   = self.data.ctrl.flatten() #force sensors for each muscle
        dforces  = forces - self.old_forces
        self.old_forces = forces

        dc = self.c - self.old_c
        self.old_c = self.c

        attitude = self.data.sensordata[0:3].flatten() #gyro sensor on the body
        height = self.data.sensordata[3].flatten() #rangefinder sensor on the body

        observation = np.concatenate((forces, dforces, self.c, dc, attitude, height, velocity)).ravel()
        return observation
    
    def do_simulation(self, ctrl, n_frames) -> None:
        """
        Step the simulation n number of frames and applying a control action.
        """

        # converting the crtl to ctrl final
        # ctrl: 2 Forces and 8 on/off valves
        # ctrl_final: 8 forces

        ctrl_final = np.zeros((8,))
        for i in range(len(ctrl_final)):
            if ctrl[2+i] == self._switching_max:
                ctrl_final[i] = ctrl[i%2]
            else:
                ctrl_final[i] = self.old_forces[i]
        # Check control input is contained in thet action space
        if np.array(ctrl_final).shape != (self.model.nu,):
            raise ValueError(
                f"Action dimension mismatch. Expected {(self.model.nu,)}, found {np.array(ctrl_final).shape}"
            )
        self._step_mujoco_simulation(ctrl_final, n_frames)

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

        observation = self._get_obs()
        return observation

    def _get_reset_info(self):
        return {
            "x_position": self.data.qpos[0],
        }
