from xml.dom import minidom 
import os

from environment import *
import builders

root = minidom.Document()

env = Env(root)
env.constants = {
    'air_density': 1.2,
    'geom_density': 2000,
    'integrator': 'RK4', #implicitfast
    'timestep': 0.001,
    'viscosity': 0.002,

    'hinge_stiffness': 1.14,
    'muscle_tendon_stiffness': 0,
    'muscle_tendon_damping': 1,
    'muscle_tendon_rgba': '0.05 0.05 0.8 1',
    'muscle_tendon_range': '-0.01 0.01',
    'muscle_tendon_limited': 'false',

    'tendon_stiffness': 2000,
    'tendon_damping': 1,
    'tendon_rgba': '0.8 0.05 0.05 1',
    'tendon_range': '-0.1 0.1',
    'tendon_limited': 'true',
    
    'muscle_lengthrange': '-10 10', #exact value not revelant, must be big enough for stability
    'muscle_scale': 200, #200 is the default scale
    'muscle_force': 80,
    'muscle_range': '0.1 1.8',

    'star_teeth_length': 0.06,
    'fork_teeth_length': 0.04,
    'fork_opening_big': 0.06,
    'fork_opening_small': 0.04,

    'site_space': 0.0025,
    'site_radius': 0.0041,
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

    'core_mass': 0.1,
    'core_pos': [0, 0, 0.1]
}
env.init()

if __name__ == "__main__":
    builders.env = env
    
    #robot = builders.Quadruped('QuadSegrity1', env.constants['core_pos'])
    leg = builders.Leg('leg', env.worldbody, env.constants['core_pos'], 0)
    xml_str = root.toprettyxml(indent ="\t")
    save_path_file = "leg_parametric.xml"
    with open(save_path_file, "w") as f:
        f.write(xml_str)