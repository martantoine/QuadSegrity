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
    global valves, pressures, serial_order
    
    print("Starting commmunication thread")
    serial_port = sys.argv[1]
    #ort_sess = ort.InferenceSession(onnx_path)
    # check first if the serial port exists
    
    try:
        ser = serial.Serial(serial_port, baudrate=115200, timeout=0.1) #blocking reading because timeout=0
        #ser.write(0xFFFFFFFF) #send the reset command
        started = False
        while not started:
            if ser.inWaiting() == 0:
                time.sleep(0.1)
            else:
                print(ser.readline()) 
                started = True
        while True:
            if serial_order == 1:
                ser.close()
                serial_order = 0
                print("Quitting commmunication thread")
                dpg.configure_item(item=100, label="Connect", callback=start_communicate)
                dpg.configure_item(item=200, default_value="Status: Closed")
                return
            
            if ser.inWaiting() < 4:
                time.sleep(0.1)
            else:
                observation = int.from_bytes(ser.read(4))
                print(observation)
                #scaled_action = ort_sess.run(None, {"input": observation})[0]
                [valves[i].append((observation >> i) & 0x1) for i in range(len(valves))]
                [pressures[i].append(random()) for i in range(len(pressures))]
                time.sleep(update_interval)
                
                #ser.write(scaled_action)
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
    dpg.create_viewport(decorated=False, resizable=False, width=500, height=800)
    
    with dpg.window(label="Main", no_title_bar=True, no_resize=True, no_collapse=True, no_move=True, no_background=False, no_scrollbar=True, width=500, height=800):
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
    thread1 = threading.Thread(name="update plots", target=update_plots, args=((pressures_plot, yax, )), daemon=True)
    thread1.start()
    start_communicate()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()