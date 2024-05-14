from array import array
from math import sin, pi
from random import random
import numpy as np 
from time import time
import dearpygui.dearpygui as dpg
from collections import deque
import time
import threading

max_history_time_seconds = 10
update_interval = 0.5
valve_history_length = int(max_history_time_seconds / update_interval)
r = [[0 for i in range(valve_history_length)] for j in range(10)]
valves = [deque([False]*valve_history_length, maxlen=valve_history_length) for i in range(10)]
pressures = [deque([0]*valve_history_length, maxlen=valve_history_length) for i in range(2)]
pressures_aug = [deque([0]*valve_history_length*2, maxlen=valve_history_length*2) for i in range(2)]
xP = np.sort(list(np.linspace(0, max_history_time_seconds, valve_history_length))*2)
w = 20

def update_plots(pressures_plot, yax):
    global r, pressures, pressures_aug
    while True:
        [valves[i].append(random() > 0.5) for i in range(len(valves))]
        [pressures[i].append(random()) for i in range(len(pressures))]
        pressures_aug[0].append(pressures[0][-1])
        pressures_aug[0].append(pressures[0][-1])
        pressures_aug[1].append(pressures[1][-1])
        pressures_aug[1].append(pressures[1][-1])
        for y in range(10):
            for x in range(valve_history_length):
                if valves[y][x] == 0:
                    color = [0xff, 0, 0, 0 + 0xff * x / valve_history_length]
                else:
                    color = [0x11, 0x11, 0x11, 0 + 0xff * x / valve_history_length]
                dpg.configure_item(item=r[y][x], fill=color)
        
        dpg.configure_item(item=pressures_plot[0], x=list(xP), y1=list(pressures_aug[0]))
        dpg.configure_item(item=pressures_plot[1], x=list(xP), y1=list(pressures_aug[1]))
        dpg.fit_axis_data(yax)
        time.sleep(update_interval)

def main():
    dpg.create_context()
    dpg.create_viewport()

    with dpg.window(label="Valves Histograph"):
        dpg.add_text("On/Off valves")
        for y in range(10):
            with dpg.drawlist((valve_history_length+5)*w, w):
                for x in range(valve_history_length):
                    dw = 0
                    if valves[y][x] == 0:
                        color = [0xff, 0, 0, 0 + 0xff * x / valve_history_length]
                    else:
                        color = [0x11, 0x11, 0x11, 0 + 0xff * x / valve_history_length]
                    if x == valve_history_length - 1:
                        dw = w
                    r[y][x] = dpg.draw_rectangle(pmin=[x*w, 0], pmax=[(x+0.9)*w + dw, 0.9*w], color=color, fill=color, rounding=1.0)
                    dpg.draw_text([(valve_history_length+1.5)*w, 0], "valve %d" % y, size=15.0, color=color)
                    
        
        with dpg.plot(label="Pressure commands", height=200, width=(valve_history_length+5)*w):
            # optionally create legend
            dpg.add_plot_legend()

            # REQUIRED: create x and y axes
            dpg.add_plot_axis(dpg.mvXAxis, label="time", tag="x_axis")
            yax = dpg.add_plot_axis(dpg.mvYAxis, label="pressure", tag="y_axis")
            
            # series belong to a y axis
            pressures_plot = [0]*2
            pressures_plot[0] = dpg.add_shade_series(list(xP), list(pressures_aug[0]), label="hip", parent="y_axis")
            pressures_plot[1] = dpg.add_shade_series(list(xP), list(pressures_aug[1]), label="knee", parent="y_axis")
                
    thread1 = threading.Thread(name="update plots", target=update_plots, args=((pressures_plot, yax, )), daemon=True)
    thread1.start()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()