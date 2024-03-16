from xml.dom import minidom 
import numpy as np
import os  

root = minidom.Document() 
  
xml = root.createElement('mujoco')  
root.appendChild(xml) 

class Fork:
    def __init__(self, name, parent, center, mode, stick_length, angle_y, angle_opening):
        self.name = name
        self.parent = parent
        self.center = center
        self.mode = mode
        self.stick_length = stick_length
        self.angle_y = angle_y
        self.angle_opening = angle_opening
        self.create_fork()

    def create_fork(self):
        # A
        #   \
        #    C -- D
        #   /
        # B
        # mode: 'AB': center between A and B
        # mode: 'D' : center at D
        angle_y = np.deg2rad(self.angle_y)
        angle_opening = np.deg2rad(self.angle_opening)
        rotation = np.array([[1, 0, 0],
                             [0, np.cos(angle_y), -np.sin(angle_y)],
                             [0, np.sin(angle_y), np.cos(angle_y)]])

        if self.mode == 'AB':
            self.A = self.center + np.dot(rotation, [ np.sin(angle_opening) * teeth_length, 0                                                       , 0])
            self.B = self.center + np.dot(rotation, [-np.sin(angle_opening) * teeth_length, 0                                                       , 0])
            self.C = self.center + np.dot(rotation, [ 0.0                                 , np.cos(angle_opening) * teeth_length                    , 0])
            self.D = self.center + np.dot(rotation, [ 0.0                                 , np.cos(angle_opening) * teeth_length + self.stick_length, 0])
        elif self.mode == 'D':
            self.A = self.center + np.dot(rotation, [ np.sin(angle_opening) * teeth_length, np.cos(angle_opening) * teeth_length + self.stick_length, 0])
            self.B = self.center + np.dot(rotation, [-np.sin(angle_opening) * teeth_length, np.cos(angle_opening) * teeth_length + self.stick_length, 0])
            self.C = self.center + np.dot(rotation, [ 0.0                                 , self.stick_length                                       , 0])
            self.D = self.center + np.dot(rotation, [ 0.0                                 , 0                                                       , 0])

        beam = root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.A[0]} {self.A[1]} {self.A[2]} {self.C[0]} {self.C[1]} {self.C[2]}')
        self.parent.appendChild(beam)
        beam = root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.B[0]} {self.B[1]} {self.B[2]} {self.C[0]} {self.C[1]} {self.C[2]}')
        self.parent.appendChild(beam)
        beam = root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.D[0]} {self.D[1]} {self.D[2]} {self.C[0]} {self.C[1]} {self.C[2]}')
        self.parent.appendChild(beam)

    def getAB(self):
        return (self.A + self.B) / 2

    def getD(self):
        return self.D

class Star:
    def __init__(self, name, parent, center, angle_y):
        self.name = name
        self.parent = parent
        self.center = center
        self.angle_y = angle_y
        self.create_star()

    def create_star(self):
        # B
        #   \
        #    A -- D
        #   /
        # C
        # center at A
        angle_y = np.deg2rad(self.angle_y)
        angle_opening = np.deg2rad(120)
        rotation = np.array([[1, 0              ,  0              ],
                             [0, np.cos(angle_y), -np.sin(angle_y)],
                             [0, np.sin(angle_y),  np.cos(angle_y)]])
                            
        A = self.center
        B = self.center + np.dot(rotation, teeth_length * np.array([0, np.cos(angle_opening),  np.sin(angle_opening)]))
        C = self.center + np.dot(rotation, teeth_length * np.array([0, np.cos(angle_opening), -np.sin(angle_opening)]))
        D = self.center + np.dot(rotation, teeth_length * np.array([0, 1                    ,  0                    ]))
        
        beam = root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{A[0]} {A[1]} {A[2]} {B[0]} {B[1]} {B[2]}')
        self.parent.appendChild(beam)

        beam = root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{A[0]} {A[1]} {A[2]} {C[0]} {C[1]} {C[2]}')
        self.parent.appendChild(beam)

        beam = root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{A[0]} {A[1]} {A[2]} {D[0]} {D[1]} {D[2]}')
        self.parent.appendChild(beam)

class Leg:
    def __init__(self, name, parent, center):
        self.name = name
        self.parent = parent
        self.center = center
        self.create_leg()
    
    def create_leg(self):
        self.scalupa     = Fork(self.name + '_scalupa'    , self.parent      , self.center            , 'D' , 0.1, 225, 45)
        
        self.humerus_body = root.createElement('body')
        humerus_origin = self.scalupa.getAB()
        self.humerus_body.setAttribute('pos', str(humerus_origin)[1:-1].replace(',', ''))
        self.parent.appendChild(self.humerus_body)
        self.humerus_top = Fork(self.name + '_humerus_top', self.humerus_body, np.array([0, 0, 0])   , 'AB', 0.1, -45, 28)
        self.humerus_bot = Fork(self.name + '_humerus_bot', self.humerus_body, self.humerus_top.getD(), 'D' , 0.1, -45, 28)

        self.radius_body = root.createElement('body')
        radius_origin = humerus_origin + self.humerus_bot.getAB()
        self.radius_body.setAttribute('pos', str(radius_origin)[1:-1].replace(',', ''))
        self.parent.appendChild(self.radius_body)
        self.radius      = Fork(self.name + '_radius', self.radius_body, np.array([0, 0, 0]), 'AB' , 0.15, 225, 45)

        self.hip_body = root.createElement('body')
        self.hip_body.setAttribute('pos', str(humerus_origin)[1:-1].replace(',', ''))
        self.hip  = Star(self.name + '_hip' , self.hip_body, np.array([0, 0, 0]), 0)
        self.parent.appendChild(self.hip_body)
        
        self.knee_body = root.createElement('body')
        self.knee_body.setAttribute('pos', str(radius_origin)[1:-1].replace(',', ''))
        self.knee = Star(self.name + '_knee', self.knee_body, np.array([0, 0, 0]), 180)
        self.parent.appendChild(self.knee_body)


# MODEL PARAMETERS (S.I. units)
teeth_length = 0.03
teeth_opening_big = 40
teeth_opening_small = 25
site_space = 0.0025
site_radius = 0.0025
beam_radius = 0.0025

scapula_length = 0.05
scapula_angle = 45
hip_angle = -45
humerus_length = 0.10
knee_angle = -45
radius_length = 0.05
radius_angle = -135



# CAMERA
statistic = root.createElement('statistic')
statistic.setAttribute('extent', '0.4')
statistic.setAttribute('center', '0 0 -0.1')
xml.appendChild(statistic)

visual = root.createElement('visual')
visual_global = root.createElement('global')
visual_global.setAttribute('azimuth', '150')
visual_global.setAttribute('elevation', '-30')
visual.appendChild(visual_global)
xml.appendChild(visual)


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
geom.setAttribute('pos', '0 0 -0.5')
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

#def addFork(name, parent, center, stick_length, angle_y, angle_opening, vias=[True, True, True, True, True, True, True, True]):
#    # A
#    #   \
#    #    C -- D
#    #   /
#    # B
#    # center between A and B
#    angle_y = np.deg2rad(angle_y)
#    angle_opening = np.deg2rad(angle_opening)
#    rotation = np.array([[1, 0              ,  0              ],
#                         [0, np.cos(angle_y), -np.sin(angle_y)],
#                         [0, np.sin(angle_y),  np.cos(angle_y)]])
#                         
#    A = center + np.dot(rotation, [ np.sin(angle_opening) * teeth_length, 0, 0])
#    B = center + np.dot(rotation, [-np.sin(angle_opening) * teeth_length, 0, 0])
#    C = center + np.dot(rotation, [ 0.0                                 , np.cos(angle_opening) * teeth_length, 0])
#    D = center + np.dot(rotation, [ 0.0                                 , np.cos(angle_opening) * teeth_length + stick_length, 0])
#    
#    beam = root.createElement('geom')
#    beam.setAttribute('type', 'capsule')
#    beam.setAttribute('fromto', f'{A[0]} {A[1]} {A[2]} {C[0]} {C[1]} {C[2]}')
#    parent.appendChild(beam)
#
#    beam = root.createElement('geom')
#    beam.setAttribute('type', 'capsule')
#    beam.setAttribute('fromto', f'{B[0]} {B[1]} {B[2]} {C[0]} {C[1]} {C[2]}')
#    parent.appendChild(beam)
#
#    beam = root.createElement('geom')
#    beam.setAttribute('type', 'capsule')
#    beam.setAttribute('fromto', f'{D[0]} {D[1]} {D[2]} {C[0]} {C[1]} {C[2]}')
#    parent.appendChild(beam)
#
#    #QUAD FORK START
#    s = np.cos(angle_opening) * teeth_length + stick_length
#    s0 = center + np.dot(rotation, np.array([0, s, 0]) + np.array([0, 0, site_space]))
#    s1 = center + np.dot(rotation, np.array([0, s, 0]) + np.array([0, 0, -site_space]))
#    s2 = center + np.dot(rotation, np.array([0, s, 0]) + np.array([ site_space, 0, 0]))
#    s3 = center + np.dot(rotation, np.array([0, s, 0]) + np.array([-site_space, 0, 0]))
#    site = root.createElement('site')
#    site.setAttribute('name', name + '_0')
#    site.setAttribute('pos', f'{s0[0]} {s0[1]} {s0[2]}')
#    if vias[0]: parent.appendChild(site)
#    site = root.createElement('site')
#    site.setAttribute('name', name + '_1')
#    site.setAttribute('pos', f'{s1[0]} {s1[1]} {s1[2]}')
#    if vias[1]: parent.appendChild(site)
#    site = root.createElement('site')
#    site.setAttribute('name', name + '_2')
#    site.setAttribute('pos', f'{s2[0]} {s2[1]} {s2[2]}')
#    if vias[2]: parent.appendChild(site)
#    site = root.createElement('site')
#    site.setAttribute('name', name + '_3')
#    site.setAttribute('pos', f'{s3[0]} {s3[1]} {s3[2]}')
#    if vias[3]: parent.appendChild(site)
#
#    #QUAD FORK MIDDLE
#    s4 = center + np.dot(rotation, np.array([0, np.cos(angle_opening) * teeth_length, 0]) + np.array([0, 0, site_space]))
#    s5 = center + np.dot(rotation, np.array([0, np.cos(angle_opening) * teeth_length, 0]) + np.array([0, 0, -site_space]))
#    s6 = center + np.dot(rotation, np.array([0, np.cos(angle_opening) * teeth_length, 0]) + np.array([ site_space, 0, 0]))
#    s7 = center + np.dot(rotation, np.array([0, np.cos(angle_opening) * teeth_length, 0]) + np.array([-site_space, 0, 0]))
#    site = root.createElement('site')
#    site.setAttribute('name', name + '_4')
#    site.setAttribute('pos', f'{s4[0]} {s4[1]} {s4[2]}')
#    if vias[4]: parent.appendChild(site)
#    site = root.createElement('site')
#    site.setAttribute('name', name + '_5')
#    site.setAttribute('pos', f'{s5[0]} {s5[1]} {s5[2]}')
#    if vias[5]: parent.appendChild(site)
#    site = root.createElement('site')
#    site.setAttribute('name', name + '_6')
#    site.setAttribute('pos', f'{s6[0]} {s6[1]} {s6[2]}')
#    if vias[6]: parent.appendChild(site)
#    site = root.createElement('site')
#    site.setAttribute('name', name + '_7')
#    site.setAttribute('pos', f'{s7[0]} {s7[1]} {s7[2]}')
#    if vias[7]: parent.appendChild(site)
#
#    #QUAD FORK END
#    site = root.createElement('site')
#    site.setAttribute('name', name + '_9')
#    site.setAttribute('pos', f'{A[0]} {A[1]} {A[2]}')
#    parent.appendChild(site)
#    site = root.createElement('site')
#    site.setAttribute('name', name + '_8')
#    site.setAttribute('pos', f'{B[0]} {B[1]} {B[2]}')
#    parent.appendChild(site)
#    
#    return (A + B) / 2, 2*D-((A+B)/2)


#def addStar(name, parent, center, angle_y):
#    # B
#    #   \
#    #    A -- D
#    #   /
#    # C
#    # center at A
#    angle_y = np.deg2rad(angle_y)
#    angle_opening = np.deg2rad(120)
#    rotation = np.array([[1, 0              ,  0              ],
#                         [0, np.cos(angle_y), -np.sin(angle_y)],
#                         [0, np.sin(angle_y),  np.cos(angle_y)]])
#                         
#    A = center
#    B = center + np.dot(rotation, teeth_length * np.array([0, np.cos(angle_opening),  np.sin(angle_opening)]))
#    C = center + np.dot(rotation, teeth_length * np.array([0, np.cos(angle_opening), -np.sin(angle_opening)]))
#    D = center + np.dot(rotation, teeth_length * np.array([0, 1                    ,  0                    ]))
#    
#    beam = root.createElement('geom')
#    beam.setAttribute('type', 'capsule')
#    beam.setAttribute('fromto', f'{A[0]} {A[1]} {A[2]} {B[0]} {B[1]} {B[2]}')
#    parent.appendChild(beam)
#
#    beam = root.createElement('geom')
#    beam.setAttribute('type', 'capsule')
#    beam.setAttribute('fromto', f'{A[0]} {A[1]} {A[2]} {C[0]} {C[1]} {C[2]}')
#    parent.appendChild(beam)
#
#    beam = root.createElement('geom')
#    beam.setAttribute('type', 'capsule')
#    beam.setAttribute('fromto', f'{A[0]} {A[1]} {A[2]} {D[0]} {D[1]} {D[2]}')
#    parent.appendChild(beam)

## SCAPULA
#tmp, _ = addFork('scapula', worldbody, np.array([0, 0, 0]), scapula_length, scapula_angle, teeth_opening_big)
#
## HIP
#hip = root.createElement('body')
#hip.setAttribute('pos', '0 0 0')
#hip.setAttribute('euler', f'{scapula_angle} 0 0')
#free_joint = root.createElement('joint')
#free_joint.setAttribute('type', 'free')
##hip.appendChild(free_joint)
#worldbody.appendChild(hip)
#addStar('hip', hip, [0, 0, 0], 75)
#
## HUMERUS
#humerus = root.createElement('body')
#humerus.setAttribute('pos', '0 0 0')
#humerus.setAttribute('euler', f'{hip_angle} 0 0')
#free_joint = root.createElement('joint')
#free_joint.setAttribute('type', 'free')
##humerus.appendChild(free_joint)
#worldbody.appendChild(humerus)
#_, tmp = addFork('humerus_start', humerus, tmp, humerus_length/2, 0, teeth_opening_small, vias=[False, False, False, False, True, True, True, True])
#tmp, _ = addFork('humerus_end'  , humerus, tmp, humerus_length/2, 180, teeth_opening_small, vias=[False, False, False, False, True, True, True, True])
#
#
## KNEE POSITION
#rotation = np.array([[1, 0              ,  0              ],
#                     [0, np.cos(np.deg2rad(knee_angle)), -np.sin(np.deg2rad(knee_angle))],
#                     [0, np.sin(np.deg2rad(knee_angle)),  np.cos(np.deg2rad(knee_angle))]])
#tmp = np.dot(rotation, tmp)
#
## KNEE
#knee = root.createElement('body')
#knee.setAttribute('pos', f'{tmp[0]} {tmp[1]} {tmp[2]}')
#knee.setAttribute('euler', f'{knee_angle} 0 0')
#free_joint = root.createElement('joint')
#free_joint.setAttribute('type', 'free')
##knee.appendChild(free_joint)
#worldbody.appendChild(knee)
#addStar('knee', knee, [0, 0, 0], 0)
#
## RADIUS
#radius = root.createElement('body')
#radius.setAttribute('pos', f'{tmp[0]} {tmp[1]} {tmp[2]}')
#radius.setAttribute('euler', f'{radius_angle} 0 0')
#free_joint = root.createElement('joint')
#free_joint.setAttribute('type', 'free')
##radius.appendChild(free_joint)
#worldbody.appendChild(radius)
#addFork('radius', radius, [0, 0, 0], radius_length, 0, teeth_opening_big, vias=[False, False, False, False, True, True, False, False])
#
#beam = root.createElement('geom')
#beam.setAttribute('type', 'sphere')
#beam.setAttribute('pos', '0 0 0')
#worldbody.appendChild(beam)


leg = Leg('leg', worldbody, np.array([0.2, 0.2, 0]))
beam = root.createElement('geom')
beam.setAttribute('type', 'sphere')
beam.setAttribute('pos', '0.2 0.2 0')
beam.setAttribute('size', '0.04')
worldbody.appendChild(beam)
xml_str = root.toprettyxml(indent ="\t")  
  
save_path_file = "leg_parametric.xml"

with open(save_path_file, "w") as f: 
    f.write(xml_str)  