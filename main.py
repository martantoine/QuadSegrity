from xml.dom import minidom 
import os

from environment import *
import builders

root = minidom.Document()

env = Env(root)
env.constants = {
    'density': 1000,
    
    'tendon_stiffness': 100,
    'tendon_damping': 10,
    'tendon_rgba': '0.5 0.5 0.5 1',
    'tendon_range': '-0.01 0.01',
    'tendon_limited': 'true',

    'muscle_tendon_stiffness': 100,
    'muscle_tendon_damping': 10,
    'muscle_tendon_rgba': '1 1 1 1',
    'muscle_tendon_range': '-0.01 0.01',
    'muscle_tendon_limited': 'true',

    'muscle_lengthrange': '-10.15 10.25',
    'muscle_forcerange': '-20 20',
    'muscle_range': '0.7 1.3',

    'teeth_length': 0.03,
    'teeth_opening_big': 40,
    'teeth_opening_small': 25,

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

builders.env = env
leg = builders.Leg('rl', [ 0, 0, 0])
#leg = builders.Leg('rl', [ 0.15,  0.2, 0])
#leg = builders.Leg('rr', [-0.15,  0.2, 0])
#leg = builders.Leg('fr', [ 0.15, -0.2, 0])
#leg = builders.Leg('fl', [-0.15, -0.2, 0])

xml_str = root.toprettyxml(indent ="\t")
save_path_file = "leg_parametric.xml"
with open(save_path_file, "w") as f:
    f.write(xml_str)