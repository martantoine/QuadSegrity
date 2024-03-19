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
    'viscosity': 0.0002,
    
    'tendon_stiffness': 2000,
    'tendon_damping': 1,
    'tendon_rgba': '0.5 0.5 0.5 1',
    'tendon_range': '-0.01 0.01',
    'tendon_limited': 'true',

    'muscle_tendon_stiffness': 500,
    'muscle_tendon_damping': 1,
    'muscle_tendon_rgba': '1 1 1 1',
    'muscle_tendon_range': '-0.01 0.01',
    'muscle_tendon_limited': 'false',
    
    'muscle_lengthrange': '-1 1', #exact value not revelant, must be big enough for stability
    'muscle_scale': 200, #200 is the default scale
    'muscle_force': 20,
    'muscle_range': '0.8 1.0',

    'teeth_length': 0.03,
    'teeth_opening_big': 42,
    'teeth_opening_small': 22,

    'site_space': 0.0025,
    'site_radius': 0.003,
    'beam_radius': 0.0025,
    'geom_rgba': '0.3 0.3 0.3 1',

    'scapula_length': 0.1,
    'scapula_angle': 225,
    
    'humerus_length': 0.2,
    'humerus_angle': -45,
    
    'radius_length': 0.15,
    'radius_angle': -135,
    
    'hip_angle': 0,
    'knee_angle': 180
}
env.init()

if __name__ == "__main__":
    builders.env = env
    robot = builders.env.root.createElement('body')
    robot.setAttribute('pos', '0 0 0')
    env.worldbody.appendChild(robot)
    free_joint = builders.env.root.createElement('joint')
    free_joint.setAttribute('type', 'free')
    robot.appendChild(free_joint)
    box = env.root.createElement('geom')
    box.setAttribute('type', 'box')
    box.setAttribute('density', '100')
    box.setAttribute('rgba', '0.3 0.3 0.3 0.5')
    box.setAttribute('pos', f'0 0 -0.1')
    box.setAttribute('size', f'0.15 0.2 {env.constants["beam_radius"]}')
    box.setAttribute('euler', f'180 0 0')
    robot.appendChild(box)


    #leg = builders.Leg('rl', [ 0, 0, 0])
    legRL = builders.Leg('rl', robot, [ 0.15,  0.2, -0.1])
    legRR = builders.Leg('rr', robot, [-0.15,  0.2, -0.1])
    legFR = builders.Leg('fr', robot, [ 0.15, -0.2, -0.1])
    legFL = builders.Leg('fl', robot, [-0.15, -0.2, -0.1])

    xml_str = root.toprettyxml(indent ="\t")
    save_path_file = "leg_parametric.xml"
    with open(save_path_file, "w") as f:
        f.write(xml_str)