from array import array
from math import sin, pi
from random import random
from time import time
import dearpygui.dearpygui as dpg
from collections import deque
import time
import threading

C = 0.01
L = int(pi * 2 * 100)

max_history_time_seconds = 10
update_interval = 0.5
valve_history_length = int(max_history_time_seconds / update_interval)
r = [[0 for i in range(valve_history_length)] for j in range(10)]
valves = [deque([False]*valve_history_length, maxlen=valve_history_length) for i in range(10)]
w = 20

def update_plots():
    global r

    while True:
        [valves[i].append(random() > 0.5) for i in range(len(valves))]
        for y in range(10):
            for x in range(valve_history_length):
                if valves[y][x] == 0:
                    color = [0xff, 0, 0, 0 + 0xff * x / valve_history_length]
                else:
                    color = [0x11, 0x11, 0x11, 0 + 0xff * x / valve_history_length]
                dpg.configure_item(item=r[y][x], fill=color)
        
        time.sleep(update_interval)

def main():
    plot_values = array("f", [sin(x * C) for x in range(L)])
    histogram_values = array("f", [random() for _ in range(20)])
    last_time = time.time()

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
                    
        #dpg.plot_histogram(
        #    "histogram(random())",
        #    histogram_values,
        #    overlay_text="random histogram",
        #    values_count=22,
        #    values_offset=0,
        #    # offset by one item every milisecond, plot values
        #    # buffer its end wraps around
        #    graph_size=(21*w, 2*w),
        #)

    thread1 = threading.Thread(name="update plots", target=update_plots, args=(), daemon=True)
    thread1.start()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()