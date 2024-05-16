import serial
import sys
import onnxruntime as ort
from array import array
from math import sin, pi
from random import random
import numpy as np 
from time import time
import dearpygui.dearpygui as dpg
from collections import deque
import time
import threading
import struct
import os


COMMAND_BYTES_LEN = 4
OBSERVATION_BYTES_LEN = 24
VALVES_HISTORY_WIDTH = 400
onnx_path = "remote_model.onnx"
drawlists = []

max_history_time_seconds = 10
update_interval = 0.5
valve_history_length = int(max_history_time_seconds / update_interval)
valves = [deque([False]*valve_history_length, maxlen=valve_history_length) for i in range(10)]
pressures = [deque([0]*valve_history_length, maxlen=valve_history_length) for i in range(2)]
xP = list(np.linspace(0, max_history_time_seconds, valve_history_length))
w = VALVES_HISTORY_WIDTH / (valve_history_length)

serial_order = 0
class IMUData:
    def __init__(self, history_length):
        self.angle        = deque([[0.0, 0.0, 0.0]], maxlen=history_length)
        self.acceleration = deque([[0.0, 0.0, 0.0]], maxlen=history_length)    
imu_data = IMUData(100)

def update_plots(pressures_plot, yax):
    global valves, pressures, r, pressures, pressures_aug

    print("Starting plot thread")
    while True:
        for y in range(10):
            for x in range(valve_history_length):
                if valves[y][x] == 0:
                    color = [0xff, 0, 0, 0 + 0xff * (x+1) / valve_history_length]
                else:
                    color = [0x11, 0x11, 0x11, 0 + 0xff * (x+1) / valve_history_length]
                dpg.configure_item(item=1000 + x + y*valve_history_length, fill=color)
        
        dpg.configure_item(item=pressures_plot[0], x=list(xP), y=list(pressures[0]))
        dpg.configure_item(item=pressures_plot[1], x=list(xP), y=list(pressures[1]))
        dpg.fit_axis_data(yax)
        time.sleep(update_interval)


if len(sys.argv) < 2:
    print("Usage: python Remote.py <serial_port>")
    sys.exit(1)
if len(sys.argv) == 3:
    onnx_path = sys.argv[2]
    
def communicate():
    global valves, pressures, serial_order, imu_data
    
    print("Starting commmunication thread")
    serial_port = sys.argv[1]
    #ort_sess = ort.InferenceSession(onnx_path)
    # check first if the serial port exists
    
    try:
        ser = serial.Serial(serial_port, baudrate=115200, timeout=0.1) #blocking reading because timeout=0
        #ser.write(0xFFFFFFFF) #send the reset command
        #started = ""
        #while started != "Reset successful":
        #    if ser.inWaiting() == 0:
        #        time.sleep(0.1)
        #    else:
        #        started = ser.readline().decode("ascii")[0:-2]
        #        print(started)

        while True:
            if serial_order == 1:
                ser.close()
                serial_order = 0
                print("Quitting commmunication thread")
                dpg.configure_item(item=100, label="Connect", callback=start_communicate)
                dpg.configure_item(item=200, default_value="Status: Closed")
                return
        
            #scaled_action = ort_sess.run(None, {"input": observation})[0]
            #[valves[i].append((observation >> i) & 0x1) for i in range(len(valves))]
            #[pressures[i].append(random()) for i in range(len(pressures))]
            
            #observation = []
            has_start = False
            while not has_start:
                if ser.inWaiting() >= 1:
                    if ser.read().decode("ascii") == 'i':
                        has_start = True
                time.sleep(0.05)

            def get_int():
                #while ser.inWaiting() < 5:
                #    time.sleep(0.1)
                return int(struct.unpack('<I', ser.read(4))[0])
                

            def get_float():
                #while ser.inWaiting() < 5:
                #    time.sleep(0.1)
                #if ser.read(2).decode("ascii") == "f":
                return float(struct.unpack('<f', ser.read(4))[0])
                return -1
                
            observation = get_int()
            imu_data.acceleration.append([get_float(), get_float(), get_float()])
            imu_data.angle.append([get_float(), get_float(), get_float()])
            print(imu_data.acceleration[-1])
            print(imu_data.angle[-1])
            time.sleep(0.1)
            #ser.write(scaled_action)
            ser.flushInput()
    except:
        dpg.configure_item(item=100, label="Connect", callback=start_communicate)
        dpg.configure_item(item=200, default_value="Status: Closed")                  
        print("Unexpectedly quitting commmunication thread!")

def close_serial():
    global serial_order
    dpg.configure_item(item=100, label="Connect", callback=start_communicate)
    dpg.configure_item(item=200, default_value="Status: Closed")
    serial_order = 1

def start_communicate():
    dpg.configure_item(item=100, label="Disconnect", callback=close_serial)
    dpg.configure_item(item=200, default_value="Status: Opened")
    thread = threading.Thread(name="communication", target=communicate, args=(), daemon=True)
    thread.start()

def history_resize():
    global valve_history_length, w, drawlists, valves, pressures, xP
    for y in range(10):
        for x in range(valve_history_length):
            dpg.delete_item(item=1000 + x + y*valve_history_length)
    valve_history_length = int(dpg.get_value(item=300) / update_interval)
    for i in range(10):
        valves[i] = deque([0]*valve_history_length, maxlen=valve_history_length)
    pressures[0] = deque([0]*valve_history_length, maxlen=valve_history_length)
    pressures[1] = deque([0]*valve_history_length, maxlen=valve_history_length)
    xP = list(np.linspace(0, max_history_time_seconds, valve_history_length))

    w = VALVES_HISTORY_WIDTH / (valve_history_length)
    for y in range(10):
        for x in range(valve_history_length):
            dw = 0
            if valves[y][x] == 0:
                color = [0xff, 0, 0, 0 + 0xff * x / valve_history_length]
            else:
                color = [0x11, 0x11, 0x11, 0 + 0xff * x / valve_history_length]
            if x == valve_history_length - 1:
                dw = w
            dpg.draw_rectangle(pmin=[x*w, 0], pmax=[(x+0.9)*w + dw, 0.9*20], color=color, fill=color, rounding=1.0, tag=1000 + x + y * valve_history_length, parent=drawlists[y])
                        
def main():
    global drawlists
    dpg.create_context()
    dpg.create_viewport(decorated=False, resizable=False, width=1000, height=800)
    dpg.show_implot_demo()
    with dpg.window(label="Commands", no_title_bar=True, no_resize=True, no_collapse=True, no_move=True, no_background=False, no_scrollbar=True, width=500, height=800):
        with dpg.collapsing_header(label="Communication", default_open=True):
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Disonnect", callback=close_serial, tag=100)
                dpg.add_text("Status: Unknown", tag=200)    
                
        with dpg.collapsing_header(label="Valves Commands Histograph", default_open=True):
            dpg.add_slider_int(label="History length (seconds)", default_value=valve_history_length, min_value=10, width=300, max_value=20, tag=300, callback=history_resize)

            dpg.add_text("On/Off valves commands")
            for y in range(10):
                with dpg.drawlist((valve_history_length+5)*w, w) as di:
                    drawlists.append(di)
                    for x in range(valve_history_length):
                        dw = 0
                        if valves[y][x] == 0:
                            color = [0xff, 0, 0, 0 + 0xff * x / valve_history_length]
                        else:
                            color = [0x11, 0x11, 0x11, 0 + 0xff * x / valve_history_length]
                        if x == valve_history_length - 1:
                            dw = w
                        dpg.draw_rectangle(pmin=[x*w, 0], pmax=[(x+0.9)*w + dw, 0.9*w], color=color, fill=color, rounding=1.0, tag=1000 + x + y * valve_history_length, parent=drawlists[-1])
                        dpg.draw_text([VALVES_HISTORY_WIDTH+1.5*w, 0], "valve %d" % y, size=15.0, color=color)
                        
        
            with dpg.plot(label="Pressure commands", height=200, width=(valve_history_length+5)*w):
                dpg.add_plot_legend()

                dpg.add_plot_axis(dpg.mvXAxis, label="time", tag="x_axis")
                yax = dpg.add_plot_axis(dpg.mvYAxis, label="pressure", tag="y_axis")

                pressures_plot = [0]*2
                pressures_plot[0] = dpg.add_stair_series(list(xP), list(pressures[0]), label="hip", parent="y_axis")
                pressures_plot[1] = dpg.add_stair_series(list(xP), list(pressures[1]), label="knee", parent="y_axis")

        with dpg.collapsing_header(label="Jog Mode", default_open=True):
            with dpg.group(horizontal=True, horizontal_spacing=200):
                with dpg.group(horizontal=False):
                    dpg.add_text("Hip Joints")
                    with dpg.group(horizontal=True):
                        dpg.add_slider_int(width=60, default_value=0, min_value=0, max_value=5, vertical=True, format="%d bar")
                        with dpg.group(horizontal=False):
                            dpg.add_checkbox(label="Valve 0", default_value=True)
                            dpg.add_checkbox(label="Valve 1", default_value=True)
                            dpg.add_checkbox(label="Valve 2", default_value=True)
                            dpg.add_checkbox(label="Valve 3", default_value=True)
                            dpg.add_checkbox(label="Valve 4", default_value=True)
                with dpg.group(horizontal=False):
                    dpg.add_text("Knee Joints")
                    with dpg.group(horizontal=True):
                        dpg.add_slider_int(width=60, default_value=0, min_value=0, max_value=5, vertical=True, format="%d bar")
                        with dpg.group(horizontal=False):
                            dpg.add_checkbox(label="Valve 5", default_value=True)
                            dpg.add_checkbox(label="Valve 6", default_value=True)
                            dpg.add_checkbox(label="Valve 7", default_value=True)
                            dpg.add_checkbox(label="Valve 8", default_value=True)
                            dpg.add_checkbox(label="Valve 9", default_value=True)
            dpg.add_button(label="Send Command", width=500, height=50)

    with dpg.window(label="Sensors", no_title_bar=True, no_resize=True, no_collapse=True, no_move=True, no_background=False, no_scrollbar=True, pos=(500, 0), width=500, height=800):
        with dpg.collapsing_header(label="IMU", default_open=True):
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
            with dpg.drawlist(width=500, height=500):
                with dpg.draw_layer(tag="main pass", depth_clipping=True, perspective_divide=True, cull_mode=dpg.mvCullMode_Back):
                    with dpg.draw_node(tag="cube"):
                        dpg.draw_triangle(verticies[1],  verticies[2],  verticies[0],  color=[0,0,0.0], fill=colors[0])
                        dpg.draw_triangle(verticies[1],  verticies[3],  verticies[2],  color=[0,0,0.0], fill=colors[1])
                        dpg.draw_triangle(verticies[7],  verticies[5],  verticies[4],  color=[0,0,0.0], fill=colors[2])
                        dpg.draw_triangle(verticies[6],  verticies[7],  verticies[4],  color=[0,0,0.0], fill=colors[3])
                        dpg.draw_triangle(verticies[9],  verticies[10], verticies[8],  color=[0,0,0.0], fill=colors[4])
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
            proj = dpg.create_perspective_matrix(pi*70.0/180.0, 1.0, 0.1, 100)
            model = dpg.create_rotation_matrix(pi*x_rot/180.0 , [1, 0, 0])*\
                                    dpg.create_rotation_matrix(pi*y_rot/180.0 , [0, 1, 0])*\
                                    dpg.create_rotation_matrix(pi*z_rot/180.0 , [0, 0, 1])

            dpg.set_clip_space("main pass", 0, 0, 500, 500, -1.0, 1.0)
            dpg.apply_transform("cube", proj*view*model)

    thread1 = threading.Thread(name="update plots", target=update_plots, args=((pressures_plot, yax, )), daemon=True)
    thread1.start()
    start_communicate()

    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        x_rot = imu_data.angle[-1][0]
        y_rot = imu_data.angle[-1][1]
        z_rot = imu_data.angle[-1][2]
        model = dpg.create_rotation_matrix(np.deg2rad(z_rot), [0, 0, 1])*\
                dpg.create_rotation_matrix(np.deg2rad(y_rot), [1, 0, 0])*\
                dpg.create_rotation_matrix(np.deg2rad(x_rot), [0, 1, 0])
        dpg.apply_transform("cube", proj*view*model)
        dpg.render_dearpygui_frame()

    dpg.destroy_context()

if __name__ == "__main__":
    main()