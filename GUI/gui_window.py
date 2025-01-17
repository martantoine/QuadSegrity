import dearpygui.dearpygui as dpg
import delegate

dpg.create_context()


def update_connection(state):
    """
    Update UI elements (button and label) related to connection status
    the button action performs the opposite of the current status
    i.o.w: if connected, the button will trigger a disconnection, etc

    Args:
        state (bool): connection status (true -> connected, fale -> disconnected)
    """
    button_txt = ""
    label_txt = ""
    if state:
        button_txt="Disconnect"
        label_txt = "connected"
    else:
        button_txt = "Connect"
        label_txt = "disconnected"
    dpg.configure_item(item="connection_button", label=button_txt)
    dpg.set_value("connection_status", "Status: " + label_txt)

def get_jog_commands():
    commands = []
    for i in range(10):
        commands.append(dpg.get_value("valve_" + str(i)))
    return commands
    
def main():
    global drawlists
    dpg.create_viewport(decorated=False, resizable=False, width=1000, height=800)
    
    with dpg.window(label="Commands", no_title_bar=True, no_resize=True, no_collapse=True, no_move=True, no_background=False, no_scrollbar=True, width=500, height=800):
        with dpg.collapsing_header(label="Communication", default_open=True):
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Connect", callback=delegate.connection_cb, tag="connection_button")
                dpg.add_text("Status: Unknown", tag="connection_status")
                
        # with dpg.collapsing_header(label="Valves Commands Histograph", default_open=True):
        #     #dpg.add_slider_int(label="History length (seconds)", default_value=valve_history_length, min_value=10, width=300, max_value=20, tag=300, callback=history_resize)

        #     dpg.add_text("On/Off valves commands")
        #     for y in range(10):
        #         with dpg.drawlist((valve_history_length+5)*w, w) as di:
        #             drawlists.append(di)
        #             for x in range(valve_history_length):
        #                 dw = 0
        #                 if valves[y][x] == 0:
        #                     color = [0xff, 0, 0, 0 + 0xff * x / valve_history_length]
        #                 else:
        #                     color = [0x11, 0x11, 0x11, 0 + 0xff * x / valve_history_length]
        #                 if x == valve_history_length - 1:
        #                     dw = w
        #                 #dpg.draw_rectangle(pmin=[x*w, 0], pmax=[(x+0.9)*w + dw, 0.9*w], color=color, fill=color, rounding=1.0, tag=1000 + x + y * valve_history_length, parent=drawlists[-1])
        #                 dpg.draw_text([VALVES_HISTORY_WIDTH+1.5*w, 0], "valve %d" % y, size=15.0, color=color)
                        
        
        #     with dpg.plot(label="Pressure commands", height=200, width=(valve_history_length+5)*w):
        #         dpg.add_plot_legend()

        #         dpg.add_plot_axis(dpg.mvXAxis, label="time", tag="x_axis")
        #         yax = dpg.add_plot_axis(dpg.mvYAxis, label="pressure", tag="y_axis")

        #         pressures_plot = [0]*2
        #         pressures_plot[0] = dpg.add_stair_series(list(xP), list(pressures[0]), label="hip", parent="y_axis")
        #         pressures_plot[1] = dpg.add_stair_series(list(xP), list(pressures[1]), label="knee", parent="y_axis")

        with dpg.collapsing_header(label="Jog Mode", default_open=True):
            with dpg.group(horizontal=True, horizontal_spacing=200):
                with dpg.group(horizontal=False):
                    dpg.add_text("Hip Joints")
                    with dpg.group(horizontal=True):
                        with dpg.group(horizontal=False):
                            dpg.add_checkbox(label="Valve 0", default_value=True, tag="valve_0")
                            dpg.add_checkbox(label="Valve 1", default_value=True, tag="valve_1")
                            dpg.add_checkbox(label="Valve 2", default_value=True, tag="valve_2")
                            dpg.add_checkbox(label="Valve 3", default_value=True, tag="valve_3")
                            dpg.add_checkbox(label="Valve 4", default_value=True, tag="valve_4")
                with dpg.group(horizontal=False):
                    dpg.add_text("Knee Joints")
                    with dpg.group(horizontal=True):
                        with dpg.group(horizontal=False):
                            dpg.add_checkbox(label="Valve 5", default_value=True, tag="valve_5")
                            dpg.add_checkbox(label="Valve 6", default_value=True, tag="valve_6")
                            dpg.add_checkbox(label="Valve 7", default_value=True, tag="valve_7")
                            dpg.add_checkbox(label="Valve 8", default_value=True, tag="valve_8")
                            dpg.add_checkbox(label="Valve 9", default_value=True, tag="valve_9")
            dpg.add_button(label="Send Command", width=500, height=50, callback=delegate.send_actuators_command)

    # with dpg.window(label="Sensors", no_title_bar=True, no_resize=True, no_collapse=True, no_move=True, no_background=False, no_scrollbar=True, pos=(500, 0), width=500, height=800):
    #     with dpg.collapsing_header(label="IMU", default_open=True):
    #         width = 5
    #         length = 10
    #         height = 2
    #         verticies = [
    #                 [-length, -width, -height],  # 0 near side
    #                 [ length, -width, -height],  # 1
    #                 [-length,  width, -height],  # 2
    #                 [ length,  width, -height],  # 3
    #                 [-length, -width,  height],  # 4 far side
    #                 [ length, -width,  height],  # 5
    #                 [-length,  width,  height],  # 6
    #                 [ length,  width,  height],  # 7
    #                 [-length, -width, -height],  # 8 left side
    #                 [-length,  width, -height],  # 9
    #                 [-length, -width,  height],  # 10
    #                 [-length,  width,  height],  # 11
    #                 [ length, -width, -height],  # 12 right side
    #                 [ length,  width, -height],  # 13
    #                 [ length, -width,  height],  # 14
    #                 [ length,  width,  height],  # 15
    #                 [-length, -width, -height],  # 16 bottom side
    #                 [ length, -width, -height],  # 17
    #                 [-length, -width,  height],  # 18
    #                 [ length, -width,  height],  # 19
    #                 [-length,  width, -height],  # 20 top side
    #                 [ length,  width, -height],  # 21
    #                 [-length,  width,  height],  # 22
    #                 [ length,  width,  height],  # 23
    #             ]

    #         colors = [[150, 150, 150, 255]] * int(len(verticies)/2)
    #         with dpg.drawlist(width=500, height=500):
    #             with dpg.draw_layer(tag="main pass", depth_clipping=True, perspective_divide=True, cull_mode=dpg.mvCullMode_Back):
    #                 with dpg.draw_node(tag="cube"):
    #                     dpg.draw_triangle(verticies[1],  verticies[2],  verticies[0],  color=[0,0,0.0], fill=colors[0])
    #                     dpg.draw_triangle(verticies[1],  verticies[3],  verticies[2],  color=[0,0,0.0], fill=colors[1])
    #                     dpg.draw_triangle(verticies[7],  verticies[5],  verticies[4],  color=[0,0,0.0], fill=colors[2])
    #                     dpg.draw_triangle(verticies[6],  verticies[7],  verticies[4],  color=[0,0,0.0], fill=colors[3])
    #                     dpg.draw_triangle(verticies[9],  verticies[10], verticies[8],  color=[0,0,0.0], fill=colors[4])
    #                     dpg.draw_triangle(verticies[9],  verticies[11], verticies[10], color=[0,0,0.0], fill=colors[5])
    #                     dpg.draw_triangle(verticies[15], verticies[13], verticies[12], color=[0,0,0.0], fill=colors[6])
    #                     dpg.draw_triangle(verticies[14], verticies[15], verticies[12], color=[0,0,0.0], fill=colors[7])
    #                     dpg.draw_triangle(verticies[18], verticies[17], verticies[16], color=[0,0,0.0], fill=colors[8])
    #                     dpg.draw_triangle(verticies[19], verticies[17], verticies[18], color=[0,0,0.0], fill=colors[9])
    #                     dpg.draw_triangle(verticies[21], verticies[23], verticies[20], color=[0,0,0.0], fill=colors[10])
    #                     dpg.draw_triangle(verticies[23], verticies[22], verticies[20], color=[0,0,0.0], fill=colors[11])

    #         x_rot = 0
    #         y_rot = 0
    #         z_rot = 0

    #         view = dpg.create_fps_matrix([0, -50, 10], np.deg2rad(90.0), 0.0)
    #         proj = dpg.create_perspective_matrix(pi*90.0/180.0, 1.0, 0.01, 200)
    #         model = dpg.create_rotation_matrix(pi*x_rot/180.0 , [1, 0, 0])*\
    #                                 dpg.create_rotation_matrix(pi*y_rot/180.0 , [0, 1, 0])*\
    #                                 dpg.create_rotation_matrix(pi*z_rot/180.0 , [0, 0, 1])

    #         dpg.set_clip_space("main pass", 0, 0, 500, 500, -1.0, 1.0)
    #         dpg.apply_transform("cube", proj*view*model)

    # thread1 = threading.Thread(name="update plots", target=update_plots, args=((pressures_plot, yax, )), daemon=True)
    # thread1.start()
    # start_communicate()

    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        #x_rot = imu_data.angle[-1][0]
        #y_rot = imu_data.angle[-1][1]
        #z_rot = 0#imu_data.angle[-1][2]
        #model = dpg.create_rotation_matrix(np.deg2rad(z_rot), [0, 0, 1])*\
        #        dpg.create_rotation_matrix(np.deg2rad(y_rot), [1, 0, 0])*\
        #        dpg.create_rotation_matrix(np.deg2rad(x_rot), [0, 1, 0])
        #dpg.apply_transform("cube", proj*view*model)
        dpg.render_dearpygui_frame()

    dpg.destroy_context()

if __name__ == "__main__":
    main()