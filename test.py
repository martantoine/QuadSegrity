import serial
from array import array
from math import sin, pi
from random import random
import numpy as np 
from time import time
from collections import deque
import time
import struct
    
with serial.Serial("/dev/ttyACM0", baudrate=115200) as ser:
    while True:
        start_detected = False
        while not start_detected:
            ser.read_until(b'start\n')
            start_detected = True

        def get_int():
            return int(struct.unpack('<I', ser.read(4))[0])

        def get_float():
            return float(struct.unpack('<f', ser.read(4))[0])
            
        print("order ", get_int())
        print("accel ", get_float(), get_float(), get_float())
        print("angle ", get_float(), get_float(), get_float())
        time.sleep(0.08)