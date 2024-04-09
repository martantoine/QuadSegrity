class Env:
    constants = {}

    def __init__(self, root):
        # MAIN XML
        self.root = root
        self.xml = self.root.createElement('mujoco')  
        self.root.appendChild(self.xml)

    def init(self):
        # SENSOR
        self.sensor1 = self.root.createElement('sensor')
        self.xml.appendChild(self.sensor1)
        self.sensor2 = self.root.createElement('sensor')
        self.xml.appendChild(self.sensor2)

        # ACTUATOR
        self.actuator = self.root.createElement('actuator')
        self.xml.appendChild(self.actuator)

        # TENDON
        self.tendon = self.root.createElement('tendon')
        self.xml.appendChild(self.tendon)

        # CAMERA
        statistic = self.root.createElement('statistic')
        self.xml.appendChild(statistic)
        statistic.setAttribute('extent', '0.4')
        statistic.setAttribute('center', '0 0 -0.1')

        visual = self.root.createElement('visual')
        self.xml.appendChild(visual)
        visual_global = self.root.createElement('global')
        visual_global.setAttribute('azimuth', '150')
        visual_global.setAttribute('elevation', '-30')
        visual.appendChild(visual_global)

        headlight = self.root.createElement('headlight')
        headlight.setAttribute('ambient', '0.3 0.3 0.3')
        visual.appendChild(headlight)

        rgba = self.root.createElement('rgba')
        rgba.setAttribute('haze', '1 1 1 1')
        visual.appendChild(rgba)


        # OPTION
        option = self.root.createElement('option')
        self.xml.appendChild(option) 
        option.setAttribute('timestep', f'{self.constants["timestep"]}')
        option.setAttribute('iterations', '50')
        option.setAttribute('integrator', self.constants["integrator"])
        option.setAttribute('tolerance', '1e-10')
        option.setAttribute('viscosity', f'{self.constants["viscosity"]}')
        option.setAttribute('density', f'{self.constants["air_density"]}')
        
        # DEFAULT
        default = self.root.createElement('default') 
        joint = self.root.createElement('joint')
        joint.setAttribute('type', 'ball')
        default.appendChild(joint)

        muscle = self.root.createElement('muscle')
        muscle.setAttribute('ctrllimited', 'true')
        muscle.setAttribute('ctrlrange', '-1000 1000')
        default.appendChild(muscle)

        geom = self.root.createElement('geom')
        geom.setAttribute('size', f'{self.constants["beam_radius"]}')
        geom.setAttribute('density', f'{self.constants["geom_density"]}')
        geom.setAttribute('rgba', self.constants["geom_rgba"])
        default.appendChild(geom)

        site = self.root.createElement('site')
        site.setAttribute('size', f'{self.constants["site_radius"]}')
        site.setAttribute('rgba', '0.1 0.4 0.1 1')
        default.appendChild(site)

        #tendon2 = self.root.createElement('tendon')
        #tendon2.setAttribute('rgba', '0 1 0 1')
        #tendon2.setAttribute('stiffness', '100')
        #tendon2.setAttribute('damping', '1')
        #default.appendChild(tendon2)
        self.xml.appendChild(default)

        # ASSET         
        asset = self.root.createElement('asset')
        self.xml.appendChild(asset)
        texture = self.root.createElement('texture')
        texture.setAttribute('name', 'texplane')
        texture.setAttribute('type', '2d')
        texture.setAttribute('builtin', 'checker')
        texture.setAttribute('rgb1', '.25 .25 .25')
        texture.setAttribute('rgb2', '.28 .28 .28')
        texture.setAttribute('width', '512')
        texture.setAttribute('height', '512')
        texture.setAttribute('markrgb', '.8 .8 .8')
        asset.appendChild(texture)

        texture = self.root.createElement('texture')
        texture.setAttribute('name', 'skybox')
        texture.setAttribute('type', 'skybox')
        texture.setAttribute('builtin', 'gradient')
        texture.setAttribute('rgb1', '1 1 1')
        texture.setAttribute('rgb2', '1 1 1')
        texture.setAttribute('width', '800')
        texture.setAttribute('height', '800')
        texture.setAttribute('mark', 'none')
        texture.setAttribute('markrgb', '1 1 1')
        asset.appendChild(texture)

        material = self.root.createElement('material')
        material.setAttribute('name', 'matplane')
        material.setAttribute('reflectance', '0.1')
        material.setAttribute('texture', 'texplane')
        material.setAttribute('texrepeat', '1 1')
        material.setAttribute('texuniform', 'true')
        asset.appendChild(material)

        # WORLDBODY
        self.worldbody = self.root.createElement('worldbody')
        self.xml.appendChild(self.worldbody)
        geom = self.root.createElement('geom')
        geom.setAttribute('name', 'floor')
        geom.setAttribute('rgba', '1 1 1 1')
        geom.setAttribute('pos', '0 0 -0.7')
        geom.setAttribute('size', '0 0 1')
        geom.setAttribute('type', 'plane')
        geom.setAttribute('material', 'matplane')
        self.worldbody.appendChild(geom)


        light = self.root.createElement('light')
        light.setAttribute('directional', 'true')
        light.setAttribute('diffuse', '.8 .8 .8')
        light.setAttribute('specular', '.2 .2 .2')
        light.setAttribute('pos', '0 0 5')
        light.setAttribute('dir', '0 0 -1')
        self.worldbody.appendChild(light)