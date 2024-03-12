from xml.dom import minidom 
import numpy as np
import os  
  
# MODEL PARAMETERS (S.I. units)
teeth_length = 0.02
site_space = 0.0025
site_radius = 0.0025
beam_radius = 0.0025

root = minidom.Document() 
  
xml = root.createElement('mujoco')  
root.appendChild(xml) 
  
# OPTION
option = root.createElement('option') 
option.setAttribute('timestep', '0.005')
option.setAttribute('iterations', '50')
option.setAttribute('integrator', 'RK4')
option.setAttribute('tolerance', '1e-10') 
xml.appendChild(option) 
  
# DEFAULT
default = root.createElement('default') 
joint = root.createElement('joint')
joint.setAttribute('type', 'ball')
default.appendChild(joint)

muscle = root.createElement('muscle')
muscle.setAttribute('ctrllimited', 'true')
muscle.setAttribute('ctrlrange', '-1000 1000')
default.appendChild(muscle)

geom = root.createElement('geom')
geom.setAttribute('size', f'{beam_radius}')
geom.setAttribute('mass', '0.1')
geom.setAttribute('rgba', '.5 .1 .1 1')
default.appendChild(geom)

site = root.createElement('site')
site.setAttribute('size', f'{site_radius}')
site.setAttribute('rgba', '0 .7 0 1')
default.appendChild(site)

tendon = root.createElement('tendon')
tendon.setAttribute('rgba', '0 1 0 1')
tendon.setAttribute('stiffness', '1000')
tendon.setAttribute('damping', '15')
default.appendChild(tendon)
xml.appendChild(default)

# ASSET
asset = root.createElement('asset')
texture = root.createElement('texture')
texture.setAttribute('name', 'texplane')
texture.setAttribute('type', '2d')
texture.setAttribute('builtin', 'checker')
texture.setAttribute('rgb1', '.25 .25 .25')
texture.setAttribute('rgb2', '.28 .28 .28')
texture.setAttribute('width', '512')
texture.setAttribute('height', '512')
texture.setAttribute('markrgb', '.8 .8 .8')
asset.appendChild(texture)

material = root.createElement('material')
material.setAttribute('name', 'matplane')
material.setAttribute('reflectance', '0.1')
material.setAttribute('texture', 'texplane')
material.setAttribute('texrepeat', '1 1')
material.setAttribute('texuniform', 'true')
asset.appendChild(material)
xml.appendChild(asset)

# WORLDBODY
worldbody = root.createElement('worldbody')
geom = root.createElement('geom')
geom.setAttribute('name', 'floor')
geom.setAttribute('rgba', '1 1 1 1')
geom.setAttribute('pos', '0 0 -0.35')
geom.setAttribute('size', '0 0 1')
geom.setAttribute('type', 'plane')
geom.setAttribute('material', 'matplane')
worldbody.appendChild(geom)

light = root.createElement('light')
light.setAttribute('directional', 'true')
light.setAttribute('diffuse', '.8 .8 .8')
light.setAttribute('specular', '.2 .2 .2')
light.setAttribute('pos', '0 0 5')
light.setAttribute('dir', '0 0 -1')
worldbody.appendChild(light)
xml.appendChild(worldbody)


def addFork(name, parent, center, stick_length, angle_y, angle_opening):
    # A
    #   \
    #    C -- D
    #   /
    # B
    # center between A and B
    angle_y = np.deg2rad(angle_y)
    angle_opening = np.deg2rad(angle_opening)
    rotation = np.array([[1, 0              ,  0              ],
                         [0, np.cos(angle_y), -np.sin(angle_y)],
                         [0, np.sin(angle_y),  np.cos(angle_y)]])
                         
    print(center + [ np.sin(angle_opening) * teeth_length, 0, 0])
    A = np.dot(rotation, center + [ np.sin(angle_opening) * teeth_length, 0, 0])
    B = np.dot(rotation, center + [-np.sin(angle_opening) * teeth_length, 0, 0])
    C = np.dot(rotation, center + [ 0.0                                 , np.cos(angle_opening) * teeth_length, 0])
    D = np.dot(rotation, center + [ 0.0                                 , np.cos(angle_opening) * teeth_length + stick_length, 0])
    
    beam = root.createElement('geom')
    beam.setAttribute('type', 'capsule')
    beam.setAttribute('fromto', f'{A[0]} {A[1]} {A[2]} {C[0]} {C[1]} {C[2]}')
    parent.appendChild(beam)

    beam = root.createElement('geom')
    beam.setAttribute('type', 'capsule')
    beam.setAttribute('fromto', f'{B[0]} {B[1]} {B[2]} {C[0]} {C[1]} {C[2]}')
    parent.appendChild(beam)

    beam = root.createElement('geom')
    beam.setAttribute('type', 'capsule')
    beam.setAttribute('fromto', f'{D[0]} {D[1]} {D[2]} {C[0]} {C[1]} {C[2]}')
    parent.appendChild(beam)

    #<!--QUAD FORK START-->
    s0 = np.dot(rotation, center + [0.0, np.cos(angle_opening) * teeth_length + stick_length, 0] + [0, 0, site_space])
    s1 = np.dot(rotation, center + [0.0, np.cos(angle_opening) * teeth_length + stick_length, 0] + [0, 0, -site_space])
    s2 = np.dot(rotation, center + [0.0, np.cos(angle_opening) * teeth_length + stick_length, 0] + [ site_space, 0, 0])
    s3 = np.dot(rotation, center + [0.0, np.cos(angle_opening) * teeth_length + stick_length, 0] + [-site_space, 0, 0])
    
    site = root.createElement('site')
    site.setAttribute('name', name + '_0')
    site.setAttribute('pos', f'{s0[0]} {s0[1]} {s0[2]}')
    parent.appendChild(site)
    site = root.createElement('site')
    site.setAttribute('name', name + '_1')
    site.setAttribute('pos', f'{s1[0]} {s1[1]} {s1[2]}')
    parent.appendChild(site)
    site = root.createElement('site')
    site.setAttribute('name', name + '_2')
    site.setAttribute('pos', f'{s2[0]} {s2[1]} {s2[2]}')
    parent.appendChild(site)
    site = root.createElement('site')
    site.setAttribute('name', name + '_3')
    site.setAttribute('pos', f'{s3[0]} {s3[1]} {s3[2]}')
    parent.appendChild(site)

    #<!--QUAD FORK MIDDLE-->
    #<site name="y0_4" pos="0.05  0.01  0   " rgba="0 0 .7 1"/>
    #<site name="y0_5" pos="0.05 -0.01  0   " rgba="0 0 .7 1"/>
    #<site name="y0_6" pos="0.05  0     0.01" rgba="0 0 .7 1"/>
    #<site name="y0_7" pos="0.05  0    -0.01" rgba="0 0 .7 1"/>
#
    #<!--QUAD FORK END-->
    #<site name="y0_8" pos="0.1  0.05 0"/>
    #<site name="y0_9" pos="0.1 -0.05 0"/>


addFork('y0', worldbody, np.array([0, 0, 0]), 0.03, 25, 30)
xml_str = root.toprettyxml(indent ="\t")  
  
save_path_file = "leg_parametric.xml"

with open(save_path_file, "w") as f: 
    f.write(xml_str)  