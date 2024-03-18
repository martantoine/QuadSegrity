import numpy as np

env = None

class Fork:
    def __init__(self, name, parent, center, mode, stick_length, angle_y, angle_opening, free=True, vias=[True, True, True, True, True, True, True, True]):
        self.name = name
        self.parent = parent
        self.center = center
        self.mode = mode
        self.stick_length = stick_length
        self.angle_y = angle_y
        self.angle_opening = angle_opening
        self.free = free
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
        angle_opening = np.deg2rad(self.angle_opening)
        rotation = np.array([[1, 0, 0],
                             [0, np.cos(angle_y), -np.sin(angle_y)],
                             [0, np.sin(angle_y), np.cos(angle_y)]])
        s = np.cos(angle_opening) * env.constants["teeth_length"] + self.stick_length

        if self.mode == 'AB':
            self.A = self.center + np.dot(rotation, [ np.sin(angle_opening) * env.constants["teeth_length"], 0                                        , 0])
            self.B = self.center + np.dot(rotation, [-np.sin(angle_opening) * env.constants["teeth_length"], 0                                        , 0])
            self.C = self.center + np.dot(rotation, [ 0.0                                      , np.cos(angle_opening) * env.constants["teeth_length"], 0])
            self.D = self.center + np.dot(rotation, [ 0.0                                      , s                                        , 0])

            # FORK END
            s0     = self.center + np.dot(rotation, np.array([0, s, 0]) + np.array([ 0              , 0, env.constants["site_space"]]))
            s1     = self.center + np.dot(rotation, np.array([0, s, 0]) + np.array([ 0              , 0, -env.constants["site_space"]]))
            s2     = self.center + np.dot(rotation, np.array([0, s, 0]) + np.array([ env.constants["site_space"], 0, 0]))
            s3     = self.center + np.dot(rotation, np.array([0, s, 0]) + np.array([-env.constants["site_space"], 0, 0]))
            # FORK MIDDLE
            s4     = self.center + np.dot(rotation, np.array([0, np.cos(angle_opening) * env.constants["teeth_length"], 0]) + np.array([ 0              , 0, env.constants["site_space"]]))
            s5     = self.center + np.dot(rotation, np.array([0, np.cos(angle_opening) * env.constants["teeth_length"], 0]) + np.array([ 0              , 0, -env.constants["site_space"]]))
            s6     = self.center + np.dot(rotation, np.array([0, np.cos(angle_opening) * env.constants["teeth_length"], 0]) + np.array([ env.constants["site_space"], 0, 0]))
            s7     = self.center + np.dot(rotation, np.array([0, np.cos(angle_opening) * env.constants["teeth_length"], 0]) + np.array([-env.constants["site_space"], 0, 0]))
        elif self.mode == 'D':
            self.A = self.center + np.dot(rotation, [ np.sin(angle_opening) * env.constants["teeth_length"] , s                , 0])
            self.B = self.center + np.dot(rotation, [-np.sin(angle_opening) * env.constants["teeth_length"] , s                , 0])
            self.C = self.center + np.dot(rotation, [ 0.0                                       , self.stick_length, 0])
            self.D = self.center + np.dot(rotation, [ 0.0                                       , 0                , 0])

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
        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.A[0]} {self.A[1]} {self.A[2]} {self.C[0]} {self.C[1]} {self.C[2]}')
        self.parent.appendChild(beam)
        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.B[0]} {self.B[1]} {self.B[2]} {self.C[0]} {self.C[1]} {self.C[2]}')
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

        if self.free:
            free_joint = env.root.createElement('joint')
            free_joint.setAttribute('type', 'free')
            self.parent.appendChild(free_joint)

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
        self.B = self.center + np.dot(rotation, env.constants["teeth_length"] * np.array([0, np.cos(angle_opening),  np.sin(angle_opening)]))
        self.C = self.center + np.dot(rotation, env.constants["teeth_length"] * np.array([0, np.cos(angle_opening), -np.sin(angle_opening)]))
        self.D = self.center + np.dot(rotation, env.constants["teeth_length"] * np.array([0, 1                    ,  0                    ]))
        
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
        

        free_joint = env.root.createElement('joint')
        free_joint.setAttribute('type', 'free')
        self.parent.appendChild(free_joint)

class Leg:
    def __init__(self, name, center):
        self.name = name
        self.center = center
        self.create_leg()
    
    def add_site(self, spatial, site_name):
        site = env.root.createElement('site')
        site.setAttribute('site', site_name)
        spatial.appendChild(site)


    def link_joint(self, forkA, forkB, star):
        def link(site0, site1, i):
            
            spatial = env.root.createElement('spatial')
            spatial.setAttribute('limited', 'true')
            spatial.setAttribute('name', star.name + '_' + str(i))
            spatial.setAttribute('range', '-0.01 0.01')
            spatial.setAttribute('width', '0.001')
            env.tendon.appendChild(spatial)
            
            self.add_site(spatial, site0)
            self.add_site(spatial, site1)
            return i + 1
        
        i = 0
        i = link(forkA.name + '_A', star.name + '_B', i)
        i = link(forkA.name + '_B', star.name + '_B', i)
        i = link(forkA.name + '_A', star.name + '_C', i)
        i = link(forkA.name + '_B', star.name + '_C', i)
        i = link(forkA.name + '_A', star.name + '_D', i)
        i = link(forkA.name + '_B', star.name + '_D', i)

        i = link(forkB.name + '_A', star.name + '_B', i)
        i = link(forkB.name + '_B', star.name + '_B', i)
        i = link(forkB.name + '_A', star.name + '_C', i)
        i = link(forkB.name + '_B', star.name + '_C', i)
        i = link(forkB.name + '_A', star.name + '_D', i)
        i = link(forkB.name + '_B', star.name + '_D', i)

        i = link(forkA.name + '_B', forkB.name + '_B', i)
        i = link(forkA.name + '_A', forkB.name + '_A', i)


    def create_leg(self):
        self.scalupa     = Fork(self.name + '_scalupa'    , env.worldbody      , self.center            , 'D' , 0.1, 225, 45, free=False)
        
        self.humerus_body = env.root.createElement('body')
        humerus_origin = self.scalupa.getAB()
        self.humerus_body.setAttribute('pos', str(humerus_origin)[1:-1].replace(',', ''))
        env.worldbody.appendChild(self.humerus_body)
        self.humerus_top = Fork(self.name + '_humerus_top', self.humerus_body, np.array([0, 0, 0])   , 'AB', 0.1, -45, 28, vias=[False, False, False, False, True, True, True, True])
        self.humerus_bot = Fork(self.name + '_humerus_bot', self.humerus_body, self.humerus_top.getD(), 'D' , 0.1, -45, 28, free=False, vias=[False, False, False, False, True, True, False, False])

        self.radius_body = env.root.createElement('body')
        radius_origin = humerus_origin + self.humerus_bot.getAB()
        self.radius_body.setAttribute('pos', str(radius_origin)[1:-1].replace(',', ''))
        env.worldbody.appendChild(self.radius_body)
        self.radius      = Fork(self.name + '_radius', self.radius_body, np.array([0, 0, 0]), 'AB' , 0.15, 225, 45, vias=[False, False, False, False, True, True, False, False])

        self.hip_body = env.root.createElement('body')
        self.hip_body.setAttribute('pos', str(humerus_origin)[1:-1].replace(',', ''))
        self.hip  = Star(self.name + '_hip' , self.hip_body, np.array([0, 0, 0]), 0)
        env.worldbody.appendChild(self.hip_body)
        
        self.knee_body = env.root.createElement('body')
        self.knee_body.setAttribute('pos', str(radius_origin)[1:-1].replace(',', ''))
        self.knee = Star(self.name + '_knee', self.knee_body, np.array([0, 0, 0]), 180)
        env.worldbody.appendChild(self.knee_body)

        self.link_joint(self.scalupa, self.humerus_top, self.hip)
        self.link_joint(self.radius , self.humerus_bot, self.knee)


        spatial = env.root.createElement('spatial')
        spatial.setAttribute('limited', 'true')
        spatial.setAttribute('name', self.name + '_hip_flexor')
        spatial.setAttribute('range', '-0.01 0.01')
        spatial.setAttribute('width', '0.001')
        env.tendon.appendChild(spatial)
        self.add_site(spatial, self.scalupa.name + '_0')
        self.add_site(spatial, self.scalupa.name + '_4')
        self.add_site(spatial, self.hip.name + '_2')
        self.add_site(spatial, self.humerus_top.name + '_4')

        spatial = env.root.createElement('spatial')
        spatial.setAttribute('limited', 'true')
        spatial.setAttribute('name', self.name + '_hip_extensor')
        spatial.setAttribute('range', '-0.01 0.01')
        spatial.setAttribute('width', '0.001')
        env.tendon.appendChild(spatial)
        self.add_site(spatial, self.scalupa.name + '_1')
        self.add_site(spatial, self.scalupa.name + '_5')
        self.add_site(spatial, self.hip.name + '_0')
        self.add_site(spatial, self.hip.name + '_1')
        self.add_site(spatial, self.humerus_top.name + '_5')

        spatial = env.root.createElement('spatial')
        spatial.setAttribute('limited', 'true')
        spatial.setAttribute('name', self.name + '_knee_flexor')
        spatial.setAttribute('range', '-0.01 0.01')
        spatial.setAttribute('width', '0.001')
        env.tendon.appendChild(spatial)
        self.add_site(spatial, self.scalupa.name + '_2')
        self.add_site(spatial, self.scalupa.name + '_6')
        self.add_site(spatial, self.hip.name + '_3')
        self.add_site(spatial, self.humerus_top.name + '_6')
        self.add_site(spatial, self.humerus_bot.name + '_5')
        self.add_site(spatial, self.knee.name + '_2')
        self.add_site(spatial, self.radius.name + '_5')

        spatial = env.root.createElement('spatial')
        spatial.setAttribute('limited', 'true')
        spatial.setAttribute('name', self.name + '_knee_extensor')
        spatial.setAttribute('range', '-0.01 0.01')
        spatial.setAttribute('width', '0.001')
        env.tendon.appendChild(spatial)
        self.add_site(spatial, self.scalupa.name + '_3')
        self.add_site(spatial, self.scalupa.name + '_7')
        self.add_site(spatial, self.hip.name + '_4')
        self.add_site(spatial, self.humerus_top.name + '_7')
        self.add_site(spatial, self.humerus_bot.name + '_4')
        self.add_site(spatial, self.knee.name + '_1')
        self.add_site(spatial, self.knee.name + '_0')
        self.add_site(spatial, self.radius.name + '_4')