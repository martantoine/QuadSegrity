import numpy as np

env = None

class Fork:
    def __init__(self, name, parent, center, zangle, mode, stick_length, angle_y, opening, vias=[True, True, True, True, True, True, True, True]):
        self.name = name
        self.parent = parent
        self.center = center
        self.zangle = np.deg2rad(zangle)
        self.mode = mode
        self.stick_length = stick_length
        self.angle_y = angle_y
        self.opening = opening
        self.vias = vias
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
        rotationX = np.array([[1, 0, 0],
                              [0, np.cos(angle_y), -np.sin(angle_y)],
                              [0, np.sin(angle_y), np.cos(angle_y)]])
        rotationZ = np.array([[np.cos(self.zangle), -np.sin(self.zangle), 0],
                              [np.sin(self.zangle),  np.cos(self.zangle), 0],
                              [0              ,  0              , 1]])
        rotation = np.dot(rotationZ, rotationX)

        s = env.constants["fork_teeth_length"] + self.stick_length

        if self.mode == 'AB':
            self.A = self.center + np.dot(rotation, [ self.opening/2, 0                                 , 0])
            self.B = self.center + np.dot(rotation, [-self.opening/2, 0                                 , 0])
            self.C = self.center + np.dot(rotation, [ 0.0           , env.constants["fork_teeth_length"], 0])
            self.D = self.center + np.dot(rotation, [ 0.0           , s                                 , 0])

            # FORK END
            s0     = self.center + np.dot(rotation, np.array([0, s, 0]) + np.array([ 0              , 0, env.constants["site_space"]]))
            s1     = self.center + np.dot(rotation, np.array([0, s, 0]) + np.array([ 0              , 0, -env.constants["site_space"]]))
            s2     = self.center + np.dot(rotation, np.array([0, s, 0]) + np.array([ env.constants["site_space"], 0, 0]))
            s3     = self.center + np.dot(rotation, np.array([0, s, 0]) + np.array([-env.constants["site_space"], 0, 0]))
            # FORK MIDDLE
            s4     = self.center + np.dot(rotation, np.array([0, env.constants["fork_teeth_length"], 0]) + np.array([ 0                          , 0, env.constants["site_space"]]))
            s5     = self.center + np.dot(rotation, np.array([0, env.constants["fork_teeth_length"], 0]) + np.array([ 0                          , 0, -env.constants["site_space"]]))
            s6     = self.center + np.dot(rotation, np.array([0, env.constants["fork_teeth_length"], 0]) + np.array([ env.constants["site_space"], 0, 0]))
            s7     = self.center + np.dot(rotation, np.array([0, env.constants["fork_teeth_length"], 0]) + np.array([-env.constants["site_space"], 0, 0]))
        elif self.mode == 'D':
            self.A = self.center + np.dot(rotation, [ self.opening/2, s                , 0])
            self.B = self.center + np.dot(rotation, [-self.opening/2, s                , 0])
            self.C = self.center + np.dot(rotation, [ 0.0           , self.stick_length, 0])
            self.D = self.center + np.dot(rotation, [ 0.0           , 0                , 0])

            # FORK END
            s0     = self.center + np.dot(rotation, np.array([0, 0, 0]) + np.array([               0, 0, env.constants["site_space"]]))
            s1     = self.center + np.dot(rotation, np.array([0, 0, 0]) + np.array([               0, 0, -env.constants["site_space"]]))
            s2     = self.center + np.dot(rotation, np.array([0, 0, 0]) + np.array([ env.constants["site_space"], 0, 0]))
            s3     = self.center + np.dot(rotation, np.array([0, 0, 0]) + np.array([-env.constants["site_space"], 0, 0]))
            # FORK MIDDLE
            s4     = self.center + np.dot(rotation, np.array([0, self.stick_length, 0]) + np.array([0, 0, env.constants["site_space"]]))
            s5     = self.center + np.dot(rotation, np.array([0, self.stick_length, 0]) + np.array([0, 0, -env.constants["site_space"]]))
            s6     = self.center + np.dot(rotation, np.array([0, self.stick_length, 0]) + np.array([ env.constants["site_space"], 0, 0]))
            s7     = self.center + np.dot(rotation, np.array([0, self.stick_length, 0]) + np.array([-env.constants["site_space"], 0, 0]))
        
        self.E = self.C + self.A - (self.A + self.B)/2
        self.F = self.C - self.A + (self.A + self.B)/2
        
        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.A[0]} {self.A[1]} {self.A[2]} {self.E[0]} {self.E[1]} {self.E[2]}')
        self.parent.appendChild(beam)
        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.E[0]} {self.E[1]} {self.E[2]} {self.C[0]} {self.C[1]} {self.C[2]}')
        self.parent.appendChild(beam)
        
        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.B[0]} {self.B[1]} {self.B[2]} {self.F[0]} {self.F[1]} {self.F[2]}')
        self.parent.appendChild(beam)
        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.F[0]} {self.F[1]} {self.F[2]} {self.C[0]} {self.C[1]} {self.C[2]}')
        self.parent.appendChild(beam)
        
        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.D[0]} {self.D[1]} {self.D[2]} {self.C[0]} {self.C[1]} {self.C[2]}')
        self.parent.appendChild(beam)

        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_A')
        site.setAttribute('pos', f'{self.A[0]} {self.A[1]} {self.A[2]}')
        self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_B')
        site.setAttribute('pos', f'{self.B[0]} {self.B[1]} {self.B[2]}')
        self.parent.appendChild(site)

        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_0')
        site.setAttribute('pos', f'{s0[0]} {s0[1]} {s0[2]}')
        if self.vias[0]: self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_1')
        site.setAttribute('pos', f'{s1[0]} {s1[1]} {s1[2]}')
        if self.vias[1]: self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_2')
        site.setAttribute('pos', f'{s2[0]} {s2[1]} {s2[2]}')
        if self.vias[2]: self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_3')
        site.setAttribute('pos', f'{s3[0]} {s3[1]} {s3[2]}')
        if self.vias[3]: self.parent.appendChild(site)

        #QUAD FORK MIDDLE
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_4')
        site.setAttribute('pos', f'{s4[0]} {s4[1]} {s4[2]}')
        if self.vias[4]: self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_5')
        site.setAttribute('pos', f'{s5[0]} {s5[1]} {s5[2]}')
        if self.vias[5]: self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_6')
        site.setAttribute('pos', f'{s6[0]} {s6[1]} {s6[2]}')
        if self.vias[6]: self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_7')
        site.setAttribute('pos', f'{s7[0]} {s7[1]} {s7[2]}')
        if self.vias[7]: self.parent.appendChild(site)

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
                            
        self.A = self.center
        self.B = self.center + np.dot(rotation, env.constants["star_teeth_length"] * np.array([0, np.cos(angle_opening),  np.sin(angle_opening)]))
        self.C = self.center + np.dot(rotation, env.constants["star_teeth_length"] * np.array([0, np.cos(angle_opening), -np.sin(angle_opening)]))
        self.D = self.center + np.dot(rotation, env.constants["star_teeth_length"] * np.array([0, 1                    ,  0                    ]))
        
        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.A[0]} {self.A[1]} {self.A[2]} {self.B[0]} {self.B[1]} {self.B[2]}')
        self.parent.appendChild(beam)

        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.A[0]} {self.A[1]} {self.A[2]} {self.C[0]} {self.C[1]} {self.C[2]}')
        self.parent.appendChild(beam)

        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.A[0]} {self.A[1]} {self.A[2]} {self.D[0]} {self.D[1]} {self.D[2]}')
        self.parent.appendChild(beam)

        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_B')
        site.setAttribute('pos', f'{self.B[0]} {self.B[1]} {self.B[2]}')
        self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_C')
        site.setAttribute('pos', f'{self.C[0]} {self.C[1]} {self.C[2]}')
        self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_D')
        site.setAttribute('pos', f'{self.D[0]} {self.D[1]} {self.D[2]}')
        self.parent.appendChild(site)

        s0 = (self.A + self.B) / 2
        s1 = (self.A + self.C) / 2
        s2 = (self.A + self.D) / 2
        s3 = self.A + np.array([ env.constants["site_space"], 0, 0])
        s4 = self.A + np.array([-env.constants["site_space"], 0, 0])
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_0')
        site.setAttribute('pos', f'{s0[0]} {s0[1]} {s0[2]}')
        self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_1')
        site.setAttribute('pos', f'{s1[0]} {s1[1]} {s1[2]}')
        self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_2')
        site.setAttribute('pos', f'{s2[0]} {s2[1]} {s2[2]}')
        self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_3')
        site.setAttribute('pos', f'{s3[0]} {s3[1]} {s3[2]}')
        self.parent.appendChild(site)
        site = env.root.createElement('site')
        site.setAttribute('name', self.name + '_4')
        site.setAttribute('pos', f'{s4[0]} {s4[1]} {s4[2]}')
        self.parent.appendChild(site)
        
        box = env.root.createElement('geom')
        box.setAttribute('type', 'box')
        box.setAttribute('mass', '0')
        box.setAttribute('rgba', '0 0 0 0')
        box.setAttribute('pos', f'{self.B[0]} {self.B[1]} {self.B[2]}')
        box.setAttribute('size', f'0.02 0.02 {2*env.constants["beam_radius"]}')
        box.setAttribute('euler', f'-60 0 0')
        self.parent.appendChild(box)
        box = env.root.createElement('geom')
        box.setAttribute('type', 'box')
        box.setAttribute('mass', '0')
        box.setAttribute('rgba', '0 0 0 0')
        box.setAttribute('pos', f'{self.C[0]} {self.C[1]} {self.C[2]}')
        box.setAttribute('size', f'0.02 0.02 {2*env.constants["beam_radius"]}')
        box.setAttribute('euler', f'60 0 0')
        self.parent.appendChild(box)
        box = env.root.createElement('geom')
        box.setAttribute('type', 'box')
        box.setAttribute('mass', '0')
        box.setAttribute('rgba', '0 0 0 0')
        box.setAttribute('pos', f'{self.D[0]} {self.D[1]} {self.D[2]}')
        box.setAttribute('size', f'0.02 0.02 {2*env.constants["beam_radius"]}')
        box.setAttribute('euler', f'180 0 0')
        self.parent.appendChild(box)

# class Leg:
#     def __init__(self, name, parent, center, zangle):
#         self.name = name
#         self.parent = parent
#         self.center = center
#         self.zangle = zangle
#         self.create_leg()
    

#     def add_site(self, spatial, site_name):
#         site = env.root.createElement('site')
#         site.setAttribute('site', site_name)
#         spatial.appendChild(site)


#     def link_joint(self, forkA, forkB, star, type):
#         hinge_joint = env.root.createElement('joint')
#         hinge_joint.setAttribute('type', 'hinge')
#         hinge_joint.setAttribute('axis', '1 0 0')
#         hinge_joint.setAttribute('stiffness', f'{env.constants["hinge_stiffness"]/3}')
#         forkB.parent.appendChild(hinge_joint)

#         hinge_joint = env.root.createElement('joint')
#         hinge_joint.setAttribute('type', 'hinge')
#         hinge_joint.setAttribute('axis', '1 0 0')
#         hinge_joint.setAttribute('stiffness', f'{env.constants["hinge_stiffness"]*2/3}')
#         star.parent.appendChild(hinge_joint)

#     def muscle_joint(self):
#         def add_muscle(name, sites):
#             spatial = env.root.createElement('spatial')
#             env.tendon.appendChild(spatial)
#             spatial.setAttribute('limited', env.constants['muscle_tendon_limited'])
#             spatial.setAttribute('name', name)
#             spatial.setAttribute('range', env.constants['muscle_tendon_range'])
#             spatial.setAttribute('width', '0.001')
#             spatial.setAttribute('rgba', env.constants['muscle_tendon_rgba'])
#             spatial.setAttribute('stiffness', f'{env.constants["muscle_tendon_stiffness"]}')
#             spatial.setAttribute('damping', f'{env.constants["muscle_tendon_damping"]}')
            
#             muscle = env.root.createElement('muscle')
#             env.actuator.appendChild(muscle)
#             muscle.setAttribute('name', name)
#             muscle.setAttribute('tendon', name)
#             muscle.setAttribute('ctrllimited', 'false')
#             muscle.setAttribute('forcelimited', 'false')
#             muscle.setAttribute('lengthrange', env.constants['muscle_lengthrange'])
#             muscle.setAttribute('force', f'{env.constants["muscle_force"]}')
#             muscle.setAttribute('scale', f'{env.constants["muscle_scale"]}')
#             muscle.setAttribute('range', env.constants['muscle_range'])
            
#             #actuatorforce = env.root.createElement('actuatorfrc')
#             #env.sensor1.appendChild(actuatorforce)
#             #actuatorforce.setAttribute('name', name)
#             #actuatorforce.setAttribute('actuator', name)

#             #actuatorpos = env.root.createElement('actuatorpos')
#             #env.sensor2.appendChild(actuatorpos)
#             #actuatorpos.setAttribute('name', name + '_pos')
#             #actuatorpos.setAttribute('actuator', name)
            
#             for s in sites:
#                 self.add_site(spatial, s)

#         add_muscle(self.name + '_hip_flexor',   [self.scalupa.name + '_0',
#                                                  self.scalupa.name + '_4',
#                                                  self.hip.name + '_2',
#                                                  self.humerus_top.name + '_4'])
#         actuatorpos = env.root.createElement('actuatorpos')
#         env.sensor2.appendChild(actuatorpos)
#         actuatorpos.setAttribute('name', self.name + '_hip_flexor' + '_pos')
#         actuatorpos.setAttribute('actuator', self.name + '_hip_flexor')

#         actuatorfrc = env.root.createElement('actuatorfrc')
#         env.sensor2.appendChild(actuatorfrc)
#         actuatorfrc.setAttribute('name', self.name + '_hip_flexor' + '_frc')
#         actuatorfrc.setAttribute('actuator', self.name + '_hip_flexor')
        
#         add_muscle(self.name + '_hip_extensor', [self.scalupa.name + '_1',
#                                                  self.scalupa.name + '_5',
#                                                  self.hip.name + '_0',
#                                                  self.hip.name + '_1',
#                                                  self.humerus_top.name + '_5'])
        
#         add_muscle(self.name + '_knee_flexor', [self.scalupa.name + '_2',
#                                                 self.scalupa.name + '_6',
#                                                 self.hip.name + '_3',
#                                                 self.humerus_top.name + '_6',
#                                                 self.humerus_bot.name + '_5',
#                                                 self.knee.name + '_2',
#                                                 self.radius.name + '_5'])
#         add_muscle(self.name + '_knee_extensor', [self.scalupa.name + '_3',
#                                                   self.scalupa.name + '_7',
#                                                   self.hip.name + '_4',
#                                                   self.humerus_top.name + '_7',
#                                                   self.humerus_bot.name + '_4',
#                                                   self.knee.name + '_1',
#                                                   self.knee.name + '_0',
#                                                   self.radius.name + '_4'])
        

#     def create_leg(self):
#         self.scalupa = Fork(self.name + '_scalupa', self.parent, self.center, self.zangle, 'D', env.constants['scapula_length'], env.constants['scapula_angle'], env.constants['fork_opening_big'])
        
#         self.humerus_body = env.root.createElement('body')
#         humerus_origin = self.scalupa.getAB()
#         self.humerus_body.setAttribute('pos', str(humerus_origin)[1:-1].replace(',', ''))
#         self.humerus_body.setAttribute('euler', f'0 0 {self.zangle}')
#         self.parent.appendChild(self.humerus_body)
#         self.humerus_top = Fork(self.name + '_humerus_top', self.humerus_body, [0, 0, 0], 0              , 'AB', env.constants['humerus_length'] / 2, env.constants['humerus_angle'], env.constants['fork_opening_small'], vias=[False, False, False, False, True, True, True, True])
#         self.humerus_bot = Fork(self.name + '_humerus_bot', self.humerus_body, self.humerus_top.getD(), 0, 'D' , env.constants['humerus_length'] / 2, env.constants['humerus_angle'], env.constants['fork_opening_small'], vias=[False, False, False, False, True, True, False, False])

#         self.radius_body = env.root.createElement('body')
#         radius_origin = self.humerus_bot.getAB()
#         self.radius_body.setAttribute('pos', str(radius_origin)[1:-1].replace(',', ''))
#         self.humerus_body.appendChild(self.radius_body)
#         self.humerus_body.setAttribute('euler', f'0 0 {self.zangle}')
#         self.radius = Fork(self.name + '_radius', self.radius_body, [0, 0, 0], 0, 'AB', env.constants['radius_length'], env.constants['radius_angle'], env.constants['fork_opening_big'], vias=[False, False, False, False, True, True, False, False])


#         self.hip_body = env.root.createElement('body')
#         self.hip_body.setAttribute('pos', str(humerus_origin)[1:-1].replace(',', ''))
#         self.hip_body.setAttribute('euler', f'0 0 {self.zangle}')
#         self.hip  = Star(self.name + '_hip' , self.hip_body, [0, 0, 0], env.constants['hip_angle'])
#         self.parent.appendChild(self.hip_body)
        
#         self.knee_body = env.root.createElement('body')
#         self.knee_body.setAttribute('pos', str(radius_origin)[1:-1].replace(',', ''))
#         self.knee_body.setAttribute('euler', f'0 0 0')
#         self.knee = Star(self.name + '_knee', self.knee_body, [0, 0, 0], env.constants['knee_angle'])
#         self.humerus_body.appendChild(self.knee_body)

#         self.link_joint(self.scalupa, self.humerus_top, self.hip, 'A')
#         self.link_joint(self.humerus_bot, self.radius, self.knee, 'B')
#         self.muscle_joint()

def add_site(parent, pos, site_name):
    site = env.root.createElement('site')
    site.setAttribute('name', site_name)
    site.setAttribute('pos', f'{pos[0]} {pos[1]} {pos[2]}')
    parent.appendChild(site)

def add_muscle(name, sites):
    spatial = env.root.createElement('spatial')
    env.tendon.appendChild(spatial)
    spatial.setAttribute('limited', env.constants['muscle_tendon_limited'])
    spatial.setAttribute('name', name)
    spatial.setAttribute('range', env.constants['muscle_tendon_range'])
    spatial.setAttribute('width', '0.001')
    spatial.setAttribute('rgba', env.constants['muscle_tendon_rgba'])
    spatial.setAttribute('stiffness', f'{env.constants["muscle_tendon_stiffness"]}')
    spatial.setAttribute('damping', f'{env.constants["muscle_tendon_damping"]}')
    
    muscle = env.root.createElement('muscle')
    env.actuator.appendChild(muscle)
    muscle.setAttribute('name', name)
    muscle.setAttribute('tendon', name)
    muscle.setAttribute('ctrllimited', 'false')
    muscle.setAttribute('forcelimited', 'false')
    muscle.setAttribute('lengthrange', env.constants['muscle_lengthrange'])
    muscle.setAttribute('force', f'{env.constants["muscle_force"]}')
    muscle.setAttribute('scale', f'{env.constants["muscle_scale"]}')
    muscle.setAttribute('range', env.constants['muscle_range'])
    
    actuatorforce = env.root.createElement('actuatorfrc')
    env.sensor1.appendChild(actuatorforce)
    actuatorforce.setAttribute('name', name)
    actuatorforce.setAttribute('actuator', name)

    #actuatorpos = env.root.createElement('actuatorpos')
    #env.sensor2.appendChild(actuatorpos)
    #actuatorpos.setAttribute('name', name + '_pos')
    #actuatorpos.setAttribute('actuator', name)
    def add_siteM(spatial, site_name):
        site = env.root.createElement('site')
        site.setAttribute('site', site_name)
        spatial.appendChild(site)
    
    for s in sites:
        add_siteM(spatial, s)

    
class Joint:
    def __init__(self, name, parent, center, length, muscle_A, muscle_B, angle, shape):
        self.name = name
        self.parent = parent
        self.center = center
        self.angle = angle

        if shape == 'arrow':
            parent_rotation = np.array([[1,  0,  0],
                                      [0,  1,  0],
                                      [0,  0,  1]])
        elif shape == 'fork':
            parent_rotation = np.array([[1,  0,  0],
                                      [0, -1,  0],
                                      [0,  0, -1]])
        child_rotation = np.array([[1,              0,             0],
                                   [0,  np.cos(angle), np.sin(angle)],
                                   [0, -np.sin(angle), np.cos(angle)]])
        
        #   A         
        #     \         E
        #S2    C -- D   S2     G S1   H
        #     /         F
        #   B
        a = env.constants["a"]
        b = env.constants["b"]
        c = env.constants["c"]

        self.A = center + np.dot(parent_rotation, [0, a*np.cos(2*np.pi/3),  a*np.sin(2*np.pi/3)])
        self.B = center + np.dot(parent_rotation, [0, a*np.cos(-2*np.pi/3), a*np.sin(-2*np.pi/3)])
        self.C = center + np.dot(parent_rotation, [0, 0, 0])
        self.D = center + np.dot(parent_rotation, [0, a, 0])
        self.E = np.dot(parent_rotation, [ b, 0, 0])
        self.F = np.dot(parent_rotation, [-b, 0, 0])
        self.G = np.dot(parent_rotation, [0, c, 0])
        self.H = np.dot(parent_rotation, [0, length-c, 0])
        self.S1 = np.dot(parent_rotation, [0, muscle_A, 0])
        self.S2 = center + np.array([0, -muscle_B, 0])


        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.C[0]} {self.C[1]} {self.C[2]} {self.A[0]} {self.A[1]} {self.A[2]}')
        self.parent.appendChild(beam)

        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.C[0]} {self.C[1]} {self.C[2]} {self.B[0]} {self.B[1]} {self.B[2]}')
        self.parent.appendChild(beam)

        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.C[0]} {self.C[1]} {self.C[2]} {self.D[0]} {self.D[1]} {self.D[2]}')
        self.parent.appendChild(beam)


        self.child = env.root.createElement('body')
        self.child.setAttribute('pos', f'{center[0]} {center[1]} {center[2]}')
        self.parent.appendChild(self.child)
        free_joint = env.root.createElement('joint')
        free_joint.setAttribute('type', 'hinge')
        free_joint.setAttribute('axis', '1 0 0')
        self.child.setAttribute('euler', f'{np.rad2deg(-angle)} 0 0')
        free_joint.setAttribute('stiffness', f'{env.constants["hinge_stiffness"]}')
        free_joint.setAttribute('damping', '0.1')
        self.child.appendChild(free_joint)


        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.G[0]} {self.G[1]} {self.G[2]} {self.E[0]} {self.E[1]} {self.E[2]}')
        self.child.appendChild(beam)

        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.G[0]} {self.G[1]} {self.G[2]} {self.F[0]} {self.F[1]} {self.F[2]}')
        self.child.appendChild(beam)

        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.G[0]} {self.G[1]} {self.G[2]} {self.H[0]} {self.H[1]} {self.H[2]}')
        self.child.appendChild(beam)

        add_site(self.child, [self.S1[0], self.S1[1], self.S1[2]], self.name + '_0')
        add_site(self.parent, [self.S2[0], self.S2[1], self.S2[2]], self.name + '_1')
        add_muscle(self.name + '_hip_flexor', [self.name + '_0', self.name + '_1'])

class Leg:
    def __init__(self, parent, name, center, orientation):
        if orientation == "rear":
            j1 = Joint(name + 'j1', parent, center, 0.3-env.constants["a"], 0.1, 0.4, np.deg2rad(120), 'arrow')
            j2 = Joint(name + 'j2', j1.child, np.array([0, 0.3-env.constants["c"], 0]), 0.3, 0.2, 0.1, np.deg2rad(120), 'fork')
        elif orientation == "front":
            j1 = Joint(name + 'j1', parent, center, 0.3-env.constants["a"], 0.1, -0.1, np.deg2rad(-120), 'fork')
            j2 = Joint(name + 'j2', j1.child, np.array([0, -0.3+env.constants["c"], 0]), 0.3, 0.1, -0.1, np.deg2rad(-120), 'arrow')

class Quadruped:
    def __init__(self, name, center):
        self.name = name
        
        robot = env.root.createElement('body')
        robot.setAttribute('pos', '0 0 0')
        env.worldbody.appendChild(robot)
        free_joint = env.root.createElement('joint')
        free_joint.setAttribute('type', 'free')
        robot.appendChild(free_joint)

        hw = env.constants["body_width"]/2
        hl = env.constants["body_length"]/2

        legRL = Leg(robot, self.name + 'rl', center + np.array([ hw,  hl, 0]), "rear")
        legFL = Leg(robot, self.name + 'fl', center + np.array([ hw,  -hl, 0]), "front")
        legRR = Leg(robot, self.name + 'rr', center + np.array([-hw,  hl, 0]), "rear")
        legFR = Leg(robot, self.name + 'fr', center + np.array([-hw,  -hl, 0]), "front")
        
        box = env.root.createElement('geom')
        box.setAttribute('type', 'box')
        box.setAttribute('mass', f'{env.constants["core_mass"]}')
        box.setAttribute('rgba', '0.3 0.3 0.3 0.5')
        box_center = center + np.array([0, -0.15/2*np.cos(120), 0.0])
        box.setAttribute('pos', f'0 {box_center[1]} 0')
        box.setAttribute('size', f'{hw} {hl} {env.constants["beam_radius"]}')
        robot.appendChild(box)