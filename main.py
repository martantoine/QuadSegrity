from xml.dom import minidom 
import os

from environment import *
import builders

root = minidom.Document()

env = Env(root)
env.constants = {
    'teeth_length': 0.03,
    'teeth_opening_big': 40,
    'teeth_opening_small': 25,
    'site_space': 0.0025,
    'site_radius': 0.003,
    'beam_radius': 0.0025,

    'scapula_length': 0.05,
    'scapula_angle': 45,
    'hip_angle': -45,
    'humerus_length': 0.10,
    'knee_angle': -45,
    'radius_length': 0.05,
    'radius_angle': -135
}
env.init()

builders.env = env
leg = builders.Leg('rl', [ 0.15,  0.2, 0])
leg = builders.Leg('rr', [-0.15,  0.2, 0])
leg = builders.Leg('fr', [ 0.15, -0.2, 0])
leg = builders.Leg('fl', [-0.15, -0.2, 0])

xml_str = root.toprettyxml(indent ="\t")
save_path_file = "leg_parametric.xml"
with open(save_path_file, "w") as f:
    f.write(xml_str)