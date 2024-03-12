from xml.dom import minidom 
import os  
  
  
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
geom.setAttribute('size', '0.003')
geom.setAttribute('mass', '0.1')
geom.setAttribute('rgba', '.5 .1 .1 1')
default.appendChild(geom)

site = root.createElement('site')
site.setAttribute('size', '0.005')
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

xml_str = root.toprettyxml(indent ="\t")  
  
save_path_file = "leg_parametric.xml"
  
with open(save_path_file, "w") as f: 
    f.write(xml_str)  