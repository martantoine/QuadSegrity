from xml.dom import minidom 
import os

import numpy as np

from environment import *
import builders

root = minidom.Document()

env = Env(root)
env.constants = {
    'air_density': 1.2,
    'geom_density': 2000,
    'gravity': '0 0 -9.81',
    'integrator': 'RK4', #implicitfast
    'timestep': 0.001,
    'viscosity': 0.2,

    'hinge_stiffness': 4.40,
    
    'muscle_tendon_limited': 'false',
    'muscle_tendon_range': '-0.01 0.01',
    'muscle_tendon_rgba': '0.05 0.05 0.8 1',
    'muscle_tendon_stiffness': 0,
    'muscle_tendon_damping': 1,
    
    'muscle_lengthrange': '-10 10', #exact value not revelant, must be big enough for stability
    'muscle_force': 40,
    'muscle_scale': 200, #200 is the default scale
    'muscle_range': '0.8 1.2',

    'site_space': 0.0025,
    'site_radius': 0.008,
    'beam_radius': 0.004,
    'geom_rgba': '0.3 0.3 0.3 1',

    'scapula_length': 0.1,
    'scapula_angle': 225,
    
    'humerus_length': 0.2,
    'humerus_angle': -45,
    
    'radius_length': 0.25,
    'radius_angle': -110,
    
    'hip_angle': 0,
    'knee_angle': 180,

    'core_mass': 1.5,
    'core_pos': [0, 0, 0.1],

    'body_width': 0.33,
    'body_length': 0.72,
    'feet_radius': 0.02,
    'feet_width': 0.045,
    #'feet_width': 0.02,

    'star_length': 0.05,
    'losange_spacing': 0.0358,
    'losange_length': 0.1
}
env.init()

builders.env = env
robot = builders.Quadruped('QuadSegrity1', np.array([0, 0, 0]))
xml_str = root.toprettyxml(indent ="\t")
save_path_file = "leg_parametric.xml"
with open(save_path_file, "w") as f:
    f.write(xml_str)
