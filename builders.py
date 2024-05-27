import numpy as np

env = None

def add_site(parent, pos, site_name, zaxis=[0, 0, 1]):
    site = env.root.createElement('site')
    site.setAttribute('name', site_name)
    site.setAttribute('pos', f'{pos[0]} {pos[1]} {pos[2]}')
    site.setAttribute('zaxis', f'{zaxis[0]} {zaxis[1]} {zaxis[2]}')
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
    def __init__(self, name, parent, center, length, muscle_A, muscle_B, angle, connect_to):
        self.name = name
        self.parent = parent
        self.center = center
        self.angle = angle

        if connect_to == 'star':
            parent_rotation = np.array([[1,  0,  0],
                                      [0,  1,  0],
                                      [0,  0,  1]])
        elif connect_to == 'losange':
            parent_rotation = np.array([[1,  0,  0],
                                      [0, -1,  0],
                                      [0,  0, -1]])
        
        #   A         
        #     \         E
        #S2    C -- D   S2     G S1   H
        #     /         F
        #   B
        star_length = env.constants["star_length"]
        losange_spacing = env.constants["losange_spacing"]
        losange_length  = env.constants["losange_length"]

        # Star
        self.A = center + np.dot(parent_rotation, [0, star_length*np.cos(2*np.pi/3),  star_length*np.sin(2*np.pi/3)])
        self.B = center + np.dot(parent_rotation, [0, star_length*np.cos(-2*np.pi/3), star_length*np.sin(-2*np.pi/3)])
        self.C = center + np.dot(parent_rotation, [0, 0, 0])
        self.D = center + np.dot(parent_rotation, [0, star_length, 0])
     
        # Losange
        self.E = np.dot(parent_rotation, [ losange_spacing, 0, 0])
        self.F = np.dot(parent_rotation, [-losange_spacing, 0, 0])
        self.G = np.dot(parent_rotation, [0,  losange_length, 0])
        self.I = np.dot(parent_rotation, [0, -losange_length, 0])

        # Limb
        self.H = np.dot(parent_rotation, [0, length-losange_length, 0])
        
        # Sites
        self.S1 = np.dot(parent_rotation, [0, -muscle_B, 0])
        self.S2 = center + np.array([0, -muscle_A, 0])


        # Star
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

        # Losange
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

        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.E[0]} {self.E[1]} {self.E[2]} {self.I[0]} {self.I[1]} {self.I[2]}')
        self.child.appendChild(beam)
        
        beam = env.root.createElement('geom')
        beam.setAttribute('type', 'capsule')
        beam.setAttribute('fromto', f'{self.F[0]} {self.F[1]} {self.F[2]} {self.I[0]} {self.I[1]} {self.I[2]}')
        self.child.appendChild(beam)
        

        add_site(self.child, [self.S1[0], self.S1[1], self.S1[2]], self.name + '_0')
        add_site(self.parent, [self.S2[0], self.S2[1], self.S2[2]], self.name + '_1')
        add_muscle(self.name + '_hip_flexor', [self.name + '_0', self.name + '_1'])

class Leg:
    def __init__(self, parent, name, center, orientation, limb_length=0.3):
        muscle_A1 = 0.4
        muscle_A2 = limb_length
        if orientation == "rear":
            j1 = Joint(name + 'j1', parent, center,
                       limb_length, muscle_A1, -env.constants["losange_length"],
                       np.deg2rad(120), 'star')
            j2_center = np.array([0, limb_length-env.constants["losange_length"], 0])
            j2 = Joint(name + 'j2', j1.child, j2_center,
                       limb_length, muscle_A2, -env.constants["losange_length"],
                       np.deg2rad(120), 'losange')
        elif orientation == "front":
            j1 = Joint(name + 'j1', parent, center,
                       limb_length, -muscle_A1, env.constants["losange_length"],
                       np.deg2rad(120), 'star')
            j2_center = np.array([0, limb_length-env.constants["losange_length"], 0])
            j2 = Joint(name + 'j2', j1.child, j2_center,
                       limb_length, muscle_A2, -env.constants["losange_length"],
                       np.deg2rad(120), 'losange')

class Quadruped:
    def __init__(self, name, center):
        self.name = name
        
        robot = env.root.createElement('body')
        robot.setAttribute('pos', '0 0 0')
        env.worldbody.appendChild(robot)
        free_joint = env.root.createElement('joint')
        free_joint.setAttribute('type', 'free')
        robot.appendChild(free_joint)

        add_site(robot, [0, 0, 0], name + '_sensors', zaxis=[0, 0, -1])

        gyro = env.root.createElement('gyro')
        env.sensor1.appendChild(gyro)
        gyro.setAttribute('name', name + '_gyro')
        gyro.setAttribute('site', name + '_sensors')

        rangefinder = env.root.createElement('rangefinder')
        env.sensor1.appendChild(rangefinder)
        rangefinder.setAttribute('name', name + '_rangefinder')
        rangefinder.setAttribute('site', name + '_sensors')
        
        hw = env.constants["body_width"]/2
        hl = env.constants["body_length"]/2

        legRL = Leg(robot, self.name + 'rl', center + np.array([ hw,  hl, 0]), "rear", 0.3)
        legFL = Leg(robot, self.name + 'fl', center + np.array([ hw,  -hl, 0]), "front", 0.3)
        legRR = Leg(robot, self.name + 'rr', center + np.array([-hw,  hl, 0]), "rear", 0.3)
        legFR = Leg(robot, self.name + 'fr', center + np.array([-hw,  -hl, 0]), "front", 0.3)
        
        box = env.root.createElement('geom')
        box.setAttribute('type', 'box')
        box.setAttribute('mass', f'{env.constants["core_mass"]}')
        box.setAttribute('rgba', '0.3 0.3 0.3 0.5')
        box_center = center + np.array([0, -0.15/2*np.cos(120), 0.0])
        #box.setAttribute('pos', f'0 {box_center[1]} 0')
        box.setAttribute('size', f'{hw} {hl} {env.constants["beam_radius"]}')
        robot.appendChild(box)