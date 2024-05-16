import dearpygui.dearpygui as dpg
import numpy as np
import math

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

width = 5
length = 10
height = 2

verticies = [
        [-length, -width, -height],  # 0 near side
        [ length, -width, -height],  # 1
        [-length,  width, -height],  # 2
        [ length,  width, -height],  # 3
        [-length, -width,  height],  # 4 far side
        [ length, -width,  height],  # 5
        [-length,  width,  height],  # 6
        [ length,  width,  height],  # 7
        [-length, -width, -height],  # 8 left side
        [-length,  width, -height],  # 9
        [-length, -width,  height],  # 10
        [-length,  width,  height],  # 11
        [ length, -width, -height],  # 12 right side
        [ length,  width, -height],  # 13
        [ length, -width,  height],  # 14
        [ length,  width,  height],  # 15
        [-length, -width, -height],  # 16 bottom side
        [ length, -width, -height],  # 17
        [-length, -width,  height],  # 18
        [ length, -width,  height],  # 19
        [-length,  width, -height],  # 20 top side
        [ length,  width, -height],  # 21
        [-length,  width,  height],  # 22
        [ length,  width,  height],  # 23
    ]


colors = [[150, 150, 150, 255]] * int(len(verticies)/2)

with dpg.window(label="tutorial", width=550, height=550):

    with dpg.drawlist(width=500, height=500):

        with dpg.draw_layer(tag="main pass", depth_clipping=True, perspective_divide=True, cull_mode=dpg.mvCullMode_Back):

            with dpg.draw_node(tag="cube"):

                dpg.draw_triangle(verticies[1],  verticies[2],  verticies[0], color=[0,0,0.0],  fill=colors[0])
                dpg.draw_triangle(verticies[1],  verticies[3],  verticies[2], color=[0,0,0.0],  fill=colors[1])
                dpg.draw_triangle(verticies[7],  verticies[5],  verticies[4], color=[0,0,0.0],  fill=colors[2])
                dpg.draw_triangle(verticies[6],  verticies[7],  verticies[4], color=[0,0,0.0],  fill=colors[3])
                dpg.draw_triangle(verticies[9],  verticies[10], verticies[8], color=[0,0,0.0],  fill=colors[4])
                dpg.draw_triangle(verticies[9],  verticies[11], verticies[10], color=[0,0,0.0], fill=colors[5])
                dpg.draw_triangle(verticies[15], verticies[13], verticies[12], color=[0,0,0.0], fill=colors[6])
                dpg.draw_triangle(verticies[14], verticies[15], verticies[12], color=[0,0,0.0], fill=colors[7])
                dpg.draw_triangle(verticies[18], verticies[17], verticies[16], color=[0,0,0.0], fill=colors[8])
                dpg.draw_triangle(verticies[19], verticies[17], verticies[18], color=[0,0,0.0], fill=colors[9])
                dpg.draw_triangle(verticies[21], verticies[23], verticies[20], color=[0,0,0.0], fill=colors[10])
                dpg.draw_triangle(verticies[23], verticies[22], verticies[20], color=[0,0,0.0], fill=colors[11])

x_rot = 0
y_rot = 0
z_rot = 0

view = dpg.create_fps_matrix([0, -50, 0], np.deg2rad(90.0), 0.0)
proj = dpg.create_perspective_matrix(math.pi*70.0/180.0, 1.0, 0.1, 100)
model = dpg.create_rotation_matrix(math.pi*x_rot/180.0 , [1, 0, 0])*\
                        dpg.create_rotation_matrix(math.pi*y_rot/180.0 , [0, 1, 0])*\
                        dpg.create_rotation_matrix(math.pi*z_rot/180.0 , [0, 0, 1])

dpg.set_clip_space("main pass", 0, 0, 500, 500, -1.0, 1.0)
dpg.apply_transform("cube", proj*view*model)

dpg.show_viewport()
while dpg.is_dearpygui_running():
    #x_rot += 1
    y_rot += 1
    z_rot += 1
    model = dpg.create_rotation_matrix(math.pi*x_rot/180.0 , [1, 0, 0])*\
                            dpg.create_rotation_matrix(math.pi*y_rot/180.0 , [0, 1, 0])*\
                            dpg.create_rotation_matrix(math.pi*z_rot/180.0 , [0, 0, 1])
    dpg.apply_transform("cube", proj*view*model)
    dpg.render_dearpygui_frame()

dpg.destroy_context()

